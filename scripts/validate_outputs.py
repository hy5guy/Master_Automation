#!/usr/bin/env python3
"""
Validate Overtime/TimeOff pipeline output (FIXED CSV schema).

Checks that the FIXED_monthly_breakdown_*.csv has required columns (YearMonth, Class, Metric, Hours),
exactly 13 unique months, and numeric Hours. Use after a full pipeline run.

Usage:
  python scripts/validate_outputs.py [--fixed path/to/FIXED_monthly_breakdown_*.csv]
  If --fixed is omitted, infers path from previous month and default output dir.
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date, timedelta
from pathlib import Path

REQUIRED_COLUMNS = {"YearMonth", "Class", "Metric", "Hours"}
EXPECTED_MONTH_COUNT = 13
EXIT_OK = 0
EXIT_FAIL = 1

try:
    from path_config import get_onedrive_root
except ImportError:
    def get_onedrive_root() -> Path:
        base = os.environ.get("ONEDRIVE_BASE") or os.environ.get("ONEDRIVE_HACKENSACK")
        if base:
            return Path(base)
        return Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack")


def get_overtime_timeoff_dir() -> Path:
    """02_ETL_Scripts/Overtime_TimeOff under OneDrive root."""
    return get_onedrive_root() / "02_ETL_Scripts" / "Overtime_TimeOff"


def prev_month(d: date) -> date:
    first = d.replace(day=1)
    last_prev = first - timedelta(days=1)
    return last_prev.replace(day=1)


def validate_fixed_schema(file_path: Path) -> None:
    """Validate FIXED CSV. Raises ValueError if invalid."""
    if not file_path.exists():
        raise FileNotFoundError(f"FIXED file not found: {file_path}")
    with file_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames or [])
    missing = REQUIRED_COLUMNS - headers
    if missing:
        raise ValueError(f"FIXED CSV missing required columns: {sorted(missing)}. Found: {sorted(headers)}")

    months: set[str] = set()
    with file_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ym = (row.get("YearMonth") or "").strip()
            if ym:
                months.add(ym)
            hrs = (row.get("Hours") or "").strip()
            if hrs != "":
                try:
                    float(hrs)
                except ValueError:
                    raise ValueError(f"FIXED CSV has non-numeric Hours value: {hrs!r}")

    if len(months) != EXPECTED_MONTH_COUNT:
        raise ValueError(
            f"FIXED CSV must contain exactly {EXPECTED_MONTH_COUNT} unique YearMonth values; found {len(months)}: {sorted(months)}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Overtime/TimeOff FIXED output schema.")
    parser.add_argument(
        "--fixed",
        type=Path,
        default=None,
        help="Path to FIXED_monthly_breakdown_*.csv (default: infer from previous month).",
    )
    args = parser.parse_args()

    if args.fixed is not None:
        fixed_path = args.fixed.resolve()
    else:
        today = date.today()
        end_month = prev_month(today)
        start_month = end_month.replace(year=end_month.year - 1)
        start_str = f"{start_month.year:04d}-{start_month.month:02d}"
        end_str = f"{end_month.year:04d}-{end_month.month:02d}"
        filename = f"FIXED_monthly_breakdown_{start_str}_{end_str}.csv"
        ot_dir = get_overtime_timeoff_dir()
        fixed_path = (ot_dir / "output" / filename).resolve()
        print(f"[INFO] No --fixed specified; using inferred path: {fixed_path}")

    if not fixed_path.exists():
        print(f"[ERROR] FIXED file not found: {fixed_path}")
        print("Run the Overtime/TimeOff pipeline first, then run this validation.")
        return EXIT_FAIL

    try:
        validate_fixed_schema(fixed_path)
        print("[OK] FIXED schema validated: required columns present, 13 months, numeric Hours.")
        return EXIT_OK
    except (ValueError, FileNotFoundError) as e:
        print(f"[ERROR] Validation failed: {e}")
        return EXIT_FAIL


if __name__ == "__main__":
    sys.exit(main())
