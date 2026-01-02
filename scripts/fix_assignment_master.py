#!/usr/bin/env python3
"""
Fix Assignment_Master_V2.csv:
1. Ensure all PADDED_BADGE_NUMBER values are correctly padded to 4 digits
2. Add new entry for badge 1711 (PEO JOHN SQUILLACE)
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

ASSIGNMENT_CSV = Path(
    r"C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv"
)

# Backup the original file
backup_path = ASSIGNMENT_CSV.with_suffix('.csv.backup')
print(f"Creating backup: {backup_path}")
df = pd.read_csv(ASSIGNMENT_CSV, dtype=str)
df.to_csv(backup_path, index=False)

print(f"\nLoaded {len(df)} rows from Assignment_Master_V2.csv")

# Fix PADDED_BADGE_NUMBER column
print("\nFixing PADDED_BADGE_NUMBER column...")
fixed_count = 0
for idx, row in df.iterrows():
    badge = str(row.get("BADGE_NUMBER", "")).strip()
    padded = str(row.get("PADDED_BADGE_NUMBER", "")).strip()
    
    if badge and badge != "nan" and badge != "" and badge != "0000":
        # Remove .0 if present
        badge_clean = badge.replace(".0", "").replace(".", "")
        
        # Calculate expected padded value
        if badge_clean.isdigit():
            expected_padded = badge_clean.zfill(4)
            
            # Fix if not correct
            padded_clean = padded.replace(".0", "").replace(".", "")
            if padded_clean != expected_padded:
                df.at[idx, "PADDED_BADGE_NUMBER"] = expected_padded
                fixed_count += 1
                print(f"  Fixed: Badge {badge} -> PADDED_BADGE_NUMBER: {padded} -> {expected_padded}")

print(f"Fixed {fixed_count} PADDED_BADGE_NUMBER values")

# Check if badge 1711 already exists
existing_1711 = df[df["BADGE_NUMBER"] == "1711"]
if len(existing_1711) > 0:
    print(f"\nWARNING: Badge 1711 already exists in the file:")
    print(existing_1711[["FULL_NAME", "TITLE", "BADGE_NUMBER", "PADDED_BADGE_NUMBER", "TEAM", "WG2"]].to_string())
    response = input("\nDo you want to replace it? (y/N): ")
    if response.lower() != 'y':
        print("Skipping badge 1711 entry.")
    else:
        # Remove existing entry
        df = df[df["BADGE_NUMBER"] != "1711"]
        print("Removed existing badge 1711 entry.")
else:
    print("\nBadge 1711 not found. Adding new entry...")

# Find the highest REF_NUMBER to assign next
max_ref = df["REF_NUMBER"].astype(str).str.replace(".0", "").replace(".", "")
max_ref = max_ref[max_ref.str.isdigit()]
next_ref = int(max_ref.max()) + 1 if len(max_ref) > 0 else 164

# Find a similar PEO entry to copy structure from
peo_example = df[df["TITLE"] == "PEO"].iloc[0] if len(df[df["TITLE"] == "PEO"]) > 0 else None

# Create new row for badge 1711
new_row = {
    "REF_NUMBER": str(next_ref),
    "FULL_NAME": "PEO JOHN SQUILLACE",
    "TITLE": "PEO",
    "FIRST_NAME": "JOHN",
    "LAST_NAME": "SQUILLACE",
    "BADGE_NUMBER": "1711",
    "PADDED_BADGE_NUMBER": "1711",
    "TEAM": "TRAFFIC",
    "WG1": "OPERATIONS DIVISION",
    "WG2": "TRAFFIC BUREAU",
    "WG3": "PEO",
    "WG4": "",
    "WG5": "",
    "POSS_CONTRACT_TYPE": "PARKING ENFORCEMENT OFF",
    "Last Name": "SQUILLACE",
    "First Name": "JOHN",
    "Current Badge": "1711",
    "Current Display Format": "PEO JOHN SQUILLACE",
    "Proposed Standardized Name": "J. SQUILLACE",
    "Proposed 4-Digit Format": "J. SQUILLACE #1711",
    "Conflict Resolution": "NO",
    "Special Notes": "",
}

# Fill in remaining columns from example or with empty values
if peo_example is not None:
    for col in df.columns:
        if col not in new_row:
            new_row[col] = peo_example.get(col, "")

# Add empty values for any remaining columns
for col in df.columns:
    if col not in new_row:
        new_row[col] = ""

# Create DataFrame from new row and append
new_df = pd.DataFrame([new_row])
df = pd.concat([df, new_df], ignore_index=True)

print(f"\nAdded new entry for badge 1711:")
print(f"  REF_NUMBER: {next_ref}")
print(f"  FULL_NAME: PEO JOHN SQUILLACE")
print(f"  BADGE_NUMBER: 1711")
print(f"  PADDED_BADGE_NUMBER: 1711")
print(f"  TEAM: TRAFFIC")
print(f"  WG2: TRAFFIC BUREAU")

# Save the updated file
print(f"\nSaving updated file to: {ASSIGNMENT_CSV}")
df.to_csv(ASSIGNMENT_CSV, index=False)

print("\nDone!")
print(f"Backup saved to: {backup_path}")
