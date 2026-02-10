"""Update backfill file with March 2025 data"""
import pandas as pd
from pathlib import Path

backfill_file = Path(r"C:\Dev\PowerBI_Date\Backfill\2025_09\summons\Hackensack Police Department - Summons Dashboard.csv")

print("=" * 70)
print("UPDATING BACKFILL FILE WITH MARCH 2025 DATA")
print("=" * 70)

# Read existing backfill file
df = pd.read_csv(backfill_file, encoding='utf-8')
print(f"\nCurrent rows in backfill file: {len(df)}")
print(f"\nExisting months: {sorted(df['Month_Year'].unique())}")

# Check if 03-25 already exists
if '03-25' in df['Month_Year'].values:
    print("\nWARNING: 03-25 already exists in backfill file!")
    existing = df[df['Month_Year'] == '03-25']
    print(existing)
else:
    print("\n03-25 not found - will add it")

# Create new rows for March 2025
new_rows = pd.DataFrame([
    {'TYPE': 'M', 'Month_Year': '03-25', 'Count of TICKET_NUMBER': 454},
    {'TYPE': 'P', 'Month_Year': '03-25', 'Count of TICKET_NUMBER': 3097}
])

# Combine existing data with new rows
df_updated = pd.concat([df, new_rows], ignore_index=True)

# Sort by TYPE and Month_Year for consistency
df_updated = df_updated.sort_values(['TYPE', 'Month_Year']).reset_index(drop=True)

print(f"\nUpdated rows: {len(df_updated)}")
print(f"\n03-25 rows added:")
march_rows = df_updated[df_updated['Month_Year'] == '03-25']
print(march_rows.to_string(index=False))

# Save updated file
df_updated.to_csv(backfill_file, index=False, encoding='utf-8')
print(f"\n✅ Backfill file updated and saved: {backfill_file}")
