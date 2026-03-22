#!/usr/bin/env python3
"""
restore_fixed_from_backfill.py

Populates historical months in a FIXED_monthly_breakdown_*.csv using a Power BI
visual export "Monthly Accrual and Usage Summary" backfill CSV.

Why this fixes your Power BI issue
----------------------------------
Your Overtime/TimeDue M query uses FIXED_monthly_breakdown for NON-accrual rows:
  - Comp (Hours)
  - Employee Sick Time (Hours)
  - Injured on Duty (Hours)
  - Military Leave (Hours)
  - Used SAT Time (Hours)

If FIXED has zeros for historical months (11-24 .. 09-25), those rows show as
0/null in the visual. This script overwrites those FIXED columns for any month
label present in the backfill export (e.g., 10-24 .. 10-25).

Usage (PowerShell)
------------------
python .\\scripts\\restore_fixed_from_backfill.py `
  --fixed \"C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\02_ETL_Scripts\\Overtime_TimeOff\\output\\FIXED_monthly_breakdown_2024-11_2025-11.csv\" `
  --backfill \"C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\PowerBI_Data\\Backfill\\2025_10\\vcs_time_report\\2025_10_Monthly Accrual and Usage Summary.csv\" `
  --inplace

Notes
-----
- Creates a `.bak` backup alongside the FIXED file when using `--inplace`.
- If the backfill export does NOT contain a month label (e.g. "11-25"), that
  row is skipped (you need the newer backfill export that includes that month).
"""

from __future__ import annotations

import argparse
import csv
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _norm_month_label(label: str) -> str:
    """Normalize labels like 'Sum of 11-25' -> '11-25' and trim whitespace."""
    s = (label or "").strip()
    if not s:
        return s
    s_lower = s.lower()
    if s_lower.startswith("sum of "):
        s = s[7:].strip()
    return s


def _period_to_mmyy(period_yyyy_mm: str) -> str:
    """Convert 'YYYY-MM' -> 'MM-YY'."""
    yyyy, mm = period_yyyy_mm.split("-")
    return f"{mm}-{yyyy[2:]}"


@dataclass(frozen=True)
class BackfillValues:
    by_category: Dict[str, Dict[str, float]]

    def get(self, category: str, label: str) -> Optional[float]:
        d = self.by_category.get(category)
        if not d:
            return None
        return d.get(label)


def load_backfill_csv(path: Path) -> BackfillValues:
    if not path.exists():
        raise FileNotFoundError(f"Backfill CSV not found: {path}")

    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Backfill CSV has no headers")

        # Detect Time Category column name
        time_col = None
        for candidate in ("Time_Category", "Time Category", "TimeCategory"):
            if candidate in reader.fieldnames:
                time_col = candidate
                break
        if not time_col:
            raise ValueError(
                f"Backfill CSV missing Time Category column. Found: {reader.fieldnames}"
            )

        # Support TWO export shapes:
        # 1) WIDE (legacy visual export): one row per category, month labels as columns
        #    e.g. Time_Category,10-24,11-24,...,10-25
        # 2) LONG (table export from a long query): one row per (category, periodlabel)
        #    e.g. Time_Category,Sum of Value,PeriodLabel
        is_long = ("PeriodLabel" in reader.fieldnames) and (
            "Value" in reader.fieldnames
            or "Sum of Value" in reader.fieldnames
            or "Sum ofValue" in reader.fieldnames
            or "Sum of  Value" in reader.fieldnames
        )

        by_cat: Dict[str, Dict[str, float]] = {}

        if is_long:
            # Find value column
            value_col = None
            for candidate in ("Value", "Sum of Value", "Sum ofValue", "Sum of  Value"):
                if candidate in reader.fieldnames:
                    value_col = candidate
                    break
            if not value_col:
                raise ValueError(f"Backfill LONG CSV missing value column. Found: {reader.fieldnames}")

            for row in reader:
                cat = (row.get(time_col) or "").strip()
                if not cat:
                    continue
                label = _norm_month_label((row.get("PeriodLabel") or "").strip())
                if not label:
                    continue
                raw_val = (row.get(value_col) or "").strip()
                if raw_val == "":
                    continue
                try:
                    val = float(raw_val)
                except ValueError:
                    continue
                by_cat.setdefault(cat, {})[label] = val
        else:
            month_cols: List[Tuple[str, str]] = []
            for col in reader.fieldnames:
                if col == time_col:
                    continue
                month_cols.append((col, _norm_month_label(col)))

            for row in reader:
                cat = (row.get(time_col) or "").strip()
                if not cat:
                    continue
                out: Dict[str, float] = {}
                for raw_col, norm_col in month_cols:
                    raw_val = (row.get(raw_col) or "").strip()
                    if raw_val == "":
                        continue
                    try:
                        out[norm_col] = float(raw_val)
                    except ValueError:
                        continue
                by_cat[cat] = out

    return BackfillValues(by_category=by_cat)


def read_fixed_rows(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    if not path.exists():
        raise FileNotFoundError(f"FIXED CSV not found: {path}")
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("FIXED CSV has no headers")
        rows = list(reader)
        return list(reader.fieldnames), rows


def write_fixed_rows(path: Path, fieldnames: List[str], rows: List[Dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def restore_fixed_from_backfill(
    fixed_path: Path, backfill_path: Path, inplace: bool, include_accruals: bool
) -> Path:
    backfill = load_backfill_csv(backfill_path)
    fieldnames, rows = read_fixed_rows(fixed_path)

    required_fixed_cols = [
        "Period",
        "Accrued_Comp_Time",
        "Accrued_Overtime_Paid",
        "Employee_Sick_Time_Hours",
        "Used_SAT_Time_Hours",
        "Used_Comp_Time",
        "Military_Leave_Hours",
        "Injured_on_Duty_Hours",
        "Vacation_Hours",
    ]
    missing_fixed = [c for c in required_fixed_cols if c not in fieldnames]
    if missing_fixed:
        raise ValueError(f"FIXED CSV missing required columns: {missing_fixed}")

    legacy_map = {
        "Employee Sick Time (Hours)": "Employee_Sick_Time_Hours",
        "Used SAT Time (Hours)": "Used_SAT_Time_Hours",
        "Comp (Hours)": "Used_Comp_Time",
        "Military Leave (Hours)": "Military_Leave_Hours",
        "Injured on Duty (Hours)": "Injured_on_Duty_Hours",
        "Vacation (Hours)": "Vacation_Hours",
    }

    accrual_pairs = {
        "Accrued_Comp_Time": (
            "Accrued Comp. Time - Non-Sworn",
            "Accrued Comp. Time - Sworn",
        ),
        "Accrued_Overtime_Paid": (
            "Accrued Overtime - Non-Sworn",
            "Accrued Overtime - Sworn",
        ),
    }

    updated_rows = 0
    updated_cells = 0
    for r in rows:
        period = (r.get("Period") or "").strip()
        if not period:
            continue
        label = _period_to_mmyy(period)

        row_changed = False
        for backfill_cat, fixed_col in legacy_map.items():
            val = backfill.get(backfill_cat, label)
            if val is None:
                continue
            r[fixed_col] = f"{val}"
            row_changed = True
            updated_cells += 1

        # Optional: restore accrual totals from the backfill export.
        # Disabled by default because some exports may have accrual history as 0
        # (e.g., exported from a visual that was already broken).
        if include_accruals:
            for fixed_col, (cat_a, cat_b) in accrual_pairs.items():
                a = backfill.get(cat_a, label)
                b = backfill.get(cat_b, label)
                if a is None or b is None:
                    continue
                r[fixed_col] = f"{(a + b)}"
                row_changed = True
                updated_cells += 1

        if row_changed:
            updated_rows += 1

    if inplace:
        backup = fixed_path.with_suffix(fixed_path.suffix + ".bak")
        shutil.copy2(fixed_path, backup)
        out_path = fixed_path
    else:
        out_path = fixed_path.with_name(fixed_path.stem + "_RESTORED.csv")
        backup = None

    write_fixed_rows(out_path, fieldnames, rows)

    print(f"[OK] Backfill used: {backfill_path}")
    if backup:
        print(f"[OK] Backup created: {backup}")
    print(f"[OK] FIXED written: {out_path}")
    print(f"[OK] Rows updated: {updated_rows}/{len(rows)}")
    print(f"[OK] Cells updated: {updated_cells}")
    if not include_accruals:
        print("[INFO] Accrual totals were NOT restored from backfill (legacy categories only).")

    return out_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed", required=True, help="Path to FIXED_monthly_breakdown_*.csv")
    parser.add_argument("--backfill", required=True, help="Path to backfill visual export CSV")
    parser.add_argument("--inplace", action="store_true", help="Overwrite FIXED file (creates .bak)")
    parser.add_argument(
        "--include-accruals",
        action="store_true",
        help="Also restore Accrued_Comp_Time and Accrued_Overtime_Paid totals from backfill export.",
    )
    args = parser.parse_args()

    restore_fixed_from_backfill(
        Path(args.fixed),
        Path(args.backfill),
        bool(args.inplace),
        bool(args.include_accruals),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


