"""Debug script to inspect Pay Type values in December 2025 overtime file."""

import pandas as pd

# Load overtime file
ot_file = r"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Overtime\export\month\2025\2025_12_otactivity.xlsx"
df = pd.read_excel(ot_file, engine='openpyxl')

print("=" * 80)
print("DECEMBER 2025 OVERTIME FILE INSPECTION")
print("=" * 80)
print(f"\nTotal rows: {len(df)}")
print(f"\nColumns: {list(df.columns)}")

# Show first few rows
print("\n" + "=" * 80)
print("FIRST 10 ROWS:")
print("=" * 80)
print(df.head(10))

# Check Pay Type column
if 'Pay Type' in df.columns:
    print("\n" + "=" * 80)
    print("PAY TYPE VALUE COUNTS:")
    print("=" * 80)
    print(df['Pay Type'].value_counts())

    print("\n" + "=" * 80)
    print("UNIQUE PAY TYPES (sample):")
    print("=" * 80)
    for pt in df['Pay Type'].unique()[:20]:
        print(f"  '{pt}'")

    # Check for keywords
    print("\n" + "=" * 80)
    print("KEYWORD CHECKS:")
    print("=" * 80)
    pt_lower = df['Pay Type'].astype(str).str.lower()
    print(f"  Contains 'comp': {pt_lower.str.contains('comp').sum()}")
    print(f"  Contains 'overtime': {pt_lower.str.contains('overtime').sum()}")
    print(f"  Contains 'o.t.': {pt_lower.str.contains('o.t.').sum()}")
    print(f"  Contains 'cash': {pt_lower.str.contains('cash').sum()}")
    print(f"  Contains '1.5': {pt_lower.str.contains('1.5').sum()}")
    print(f"  Contains '2.0': {pt_lower.str.contains('2.0').sum()}")

# Check Status column
if 'Status' in df.columns:
    print("\n" + "=" * 80)
    print("STATUS VALUE COUNTS:")
    print("=" * 80)
    print(df['Status'].value_counts())

# Check Date range
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    print("\n" + "=" * 80)
    print("DATE RANGE:")
    print("=" * 80)
    print(f"  Min: {df['Date'].min()}")
    print(f"  Max: {df['Date'].max()}")
    print(f"  December 2025 rows: {((df['Date'].dt.year == 2025) & (df['Date'].dt.month == 12)).sum()}")
