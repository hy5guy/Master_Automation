#!/usr/bin/env python3
"""
Response Time Fresh Calculator - ETL Script
Version: 3.0.0
Date: 2026-02-09

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
    - PowerBI_Date/_DropExports/YYYY_MM_Average_Response_Times__Values_are_in_mmss.csv

Logic:
    1. Load raw timereport data (yearly + monthly supplement)
    2. Apply filtering (How Reported, Category_Type, Specific Incidents)
    3. Calculate first response times per incident
    4. Deduplicate by ReportNumberNew
    5. Map to Response_Type (Emergency, Routine, Urgent)
    6. Aggregate by month and Response_Type
    7. Output in long format (one row per month-type combination)

Features:
    - Hybrid data loading (yearly baseline + monthly supplement)
    - Comprehensive filtering from JSON configuration
    - Deduplication to prevent multi-officer double-counting
    - Consistent calculations across all months
    - Handles missing/null values gracefully
"""

import pandas as pd
import numpy as np
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging

# =============================================================================
# CONFIGURATION
# =============================================================================

VERSION = "3.0.0"

# Base paths
BASE_DIR = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack")
MASTER_AUTO_DIR = BASE_DIR / "Master_Automation"
TIMEREPORT_BASE = BASE_DIR / "05_EXPORTS" / "_CAD" / "timereport"
POWERBI_DROP = BASE_DIR / "PowerBI_Date" / "_DropExports"
CONFIG_DIR = MASTER_AUTO_DIR / "config"

# Input files
YEARLY_TIMEREPORT_BASE = TIMEREPORT_BASE / "yearly"
MONTHLY_TIMEREPORT_BASE = TIMEREPORT_BASE / "monthly"
FILTER_CONFIG = CONFIG_DIR / "response_time_filters.json"
MAPPING_FILE = BASE_DIR / "02_ETL_Scripts" / "Response_Times" / "input" / "Response_Type_Mapping.xlsx"

# Date range configuration
START_YEAR = 2025
START_MONTH = 1
END_YEAR = 2026
END_MONTH = 1

# Response time window (minutes)
MIN_RESPONSE_TIME = 0
MAX_RESPONSE_TIME = 10

# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging():
    """Configure logging for the script."""
    log_dir = MASTER_AUTO_DIR / "logs"
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
    """Load Response_Type mapping from Excel file."""
    logger = logging.getLogger(__name__)
    logger.info(f"Loading mapping file from: {mapping_path}")
    
    df = pd.read_excel(mapping_path)
    logger.info(f"Loaded {len(df)} incident type mappings")
    
    # Create mapping dictionaries
    response_type_map = dict(zip(df['Incident_Type'], df['Response_Type']))
    category_type_map = dict(zip(df['Incident_Type'], df['Category_Type']))
    
    return response_type_map, category_type_map

def load_timereport_hybrid(yearly_base, monthly_base, start_year, start_month, end_year, end_month):
    """
    Load timereport data using hybrid strategy:
    1. Load full year file for baseline
    2. Supplement with monthly files for most recent data
    3. Deduplicate between sources
    """
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("HYBRID TIMEREPORT LOADING")
    logger.info("=" * 80)
    
    all_data = []
    
    # Load yearly files
    for year in range(start_year, end_year + 1):
        yearly_file = yearly_base / str(year) / f"{year}_full_timereport.xlsx"
        if yearly_file.exists():
            logger.info(f"Loading yearly file: {yearly_file}")
            try:
                df_year = pd.read_excel(yearly_file)
                logger.info(f"  Loaded {len(df_year):,} records from {year} yearly file")
                all_data.append(df_year)
            except Exception as e:
                logger.error(f"  Error loading {yearly_file}: {e}")
        else:
            logger.warning(f"  Yearly file not found: {yearly_file}")
    
    # Load monthly supplements
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
    
    # Combine all data
    if not all_data:
        logger.error("No timereport files loaded!")
        return pd.DataFrame()
    
    df_combined = pd.concat(all_data, ignore_index=True)
    logger.info(f"Combined dataset: {len(df_combined):,} records before deduplication")
    
    # Deduplicate by ReportNumberNew (keep first occurrence)
    initial_count = len(df_combined)
    df_combined = df_combined.drop_duplicates(subset=['ReportNumberNew'], keep='first')
    dedup_count = initial_count - len(df_combined)
    logger.info(f"Removed {dedup_count:,} duplicate records")
    logger.info(f"Final dataset: {len(df_combined):,} unique records")
    
    return df_combined

# =============================================================================
# DATA PROCESSING
# =============================================================================

def apply_filters(df, filters, response_type_map, category_type_map):
    """Apply filtering logic based on configuration."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("APPLYING FILTERS")
    logger.info("=" * 80)
    
    initial_count = len(df)
    logger.info(f"Starting records: {initial_count:,}")
    
    # Filter 1: How Reported
    how_reported_exclude = filters.get('how_reported', {}).get('exclude', [])
    if how_reported_exclude:
        df = df[~df['How_Reported'].isin(how_reported_exclude)]
        logger.info(f"After How Reported filter: {len(df):,} records ({initial_count - len(df):,} removed)")
    
    # Add Category_Type mapping
    df['Category_Type'] = df['Incident_Type'].map(category_type_map)
    
    # Filter 2: Category_Type exclusions (with inclusion overrides)
    category_exclude = filters.get('category_types', {}).get('exclude', [])
    inclusion_overrides = filters.get('inclusion_overrides', {}).get('include_despite_category_filter', [])
    
    if category_exclude:
        # Exclude categories EXCEPT for incidents in inclusion_overrides list
        df = df[
            (~df['Category_Type'].isin(category_exclude)) | 
            (df['Incident_Type'].isin(inclusion_overrides))
        ]
        logger.info(f"After Category_Type filter: {len(df):,} records")
    
    # Filter 3: Specific incident exclusions
    incident_exclude = filters.get('incidents', {}).get('exclude', [])
    if incident_exclude:
        df = df[~df['Incident_Type'].isin(incident_exclude)]
        logger.info(f"After Specific Incident filter: {len(df):,} records")
    
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
    
    # Calculate response time in minutes
    df['Response_Time_Minutes'] = pd.to_numeric(df['First_Response_Time_Minutes'], errors='coerce')
    
    # Filter valid response times (0-10 minutes)
    valid_mask = (
        (df['Response_Time_Minutes'].notna()) & 
        (df['Response_Time_Minutes'] >= MIN_RESPONSE_TIME) & 
        (df['Response_Time_Minutes'] <= MAX_RESPONSE_TIME)
    )
    
    df_filtered = df[valid_mask].copy()
    
    invalid_count = len(df) - len(df_filtered)
    logger.info(f"Valid response times: {len(df_filtered):,}")
    logger.info(f"Invalid/Out of range: {invalid_count:,}")
    
    return df_filtered

def map_response_types(df, response_type_map):
    """Map incident types to response types."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("MAPPING RESPONSE TYPES")
    logger.info("=" * 80)
    
    df['Response_Type'] = df['Incident_Type'].map(response_type_map)
    
    # Count unmapped incidents
    unmapped = df['Response_Type'].isna().sum()
    if unmapped > 0:
        logger.warning(f"Unmapped incidents: {unmapped:,}")
        unmapped_types = df[df['Response_Type'].isna()]['Incident_Type'].value_counts()
        logger.warning(f"Top unmapped types:\n{unmapped_types.head(10)}")
    
    # Remove unmapped incidents
    df = df[df['Response_Type'].notna()].copy()
    logger.info(f"Records with valid Response_Type: {len(df):,}")
    
    return df

def aggregate_by_month(df, start_year, start_month, end_year, end_month):
    """Aggregate response times by month and response type."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("AGGREGATING BY MONTH")
    logger.info("=" * 80)
    
    # Ensure date columns are datetime
    df['Event_Date'] = pd.to_datetime(df['cDate'], errors='coerce')
    
    # Add YearMonth column
    df['YearMonth'] = df['Event_Date'].dt.to_period('M')
    
    # Calculate average response time by month and response type
    monthly_avg = df.groupby(['YearMonth', 'Response_Type'])['Response_Time_Minutes'].mean().reset_index()
    monthly_avg.columns = ['YearMonth', 'Response_Type', 'Average_Response_Time']
    
    logger.info(f"Generated {len(monthly_avg)} month-type combinations")
    logger.info(f"\nSample aggregated data:")
    logger.info(monthly_avg.head(10).to_string())
    
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
    
    # Convert YearMonth period to string format MM-YY
    df_monthly['MM-YY'] = df_monthly['YearMonth'].dt.strftime('%m-%y')
    
    # Convert average response time to MM:SS format
    df_monthly['First Response_Time_MMSS'] = df_monthly['Average_Response_Time'].apply(convert_to_mmss_format)
    
    # Select and order columns
    output_df = df_monthly[['Response_Type', 'MM-YY', 'First Response_Time_MMSS']].copy()
    
    # Sort by YearMonth and Response_Type
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
    
    # Group by month
    df_output['YearMonth_Sort'] = pd.to_datetime(
        df_output['MM-YY'], 
        format='%m-%y'
    ).dt.to_period('M')
    
    files_created = []
    
    for year_month, group_df in df_output.groupby('YearMonth_Sort'):
        year = year_month.year
        month = year_month.month
        
        # Format filename
        filename = f"{year}_{month:02d}_Average_Response_Times__Values_are_in_mmss.csv"
        output_path = output_dir / filename
        
        # Save (drop the YearMonth_Sort column)
        group_df = group_df.drop('YearMonth_Sort', axis=1)
        group_df.to_csv(output_path, index=False)
        
        logger.info(f"Created: {filename} ({len(group_df)} rows)")
        files_created.append(output_path)
    
    logger.info(f"\nTotal files created: {len(files_created)}")
    return files_created

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main execution function."""
    logger = setup_logging()
    
    logger.info("=" * 80)
    logger.info(f"RESPONSE TIME FRESH CALCULATOR v{VERSION}")
    logger.info("=" * 80)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Date range: {START_YEAR}-{START_MONTH:02d} to {END_YEAR}-{END_MONTH:02d}")
    
    try:
        # Step 1: Load configuration
        filters = load_filter_config(FILTER_CONFIG)
        response_type_map, category_type_map = load_mapping_file(MAPPING_FILE)
        
        # Step 2: Load timereport data
        df_raw = load_timereport_hybrid(
            YEARLY_TIMEREPORT_BASE,
            MONTHLY_TIMEREPORT_BASE,
            START_YEAR,
            START_MONTH,
            END_YEAR,
            END_MONTH
        )
        
        if df_raw.empty:
            logger.error("No data loaded! Exiting.")
            return 1
        
        # Step 3: Apply filters
        df_filtered = apply_filters(df_raw, filters, response_type_map, category_type_map)
        
        # Step 4: Calculate response times
        df_valid = calculate_response_times(df_filtered)
        
        # Step 5: Map response types
        df_mapped = map_response_types(df_valid, response_type_map)
        
        # Step 6: Aggregate by month
        df_monthly = aggregate_by_month(df_mapped, START_YEAR, START_MONTH, END_YEAR, END_MONTH)
        
        # Step 7: Format output
        df_output = format_output(df_monthly)
        
        # Step 8: Save files
        files_created = save_monthly_files(df_output, POWERBI_DROP, START_YEAR, START_MONTH, END_YEAR, END_MONTH)
        
        # Summary
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
        logger.info(f"Output directory: {POWERBI_DROP}")
        logger.info(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        logger.info("✅ SUCCESS - Response Time calculation complete!")
        logger.info("=" * 80)
        
        return 0
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ ERROR: {str(e)}")
        logger.error("=" * 80)
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
