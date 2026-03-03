"""Verify ETL output"""
import pandas as pd
from pathlib import Path

print("=" * 70)
print("VERIFICATION RESULTS")
print("=" * 70)

# Read Excel output
excel_file = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx")
df_excel = pd.read_excel(excel_file, sheet_name='Summons_Data')
dec25 = df_excel[df_excel['Month_Year'] == '12-25'].copy()

dec25_m = dec25[dec25['TYPE'] == 'M']['TICKET_COUNT'].sum()
dec25_p = dec25[dec25['TYPE'] == 'P']['TICKET_COUNT'].sum()
dec25_c = dec25[dec25['TYPE'] == 'C']['TICKET_COUNT'].sum() if 'C' in dec25['TYPE'].values else 0

print(f"\nExcel Output (12-25):")
print(f"  Moving (M): {dec25_m:,}")
print(f"  Parking (P): {dec25_p:,}")
print(f"  Special (C): {dec25_c:,}")
print(f"  Total: {dec25_m + dec25_p + dec25_c:,}")

# Read raw export
raw_file = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\2025\raw\month\2025_12_eticket_export.csv")
with open(raw_file, 'r', encoding='utf-8') as f:
    first_line = f.readline()
    delimiter = ";" if first_line.count(";") > first_line.count(",") else ","
df_raw = pd.read_csv(raw_file, sep=delimiter, encoding='utf-8', low_memory=False, dtype=str)

raw_counts = df_raw['Case Type Code'].value_counts()
raw_m = int(raw_counts.get('M', 0))
raw_p = int(raw_counts.get('P', 0))
raw_c = int(raw_counts.get('C', 0))

print(f"\nRaw Export (all records):")
print(f"  Moving (M): {raw_m:,}")
print(f"  Parking (P): {raw_p:,}")
print(f"  Special (C): {raw_c:,}")
print(f"  Total: {raw_m + raw_p + raw_c:,}")

print(f"\n" + "=" * 70)
print("COMPARISON")
print("=" * 70)

m_diff = dec25_m - raw_m
p_diff = dec25_p - raw_p
total_diff = (dec25_m + dec25_p + dec25_c) - (raw_m + raw_p + raw_c)

print(f"\nDifference (Excel - Raw):")
print(f"  Moving (M): {m_diff:+,} ({'+' if m_diff >= 0 else ''}{m_diff})")
print(f"  Parking (P): {p_diff:+,} ({'+' if p_diff >= 0 else ''}{p_diff})")
print(f"  Total: {total_diff:+,} ({'+' if total_diff >= 0 else ''}{total_diff} records filtered by date)")

print(f"\nNote: Excel output filters records by Issue Date (December 2025 only)")
print(f"Raw export includes all records regardless of Issue Date")

# Check if dates explain the difference
if 'Issue Date' in df_raw.columns:
    print(f"\nChecking date distribution in raw export...")
    df_raw['Issue Date'] = pd.to_datetime(df_raw['Issue Date'], errors='coerce')
    dec_only = df_raw[(df_raw['Issue Date'].dt.year == 2025) & (df_raw['Issue Date'].dt.month == 12)]
    if len(dec_only) > 0:
        dec_counts = dec_only['Case Type Code'].value_counts()
        dec_m = int(dec_counts.get('M', 0))
        dec_p = int(dec_counts.get('P', 0))
        print(f"\nRaw export - December 2025 only:")
        print(f"  Moving (M): {dec_m:,}")
        print(f"  Parking (P): {dec_p:,}")
        print(f"  Total records: {len(dec_only):,}")
        
        print(f"\nComparison (Excel vs Raw Dec 2025):")
        print(f"  Moving (M): Excel={dec25_m}, Raw Dec={dec_m}, Match={dec25_m == dec_m}")
        print(f"  Parking (P): Excel={dec25_p}, Raw Dec={dec_p}, Match={dec25_p == dec_p}")
