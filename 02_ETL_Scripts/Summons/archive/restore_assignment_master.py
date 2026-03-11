#!/usr/bin/env python3
"""
Restore Assignment Master file from archive and update PATROL BUREAU to PATROL DIVISION
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def main():
    # Paths
    archived_file = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\99_Archive\2026_01_11_Assignment_Master_V2.csv")
    target_file = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv")
    
    print("Loading archived Assignment Master file...")
    if not archived_file.exists():
        print(f"ERROR: Archived file not found: {archived_file}")
        return 1
    
    am = pd.read_csv(archived_file)
    print(f"Loaded {len(am)} records from archived file")
    
    # Check current WG2 values
    patrol_bureau = (am['WG2'] == 'PATROL BUREAU').sum()
    patrol_division = (am['WG2'] == 'PATROL DIVISION').sum()
    print(f"  PATROL BUREAU: {patrol_bureau} records")
    print(f"  PATROL DIVISION: {patrol_division} records")
    
    # Update PATROL BUREAU to PATROL DIVISION if needed
    if patrol_bureau > 0:
        print(f"\nUpdating {patrol_bureau} records from PATROL BUREAU to PATROL DIVISION...")
        am['WG2'] = am['WG2'].replace('PATROL BUREAU', 'PATROL DIVISION')
        updated_count = (am['WG2'] == 'PATROL DIVISION').sum()
        print(f"  Updated: {updated_count} records now have PATROL DIVISION")
    else:
        print("\nNo PATROL BUREAU records found - already updated")
    
    # Create backup if target file exists
    if target_file.exists():
        backup_path = target_file.parent / f"Assignment_Master_V2_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        pd.read_csv(target_file).to_csv(backup_path, index=False)
        print(f"\nCreated backup of existing file: {backup_path.name}")
    
    # Save to target location
    am.to_csv(target_file, index=False)
    print(f"\nAssignment Master file restored to:")
    print(f"  {target_file}")
    print(f"\nFile is ready for ETL processing")
    
    return 0

if __name__ == "__main__":
    exit(main())
