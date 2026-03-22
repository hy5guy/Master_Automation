"""
Update WG2 for existing Traffic/PEO officers
Simply updates the WG2 and TEAM columns for badges that already exist
"""
import sys
from pathlib import Path

try:
    import pandas as pd
    from datetime import datetime
    
    # Load Assignment Master
    master_path = Path(r"C:\Users\RobertCarucci\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv")
    
    print(f"Reading: {master_path.name}")
    df = pd.read_csv(master_path)
    
    print(f"Total rows: {len(df)}")
    
    # Create backup
    backup = master_path.parent / f"{master_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(backup, index=False)
    print(f"Backup created: {backup.name}")
    
    # Update badges
    updates = [
        {'badge': '387', 'name': 'ROYAL', 'wg2': 'TRAFFIC BUREAU', 'team': 'TRAFFIC'},
        {'badge': '839', 'name': 'VIVONA', 'wg2': 'TRAFFIC BUREAU', 'team': 'TRAFFIC'},
        {'badge': '844', 'name': 'TAHA-ZEIDAN', 'wg2': 'TRAFFIC BUREAU', 'team': 'TRAFFIC'}
    ]
    
    print("\nUpdating WG2 assignments:")
    for update in updates:
        badge = update['badge']
        mask = df['PADDED_BADGE_NUMBER'].astype(str).str.zfill(4) == badge.zfill(4)
        
        if mask.sum() > 0:
            df.loc[mask, 'WG2'] = update['wg2']
            df.loc[mask, 'TEAM'] = update['team']
            df.loc[mask, 'STATUS'] = 'ACTIVE'
            print(f"  Badge {badge} ({update['name']}): WG2 = {update['wg2']}, TEAM = {update['team']}")
        else:
            print(f"  Badge {badge} NOT FOUND")
    
    # Save
    df.to_csv(master_path, index=False)
    print(f"\nSaved: {master_path.name}")
    
    # Verify
    print("\nVerifying updates:")
    for update in updates:
        badge = update['badge']
        record = df[df['PADDED_BADGE_NUMBER'].astype(str).str.zfill(4) == badge.zfill(4)]
        if len(record) > 0:
            print(f"  Badge {badge}: WG2={record.iloc[0]['WG2']}, TEAM={record.iloc[0]['TEAM']}, STATUS={record.iloc[0]['STATUS']}")
    
    print("\nDONE! Now re-run the patch script to update summons data.")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
