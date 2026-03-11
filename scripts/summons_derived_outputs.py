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

try:
    from path_config import get_onedrive_root, get_powerbi_paths
except ImportError:
    def get_onedrive_root() -> Path:
        import os
        base = os.environ.get("ONEDRIVE_BASE") or os.environ.get("ONEDRIVE_HACKENSACK")
        return Path(base) if base else Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack")

    def get_powerbi_paths() -> tuple[Path, Path]:
        import json, os
        config_path = Path(__file__).resolve().parent.parent / "config" / "scripts.json"
        try:
            with open(config_path, encoding="utf-8") as f:
                data = json.load(f)
            drop = Path(data["settings"]["powerbi_drop_path"])
            return drop, drop.parent / "Backfill"
        except Exception:
            root = get_onedrive_root()
            return root / "PowerBI_Date" / "_DropExports", root / "PowerBI_Date" / "Backfill"


def _find_file(candidates: list[Path]) -> Path | None:
    """Return first existing path from candidates."""
    for p in candidates:
        if p.exists():
            return p
    return None


def main() -> int:
    """Main execution function"""
    print("[INFO] Starting Summons Derived Outputs generation (SIMPLIFIED)...")
    
    root = get_onedrive_root()
    output_dir, backfill_root = get_powerbi_paths()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Candidate paths for 2026_01 exports (prefer Compstat, fallback to Backfill)
    compstat = root / "Shared Folder" / "Compstat" / "Monthly Reports" / "2026" / "01_january"
    compstat_archive = compstat / "archive"
    backfill = backfill_root / "2026_01" / "summons"
    
    try:
        # FILE 1: backfill_summons_summary.csv - Use Power BI export directly
        dept_candidates = [
            compstat / "Department-Wide Summons  Moving and Parking.csv",
            compstat_archive / "Department-Wide Summons  Moving and Parking.csv",
            backfill / "2026_01_Department-Wide Summons  Moving and Parking.csv",
        ]
        dept_file = _find_file(dept_candidates)
        if dept_file:
            backfill_df = pd.read_csv(dept_file)
            out_backfill = output_dir / "backfill_summons_summary.csv"
            backfill_df.to_csv(out_backfill, index=False)
            print(f"[OK] Written: {out_backfill.name} ({len(backfill_df)} rows) from {dept_file.name}")
            jan26_data = backfill_df[backfill_df['Month_Year'] == '01-26'] if 'Month_Year' in backfill_df.columns else []
            if len(jan26_data) > 0 and 'TYPE' in backfill_df.columns and 'Sum of TICKET_COUNT' in backfill_df.columns:
                print(f"[INFO] January 2026 data confirmed:")
                for _, row in jan26_data.iterrows():
                    print(f"  {row['TYPE']}: {row['Sum of TICKET_COUNT']} tickets")
        else:
            print(f"[ERROR] Department-Wide file not found. Checked: Compstat/01_january, archive, Backfill/2026_01/summons")
            return 1
        
        # FILE 2: wg2_movers_parkers_nov2025.csv
        wg2_candidates = [
            compstat / "Summons  Moving & Parking  All Bureaus.csv",
            compstat_archive / "Summons  Moving & Parking  All Bureaus.csv",
            backfill / "2026_01_Summons  Moving & Parking  All Bureaus.csv",
        ]
        wg2_file = _find_file(wg2_candidates)
        if wg2_file:
            wg2_df = pd.read_csv(wg2_file)
            out_wg2 = output_dir / "wg2_movers_parkers_nov2025.csv"
            wg2_df.to_csv(out_wg2, index=False)
            print(f"[OK] Written: {out_wg2.name} ({len(wg2_df)} rows) from {wg2_file.name}")
            if 'M' in wg2_df.columns and 'P' in wg2_df.columns:
                print(f"[INFO] WG2 totals - Moving: {wg2_df['M'].sum()}, Parking: {wg2_df['P'].sum()}")
        else:
            print(f"[ERROR] WG2 file not found. Checked: Compstat, archive, Backfill/2026_01/summons")
            return 1
        
        # FILE 3: top5_moving_1125.csv
        top5m_candidates = [
            compstat / "Top 5 Moving Violations - Department Wide.csv",
            compstat_archive / "Top 5 Moving Violations - Department Wide.csv",
            backfill / "2026_01_Top 5 Moving Violations - Department Wide.csv",
        ]
        top5m_file = _find_file(top5m_candidates)
        if top5m_file:
            top5m_df = pd.read_csv(top5m_file)
            out_top_m = output_dir / "top5_moving_1125.csv"
            top5m_df.to_csv(out_top_m, index=False)
            print(f"[OK] Written: {out_top_m.name} ({len(top5m_df)} rows) from {top5m_file.name}")
            if len(top5m_df) > 0 and 'Officer' in top5m_df.columns:
                top_officer = top5m_df.iloc[0]
                col = 'Summons Count' if 'Summons Count' in top5m_df.columns else top5m_df.columns[1]
                print(f"[INFO] Top moving officer: {top_officer['Officer']} ({top_officer[col]} summons)")
        else:
            print(f"[ERROR] Top 5 Moving file not found. Checked: Compstat, archive, Backfill/2026_01/summons")
            return 1
        
        # FILE 4: top5_parking_1125.csv
        top5p_candidates = [
            compstat / "Top 5 Parking Violations - Department Wide.csv",
            compstat_archive / "Top 5 Parking Violations - Department Wide.csv",
            backfill / "2026_01_Top 5 Parking Violations - Department Wide.csv",
        ]
        top5p_file = _find_file(top5p_candidates)
        if top5p_file:
            top5p_df = pd.read_csv(top5p_file)
            out_top_p = output_dir / "top5_parking_1125.csv"
            top5p_df.to_csv(out_top_p, index=False)
            print(f"[OK] Written: {out_top_p.name} ({len(top5p_df)} rows) from {top5p_file.name}")
            if len(top5p_df) > 0 and 'Officer' in top5p_df.columns:
                top_officer = top5p_df.iloc[0]
                col_name = top5p_df.columns[1] if len(top5p_df.columns) > 1 else top5p_df.columns[0]
                print(f"[INFO] Top parking officer: {top_officer['Officer']} ({top_officer[col_name]} summons)")
        else:
            print(f"[ERROR] Top 5 Parking file not found. Checked: Compstat, archive, Backfill/2026_01/summons")
            return 1
        
        print("\n[SUCCESS] All 4 Summons derived CSVs written to PowerBI_Date\\_DropExports:")
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