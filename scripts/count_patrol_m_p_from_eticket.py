#!/usr/bin/env python3
"""
Count Moving (M) vs Parking (P) tickets in a raw e-ticket export for officers assigned to Patrol.

Logic:
- Parse the raw e-ticket export (semicolon-delimited payload lines, often CSV-wrapped in quotes)
- Normalize Officer Id -> 4-digit string
- Load Assignment_Master_V2.csv and select badges where WG2 == PATROL BUREAU
- Count Case Type Code in {M, P} for those Patrol-assigned officers
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_raw_eticket(path: Path) -> pd.DataFrame:
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        header_line = f.readline().rstrip("\n")
        header = header_line.split(";")
        rows = []
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            # Most rows are a quoted payload plus trailing commas:  "a;b;c;...;z",,,,,
            if line.startswith('"'):
                # take content inside first pair of quotes
                try:
                    inner = line.split('"', 2)[1]
                except Exception:
                    inner = line.strip('"')
                parts = inner.split(";")
            else:
                parts = line.split(";")
            if len(parts) < 10:
                continue
            row = dict(zip(header, parts + [""] * max(0, len(header) - len(parts))))
            rows.append(row)
    return pd.DataFrame(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--eticket", required=True, help="Path to raw YYYY_MM_eticket_export.csv (e.g., 2025_12_eticket_export.csv)")
    ap.add_argument(
        "--assignment",
        default=r"C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv",
        help="Path to Assignment_Master_V2.csv",
    )
    args = ap.parse_args()

    et_path = Path(args.eticket)
    am_path = Path(args.assignment)

    et = parse_raw_eticket(et_path)
    if et.empty:
        raise SystemExit(f"No rows parsed from: {et_path}")

    # Normalize keys
    et["Officer Id"] = et.get("Officer Id", "").astype(str).str.strip()
    et["Officer Id"] = et["Officer Id"].str.replace(".0", "", regex=False).str.zfill(4)
    et["Case Type Code"] = et.get("Case Type Code", "").astype(str).str.strip().str.upper()

    am = pd.read_csv(am_path, dtype=str)
    am["PADDED_BADGE_NUMBER"] = am["PADDED_BADGE_NUMBER"].astype(str).str.strip()
    am["PADDED_BADGE_NUMBER"] = am["PADDED_BADGE_NUMBER"].str.replace(".0", "", regex=False).str.zfill(4)
    wg2 = am.get("WG2", "").astype(str).str.strip().str.upper()
    patrol_badges = set(am.loc[wg2 == "PATROL BUREAU", "PADDED_BADGE_NUMBER"])

    patrol = et[et["Officer Id"].isin(patrol_badges)].copy()
    counts = patrol["Case Type Code"].value_counts()

    m = int(counts.get("M", 0))
    p = int(counts.get("P", 0))

    print(f"ETicket file: {et_path}")
    print(f"Patrol-assigned tickets: {len(patrol)}")
    print(f"Moving (M): {m}")
    print(f"Parking (P): {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


