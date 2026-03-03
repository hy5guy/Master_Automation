"""
Check Assignment Master for Traffic Bureau officers (manual audit badges).
"""
import pandas as pd

master_path = r'C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv'

# Manual audit officers: badge (as in e-ticket) -> expected name
traffic_officers = {
    '2027': 'K. TORRES',
    '256': 'G. GALLORINI',
    '717': 'D. MATTALIAN',
    '2030': 'D. RIZZI',
    '2025': 'M. RAMIREZ',
    '329': 'D. FRANCAVILLA',
    '2021': 'J. SQUILLACE',
    '138': 'M. JACOBSEN',
    '327': "M. O'NEILL",
    '2022': 'D. CASSIDY',
}

print("=" * 70)
print("ASSIGNMENT MASTER - TRAFFIC OFFICER CHECK")
print("=" * 70)

master = pd.read_csv(master_path)
print(f"\nTotal master records: {len(master)}")

# Normalize PADDED_BADGE_NUMBER for lookup (handle mixed formats)
master['BADGE_4'] = master['PADDED_BADGE_NUMBER'].astype(str).str.replace(r'\D', '', regex=True).str.zfill(4)

print(f"\n{'Badge':<8} {'Name (Manual)':<20} {'In Master?':<12} {'WG2':<25} {'STATUS':<10}")
print("-" * 80)

for badge_raw, name in traffic_officers.items():
    # E-ticket uses 256, 717, 329 etc. Master may have 0256, 0717, 0329
    badge_4 = str(badge_raw).zfill(4)
    
    # Try exact match first, then 4-digit padded
    match = master[master['BADGE_4'] == badge_4]
    
    if len(match) == 0:
        print(f"{badge_raw:<8} {name:<20} NOT FOUND    {'':<25} {'':<10}")
    else:
        row = match.iloc[0]
        wg2 = str(row.get('WG2', '')).strip() if pd.notna(row.get('WG2')) else ''
        status = str(row.get('STATUS', '')).strip() if pd.notna(row.get('STATUS')) else ''
        full_name = str(row.get('FULL_NAME', '')).strip() if pd.notna(row.get('FULL_NAME')) else ''
        
        ok = "YES" if wg2 == 'TRAFFIC BUREAU' else "NO (wrong bureau)"
        print(f"{badge_raw:<8} {name:<20} {ok:<12} {wg2:<25} {status:<10}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Count how many are TRAFFIC BUREAU vs other
traffic_count = 0
wrong_bureau = []
missing = []

for badge_raw in traffic_officers:
    badge_4 = str(badge_raw).zfill(4)
    match = master[master['BADGE_4'] == badge_4]
    if len(match) == 0:
        missing.append((badge_raw, traffic_officers[badge_raw]))
    else:
        wg2 = str(match.iloc[0].get('WG2', '')).strip()
        if wg2 == 'TRAFFIC BUREAU':
            traffic_count += 1
        else:
            wrong_bureau.append((badge_raw, traffic_officers[badge_raw], wg2))

print(f"\nCorrectly assigned to TRAFFIC BUREAU: {traffic_count} / {len(traffic_officers)}")
if wrong_bureau:
    print(f"\nWrong bureau (need WG2 = TRAFFIC BUREAU):")
    for b, n, w in wrong_bureau:
        print(f"  Badge {b} ({n}) -> currently {w}")
if missing:
    print(f"\nMissing from Assignment Master:")
    for b, n in missing:
        print(f"  Badge {b} ({n})")
