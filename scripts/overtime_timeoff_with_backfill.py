#!/usr/bin/env python3
"""
Overtime TimeOff monthly pipeline wrapper

What this does (automates the correct workflow)
-----------------------------------------------
1) Ensure current month exports are readable by v10:
   - v10 reads *.xlsx and *.csv (NOT *.xls)
   - If only *.xls exist for the month, we convert using the existing
     xls_to_xlsx_archiver_com_multi.py (Excel COM) and verify *.xlsx exists.

2) Run the production script:
   - overtime_timeoff_13month_sworn_breakdown_v10.py
   - Produces output/FIXED_monthly_breakdown_{start}_{end}.csv (13 months)

3) Re-apply prior-month backfill to pin historical months:
   - Uses previous-month visual export (e.g., 2025_10 Monthly Accrual and Usage Summary)
   - Overwrites months present in that backfill (typically the prior 12 months)
   - Keeps the new month (e.g., 11-25) from the v10 run

This yields a FIXED file that Power Query can load with:
  - History from backfill (11-24 .. 10-25)
  - Current month from processing (11-25)
"""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

# Centralized path resolution (avoid hardcoded user paths)
try:
    from path_config import get_onedrive_root
except ImportError:
    # Fallback if path_config not found (e.g. running outside scripts dir)
    def get_onedrive_root() -> Path:
        base = os.environ.get("ONEDRIVE_BASE") or os.environ.get("ONEDRIVE_HACKENSACK")
        if base:
            return Path(base)
        return Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack")


@dataclass(frozen=True)
class Paths:
    overtime_timeoff_dir: Path
    overtime_dir: Path
    time_off_dir: Path
    backfill_root: Path
    v10_script: Path
    xls_to_xlsx_multi: Path
    restore_script: Path


def prev_month(d: date) -> date:
    """Return a date in the previous month (day=1)."""
    first = d.replace(day=1)
    last_prev = first - timedelta(days=1)
    return last_prev.replace(day=1)


def month_key_yyyy_mm(d: date) -> str:
    return f"{d.year:04d}_{d.month:02d}"


def month_key_yyyy_mm_dash(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def expected_fixed_filename(start_month: date, end_month: date) -> str:
    return f"FIXED_monthly_breakdown_{month_key_yyyy_mm_dash(start_month)}_{month_key_yyyy_mm_dash(end_month)}.csv"


def find_backfill_csv(backfill_root: Path, month: date) -> Path:
    """Find the prior-month backfill visual export. Checks Time_Off (process_powerbi_exports) then vcs_time_report (legacy)."""
    month_key = month_key_yyyy_mm(month)
    preferred_name = f"{month_key}_monthly_accrual_and_usage_summary.csv"
    alt_name = "Monthly Accrual and Usage Summary.csv"

    for folder_name in ("Time_Off", "vcs_time_report"):
        folder = backfill_root / month_key / folder_name
        if not folder.exists():
            continue
        for name in (preferred_name, alt_name):
            p = folder / name
            if p.exists():
                return p
        candidates = sorted(folder.glob("*onthly*ccrual*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
        if candidates:
            return candidates[0]

    raise FileNotFoundError(
        f"No Monthly Accrual CSV found in {backfill_root / month_key} (checked Time_Off, vcs_time_report)"
    )


def ensure_month_exports_are_xlsx(paths: Paths, run_month: date, dry_run: bool) -> None:
    """Ensure the month exports exist as .xlsx at the exact path. Convert .xls if necessary (no fallback search).

    Strict: only looks for YYYY_MM_otactivity.xlsx and YYYY_MM_timeoffactivity.xlsx in
    export/month/{year}/. Conversion .xls -> .xlsx is a distinct pre-step when .xlsx is missing.
    """
    year = run_month.year
    yyyymm = month_key_yyyy_mm(run_month)
    ot_subdir = paths.overtime_dir / "export" / "month" / str(year)
    to_subdir = paths.time_off_dir / "export" / "month" / str(year)

    ot_xlsx = ot_subdir / f"{yyyymm}_otactivity.xlsx"
    to_xlsx = to_subdir / f"{yyyymm}_timeoffactivity.xlsx"

    if ot_xlsx.exists() and to_xlsx.exists():
        print(f"[INFO] Found export files:\n  Overtime: {ot_xlsx}\n  Time Off: {to_xlsx}")
        return

    # Distinct pre-step: if .xlsx missing, try .xls and convert once
    ot_xls = ot_subdir / f"{yyyymm}_otactivity.xls"
    to_xls = to_subdir / f"{yyyymm}_timeoffactivity.xls"
    if (ot_xlsx.exists() or ot_xls.exists()) and (to_xlsx.exists() or to_xls.exists()):
        if dry_run:
            print(f"[DRY RUN] Would convert .xls -> .xlsx for month {yyyymm} (if needed).")
            return
        if not paths.xls_to_xlsx_multi.exists():
            raise FileNotFoundError(f"XLS->XLSX converter not found: {paths.xls_to_xlsx_multi}")
        print(f"[INFO] Converting exports to .xlsx for {yyyymm} (Excel COM)...")
        subprocess.check_call(
            [sys.executable, str(paths.xls_to_xlsx_multi), str(paths.overtime_dir), str(paths.time_off_dir)]
        )
        if not ot_xlsx.exists():
            raise FileNotFoundError(f"After conversion, Overtime .xlsx still missing: {ot_xlsx}")
        if not to_xlsx.exists():
            raise FileNotFoundError(f"After conversion, Time Off .xlsx still missing: {to_xlsx}")
        print(f"[INFO] Found export files after conversion:\n  Overtime: {ot_xlsx}\n  Time Off: {to_xlsx}")
        return

    raise FileNotFoundError(
        f"Required exports not found for {yyyymm}. Expected exactly:\n"
        f"  Overtime:   {ot_xlsx}\n"
        f"  Time Off:   {to_xlsx}\n"
        f"  (Or same base name with .xls for conversion.)"
    )


REQUIRED_FIXED_COLUMNS = {"Date", "Period", "Month", "Year", "Month_Name"}
EXPECTED_MONTH_COUNT = 13


def validate_fixed_schema(file_path: Path) -> None:
    """Validate FIXED CSV schema before exit. Raises ValueError if invalid (prevents bad data reaching Power BI)."""
    if not file_path.exists():
        raise FileNotFoundError(f"FIXED file not found: {file_path}")
    
    with file_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames or [])
    
    # Check for required columns (wide format with Date, Period, Month, etc.)
    missing = REQUIRED_FIXED_COLUMNS - headers
    if missing:
        raise ValueError(f"FIXED CSV missing required columns: {sorted(missing)}. Found: {sorted(headers)}")
    
    # Validate row count (should be exactly 13 months)
    row_count = 0
    with file_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_count += 1
            # Validate numeric columns (optional - check if any hours columns have valid numbers)
            for col in headers:
                if col in REQUIRED_FIXED_COLUMNS:
                    continue  # Skip date/period columns
                val = (row.get(col) or "").strip()
                if val != "" and val != "0":
                    try:
                        float(val)
                    except ValueError:
                        raise ValueError(f"FIXED CSV has non-numeric value in column {col}: {val!r}")
    
    if row_count != EXPECTED_MONTH_COUNT:
        raise ValueError(
            f"FIXED CSV must contain exactly {EXPECTED_MONTH_COUNT} rows (months); found {row_count}"
        )


def run_v10(paths: Paths, dry_run: bool) -> None:
    if dry_run:
        print(f"[DRY RUN] Would run v10: {paths.v10_script}")
        return
    subprocess.check_call([sys.executable, str(paths.v10_script)], cwd=str(paths.overtime_timeoff_dir))


def restore_fixed(paths: Paths, fixed_path: Path, backfill_csv: Path, dry_run: bool) -> None:
    if dry_run:
        print(f"[DRY RUN] Would restore FIXED from backfill:\n  FIXED={fixed_path}\n  Backfill={backfill_csv}")
        return
    subprocess.check_call(
        [sys.executable, str(paths.restore_script), "--fixed", str(fixed_path), "--backfill", str(backfill_csv), "--inplace"],
        cwd=str(paths.restore_script.parent),
    )


def _periodlabel_to_yearmonth(period_label: str) -> str:
    """Convert 'MM-YY' -> 'YYYY-MM'."""
    s = (period_label or "").strip()
    if len(s) != 5 or s[2] != "-":
        raise ValueError(f"Unexpected PeriodLabel format: {period_label!r}")
    mm = int(s[0:2])
    yy = int(s[3:5])
    yyyy = 2000 + yy
    return f"{yyyy:04d}-{mm:02d}"


def backfill_monthly_breakdown_from_backfill(
    backfill_csv: Path,
    analytics_folder: Path,
    start_month: date,
    end_month: date,
    dry_run: bool,
) -> None:
    """
    Ensure analytics_output/monthly_breakdown.csv has a full 13-month history for accrual rows
    by using the prior-month backfill export for months start_month..(end_month-1),
    and keeping end_month values from the v10 output if present.
    """
    target = analytics_folder / "monthly_breakdown.csv"

    # Build window list
    months: list[date] = []
    cur = start_month.replace(day=1)
    end = end_month.replace(day=1)
    while cur <= end:
        months.append(cur)
        cur = (cur.replace(day=28) + timedelta(days=4)).replace(day=1)  # next month
    window_set = {f"{m.year:04d}-{m.month:02d}" for m in months}

    # Read current (v10) monthly_breakdown if present to preserve end_month values.
    current_rows: dict[tuple[str, str, str], float] = {}
    if target.exists():
        with target.open("r", newline="", encoding="utf-8-sig") as f:
            r = csv.DictReader(f)
            for row in r:
                ym = (row.get("YearMonth") or "").strip()
                cls = (row.get("Class") or "").strip()
                met = (row.get("Metric") or "").strip()
                hrs = (row.get("Hours") or "").strip()
                if not ym or not cls or not met or hrs == "":
                    continue
                try:
                    v = float(hrs)
                except ValueError:
                    continue
                current_rows[(ym, cls, met)] = v

    # Parse backfill (WIDE expected; LONG also supported)
    with backfill_csv.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Backfill CSV has no headers")

        time_col = "Time_Category" if "Time_Category" in reader.fieldnames else ("Time Category" if "Time Category" in reader.fieldnames else None)
        if not time_col:
            raise ValueError(f"Backfill CSV missing Time_Category column. Found: {reader.fieldnames}")

        is_long = ("PeriodLabel" in reader.fieldnames) and any(c in reader.fieldnames for c in ("Value", "Sum of Value"))
        value_col = None
        if is_long:
            value_col = "Value" if "Value" in reader.fieldnames else "Sum of Value"

        # Collect accrual backfill values: (YearMonth, Class, Metric) -> Hours
        backfill_rows: dict[tuple[str, str, str], float] = {}

        def add_value(period_label: str, category: str, value: float) -> None:
            # Only accrual categories
            if not category.startswith("Accrued "):
                return
            # Skip window-external months
            ym = _periodlabel_to_yearmonth(period_label)
            if ym not in window_set:
                return
            # Map to monthly_breakdown schema
            metric = "Accrued Comp. Time" if category.startswith("Accrued Comp. Time") else "Accrued Overtime"
            cls = "NonSworn" if "Non-Sworn" in category else "Sworn"
            backfill_rows[(ym, cls, metric)] = float(value)

        if is_long:
            for row in reader:
                cat = (row.get(time_col) or "").strip()
                pl = (row.get("PeriodLabel") or "").strip()
                raw = (row.get(value_col) or "").strip()
                if not cat or not pl or raw == "":
                    continue
                try:
                    v = float(raw)
                except ValueError:
                    continue
                add_value(pl, cat, v)
        else:
            # WIDE: month columns + Time_Category column
            month_cols = [c for c in reader.fieldnames if c and c != time_col]
            for row in reader:
                cat = (row.get(time_col) or "").strip()
                if not cat:
                    continue
                for col in month_cols:
                    if col == time_col:
                        continue
                    pl = col.strip()
                    raw = (row.get(col) or "").strip()
                    if raw == "":
                        continue
                    try:
                        v = float(raw)
                    except ValueError:
                        continue
                    add_value(pl, cat, v)

    # Compose final file rows:
    # - For months prior to end_month: use backfill (must exist for full history)
    # - For end_month: prefer current (v10) values; fallback to backfill if missing
    end_ym = f"{end_month.year:04d}-{end_month.month:02d}"
    keys: list[tuple[str, str, str]] = []
    for m in months:
        ym = f"{m.year:04d}-{m.month:02d}"
        for cls in ("NonSworn", "Sworn"):
            for metric in ("Accrued Comp. Time", "Accrued Overtime"):
                keys.append((ym, cls, metric))

    out_lines: list[tuple[str, str, str, float]] = []
    missing: list[tuple[str, str, str]] = []
    for k in keys:
        ym, cls, metric = k
        if ym == end_ym and k in current_rows:
            out_lines.append((ym, cls, metric, current_rows[k]))
        elif k in backfill_rows:
            out_lines.append((ym, cls, metric, backfill_rows[k]))
        elif k in current_rows:
            out_lines.append((ym, cls, metric, current_rows[k]))
        else:
            missing.append(k)
            out_lines.append((ym, cls, metric, 0.0))

    if dry_run:
        print(f"[DRY RUN] Would write accrual history to: {target}")
        if missing:
            print(f"[DRY RUN][WARN] Missing accrual backfill values for {len(missing)} keys (will write 0.0).")
        return

    analytics_folder.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["YearMonth", "Class", "Metric", "Hours"])
        for ym, cls, metric, hrs in out_lines:
            w.writerow([ym, cls, metric, f"{hrs}"])

    print(f"[OK] monthly_breakdown.csv backfilled: {target}")
    if missing:
        print(f"[WARN] Missing accrual values for {len(missing)} month/class/metric keys; wrote 0.0 for those cells.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backfill-root",
        default=None,
        help="Root folder containing Backfill\\YYYY_MM\\vcs_time_report\\... (default: <OneDrive>\\PowerBI_Data\\Backfill)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without executing.")
    args = parser.parse_args()

    root = get_onedrive_root()
    overtime_timeoff_dir = root / "02_ETL_Scripts" / "Overtime_TimeOff"
    overtime_dir = root / "05_EXPORTS" / "_Overtime"
    time_off_dir = root / "05_EXPORTS" / "_Time_Off"
    backfill_root = Path(args.backfill_root) if args.backfill_root else root / "PowerBI_Data" / "Backfill"

    paths = Paths(
        overtime_timeoff_dir=overtime_timeoff_dir,
        overtime_dir=overtime_dir,
        time_off_dir=time_off_dir,
        backfill_root=backfill_root,
        v10_script=overtime_timeoff_dir / "overtime_timeoff_13month_sworn_breakdown_v10.py",
        xls_to_xlsx_multi=overtime_dir / "xls_to_xlsx_archiver_com_multi.py",
        restore_script=Path(__file__).resolve().parent / "restore_fixed_from_backfill.py",
    )

    today = date.today()
    # v10 window ends on previous month
    end_month = prev_month(today)
    start_month = end_month.replace(year=end_month.year - 1)  # 13-month window start month

    # Backfill should come from the CURRENT end_month (e.g., if end is 2025_12, backfill is 2025_12)
    # Try current month first, then fallback to previous month if current doesn't exist
    backfill_month = end_month
    backfill_folder = backfill_root / month_key_yyyy_mm(backfill_month) / "vcs_time_report"
    if not backfill_folder.exists():
        # Fallback to previous month's backfill
        backfill_month = prev_month(end_month)
        print(f"[INFO] Current month backfill not found, using previous month: {month_key_yyyy_mm(backfill_month)}")

    fixed_path = paths.overtime_timeoff_dir / "output" / expected_fixed_filename(start_month, end_month)

    print(f"[INFO] Window end month: {month_key_yyyy_mm_dash(end_month)}")
    print(f"[INFO] Expected FIXED: {fixed_path}")
    print(f"[INFO] Backfill month: {month_key_yyyy_mm(backfill_month)}")

    ensure_month_exports_are_xlsx(paths, end_month, dry_run=bool(args.dry_run))
    run_v10(paths, dry_run=bool(args.dry_run))

    if not fixed_path.exists() and not args.dry_run:
        # Fallback: pick newest FIXED file if name differs for any reason
        out_dir = paths.overtime_timeoff_dir / "output"
        candidates = sorted(out_dir.glob("FIXED_monthly_breakdown_*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not candidates:
            raise FileNotFoundError(f"No FIXED_monthly_breakdown_*.csv found in {out_dir}")
        fixed_path = candidates[0]
        print(f"[WARN] Expected FIXED not found; using newest: {fixed_path}")

    backfill_csv = find_backfill_csv(paths.backfill_root, backfill_month)
    print(f"[INFO] Using backfill CSV: {backfill_csv}")

    restore_fixed(paths, fixed_path=fixed_path, backfill_csv=backfill_csv, dry_run=bool(args.dry_run))

    # Backfill accrual history for the 13-month window so Power BI accrual rows are populated
    backfill_monthly_breakdown_from_backfill(
        backfill_csv=backfill_csv,
        analytics_folder=paths.overtime_timeoff_dir / "analytics_output",
        start_month=start_month,
        end_month=end_month,
        dry_run=bool(args.dry_run),
    )

    if not args.dry_run and fixed_path.exists():
        validate_fixed_schema(fixed_path)
        print("[OK] FIXED schema validated.")

    print("[OK] Pipeline complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


