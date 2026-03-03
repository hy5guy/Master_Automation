#!/usr/bin/env python3
"""
Compare Summons 'Department-Wide Summons Moving and Parking' export vs backfill and ETL output.

Inputs:
- visual export CSV: TYPE, Month_Year, Sum of TICKET_COUNT
- backfill CSV (historical): TYPE, Month_Year, Sum of TICKET_COUNT
- ETL staging workbook: summons_powerbi_latest.xlsx (Summons_Data sheet), compare 11-25 by summing TICKET_COUNT
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def load_summary_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["TYPE"] = df["TYPE"].astype(str).str.strip()
    df["Month_Year"] = df["Month_Year"].astype(str).str.strip()
    df["Sum of TICKET_COUNT"] = pd.to_numeric(df["Sum of TICKET_COUNT"], errors="coerce").fillna(0).astype(int)
    return df


def diff(a: pd.DataFrame, b: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    m = a.merge(b, on=["TYPE", "Month_Year"], how="outer", suffixes=("_a", "_b"), indicator=True)
    missing = m[m["_merge"] != "both"][["TYPE", "Month_Year", "_merge"]].sort_values(["Month_Year", "TYPE"])
    both = m[m["_merge"] == "both"].copy()
    both["diff"] = both["Sum of TICKET_COUNT_a"] - both["Sum of TICKET_COUNT_b"]
    diffs = both[both["diff"] != 0][
        ["TYPE", "Month_Year", "Sum of TICKET_COUNT_a", "Sum of TICKET_COUNT_b", "diff"]
    ].sort_values(["Month_Year", "TYPE"])
    return missing, diffs


def compute_month_from_etl(xlsx_path: Path, month: str) -> pd.DataFrame:
    df = pd.read_excel(xlsx_path, sheet_name="Summons_Data")
    # Ensure types
    df["Month_Year"] = df["Month_Year"].astype(str).str.strip()
    df["TYPE"] = df["TYPE"].astype(str).str.strip()
    df["TICKET_COUNT"] = pd.to_numeric(df["TICKET_COUNT"], errors="coerce").fillna(0).astype(int)
    m = df[df["Month_Year"] == month].copy()
    out = m.groupby(["TYPE", "Month_Year"], as_index=False)["TICKET_COUNT"].sum()
    out = out.rename(columns={"TICKET_COUNT": "Sum of TICKET_COUNT"})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--visual", required=True, help="Path to visual export CSV")
    ap.add_argument("--backfill", required=True, help="Path to backfill CSV")
    ap.add_argument("--etl-xlsx", required=True, help="Path to summons_powerbi_latest.xlsx")
    ap.add_argument("--current", default="11-25", help="Current month label (MM-YY)")
    args = ap.parse_args()

    visual = load_summary_csv(Path(args.visual))
    backfill = load_summary_csv(Path(args.backfill))

    # 1) History comparison: only months present in backfill
    backfill_months = set(backfill["Month_Year"].unique())
    visual_hist = visual[visual["Month_Year"].isin(backfill_months)].copy()
    missing, diffs = diff(visual_hist, backfill)

    print("=== Visual vs Backfill (History Months) ===")
    print(f"Missing keys: {len(missing)}")
    print(f"Value diffs:  {len(diffs)}")
    if len(missing):
        print("\nMissing (first 50):")
        print(missing.head(50).to_string(index=False))
    if len(diffs):
        print("\nDiffs (first 50):")
        print(diffs.head(50).to_string(index=False))

    # 2) Current month comparison: visual vs ETL
    etl_cur = compute_month_from_etl(Path(args.etl_xlsx), args.current)
    visual_cur = visual[visual["Month_Year"] == args.current].copy()

    # Normalize column name for diff()
    etl_cur = etl_cur.rename(columns={"Sum of TICKET_COUNT": "Sum of TICKET_COUNT"})
    missing2, diffs2 = diff(visual_cur, etl_cur)

    print(f"\n=== Visual vs ETL (Current Month {args.current}) ===")
    print(f"Missing keys: {len(missing2)}")
    print(f"Value diffs:  {len(diffs2)}")
    if len(missing2):
        print("\nMissing:")
        print(missing2.to_string(index=False))
    if len(diffs2):
        print("\nDiffs:")
        print(diffs2.to_string(index=False))

    if len(diffs) == 0 and len(missing) == 0 and len(diffs2) == 0 and len(missing2) == 0:
        print("\n[OK] Visual matches backfill history and ETL current month.")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())


