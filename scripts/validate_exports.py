#!/usr/bin/env python3
"""
Pre-flight validation for Overtime/TimeOff pipeline.

Checks that required Excel exports exist at the exact paths and are readable
with required columns: Date, Hours, Employee, Group.
Fail-fast with clear exit code if missing or invalid.

Usage:
  python scripts/validate_exports.py [--year-month YYYY_MM]
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import date
from pathlib import Path

REQUIRED_COLUMNS = {"Date", "Hours", "Employee", "Group"}
EXIT_OK = 0
EXIT_MISSING = 1
EXIT_INVALID = 2

try:
    from path_config import get_onedrive_root
except ImportError:
    def get_onedrive_root() -> Path:
        base = os.environ.get("ONEDRIVE_BASE") or os.environ.get("ONEDRIVE_HACKENSACK")
        if base:
            return Path(base)
        return Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack")


def get_exports_base() -> Path:
    """05_EXPORTS under OneDrive root (centralized with ETL paths)."""
    return get_onedrive_root() / "05_EXPORTS"


def log(msg: str) -> None:
    print(f"[{date.today().isoformat()}] {msg}")


def is_visual_export_path(path: Path) -> bool:
    """True if path looks like a Power BI visual export (skip Excel column validation)."""
    name = path.name
    if (path.suffix or "").lower() == ".csv":
        return True
    if "Monthly Accrual" in name:
        return True
    return False


def validate_excel_columns(path: Path, required: set[str]) -> None:
    """Ensure the Excel file is readable and contains required columns. Raises ValueError if not.
    Retries on PermissionError/OSError (e.g. OneDrive sync lock) up to 3 times with 2s delay.
    Skips validation (returns without error) for known visual export filenames (e.g. Monthly Accrual, CSV).
    """
    if is_visual_export_path(path):
        return
    try:
        import pandas as pd
    except ImportError as e:
        raise ValueError("pandas is required to validate Excel files") from e

    last_error = None
    for attempt in range(3):
        try:
            # nrows=0 avoids mixed-type/dtype warnings; we only need headers
            df = pd.read_excel(path, nrows=0)
            found = {str(c).strip() for c in df.columns if c is not None}
            break
        except (PermissionError, OSError) as e:
            last_error = e
            if attempt < 2:
                time.sleep(2)
            else:
                raise ValueError(f"Could not read Excel file (retried 3x; possible OneDrive sync lock): {e}") from e
        except Exception as e:
            raise ValueError(f"Could not read Excel file: {e}") from e
    else:
        if last_error:
            raise ValueError(f"Could not read Excel file: {last_error}") from last_error

    missing = required - found
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}. Found: {sorted(found)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-flight check for Overtime/TimeOff exports.")
    parser.add_argument(
        "--year-month",
        default=None,
        help="Target month as YYYY_MM (default: previous month from today).",
    )
    parser.add_argument(
        "--exports-base",
        type=Path,
        default=None,
        help="Base path for 05_EXPORTS (default: ONEDRIVE_BASE/05_EXPORTS or built-in default).",
    )
    args = parser.parse_args()

    # Resolve target month
    if args.year_month:
        parts = args.year_month.strip().split("_")
        if len(parts) != 2:
            log(f"ERROR: --year-month must be YYYY_MM, got {args.year_month!r}")
            return EXIT_INVALID
        try:
            year = int(parts[0])
            month = int(parts[1])
            if not (1 <= month <= 12 and year >= 2000):
                raise ValueError("Invalid month or year")
        except ValueError as e:
            log(f"ERROR: Invalid --year-month: {e}")
            return EXIT_INVALID
    else:
        today = date.today()
        first = today.replace(day=1)
        prev = (first.replace(month=first.month - 1) if first.month > 1 else first.replace(year=first.year - 1, month=12))
        year, month = prev.year, prev.month

    yyyy_mm = f"{year:04d}_{month:02d}"
    if args.year_month:
        log(f"Target month specified via argument: {yyyy_mm}")
    else:
        log(f"Target month inferred (previous month): {yyyy_mm}")

    base = args.exports_base or get_exports_base()
    overtime_dir = base / "_Overtime" / "export" / "month" / str(year)
    time_off_dir = base / "_Time_Off" / "export" / "month" / str(year)
    ot_file = overtime_dir / f"{yyyy_mm}_otactivity.xlsx"
    to_file = time_off_dir / f"{yyyy_mm}_timeoffactivity.xlsx"

    log(f"Validating exports for {yyyy_mm}")
    log(f"  Overtime:   {ot_file}")
    log(f"  Time Off:   {to_file}")

    # 1. Existence
    if not ot_file.exists():
        log(f"ERROR: Overtime export not found: {ot_file}")
        return EXIT_MISSING
    if not to_file.exists():
        log(f"ERROR: Time Off export not found: {to_file}")
        return EXIT_MISSING

    # 2. Readable and required columns
    for label, path in [("Overtime", ot_file), ("Time Off", to_file)]:
        try:
            validate_excel_columns(path, REQUIRED_COLUMNS)
        except ValueError as e:
            log(f"ERROR: {label} file invalid: {e}")
            return EXIT_INVALID

    log("OK: Both exports exist and contain required columns (Date, Hours, Employee, Group).")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
