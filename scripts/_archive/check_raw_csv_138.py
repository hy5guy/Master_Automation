import pandas as pd

csv_path = r'C:\Users\RobertCarucci\OneDrive - City of Hackensack\01_SourceData\Summons\2026_01_eticket_export.csv'

print("Loading raw CSV...")
df = pd.read_csv(csv_path, sep=';', dtype=str, on_bad_lines='skip')

print(f"Total records: {len(df)}")
print()

print("Officer Id value types:")
print(f"  Non-null: {df['Officer Id'].notna().sum()}")
print(f"  Numeric pattern: {df['Officer Id'].astype(str).str.match(r'^\d+$').sum()}")
print(f"  Not '0': {(df['Officer Id'].astype(str).str.strip() != '0').sum()}")
print()

print("Officer Id 138 analysis:")
badge_138_all = df[df['Officer Id'].astype(str).str.strip() == '138']
print(f"Total records with Officer Id = 138: {len(badge_138_all)}")
print(f"  Moving (M): {len(badge_138_all[badge_138_all['Case Type Code'] == 'M'])}")
print(f"  Parking (P): {len(badge_138_all[badge_138_all['Case Type Code'] == 'P'])}")
print(f"  Court (C): {len(badge_138_all[badge_138_all['Case Type Code'] == 'C'])}")
print()

print("Officer Last Name variations for Officer Id 138:")
print(badge_138_all['Officer Last Name'].value_counts())
