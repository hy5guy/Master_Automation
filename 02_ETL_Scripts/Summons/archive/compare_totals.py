#!/usr/bin/env python3
"""Compare totals between 13-month visual and All Bureaus visual"""

import pandas as pd

# Load the ETL output
df = pd.read_excel(
    r"C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx",
    sheet_name="Summons_Data"
)

# December 2025 e-ticket data (what 13-month visual uses)
dec25_all = df[(df['Month_Year'] == '12-25') & (df['ETL_VERSION'] == 'ETICKET_CURRENT')]

print("=" * 80)
print("DECEMBER 2025 DATA ANALYSIS")
print("=" * 80)
print(f"\nTotal records: {len(dec25_all):,}")

# Total TYPE breakdown (what 13-month visual shows)
print("\n" + "-" * 80)
print("TOTAL TYPE BREAKDOWN (13-month visual totals):")
print("-" * 80)
type_totals = dec25_all.groupby('TYPE')['TICKET_COUNT'].sum()
print(f"M (Moving): {type_totals.get('M', 0)}")
print(f"P (Parking): {type_totals.get('P', 0)}")
print(f"Total: {type_totals.get('M', 0) + type_totals.get('P', 0)}")

# WG2 breakdown (what All Bureaus visual shows)
print("\n" + "-" * 80)
print("WG2 BREAKDOWN (All Bureaus visual - excluding UNKNOWN):")
print("-" * 80)
dec25_with_wg2 = dec25_all[
    (dec25_all['WG2'].notna()) & 
    (dec25_all['WG2'] != '') & 
    (dec25_all['WG2'] != 'UNKNOWN')
]

wg2_breakdown = dec25_with_wg2.groupby(['WG2', 'TYPE'])['TICKET_COUNT'].sum().unstack(fill_value=0)
print("\nBy Bureau:")
print(wg2_breakdown[['M', 'P']].sort_index())

all_bureaus_m = wg2_breakdown['M'].sum() if 'M' in wg2_breakdown.columns else 0
all_bureaus_p = wg2_breakdown['P'].sum() if 'P' in wg2_breakdown.columns else 0
print(f"\nAll Bureaus Total - M: {all_bureaus_m}, P: {all_bureaus_p}")

# UNKNOWN records
print("\n" + "-" * 80)
print("UNKNOWN RECORDS (excluded from All Bureaus visual):")
print("-" * 80)
unknown_records = dec25_all[
    (dec25_all['WG2'].isna()) | 
    (dec25_all['WG2'] == '') | 
    (dec25_all['WG2'] == 'UNKNOWN')
]
print(f"Count: {len(unknown_records)}")
if len(unknown_records) > 0:
    unknown_totals = unknown_records.groupby('TYPE')['TICKET_COUNT'].sum()
    print(f"M: {unknown_totals.get('M', 0)}")
    print(f"P: {unknown_totals.get('P', 0)}")

# Compare
print("\n" + "=" * 80)
print("COMPARISON:")
print("=" * 80)
print(f"13-month visual (includes UNKNOWN):")
print(f"  M: {type_totals.get('M', 0)}, P: {type_totals.get('P', 0)}")
print(f"\nAll Bureaus visual (excludes UNKNOWN):")
print(f"  M: {all_bureaus_m}, P: {all_bureaus_p}")
print(f"\nDifference:")
print(f"  M: {type_totals.get('M', 0) - all_bureaus_m}")
print(f"  P: {type_totals.get('P', 0) - all_bureaus_p}")
