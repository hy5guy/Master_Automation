"""
Benchmark Data Architecture Overhaul Script
Date: 2026-01-12
Purpose: Restructure Benchmark use-of-force tracking system
Author: Claude Code (with R. A. Carucci)
"""

import pandas as pd
import json
import shutil
import os
from datetime import datetime, date
from pathlib import Path
import csv

# Configuration
ROOT_BENCHMARK = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Benchmark")
ROOT_AUTOMATION = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation")
BACKUP_DIR = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Benchmark_BACKUP_20260112")
TODAY = date(2026, 1, 12)

# Source files
SOURCE_FILES = {
    "show_force": ROOT_BENCHMARK / "show_force" / "complete_report" / "all_time" / "show-of-force-reports-01_01_2001-01_07_2026.csv",
    "use_force": ROOT_BENCHMARK / "use_force" / "complete_report" / "all_time" / "use-of-force-reports-01_01_2001-01_07_2026.csv",
    "vehicle_pursuit": ROOT_BENCHMARK / "vehicle_pursuit" / "complete_report" / "all_time" / "vehicle-pursuit-reports-01_01_2001-01_07_2026.csv"
}

def log(message):
    """Print timestamped log message"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def create_backup():
    """Create complete backup of _Benchmark folder"""
    log("=" * 80)
    log("PHASE 1: CREATING BACKUP")
    log("=" * 80)

    if BACKUP_DIR.exists():
        log(f"Backup directory already exists: {BACKUP_DIR}")
        log("Skipping backup creation")
        return True

    try:
        log(f"Creating backup: {BACKUP_DIR}")
        shutil.copytree(ROOT_BENCHMARK, BACKUP_DIR)

        # Count files
        backup_files = list(BACKUP_DIR.rglob("*"))
        backup_file_count = len([f for f in backup_files if f.is_file()])

        log(f"[OK] Backup created successfully")
        log(f"[OK] Total files backed up: {backup_file_count}")
        return True
    except Exception as e:
        log(f"[ERROR] Backup failed: {e}")
        return False

def validate_source_data():
    """Validate source CSV files and return metadata"""
    log("=" * 80)
    log("PHASE 1: VALIDATING SOURCE DATA")
    log("=" * 80)

    validation_results = {}

    for event_type, file_path in SOURCE_FILES.items():
        log(f"\nValidating {event_type}...")

        try:
            # Read file
            df = pd.read_csv(file_path, encoding='utf-8')

            # Get metadata
            record_count = len(df)
            columns = list(df.columns)

            # Parse dates
            df['Incident Date'] = pd.to_datetime(df['Incident Date'], errors='coerce')
            date_min = df['Incident Date'].min()
            date_max = df['Incident Date'].max()

            # Store results
            validation_results[event_type] = {
                "file_path": str(file_path),
                "record_count": record_count,
                "columns": columns,
                "date_range": {
                    "start": date_min.strftime('%Y-%m-%d') if pd.notna(date_min) else None,
                    "end": date_max.strftime('%Y-%m-%d') if pd.notna(date_max) else None
                }
            }

            log(f"  [OK] Records: {record_count}")
            log(f"  [OK] Columns: {len(columns)}")
            log(f"  [OK] Date range: {date_min.strftime('%Y-%m-%d')} to {date_max.strftime('%Y-%m-%d')}")

        except Exception as e:
            log(f"  [ERROR] Error: {e}")
            validation_results[event_type] = {"error": str(e)}

    return validation_results

def create_master_combined_dataset():
    """Create master combined dataset with all event types"""
    log("=" * 80)
    log("PHASE 2: CREATING MASTER COMBINED DATASET")
    log("=" * 80)

    all_data = []

    # Common columns across all event types
    common_columns = [
        "Officer Name", "Badge Number", "Rank", "Organization",
        "Incident Number", "Report Number", "Incident Date",
        "Subject type", "Report Key"
    ]

    # Event-specific additional columns
    event_configs = {
        "Show of Force": {"file": SOURCE_FILES["show_force"], "abbrev": "show_force"},
        "Use of Force": {"file": SOURCE_FILES["use_force"], "abbrev": "use_force"},
        "Vehicle Pursuit": {"file": SOURCE_FILES["vehicle_pursuit"], "abbrev": "vehicle_pursuit"}
    }

    for event_type, config in event_configs.items():
        log(f"\nProcessing {event_type}...")

        try:
            # Read CSV
            df = pd.read_csv(config["file"], encoding='utf-8')

            # Add EventType column
            df['EventType'] = event_type

            # Parse and standardize dates
            df['Incident Date'] = pd.to_datetime(df['Incident Date'], errors='coerce')

            # Select columns (keep all columns, pad missing ones with None)
            all_cols = set(df.columns.tolist())

            log(f"  [OK] Loaded {len(df)} records")
            all_data.append(df)

        except Exception as e:
            log(f"  [ERROR] Error processing {event_type}: {e}")

    # Combine all dataframes
    log("\nCombining all datasets...")
    combined_df = pd.concat(all_data, ignore_index=True, sort=False)

    # Sort by Incident Date
    combined_df = combined_df.sort_values('Incident Date')

    # Create output directory
    output_dir = ROOT_BENCHMARK / "all_events_combined"
    output_dir.mkdir(exist_ok=True)

    # Save combined dataset
    output_file = output_dir / "master_combined_all_time.csv"
    combined_df.to_csv(output_file, index=False, encoding='utf-8')

    log(f"[OK] Master combined dataset created: {output_file}")
    log(f"[OK] Total records: {len(combined_df)}")

    # Create metadata
    metadata = {
        "total_records": len(combined_df),
        "date_range": {
            "start": combined_df['Incident Date'].min().strftime('%Y-%m-%d'),
            "end": combined_df['Incident Date'].max().strftime('%Y-%m-%d')
        },
        "by_event_type": {},
        "last_updated": datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    }

    for event_type in event_configs.keys():
        count = len(combined_df[combined_df['EventType'] == event_type])
        metadata["by_event_type"][event_type] = count
        log(f"  - {event_type}: {count} records")

    # Save metadata
    metadata_file = output_dir / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    log(f"[OK] Metadata saved: {metadata_file}")

    return combined_df, metadata

def generate_rolling_13month_datasets(combined_df):
    """Generate rolling 13-month datasets"""
    log("=" * 80)
    log("PHASE 2: GENERATING ROLLING 13-MONTH DATASETS")
    log("=" * 80)

    # Calculate rolling window (today = 2026-01-12)
    # Last complete month is December 2025
    # 13-month window: Dec 2024 - Dec 2025
    end_date = date(2025, 12, 31)
    start_date = date(2024, 12, 1)

    log(f"Rolling 13-month window: {start_date} to {end_date}")

    # Filter data
    combined_df['Incident Date'] = pd.to_datetime(combined_df['Incident Date'])
    rolling_df = combined_df[
        (combined_df['Incident Date'] >= pd.Timestamp(start_date)) &
        (combined_df['Incident Date'] <= pd.Timestamp(end_date))
    ].copy()

    log(f"[OK] Filtered to {len(rolling_df)} records in rolling window")

    # Create output directories
    rolling_dir = ROOT_BENCHMARK / "by_time_period" / "rolling_13month"
    rolling_dir.mkdir(parents=True, exist_ok=True)

    by_event_dir = rolling_dir / "by_event_type"
    by_event_dir.mkdir(exist_ok=True)

    # Save combined rolling dataset
    current_window_file = rolling_dir / "current_window.csv"
    rolling_df.to_csv(current_window_file, index=False, encoding='utf-8')
    log(f"[OK] Combined rolling 13-month dataset: {current_window_file}")

    # Save by event type
    for event_type in rolling_df['EventType'].unique():
        event_df = rolling_df[rolling_df['EventType'] == event_type]
        filename = event_type.lower().replace(' ', '_') + '_13month.csv'
        output_file = by_event_dir / filename
        event_df.to_csv(output_file, index=False, encoding='utf-8')
        log(f"  [OK] {event_type}: {len(event_df)} records -> {filename}")

    # Save last_updated timestamp
    timestamp_file = rolling_dir / "last_updated.txt"
    with open(timestamp_file, 'w') as f:
        f.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Window: {start_date} to {end_date}\n")
        f.write(f"Total Records: {len(rolling_df)}\n")

    log(f"[OK] Timestamp saved: {timestamp_file}")

    return rolling_df

def generate_ytd_2026_datasets(combined_df):
    """Generate YTD 2026 datasets"""
    log("=" * 80)
    log("PHASE 2: GENERATING YTD 2026 DATASETS")
    log("=" * 80)

    # YTD 2026: Jan 1 - Jan 7, 2026
    start_date = date(2026, 1, 1)
    end_date = date(2026, 1, 7)

    log(f"YTD 2026 window: {start_date} to {end_date}")

    # Filter data
    combined_df['Incident Date'] = pd.to_datetime(combined_df['Incident Date'])
    ytd_df = combined_df[
        (combined_df['Incident Date'] >= pd.Timestamp(start_date)) &
        (combined_df['Incident Date'] <= pd.Timestamp(end_date))
    ].copy()

    log(f"[OK] Filtered to {len(ytd_df)} records in YTD 2026 window")

    # Create output directories
    ytd_dir = ROOT_BENCHMARK / "by_time_period" / "ytd_current"
    ytd_dir.mkdir(parents=True, exist_ok=True)

    by_event_dir = ytd_dir / "by_event_type"
    by_event_dir.mkdir(exist_ok=True)

    # Save combined YTD dataset
    ytd_file = ytd_dir / "2026_ytd.csv"
    ytd_df.to_csv(ytd_file, index=False, encoding='utf-8')
    log(f"[OK] Combined YTD 2026 dataset: {ytd_file}")

    # Save by event type
    if len(ytd_df) > 0:
        for event_type in ytd_df['EventType'].unique():
            event_df = ytd_df[ytd_df['EventType'] == event_type]
            filename = event_type.lower().replace(' ', '_') + '_2026_ytd.csv'
            output_file = by_event_dir / filename
            event_df.to_csv(output_file, index=False, encoding='utf-8')
            log(f"  [OK] {event_type}: {len(event_df)} records -> {filename}")
    else:
        log("  Note: No records in YTD 2026 window")

    return ytd_df

def archive_historical_years(combined_df):
    """Archive historical complete years (2024, 2025)"""
    log("=" * 80)
    log("PHASE 2: ARCHIVING HISTORICAL COMPLETE YEARS")
    log("=" * 80)

    years_to_archive = [2024, 2025]

    for year in years_to_archive:
        log(f"\nArchiving {year}...")

        # Filter data for the year
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        combined_df['Incident Date'] = pd.to_datetime(combined_df['Incident Date'])
        year_df = combined_df[
            (combined_df['Incident Date'] >= pd.Timestamp(start_date)) &
            (combined_df['Incident Date'] <= pd.Timestamp(end_date))
        ].copy()

        log(f"  [OK] Filtered to {len(year_df)} records for {year}")

        # Archive by event type
        for event_type in ["Show of Force", "Use of Force", "Vehicle Pursuit"]:
            event_df = year_df[year_df['EventType'] == event_type]

            if len(event_df) == 0:
                log(f"    - {event_type}: No records")
                continue

            # Create directory
            event_slug = event_type.lower().replace(' ', '_')
            archive_dir = ROOT_BENCHMARK / "by_event_type" / event_slug / "archives"
            archive_dir.mkdir(parents=True, exist_ok=True)

            # Save file
            archive_file = archive_dir / f"{year}_complete.csv"
            event_df.to_csv(archive_file, index=False, encoding='utf-8')
            log(f"    [OK] {event_type}: {len(event_df)} records -> {archive_file.name}")

def generate_use_of_force_matrix(rolling_df):
    """Generate Use of Force Incident Matrix"""
    log("=" * 80)
    log("PHASE 3: GENERATING USE OF FORCE MATRIX")
    log("=" * 80)

    # Filter to rolling 13-month window
    rolling_df['Incident Date'] = pd.to_datetime(rolling_df['Incident Date'])

    # Add MonthLabel column (MM-YY format)
    rolling_df['MonthLabel'] = rolling_df['Incident Date'].dt.strftime('%m-%y')

    # Group by EventType and MonthLabel
    matrix_df = rolling_df.groupby(['EventType', 'MonthLabel']).size().reset_index(name='IncidentCount')

    # Sort by date
    matrix_df['SortKey'] = pd.to_datetime('20' + matrix_df['MonthLabel'].str[-2:] + '-' + matrix_df['MonthLabel'].str[:2] + '-01')
    matrix_df = matrix_df.sort_values(['EventType', 'SortKey'])
    matrix_df = matrix_df.drop('SortKey', axis=1)

    # Save matrix
    output_file = ROOT_AUTOMATION / "Use of Force Incident Matrix_UPDATED.csv"
    matrix_df.to_csv(output_file, index=False, encoding='utf-8')

    log(f"[OK] Matrix saved: {output_file}")
    log(f"[OK] Total records: {len(matrix_df)}")

    # Validate totals
    totals = rolling_df.groupby('EventType').size()
    log("\nValidation - Total incidents by event type:")
    total_all = 0
    for event_type, count in totals.items():
        log(f"  - {event_type}: {count}")
        total_all += count
    log(f"  - TOTAL: {total_all}")

    expected_total = 71
    if total_all == expected_total:
        log(f"[OK] Totals match expected: {expected_total}")
    else:
        log(f"[WARNING] Warning: Expected {expected_total}, got {total_all}")

    return matrix_df

def generate_supporting_visualizations(rolling_df):
    """Generate supporting visualization data files"""
    log("=" * 80)
    log("PHASE 3: GENERATING SUPPORTING VISUALIZATIONS")
    log("=" * 80)

    # 1. Incident Distribution by Event Type
    log("\nGenerating Incident Distribution by Event Type...")
    dist_df = rolling_df.groupby('EventType').size().reset_index(name='IncidentCount_13Month')
    dist_file = ROOT_AUTOMATION / "Incident Distribution by Event Type_UPDATED.csv"
    dist_df.to_csv(dist_file, index=False, encoding='utf-8')
    log(f"[OK] {dist_file.name}")

    # 2. Incident Count by Date and Event Type
    log("\nGenerating Incident Count by Date and Event Type...")
    rolling_df['MonthLabel'] = rolling_df['Incident Date'].dt.strftime('%m-%y')
    count_df = rolling_df.groupby(['MonthLabel', 'EventType']).size().reset_index(name='IncidentCount')

    # Pivot to wide format (Date, EventType, IncidentCount)
    # But keep long format for easier charting
    count_df['SortKey'] = pd.to_datetime('20' + count_df['MonthLabel'].str[-2:] + '-' + count_df['MonthLabel'].str[:2] + '-01')
    count_df = count_df.sort_values('SortKey')
    count_df = count_df.rename(columns={'MonthLabel': 'Date'})
    count_df = count_df[['Date', 'EventType', 'IncidentCount']]

    count_file = ROOT_AUTOMATION / "Incident Count by Date and Event Type_UPDATED.csv"
    count_df.to_csv(count_file, index=False, encoding='utf-8')
    log(f"[OK] {count_file.name}")

def create_folder_structure_readme():
    """Create README documenting the new folder structure"""
    log("=" * 80)
    log("PHASE 4: CREATING FOLDER STRUCTURE README")
    log("=" * 80)

    readme_content = r"""# Benchmark Data Architecture

## Overview
This directory contains Hackensack Police Department's Benchmark use-of-force tracking data, restructured for efficient querying and analysis.

## Folder Structure

### `all_events_combined/`
Master combined dataset merging all three event types:
- `master_combined_all_time.csv` - Complete historical dataset (2001-present)
- `metadata.json` - Record counts, date ranges, and last update timestamp

### `by_event_type/`
Individual event type datasets organized for query optimization:

```
by_event_type/
├── show_force/
│   ├── historical_complete.csv (future: all historical data)
│   └── archives/
│       ├── 2024_complete.csv
│       └── 2025_complete.csv
├── use_force/
│   ├── historical_complete.csv
│   └── archives/
│       ├── 2024_complete.csv
│       └── 2025_complete.csv
└── vehicle_pursuit/
    ├── historical_complete.csv
    └── archives/
        ├── 2024_complete.csv
        └── 2025_complete.csv
```

### `by_time_period/`
Pre-filtered datasets for common time windows:

#### `rolling_13month/`
**Current Window: December 2024 - December 2025**
- `current_window.csv` - All events combined for the rolling 13-month window
- `by_event_type/` - Individual event type files for the window
  - `show_force_13month.csv`
  - `use_force_13month.csv`
  - `vehicle_pursuit_13month.csv`
- `last_updated.txt` - Timestamp and window details

**Rolling Window Logic:**
- Always excludes the current incomplete month
- Includes the last 13 complete calendar months
- Updates monthly (today = 2026-01-12, so last complete month = Dec 2025)

#### `ytd_current/`
Year-to-date data for the current year:
- `2026_ytd.csv` - Combined YTD dataset
- `by_event_type/` - Individual event type YTD files

#### `archives/`
Historical snapshots of rolling windows for trend analysis.

## File Naming Conventions

### Date Formats
- **YYYY-MM-DD**: ISO 8601 standard for date columns in CSV files
- **MM-YY**: Display format for month labels (e.g., "12-24" = December 2024)

### Event Types
- `Show of Force`
- `Use of Force`
- `Vehicle Pursuit`

## Update Frequency

### Automated Updates
- `all_events_combined/` - Updated when new source data is available
- `rolling_13month/` - Updated monthly (first week of new month)
- `ytd_current/` - Updated daily/weekly as new incidents are recorded

### Manual Updates
- Archive historical years at year-end
- Update rolling window parameters as needed

## Power BI Integration

### Recommended Query Paths

**For 13-Month Rolling Window:**
```m
Source = Csv.Document(
    File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Benchmark\by_time_period\rolling_13month\current_window.csv")
)
```

**For YTD Current Year:**
```m
Source = Csv.Document(
    File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Benchmark\by_time_period\ytd_current\2026_ytd.csv")
)
```

**For All-Time Analysis:**
```m
Source = Csv.Document(
    File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Benchmark\all_events_combined\master_combined_all_time.csv")
)
```

## Data Schemas

### Common Columns (All Event Types)
- `Officer Name` (text)
- `Badge Number` (integer)
- `Rank` (text)
- `Organization` (text)
- `Incident Number` (text)
- `Report Number` (text)
- `Incident Date` (datetime, YYYY-MM-DD)
- `Subject type` (text)
- `Report Key` (text, unique identifier)
- `EventType` (text, added during merge)

### Use of Force Additional Columns
- `Location` (text)
- `Initial Contact` (text)
- `# of Officers Involved` (integer)
- `# of Subjects` (integer)

## Migration History

### Version 1.0 (2026-01-12)
- Initial restructuring from legacy `show_force/`, `use_force/`, `vehicle_pursuit/` folders
- Created master combined dataset
- Implemented rolling 13-month window (Dec 2024 - Dec 2025)
- Archived complete years 2024 and 2025
- Generated Power BI-ready datasets

## Backup Location
Full backup of legacy structure: `_Benchmark_BACKUP_20260112/`

## Support
For questions or issues, contact R. A. Carucci or refer to:
- `MIGRATION_REPORT_20260112.md` for detailed migration results
- `Master_Automation/2026_01_12_benchmark_m_codes_UPDATED.m` for updated Power BI queries
"""

    readme_file = ROOT_BENCHMARK / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    log(f"[OK] README created: {readme_file}")

def main():
    """Main execution function"""
    log("=" * 80)
    log("BENCHMARK DATA ARCHITECTURE OVERHAUL")
    log("Started: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    log("=" * 80)

    # Phase 1: Backup and Validation
    if not create_backup():
        log("[ERROR] Backup failed. Aborting migration.")
        return

    validation_results = validate_source_data()

    # Phase 2: Data Processing
    combined_df, metadata = create_master_combined_dataset()
    rolling_df = generate_rolling_13month_datasets(combined_df)
    ytd_df = generate_ytd_2026_datasets(combined_df)
    archive_historical_years(combined_df)

    # Phase 3: Power BI Integration
    matrix_df = generate_use_of_force_matrix(rolling_df)
    generate_supporting_visualizations(rolling_df)

    # Phase 4: Documentation
    create_folder_structure_readme()

    log("=" * 80)
    log("MIGRATION COMPLETED SUCCESSFULLY")
    log("Completed: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    log("=" * 80)
    log("\nNext steps:")
    log("1. Review generated files in by_time_period/ folders")
    log("2. Update Power BI M-code with new paths")
    log("3. Test Power BI queries and visualizations")
    log("4. Archive legacy structure if all validations pass")

if __name__ == "__main__":
    main()
