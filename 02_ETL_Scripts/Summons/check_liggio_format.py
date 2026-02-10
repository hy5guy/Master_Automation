#!/usr/bin/env python3
"""Check LIGGIO formatting"""

import pandas as pd

df = pd.read_excel(
    r"C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx",
    sheet_name="Summons_Data"
)

liggio = df[
    (df['Month_Year'] == '12-25') & 
    (df['ETL_VERSION'] == 'ETICKET_CURRENT') &
    (df['PADDED_BADGE_NUMBER'].astype(str).str.contains('388', na=False))
]

print("LIGGIO records:")
print(liggio[['OFFICER_DISPLAY_NAME', 'OFFICER_NAME_RAW', 'PADDED_BADGE_NUMBER', 'TYPE', 'TICKET_COUNT']].to_string())

# Check top 5 parking
dec25_p = df[
    (df['Month_Year'] == '12-25') & 
    (df['ETL_VERSION'] == 'ETICKET_CURRENT') & 
    (df['TYPE'] == 'P')
]

print("\n\nTop 5 Parking Officers:")
top = dec25_p.groupby(['OFFICER_DISPLAY_NAME', 'PADDED_BADGE_NUMBER', 'WG2', 'WG3'])['TICKET_COUNT'].sum().sort_values(ascending=False).head(5)
for i, (name, badge, wg2, wg3, count) in enumerate(zip(
    top.index.get_level_values(0), 
    top.index.get_level_values(1), 
    top.index.get_level_values(2), 
    top.index.get_level_values(3),
    top.values
), 1):
    print(f"{i}. {name} | Badge: {badge} | {wg2} | {wg3} | Count: {count}")
