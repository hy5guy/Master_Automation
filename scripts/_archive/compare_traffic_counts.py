"""
Compare Traffic Bureau summons counts - Visual Export vs Staging File
"""
import pandas as pd
from pathlib import Path

print("=" * 100)
print("TRAFFIC BUREAU SUMMONS COMPARISON - January 2026")
print("=" * 100)

# Load summons staging file
staging_path = Path(r"C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx")
df = pd.read_excel(staging_path, sheet_name="Summons_Data")

print(f"\nTotal records in staging: {len(df)}")

# Filter to January 2026
jan_2026 = df[df['YearMonthKey'] == 202601]
print(f"January 2026 records: {len(jan_2026)}")

# Traffic Bureau only
traffic = jan_2026[jan_2026['WG2'] == 'TRAFFIC BUREAU']
print(f"\nTRAFFIC BUREAU January 2026:")
print(f"  Total: {len(traffic)}")
print(f"  Moving (M): {(traffic['TYPE'] == 'M').sum()}")
print(f"  Parking (P): {(traffic['TYPE'] == 'P').sum()}")

# All January data by bureau
print(f"\nALL BUREAUS January 2026:")
for bureau in ['TRAFFIC BUREAU', 'PATROL DIVISION', 'OFFICE OF SPECIAL OPERATIONS', 'HOUSING', 'DETECTIVE BUREAU', 'UNKNOWN']:
    bureau_data = jan_2026[jan_2026['WG2'] == bureau]
    if len(bureau_data) > 0:
        m_count = (bureau_data['TYPE'] == 'M').sum()
        p_count = (bureau_data['TYPE'] == 'P').sum()
        print(f"  {bureau:35} M={m_count:4} P={p_count:4} Total={len(bureau_data):4}")

# Visual Export says (from Traffic Bureau.csv):
print(f"\n" + "=" * 100)
print("VISUAL EXPORT (Traffic Bureau.csv):")
print("=" * 100)
print(f"  Moving Summons (01-26): 191")
print(f"  Parking Summons (01-26): 3,061")

print(f"\n" + "=" * 100)
print("DISCREPANCY ANALYSIS:")
print("=" * 100)
print(f"  Missing Moving: {191 - (traffic['TYPE'] == 'M').sum()}")
print(f"  Missing Parking: {3061 - (traffic['TYPE'] == 'P').sum()}")

# Check if there are records with null WG2
null_wg2 = jan_2026[jan_2026['WG2'].isna() | (jan_2026['WG2'] == '') | (jan_2026['WG2'] == 'UNKNOWN')]
print(f"\n  Records with UNKNOWN/NULL WG2: {len(null_wg2)}")
if len(null_wg2) > 0:
    print(f"    Moving: {(null_wg2['TYPE'] == 'M').sum()}")
    print(f"    Parking: {(null_wg2['TYPE'] == 'P').sum()}")

# Check PEO badges (2000-2099)
peo_badges = jan_2026[jan_2026['PADDED_BADGE_NUMBER'].astype(str).str.match(r'^20[0-9]{2}$', na=False)]
print(f"\n  PEO badges (2000-2099): {len(peo_badges)}")
if len(peo_badges) > 0:
    print(f"    Moving: {(peo_badges['TYPE'] == 'M').sum()}")
    print(f"    Parking: {(peo_badges['TYPE'] == 'P').sum()}")
    print(f"    WG2 distribution:")
    print(peo_badges['WG2'].value_counts())

print("\n" + "=" * 100)
