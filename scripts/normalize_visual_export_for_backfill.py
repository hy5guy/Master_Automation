#!/usr/bin/env python3
"""
Normalize a Power BI visual export "Monthly Accrual and Usage Summary" for backfill.

Bridges the default export structure with what the pipeline expects:
- LONG (default): Time Category, Sum of Value, PeriodLabel — already accepted by
  restore_fixed_from_backfill.py and overtime_timeoff_with_backfill. This script
  normalizes column names and PeriodLabel values (e.g. "Sum of 11-25" -> "11-25").
- WIDE: optional output with months as columns for any consumer that expects it.

Usage:
  python scripts\\normalize_visual_export_for_backfill.py ^
    --input "path\\to\\2025_12_Monthly Accrual and Usage Summary.csv" ^
    [--backfill-month 2025_12] ^
    [--backfill-root "C:\\...\\PowerBI_Date\\Backfill"] ^
    [--wide] ^
    [--dry-run]

If --backfill-month is omitted, it is inferred from the filename (e.g. 2025_12_...)
or from the latest period in the data (MM-YY -> 20YY-MM).
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from pathlib import Path
from typing import List, Optional, Tuple

try:
    from path_config import get_onedrive_root
except ImportError:
    def get_onedrive_root() -> Path:
        base = os.environ.get("ONEDRIVE_BASE") or os.environ.get("ONEDRIVE_HACKENSACK")
        if base:
            return Path(base)
        return Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack")


def _default_backfill_root() -> Path:
    """Backfill root (PowerBI_Date\\Backfill) using centralized path config."""
    return get_onedrive_root() / "PowerBI_Date" / "Backfill"


# Column names the pipeline expects (restore_fixed_from_backfill, backfill_monthly_breakdown)
TIME_CAT_CANDIDATES = ("Time_Category", "Time Category", "TimeCategory")
VALUE_CANDIDATES = ("Value", "Sum of Value", "Sum ofValue", "Sum of  Value")
PERIOD_LABEL_COL = "PeriodLabel"
VCS_TIME_REPORT = "vcs_time_report"
BACKFILL_FILENAME = "Monthly Accrual and Usage Summary.csv"


def _norm_month_label(label: str) -> str:
    """Normalize 'Sum of 11-25' -> '11-25', trim whitespace."""
    s = (label or "").strip()
    if not s:
        return s
    s_lower = s.lower()
    if s_lower.startswith("sum of "):
        s = s[7:].strip()
    return s


def _period_label_to_year_month(period_label: str) -> Optional[Tuple[int, int]]:
    """Parse MM-YY or similar to (year, month). Returns None if invalid."""
    s = _norm_month_label(period_label)
    if not s or len(s) < 5:
        return None
    # MM-YY or M-YY
    parts = s.split("-")
    if len(parts) != 2:
        return None
    try:
        mm = int(parts[0].strip())
        yy = int(parts[1].strip())
        if yy < 100:
            year = 2000 + yy
        else:
            year = yy
        if 1 <= mm <= 12 and year >= 2000:
            return (year, mm)
    except ValueError:
        pass
    return None


def _infer_backfill_month_from_filename(path: Path) -> Optional[str]:
    """e.g. 2025_12_Monthly Accrual... or Monthly Accrual..._2025_12.csv -> 2025_12."""
    name = path.stem
    # 2025_12_...
    m = re.match(r"^(\d{4}_\d{2})_", name)
    if m:
        return m.group(1)
    # ..._2025_12
    m = re.search(r"_(\d{4}_\d{2})(?:\.[^.]+)?$", name)
    if m:
        return m.group(1)
    return None


def detect_format(reader: csv.DictReader) -> Tuple[str, Optional[str], Optional[str]]:
    """Returns (format, time_col, value_col). format is 'long' or 'wide'."""
    names = [c for c in (reader.fieldnames or []) if c]
    time_col = None
    for c in TIME_CAT_CANDIDATES:
        if c in names:
            time_col = c
            break
    if not time_col:
        return "unknown", None, None

    if PERIOD_LABEL_COL in names:
        value_col = None
        for c in VALUE_CANDIDATES:
            if c in names:
                value_col = c
                break
        if value_col:
            return "long", time_col, value_col

    # Wide: first column is time, rest are month-like (e.g. 01-25, 11-24)
    month_cols = [c for c in names if c != time_col and _period_label_to_year_month(_norm_month_label(c))]
    if month_cols:
        return "wide", time_col, None

    return "unknown", time_col, None


def normalize_long(
    input_path: Path,
    time_col: str,
    value_col: str,
    output_path: Path,
    dry_run: bool,
) -> None:
    """Read Long CSV, normalize labels and column names, write standard Long."""
    rows_out: List[dict] = []
    with input_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat = (row.get(time_col) or "").strip()
            pl_raw = (row.get(PERIOD_LABEL_COL) or "").strip()
            pl = _norm_month_label(pl_raw)
            val = (row.get(value_col) or "").strip()
            if not cat or not pl:
                continue
            rows_out.append({
                "Time Category": cat,
                "Sum of Value": val,
                "PeriodLabel": pl,
            })

    if dry_run:
        print(f"[DRY RUN] Would write {len(rows_out)} rows to {output_path}")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Time Category", "Sum of Value", "PeriodLabel"])
        w.writeheader()
        w.writerows(rows_out)
    print(f"[OK] Wrote {len(rows_out)} rows -> {output_path}")


def normalize_wide(
    input_path: Path,
    time_col: str,
    output_path: Path,
    dry_run: bool,
) -> None:
    """Read Wide CSV, normalize column headers (Sum of 01-25 -> 01-25), write Wide."""
    with input_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        names = list(reader.fieldnames or [])
        rows = list(reader)

    # Normalize header: Time Category + month columns
    new_names = [time_col if n == time_col else _norm_month_label(n) or n for n in names]
    # Keep column order; use first row to build dict keys
    fieldnames = [n for n in new_names if n]

    if dry_run:
        print(f"[DRY RUN] Would write Wide {len(rows)} rows, columns {fieldnames[:5]}... -> {output_path}")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            new_row = {}
            for old_name, new_name in zip(names, new_names):
                if new_name and old_name in row:
                    new_row[new_name] = row[old_name]
            w.writerow(new_row)
    print(f"[OK] Wrote Wide {len(rows)} rows -> {output_path}")


def long_to_wide(input_path: Path, time_col: str, value_col: str, output_path: Path, dry_run: bool) -> None:
    """Pivot Long to Wide: one row per Time Category, columns = PeriodLabel."""
    by_cat: dict[str, dict[str, str]] = {}
    periods: List[str] = []
    with input_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat = (row.get(time_col) or "").strip()
            pl = _norm_month_label((row.get(PERIOD_LABEL_COL) or "").strip())
            val = (row.get(value_col) or "").strip()
            if not cat or not pl:
                continue
            if pl not in periods:
                periods.append(pl)
            by_cat.setdefault(cat, {})[pl] = val

    # Sort periods chronologically (MM-YY)
    def period_key(p: str) -> Tuple[int, int]:
        t = _period_label_to_year_month(p)
        return t if t else (0, 0)

    periods.sort(key=period_key)
    fieldnames = ["Time Category"] + periods

    if dry_run:
        print(f"[DRY RUN] Would write Wide {len(by_cat)} rows, columns {len(periods)} months -> {output_path}")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for cat in sorted(by_cat.keys()):
            row = {"Time Category": cat, **by_cat[cat]}
            w.writerow(row)
    print(f"[OK] Wrote Wide {len(by_cat)} rows -> {output_path}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Normalize Monthly Accrual and Usage Summary export for backfill.")
    ap.add_argument("--input", "-i", required=True, type=Path, help="Input CSV (Long or Wide export)")
    ap.add_argument(
        "--backfill-month",
        type=str,
        default=None,
        help="YYYY_MM (e.g. 2025_12). Inferred from filename or data if omitted.",
    )
    ap.add_argument(
        "--backfill-root",
        type=Path,
        default=None,
        help="Backfill root folder (default: <OneDrive>\\PowerBI_Date\\Backfill)",
    )
    ap.add_argument(
        "--wide",
        action="store_true",
        help="Output Wide format (months as columns). Default is Long.",
    )
    ap.add_argument("--dry-run", action="store_true", help="Do not write files.")
    ap.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Explicit output path. If set, --backfill-month and --backfill-root are ignored.",
    )
    args = ap.parse_args()

    input_path = args.input.resolve()
    if not input_path.exists():
        print(f"[ERROR] Input not found: {input_path}")
        return 1

    with input_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fmt, time_col, value_col = detect_format(reader)

    if fmt == "unknown" or not time_col:
        print("[ERROR] Could not detect Long or Wide format or Time Category column.")
        return 1

    backfill_root = args.backfill_root if args.backfill_root is not None else _default_backfill_root()

    if args.output is not None:
        output_path = args.output.resolve()
    else:
        backfill_month = args.backfill_month or _infer_backfill_month_from_filename(input_path)
        if not backfill_month:
            # Infer from latest period in data
            with input_path.open("r", newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                latest = None
                for row in reader:
                    if fmt == "long" and value_col:
                        pl = _norm_month_label((row.get(PERIOD_LABEL_COL) or "").strip())
                    else:
                        for col in (reader.fieldnames or []):
                            if col != time_col:
                                pl = _norm_month_label(col)
                                break
                        else:
                            pl = ""
                    t = _period_label_to_year_month(pl) if pl else None
                    if t and (latest is None or t > latest):
                        latest = t
                if latest:
                    y, m = latest
                    backfill_month = f"{y:04d}_{m:02d}"
            if not backfill_month:
                print("[ERROR] Could not infer backfill month. Use --backfill-month YYYY_MM or --output path.")
                return 1
        # Standard name: YYYY_MM_Monthly Accrual and Usage Summary.csv
        out_name = f"{backfill_month}_{BACKFILL_FILENAME}"
        output_path = (backfill_root / backfill_month / VCS_TIME_REPORT / out_name).resolve()
        print(f"[INFO] Backfill month: {backfill_month} -> {output_path}")

    if fmt == "long" and value_col:
        if args.wide:
            long_to_wide(input_path, time_col, value_col, output_path, args.dry_run)
        else:
            normalize_long(input_path, time_col, value_col, output_path, args.dry_run)
    else:
        if args.wide:
            normalize_wide(input_path, time_col, output_path, args.dry_run)
        else:
            # Wide input -> convert to Long for consistency (pipeline accepts both)
            # For simplicity we only support Long input -> Long or Wide output here.
            # Wide input -> Long would require unpivot; pipeline already accepts Wide.
            print("[INFO] Input is Wide; writing as-is (pipeline accepts Wide). Use --wide to keep Wide.")
            normalize_wide(input_path, time_col, output_path, args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
