"""
Add Traffic/PEO officers to Assignment Master
Adds the 4 UNKNOWN badges to Assignment_Master_V2.csv
"""
import sys
from pathlib import Path

try:
    import pandas as pd
    
    # Load Assignment Master
    master_path = Path(r"C:\Users\RobertCarucci\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv")
    
    print(f"Reading: {master_path.name}")
    df = pd.read_csv(master_path)
    
    print(f"Current rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Check if these badges already exist
    badges_to_add = ['0387', '0839', '0844', '9110']
    
    for badge in badges_to_add:
        exists = df[df['PADDED_BADGE_NUMBER'].astype(str).str.zfill(4) == badge]
        if len(exists) > 0:
            print(f"\nBadge {badge} already exists:")
            print(exists[['PADDED_BADGE_NUMBER', 'FIRST_NAME', 'LAST_NAME', 'WG2', 'TEAM', 'STATUS']].to_string(index=False))
        else:
            print(f"\nBadge {badge} NOT FOUND - needs to be added")
    
    # Show what columns we need for new records
    print("\nRequired columns for new records:")
    print(df.columns.tolist())
    
    # Create backup
    backup = master_path.parent / f"{master_path.stem}_backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(backup, index=False)
    print(f"\nBackup created: {backup.name}")
    
    # Prepare new records based on the summons data
    new_records = [
        # Badge 387 - PO C ROYAL (18 summons - mostly Parking)
        {
            'PADDED_BADGE_NUMBER': '0387',
            'BADGE_NUMBER': 387,
            'FIRST_NAME': 'C',
            'LAST_NAME': 'ROYAL',
            'RANK': 'PO',
            'TITLE': 'PARKING ENFORCEMENT OFFICER',
            'WG2': 'TRAFFIC BUREAU',
            'TEAM': 'TRAFFIC',
            'STATUS': 'ACTIVE',
            'WG1': '',
            'WG3': '',
            'WG4': '',
            'WG5': '',
            'POSS_CONTRACT_TYPE': ''
        },
        # Badge 839 - SPO R VIVONA (4 summons)
        {
            'PADDED_BADGE_NUMBER': '0839',
            'BADGE_NUMBER': 839,
            'FIRST_NAME': 'R',
            'LAST_NAME': 'VIVONA',
            'RANK': 'SPO',
            'TITLE': 'SPECIAL POLICE OFFICER',
            'WG2': 'TRAFFIC BUREAU',
            'TEAM': 'TRAFFIC',
            'STATUS': 'ACTIVE',
            'WG1': '',
            'WG3': '',
            'WG4': '',
            'WG5': '',
            'POSS_CONTRACT_TYPE': ''
        },
        # Badge 844 - SPO H TAHA-ZEIDAN (3 summons)
        {
            'PADDED_BADGE_NUMBER': '0844',
            'BADGE_NUMBER': 844,
            'FIRST_NAME': 'H',
            'LAST_NAME': 'TAHA-ZEIDAN',
            'RANK': 'SPO',
            'TITLE': 'SPECIAL POLICE OFFICER',
            'WG2': 'TRAFFIC BUREAU',
            'TEAM': 'TRAFFIC',
            'STATUS': 'ACTIVE',
            'WG1': '',
            'WG3': '',
            'WG4': '',
            'WG5': '',
            'POSS_CONTRACT_TYPE': ''
        },
        # Badge 9110 - D.C.FF C ANNUNZIATA (2 summons)
        {
            'PADDED_BADGE_NUMBER': '9110',
            'BADGE_NUMBER': 9110,
            'FIRST_NAME': 'C',
            'LAST_NAME': 'ANNUNZIATA',
            'RANK': 'D.C.FF',
            'TITLE': 'FIRE FIGHTER',
            'WG2': 'FIRE DEPARTMENT',
            'TEAM': 'FIRE',
            'STATUS': 'ACTIVE',
            'WG1': '',
            'WG3': '',
            'WG4': '',
            'WG5': '',
            'POSS_CONTRACT_TYPE': ''
        }
    ]
    
    # Add new records
    new_df = pd.DataFrame(new_records)
    
    # Reorder columns to match original
    new_df = new_df[df.columns]
    
    # Append to existing
    updated_df = pd.concat([df, new_df], ignore_index=True)
    
    print(f"\nAdding {len(new_records)} new records...")
    print("\nNew records:")
    for rec in new_records:
        print(f"  {rec['PADDED_BADGE_NUMBER']} - {rec['RANK']} {rec['FIRST_NAME']} {rec['LAST_NAME']} - {rec['WG2']}")
    
    # Save updated file
    updated_df.to_csv(master_path, index=False)
    print(f"\nSaved: {master_path}")
    print(f"Total rows: {len(updated_df)} (was {len(df)})")
    
    print("\nDONE! Assignment Master updated.")
    print("Next: Re-run patch_summons_direct.py to reclassify with new assignments")
    
except ImportError:
    print("ERROR: pandas not installed")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
