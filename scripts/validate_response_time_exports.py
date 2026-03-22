#!/usr/bin/env python3
"""
Validate Processed_Exports response_time CSV shapes for backfill / Power BI refresh.

Non-fatal: returns (ok, warnings, errors). Errors indicate likely ETL breakage; warnings are actionable review.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd

# Series shapes (Emergency/Routine/Urgent Total Response, mm:ss or min columns)
RT_SERIES_DATE_CANDIDATES = ("Date_Sort_Key", "Date", "Month")
RT_PRIORITY_PERIOD = "MM-YY"
RT_PRIORITY_TYPE_COLS = ("Response_Type", "Metric_Label", "RT Avg Formatted")

# Classic mm:ss grid export
RT_MMSS_PRIORITY = "Response Type"

# All-metrics / calculator long export (per-month rows)
RT_ALL_METRICS_OPTIONAL = (
    "First_Response_Time_MMSS",
    "Avg_Minutes",
    "Record_Count",
    "Median_Minutes",
    "Metric_Type",
)


def _norm_col(c: Any) -> str:
    return str(c).strip() if c is not None else ""


def validate_response_time_csv(path: Path) -> tuple[bool, list[str], list[str]]:
    """
    Inspect a single CSV. Returns (ok, warnings, errors).
    ok is True if no errors (warnings allowed).
    """
    warnings: list[str] = []
    errors: list[str] = []

    if not path.exists():
        return False, [], [f"File not found: {path}"]
    if path.stat().st_size == 0:
        return False, [], [f"Empty file: {path}"]

    try:
        df = pd.read_csv(path, nrows=5000, low_memory=False)
    except Exception as e:
        return False, [], [f"Cannot read CSV: {e}"]

    if df.empty:
        return False, [], ["CSV has no rows"]

    cols = [_norm_col(c) for c in df.columns]
    colset = set(cols)

    stem = path.stem.lower()

    # All-metrics long-form export
    if (
        "all_metrics" in stem
        or "response_time_all" in stem
        or ("Metric_Type" in colset and RT_PRIORITY_PERIOD in colset)
    ):
        if RT_PRIORITY_PERIOD not in colset:
            errors.append(f"Expected column '{RT_PRIORITY_PERIOD}' for all-metrics style export")
            return (not errors, warnings, errors)
        miss = [c for c in RT_ALL_METRICS_OPTIONAL if c not in colset]
        if len(miss) >= len(RT_ALL_METRICS_OPTIONAL):
            warnings.append(
                "All-metrics export missing typical measure columns "
                f"({RT_ALL_METRICS_OPTIONAL}); confirm export template."
            )
        elif miss:
            warnings.append(f"All-metrics export missing some optional columns {miss}.")
        mm = df[RT_PRIORITY_PERIOD].dropna().astype(str).str.strip()
        if mm.eq("").all():
            warnings.append(f"Column '{RT_PRIORITY_PERIOD}' has no non-blank values.")
        return (not errors, warnings, errors)

    # Priority matrix / trends export
    if RT_PRIORITY_PERIOD in colset or "response_time_trends" in stem or "trends_by_priority" in stem:
        if RT_PRIORITY_PERIOD not in colset:
            errors.append(f"Expected column '{RT_PRIORITY_PERIOD}' for priority-matrix style export")
        else:
            miss = [c for c in RT_PRIORITY_TYPE_COLS if c not in colset]
            if miss:
                warnings.append(f"Priority-matrix export missing optional columns {miss}; confirm visual layout.")
            mm = df[RT_PRIORITY_PERIOD].dropna().astype(str).str.strip()
            if mm.eq("").all():
                warnings.append(f"Column '{RT_PRIORITY_PERIOD}' has no non-blank values.")
        return (not errors, warnings, errors)

    # Series export (date + value)
    date_hit = next((c for c in RT_SERIES_DATE_CANDIDATES if c in colset), None)
    if date_hit:
        value_cols = [c for c in cols if c != date_hit and not str(c).startswith("Unnamed")]
        if not value_cols:
            errors.append(f"No value columns found beside '{date_hit}'")
        else:
            sample = df[value_cols[0]].dropna().astype(str).head(20)
            if not sample.empty:
                looks_min = sample.str.contains(r"min", case=False, regex=True).any()
                looks_time = sample.str.contains(r":\d{2}", regex=True).any()
                if not looks_min and not looks_time:
                    warnings.append(
                        f"Value column '{value_cols[0]}' does not look like mm:ss or 'X.X min'; verify export."
                    )
        return (not errors, warnings, errors)

    # Classic Average Response Times (Response Type + MM-YY style)
    if RT_MMSS_PRIORITY in colset or any(re.search(r"response.type", c, re.I) for c in cols):
        mm_cols = [c for c in cols if re.match(r"^\d{2}-\d{2}$", _norm_col(c)) or _norm_col(c).startswith("Sum of ")]
        if not mm_cols:
            warnings.append("No MM-YY period columns detected; wide-format response export may differ.")
        return (not errors, warnings, errors)

    warnings.append(
        f"Unrecognized response_time layout; columns: {cols[:12]}{'...' if len(cols) > 12 else ''}"
    )
    return True, warnings, errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate response_time CSV exports.")
    ap.add_argument("paths", nargs="+", type=Path, help="CSV file(s) to validate")
    ap.add_argument("--strict", action="store_true", help="Treat warnings as failures (exit 1)")
    args = ap.parse_args()

    any_err = False
    for p in args.paths:
        ok, warns, errs = validate_response_time_csv(p.resolve())
        print(f"=== {p.name} ===")
        for e in errs:
            print(f"  [ERROR] {e}")
        for w in warns:
            print(f"  [WARN] {w}")
        if not errs and not warns:
            print("  [OK] Structure acceptable")
        if errs or (args.strict and warns):
            any_err = True
    return 1 if any_err else 0


if __name__ == "__main__":
    sys.exit(main())
