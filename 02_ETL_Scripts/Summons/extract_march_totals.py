"""Extract March 2025 totals from e-ticket export for backfill update"""
import pandas as pd
from pathlib import Path

print("=" * 70)
print("EXTRACTING MARCH 2025 TOTALS FOR BACKFILL")
print("=" * 70)

# Read March 2025 e-ticket export
march_file = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\2025\raw\month\2025_03_eticket_export.csv")

if not march_file.exists():
    print(f"\nERROR: File not found: {march_file}")
    exit(1)

# Detect delimiter
with open(march_file, 'r', encoding='utf-8') as f:
    first_line = f.readline()
    delimiter = ";" if first_line.count(";") > first_line.count(",") else ","

print(f"\nDetected delimiter: '{delimiter}'")

# Load data
df = pd.read_csv(march_file, sep=delimiter, encoding='utf-8', low_memory=False, dtype=str)
print(f"\nTotal rows in export: {len(df):,}")

# Check Case Type Code column
if 'Case Type Code' not in df.columns:
    print("\nERROR: 'Case Type Code' column not found")
    print(f"Available columns: {list(df.columns)[:20]}")
    exit(1)

# Count by Case Type Code
counts = df['Case Type Code'].value_counts()
m_count = int(counts.get('M', 0))
p_count = int(counts.get('P', 0))
c_count = int(counts.get('C', 0))

print(f"\n" + "=" * 70)
print("MARCH 2025 TOTALS (Case Type Code)")
print("=" * 70)
print(f"\nMoving (M): {m_count:,}")
print(f"Parking (P): {p_count:,}")
print(f"Special (C): {c_count:,}")
print(f"Total: {m_count + p_count + c_count:,}")

# Format for backfill CSV (TYPE, Month_Year, Count of TICKET_NUMBER)
print(f"\n" + "=" * 70)
print("BACKFILL CSV FORMAT")
print("=" * 70)
print("\nAdd these rows to the backfill CSV:")
print(f"TYPE,Month_Year,Count of TICKET_NUMBER")
print(f"M,03-25,{m_count}")
print(f"P,03-25,{p_count}")

if c_count > 0:
    print(f"C,03-25,{c_count}")

# Check for Issue Date to verify all records are from March 2025
if 'Issue Date' in df.columns:
    print(f"\n" + "=" * 70)
    print("DATE VERIFICATION")
    print("=" * 70)
    df['Issue Date'] = pd.to_datetime(df['Issue Date'], errors='coerce')
    march_only = df[(df['Issue Date'].dt.year == 2025) & (df['Issue Date'].dt.month == 3)]
    print(f"\nRecords with March 2025 dates: {len(march_only):,}")
    
    if len(march_only) != len(df):
        other_dates = df[~((df['Issue Date'].dt.year == 2025) & (df['Issue Date'].dt.month == 3))]
        print(f"Records with other dates: {len(other_dates):,}")
        print("\nNote: Some records may have dates outside March 2025")

print(f"\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"\nFor backfill file, add:")
print(f"  M,03-25,{m_count}")
print(f"  P,03-25,{p_count}")
