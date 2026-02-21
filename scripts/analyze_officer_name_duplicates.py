"""
Analyze officer name duplication in Summons data
Shows which officers have multiple name formats that need fuzzy matching
"""
import pandas as pd
from collections import defaultdict

staging_file = r'C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx'

print("Loading staging file...")
df = pd.read_excel(staging_file, sheet_name='Summons_Data')

# Get January 2026 data
jan26 = df[df['YearMonthKey'] == 202601].copy()

print(f"\nJanuary 2026: {len(jan26)} total records")
print(f"Moving: {len(jan26[jan26['TYPE'] == 'M'])}")
print(f"Parking: {len(jan26[jan26['TYPE'] == 'P'])}")

# Check for potential duplicates by last name
print("\n" + "="*80)
print("ANALYZING POTENTIAL OFFICER NAME DUPLICATES")
print("="*80)

# Extract last name from OFFICER_DISPLAY_NAME
def extract_last_name(display_name):
    """Extract last name from display name"""
    if pd.isna(display_name):
        return None
    
    # Remove rank prefixes
    name = str(display_name)
    for prefix in ['PEO ', 'P.O. ', 'PO ', 'DET. ', 'SGT. ', 'S.CAPT ', 'CAPT. ', 'LT. ']:
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    
    # Get first word (last name)
    parts = name.split()
    return parts[-1] if parts else None

jan26['LastName'] = jan26['OFFICER_DISPLAY_NAME'].apply(extract_last_name)

# Find last names with multiple display names
last_name_groups = jan26.groupby('LastName')['OFFICER_DISPLAY_NAME'].unique()
duplicates = {ln: names for ln, names in last_name_groups.items() if len(names) > 1 and ln}

if duplicates:
    print(f"\nFound {len(duplicates)} last names with multiple display formats:")
    print()
    
    for last_name in sorted(duplicates.keys()):
        display_names = duplicates[last_name]
        counts_by_type = {}
        
        for display_name in display_names:
            officer_data = jan26[jan26['OFFICER_DISPLAY_NAME'] == display_name]
            moving = len(officer_data[officer_data['TYPE'] == 'M'])
            parking = len(officer_data[officer_data['TYPE'] == 'P'])
            counts_by_type[display_name] = {'M': moving, 'P': parking, 'Total': moving + parking}
        
        print(f"Last Name: {last_name}")
        for display_name in sorted(display_names):
            counts = counts_by_type[display_name]
            print(f"  {display_name:30} - M: {counts['M']:3}, P: {counts['P']:4}, Total: {counts['Total']:4}")
        print()
else:
    print("\nNo duplicate officer names found in January 2026 data!")

print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)

moving = jan26[jan26['TYPE'] == 'M']
parking = jan26[jan26['TYPE'] == 'P']

print(f"\nTop 10 Moving Summons Officers:")
print(moving.groupby('OFFICER_DISPLAY_NAME').size().sort_values(ascending=False).head(10))

print(f"\nTop 10 Parking Summons Officers:")
print(parking.groupby('OFFICER_DISPLAY_NAME').size().sort_values(ascending=False).head(10))
