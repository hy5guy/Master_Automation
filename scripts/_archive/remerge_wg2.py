"""
Re-classify summons with updated Assignment Master (includes WG2 assignments)
"""
import sys
from pathlib import Path

try:
    import pandas as pd
    from datetime import datetime
    
    # Paths
    summons_path = Path(r"C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx")
    master_path = Path(r"C:\Users\RobertCarucci\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv")
    
    print("Loading files...")
    df = pd.read_excel(summons_path, sheet_name="Summons_Data")
    master = pd.read_csv(master_path)
    
    print(f"Summons records: {len(df)}")
    print(f"Assignment Master records: {len(master)}")
    
    # Prepare master lookup
    master['PADDED_BADGE_NUMBER'] = master['PADDED_BADGE_NUMBER'].astype(str).str.zfill(4)
    master_lookup = master[['PADDED_BADGE_NUMBER', 'WG2', 'TEAM', 'STATUS']].copy()
    master_lookup = master_lookup[master_lookup['STATUS'] == 'ACTIVE']
    
    print(f"\nActive officers in master: {len(master_lookup)}")
    
    # Fix data type for merge
    df['PADDED_BADGE_NUMBER'] = df['PADDED_BADGE_NUMBER'].astype(str).str.zfill(4)
    
    # Check UNKNOWN before update
    unknown_before = df[(df['WG2'].isna()) | (df['WG2'] == '') | (df['WG2'] == 'UNKNOWN')]
    print(f"UNKNOWN WG2 records BEFORE: {len(unknown_before)}")
    
    # Re-merge WG2 from Assignment Master
    # First, drop old WG2/TEAM columns
    if 'WG2' in df.columns:
        df = df.drop(columns=['WG2'])
    if 'TEAM' in df.columns:
        df = df.drop(columns=['TEAM'])
    
    # Merge with updated master
    df = df.merge(
        master_lookup[['PADDED_BADGE_NUMBER', 'WG2', 'TEAM']],
        on='PADDED_BADGE_NUMBER',
        how='left'
    )
    
    # Fill missing with UNKNOWN
    df['WG2'] = df['WG2'].fillna('UNKNOWN')
    df['TEAM'] = df['TEAM'].fillna('UNKNOWN')
    
    # Check UNKNOWN after update
    unknown_after = df[(df['WG2'] == 'UNKNOWN')]
    print(f"UNKNOWN WG2 records AFTER: {len(unknown_after)}")
    
    if len(unknown_after) < len(unknown_before):
        print(f"SUCCESS! Reduced UNKNOWN by {len(unknown_before) - len(unknown_after)} records")
    
    # Show WG2 distribution
    print(f"\nWG2 Distribution:")
    print(df['WG2'].value_counts())
    
    # Backup and save
    backup = summons_path.parent / f"{summons_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    import shutil
    shutil.copy2(summons_path, backup)
    print(f"\nBackup: {backup.name}")
    
    df.to_excel(summons_path, sheet_name="Summons_Data", index=False)
    print(f"Saved: {summons_path.name}")
    
    print("\nDONE! Summons data updated with new WG2 assignments.")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
