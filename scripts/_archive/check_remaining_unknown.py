"""
Check remaining UNKNOWN records after WG2 update
"""
import pandas as pd
from pathlib import Path

file_path = Path(r"C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx")

print(f"Reading: {file_path.name}")
df = pd.read_excel(file_path, sheet_name="Summons_Data")

# Filter to UNKNOWN WG2
unknown = df[df["WG2"] == "UNKNOWN"].copy()

print(f"\nTotal UNKNOWN records: {len(unknown)}")

if len(unknown) > 0:
    print("\nRemaining UNKNOWN records:")
    print("=" * 100)
    
    # Show each record with details
    for idx, row in unknown.iterrows():
        badge = row.get("PADDED_BADGE_NUMBER", "N/A")
        first = row.get("Officer First Name", "N/A")
        last = row.get("Officer Last Name", "N/A")
        issue_date = row.get("Issue Date", "N/A")
        vtype = row.get("TYPE", "N/A")
        violation = row.get("VIOLATION_DESCRIPTION", "N/A")[:50]
        
        print(f"Badge: {badge:6} | {first:15} {last:20} | Date: {issue_date} | Type: {vtype} | {violation}")
    
    # Group summary
    print("\n" + "=" * 100)
    print("Summary by Badge:")
    summary = unknown.groupby(["PADDED_BADGE_NUMBER", "Officer First Name", "Officer Last Name"]).size().reset_index(name="Count")
    for idx, row in summary.iterrows():
        print(f"  Badge {row['PADDED_BADGE_NUMBER']}: {row['Officer First Name']} {row['Officer Last Name']} - {row['Count']} summons")

else:
    print("\nNo UNKNOWN records!")
