#!/usr/bin/env python3
"""Verify the Assignment_Master_V2.csv fix."""

import pandas as pd
from pathlib import Path

ASSIGNMENT_CSV = Path(
    r"C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv"
)

df = pd.read_csv(ASSIGNMENT_CSV, dtype=str)

# Check badge 1711
badge_1711 = df[df["BADGE_NUMBER"] == "1711"]
if len(badge_1711) > 0:
    print("Badge 1711 entry found:")
    row = badge_1711.iloc[0]
    print(f"  REF_NUMBER: {row['REF_NUMBER']}")
    print(f"  FULL_NAME: {row['FULL_NAME']}")
    print(f"  TITLE: {row['TITLE']}")
    print(f"  BADGE_NUMBER: {row['BADGE_NUMBER']}")
    print(f"  PADDED_BADGE_NUMBER: {row['PADDED_BADGE_NUMBER']}")
    print(f"  TEAM: {row['TEAM']}")
    print(f"  WG1: {row['WG1']}")
    print(f"  WG2: {row['WG2']}")
    print(f"  WG3: {row['WG3']}")
    print(f"  POSS_CONTRACT_TYPE: {row['POSS_CONTRACT_TYPE']}")
    print(f"  Current Display Format: {row['Current Display Format']}")
    print(f"  Proposed Standardized Name: {row['Proposed Standardized Name']}")
    print(f"  Proposed 4-Digit Format: {row['Proposed 4-Digit Format']}")
    print(f"  Conflict Resolution: {row['Conflict Resolution']}")
else:
    print("ERROR: Badge 1711 not found!")

# Check PADDED_BADGE_NUMBER format
print("\nChecking PADDED_BADGE_NUMBER format...")
issues = []
for idx, row in df.iterrows():
    badge = str(row.get("BADGE_NUMBER", "")).strip()
    padded = str(row.get("PADDED_BADGE_NUMBER", "")).strip()
    
    if badge and badge != "nan" and badge != "" and badge != "0000":
        badge_clean = badge.replace(".0", "").replace(".", "")
        if badge_clean.isdigit():
            expected = badge_clean.zfill(4)
            padded_clean = padded.replace(".0", "").replace(".", "")
            if padded_clean != expected:
                issues.append({
                    "BADGE_NUMBER": badge,
                    "PADDED_BADGE_NUMBER": padded,
                    "Expected": expected
                })

if issues:
    print(f"Found {len(issues)} entries with incorrect padding:")
    for issue in issues[:10]:
        print(f"  Badge {issue['BADGE_NUMBER']}: {issue['PADDED_BADGE_NUMBER']} -> should be {issue['Expected']}")
else:
    print("All PADDED_BADGE_NUMBER values are correctly formatted!")
