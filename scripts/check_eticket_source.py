"""
Check January 2026 E-ticket export and compare with staging
"""
import pandas as pd
from pathlib import Path

eticket_path = Path(r"C:\Users\RobertCarucci\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\2026\month\2026_01_eticket_export.csv")
staging_path = Path(r"C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx")

print("=" * 100)
print("E-TICKET SOURCE FILE CHECK")
print("=" * 100)

# Read E-ticket
print(f"\nReading: {eticket_path}")
eticket = pd.read_csv(eticket_path, sep=';', on_bad_lines='skip', engine='python')
print(f"Total records in E-ticket: {len(eticket)}")
print(f"Columns: {list(eticket.columns)[:10]}...")

# Check Case Type Code distribution
if 'Case Type Code' in eticket.columns:
    print(f"\nCase Type Code distribution:")
    print(eticket['Case Type Code'].value_counts())

# Check for statute column
if 'Statute' in eticket.columns:
    title39 = eticket[eticket['Statute'].astype(str).str.startswith('39:', na=False)]
    print(f"\nTitle 39 violations in E-ticket: {len(title39)}")

# Read staging file
print(f"\n" + "=" * 100)
print("STAGING FILE CHECK")
print("=" * 100)
staging = pd.read_excel(staging_path, sheet_name="Summons_Data")
jan_staging = staging[staging['YearMonthKey'] == 202601]

print(f"\nTotal records in staging (Jan 2026): {len(jan_staging)}")
print(f"Moving (M): {(jan_staging['TYPE'] == 'M').sum()}")
print(f"Parking (P): {(jan_staging['TYPE'] == 'P').sum()}")

print(f"\n" + "=" * 100)
print("COMPARISON:")
print("=" * 100)
print(f"E-ticket records:     {len(eticket)}")
print(f"Staging records:      {len(jan_staging)}")
print(f"Missing:              {len(eticket) - len(jan_staging)}")

print(f"\n" + "=" * 100)
print("ACTION: Need to re-run classification script with fresh E-ticket data")
print("=" * 100)
