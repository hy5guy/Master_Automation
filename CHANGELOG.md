# Changelog

All notable changes to the Master_Automation workspace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- [ ] Fix Power BI date filters for Engagement Initiatives visual (remove `TODAY()` logic)
- [ ] Fix Power BI date filters for Chief's Projects & Initiatives visual
- [ ] Investigate and backfill missing summons months (03-25, 07-25, 10-25, 11-25)
- [ ] Create export validation checklist for monthly Power BI exports
- [ ] Enhanced error reporting and recovery
- [ ] Performance monitoring and optimization
- [ ] Automated testing suite
- [ ] Integration with Power BI refresh scheduling

---

## [1.8.1] - 2026-02-05

### Added
- **December 2025 Power BI Visual Export Processing**
  - Processed and organized 36 CSV exports from December 2025 monthly report
  - Created comprehensive diagnostic reports for data quality issues
  - Added `2025_12_` prefix to all exported files for organization
  - Organized 53 total files into 16 categorized subdirectories
  
### Documentation
- **New Reports Created:**
  - `docs/DECEMBER_2025_VISUAL_EXPORT_DIAGNOSTIC_REPORT.md` - Full analysis of 53 exported files
  - `docs/ENGAGEMENT_INITIATIVES_BLANK_EXPORT_INVESTIGATION.md` - Technical troubleshooting guide with 7-step investigation plan
  - `docs/DECEMBER_2025_EXPORT_QUICK_SUMMARY.md` - Quick reference action guide and validation checklist
  
### Issues Identified
- **Critical Data Quality Issues (3 total):**
  1. **Engagement Initiatives by Bureau** - Blank CSV export despite showing 22 events in PDF report
     - Expected: 22 events, 71 attendees, 15.5 hours
     - Actual: Only headers, 0 data rows (83 bytes)
     - Root cause: Date filter using `TODAY()` or relative date logic
     - Affects all 3 .pbix copies
  
  2. **Chief Michael Antista's Projects and Initiatives** - Blank CSV export
     - Expected: Data rows
     - Actual: Only headers, 0 data rows (15 bytes)
     - Same root cause as Issue #1
  
  3. **Department-Wide Summons | Moving and Parking** - Missing 4 months of 2025 data
     - Missing: March, July, October, November 2025
     - Present: 9 of 13 months (12-24, 01-25, 02-25, 04-25, 05-25, 06-25, 08-25, 09-25, 12-25)
     - Root cause: Source data gap, not export issue
  
### Changed
- **File Organization Structure:**
  - Cleaned `PowerBI_Date\_DropExports\` folder after organizing exports
  - Created `PowerBI_Date\Backfill\2025_12\` with 16 subdirectories
  - Files distributed across: arrests (3), summons (11), response_time (10), community_engagement (2),
    use_of_force (3), nibrs (2), patrol (1), traffic (4), detective (4), crime_suppression (1),
    training (2), records (1), safe_streets (2), drones (2), school (2), chief (3)

### Fixed
- **Export Workflow Issues Documented:**
  - Identified date filter logic causing blank exports
  - Provided 4 fix options with DAX/M code examples
  - Created step-by-step troubleshooting guide
  - Documented export validation checklist for future use

### Recommendations
- **Power BI Report Fixes Needed:**
  - Replace `TODAY()` functions in date filters with explicit dates or parameters
  - Create month/year parameter for dynamic report filtering
  - Test exports immediately after PDF generation
  - Implement file size validation checks before archiving

---

## [1.8.0] - 2026-02-04

### Changed
- **Major Directory Consolidation and Cleanup**
  - Consolidated duplicate directories: merged `output/` into `outputs/`, merged `verification_reports/` into `verifications/reports/`
  - Cleaned root directory from 91 files to 7 essential files (92% reduction)
  - Organized 84 files into appropriate subdirectories
  - Deleted 50 temporary Claude Code marker files (`tmpclaude-*-cwd`)
  - Deleted 6 unnecessary temporary files (Untitled files, VERSION, error logs, etc.)
  
- **Documentation Consolidation**
  - Merged README.md versions (desktop + laptop `-PD_BCI_LTP` versions)
  - Merged CHANGELOG.md versions (consolidated all version history v1.0.0 → v1.7.0)
  - Merged SUMMARY.md versions (desktop + laptop versions)
  - Deleted redundant documentation files: `README-PD_BCI_LTP.md`, `CHANGELOG-PD_BCI_LTP.md`, `SUMMARY-PD_BCI_LTP.md`, `CHANGELOG1.md`

### Added
- **New Directory Structure**
  - `docs/response_time/` - Response Time documentation and reports (13 files)
  - `docs/archived_workflows/` - Archived workflow files
  - `outputs/arrests/` - Arrest-related exports (3 files)
  - `outputs/visual_exports/` - Power BI visual exports (23 files)
  - `outputs/summons_validation/` - Summons testing data (11 files)
  - `outputs/metadata/` - Configuration and verification metadata (6 files)
  - `outputs/community_engagement/` - Community engagement data (6 files)
  - `outputs/misc/` - Miscellaneous output files (9 files)
  - `outputs/large_exports/` - Large Excel exports (2 files, 37MB)
  - `scripts/_testing/` - Benchmark and debug scripts (4 files)
  - `verifications/reports/` - Verification markdown reports (2 files)

### Fixed
- **Directory Organization**
  - Eliminated confusion between `output/` and `outputs/` directories
  - Grouped all verification code and reports in single `verifications/` directory
  - Maintained `m_code/` in root for Power BI query access (industry standard)

### Documentation
- Created `docs/DOCUMENTATION_CONSOLIDATION_2026_02_04.md` - Documentation merge summary
- Created `docs/TEMP_FILES_CLEANUP_2026_02_04.md` - Temporary files cleanup log
- Created `docs/ROOT_CLEANUP_PLAN_2026_02_04.md` - Root cleanup plan
- Created `docs/ROOT_CLEANUP_COMPLETE_2026_02_04.md` - Root cleanup completion report
- Created `docs/DIRECTORY_CONSOLIDATION_PLAN_2026_02_04.md` - Directory consolidation plan
- Created `docs/DIRECTORY_CONSOLIDATION_COMPLETE_2026_02_04.md` - Consolidation completion report
- Updated `verifications/README.md` - Documented new reports/ subdirectory structure
- Updated `.gitignore` - Added patterns for temporary files and output directories

### Infrastructure
- **Root Directory**: Reduced from 91 files to 7 essential files
- **Documentation**: Consolidated from 6 versions to 3 canonical files
- **Directory Structure**: Professional organization with clear separation of concerns
- **M Code Location**: Confirmed as standalone in root (Power BI-specific, frequently accessed)

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
  - Deduplicates by ReportNumberNew (fixes multiple officer issue)
  - Filters 80+ administrative incident types
  - Calculates response times with fallback logic

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

---

## [1.3.0] - 2025-12-11 - PowerBI_Date Migration to OneDrive

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

## [1.2.0] - 2025-12-10 - Response Times Script Update & Full System Testing

### Added
- **MISSING_DATA_EXPORTS.md**: Documentation of ETL execution results and data export requirements
- Monthly export file support for Response Times script
- Documentation for two-phase data processing approach (backfill + monthly ETL)

### Changed
- **Response Times Script**: Updated `process_cad_data_for_powerbi_FINAL.py`
  - Changed from loading 3 historical Excel files to loading single monthly export
  - Now processes: `monthly_export\2025\2025_11_Monthly_CAD.xlsx.xlsx`
  - Script now handles only current month (November 2025)
  - Historical data (Nov 2024 - Oct 2025) handled via Power BI M code with backfill CSV files
- **Overtime TimeOff Script**: Previously corrected from v11 to v10 (confirmed working)
- **ACTION_ITEMS.md**: Updated with Response Times testing requirements and M code update needs
- **M_CODE_UPDATE_GUIDE.md**: Enhanced with Response Times specific templates

### Fixed
- Response Times script now successfully processes monthly export files
- All 7 enabled scripts tested and verified working
- File discovery in subdirectories working correctly (previous fix confirmed)

### Tested
- **Full ETL Execution**: All 7 enabled scripts executed successfully
  - Execution time: ~8 minutes
  - Files generated: 268 files
  - Scripts tested: Arrests, Community Engagement, Overtime TimeOff, Policy Training Monthly, Response Times, Summons, Arrest Data Source
- **Response Times Script**: Successfully loaded and processed November 2025 monthly export
  - Generated 66 output files
  - Completed in 6.18 seconds
- **Power BI Organization**: Successfully executed `organize_backfill_exports.ps1`
  - Organized 178 files into `Backfill\2025_12\`
  - Created categorized folder structure

### Documentation
- Updated README.md with latest status
- Updated SUMMARY.md with test results and current operational status
- Created comprehensive execution summary in MISSING_DATA_EXPORTS.md

---

## [1.1.0] - 2025-12-09 - Script Path Verification & Configuration Update

### Added
- **VERIFICATION_REPORT.md**: Comprehensive verification report documenting all script path checks
- **SUMMARY.md**: Quick reference summary of project status
- `notes` field to all script entries in `config/scripts.json` documenting path corrections

### Changed
- **Script Path Corrections**: Updated all script entry points in `config/scripts.json`:
  - **Arrests**: Changed from `main.py` → `arrest_python_processor.py`
  - **Community Engagement**: Changed from `main.py` → `src\main_processor.py`
  - **Overtime TimeOff**: Changed from `main.py` → `overtime_timeoff_13month_sworn_breakdown_v11.py` (later corrected to v10)
  - **Policy Training Monthly**: Changed from `main.py` → `src\policy_training_etl.py`
  - **Response Times**: Changed from `main.py` → `scripts\process_cad_data_for_powerbi_FINAL.py`
  - **Summons**: Changed from `main.py` → `SummonsMaster.py`
  - **Arrest Data Source**: Changed from `main.py` → `Analysis_Scripts\arrest_python_processor.py`
- **Overtime TimeOff**: Updated to use v10 instead of v11 (v11 was template, v10 is production-ready)
- **README.md**: Updated configuration examples and documentation to reflect actual script paths
- **README.md**: Added reference to verification report and updated directory structure

### Fixed
- All script paths now point to valid, existing Python files
- Script paths verified to exist on filesystem
- PowerShell script enhanced to search subdirectories for output files (`-Recurse` added to `Get-ChildItem`)

### Disabled
- **NIBRS**: Script disabled (`enabled: false`) - No Python processing script found in directory
  - Directory exists but contains only `.txt` and `.xlsx` files
  - Requires Python script creation or removal from config

### Verification Results
- ✅ **8/8 directories verified** - All paths exist
- ✅ **7/8 scripts corrected** - Valid Python entry points found and configured
- ⚠️ **0 scripts use `main.py`** - All scripts use specific entry point files
- ❌ **1 script disabled** - NIBRS has no Python script

### Notes
- None of the ETL scripts use a standard `main.py` entry point
- Each script uses project-specific filenames based on their actual implementation
- Configuration now includes `notes` field documenting the corrections

---

## [1.0.0] - 2025-12-09 - Initial Setup

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
**Last Updated:** 2026-02-05  
**Version:** 1.8.1
