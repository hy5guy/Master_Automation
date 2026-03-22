#!/usr/bin/env python3
# 2026-02-21-00-38-51 (EST)
# Project Name: Hackensack PD | Data Ops & ETL Remediation
# File Name: scripts/summons_derived_outputs_simple.py
# Author: R. A. Carucci
# Purpose: Generate Summons derived outputs from Power BI exports with dynamic month handling, IS_AGGREGATE, and TICKET_COUNT normalization.

import argparse
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from path_config import get_onedrive_root

import pandas as pd

MONTH_NAMES = {
    1: "january", 2: "february", 3: "march", 4: "april",
    5: "may", 6: "june", 7: "july", 8: "august",
    9: "september", 10: "october", 11: "november", 12: "december",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Summons Derived Outputs for Power BI")
    parser.add_argument("--report-month", required=True, help="Report month in YYYY-MM format")
    args = parser.parse_args()

    year, month = (int(x) for x in args.report_month.split("-"))
    yyyy_mm = f"{year}_{month:02d}"

    root = get_onedrive_root()
    output_dir = root / "PowerBI_Data" / "_DropExports"
    export_path = root / "Shared Folder" / "Compstat" / "Monthly Reports" / str(year) / f"{month:02d}_{MONTH_NAMES[month]}"

    print(f"[INFO] Starting Summons Derived Outputs generation (SIMPLIFIED)...")
    print(f"[INFO] Report month: {args.report_month}  |  Export path: {export_path}")

    written = []
    skipped = []

    try:
        dept_file = export_path / "Department-Wide Summons  Moving and Parking.csv"
        if not dept_file.exists():
            print(f"[ERROR] Department-Wide file not found: {dept_file}")
            return 1

        backfill_df = pd.read_csv(dept_file)
        if "Sum of TICKET_COUNT" in backfill_df.columns:
            backfill_df.rename(columns={"Sum of TICKET_COUNT": "TICKET_COUNT"}, inplace=True)
        backfill_df["IS_AGGREGATE"] = True
        out_backfill = output_dir / "backfill_summons_summary.csv"
        backfill_df.to_csv(out_backfill, index=False)
        print(f"[OK] Written: {out_backfill.name} ({len(backfill_df)} rows)")
        written.append(out_backfill.name)

        mm_yy = f"{month:02d}-{year % 100:02d}"
        month_data = backfill_df[backfill_df.get("Month_Year", pd.Series(dtype=str)) == mm_yy]
        if len(month_data) > 0:
            ticket_col = "TICKET_COUNT" if "TICKET_COUNT" in month_data.columns else None
            print(f"[INFO] {args.report_month} data confirmed:")
            for _, row in month_data.iterrows():
                if ticket_col:
                    print(f"  {row['TYPE']}: {row[ticket_col]} tickets")

        wg2_file = export_path / "Summons  Moving & Parking  All Bureaus.csv"
        if wg2_file.exists():
            wg2_df = pd.read_csv(wg2_file)
            out_wg2 = output_dir / f"wg2_movers_parkers_{yyyy_mm}.csv"
            wg2_df.to_csv(out_wg2, index=False)
            print(f"[OK] Written: {out_wg2.name} ({len(wg2_df)} rows)")
            total_m = wg2_df["M"].sum()
            total_p = wg2_df["P"].sum()
            print(f"[INFO] WG2 totals - Moving: {total_m}, Parking: {total_p}")
            written.append(out_wg2.name)
        else:
            print(f"[WARN] WG2 file not found (skipping): {wg2_file}")
            skipped.append("wg2_movers_parkers")

        top5m_file = export_path / "Top 5 Moving Violations - Department Wide.csv"
        if top5m_file.exists():
            top5m_df = pd.read_csv(top5m_file)
            out_top_m = output_dir / f"top5_moving_{yyyy_mm}.csv"
            top5m_df.to_csv(out_top_m, index=False)
            print(f"[OK] Written: {out_top_m.name} ({len(top5m_df)} rows)")
            written.append(out_top_m.name)
        else:
            print(f"[WARN] Top 5 Moving file not found (skipping): {top5m_file}")
            skipped.append("top5_moving")

        top5p_file = export_path / "Top 5 Parking Violations - Department Wide.csv"
        if top5p_file.exists():
            top5p_df = pd.read_csv(top5p_file)
            out_top_p = output_dir / f"top5_parking_{yyyy_mm}.csv"
            top5p_df.to_csv(out_top_p, index=False)
            print(f"[OK] Written: {out_top_p.name} ({len(top5p_df)} rows)")
            written.append(out_top_p.name)
        else:
            print(f"[WARN] Top 5 Parking file not found (skipping): {top5p_file}")
            skipped.append("top5_parking")

        print(f"\n[SUCCESS] Summons derived outputs complete:")
        for name in written:
            print(f"  + {name}")
        for name in skipped:
            print(f"  - {name} (skipped)")
        print(f"[INFO] Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return 0

    except Exception as e:
        print(f"[ERROR] Failed to generate outputs: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
