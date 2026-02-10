#!/usr/bin/env python3
"""
Validate the Summons 'Moving & Parking All Bureaus' visual export against the ETL output workbook.

Compares:
- visual export CSV with columns: Bureau, TYPE, Sum of TICKET_COUNT
  (Bureau corresponds to WG2 in the ETL output)
- ETL output workbook: summons_powerbi_latest.xlsx (Summons_Data sheet)

Also prints Patrol officer last-name contributions for the month to help debug "Patrol is incorrect" issues.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def load_visual(path: Path) -> pd.DataFrame:
    v = pd.read_csv(path)
    v["Bureau"] = v["Bureau"].astype(str).str.strip()
    v["TYPE"] = v["TYPE"].astype(str).str.strip().str.upper()
    v["Sum of TICKET_COUNT"] = pd.to_numeric(v["Sum of TICKET_COUNT"], errors="coerce").fillna(0).astype(int)
    return v


def load_etl(xlsx: Path, month: str) -> pd.DataFrame:
    df = pd.read_excel(xlsx, sheet_name="Summons_Data")
    needed = ["WG2", "TYPE", "TICKET_COUNT", "Month_Year"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise SystemExit(f"Missing columns in ETL workbook: {missing}")

    df["Month_Year"] = df["Month_Year"].astype(str).str.strip()
    df = df[df["Month_Year"] == month].copy()
    df["WG2"] = df["WG2"].astype(str).str.strip()
    df["TYPE"] = df["TYPE"].astype(str).str.strip().str.upper()
    df["TICKET_COUNT"] = pd.to_numeric(df["TICKET_COUNT"], errors="coerce").fillna(0).astype(int)
    return df


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--visual", required=True, help="Path to visual export CSV (All Bureaus)")
    ap.add_argument("--etl-xlsx", required=True, help="Path to summons_powerbi_latest.xlsx")
    ap.add_argument("--month", default="11-25", help="Month_Year label (MM-YY)")
    ap.add_argument("--patrol-bureau", default="PATROL BUREAU", help="WG2 label used for Patrol")
    args = ap.parse_args()

    visual = load_visual(Path(args.visual))
    etl = load_etl(Path(args.etl_xlsx), args.month)

    # ETL grouped as the visual does: WG2 -> Bureau, TYPE, sum(TICKET_COUNT)
    etl_grp = (
        etl.groupby(["WG2", "TYPE"], as_index=False)["TICKET_COUNT"].sum()
        .rename(columns={"WG2": "Bureau", "TICKET_COUNT": "Sum of TICKET_COUNT"})
    )

    # Keep only M/P in comparison because this visual is "Moving & Parking"
    visual_mp = visual[visual["TYPE"].isin(["M", "P"])].copy()
    etl_mp = etl_grp[etl_grp["TYPE"].isin(["M", "P"])].copy()

    merged = visual_mp.merge(etl_mp, on=["Bureau", "TYPE"], how="outer", suffixes=("_visual", "_etl"), indicator=True)
    missing = merged[merged["_merge"] != "both"][["Bureau", "TYPE", "_merge"]].sort_values(["Bureau", "TYPE"])
    both = merged[merged["_merge"] == "both"].copy()
    both["diff"] = both["Sum of TICKET_COUNT_visual"] - both["Sum of TICKET_COUNT_etl"]
    diffs = both[both["diff"] != 0][
        ["Bureau", "TYPE", "Sum of TICKET_COUNT_visual", "Sum of TICKET_COUNT_etl", "diff"]
    ].sort_values(["Bureau", "TYPE"])

    print(f"=== All Bureaus Visual vs ETL (month {args.month}) ===")
    print(f"Missing keys: {len(missing)}")
    print(f"Value diffs:  {len(diffs)}")
    if len(missing):
        print("\nMissing (first 50):")
        print(missing.head(50).to_string(index=False))
    if len(diffs):
        print("\nDiffs (first 50):")
        print(diffs.head(50).to_string(index=False))

    # Patrol-specific drilldown: officer last names + M/P counts
    patrol = etl[etl["WG2"].str.upper() == args.patrol_bureau.upper()].copy()
    if "OFFICER_NAME_RAW" in patrol.columns:
        patrol["OFFICER_NAME_RAW"] = patrol["OFFICER_NAME_RAW"].astype(str).str.strip()
        # Last name is before comma in "LAST, FIRST"
        patrol["Officer_Last_Name"] = patrol["OFFICER_NAME_RAW"].str.split(",", n=1).str[0].str.strip()
    else:
        patrol["Officer_Last_Name"] = ""

    patrol_mp = patrol[patrol["TYPE"].isin(["M", "P"])].copy()
    by_last = (
        patrol_mp.groupby(["Officer_Last_Name", "TYPE"], as_index=False)["TICKET_COUNT"].sum()
        .sort_values(["TICKET_COUNT"], ascending=False)
    )
    if not by_last.empty:
        print("\n=== Patrol Drilldown (Officer Last Name, TYPE) ===")
        print(by_last.head(30).to_string(index=False))

    # Totals sanity
    vis_tot = int(visual_mp["Sum of TICKET_COUNT"].sum())
    etl_tot = int(etl_mp["Sum of TICKET_COUNT"].sum())
    print(f"\nTotals (M+P) - Visual: {vis_tot}   ETL: {etl_tot}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


