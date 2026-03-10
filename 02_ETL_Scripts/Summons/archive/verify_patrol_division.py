#!/usr/bin/env python3
"""Verify PATROL DIVISION appears in ETL output"""

import pandas as pd

df = pd.read_excel(
    r"C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx",
    sheet_name="Summons_Data"
)

dec25 = df[(df['Month_Year'] == '12-25') & (df['ETL_VERSION'] == 'ETICKET_CURRENT')]

print("WG2 values for December 2025:")
print(dec25['WG2'].value_counts().to_string())
print(f'\nTotal records: {len(dec25):,}')
print(f'\nPATROL DIVISION count: {(dec25["WG2"] == "PATROL DIVISION").sum()}')
print(f'PATROL BUREAU count: {(dec25["WG2"] == "PATROL BUREAU").sum()}')
