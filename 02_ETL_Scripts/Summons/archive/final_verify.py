"""Final verification of 03-25 data"""
import pandas as pd
from pathlib import Path

print("=" * 70)
print("FINAL VERIFICATION - 03-25 DATA")
print("=" * 70)

# Check ETL output
excel_file = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx")
df_excel = pd.read_excel(excel_file, sheet_name='Summons_Data')
march_excel = df_excel[df_excel['Month_Year'] == '03-25']

if len(march_excel) > 0:
    march_m = march_excel[march_excel['TYPE'] == 'M']['TICKET_COUNT'].sum()
    march_p = march_excel[march_excel['TYPE'] == 'P']['TICKET_COUNT'].sum()
    
    print(f"\nSUCCESS: 03-25 data found in ETL output")
    print(f"  Moving (M): {march_m:,}")
    print(f"  Parking (P): {march_p:,}")
    print(f"  Expected: M=454, P=3097")
    print(f"  Match: M={'YES' if march_m == 454 else 'NO'}, P={'YES' if march_p == 3097 else 'NO'}")
    
    # Check ETL_VERSION
    print(f"\n  ETL_VERSION: {march_excel['ETL_VERSION'].unique()[0]}")
    print(f"  IS_AGGREGATE: {march_excel['IS_AGGREGATE'].unique()[0]}")
else:
    print("\nERROR: 03-25 data NOT found in ETL output")

# List all months
print(f"\n" + "=" * 70)
print("ALL MONTHS IN OUTPUT")
print("=" * 70)
all_months = sorted(df_excel['Month_Year'].unique())
print(f"\nMonths: {', '.join(all_months)}")

if '03-25' in all_months:
    print(f"\nSUCCESS: 03-25 is now included!")
else:
    print(f"\nERROR: 03-25 is still missing")

print(f"\nTotal records: {len(df_excel):,}")
