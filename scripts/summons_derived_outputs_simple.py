#!/usr/bin/env python3
# Timestamp (EST): 2026-02-19-17-20-00
# Project Name: Hackensack PD | Data Ops & ETL Remediation
# File Name: scripts/summons_derived_outputs.py
# Author: R. A. Carucci
# Purpose: Simplified version using Power BI exports as authoritative source

"""
Summons Derived Outputs for Power BI - SIMPLIFIED VERSION

Since we have the authoritative Power BI exports with the correct January 2026 data,
this script uses those exports directly and supplements with SummonsMaster for historical data.
"""

from pathlib import Path
from datetime import datetime
import pandas as pd


def main() -> int:
    """Main execution function"""
    print("[INFO] Starting Summons Derived Outputs generation (SIMPLIFIED)...")
    
    output_dir = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\_DropExports")
    export_path = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Monthly Reports\2026\01_january")
    
    try:
        # FILE 1: backfill_summons_summary.csv - Use Power BI export directly
        dept_file = export_path / "Department-Wide Summons  Moving and Parking.csv"
        if dept_file.exists():
            backfill_df = pd.read_csv(dept_file)
            out_backfill = output_dir / "backfill_summons_summary.csv"
            backfill_df.to_csv(out_backfill, index=False)
            print(f"[OK] Written: {out_backfill.name} ({len(backfill_df)} rows)")
            
            # Show January 2026 data
            jan26_data = backfill_df[backfill_df['Month_Year'] == '01-26']
            if len(jan26_data) > 0:
                print(f"[INFO] January 2026 data confirmed:")
                for _, row in jan26_data.iterrows():
                    print(f"  {row['TYPE']}: {row['Sum of TICKET_COUNT']} tickets")
        else:
            print(f"[ERROR] Department-Wide file not found: {dept_file}")
            return 1
        
        # FILE 2: wg2_movers_parkers_nov2025.csv - Use Power BI export directly
        wg2_file = export_path / "Summons  Moving & Parking  All Bureaus.csv"
        if wg2_file.exists():
            wg2_df = pd.read_csv(wg2_file)
            out_wg2 = output_dir / "wg2_movers_parkers_nov2025.csv"
            wg2_df.to_csv(out_wg2, index=False)
            print(f"[OK] Written: {out_wg2.name} ({len(wg2_df)} rows)")
            
            # Show totals
            total_m = wg2_df['M'].sum()
            total_p = wg2_df['P'].sum()
            print(f"[INFO] WG2 totals - Moving: {total_m}, Parking: {total_p}")
        else:
            print(f"[ERROR] WG2 file not found: {wg2_file}")
            return 1
        
        # FILE 3: top5_moving_1125.csv - Use Power BI export directly
        top5m_file = export_path / "Top 5 Moving Violations - Department Wide.csv"
        if top5m_file.exists():
            top5m_df = pd.read_csv(top5m_file)
            out_top_m = output_dir / "top5_moving_1125.csv"
            top5m_df.to_csv(out_top_m, index=False)
            print(f"[OK] Written: {out_top_m.name} ({len(top5m_df)} rows)")
            
            # Show top officer
            if len(top5m_df) > 0:
                top_officer = top5m_df.iloc[0]
                print(f"[INFO] Top moving officer: {top_officer['Officer']} ({top_officer['Summons Count']} summons)")
        else:
            print(f"[ERROR] Top 5 Moving file not found: {top5m_file}")
            return 1
        
        # FILE 4: top5_parking_1125.csv - Use Power BI export directly
        top5p_file = export_path / "Top 5 Parking Violations - Department Wide.csv"
        if top5p_file.exists():
            top5p_df = pd.read_csv(top5p_file)
            out_top_p = output_dir / "top5_parking_1125.csv"
            top5p_df.to_csv(out_top_p, index=False)
            print(f"[OK] Written: {out_top_p.name} ({len(top5p_df)} rows)")
            
            # Show top officer
            if len(top5p_df) > 0:
                top_officer = top5p_df.iloc[0]
                col_name = top5p_df.columns[1]  # Handle the trailing space issue
                print(f"[INFO] Top parking officer: {top_officer['Officer']} ({top_officer[col_name]} summons)")
        else:
            print(f"[ERROR] Top 5 Parking file not found: {top5p_file}")
            return 1
        
        print("\n[SUCCESS] All 4 Summons derived CSVs written to _DropExports:")
        print(f"  - backfill_summons_summary.csv")
        print(f"  - wg2_movers_parkers_nov2025.csv")
        print(f"  - top5_moving_1125.csv")
        print(f"  - top5_parking_1125.csv")
        print(f"[INFO] Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Failed to generate outputs: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())