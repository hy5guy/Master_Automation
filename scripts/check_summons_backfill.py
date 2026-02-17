#!/usr/bin/env python3
"""Check if summons backfill folder and files exist and whether the merge would find gap-month data."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from path_config import get_onedrive_root
except ImportError:
    get_onedrive_root = lambda: Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack")

SUMMONS_GAP_MONTHS = ("03-25", "07-25", "10-25", "11-25")
DEFAULT_LABEL = "2025_12"

def main():
    root = get_onedrive_root() / "PowerBI_Date" / "Backfill"
    summons_dir = root / DEFAULT_LABEL / "summons"
    print("Backfill root:", root)
    print("Summons dir:  ", summons_dir)
    print("Exists:      ", summons_dir.exists())
    if not summons_dir.exists():
        print("\nBackfill summons folder not found. Create:")
        print("  ", summons_dir)
        return 1
    all_files = list(summons_dir.glob("*.csv"))
    print("CSV files:    ", len(all_files))
    # Prefer department_wide_summons (has all months as rows)
    consolidated = [f for f in all_files if "department_wide_summons" in f.name.lower()]
    if not consolidated:
        consolidated = [f for f in all_files if "department_wide" in f.name.lower()
                       or ("Department-Wide" in f.name and ("Summons" in f.name or "Moving" in f.name))]
    if not consolidated:
        print("\nNo consolidated 'department wide' CSV found. Merge will add 0 backfill rows.")
        return 0
    print("Using:        ", consolidated[0].name)
    import pandas as pd
    RENAME = {"PeriodLabel": "Month_Year", "Sum of Value": "TICKET_COUNT", "Sum of TICKET_COUNT": "TICKET_COUNT",
              "Time Category": "TYPE", "Type": "TYPE", "Moving/Parking": "TYPE"}
    bf = pd.read_csv(consolidated[0], low_memory=False).rename(columns=RENAME)
    if "Month_Year" not in bf.columns and "PeriodLabel" in bf.columns:
        bf["Month_Year"] = bf["PeriodLabel"]
    if "Month_Year" not in bf.columns:
        print("  (no Month_Year/PeriodLabel column)")
        return 0
    gap = bf[bf["Month_Year"].astype(str).str.strip().isin(SUMMONS_GAP_MONTHS)]
    print("Gap-month rows (03-25, 07-25, 10-25, 11-25):", len(gap))
    if not gap.empty:
        print(gap[["Month_Year", "TYPE", "TICKET_COUNT"]].to_string(index=False))
    print("\nBackfill is present; ETL merge will add", len(gap), "rows when you run run_summons_etl.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())
