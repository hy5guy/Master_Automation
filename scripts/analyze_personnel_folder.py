#!/usr/bin/env python3
"""
Personnel Folder Analysis and Cleanup
Analyzes all Assignment_Master files and Personnel folder for consolidation.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def analyze_personnel_folder():
    """Analyze Personnel folder and recommend cleanup."""
    personnel_dir = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel")
    
    print("=" * 80)
    print("PERSONNEL FOLDER ANALYSIS")
    print("=" * 80)
    print(f"Location: {personnel_dir}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # List all CSV and XLSX files
    csv_files = list(personnel_dir.glob("**/*.csv"))
    xlsx_files = list(personnel_dir.glob("**/*.xlsx"))
    xlsm_files = list(personnel_dir.glob("**/*.xlsm"))
    
    print(f"Found {len(csv_files)} CSV files")
    print(f"Found {len(xlsx_files)} XLSX files")
    print(f"Found {len(xlsm_files)} XLSM files")
    print()
    
    # Analyze Assignment_Master_V2.csv (canonical source)
    canonical_file = personnel_dir / "Assignment_Master_V2.csv"
    if canonical_file.exists():
        print("--- CANONICAL FILE ---")
        print(f"File: {canonical_file.name}")
        print(f"Size: {canonical_file.stat().st_size:,} bytes")
        print(f"Modified: {datetime.fromtimestamp(canonical_file.stat().st_mtime)}")
        
        try:
            df = pd.read_csv(canonical_file, low_memory=False)
            print(f"Rows: {len(df)}")
            print(f"Columns: {len(df.columns)}")
            
            # Key columns
            key_cols = ['FULL_NAME', 'BADGE_NUMBER', 'TEAM', 'STATUS', 'RANK']
            existing = [c for c in key_cols if c in df.columns]
            print(f"Key columns present: {len(existing)}/{len(key_cols)}")
            print(f"  {', '.join(existing)}")
            
            # Check for actual data
            non_null_rows = df[existing].dropna(how='all')
            print(f"Non-null data rows: {len(non_null_rows)}")
            
        except Exception as e:
            print(f"ERROR reading file: {e}")
    else:
        print(f"⚠ CANONICAL FILE NOT FOUND: {canonical_file}")
    
    print()
    print("=" * 80)
    print("ALL FILES IN PERSONNEL FOLDER")
    print("=" * 80)
    
    all_files = sorted(csv_files + xlsx_files + xlsm_files, key=lambda x: x.stat().st_mtime, reverse=True)
    
    for f in all_files:
        rel_path = f.relative_to(personnel_dir)
        size_kb = f.stat().st_size / 1024
        modified = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
        
        # Categorize
        if "99_Archive" in str(f) or "backups" in str(f):
            category = "ARCHIVE"
        elif f.name == "Assignment_Master_V2.csv":
            category = "CANONICAL"
        elif "assigned_shift" in f.name.lower():
            category = "SHIFT"
        else:
            category = "OTHER"
        
        print(f"[{category:9s}] {rel_path}")
        print(f"              Size: {size_kb:>8.1f} KB | Modified: {modified}")
        print()
    
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    print("""
FILES TO KEEP:
✓ Assignment_Master_V2.csv - CANONICAL source (keep in root)
✓ 2025_12_29_assigned_shift.csv - Recent shift schedule supplement (keep in root)
✓ Assignment_Master_SCHEMA.md - Documentation (keep in root)
✓ 99_Archive/ folder - Historical versions (keep)
✓ backups/ folder - Backups (keep)

FILES TO REVIEW/REMOVE:
? Any Assignment_Master_V2.xlsx in root - May be duplicate of CSV
? Multiple versions in 99_Archive - Keep only dated backups
? Seniority/EmployeeListingByWorkGroup files - Check if still needed

ACTION ITEMS:
1. Verify Assignment_Master_V2.csv has actual personnel data (not just headers)
2. Check if any scripts need .xlsx version (most use .csv)
3. Remove any duplicates in root folder
4. Consolidate archive files with clear dates
    """)

if __name__ == "__main__":
    analyze_personnel_folder()
