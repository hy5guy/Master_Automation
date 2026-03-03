#!/usr/bin/env python3
"""
Diagnose Summons Top-5 exports vs Dept-wide totals.

Reads the ETL staging workbook and computes:
- Dept-wide totals by TYPE for the latest Month_Year
- Top 10 officers by TYPE (moving M, parking P, non-parking != P)

Uses Sum(TICKET_COUNT) so it works for both detail and aggregate rows.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", required=True, help="Path to summons_powerbi_latest.xlsx")
    ap.add_argument("--month", default=None, help="Month_Year label (MM-YY). If omitted, uses max YearMonthKey.")
    args = ap.parse_args()

    xlsx = Path(args.xlsx)
    df = pd.read_excel(xlsx, sheet_name="Summons_Data")

    # Normalize
    df["YearMonthKey"] = pd.to_numeric(df.get("YearMonthKey"), errors="coerce")
    df["Month_Year"] = df.get("Month_Year", "").astype(str).str.strip()
    df["TYPE"] = df.get("TYPE", "").astype(str).str.strip().str.upper()
    df["TICKET_COUNT"] = pd.to_numeric(df.get("TICKET_COUNT"), errors="coerce").fillna(0).astype(int)
    df["OFFICER_DISPLAY_NAME"] = df.get("OFFICER_DISPLAY_NAME", "").astype(str).str.strip()
    df["OFFICER_NAME_RAW"] = df.get("OFFICER_NAME_RAW", "").astype(str).str.strip()

    # Pick month
    if args.month:
        month = args.month
        cur = df[df["Month_Year"] == month].copy()
    else:
        ymk = int(df["YearMonthKey"].dropna().max())
        cur = df[df["YearMonthKey"] == ymk].copy()
        month = cur["Month_Year"].iloc[0] if not cur.empty else "?"

    if cur.empty:
        raise SystemExit("No rows found for selected month.")

    print(f"Workbook: {xlsx}")
    print(f"Month: {month}")
    print(f"Rows: {len(cur):,}  Tickets(sum): {int(cur['TICKET_COUNT'].sum()):,}")

    dept = cur.groupby("TYPE")["TICKET_COUNT"].sum().sort_values(ascending=False)
    print("\n=== Dept-wide totals by TYPE (Sum TICKET_COUNT) ===")
    print(dept.to_string())

    # Officer effective
    cur["Officer_Effective"] = cur["OFFICER_DISPLAY_NAME"]
    mask_blank = (cur["Officer_Effective"] == "") | (cur["Officer_Effective"].str.lower() == "nan")
    cur.loc[mask_blank, "Officer_Effective"] = cur.loc[mask_blank, "OFFICER_NAME_RAW"]

    def top_n(filter_expr, label: str, n: int = 10) -> None:
        sub = cur.loc[filter_expr].copy()
        grp = (
            sub.groupby("Officer_Effective", as_index=False)["TICKET_COUNT"].sum()
            .sort_values("TICKET_COUNT", ascending=False)
            .head(n)
        )
        print(f"\n=== Top {n} Officers: {label} (Sum TICKET_COUNT) ===")
        print(grp.to_string(index=False))

    top_n(cur["TYPE"] == "M", "Moving (TYPE=M)")
    top_n(cur["TYPE"] == "P", "Parking (TYPE=P)")
    top_n(cur["TYPE"] != "P", "Non-Parking (TYPE!=P)")

    # Also show rowcount-based top5 (to catch RowCount vs Sum(TICKET_COUNT) issues)
    def top_n_rowcount(filter_expr, label: str, n: int = 10) -> None:
        sub = cur.loc[filter_expr].copy()
        grp = (
            sub.groupby("Officer_Effective", as_index=False)
            .size()
            .rename(columns={"size": "RowCount"})
            .sort_values("RowCount", ascending=False)
            .head(n)
        )
        print(f"\n=== Top {n} Officers: {label} (RowCount) ===")
        print(grp.to_string(index=False))

    top_n_rowcount(cur["TYPE"] == "M", "Moving (TYPE=M)")
    top_n_rowcount(cur["TYPE"] != "P", "Non-Parking (TYPE!=P)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


