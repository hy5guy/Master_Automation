"""
Show expected January 2026 values for All Bureaus visual
"""
import pandas as pd
from pathlib import Path

staging_path = Path(r"C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx")
df = pd.read_excel(staging_path, sheet_name="Summons_Data")

# Filter to January 2026
jan_2026 = df[df['YearMonthKey'] == 202601].copy()

# Consolidate Housing and OSO with Patrol
jan_2026['WG2_CONSOLIDATED'] = jan_2026['WG2'].replace({
    'HOUSING': 'PATROL DIVISION',
    'OFFICE OF SPECIAL OPERATIONS': 'PATROL DIVISION'
})

# Filter out UNKNOWN and Fire Dept
jan_2026_clean = jan_2026[~jan_2026['WG2_CONSOLIDATED'].isin(['UNKNOWN'])]

# Group by consolidated bureau and type
summary = jan_2026_clean.groupby(['WG2_CONSOLIDATED', 'TYPE']).size().unstack(fill_value=0)

print("=" * 80)
print("ALL BUREAUS - JANUARY 2026 (Expected Values)")
print("=" * 80)
print("\nBureau                           M      P    Total")
print("-" * 80)

for bureau in summary.index:
    m = summary.loc[bureau, 'M'] if 'M' in summary.columns else 0
    p = summary.loc[bureau, 'P'] if 'P' in summary.columns else 0
    total = m + p
    print(f"{bureau:30} {m:4}  {p:4}   {total:4}")

print("-" * 80)
print(f"{'TOTAL':30} {summary['M'].sum():4}  {summary['P'].sum():4}   {summary.sum().sum():4}")

print("\n" + "=" * 80)
print("COMPARISON WITH TRAFFIC BUREAU VISUAL EXPORT:")
print("=" * 80)
print(f"Visual Export Moving:  191")
print(f"Data file Moving:      {summary.loc['TRAFFIC BUREAU', 'M']}")
print(f"Difference:            {191 - int(summary.loc['TRAFFIC BUREAU', 'M'])}")
print()
print(f"Visual Export Parking: 3,061")
print(f"Data file Parking:     {summary.loc['TRAFFIC BUREAU', 'P']}")
print(f"Difference:            {3061 - int(summary.loc['TRAFFIC BUREAU', 'P'])}")

print("\n" + "=" * 80)
print("NOTE: Visual Export is HIGHER - this suggests some summons in the")
print("visual export are NOT in the staging file (missing backfill data?)")
print("=" * 80)
