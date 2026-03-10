#!/usr/bin/env python3
"""Analyze officer name formatting in raw export and ETL output"""

import pandas as pd

# Load raw export
print("=" * 80)
print("RAW EXPORT DATA")
print("=" * 80)
raw_df = pd.read_csv(
    r"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\2025\raw\month\2025_12_eticket_export.csv",
    sep=';',
    encoding='utf-8',
    on_bad_lines='skip',
    nrows=100
)

print(f"\nColumns: {list(raw_df.columns)[:20]}")

# Check officer columns
if 'Officer Id' in raw_df.columns:
    print("\nOfficer Id samples:")
    print(raw_df['Officer Id'].head(10).to_string())
    
if 'Officer First Name' in raw_df.columns and 'Officer Last Name' in raw_df.columns:
    print("\nOfficer name samples:")
    print(raw_df[['Officer First Name', 'Officer Last Name', 'Officer Id']].head(10))

# Load ETL output
print("\n" + "=" * 80)
print("ETL OUTPUT DATA")
print("=" * 80)
etl_df = pd.read_excel(
    r"C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx",
    sheet_name="Summons_Data"
)

dec25_p = etl_df[
    (etl_df['Month_Year'] == '12-25') & 
    (etl_df['ETL_VERSION'] == 'ETICKET_CURRENT') & 
    (etl_df['TYPE'] == 'P')
]

print(f"\nDecember 2025 Parking records: {len(dec25_p):,}")

# Check officer display names
print("\nTop 10 Parking Officers:")
top_officers = dec25_p.groupby(['OFFICER_DISPLAY_NAME', 'PADDED_BADGE_NUMBER', 'WG2', 'WG3'])['TICKET_COUNT'].sum().sort_values(ascending=False).head(10)
print(top_officers.to_string())

# Check for LIGGIO specifically
print("\n" + "=" * 80)
print("LIGGIO RECORDS")
print("=" * 80)
liggio = dec25_p[dec25_p['OFFICER_DISPLAY_NAME'].str.contains('LIGGIO', case=False, na=False)]
if len(liggio) > 0:
    print(f"Found {len(liggio)} LIGGIO records")
    print(liggio[['OFFICER_DISPLAY_NAME', 'OFFICER_NAME_RAW', 'PADDED_BADGE_NUMBER', 'BADGE_NUMBER']].head() if 'BADGE_NUMBER' in liggio.columns else liggio[['OFFICER_DISPLAY_NAME', 'OFFICER_NAME_RAW', 'PADDED_BADGE_NUMBER']].head())
else:
    print("No LIGGIO records found")
    # Check badge 0388
    badge_388 = dec25_p[dec25_p['PADDED_BADGE_NUMBER'].astype(str).str.contains('388', na=False)]
    if len(badge_388) > 0:
        print(f"\nBadge 0388 records: {len(badge_388)}")
        print(badge_388[['OFFICER_DISPLAY_NAME', 'OFFICER_NAME_RAW', 'PADDED_BADGE_NUMBER']].head())
