#!/usr/bin/env python3
# 🕒 2026-01-08
# Purpose:
#   Generate the 4 CSV files that the Power BI Summons queries currently reference:
#     - PowerBI_Date\\backfill_summons_summary.csv        (wide backfill summary)
#     - PowerBI_Date\\wg2_movers_parkers_nov2025.csv      (WG2 movers/parkers table; "C" column is Total)
#     - PowerBI_Date\\top5_moving_1125.csv                (Top 5 moving officers)
#     - PowerBI_Date\\top5_parking_1125.csv               (Top 5 parking officers)
#
# Source of truth:
#   03_Staging\\Summons\\summons_powerbi_latest.xlsx (sheet: Summons_Data)
#
# Notes:
# - Files are overwritten in place (filenames are historical artifacts in the M code,
#   but contents are always generated from the latest month in the workbook).

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

import pandas as pd


@dataclass(frozen=True)
class Paths:
    source_xlsx: Path
    powerbi_date_dir: Path


def _safe_int(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").fillna(0).round(0).astype("int64")


def load_df(source_xlsx: Path) -> pd.DataFrame:
    if not source_xlsx.exists():
        raise FileNotFoundError(f"Missing source workbook: {source_xlsx}")

    df = pd.read_excel(source_xlsx, sheet_name="Summons_Data", engine="openpyxl")
    required = {
        "YearMonthKey",
        "Month_Year",
        "TYPE",
        "TICKET_COUNT",
        "WG2",
        "OFFICER_DISPLAY_NAME",
        "IS_AGGREGATE",
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Summons_Data missing required columns: {missing}")

    df = df.copy()
    df["TICKET_COUNT"] = _safe_int(df["TICKET_COUNT"])
    df["YearMonthKey"] = _safe_int(df["YearMonthKey"])
    df["Month_Year"] = df["Month_Year"].astype(str).str.strip()
    df["TYPE"] = df["TYPE"].astype(str).str.strip().str.upper()
    df["WG2"] = df["WG2"].astype(str).str.strip()
    df["OFFICER_DISPLAY_NAME"] = df["OFFICER_DISPLAY_NAME"].astype(str).str.strip()
    df["IS_AGGREGATE"] = df["IS_AGGREGATE"].fillna(False).astype(bool)

    # Exclude aggregate rows so totals don't double count and Top5/WG breakdowns are correct
    df = df.loc[~df["IS_AGGREGATE"]].copy()
    return df


def latest_month_key(df: pd.DataFrame) -> int:
    if df.empty:
        raise ValueError("No non-aggregate summons rows found; cannot compute latest month.")
    return int(df["YearMonthKey"].max())


def write_backfill_summary(df: pd.DataFrame, out_csv: Path) -> None:
    base = df.loc[df["TYPE"].isin(["M", "P"])].copy()

    month_map = (
        base[["YearMonthKey", "Month_Year"]]
        .drop_duplicates()
        .sort_values("YearMonthKey")
    )
    months = month_map["Month_Year"].tolist()

    grouped = base.groupby(["TYPE", "Month_Year"], as_index=False)["TICKET_COUNT"].sum()
    wide = grouped.pivot(index="TYPE", columns="Month_Year", values="TICKET_COUNT").fillna(0)
    wide = wide.reindex(columns=months, fill_value=0).astype("int64")

    wide.insert(0, "TYPE", wide.index)
    wide = wide.reset_index(drop=True)

    total_row = wide.loc[wide["TYPE"].isin(["M", "P"]), months].sum(axis=0).to_frame().T
    total_row.insert(0, "TYPE", ["Total"])

    out = pd.concat([wide, total_row], ignore_index=True)
    out.to_csv(out_csv, index=False)


def write_wg2_movers_parkers(df: pd.DataFrame, ym_key: int, out_csv: Path) -> None:
    cur = df.loc[(df["YearMonthKey"] == ym_key) & (df["TYPE"].isin(["M", "P"]))].copy()
    grouped = cur.groupby(["WG2", "TYPE"], as_index=False)["TICKET_COUNT"].sum()
    wide = grouped.pivot(index="WG2", columns="TYPE", values="TICKET_COUNT").fillna(0).astype("int64")
    for col in ["M", "P"]:
        if col not in wide.columns:
            wide[col] = 0
    wide["C"] = (wide["M"] + wide["P"]).astype("int64")  # M code renames C -> Total
    wide = wide.reset_index()[["WG2", "M", "P", "C"]]
    wide.to_csv(out_csv, index=False)


def write_top5(df: pd.DataFrame, ym_key: int, summons_type: str, out_csv: Path) -> None:
    label = "Moving Summons" if summons_type == "M" else "Parking Summons"
    cur = df.loc[(df["YearMonthKey"] == ym_key) & (df["TYPE"] == summons_type)].copy()

    if cur.empty:
        pd.DataFrame({"Proposed Standardized Name": [], label: []}).to_csv(out_csv, index=False)
        return

    top = (
        cur.groupby("OFFICER_DISPLAY_NAME", as_index=False)["TICKET_COUNT"]
        .sum()
        .sort_values("TICKET_COUNT", ascending=False)
        .head(5)
        .rename(columns={"OFFICER_DISPLAY_NAME": "Proposed Standardized Name", "TICKET_COUNT": label})
    )
    top[label] = top[label].astype("int64")
    top.to_csv(out_csv, index=False)


def main() -> int:
    paths = Paths(
        source_xlsx=Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"),
        powerbi_date_dir=Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date"),
    )

    df = load_df(paths.source_xlsx)
    ym_key = latest_month_key(df)

    out_backfill = paths.powerbi_date_dir / "backfill_summons_summary.csv"
    out_wg2 = paths.powerbi_date_dir / "wg2_movers_parkers_nov2025.csv"
    out_top_m = paths.powerbi_date_dir / "top5_moving_1125.csv"
    out_top_p = paths.powerbi_date_dir / "top5_parking_1125.csv"

    write_backfill_summary(df, out_backfill)
    write_wg2_movers_parkers(df, ym_key, out_wg2)
    write_top5(df, ym_key, "M", out_top_m)
    write_top5(df, ym_key, "P", out_top_p)

    print("[OK] Summons derived CSVs written:")
    print(f"  - {out_backfill}")
    print(f"  - {out_wg2}  (latest YearMonthKey={ym_key})")
    print(f"  - {out_top_m}")
    print(f"  - {out_top_p}")
    print(f"[INFO] Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

