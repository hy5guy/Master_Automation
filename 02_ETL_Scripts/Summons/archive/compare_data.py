"""Compare Excel output with raw export and visual export"""
import pandas as pd
from pathlib import Path

print("=" * 70)
print("COMPARING DATA SOURCES")
print("=" * 70)

# Read Excel output
excel_file = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx")
df_excel = pd.read_excel(excel_file, sheet_name='Summons_Data')

print(f"\nExcel output total rows: {len(df_excel):,}")

# Check 12-25 data
dec25 = df_excel[df_excel['Month_Year'] == '12-25'].copy()
print(f"\n12-25 rows in Excel: {len(dec25):,}")

if len(dec25) > 0:
    dec25_m = dec25[dec25['TYPE'] == 'M']['TICKET_COUNT'].sum()
    dec25_p = dec25[dec25['TYPE'] == 'P']['TICKET_COUNT'].sum()
    dec25_c = dec25[dec25['TYPE'] == 'C']['TICKET_COUNT'].sum() if 'C' in dec25['TYPE'].values else 0
    
    print(f"  12-25 Moving (M): {dec25_m:,}")
    print(f"  12-25 Parking (P): {dec25_p:,}")
    print(f"  12-25 Special (C): {dec25_c:,}")
    print(f"  12-25 Total: {dec25_m + dec25_p + dec25_c:,}")
    
    # Check ETL_VERSION breakdown
    print(f"\n  12-25 ETL_VERSION breakdown:")
    print(dec25['ETL_VERSION'].value_counts())
    print(f"\n  12-25 IS_AGGREGATE breakdown:")
    print(dec25['IS_AGGREGATE'].value_counts())

# Check 12-24 data
dec24 = df_excel[df_excel['Month_Year'] == '12-24'].copy()
print(f"\n12-24 rows in Excel: {len(dec24):,}")

if len(dec24) > 0:
    dec24_m = dec24[dec24['TYPE'] == 'M']['TICKET_COUNT'].sum()
    dec24_p = dec24[dec24['TYPE'] == 'P']['TICKET_COUNT'].sum()
    
    print(f"  12-24 Moving (M): {dec24_m:,}")
    print(f"  12-24 Parking (P): {dec24_p:,}")
    print(f"  12-24 Total: {dec24_m + dec24_p:,}")
    
    # Check ETL_VERSION breakdown
    print(f"\n  12-24 ETL_VERSION breakdown:")
    print(dec24['ETL_VERSION'].value_counts())
    print(f"\n  12-24 IS_AGGREGATE breakdown:")
    print(dec24['IS_AGGREGATE'].value_counts())

# Read raw export
raw_file = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\2025\raw\month\2025_12_eticket_export.csv")
with open(raw_file, 'r', encoding='utf-8') as f:
    first_line = f.readline()
    delimiter = ";" if first_line.count(";") > first_line.count(",") else ","

df_raw = pd.read_csv(raw_file, sep=delimiter, encoding='utf-8', low_memory=False, dtype=str)
print(f"\nRaw export total rows: {len(df_raw):,}")

if 'Case Type Code' in df_raw.columns:
    raw_counts = df_raw['Case Type Code'].value_counts()
    raw_m = int(raw_counts.get('M', 0))
    raw_p = int(raw_counts.get('P', 0))
    raw_c = int(raw_counts.get('C', 0))
    
    print(f"\nRaw export counts (Case Type Code):")
    print(f"  Moving (M): {raw_m:,}")
    print(f"  Parking (P): {raw_p:,}")
    print(f"  Special (C): {raw_c:,}")
    print(f"  Total: {raw_m + raw_p + raw_c:,}")

# Compare
print("\n" + "=" * 70)
print("COMPARISON:")
print("=" * 70)

if len(dec25) > 0 and 'Case Type Code' in df_raw.columns:
    print(f"\n12-25 Comparison:")
    print(f"  Raw Export:      M={raw_m:,}, P={raw_p:,}, Total={raw_m + raw_p + raw_c:,}")
    print(f"  Excel Output:    M={dec25_m:,}, P={dec25_p:,}, Total={dec25_m + dec25_p + dec25_c:,}")
    print(f"  Visual Export:   M=526, P=2,835, Total=3,361")
    
    print(f"\n  Differences (Excel vs Raw):")
    print(f"    M: {dec25_m - raw_m:+,} ({'+' if dec25_m > raw_m else ''}{dec25_m - raw_m})")
    print(f"    P: {dec25_p - raw_p:+,} ({'+' if dec25_p > raw_p else ''}{dec25_p - raw_p})")
    
    print(f"\n  Differences (Visual vs Raw):")
    print(f"    M: {526 - raw_m:+,} ({'+' if 526 > raw_m else ''}{526 - raw_m})")
    print(f"    P: {2835 - raw_p:+,} ({'+' if 2835 > raw_p else ''}{2835 - raw_p})")

print("\n" + "=" * 70)
print("12-24 STATUS:")
print("=" * 70)
print(f"12-24 data in Excel: {'YES' if len(dec24) > 0 else 'NO'}")
print(f"12-24 data in Visual Export: YES (M=452, P=1,778)")
if len(dec24) > 0:
    print(f"\n12-24 in Excel matches Visual Export:")
    print(f"  M: Excel={dec24_m:,}, Visual=452, Match={dec24_m == 452}")
    print(f"  P: Excel={dec24_p:,}, Visual=1,778, Match={dec24_p == 1778}")
