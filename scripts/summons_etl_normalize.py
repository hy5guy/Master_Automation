"""
Summons E-Ticket Data Normalization Script
===========================================

Purpose: Process monthly e-ticket exports and map to Assignment_Master_V2.csv
Author: R. A. Carucci
Updated: 2026-02-17 (Hard-coded overrides added for PEO attribution)

This script implements the logic documented in SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md
with corrections for actual e-ticket export column names and formats.

Input Files:
  - 2026_01_eticket_export.csv (semicolon-delimited)
  - Assignment_Master_V2.csv

Output:
  - summons_powerbi_latest.xlsx (ready for Power BI import)

Key Features:
  - Badge number padding and normalization (256 → "0256")
  - Officer name cleaning (removes tabs, extra spaces, rank prefixes)
  - Active personnel filtering (STATUS = "ACTIVE")
  - Bureau consolidation (OSO → PATROL DIVISION)
  - Hard-coded overrides for PEO badges (2000-2099 range) [NEW 2026-02-17]
  - 13-month rolling window metadata
  - Unknown badge handling (WG2 = "UNKNOWN")
"""

import pandas as pd
import re
from datetime import datetime, date
from pathlib import Path


def clean_text(text):
    """
    Remove tabs, collapse multiple spaces, strip whitespace.
    Handles the messy officer names in e-ticket exports.
    """
    if pd.isna(text):
        return ""
    text = str(text).replace('\t', ' ')  # Remove tabs
    text = re.sub(r'\s+', ' ', text)     # Collapse multiple spaces
    return text.strip()


def apply_hard_coded_overrides(merged_df, override_log_path='logs/summons_badge_overrides.txt'):
    """
    Apply hard-coded mapping overrides for known high-volume officers.
    
    This function serves as a safety net for:
    0. TITLE-based: If TITLE = "Parking Enforcement Officer" or "PEO" → TRAFFIC BUREAU
    1. PEO badges (2000-2099 range) that may not be in Assignment Master
    2. Other known Traffic Bureau personnel who process high volumes
    
    Parameters:
    -----------
    merged_df : pandas.DataFrame
        Merged summons data after initial join to Assignment Master
    override_log_path : str
        Path to log file for tracking overrides
    
    Returns:
    --------
    pandas.DataFrame
        Data with overrides applied
    int
        Count of records affected by overrides
    """
    print("\n[8.5/9] Applying hard-coded badge overrides...")
    
    override_count = 0
    override_log = []
    
    # Rule 0: TITLE-based override - Parking Enforcement Officer / PEO → TRAFFIC BUREAU
    # If TITLE from Assignment Master is PEO, assign to Traffic regardless of WG2
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
            override_log.append(f"\n=== TITLE OVERRIDE (PEO → TRAFFIC BUREAU) ===")
            override_log.append(f"TITLE = Parking Enforcement Officer or PEO → TRAFFIC BUREAU: {peo_title_count} records")
            print(f"  ✓ TITLE override: {peo_title_count} PEO records → TRAFFIC BUREAU")
            override_count += peo_title_count
    
    # Rule 1: PEO Badge Range Override (2000-2099 → TRAFFIC BUREAU)
    # These are Parking Enforcement Officers who should always map to Traffic
    peo_range_mask = (
        (merged_df['WG2'].isna() | (merged_df['WG2'] == 'UNKNOWN')) &
        (merged_df['PADDED_BADGE_NUMBER'].str.match(r'^20[0-9]{2}$', na=False))
    )
    
    peo_range_count = peo_range_mask.sum()
    if peo_range_count > 0:
        merged_df.loc[peo_range_mask, 'WG2'] = 'TRAFFIC BUREAU'
        merged_df.loc[peo_range_mask, 'TEAM'] = 'TRAFFIC'
        merged_df.loc[peo_range_mask, 'RANK'] = 'PEO'
        merged_df.loc[peo_range_mask, 'ASSIGNMENT_FOUND'] = True  # Mark as found via override
        
        affected_badges = merged_df[peo_range_mask]['PADDED_BADGE_NUMBER'].unique()
        override_log.append(f"\n=== PEO RANGE OVERRIDE (2000-2099) ===")
        override_log.append(f"Applied to {peo_range_count} records across {len(affected_badges)} badges")
        override_log.append(f"Badges: {', '.join(sorted(affected_badges))}")
        
        print(f"  ✓ PEO Range Override: {peo_range_count} records, {len(affected_badges)} unique badges")
        override_count += peo_range_count
    
    # Rule 2: Known Traffic Bureau Officers (specific badges)
    # Add specific overrides for sworn officers assigned to Traffic who might be missing
    known_traffic_badges = {
        '0256': 'GALLORINI G',  # P.O. G GALLORINI - should be TRAFFIC not PATROL
    }
    
    for badge, name in known_traffic_badges.items():
        specific_mask = (
            (merged_df['PADDED_BADGE_NUMBER'] == badge) &
            ((merged_df['WG2'].isna()) | (merged_df['WG2'] != 'TRAFFIC BUREAU'))
        )
        
        specific_count = specific_mask.sum()
        if specific_count > 0:
            old_wg2 = merged_df.loc[specific_mask, 'WG2'].iloc[0] if specific_count > 0 else 'UNKNOWN'
            merged_df.loc[specific_mask, 'WG2'] = 'TRAFFIC BUREAU'
            merged_df.loc[specific_mask, 'TEAM'] = 'TRAFFIC'
            
            override_log.append(f"\n=== SPECIFIC BADGE OVERRIDE ===")
            override_log.append(f"Badge {badge} ({name}): {specific_count} records")
            override_log.append(f"Changed from: {old_wg2} → TRAFFIC BUREAU")
            
            print(f"  ✓ Badge {badge} ({name}): {specific_count} records corrected")
            override_count += specific_count
    
    # Write override log
    if override_count > 0:
        log_path = Path(override_log_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"BADGE OVERRIDE LOG - {timestamp}\n")
            f.write(f"{'='*60}\n")
            f.write('\n'.join(override_log))
            f.write(f"\n\nTotal records affected: {override_count}\n")
        
        print(f"  ✓ Override log written to: {log_path}")
        print(f"  ⚠ REMINDER: Update Assignment_Master_V2.csv with these badges!")
    else:
        print("  ✓ No overrides needed (all badges found in Assignment Master)")
    
    return merged_df, override_count


def normalize_personnel_data(summons_path, master_path, output_path='summons_powerbi_latest.xlsx'):
    """
    Main ETL function: normalize summons data and join with Assignment Master.
    
    Parameters:
    -----------
    summons_path : str or Path
        Path to e-ticket export CSV (semicolon-delimited)
    master_path : str or Path
        Path to Assignment_Master_V2.csv
    output_path : str or Path
        Path for output Excel file (default: summons_powerbi_latest.xlsx)
    
    Returns:
    --------
    pandas.DataFrame
        Normalized and enriched summons data
    """
    
    print("=" * 60)
    print("SUMMONS DATA NORMALIZATION - ETL PIPELINE")
    print("=" * 60)
    
    # ========================================================================
    # STEP 1: LOAD DATA
    # ========================================================================
    print("\n[1/9] Loading source data...")
    
    # Load e-ticket export (skip bad lines due to formatting issues)
    summons_df = pd.read_csv(
        summons_path, 
        sep=';', 
        on_bad_lines='skip', 
        engine='python',
        encoding='utf-8'
    )
    print(f"  ✓ Loaded {len(summons_df):,} summons records")
    
    # Load Assignment Master
    master_df = pd.read_csv(master_path)
    print(f"  ✓ Loaded {len(master_df):,} personnel records")
    
    # ========================================================================
    # STEP 2: CLEAN OFFICER NAMES
    # ========================================================================
    print("\n[2/9] Cleaning officer names (removing tabs/extra spaces)...")
    
    name_cols = ['Officer First Name', 'Officer Middle Initial', 'Officer Last Name']
    for col in name_cols:
        if col in summons_df.columns:
            summons_df[col] = summons_df[col].apply(clean_text)
    
    print("  ✓ Names cleaned")
    
    # ========================================================================
    # STEP 3: NORMALIZE BADGE NUMBERS (JOIN KEY)
    # ========================================================================
    print("\n[3/9] Normalizing badge numbers to 4-digit format...")
    
    # Summons: Convert Officer Id to zero-padded 4-digit string
    # Examples: 256 → "0256", 5 → "0005", 1234 → "1234"
    summons_df['PADDED_BADGE_NUMBER'] = (
        summons_df['Officer Id']
        .astype(str)
        .str.split('.').str[0]  # Remove decimal if present (e.g., "256.0" → "256")
        .str.zfill(4)            # Zero-pad to 4 digits
    )
    
    # Master: Standardize badge numbers (handle various formats)
    master_df['PADDED_BADGE_NUMBER'] = (
        pd.to_numeric(master_df['PADDED_BADGE_NUMBER'], errors='coerce')
        .fillna(0)
        .astype(int)
        .astype(str)
        .str.zfill(4)
    )
    
    print(f"  ✓ Badge numbers normalized")
    print(f"  ✓ Unique badges in summons: {summons_df['PADDED_BADGE_NUMBER'].nunique()}")
    
    # ========================================================================
    # STEP 4: CREATE DISPLAY NAMES
    # ========================================================================
    print("\n[4/9] Creating formatted officer names...")
    
    summons_df['OFFICER_DISPLAY_NAME'] = (
        summons_df['Officer First Name'] + " " + 
        summons_df['Officer Middle Initial'] + " " + 
        summons_df['Officer Last Name']
    ).str.replace(r'\s+', ' ', regex=True).str.strip()
    
    summons_df['OFFICER_NAME_RAW'] = summons_df['OFFICER_DISPLAY_NAME']
    
    print("  ✓ Display names created")
    
    # ========================================================================
    # STEP 5: PARSE DATES AND CREATE TIME DIMENSIONS
    # ========================================================================
    print("\n[5/9] Parsing dates and creating time dimensions...")
    
    if 'Issue Date' in summons_df.columns:
        # Handle ISO format: 2026-02-06T09:25:49 or 2026-02-06
        summons_df['ISSUE_DATE'] = pd.to_datetime(
            summons_df['Issue Date'], 
            errors='coerce'
        )
        
        # Extract time components
        summons_df['Year'] = summons_df['ISSUE_DATE'].dt.year
        summons_df['Month'] = summons_df['ISSUE_DATE'].dt.month
        
        # Create YearMonthKey for sorting (e.g., 202601, 202602)
        summons_df['YearMonthKey'] = (
            (summons_df['Year'] * 100 + summons_df['Month'])
            .fillna(0)
            .astype(int)
        )
        
        # Create Month_Year for display (MM-YY e.g. "01-26") to match backfill and visual column headers
        summons_df['Month_Year'] = summons_df['ISSUE_DATE'].dt.strftime('%m-%y')
        
        print(f"  ✓ Date range: {summons_df['ISSUE_DATE'].min()} to {summons_df['ISSUE_DATE'].max()}")
        print(f"  ✓ Unique months: {summons_df['YearMonthKey'].nunique()}")
    else:
        print("  ⚠ WARNING: 'Issue Date' column not found")
    
    # ========================================================================
    # STEP 6: ADD ETL METADATA
    # ========================================================================
    print("\n[6/9] Adding ETL metadata columns...")
    
    summons_df['TICKET_COUNT'] = 1  # Each row = 1 ticket (for aggregation)
    summons_df['IS_AGGREGATE'] = False  # Individual tickets (not historical summary)
    summons_df['ETL_VERSION'] = 'ETICKET_CURRENT'
    summons_df['PROCESSING_TIMESTAMP'] = datetime.now()
    summons_df['SOURCE_FILE'] = Path(summons_path).name
    
    print("  ✓ Metadata added")
    
    # ========================================================================
    # STEP 7: PREPARE ASSIGNMENT MASTER (ACTIVE ONLY)
    # ========================================================================
    print("\n[7/9] Filtering Assignment Master to ACTIVE personnel...")
    
    active_count = (master_df['STATUS'] == 'ACTIVE').sum()
    print(f"  ✓ Active personnel: {active_count:,} of {len(master_df):,}")
    
    master_subset = master_df[
        master_df['STATUS'] == 'ACTIVE'
    ][['PADDED_BADGE_NUMBER', 'WG1', 'WG2', 'WG3', 'WG4', 'WG5', 
       'TEAM', 'RANK', 'FULL_NAME', 'POSS_CONTRACT_TYPE', 'TITLE']].copy()
    
    master_subset['ASSIGNMENT_FOUND'] = True
    
    # ========================================================================
    # STEP 8: JOIN SUMMONS TO ASSIGNMENT MASTER
    # ========================================================================
    print("\n[8/9] Joining summons to Assignment Master on PADDED_BADGE_NUMBER...")
    
    merged_df = summons_df.merge(
        master_subset, 
        on='PADDED_BADGE_NUMBER', 
        how='left'
    )
    
    # Count matches
    matched = merged_df['ASSIGNMENT_FOUND'].fillna(False).sum()
    unmatched = len(merged_df) - matched
    
    print(f"  ✓ Matched: {matched:,} records ({matched/len(merged_df)*100:.1f}%)")
    print(f"  ✓ Unmatched: {unmatched:,} records ({unmatched/len(merged_df)*100:.1f}%)")
    
    # ========================================================================
    # STEP 8.5: APPLY HARD-CODED OVERRIDES (NEW)
    # ========================================================================
    merged_df, override_count = apply_hard_coded_overrides(merged_df)
    
    if override_count > 0:
        # Recalculate match statistics after overrides
        matched_after = merged_df['ASSIGNMENT_FOUND'].fillna(False).sum()
        print(f"  ✓ After overrides: {matched_after:,} matched ({matched_after/len(merged_df)*100:.1f}%)")
    
    # ========================================================================
    # STEP 9: POST-JOIN CLEANUP
    # ========================================================================
    print("\n[9/9] Applying bureau consolidation and cleanup rules...")
    
    # Fill missing WG2 with "UNKNOWN"
    merged_df['WG2'] = merged_df['WG2'].fillna('UNKNOWN')
    merged_df['ASSIGNMENT_FOUND'] = merged_df['ASSIGNMENT_FOUND'].fillna(False)
    
    # Bureau Consolidation Rules (per SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md)
    bureau_consolidation = {
        'OFFICE OF SPECIAL OPERATIONS': 'PATROL DIVISION',
        'PATROL BUREAU': 'PATROL DIVISION'
    }
    merged_df['WG2'] = merged_df['WG2'].replace(bureau_consolidation)
    
    print("  ✓ Bureau consolidation applied")
    
    # Rename columns to match Power BI schema
    column_mapping = {
        'Ticket Number': 'TICKET_NUMBER',
        'Statute': 'VIOLATION_NUMBER',
        'Violation Description': 'VIOLATION_DESCRIPTION',
        'Case Type Code': 'TYPE',  # "M" = Moving, "P" = Parking
        'Case Status Code': 'STATUS',
        'Offense Street Name': 'LOCATION',
        'Penalty': 'FINE_AMOUNT'
    }
    
    # Only rename columns that exist
    existing_renames = {k: v for k, v in column_mapping.items() if k in merged_df.columns}
    merged_df = merged_df.rename(columns=existing_renames)
    
    print("  ✓ Columns renamed to Power BI schema")
    
    # Derive VIOLATION_TYPE for Power BI (expected by summons_13month_trend and other queries)
    # TYPE = M/P/C; VIOLATION_TYPE = human-readable category
    if 'TYPE' in merged_df.columns:
        type_map = {'M': 'Moving', 'P': 'Parking', 'C': 'Court'}
        merged_df['VIOLATION_TYPE'] = merged_df['TYPE'].map(type_map).fillna(merged_df['TYPE'].astype(str)).replace('nan', '')
    else:
        merged_df['VIOLATION_TYPE'] = ''
    
    # WARNING_FLAG: expected by Power BI; not in current e-ticket export — add as empty
    if 'WARNING_FLAG' not in merged_df.columns:
        merged_df['WARNING_FLAG'] = ''
    
    # Data quality columns: expected by Power BI; scoring not yet implemented — add placeholders
    if 'DATA_QUALITY_SCORE' not in merged_df.columns:
        merged_df['DATA_QUALITY_SCORE'] = 0
    if 'DATA_QUALITY_TIER' not in merged_df.columns:
        merged_df['DATA_QUALITY_TIER'] = ''
    
    # Financial columns expected by Power BI; only FINE_AMOUNT (Penalty) in current export — add placeholders
    if 'TOTAL_PAID_AMOUNT' not in merged_df.columns:
        merged_df['TOTAL_PAID_AMOUNT'] = merged_df['FINE_AMOUNT'].fillna(0) if 'FINE_AMOUNT' in merged_df.columns else 0
    if 'COST_AMOUNT' not in merged_df.columns:
        merged_df['COST_AMOUNT'] = 0
    if 'MISC_AMOUNT' not in merged_df.columns:
        merged_df['MISC_AMOUNT'] = 0
    
    # ========================================================================
    # SUMMARY & OUTPUT
    # ========================================================================
    print("\n" + "=" * 60)
    print("BUREAU ASSIGNMENT SUMMARY")
    print("=" * 60)
    
    if 'TYPE' in merged_df.columns:
        summary = merged_df.groupby(['WG2', 'TYPE']).agg({
            'TICKET_COUNT': 'sum',
            'PADDED_BADGE_NUMBER': 'nunique'
        }).rename(columns={'PADDED_BADGE_NUMBER': 'Officer_Count'})
        print(summary)
    else:
        summary = merged_df.groupby('WG2').agg({
            'TICKET_COUNT': 'sum',
            'PADDED_BADGE_NUMBER': 'nunique'
        }).rename(columns={'PADDED_BADGE_NUMBER': 'Officer_Count'})
        print(summary)
    
    # Show unknown badges for investigation
    unknowns = merged_df[merged_df['WG2'] == 'UNKNOWN']['PADDED_BADGE_NUMBER'].unique()
    if len(unknowns) > 0:
        print(f"\n⚠ UNKNOWN BADGES (need investigation): {sorted(unknowns)}")
    
    # ========================================================================
    # EXPORT TO EXCEL
    # ========================================================================
    print("\n" + "=" * 60)
    print("EXPORTING TO EXCEL")
    print("=" * 60)
    
    merged_df.to_excel(output_path, sheet_name='Summons_Data', index=False)
    
    file_size = Path(output_path).stat().st_size / 1024 / 1024  # MB
    print(f"\n✓ SUCCESS! Output saved to: {output_path}")
    print(f"✓ File size: {file_size:.2f} MB")
    print(f"✓ Total records: {len(merged_df):,}")
    print(f"✓ Columns: {len(merged_df.columns)}")
    
    return merged_df


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == '__main__':
    # File paths (adjust as needed)
    SUMMONS_PATH = '2026_01_eticket_export.csv'
    MASTER_PATH = 'Assignment_Master_V2.csv'
    OUTPUT_PATH = 'summons_powerbi_latest.xlsx'
    
    # Run the ETL pipeline
    final_data = normalize_personnel_data(
        summons_path=SUMMONS_PATH,
        master_path=MASTER_PATH,
        output_path=OUTPUT_PATH
    )
    
    print("\n" + "=" * 60)
    print("ETL PIPELINE COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Open Power BI Desktop")
    print("2. Refresh the summons_13month_trend query")
    print("3. Verify visuals show correct data")
    print("4. Publish report")
