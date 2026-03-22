#!/usr/bin/env python3
"""
Compare Response Time ETL Results

Compares new ETL output with old backfill data for October 2025.
"""

import pandas as pd
from pathlib import Path
import glob

# Paths
OLD_FILE = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Backfill\2025_10\response_time\2025_10_Average Response Times  Values are in mmss.csv")
NEW_FILE = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Backfill\2025_10\response_time\2025_10_Average_Response_Times__Values_are_in_mmss.csv")
NEW_BACKFILL_DIR = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Backfill")

print("=" * 80)
print("RESPONSE TIME ETL COMPARISON")
print("=" * 80)

# Read old data (contains multiple months)
old_df = pd.read_csv(OLD_FILE)
print(f"\nOLD DATA (from {OLD_FILE.name}):")
print(f"Total records: {len(old_df)}")
print(f"Date range: {old_df['MM-YY'].min()} to {old_df['MM-YY'].max()}")
print("\nOld Data (selected months 12-24 through 10-25):")
old_filtered = old_df[old_df['MM-YY'].isin(['12-24', '01-25', '02-25', '03-25', '04-25', '05-25', '06-25', '07-25', '08-25', '09-25', '10-25'])]
print(old_filtered.to_string(index=False))

# Read new data (October 2025 only)
new_df = pd.read_csv(NEW_FILE)
print(f"\nNEW DATA (from {NEW_FILE.name}):")
print(f"Total records: {len(new_df)}")
print(f"Date range: {new_df['MM-YY'].min()} to {new_df['MM-YY'].max()}")
print("\nNew Data (October 2025):")
print(new_df.to_string(index=False))

# Compare October 2025 specifically
print("\n" + "=" * 80)
print("OCTOBER 2025 COMPARISON")
print("=" * 80)

old_oct = old_df[old_df['MM-YY'] == '10-25'].copy()
new_oct = new_df.copy()

# Merge for comparison
merged = old_oct.merge(new_oct, on=['Response Type', 'MM-YY'], how='outer', suffixes=('_old', '_new'), indicator=True)
merged = merged.sort_values('Response Type')

print("\nDetailed Comparison:")
print(merged.to_string(index=False))

# Convert times to minutes for comparison
def time_to_minutes(time_str):
    """Convert MM:SS format to minutes"""
    if pd.isna(time_str):
        return None
    parts = str(time_str).split(':')
    if len(parts) == 2:
        return int(parts[0]) + int(parts[1]) / 60.0
    return None

print("\n" + "=" * 80)
print("TIME DIFFERENCES (October 2025)")
print("=" * 80)

for response_type in ['Emergency', 'Routine', 'Urgent']:
    old_val = old_oct[old_oct['Response Type'] == response_type]['First Response_Time_MMSS'].values
    new_val = new_oct[new_oct['Response Type'] == response_type]['First Response_Time_MMSS'].values
    
    if len(old_val) > 0 and len(new_val) > 0:
        old_min = time_to_minutes(old_val[0])
        new_min = time_to_minutes(new_val[0])
        if old_min and new_min:
            diff = new_min - old_min
            diff_str = f"+{diff:.2f}" if diff >= 0 else f"{diff:.2f}"
            print(f"{response_type:10s}: Old={old_val[0]:6s} ({old_min:.2f} min) | New={new_val[0]:6s} ({new_min:.2f} min) | Diff={diff_str:>6s} min")

# Read all new monthly files for comparison
print("\n" + "=" * 80)
print("NEW ETL RESULTS (All Months)")
print("=" * 80)

new_files = sorted(NEW_BACKFILL_DIR.glob("**/*Average_Response_Times__Values_are_in_mmss.csv"))
all_new_data = []

for file in new_files:
    df = pd.read_csv(file)
    all_new_data.append(df)

if all_new_data:
    combined_new = pd.concat(all_new_data, ignore_index=True)
    combined_new = combined_new.sort_values(['MM-YY', 'Response Type'])
    
    # Filter to requested months
    months_of_interest = ['12-24', '01-25', '02-25', '03-25', '04-25', '05-25', '06-25', '07-25', '08-25', '09-25', '10-25']
    combined_filtered = combined_new[combined_new['MM-YY'].isin(months_of_interest)]
    
    print(f"\nTotal records in new ETL (months 12-24 through 10-25): {len(combined_filtered)}")
    print("\nNew ETL Results (12-24 through 10-25):")
    print(combined_filtered.to_string(index=False))

print("\n" + "=" * 80)
print("COMPARISON COMPLETE")
print("=" * 80)
