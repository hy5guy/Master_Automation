"""
Summons E-Ticket Data Normalization Script (Hybrid Version)
===========================================================
Purpose: Process monthly e-ticket exports and map to Assignment_Master_V2.csv
Author: R. A. Carucci / Coding Partner
Updated: 2026-02-17

Input Files:
  - 2026_01_eticket_export.csv (COMMA-delimited)
  - Assignment_Master_V2.csv

Output:
  - summons_powerbi_latest.xlsx

Features:
  - Robust CSV parsing (handles commas and messy quotes)
  - HTML Entity cleaning
  - Preserves hard-coded overrides for PEO/Traffic
"""

import pandas as pd
import re
import html
import csv
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================
SUMMONS_PATH = '2026_01_eticket_export.csv'
MASTER_PATH = 'Assignment_Master_V2.csv'
OUTPUT_PATH = 'summons_powerbi_latest.xlsx'
OVERRIDE_LOG_PATH = 'logs/summons_badge_overrides.txt'

def clean_text(text):
    """
    Remove tabs, collapse multiple spaces, strip whitespace, and unescape HTML.
    """
    if pd.isna(text):
        return ""
    
    text = str(text)
    
    # Unescape HTML (e.g., &amp; -> &, &#36; -> $) - Added from ChatGPT suggestion
    try:
        text = html.unescape(text)
    except:
        pass

    text = text.replace('\t', ' ')      # Remove tabs
    text = re.sub(r'\s+', ' ', text)    # Collapse multiple spaces
    return text.strip()

def apply_hard_coded_overrides(merged_df, override_log_path):
    """
    Apply hard-coded mapping overrides for known high-volume officers.
    (Preserved from Original Script)
    """
    print("\n[8.5/9] Applying hard-coded badge overrides...")
    
    override_count = 0
    override_log = []
    
    # Rule 0: TITLE-based override - Parking Enforcement Officer / PEO -> TRAFFIC BUREAU
    if 'TITLE' in merged_df.columns:
        title_str = merged_df['TITLE'].fillna('').astype(str).str.strip().str.upper()
        peo_title_mask = (
            (title_str == 'PARKING ENFORCEMENT OFFICER') |
            (title_str == 'PEO')
        )
        peo_title_count = peo_title_mask.sum()
        if peo_title_count > 0:
            merged_df.loc[peo_title_mask, 'WG2'] = 'TRAFFIC BUREAU'
            merged_df.loc[peo_title_mask, 'TEAM'] = 'TRAFFIC'
            override_log.append(f"TITLE override: {peo_title_count} records")
            override_count += peo_title_count
    
    # Rule 1: PEO Badge Range Override (2000-2099 -> TRAFFIC BUREAU)
    peo_range_mask = (
        (merged_df['WG2'].isna() | (merged_df['WG2'] == 'UNKNOWN')) &
        (merged_df['PADDED_BADGE_NUMBER'].str.match(r'^20[0-9]{2}$', na=False))
    )
    
    peo_range_count = peo_range_mask.sum()
    if peo_range_count > 0:
        merged_df.loc[peo_range_mask, 'WG2'] = 'TRAFFIC BUREAU'
        merged_df.loc[peo_range_mask, 'TEAM'] = 'TRAFFIC'
        merged_df.loc[peo_range_mask, 'RANK'] = 'PEO'
        merged_df.loc[peo_range_mask, 'ASSIGNMENT_FOUND'] = True 
        
        override_log.append(f"PEO Range Override: {peo_range_count} records")
        override_count += peo_range_count
    
    # Rule 2: Known Traffic Bureau Officers (specific badges)
    known_traffic_badges = {
        '0256': 'GALLORINI G',
    }
    
    for badge, name in known_traffic_badges.items():
        specific_mask = (
            (merged_df['PADDED_BADGE_NUMBER'] == badge) &
            ((merged_df['WG2'].isna()) | (merged_df['WG2'] != 'TRAFFIC BUREAU'))
        )
        
        specific_count = specific_mask.sum()
        if specific_count > 0:
            merged_df.loc[specific_mask, 'WG2'] = 'TRAFFIC BUREAU'
            merged_df.loc[specific_mask, 'TEAM'] = 'TRAFFIC'
            override_log.append(f"Badge {badge} ({name}): {specific_count} records")
            override_count += specific_count

    # Log writing logic
    if override_count > 0:
        print(f"  ✓ Applied overrides to {override_count} records")
        # Ensure directory exists
        Path(override_log_path).parent.mkdir(parents=True, exist_ok=True)
        with open(override_log_path, 'a', encoding='utf-8') as f:
            f.write(f"\nOverride Run {datetime.now()}:\n" + "\n".join(override_log))
    else:
        print("  ✓ No overrides needed.")

    return merged_df

def normalize_personnel_data(summons_path, master_path, output_path):
    print("=" * 60)
    print("SUMMONS DATA NORMALIZATION - HYBRID ETL")
    print("=" * 60)

    # 1. Load Data
    # UPDATED: Changed sep to ',' and added quotechar to handle messy CSVs
    print("\n[1/9] Loading source data...")
    try:
        summons_df = pd.read_csv(
            summons_path, 
            sep=',',                  # FIXED: Attachment 3 is comma-separated
            quotechar='"',            # FIXED: Handles "5'01""" quotes
            quoting=csv.QUOTE_MINIMAL,
            on_bad_lines='skip', 
            engine='python',
            encoding='utf-8' # Try utf-8 first, fall back to cp1252 if needed
        )
        print(f"  ✓ Loaded {len(summons_df)} summons records")
    except UnicodeDecodeError:
        print("  ! UTF-8 failed, retrying with cp1252...")
        summons_df = pd.read_csv(summons_path, sep=',', quotechar='"', on_bad_lines='skip', encoding='cp1252')
        print(f"  ✓ Loaded {len(summons_df)} records (cp1252)")
    except Exception as e:
        print(f"  ❌ Error loading summons file: {e}")
        return None

    try:
        master_df = pd.read_csv(master_path)
        print(f"  ✓ Loaded {len(master_df)} master personnel records")
    except Exception as e:
        print(f"  ❌ Error loading master file: {e}")
        return None

    # 2. Clean Names
    print("[2/9] Cleaning text fields...")
    name_cols = ['Officer First Name', 'Officer Middle Initial', 'Officer Last Name']
    for col in name_cols:
        if col in summons_df.columns:
            summons_df[col] = summons_df[col].apply(clean_text)
    
    # 3. Badge Normalization
    print("[3/9] Normalizing badges...")
    # Clean Officer Id before padding (remove non-numeric characters just in case)
    summons_df['Officer Id Clean'] = pd.to_numeric(summons_df['Officer Id'], errors='coerce').fillna(0).astype(int)
    summons_df['PADDED_BADGE_NUMBER'] = summons_df['Officer Id Clean'].astype(str).str.zfill(4)

    master_df['PADDED_BADGE_NUMBER'] = (
        pd.to_numeric(master_df['PADDED_BADGE_NUMBER'], errors='coerce')
        .fillna(0).astype(int).astype(str).str.zfill(4)
    )

    # 4. Create Display Name
    summons_df['OFFICER_DISPLAY_NAME'] = (
        summons_df['Officer First Name'] + " " + 
        summons_df['Officer Middle Initial'].fillna('') + " " + 
        summons_df['Officer Last Name']
    ).str.replace(r'\s+', ' ', regex=True).str.strip()
    summons_df['OFFICER_NAME_RAW'] = summons_df['OFFICER_DISPLAY_NAME']

    # 5. Date Parsing
    print("[4/9] Parsing dates...")
    if 'Issue Date' in summons_df.columns:
        summons_df['ISSUE_DATE'] = pd.to_datetime(summons_df['Issue Date'], errors='coerce')
        summons_df['Year'] = summons_df['ISSUE_DATE'].dt.year
        summons_df['Month'] = summons_df['ISSUE_DATE'].dt.month
        summons_df['Month_Year'] = summons_df['ISSUE_DATE'].dt.strftime('%m-%y')

    # 6. Metadata
    summons_df['TICKET_COUNT'] = 1
    summons_df['IS_AGGREGATE'] = False
    summons_df['PROCESSING_TIMESTAMP'] = datetime.now()
    
    # DQ Scoring
    summons_df['DATA_QUALITY_SCORE'] = 100
    summons_df.loc[summons_df['PADDED_BADGE_NUMBER'] == '0000', 'DATA_QUALITY_SCORE'] -= 50
    summons_df.loc[summons_df['ISSUE_DATE'].isna(), 'DATA_QUALITY_SCORE'] -= 50
    summons_df['DATA_QUALITY_TIER'] = summons_df['DATA_QUALITY_SCORE'].apply(lambda x: "High" if x == 100 else "Critical Issue")

    # 7. Merge with Master
    print("[6/9] Merging with Assignment Master...")
    master_subset = master_df[master_df['STATUS'] == 'ACTIVE'].copy()
    merged_df = summons_df.merge(
        master_subset[['PADDED_BADGE_NUMBER', 'WG1', 'WG2', 'WG3', 'TEAM', 'RANK', 'TITLE']], 
        on='PADDED_BADGE_NUMBER', 
        how='left'
    )

    # 8. Apply Overrides (CRITICAL LOGIC RESTORED)
    merged_df = apply_hard_coded_overrides(merged_df, OVERRIDE_LOG_PATH)

    # Fill remaining unknowns
    merged_df['WG2'] = merged_df['WG2'].fillna('UNKNOWN')

    # 9. Trim columns
    print("[9/9] Preparing final export...")
    
    col_map = {
        'Ticket Number': 'TICKET_NUMBER', 
        'Statute': 'VIOLATION_NUMBER', 
        'Case Type Code': 'TYPE', 
        'Penalty': 'FINE_AMOUNT',
        'Violation Description': 'VIOLATION_DESCRIPTION'
    }
    # Only rename columns that actually exist
    existing_map = {k: v for k, v in col_map.items() if k in merged_df.columns}
    merged_df = merged_df.rename(columns=existing_map)

    # Calculate Type
    if 'TYPE' in merged_df.columns:
        type_map = {'M': 'Moving', 'P': 'Parking', 'C': 'Court'}
        merged_df['VIOLATION_TYPE'] = merged_df['TYPE'].map(type_map).fillna('Other')

    # Ensure columns exist before selection
    keep_columns = [
        'TICKET_NUMBER', 'PADDED_BADGE_NUMBER', 'OFFICER_DISPLAY_NAME', 
        'OFFICER_NAME_RAW', 'ISSUE_DATE', 'VIOLATION_NUMBER', 
        'VIOLATION_DESCRIPTION', 'VIOLATION_TYPE', 'TYPE', 'STATUS', 
        'LOCATION', 'Year', 'Month', 'Month_Year', 'TEAM', 'WG1', 'WG2', 
        'WG3', 'RANK', 'TITLE', 'TICKET_COUNT', 'FINE_AMOUNT', 
        'DATA_QUALITY_SCORE', 'DATA_QUALITY_TIER', 'PROCESSING_TIMESTAMP'
    ]
    
    final_cols = [c for c in keep_columns if c in merged_df.columns]
    merged_df = merged_df[final_cols].copy()

    merged_df.to_excel(output_path, index=False, sheet_name='Summons_Data')
    print(f"✓ SUCCESS! Output saved to: {output_path}")
    return merged_df

# ============================================================================
# MAIN
# ============================================================================
if __name__ == '__main__':
    normalize_personnel_data(SUMMONS_PATH, MASTER_PATH, OUTPUT_PATH)