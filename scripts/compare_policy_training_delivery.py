#!/usr/bin/env python3
"""
Compare Policy Training "Training Cost by Delivery Method" visual export against:
1) ETL output workbook sheet Delivery_Cost_By_Month
2) Backfill CSV (historical months only)

This script is intentionally standalone to avoid PowerShell quoting issues.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def _norm(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Period"] = df["Period"].astype(str).str.strip()
    df["Delivery_Type"] = df["Delivery_Type"].astype(str).str.strip()
    df["Sum of Cost"] = pd.to_numeric(df["Sum of Cost"], errors="coerce").fillna(0.0)
    return df


def load_etl_delivery_long(path_xlsx: Path) -> pd.DataFrame:
    wide = pd.read_excel(path_xlsx, sheet_name="Delivery_Cost_By_Month")
    idcol = "Delivery_Type"
    valcols = [c for c in wide.columns if c not in (idcol, "Total")]
    long = wide.melt(id_vars=[idcol], value_vars=valcols, var_name="Period", value_name="Sum of Cost")
    return _norm(long)


def diff(a: pd.DataFrame, b: pd.DataFrame, tol: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns (missing, diffs) where:
    - missing contains keys present in one side only
    - diffs contains numeric mismatches beyond tolerance
    """
    m = a.merge(b, on=["Period", "Delivery_Type"], how="outer", suffixes=("_a", "_b"), indicator=True)
    missing = m[m["_merge"] != "both"][["Period", "Delivery_Type", "_merge"]].sort_values(["Period", "Delivery_Type"])
    both = m[m["_merge"] == "both"].copy()
    both["diff"] = both["Sum of Cost_a"] - both["Sum of Cost_b"]
    diffs = both[np.abs(both["diff"]) > tol][
        ["Period", "Delivery_Type", "Sum of Cost_a", "Sum of Cost_b", "diff"]
    ].sort_values(["Period", "Delivery_Type"])
    return missing, diffs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--visual", required=True, help="Path to visual export CSV (Period,Delivery_Type,Sum of Cost)")
    ap.add_argument("--etl-xlsx", required=True, help="Path to policy_training_outputs.xlsx")
    ap.add_argument("--backfill", required=True, help="Path to backfill CSV (Period,Delivery_Type,Sum of Cost)")
    ap.add_argument("--current-period", default="11-25", help="Current month period label to exclude from backfill check")
    ap.add_argument("--tol", type=float, default=1e-6, help="Numeric tolerance")
    args = ap.parse_args()

    visual = _norm(pd.read_csv(Path(args.visual)))
    etl = load_etl_delivery_long(Path(args.etl_xlsx))
    backfill = _norm(pd.read_csv(Path(args.backfill)))

    print("=== Visual vs ETL (Full Periods In Visual) ===")
    missing, diffs = diff(visual, etl, args.tol)
    print(f"Missing keys: {len(missing)}")
    print(f"Value diffs:  {len(diffs)} (tol={args.tol})")
    if len(missing):
        print("\nMissing (first 50):")
        print(missing.head(50).to_string(index=False))
    if len(diffs):
        print("\nDiffs (first 50):")
        print(diffs.head(50).to_string(index=False))

    print("\n=== Visual History vs Backfill (Exclude Current Period) ===")
    visual_hist = visual[visual["Period"] != args.current_period].copy()
    missing2, diffs2 = diff(visual_hist, backfill, args.tol)
    print(f"Missing keys: {len(missing2)}")
    print(f"Value diffs:  {len(diffs2)} (tol={args.tol})")
    if len(missing2):
        print("\nMissing (first 50):")
        print(missing2.head(50).to_string(index=False))
    if len(diffs2):
        print("\nDiffs (first 50):")
        print(diffs2.head(50).to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


