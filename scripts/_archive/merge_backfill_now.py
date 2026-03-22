"""
Merge Department-Wide backfill data with current staging file
Creates complete 13-month dataset
"""
import pandas as pd
from pathlib import Path
from datetime import datetime

# Paths
staging_path = Path(r"C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx")
backfill_path = Path(r"C:\Users\RobertCarucci\OneDrive - City of Hackensack\Master_Automation\data\backfill\2026_12_compair\2026_02_13_Department-Wide_Summons_CORRECTED.csv")

print("=" * 100)
print("MERGING DEPARTMENT-WIDE BACKFILL INTO STAGING FILE")
print("=" * 100)

# Load staging file (current January detail records)
print(f"\n1. Loading staging file: {staging_path.name}")
df_staging = pd.read_excel(staging_path, sheet_name="Summons_Data")
print(f"   Records: {len(df_staging)}")
print(f"   Date range: {df_staging['YearMonthKey'].min()} to {df_staging['YearMonthKey'].max()}")

# Load backfill (historical summary records)
print(f"\n2. Loading backfill file: {backfill_path.name}")
df_backfill = pd.read_csv(backfill_path)
print(f"   Records: {len(df_backfill)}")
print(f"   Columns: {list(df_backfill.columns)}")
print(f"\nBackfill data:")
print(df_backfill)

# Convert backfill to match staging schema
print(f"\n3. Converting backfill to staging schema...")

# Create matching rows for backfill
backfill_rows = []
for idx, row in df_backfill.iterrows():
    month_year = row['Month_Year']
    summons_type = row['TYPE']
    count = int(row['Sum of TICKET_COUNT'])
    
    # Parse Month_Year (MM-YY format)
    month, year = month_year.split('-')
    month = int(month)
    year = 2000 + int(year)  # Convert 25 to 2025, 26 to 2026
    year_month_key = year * 100 + month
    
    # Skip January 2026 (already have detail records)
    if year_month_key == 202601:
        print(f"   Skipping 01-26 (already in staging)")
        continue
    
    # Create summary row
    backfill_row = {
        'TICKET_NUMBER': f'SUMMARY_{month_year}_{summons_type}',
        'TYPE': summons_type,
        'Month_Year': month_year,
        'Year': year,
        'Month': month,
        'YearMonthKey': year_month_key,
        'TICKET_COUNT': count,
        'IS_AGGREGATE': True,
        'ETL_VERSION': 'HISTORICAL_SUMMARY',
        'PROCESSING_TIMESTAMP': datetime.now(),
        'SOURCE_FILE': 'BACKFILL_2026_02_13',
        'WG2': 'DEPARTMENT_WIDE_SUMMARY',
        'TEAM': 'ALL',
        'ASSIGNMENT_FOUND': False,
        'DATA_QUALITY_SCORE': 0,
        'COST_AMOUNT': 0,
        'MISC_AMOUNT': 0,
        'PADDED_BADGE_NUMBER': '9999',
        'OFFICER_DISPLAY_NAME': 'DEPARTMENT SUMMARY',
        'OFFICER_NAME_RAW': 'DEPARTMENT SUMMARY',
        'VIOLATION_NUMBER': '',
        'VIOLATION_DESCRIPTION': f'{summons_type} - Department Total',
        'VIOLATION_TYPE': 'Moving' if summons_type == 'M' else 'Parking',
        'STATUS': 'SUMMARY',
        'LOCATION': '',
        'TOTAL_PAID_AMOUNT': '',
        'WG1': '',
        'WG3': '',
        'WG4': '',
        'POSS_CONTRACT_TYPE': '',
        'TITLE': '',
        'RANK': '',
        'FULL_NAME': 'DEPARTMENT SUMMARY'
    }
    
    backfill_rows.append(backfill_row)

df_backfill_normalized = pd.DataFrame(backfill_rows)
print(f"   Created {len(df_backfill_normalized)} backfill rows (skipped 01-26)")

# Merge
print(f"\n4. Merging datasets...")
df_combined = pd.concat([df_staging, df_backfill_normalized], ignore_index=True)
print(f"   Combined records: {len(df_combined)}")
print(f"   Date range: {df_combined['YearMonthKey'].min()} to {df_combined['YearMonthKey'].max()}")

# Verify month coverage
print(f"\n5. Month coverage:")
months = df_combined.groupby(['YearMonthKey', 'Month_Year']).size().reset_index(name='Count')
months = months.sort_values('YearMonthKey')
for idx, row in months.iterrows():
    key = row['YearMonthKey']
    month = row['Month_Year']
    count = row['Count']
    is_aggregate = df_combined[(df_combined['YearMonthKey'] == key) & (df_combined['IS_AGGREGATE'] == True)].shape[0]
    is_detail = df_combined[(df_combined['YearMonthKey'] == key) & (df_combined['IS_AGGREGATE'] == False)].shape[0]
    print(f"   {month} ({key}): {count:4} records (Detail: {is_detail:4}, Summary: {is_aggregate:2})")

# Create backup
backup = staging_path.parent / f"{staging_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
print(f"\n6. Creating backup: {backup.name}")
import shutil
shutil.copy2(staging_path, backup)

# Save
print(f"\n7. Saving merged file: {staging_path.name}")
df_combined.to_excel(staging_path, sheet_name="Summons_Data", index=False)

print("\n" + "=" * 100)
print("COMPLETE!")
print("=" * 100)
print(f"Total records: {len(df_combined)}")
print(f"January 2026 detail: {len(df_staging)}")
print(f"Historical summary: {len(df_backfill_normalized)}")
print(f"Month coverage: {months['YearMonthKey'].nunique()} months")
print("\nNow refresh Power BI to see 13-month data!")
