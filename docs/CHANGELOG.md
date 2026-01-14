# Changelog

All notable changes to the Master_Automation workspace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- [ ] Enhanced error reporting and recovery
- [ ] Performance monitoring and optimization
- [ ] Automated testing suite
- [ ] Integration with Power BI refresh scheduling

---

## [1.7.0] - 2026-01-14

### Added
- **Response Time ETL Enhanced Filtering (v2.0.0)**
  - New JSON configuration file (`config/response_time_filters.json`) for centralized filter rules
  - Added `load_filter_config()` function for JSON configuration loading with validation
  - Updated `load_mapping_file()` to return Category_Type mapping along with Response_Type
  - Added "How Reported" filter - excludes "Self-Initiated" records from response time calculations
  - Added Category_Type filtering with inclusion override logic
  - Added specific incident filtering from configuration file
  - Added comprehensive data verification step (Step 7) with quality checks
  - Added `--config` command line argument for custom filter configuration path

### Changed
- **Response Time Monthly Generator Script (v1.0.0 → v2.0.0)**
  - Script: `02_ETL_Scripts/Response_Times/response_time_monthly_generator.py`
  - Updated `process_cad_data()` signature to accept new filter parameters
  - Processing pipeline expanded from 6 steps to 12 steps for enhanced filtering
  - Changed unmapped incident handling from error to warning (allows processing to continue)
  - Category_Type now mapped alongside Response_Type for better categorization

### Filter Logic
- **How Reported Filter**: Excludes "Self-Initiated" records (exact match, case-sensitive)
- **Category_Type Filter**: Excludes entire categories:
  - Regulatory and Ordinance
  - Administrative and Support
  - Investigations and Follow-Ups
  - Community Engagement
- **Inclusion Overrides**: 14 incidents kept despite category exclusion (Suspicious Person, Missing Person, etc.)
- **Specific Incident Filter**: 42 specific incidents excluded from non-filtered categories

### Processing Pipeline (12 Steps)
1. Deduplication by ReportNumberNew
2. How Reported filter (exclude "Self-Initiated")
3. YearMonth creation from cYear/cMonth
4. Date range filter (2024-12 to 2025-12)
5. Admin incident filter (existing)
6. Response time calculation
7. Time window filter (0-10 minutes)
8. Response Type + Category_Type mapping
9. Category_Type filter (with inclusion overrides)
10. Specific incident filter
11. Data verification
12. Final validation (valid Response_Type only)

### Configuration Files
- **New**: `config/response_time_filters.json` - JSON configuration for all filter rules
- **Updated**: Response Time ETL script now reads from configuration file

---

## [1.6.0] - 2026-01-14

### Fixed
- **Response Time ETL and Power BI Query Update**
  - Updated M code (`m_code/response_time_calculator.m`) to use correct OneDrive paths
  - Changed base path from `C:\Dev\PowerBI_Date\` to `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\`
  - Expanded data coverage from 2 months to full 13-month range (Dec 2024 - Dec 2025)
  - Added graceful handling for missing monthly files
  - Fixed deduplication to prevent double-counting when files overlap
  - Updated query name reference from `___ResponseTimeCalculator` to `response_time_calculator`

### Added
- **New Response Time Monthly Generator Script**
  - Created `02_ETL_Scripts/Response_Times/response_time_monthly_generator.py`
  - Processes consolidated CAD export file (`2024_12_to_2025_12_ResponseTime_CAD.xlsx`)
  - Generates monthly CSV files in the correct Backfill directory structure
  - Includes full pipeline: deduplication by ReportNumberNew, admin filtering, response time calculation
  - Outputs in Power BI expected format: `Response Type, MM-YY, First Response_Time_MMSS`

### Changed
- **M Code Structure Improvements**
  - Refactored to use helper function (`ProcessCSV`) for cleaner code
  - Added configurable base path and target months list
  - Improved error handling with `try...otherwise` for optional data sources
  - Changed encoding from Windows-1252 to UTF-8 (65001) for better compatibility

### Data Coverage
- Current: December 2024 through November 2025 (12 months)
- December 2025 will be added when CAD source file is synced and ETL is run

---

## [1.5.0] - 2026-01-14

### Fixed
- **Summons ESU Organizational Update**
  - Updated Assignment_Master_V2.csv to map OFFICE OF SPECIAL OPERATIONS to PATROL BUREAU
  - Updated 4 officers (RYAN CONLON 354, MASSIMO DIMARTINO 144, JOHN KNAPP 141, DANE MARBLE 271)
  - ESU (OFFICE OF SPECIAL OPERATIONS) now correctly combined with Patrol Division totals
  - Updated summons_all_bureaus.m M code to combine ESU with Patrol Division
  - Fixed M code syntax errors (removed invalid backslashes, fixed file path formatting)

### Changed
- **Summons Bureau Grouping**
  - OFFICE OF SPECIAL OPERATIONS records now grouped with PATROL BUREAU
  - Combined totals displayed as PATROL DIVISION in Power BI visuals
  - Updated M code query to handle organizational structure changes

---

## [1.4.0] - 2026-01-13

### Fixed
- **December 2025 High Values Issue - Critical Data Integrity Fix**
  - Fixed double/triple counting from file format conversions (Watchdog script converts .xls to .xlsx and .csv)
  - Added file preference logic: process only .xlsx files when multiple formats exist (.xlsx > .csv > .xls)
  - Prevents processing same data multiple times from .xls source file and converted files
  - Removed 32,749 duplicate rows by eliminating .xls and .csv when .xlsx exists

- **Raw Time Off Data Deduplication**
  - Added deduplication with parsed dates/hours and normalized employee names
  - Improved matching by parsing dates and hours before deduplication
  - Removed 41,103 duplicate records from raw Time Off data (61,899 → 20,796 rows)
  - Ensures accurate usage calculations (Sick Time, SAT, Comp, Military, IOD)

- **Status Filtering for Usage Calculations**
  - Added approved-only filtering to raw Time Off data before usage metrics calculation
  - Removed 175 non-approved records from December 2025 usage totals
  - Ensures only approved transactions are counted in final metrics

### Changed
- **File Loading Logic**
  - Updated `load_folder()` to prefer .xlsx files over .csv and .xls for same base filename
  - Updated raw Time Off loading to use same file preference logic
  - Prevents duplicate processing when Watchdog script creates multiple file formats

- **Deduplication Strategy**
  - Main dataframe deduplication: Removed 61,222 duplicates (89,445 → 28,223 rows)
  - Raw Time Off deduplication: Removed 41,103 duplicates using parsed dates/hours
  - Deduplication now happens after parsing dates and hours for accurate matching

---

## [2025-12-11] - PowerBI_Date Migration to OneDrive

### Added
- **Migration verification script** (`verify_migration.ps1`)
  - Automated 8-point verification checklist
  - Validates config paths, directory structure, junctions, and script references
  - Provides detailed status report

- **Documentation**
  - `MIGRATION_VERIFICATION.md` - Comprehensive verification guide with manual check procedures
  - `VERIFICATION_SUMMARY.md` - Quick reference summary and testing steps
  - `CHANGELOG.md` - This file, for tracking all changes
  - `CURSOR_AI_PROMPT.md` - AI assistant prompt for workspace verification

### Changed
- **Configuration (`config\scripts.json`)**
  - Updated `powerbi_drop_path` from `C:\Dev\PowerBI_Date\_DropExports` to `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports`
  - Backup created: `config\scripts.json.bak`

- **Scripts**
  - `scripts\run_all_etl.ps1` - Updated next-step instructions with new PowerBI_Date path
  - Removed all references to old `C:\Dev\PowerBI_Date` paths

- **Documentation**
  - `README.md` - Updated with migration information, new directory structure, and recent updates section
  - `QUICK_START.md` - Updated all path references to new OneDrive location

### Fixed
- All path references updated to reflect OneDrive migration
- Script file path handling verified for OneDrive paths with spaces
- Documentation consistency across all files

### Infrastructure
- **Master_Automation Junction Created**
  - Location: `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Master_Automation`
  - Target: `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation`
  - Type: NTFS Junction (symlink)

### Verified
- ✅ Config file paths correct
- ✅ PowerBI_Date directory structure intact
- ✅ Master_Automation junction functional
- ✅ All script path references updated
- ✅ Documentation paths corrected
- ✅ Python executable accessible (Python 3.13.7)
- ✅ Drop folder accessible and writable

### Known Issues
- ⚠️ ETL script filenames may differ from `main.py` - verification needed
  - Action: Check actual script files and update `config\scripts.json` if needed
  - Common alternatives: `arrest_python_processor.py`, `process_*.py`, `run.py`

---

## [2025-12-09] - Initial Setup

### Added
- Initial Master_Automation workspace structure
- ETL orchestrator scripts (`run_all_etl.ps1`, `run_all_etl.bat`, `run_etl_script.ps1`)
- Configuration file (`config\scripts.json`)
- Basic documentation (`README.md`, `QUICK_START.md`)

### Features
- Sequential ETL script execution
- Error handling and logging
- Power BI output integration
- Selective script execution
- Status reporting

---

## Future Updates

### Planned
- [ ] ETL script filename verification and auto-detection
- [ ] Enhanced error reporting and recovery
- [ ] Performance monitoring and optimization
- [ ] Automated testing suite
- [ ] Integration with Power BI refresh scheduling

### Under Consideration
- [ ] Web-based dashboard for ETL status
- [ ] Email notifications for failures
- [ ] Retry logic for transient errors
- [ ] Parallel script execution option
- [ ] Configuration UI

---

## Notes

- All paths are now OneDrive-synced for cloud backup and multi-device access
- Junction link allows seamless access to Master_Automation from PowerBI_Date directory
- Verification script should be run after any configuration changes
- Logs directory is auto-created on first ETL run

---

**Maintained by:** R. A. Carucci
**Last Updated:** 2026-01-14

