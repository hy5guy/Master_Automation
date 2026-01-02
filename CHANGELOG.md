# Changelog

All notable changes to the Master_Automation workspace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-01-02

### Added
- **Input Validation Feature**
  - Added `-ValidateInputs` parameter to `run_all_etl.ps1`
  - Automatic input validation when using `-DryRun` mode
  - Validates required export files exist before execution:
    - Summons: E-ticket exports in `05_EXPORTS\_Summons\E_Ticket\YYYY\YYYY_MM_eticket_export.csv`
    - Response Times: CAD monthly exports in `05_EXPORTS\_CAD\monthly_export\YYYY\YYYY_MM_Monthly_CAD.xlsx`
  - Shows helpful error messages with available files when expected files are missing

- **Badge Normalization Diagnostics**
  - `scripts/diagnose_badge_normalization.py` - Comprehensive badge number format validation
  - `scripts/find_missing_badge.py` - Quick script to find badges in e-ticket not in Assignment Master
  - `scripts/fix_assignment_master.py` - Fixes PADDED_BADGE_NUMBER format and adds missing entries
  - `scripts/verify_assignment_fix.py` - Verifies Assignment Master fixes

- **Script Archive**
  - Created `scripts/_archive/` directory for old/unused scripts
  - Archived `run_all_etl-PD_BCI_LTP.ps1` (old version superseded by main script)

### Changed
- **E-Ticket Export Path Structure**
  - Updated scripts to handle new e-ticket export naming convention:
    - Old: `YY_MM_e_ticketexport.csv` (e.g., `25_12_e_ticketexport.csv`)
    - New: `YYYY_MM_eticket_export.csv` in year subdirectories (e.g., `2025\2025_12_eticket_export.csv`)
  - Updated `diagnose_summons_missing_months.py` to search year subdirectories
  - Updated `count_patrol_m_p_from_eticket.py` help text

- **Response Times Validation**
  - Fixed filename pattern from `YYYY_MM_Monthly_CAD.xlsx.xlsx` to `YYYY_MM_Monthly_CAD.xlsx`
  - Updated validation to check correct year subdirectory structure

- **Assignment Master Fix**
  - Fixed `Assignment_Master_V2.csv` PADDED_BADGE_NUMBER column (ensured all values are 4-digit padded)
  - Added badge 1711 entry for PEO JOHN SQUILLACE (TRAFFIC BUREAU)

### Fixed
- E-ticket export path validation now correctly searches year subdirectories
- Response Times validation now uses correct filename format (single .xlsx extension)
- Badge 1711 missing from Assignment Master (now added with correct bureau assignment)
- All PADDED_BADGE_NUMBER values verified as correctly formatted (4-digit strings, no floats)

### Verified
- All e-ticket exports correctly formatted (4-digit Officer Id values)
- Assignment Master PADDED_BADGE_NUMBER column correctly formatted
- Badge 1711 now matches between e-ticket export and Assignment Master
- Input validation correctly identifies missing export files

## [Unreleased]

### Added
- **Validation / QC helpers**
  - `scripts/compare_policy_training_delivery.py` - Policy Training Delivery Cost: visual export vs ETL output vs backfill history
  - `scripts/compare_summons_deptwide.py` - Summons Dept-Wide Moving/Parking: visual export vs backfill history + ETL current month
  - `scripts/diagnose_summons_blank_bureau.py` - Summons: detect blank `WG2` (Bureau) rows that appear as blank Bureau in visuals
  - `scripts/run_summons_with_overrides.py` - Summons: run ETL with injected badge overrides (without editing upstream project)
  - `scripts/diagnose_summons_assignment_mapping.py` - Diagnose WG2 assignment mapping issues
  - `scripts/fix_summons_wg2_from_assignment.py` - Fix WG2 column by copying from WG2_ASSIGN
  - `scripts/diagnose_summons_missing_months.py` - Identify missing months in staging workbook
  - `scripts/diagnose_summons_top5_vs_deptwide.py` - Validate Top 5 queries vs Dept-Wide data
  - `scripts/compare_summons_all_bureaus.py` - Compare All Bureaus visual vs ETL output

- **Documentation**
  - `claude_code_summons.md` - Comprehensive troubleshooting guide for Summons Power BI issues
  - `SUMMONS_DIAGNOSTIC_REPORT_2025_12_12.md` - Complete diagnostic report with findings
  - `SUMMONS_DAX_MEASURES_CORRECTED.txt` - Corrected DAX measure with instructions
  - `DAX_MEASURES_FIXED.txt` - Alternative DAX measure versions
  - `DAX_MEASURE_FIXED_FINAL.txt` - Final DAX measure recommendations

### Verified
- Policy Training Monthly: Delivery Cost history matches backfill; ETL computed the new month (11-25)
- Summons: Dept-Wide Moving/Parking history matches backfill; ETL computed 11-25 from e-ticket export
- **Summons Data Quality (2025-12-12):**
  - WG2 column: 134,144 rows (42.52%) have bureau assignments (expected behavior)
  - M Code queries: All 3 queries working correctly, handling missing columns properly
  - Missing columns: TICKET_COUNT and ASSIGNMENT_FOUND correctly don't exist (each row = 1 ticket)
  - Top 5 queries: Returning data correctly for Moving and Parking violations
  - Data validation: 315,507 total rows, 311,588 Moving (98.76%), 3,910 Parking (1.24%)

### Fixed
- Summons "blank Bureau" row caused by missing assignment enrichment for badge 1711
  - Added a run wrapper that injects a badge override (maps 1711 → Traffic Bureau) and regenerates `summons_powerbi_latest.xlsx`
- **Summons Power BI Issues (2025-12-12):**
  - Fixed WG2 column population: WG2 now populated from WG2_ASSIGN (134,144 rows fixed)
  - Fixed M Code queries: Updated to handle missing TICKET_COUNT and ASSIGNMENT_FOUND columns dynamically
  - Fixed Top 5 Moving Violations: Excludes Traffic Bureau officers, handles null TYPE values
  - Fixed Top 5 Parking Violations: Handles null TYPE values, uses correct aggregation
  - Fixed DAX measure: Provided corrected `___Total Tickets = COUNTROWS('___Summons')` formula
  - All M code queries verified working correctly with proper column filtering

### Known Issues
- **Summons Missing Months (2025-12-12):**
  - Missing months identified: 03-25, 10-25, 11-25
  - Root cause: ETL script needs to merge backfill data with current month exports
  - Action required: Run Summons ETL script to regenerate staging workbook with all months
  - Diagnostic script created: `scripts/diagnose_summons_missing_months.py`

## [1.0.0] - 2025-12-11

### Added

#### Project Structure
- **Folder scaffolding**
  - `docs/` - Documentation files
  - `chatlogs/` - AI chat logs
  - `_DropExports/` - Optional staging folder
  - `logs/` - ETL execution logs (auto-created)

#### Documentation
- `SUMMARY.md` - Project summary and quick reference
- `CHANGELOG.md` - Version history (this file)
- `docs/PROJECT_STRUCTURE.md` - Directory structure guide
- `docs/FOLDER_STRUCTURE_CREATED.md` - Folder setup documentation
- `chatlogs/README.md` - Chat log guidelines

#### Scripts
- **Migration verification script** (`verify_migration.ps1`)
  - Automated 8-point verification checklist
  - Validates config paths, directory structure, junctions, and script references
  - Provides detailed status report

- **Overtime TimeOff helpers**
  - `scripts/overtime_timeoff_with_backfill.py` - Monthly wrapper (v10 + backfill + accrual history)
  - `scripts/restore_fixed_from_backfill.py` - Restore history into `FIXED_monthly_breakdown_*.csv`
    - Supports both WIDE exports (month columns) and LONG exports (`PeriodLabel` + `Sum of Value`)
    - Optional `--include-accruals` flag (off by default)
  - `scripts/compare_vcs_time_report_exports.py` - Compare refreshed exports vs baseline backfill exports

#### Git Repository
- Initialized local git repository
- Added `.gitignore` for logs and temporary files

### Changed

#### Configuration (`config\scripts.json`)
- Updated script filenames to match actual files:
  - Arrests: `arrest_python_processor.py`
  - Community Engagement: `deploy_production.py`
  - Overtime TimeOff: `overtime_timeoff_with_backfill.py` (wrapper around v10 + backfill)
  - Response Times: `response_time_diagnostic.py`
  - Summons: `main_orchestrator.py`
- Disabled scripts without Python files:
  - Policy Training Monthly
  - Arrest Data Source
  - NIBRS
- Updated `powerbi_drop_path` to OneDrive location
- Backup created: `config\scripts.json.bak`

#### Scripts
- `scripts\run_all_etl.ps1` - Updated next-step instructions with new PowerBI_Date path
- Removed all references to old `C:\Dev\PowerBI_Date` paths

- `scripts/overtime_timeoff_with_backfill.py`
  - Default backfill root updated to: `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill`
  - Now backfills `analytics_output\monthly_breakdown.csv` for prior 12 months from the same backfill export (preserves current month from v10)

#### Documentation Organization
- Moved all markdown files (except README.md) to `docs/` folder
- Organized documentation by topic
- Created chatlogs directory for AI conversations

#### ETL Scripts
- Updated Response Times script backfill path:
  - Changed from: `C:\Dev\PowerBI_Date\Backfill\...`
  - Changed to: `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\...`

### Fixed
- All path references updated to reflect OneDrive migration
- Script file path handling verified for OneDrive paths with spaces
- Documentation consistency across all files
- ETL script filenames verified and corrected

- Overtime TimeOff historical “null/0” issue in Power BI visual
  - Restored legacy usage rows into `FIXED_monthly_breakdown_*.csv` from backfill exports
  - Populated accrual history by backfilling `analytics_output\monthly_breakdown.csv` (previously only current month existed)

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
- ✅ All enabled script files exist and are accessible
- ✅ Dry run test passed successfully

---

## [0.9.0] - 2025-12-11 - Migration to OneDrive

### Added
- Migration verification script (`verify_migration.ps1`)
- Comprehensive migration documentation
- Verification guides and summaries

### Changed
- **PowerBI_Date Migration**
  - From: `C:\Dev\PowerBI_Date_Merged`
  - To: `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date`
- Updated all path references in configuration and scripts
- Updated documentation with new paths

### Fixed
- All old path references removed
- Script logic verified for OneDrive paths

---

## [0.1.0] - 2025-12-09 - Initial Setup

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
- [ ] Column reorder utility for backfill CSVs

### Under Consideration
- [ ] Web-based dashboard for ETL status
- [ ] Email notifications for failures
- [ ] Retry logic for transient errors
- [ ] Parallel script execution option
- [ ] Configuration UI
- [ ] Automated backfill column ordering

---

## Notes

- All paths are now OneDrive-synced for cloud backup and multi-device access
- Junction link allows seamless access to Master_Automation from PowerBI_Date directory
- Verification script should be run after any configuration changes
- Logs directory is auto-created on first ETL run
- Documentation organized in `docs/` folder for better structure
- Chat logs should be saved to `chatlogs/` folder with date prefix

---

**Maintained by:** R. A. Carucci  
**Last Updated:** 2026-01-02  
**Current Version:** 1.1.0

