"""Verify ETL output matches raw export counts"""
import pandas as pd
from pathlib import Path

print("=" * 70)
print("VERIFYING ETL OUTPUT")
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
    
    print(f"\n12-25 TYPE counts (summing TICKET_COUNT):")
    print(f"  Moving (M): {dec25_m:,}")
    print(f"  Parking (P): {dec25_p:,}")
    print(f"  Special (C): {dec25_c:,}")
    print(f"  Total: {dec25_m + dec25_p + dec25_c:,}")
    
    # Check ETL_VERSION
    print(f"\n12-25 ETL_VERSION breakdown:")
    print(dec25['ETL_VERSION'].value_counts())

# Read raw export for comparison
raw_file = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\2025\raw\month\2025_12_eticket_export.csv")
with open(raw_file, 'r', encoding='utf-8') as f:
    first_line = f.readline()
    delimiter = ";" if first_line.count(";") > first_line.count(",") else ","

df_raw = pd.read_csv(raw_file, sep=delimiter, encoding='utf-8', low_memory=False, dtype=str)

print(f"\n" + "=" * 70)
print("RAW EXPORT COMPARISON")
print("=" * 70)

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
    print(f"\n" + "=" * 70)
    print("VERIFICATION RESULTS")
    print("=" * 70)
    
    m_match = dec25_m == raw_m if len(dec25) > 0 else False
    p_match = dec25_p == raw_p if len(dec25) > 0 else False
    
    print(f"\nMoving (M):")
    print(f"  Raw Export:  {raw_m:,}")
    print(f"  Excel Output: {dec25_m:,}")
    print(f"  Match: {'✅ YES' if m_match else '❌ NO (difference: ' + str(dec25_m - raw_m) + ')'}")
    
    print(f"\nParking (P):")
    print(f"  Raw Export:  {raw_p:,}")
    print(f"  Excel Output: {dec25_p:,}")
    print(f"  Match: {'✅ YES' if p_match else '❌ NO (difference: ' + str(dec25_p - raw_p) + ')'}")
    
    if m_match and p_match:
        print(f"\n🎉 SUCCESS! ETL output matches raw export counts exactly!")
    else:
        print(f"\n⚠️  WARNING: Counts do not match - investigate further")
