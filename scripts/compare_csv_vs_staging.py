"""
Compare raw CSV vs staging Excel to find missing records
"""
import pandas as pd

print("="*80)
print("RAW CSV vs STAGING FILE COMPARISON")
print("="*80)

# Try to load raw CSV with error handling
csv_path = r'C:\Users\RobertCarucci\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\2026\month\2026_01_eticket_export.csv'

try:
    # Try semicolon delimiter with error handling
    print("\nAttempting to load CSV with semicolon delimiter...")
    df_csv = pd.read_csv(csv_path, sep=';', on_bad_lines='skip', low_memory=False)
    print(f"[OK] CSV loaded: {len(df_csv)} records")
    
    print("\nColumn names (first 10):")
    for i, col in enumerate(df_csv.columns[:10], 1):
        print(f"  {i}. {col}")
    
    # Check for Case Type Code
    if 'Case Type Code' in df_csv.columns:
        print("\nCase Type Code distribution:")
        print(df_csv['Case Type Code'].value_counts())
    else:
        print("\nWARNING: 'Case Type Code' column not found!")
        print("Available columns containing 'Type':", [c for c in df_csv.columns if 'Type' in c or 'type' in c])
    
except Exception as e:
    print(f"[ERROR] Error loading CSV: {e}")
    df_csv = None

# Load staging file
staging_file = r'C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx'

print(f"\nLoading staging file...")
df_staging = pd.read_excel(staging_file, sheet_name='Summons_Data')
jan26 = df_staging[df_staging['YearMonthKey'] == 202601]

print(f"[OK] Staging file loaded")
print(f"  January 2026: {len(jan26)} records")
print(f"  Moving: {len(jan26[jan26['TYPE'] == 'M'])}")
print(f"  Parking: {len(jan26[jan26['TYPE'] == 'P'])}")

if df_csv is not None:
    print(f"\n" + "="*80)
    print(f"RECORD COUNT COMPARISON")
    print(f"="*80)
    print(f"Raw CSV:       {len(df_csv):,} records")
    print(f"Staging File:  {len(jan26):,} records")
    print(f"Missing:       {len(df_csv) - len(jan26):,} records ({((len(df_csv) - len(jan26)) / len(df_csv) * 100):.1f}%)")
