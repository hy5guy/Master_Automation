#!/usr/bin/env python3
"""
Update Assignment Master: Change PATROL BUREAU to PATROL DIVISION
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def main():
    am_path = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv")
    
    # Create backup
    backup_path = am_path.parent / f"Assignment_Master_V2_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    print("Loading Assignment Master...")
    am = pd.read_csv(am_path)
    
    # Create backup
    am.to_csv(backup_path, index=False)
    print(f"Backup created: {backup_path.name}")
    
    # Count before
    count_before = (am['WG2'] == 'PATROL BUREAU').sum()
    print(f"  Records with 'PATROL BUREAU': {count_before}")
    
    # Replace PATROL BUREAU with PATROL DIVISION
    am['WG2'] = am['WG2'].replace('PATROL BUREAU', 'PATROL DIVISION')
    
    # Count after
    count_after = (am['WG2'] == 'PATROL DIVISION').sum()
    print(f"  Records with 'PATROL DIVISION': {count_after}")
    
    # Save updated file
    am.to_csv(am_path, index=False)
    print(f"\nAssignment Master updated successfully")
    print(f"  Changed {count_before} records from 'PATROL BUREAU' to 'PATROL DIVISION'")
    
    # Show updated WG2 distribution
    print(f"\nUpdated WG2 value counts:")
    print(am['WG2'].value_counts().to_string())

if __name__ == "__main__":
    main()
