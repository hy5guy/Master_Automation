#!/usr/bin/env python3
"""
Update visual_export_mapping.json with page-based folder names.
Normalizes page names: lowercase, "&" → "and", spaces → underscores
"""

import json
from pathlib import Path

# Mapping of visual name to Power BI page name
VISUAL_TO_PAGE = {
    # Arrests page
    "Arrest Categories by Type and Gender": "arrests",
    "Arrest Distribution by Local, State & Out of State": "arrests",
    "TOP 5 ARREST LEADERS": "arrests",
    
    # NIBRS page
    "13-Month NIBRS Clearance Rate Trend": "nibrs",
    
    # Response Time page
    "Average Response Times  Values are in mmss": "response_time",
    "Response Times by Priority": "response_time",
    
    # Benchmark page
    "Incident Count by Date and Event Type": "benchmark",
    "Incident Distribution by Event Type": "benchmark",
    "Use of Force Incident Matrix": "benchmark",
    
    # Chief Projects page
    "Chief Michael Antista's Projects and Initiatives": "chief_projects",
    
    # Social Media and Time Report page
    "Social Media Posts": "social_media_and_time_report",
    "Monthly Accrual and Usage Summary": "social_media_and_time_report",
    
    # Law Enforcement Duties page
    "Chief Law Enforcement Executive Duties": "law_enforcement_duties",
    
    # Out-Reach page
    "Engagement Initiatives by Bureau": "out_reach",
    
    # Summons page
    "Department-Wide Summons": "summons",
    "Summons  Moving & Parking  All Bureaus": "summons",
    "Top 5 Parking Violations - Department Wide": "summons",
    "Top 5 Moving Violations - Department Wide": "summons",
    
    # Patrol page
    "Patrol Division": "patrol",
    
    # Drone page
    "DFR Activity Performance Metrics": "drone",
    "Non-DFR Performance Metrics": "drone",
    
    # Traffic page
    "Traffic Bureau": "traffic",
    
    # Traffic MVA page
    "Motor Vehicle Accidents - Summary": "traffic_mva",
    
    # STACP pages
    "School Threat Assessment & Crime Prevention  Part 1": "stacp_pt1",
    "School Threat Assessment & Crime Prevention  Part 2": "stacp_pt2",
    
    # Detective pages
    "Detective Division  Part 1": "detectives_pt1",
    "Detective Division  Part 2": "detectives_pt2",
    
    # Detectives Case Dispositions page
    "Detective Clearance Rate Performance": "detectives_case_dispositions",
    "Detective Case Dispositions - Performance Review": "detectives_case_dispositions",
    
    # Crime Suppression Bureau page
    "Crime Suppressions Bureau Monthly Activity Analysis": "crime_suppression_bureau",
    
    # REMU page
    "Records & Evidence Unit": "remu",
    
    # Policy & Training Qual page
    "In-Person Training": "policy_and_training_qual",
    "Training Cost by Delivery Method": "policy_and_training_qual",
    
    # SSOCC page
    "Safe Streets Operations Control Center - Service Breakdown": "ssocc",
}

def normalize_page_name(page: str) -> str:
    """Convert page name to folder name: lowercase, & → and, spaces → _"""
    return page.lower().replace(" & ", "_and_").replace("&", "_and_").replace(" ", "_")

def update_mapping():
    """Update mapping file with page-based folder names."""
    config_path = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\Standards\config\powerbi_visuals\visual_export_mapping.json")
    
    if not config_path.exists():
        print(f"Error: {config_path} not found")
        return
    
    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)
    
    updated_count = 0
    for entry in config.get("mappings", []):
        visual_name = entry.get("visual_name", "")
        
        # Find page name for this visual
        page_folder = VISUAL_TO_PAGE.get(visual_name)
        
        if page_folder:
            old_folder = entry.get("target_folder", "")
            if old_folder != page_folder:
                entry["target_folder"] = page_folder
                print(f"[UPDATE] {visual_name}")
                print(f"  {old_folder} -> {page_folder}")
                updated_count += 1
        else:
            print(f"[WARN] No mapping for: {visual_name} (keeping {entry.get('target_folder', 'Unknown')})")
    
    if updated_count > 0:
        # Save updated mapping
        with config_path.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"\n[SUCCESS] Updated {updated_count} entries in mapping")
    else:
        print("\n[SUCCESS] No updates needed")

if __name__ == "__main__":
    update_mapping()
