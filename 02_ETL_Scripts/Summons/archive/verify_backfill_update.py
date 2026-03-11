"""Verify backfill update and ETL results"""
import pandas as pd
from pathlib import Path

print("=" * 70)
print("VERIFYING BACKFILL UPDATE AND ETL RESULTS")
print("=" * 70)

# Check backfill file
backfill_file = Path(r"C:\Dev\PowerBI_Date\Backfill\2025_09\summons\Hackensack Police Department - Summons Dashboard.csv")
df_backfill = pd.read_csv(backfill_file, encoding='utf-8')
march_backfill = df_backfill[df_backfill['Month_Year'] == '03-25']

print(f"\nBackfill file - 03-25 rows:")
if len(march_backfill) > 0:
    print(march_backfill.to_string(index=False))
    print(f"\n✅ 03-25 data found in backfill file")
    print(f"   M: {march_backfill[march_backfill['TYPE']=='M']['Count of TICKET_NUMBER'].values[0]}")
    print(f"   P: {march_backfill[march_backfill['TYPE']=='P']['Count of TICKET_NUMBER'].values[0]}")
else:
    print("❌ 03-25 data NOT found in backfill file")

# Check ETL output
excel_file = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx")
df_excel = pd.read_excel(excel_file, sheet_name='Summons_Data')
march_excel = df_excel[df_excel['Month_Year'] == '03-25']

print(f"\n" + "=" * 70)
print("ETL OUTPUT - 03-25 DATA")
print("=" * 70)

if len(march_excel) > 0:
    march_m = march_excel[march_excel['TYPE'] == 'M']['TICKET_COUNT'].sum()
    march_p = march_excel[march_excel['TYPE'] == 'P']['TICKET_COUNT'].sum()
    
    print(f"\n✅ 03-25 data found in ETL output")
    print(f"   Moving (M): {march_m:,}")
    print(f"   Parking (P): {march_p:,}")
    print(f"   Rows: {len(march_excel)}")
    
    # Check if it matches expected values
    if march_m == 454 and march_p == 3097:
        print(f"\n✅ Counts match expected values (M=454, P=3097)")
    else:
        print(f"\n⚠️  Counts differ from expected:")
        print(f"   Expected: M=454, P=3097")
        print(f"   Actual: M={march_m}, P={march_p}")
else:
    print("\n❌ 03-25 data NOT found in ETL output")

# Check all months in output
print(f"\n" + "=" * 70)
print("ALL MONTHS IN ETL OUTPUT")
print("=" * 70)
all_months = sorted(df_excel['Month_Year'].unique())
print(f"\nMonths present: {', '.join(all_months)}")

if '03-25' in all_months:
    print(f"\n✅ 03-25 is now included in the output!")
else:
    print(f"\n❌ 03-25 is still missing from the output")
