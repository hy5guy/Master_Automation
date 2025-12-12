# Changelog

All notable changes to the Master_Automation workspace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

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
**Last Updated:** 2025-12-11  
**Current Version:** 1.0.0

