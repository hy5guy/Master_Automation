#!/usr/bin/env python3
"""
Diagnose Summons 'blank Bureau' rows for the Moving/Parking by Bureau visual.

Reads the staging workbook and summarizes records where WG2 (bureau) is blank.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", required=True, help="Path to summons_powerbi_latest.xlsx")
    ap.add_argument("--month", default="11-25", help="Month_Year label to inspect (MM-YY)")
    args = ap.parse_args()

    xlsx = Path(args.xlsx)
    df = pd.read_excel(xlsx, sheet_name="Summons_Data")

    needed = ["WG2", "TYPE", "TICKET_COUNT", "Month_Year", "PADDED_BADGE_NUMBER", "OFFICER_DISPLAY_NAME"]
    missing_cols = [c for c in needed if c not in df.columns]
    if missing_cols:
        raise SystemExit(f"Missing columns in workbook: {missing_cols}")

    df["WG2"] = df["WG2"].astype(str).str.strip()
    df["TYPE"] = df["TYPE"].astype(str).str.strip()
    df["Month_Year"] = df["Month_Year"].astype(str).str.strip()
    df["PADDED_BADGE_NUMBER"] = df["PADDED_BADGE_NUMBER"].astype(str).str.strip()
    df["OFFICER_DISPLAY_NAME"] = df["OFFICER_DISPLAY_NAME"].astype(str).str.strip()
    df["TICKET_COUNT"] = pd.to_numeric(df["TICKET_COUNT"], errors="coerce").fillna(0).astype(int)

    cur = df[df["Month_Year"] == args.month].copy()
    blank = cur[cur["WG2"].isin(["", "nan", "None"])].copy()

    print(f"Workbook: {xlsx}")
    print(f"Month: {args.month}")
    print(f"Rows (month): {len(cur):,}   Tickets (month): {int(cur['TICKET_COUNT'].sum()):,}")
    print(f"Rows (blank WG2): {len(blank):,}   Tickets (blank WG2): {int(blank['TICKET_COUNT'].sum()):,}")

    if blank.empty:
        return 0

    print("\nTYPE breakdown (blank WG2):")
    print(blank.groupby("TYPE")["TICKET_COUNT"].sum().sort_values(ascending=False).to_string())

    print("\nBadges contributing (blank WG2) [top 15]:")
    print(blank["PADDED_BADGE_NUMBER"].value_counts().head(15).to_string())

    print("\nSample rows (blank WG2) [up to 25]:")
    cols = ["PADDED_BADGE_NUMBER", "OFFICER_DISPLAY_NAME", "TYPE", "TICKET_COUNT", "Month_Year", "WG2"]
    print(blank[cols].head(25).to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


