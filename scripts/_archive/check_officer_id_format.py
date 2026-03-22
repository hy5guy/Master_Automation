import pandas as pd

df = pd.read_csv(
    r'C:\Users\RobertCarucci\OneDrive - City of Hackensack\01_SourceData\Summons\2026_01_eticket_export.csv',
    sep=';', 
    dtype=str, 
    on_bad_lines='skip'
)

print('Unique Officer Id values (first 30):')
print(df['Officer Id'].unique()[:30])
print()

print('Officer Id format check:')
sample_ids = df['Officer Id'].dropna().head(10)
for oid in sample_ids:
    print(f"  '{oid}' (len={len(oid)}, stripped='{oid.strip()}')")
print()

print('Officer Id 138 search:')
oid_138 = df[df['Officer Id'].astype(str).str.strip() == '138']
print(f'Found {len(oid_138)} records with Officer Id = 138')

if len(oid_138) > 0:
    print()
    print('Case Type breakdown:')
    print(oid_138['Case Type Code'].value_counts())
