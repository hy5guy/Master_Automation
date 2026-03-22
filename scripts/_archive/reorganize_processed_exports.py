#!/usr/bin/env python3
"""
Reorganize Processed_Exports files to match page-based folder structure.
"""

import shutil
from pathlib import Path

# Old folder → New folder mapping
FOLDER_RENAMES = {
    "Arrests": "arrests",
    "NIBRS": "nibrs",
    "Response_Times": "response_time",
    "Benchmark": "benchmark",
    "Drone": "drone",
    "Patrol": "patrol",
    "Traffic": "traffic",  # Some stay, Motor Vehicle Accidents moves to traffic_mva
    "Detectives": None,  # Will split into detectives_pt1, detectives_pt2, detectives_case_dispositions
    "CSB": "crime_suppression_bureau",
    "STACP": None,  # Will split into stacp_pt1, stacp_pt2
    "Community_Engagement": "social_media_and_time_report",
    "Executive": "law_enforcement_duties",
    "Support_Services": "remu",
    "SSOCC": "ssocc",
    "Training": "policy_and_training_qual",
    "Time_Off": "social_media_and_time_report",
    "Summons": "summons",
}

# Specific file moves (legacy; canonical routing now uses traffic/ per visual_export_mapping.json)
SPECIFIC_MOVES = {
    "motor_vehicle_accidents_summary": "traffic",
}

def reorganize_files():
    """Reorganize processed export files to page-based folders."""
    processed_root = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports")
    
    if not processed_root.exists():
        print(f"Error: {processed_root} not found")
        return
    
    moved_count = 0
    
    # Process each old folder
    for old_folder in processed_root.iterdir():
        if not old_folder.is_dir() or old_folder.name == "Other":
            continue
        
        new_folder_name = FOLDER_RENAMES.get(old_folder.name)
        
        if new_folder_name is None:
            print(f"[SKIP] {old_folder.name} - needs manual split")
            continue
        
        new_folder = processed_root / new_folder_name
        new_folder.mkdir(parents=True, exist_ok=True)
        
        # Move all CSV files
        for csv_file in old_folder.glob("*.csv"):
            # Check if this file needs a specific destination
            file_base = csv_file.stem.split("_", 2)[-1] if "_" in csv_file.stem else csv_file.stem
            specific_dest = SPECIFIC_MOVES.get(file_base)
            
            if specific_dest:
                dest_folder = processed_root / specific_dest
                dest_folder.mkdir(parents=True, exist_ok=True)
                dest_file = dest_folder / csv_file.name
            else:
                dest_file = new_folder / csv_file.name
            
            if dest_file.exists():
                print(f"[EXISTS] {csv_file.name} already at destination")
            else:
                shutil.move(str(csv_file), str(dest_file))
                print(f"[MOVED] {csv_file.name}")
                print(f"  {old_folder.name}/ -> {dest_file.parent.name}/")
                moved_count += 1
        
        # Remove old folder if empty
        if not list(old_folder.glob("*.csv")):
            try:
                old_folder.rmdir()
                print(f"[REMOVED] Empty folder: {old_folder.name}/")
            except OSError:
                print(f"[KEEP] Folder not empty: {old_folder.name}/")
    
    print(f"\n[SUCCESS] Moved {moved_count} files")

if __name__ == "__main__":
    reorganize_files()
