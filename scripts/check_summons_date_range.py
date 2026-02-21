import pandas as pd
import os

staging_file = r'C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx'

print(f'File exists: {os.path.exists(staging_file)}')
print(f'File size: {os.path.getsize(staging_file):,} bytes')
print(f'Last modified: {pd.Timestamp.fromtimestamp(os.path.getmtime(staging_file))}')
print()

df = pd.read_excel(staging_file, sheet_name='Summons_Data')

print(f'Total records in file: {len(df)}')
print(f'Date range: {df["ISSUE_DATE"].min()} to {df["ISSUE_DATE"].max()}')
print()

print('Records by YearMonthKey:')
print(df['YearMonthKey'].value_counts().sort_index())
print()

print('Check if backfill data exists:')
print(f'IS_AGGREGATE=True: {len(df[df["IS_AGGREGATE"] == True])}')
print(f'IS_AGGREGATE=False: {len(df[df["IS_AGGREGATE"] == False])}')
print()

print('ETL_VERSION breakdown:')
print(df['ETL_VERSION'].value_counts())
