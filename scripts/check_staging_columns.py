"""
Check which columns exist in the summons_powerbi_latest.xlsx file
"""
import pandas as pd
from pathlib import Path

staging_path = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx")

print("Reading Excel file...")
df = pd.read_excel(staging_path, sheet_name="Summons_Data")

print(f"\nTotal columns: {len(df.columns)}")
print(f"Total rows: {len(df)}")

print(f"\n" + "=" * 100)
print("ALL COLUMNS IN FILE:")
print("=" * 100)

for i, col in enumerate(df.columns, 1):
    dtype = df[col].dtype
    nulls = df[col].isna().sum()
    print(f"{i:3}. {col:40} | Type: {str(dtype):15} | Nulls: {nulls}")

# Check for the columns expected by 13month_trend query
expected_cols = [
    'TICKET_NUMBER', 'TICKET_COUNT', 'IS_AGGREGATE', 'PADDED_BADGE_NUMBER',
    'OFFICER_DISPLAY_NAME', 'OFFICER_NAME_RAW', 'ISSUE_DATE', 
    'VIOLATION_NUMBER', 'VIOLATION_DESCRIPTION', 'VIOLATION_TYPE',
    'TYPE', 'STATUS', 'LOCATION', 'WARNING_FLAG', 'SOURCE_FILE',
    'ETL_VERSION', 'Year', 'Month', 'YearMonthKey', 'Month_Year',
    'TEAM', 'WG1', 'WG2', 'WG3', 'WG4', 'WG5',
    'POSS_CONTRACT_TYPE', 'ASSIGNMENT_FOUND', 'DATA_QUALITY_SCORE',
    'DATA_QUALITY_TIER', 'TOTAL_PAID_AMOUNT', 'FINE_AMOUNT',
    'COST_AMOUNT', 'MISC_AMOUNT', 'PROCESSING_TIMESTAMP'
]

print(f"\n" + "=" * 100)
print("MISSING COLUMNS (expected by 13month_trend query):")
print("=" * 100)

missing = []
for col in expected_cols:
    if col not in df.columns:
        missing.append(col)
        print(f"  - {col}")

if not missing:
    print("  None! All expected columns exist.")

print(f"\n" + "=" * 100)
print("EXTRA COLUMNS (not in 13month_trend query):")
print("=" * 100)

extra = []
for col in df.columns:
    if col not in expected_cols:
        extra.append(col)
        print(f"  + {col}")

print(f"\nMissing: {len(missing)}, Extra: {len(extra)}")
