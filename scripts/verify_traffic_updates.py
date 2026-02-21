"""
Verify Traffic Bureau updates in Assignment Master.
Officers that should be TRAFFIC BUREAU: FRANCAVILLA (329), J. MORA (57), S. TOVBIN (344).
"""
import pandas as pd

master_path = r'C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv'

# Officers user confirmed/updated to Traffic
traffic_updates = {
    '329': 'D. FRANCAVILLA',
    '57': 'J. MORA',   # may be 057 in master
    '344': 'S. TOVBIN',
}

print("=" * 60)
print("TRAFFIC BUREAU UPDATE VERIFICATION")
print("=" * 60)

master = pd.read_csv(master_path)
master['BADGE_4'] = master['PADDED_BADGE_NUMBER'].astype(str).str.replace(r'\D', '', regex=True).str.zfill(4)

print(f"\n{'Badge':<8} {'Name':<22} {'WG2':<25} {'Status'}")
print("-" * 65)

all_ok = True
for badge_raw, name in traffic_updates.items():
    badge_4 = str(badge_raw).zfill(4)
    match = master[master['BADGE_4'] == badge_4]
    
    if len(match) == 0:
        print(f"{badge_raw:<8} {name:<22} NOT FOUND IN MASTER")
        all_ok = False
    else:
        row = match.iloc[0]
        wg2 = str(row.get('WG2', '')).strip() if pd.notna(row.get('WG2')) else ''
        full_name = str(row.get('FULL_NAME', '')).strip() if pd.notna(row.get('FULL_NAME')) else ''
        
        if wg2 == 'TRAFFIC BUREAU':
            print(f"{badge_raw:<8} {name:<22} {wg2:<25} OK")
        else:
            print(f"{badge_raw:<8} {name:<22} {wg2:<25} -> Change to TRAFFIC BUREAU")
            all_ok = False

print("\n" + "=" * 60)
if all_ok:
    print("All three officers are set to TRAFFIC BUREAU.")
    print("Next: Re-run ETL -> python run_summons_etl.py")
else:
    print("Fix the officers above in Assignment_Master_V2.csv, then re-run ETL.")
print("=" * 60)
