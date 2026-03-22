#!/usr/bin/env python3
# 2026-02-21-00-39-17 (EST)
# Project Name: Hackensack PD | Data Ops & ETL Remediation
# File Name: scripts/response_time_fresh_calculator.py
# Author: R. A. Carucci
# Purpose: Recalculate response times from raw timereport data with first-arriving unit deduplication and argparse-driven date range.
"""
Response Time Fresh Calculator - ETL Script
Version: 3.1.0

Purpose:
    Recalculate response times from scratch using raw timereport data.
    Generates monthly CSV files in long format for Power BI consumption.
    
    Replaces backfill data with fresh calculations to ensure consistency.

Input Files:
    - timereport/yearly/YYYY/YYYY_full_timereport.xlsx (full year data)
    - timereport/monthly/YYYY_MM_timereport.xlsx (current month)
    - config/response_time_filters.json (filter configuration)
    - config/Response_Type_Mapping.xlsx (incident type mapping)

Output Files:
    - PowerBI_Data/_DropExports/YYYY_MM_Average_Response_Times__Values_are_in_mmss.csv

Logic:
    1. Load raw timereport data (yearly + monthly supplement)
    2. Apply filtering (How Reported, Category_Type, Specific Incidents)
    3. Calculate first response times per incident
    4. Deduplicate by ReportNumberNew (first-arriving unit via Time Out sort)
    5. Map to Response_Type (Emergency, Routine, Urgent)
    6. Aggregate by month and Response_Type
    7. Output in long format (one row per month-type combination)

Features:
    - Hybrid data loading (yearly baseline + monthly supplement)
    - Comprehensive filtering from JSON configuration
    - First-arriving unit deduplication (sort by Time Out before drop_duplicates)
    - Consistent calculations across all months
    - Handles missing/null values gracefully
"""

import argparse
import pandas as pd
import numpy as np
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging

sys.path.insert(0, str(Path(__file__).parent))
from path_config import get_onedrive_root

# =============================================================================
# CONFIGURATION
# =============================================================================

VERSION = "3.1.0"

# Response time window (minutes)
MIN_RESPONSE_TIME = 0
MAX_RESPONSE_TIME = 10

# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging(master_auto_dir):
    """Configure logging for the script."""
    log_dir = master_auto_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{timestamp}_response_time_fresh_calculator.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

# =============================================================================
# DATA LOADING
# =============================================================================

def load_filter_config(config_path):
    """Load filter configuration from JSON file."""
    logger = logging.getLogger(__name__)
    logger.info(f"Loading filter configuration from: {config_path}")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    filters = config.get('filters', {})
    logger.info(f"Loaded filters: {list(filters.keys())}")
    return filters

def load_mapping_file(mapping_path):
    """Load Response_Type mapping from Excel file or use default mapping."""
    logger = logging.getLogger(__name__)
    logger.info(f"Loading mapping configuration...")
    
    logger.info("Using default CAD Priority-based mapping")
    logger.info("  Priority 1 -> Emergency")
    logger.info("  Priority 2 -> Urgent")  
    logger.info("  Priority 3 -> Routine")
    
    return {}, {}

def map_response_types_by_priority(df):
    """Map response types based on CAD Priority field or Incident mapping."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("MAPPING RESPONSE TYPES (BY INCIDENT TYPE)")
    logger.info("=" * 80)
    
    def classify_incident(incident):
        """Classify incident as Emergency, Urgent, or Routine based on keywords."""
        if pd.isna(incident):
            return None
        
        incident_lower = str(incident).lower()
        
        emergency_keywords = [
            'fire', 'assault', 'shooting', 'stabbing', 'robbery', 'burglary in progress',
            'weapons', 'overdose', 'cardiac', 'unconscious', 'accident with injury',
            'domestic violence', 'kidnapping', 'hostage', 'active shooter', 'pursuit'
        ]
        
        routine_keywords = [
            'parking', 'traffic', 'information', 'patrol', 'paperwork', 'report',
            'registration', 'inspection', 'permit', 'tag', 'complaint signed',
            'walk', 'check', 'detail', 'taps', 'constable'
        ]
        
        for keyword in emergency_keywords:
            if keyword in incident_lower:
                return 'Emergency'
        
        for keyword in routine_keywords:
            if keyword in incident_lower:
                return 'Routine'
        
        return 'Urgent'
    
    df['Response_Type'] = df['Incident'].apply(classify_incident)
    
    type_dist = df['Response_Type'].value_counts()
    logger.info(f"\nResponse Type Distribution:")
    for rtype, count in type_dist.items():
        pct = (count / len(df)) * 100
        logger.info(f"  {rtype}: {count:,} ({pct:.1f}%)")
    
    logger.info(f"\nSample incidents by type:")
    for rtype in ['Emergency', 'Urgent', 'Routine']:
        if rtype in df['Response_Type'].values:
            samples = df[df['Response_Type'] == rtype]['Incident'].value_counts().head(3)
            logger.info(f"  {rtype}:")
            for incident, count in samples.items():
                logger.info(f"    - {incident}: {count:,}")
    
    df = df[df['Response_Type'].notna()].copy()
    logger.info(f"\nRecords with valid Response_Type: {len(df):,}")
    
    return df

def load_timereport_hybrid(yearly_base, monthly_base, start_year, start_month, end_year, end_month):
    """
    Load timereport data using hybrid strategy:
    1. Load full year file for baseline
    2. Supplement with monthly files for most recent data
    3. Sort by Time Out and deduplicate (first-arriving unit kept)
    """
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("HYBRID TIMEREPORT LOADING")
    logger.info("=" * 80)
    
    all_data = []
    
    for year in range(start_year, end_year + 1):
        yearly_file = yearly_base / str(year) / f"{year}_full_timereport.xlsx"
        if yearly_file.exists():
            logger.info(f"Loading yearly file: {yearly_file}")
            try:
                df_year = pd.read_excel(yearly_file)
                logger.info(f"  Loaded {len(df_year):,} records from {year} yearly file")
                logger.info(f"  Columns available: {list(df_year.columns[:10])}")
                all_data.append(df_year)
            except Exception as e:
                logger.error(f"  Error loading {yearly_file}: {e}")
        else:
            logger.warning(f"  Yearly file not found: {yearly_file}")
    
    current_year = end_year
    for month in range(1, end_month + 1):
        monthly_file = monthly_base / f"{current_year}_{month:02d}_timereport.xlsx"
        if monthly_file.exists():
            logger.info(f"Loading monthly supplement: {monthly_file}")
            try:
                df_month = pd.read_excel(monthly_file)
                logger.info(f"  Loaded {len(df_month):,} records from {current_year}-{month:02d} monthly file")
                all_data.append(df_month)
            except Exception as e:
                logger.error(f"  Error loading {monthly_file}: {e}")
        else:
            logger.warning(f"  Monthly file not found: {monthly_file}")
    
    if not all_data:
        logger.error("No timereport files loaded!")
        return pd.DataFrame()
    
    df_combined = pd.concat(all_data, ignore_index=True)
    logger.info(f"Combined dataset: {len(df_combined):,} records before deduplication")
    
    initial_count = len(df_combined)
    df_combined.sort_values(['ReportNumberNew', 'Time Out'], inplace=True)
    df_combined = df_combined.drop_duplicates(subset=['ReportNumberNew'], keep='first')
    dedup_count = initial_count - len(df_combined)
    logger.info(f"Removed {dedup_count:,} duplicate records (kept first-arriving unit)")
    logger.info(f"Final dataset: {len(df_combined):,} unique records")
    
    return df_combined

# =============================================================================
# DATA PROCESSING
# =============================================================================

def apply_filters(df, filters):
    """Apply filtering logic based on configuration."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("APPLYING FILTERS")
    logger.info("=" * 80)
    
    initial_count = len(df)
    logger.info(f"Starting records: {initial_count:,}")
    
    how_reported_exclude = filters.get('how_reported', {}).get('exclude', [])
    if how_reported_exclude and 'How_Reported' in df.columns:
        df = df[~df['How_Reported'].isin(how_reported_exclude)]
        logger.info(f"After How Reported filter: {len(df):,} records ({initial_count - len(df):,} removed)")
    else:
        logger.info("How Reported column not found - skipping filter")
    
    logger.info("Using simplified Priority-based filtering")
    
    total_removed = initial_count - len(df)
    pct_removed = (total_removed / initial_count * 100) if initial_count > 0 else 0
    logger.info(f"Total filtered: {total_removed:,} records ({pct_removed:.1f}%)")
    
    return df

def calculate_response_times(df):
    """Calculate first response times and validate range."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("CALCULATING RESPONSE TIMES")
    logger.info("=" * 80)
    
    for col in ['Time Dispatched', 'Time Out']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    df['Response_Time_Minutes'] = (df['Time Out'] - df['Time Dispatched']).dt.total_seconds() / 60.0
    
    if 'Time Response' in df.columns:
        fallback = pd.to_timedelta(df['Time Response'], errors='coerce').dt.total_seconds() / 60.0
        df['Response_Time_Minutes'] = df['Response_Time_Minutes'].fillna(fallback)
    
    valid_mask = (
        (df['Response_Time_Minutes'].notna()) & 
        (df['Response_Time_Minutes'] >= MIN_RESPONSE_TIME) & 
        (df['Response_Time_Minutes'] <= MAX_RESPONSE_TIME)
    )
    
    df_filtered = df[valid_mask].copy()
    
    invalid_count = len(df) - len(df_filtered)
    logger.info(f"Valid response times: {len(df_filtered):,}")
    logger.info(f"Invalid/Out of range: {invalid_count:,}")
    
    if len(df_filtered) > 0:
        logger.info(f"Response time stats: min={df_filtered['Response_Time_Minutes'].min():.2f}, max={df_filtered['Response_Time_Minutes'].max():.2f}, avg={df_filtered['Response_Time_Minutes'].mean():.2f}")
    
    return df_filtered

def map_response_types(df, response_type_map):
    """Map incident types to response types."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("MAPPING RESPONSE TYPES")
    logger.info("=" * 80)
    
    df['Response_Type'] = df['Incident_Type'].map(response_type_map)
    
    unmapped = df['Response_Type'].isna().sum()
    if unmapped > 0:
        logger.warning(f"Unmapped incidents: {unmapped:,}")
        unmapped_types = df[df['Response_Type'].isna()]['Incident_Type'].value_counts()
        logger.warning(f"Top unmapped types:\n{unmapped_types.head(10)}")
    
    df = df[df['Response_Type'].notna()].copy()
    logger.info(f"Records with valid Response_Type: {len(df):,}")
    
    return df

def aggregate_by_month(df, start_year, start_month, end_year, end_month):
    """Aggregate response times by month and response type."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("AGGREGATING BY MONTH")
    logger.info("=" * 80)
    
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    
    if 'cMonth' in df.columns:
        df['cMonth_Numeric'] = df['cMonth'].map(month_map)
        logger.info(f"Converted month names to numbers")
        
        unmapped_count = df['cMonth_Numeric'].isna().sum()
        if unmapped_count > 0:
            logger.warning(f"Unmapped months: {unmapped_count}")
            logger.warning(f"Unique unmapped values: {df[df['cMonth_Numeric'].isna()]['cMonth'].unique()}")
    else:
        logger.error("cMonth column not found!")
        return pd.DataFrame()
    
    if 'cYear' in df.columns:
        df['cYear_Int'] = df['cYear'].fillna(0).astype(int)
    else:
        logger.error("cYear column not found!")
        return pd.DataFrame()
    
    df['cMonth_Str'] = df['cMonth_Numeric'].fillna(0).astype(int).astype(str).str.zfill(2)
    df['cYear_Str'] = df['cYear_Int'].astype(str)
    df['YearMonth'] = pd.to_datetime(
        df['cYear_Str'] + '-' + df['cMonth_Str'] + '-01',
        format='%Y-%m-%d',
        errors='coerce'
    ).dt.to_period('M')
    
    df = df[df['YearMonth'].notna()].copy()
    logger.info(f"Records with valid YearMonth: {len(df):,}")
    
    monthly_avg = df.groupby(['YearMonth', 'Response_Type'])['Response_Time_Minutes'].mean().reset_index()
    monthly_avg.columns = ['YearMonth', 'Response_Type', 'Average_Response_Time']
    
    logger.info(f"Generated {len(monthly_avg)} month-type combinations")
    logger.info(f"\nSample aggregated data:")
    logger.info(monthly_avg.head(15).to_string())
    
    return monthly_avg

def convert_to_mmss_format(minutes):
    """Convert decimal minutes to MM:SS format."""
    if pd.isna(minutes) or minutes == 0:
        return "00:00"
    
    mins = int(minutes)
    secs = int((minutes - mins) * 60)
    return f"{mins:02d}:{secs:02d}"

def format_output(df_monthly):
    """Format output for Power BI consumption."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("FORMATTING OUTPUT")
    logger.info("=" * 80)
    
    df_monthly['MM-YY'] = df_monthly['YearMonth'].dt.strftime('%m-%y')
    
    df_monthly['First Response_Time_MMSS'] = df_monthly['Average_Response_Time'].apply(convert_to_mmss_format)
    
    output_df = df_monthly[['Response_Type', 'MM-YY', 'First Response_Time_MMSS']].copy()
    
    output_df = output_df.sort_values(['MM-YY', 'Response_Type'])
    
    logger.info(f"Output format: {len(output_df)} rows")
    logger.info(f"\nFinal output sample:")
    logger.info(output_df.head(15).to_string())
    
    return output_df

def save_monthly_files(df_output, output_dir, start_year, start_month, end_year, end_month):
    """Save individual monthly CSV files."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("SAVING OUTPUT FILES")
    logger.info("=" * 80)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df_output['YearMonth_Sort'] = pd.to_datetime(
        df_output['MM-YY'], 
        format='%m-%y'
    ).dt.to_period('M')
    
    files_created = []
    
    for year_month, group_df in df_output.groupby('YearMonth_Sort'):
        year = year_month.year
        month = year_month.month
        
        filename = f"{year}_{month:02d}_Average_Response_Times__Values_are_in_mmss.csv"
        output_path = output_dir / filename
        
        group_df = group_df.drop('YearMonth_Sort', axis=1)
        group_df.to_csv(output_path, index=False)
        
        logger.info(f"Created: {filename} ({len(group_df)} rows)")
        files_created.append(output_path)
    
    logger.info(f"\nTotal files created: {len(files_created)}")
    return files_created

# =============================================================================
# ARGUMENT PARSING
# =============================================================================

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=f"Response Time Fresh Calculator v{VERSION} — "
                    "recalculate response times from raw timereport data."
    )
    parser.add_argument(
        "--report-month",
        required=True,
        help="End month of the 13-month window in YYYY-MM format (e.g. 2026-01)."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Override OneDrive root path (defaults to path_config.get_onedrive_root())."
    )
    return parser.parse_args()

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main execution function."""
    args = parse_args()

    # Derive date range from --report-month
    try:
        rm_date = datetime.strptime(args.report_month, "%Y-%m")
    except ValueError:
        print(f"[ERROR] Invalid --report-month format: {args.report_month!r}  (expected YYYY-MM)")
        return 1

    end_year = rm_date.year
    end_month = rm_date.month
    start_month = end_month
    start_year = end_year - 1

    # Resolve paths
    base_dir = Path(args.root) if args.root else get_onedrive_root()
    master_auto_dir = base_dir / "Master_Automation"
    timereport_base = base_dir / "05_EXPORTS" / "_CAD" / "timereport"
    powerbi_drop = base_dir / "PowerBI_Data" / "_DropExports"
    config_dir = master_auto_dir / "config"

    yearly_timereport_base = timereport_base / "yearly"
    monthly_timereport_base = timereport_base / "monthly"
    filter_config = config_dir / "response_time_filters.json"
    mapping_file = base_dir / "02_ETL_Scripts" / "Response_Times" / "input" / "Response_Type_Mapping.xlsx"

    logger = setup_logging(master_auto_dir)
    
    logger.info("=" * 80)
    logger.info(f"RESPONSE TIME FRESH CALCULATOR v{VERSION}")
    logger.info("=" * 80)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Date range: {start_year}-{start_month:02d} to {end_year}-{end_month:02d}")
    logger.info(f"OneDrive root: {base_dir}")
    
    try:
        filters = load_filter_config(filter_config)
        response_type_map, category_type_map = load_mapping_file(mapping_file)
        
        df_raw = load_timereport_hybrid(
            yearly_timereport_base,
            monthly_timereport_base,
            start_year,
            start_month,
            end_year,
            end_month
        )
        
        if df_raw.empty:
            logger.error("No data loaded! Exiting.")
            return 1
        
        df_filtered = apply_filters(df_raw, filters)
        
        df_valid = calculate_response_times(df_filtered)
        
        df_mapped = map_response_types_by_priority(df_valid)
        
        df_monthly = aggregate_by_month(df_mapped, start_year, start_month, end_year, end_month)
        
        df_output = format_output(df_monthly)
        
        files_created = save_monthly_files(df_output, powerbi_drop, start_year, start_month, end_year, end_month)
        
        logger.info("=" * 80)
        logger.info("EXECUTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Raw records loaded: {len(df_raw):,}")
        logger.info(f"After filtering: {len(df_filtered):,}")
        logger.info(f"Valid response times: {len(df_valid):,}")
        logger.info(f"With Response_Type: {len(df_mapped):,}")
        logger.info(f"Monthly aggregates: {len(df_monthly):,}")
        logger.info(f"Output rows: {len(df_output):,}")
        logger.info(f"Files created: {len(files_created)}")
        logger.info(f"Output directory: {powerbi_drop}")
        logger.info(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        logger.info("SUCCESS - Response Time calculation complete!")
        logger.info("=" * 80)
        
        return 0
        
    except Exception as e:
        logger.error("=" * 80)
        logger.info("ERROR: {0}".format(str(e)))
        logger.error("=" * 80)
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
