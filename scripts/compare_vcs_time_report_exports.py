#!/usr/bin/env python3
"""
Compare two "Monthly Accrual and Usage Summary" exports.

Supports both shapes:
- WIDE: one row per Time_Category, month labels as columns (e.g. 11-24, 12-24, ...),
        sometimes with headers like "Sum of 11-25".
- LONG: one row per (Time_Category, PeriodLabel) with a value column
        (e.g. Time_Category, Sum of Value, PeriodLabel).
"""

from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path
from typing import Dict, Iterable, Tuple


MONTH_RE = re.compile(r"^(?:Sum of\s+)?(\d{2}-\d{2})$")
MMMYY_RE = re.compile(r"^(\d{2})-([A-Za-z]{3})$")
MMM_TO_MM = {
    "jan": "01",
    "feb": "02",
    "mar": "03",
    "apr": "04",
    "may": "05",
    "jun": "06",
    "jul": "07",
    "aug": "08",
    "sep": "09",
    "oct": "10",
    "nov": "11",
    "dec": "12",
}


def norm_month_label(s: str) -> str:
    s = (s or "").strip()
    m = MONTH_RE.match(s)
    if not m:
        m2 = MMMYY_RE.match(s)
        if m2:
            yy = m2.group(1)
            mon = MMM_TO_MM.get(m2.group(2).lower())
            if mon:
                return f"{mon}-{yy}"
        return s
    return m.group(1)


def load_any_export(path: Path) -> Dict[Tuple[str, str], float]:
    """
    Return mapping: (Time_Category, PeriodLabel) -> value
    """
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        if not r.fieldnames:
            raise ValueError(f"{path} has no headers")

        fields = set(r.fieldnames)

        time_col = None
        for c in ("Time_Category", "Time Category", "TimeCategory"):
            if c in fields:
                time_col = c
                break
        if not time_col:
            raise ValueError(f"{path} missing Time_Category column. Found: {r.fieldnames}")

        is_long = "PeriodLabel" in fields and (
            "Value" in fields or "Sum of Value" in fields or "Sum ofValue" in fields or "Sum of  Value" in fields
        )

        out: Dict[Tuple[str, str], float] = {}

        if is_long:
            val_col = None
            for c in ("Value", "Sum of Value", "Sum ofValue", "Sum of  Value"):
                if c in fields:
                    val_col = c
                    break
            if not val_col:
                raise ValueError(f"{path} long format but no value column found. Found: {r.fieldnames}")

            for row in r:
                cat = (row.get(time_col) or "").strip()
                pl = norm_month_label(row.get("PeriodLabel") or "")
                raw = (row.get(val_col) or "").strip()
                if not cat or not pl or raw == "":
                    continue
                try:
                    v = float(raw)
                except ValueError:
                    continue
                out[(cat, pl)] = v
            return out

        # WIDE
        month_cols = []
        for col in r.fieldnames:
            if col == time_col:
                continue
            c = (col or "").strip()
            if MONTH_RE.match(c) or MMMYY_RE.match(c):
                month_cols.append(col)

        for row in r:
            cat = (row.get(time_col) or "").strip()
            if not cat:
                continue
            for col in month_cols:
                pl = norm_month_label(col)
                raw = (row.get(col) or "").strip()
                if raw == "":
                    continue
                try:
                    v = float(raw)
                except ValueError:
                    continue
                out[(cat, pl)] = v
        return out


def fmt_float(x: float) -> str:
    if x is None:
        return "∅"
    if math.isfinite(x) and abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f"{x:.6g}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="Path to export A (ref)")
    ap.add_argument("--b", required=True, help="Path to export B (compare)")
    ap.add_argument(
        "--months",
        default="11-24,12-24,01-25,02-25,03-25,04-25,05-25,06-25,07-25,08-25,09-25,10-25",
        help="Comma-separated PeriodLabel months to compare (MM-YY). Default is 11-24..10-25.",
    )
    ap.add_argument("--tolerance", type=float, default=1e-6, help="Numeric tolerance for comparisons.")
    args = ap.parse_args()

    a_path = Path(args.a)
    b_path = Path(args.b)
    months = [m.strip() for m in (args.months or "").split(",") if m.strip()]
    month_set = set(months)

    A = load_any_export(a_path)
    B = load_any_export(b_path)

    cats = sorted({c for (c, m) in set(A.keys()) | set(B.keys()) if m in month_set})
    if not cats:
        print("[WARN] No rows found for requested months in either file.")
        return 0

    missing_in_a = []
    missing_in_b = []
    diffs = []

    for cat in cats:
        for m in months:
            ka = (cat, m)
            va = A.get(ka)
            vb = B.get(ka)
            if va is None:
                missing_in_a.append(ka)
                continue
            if vb is None:
                missing_in_b.append(ka)
                continue
            if abs(va - vb) > args.tolerance:
                diffs.append((cat, m, va, vb, vb - va))

    print("=== Comparison Summary ===")
    print(f"A: {a_path}")
    print(f"B: {b_path}")
    print(f"Months compared: {', '.join(months)}")
    print(f"Categories seen: {len(cats)}")
    print(f"Missing in A: {len(missing_in_a)}")
    print(f"Missing in B: {len(missing_in_b)}")
    print(f"Value diffs (>|tol|): {len(diffs)} (tol={args.tolerance})")

    if missing_in_a:
        print("\n--- Missing in A (first 25) ---")
        for cat, m in missing_in_a[:25]:
            print(f"{m}\t{cat}")
        if len(missing_in_a) > 25:
            print(f"... ({len(missing_in_a) - 25} more)")

    if missing_in_b:
        print("\n--- Missing in B (first 25) ---")
        for cat, m in missing_in_b[:25]:
            print(f"{m}\t{cat}")
        if len(missing_in_b) > 25:
            print(f"... ({len(missing_in_b) - 25} more)")

    if diffs:
        print("\n--- Diffs (first 50) ---")
        for cat, m, va, vb, d in diffs[:50]:
            print(f"{m}\t{cat}\tA={fmt_float(va)}\tB={fmt_float(vb)}\t(B-A)={fmt_float(d)}")
        if len(diffs) > 50:
            print(f"... ({len(diffs) - 50} more)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


