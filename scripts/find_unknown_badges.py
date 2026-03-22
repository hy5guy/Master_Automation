"""
Find UNKNOWN WG2 records in Summons data
Identifies badges that need to be added to Assignment Master
"""
import sys
from pathlib import Path

try:
    import pandas as pd
    
    # Load summons data
    file_path = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx")
    
    print(f"Reading: {file_path.name}")
    df = pd.read_excel(file_path, sheet_name="Summons_Data")
    
    # Filter to UNKNOWN WG2
    unknown = df[(df["WG2"].isna()) | (df["WG2"] == "") | (df["WG2"] == "UNKNOWN")].copy()
    
    print(f"\nTotal UNKNOWN records: {len(unknown)}")
    
    if len(unknown) > 0:
        # Group by badge and officer name
        summary = unknown.groupby(["PADDED_BADGE_NUMBER", "Officer First Name", "Officer Last Name"]).size().reset_index(name="Count")
        summary = summary.sort_values("Count", ascending=False)
        
        print("\nUNKNOWN Badges (need to add to Assignment Master):")
        print("=" * 80)
        for idx, row in summary.iterrows():
            badge = row["PADDED_BADGE_NUMBER"]
            first = row["Officer First Name"]
            last = row["Officer Last Name"]
            count = row["Count"]
            print(f"Badge: {badge:6} | {first:15} {last:20} | Count: {count:3}")
        
        # Export to CSV for easy reference
        output_file = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\data\traffic_peo_additions_2026_02_17.csv")
        summary.to_csv(output_file, index=False)
        print(f"\nExported to: {output_file}")
        
        # Show sample records
        print("\nSample UNKNOWN records:")
        print(unknown[["PADDED_BADGE_NUMBER", "Officer First Name", "Officer Last Name", "Issue Date", "TYPE"]].head(10))
        
    else:
        print("\nNo UNKNOWN records found!")
    
except ImportError:
    print("ERROR: pandas not installed")
    print("Run: python -m pip install --user pandas openpyxl")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
