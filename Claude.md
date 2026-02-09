# Project: Master_Automation - ETL Script Orchestration & Power BI Integration

## What This Is
Centralized orchestration hub that runs all Python ETL scripts feeding into Power BI reports. Provides automated execution, error handling, logging, and Power BI integration for multiple data processing workflows including Arrests, Community Engagement, Overtime/TimeOff, Response Times, and Summons.

## First Time Here?
New to this project? Start with:
1. Read `README.md` for high-level overview
2. Check `SUMMARY.md` for quick reference and enabled scripts
3. Review `config/scripts.json` for script configuration
4. Run verification: `.\verify_migration.ps1` to check paths

## Tech Stack
- **Languages**: PowerShell, Python
- **Orchestration**: PowerShell scripts (run_all_etl.ps1)
- **Data Processing**: Python ETL scripts
- **Output Format**: CSV files
- **Integration**: Power BI (via _DropExports folder)
- **Storage**: OneDrive (cloud-backed)
- **Configuration**: JSON (config/scripts.json)

## Project Map

### Active Code
- `scripts/run_all_etl.ps1` - Main PowerShell orchestrator (runs all enabled ETL scripts)
- `scripts/run_all_etl.bat` - Batch file wrapper for easy execution
- `scripts/run_etl_script.ps1` - Helper script to run individual scripts
- `scripts/overtime_timeoff_with_backfill.py` - Overtime/TimeOff monthly wrapper with backfill
- `verify_migration.ps1` - Automated verification script for paths and configuration

### Data Directories
- `config/` - Configuration files (scripts.json, response_time_filters.json)
- `scripts/` - PowerShell execution scripts and Python helper scripts
  - `_testing/` - Benchmark and debug scripts
- `logs/` - ETL execution logs (auto-created)
- `docs/` - Project documentation
  - `response_time/` - Response Time documentation and reports
  - `archived_workflows/` - Archived workflow files
- `m_code/` - Power BI M code queries (13 active + 16 archived)
  - `archive/` - Archived M code versions
- `outputs/` - Organized output files
  - `arrests/` - Arrest-related exports
  - `visual_exports/` - Power BI visual exports
  - `summons_validation/` - Summons testing data
  - `metadata/` - Configuration and verification metadata
  - `community_engagement/` - Community engagement data
  - `misc/` - Miscellaneous output files
  - `large_exports/` - Large Excel exports
- `verifications/` - ETL verification framework
  - `reports/` - Verification markdown reports

### Configuration & Docs
- `config/scripts.json` - ETL script configuration (paths, settings, enabled/disabled status)
- `README.md` - Main project documentation
- `SUMMARY.md` - Project summary and quick reference
- `CHANGELOG.md` - Version history and updates
- `docs/` - Detailed documentation (guides, reports, troubleshooting)

## How to Work on This Project

### Before Making Changes
1. Check `config/scripts.json` for script configurations
2. Review `SUMMARY.md` for enabled scripts and current status
3. Review relevant documentation in `docs/` for task context
4. Run verification: `.\verify_migration.ps1` to ensure paths are correct

### Example Workflow
**Task**: Add a new ETL script to the orchestration
1. Read `README.md` for configuration structure
2. Add script entry to `config/scripts.json` with path, script name, and order
3. Test with: `.\scripts\run_etl_script.ps1 -ScriptName "ScriptName"`
4. Verify output appears in Power BI drop folder
5. Run full suite: `.\scripts\run_all_etl.ps1`
6. Check logs in `logs/` directory
7. Commit changes

### Code Standards
- Use structured logging (detailed logs for each script execution)
- Implement error handling (scripts run independently, failures don't stop others)
- Update `CHANGELOG.md` when adding features or making significant changes
- Maintain `config/scripts.json` structure (name, path, script, enabled, order, timeout_minutes)
- Document script-specific details in `docs/` when needed

### Finding Information
When searching this codebase, focus on:
- **Core orchestration**: `scripts/run_all_etl.ps1`, `scripts/run_etl_script.ps1`
- **Configuration**: `config/scripts.json`, `README.md`, `SUMMARY.md`
- **ETL Scripts**: Individual scripts in `02_ETL_Scripts/` directories (referenced by config)
- **Documentation**: `docs/` folder for detailed guides and troubleshooting

Avoid loading all files at once - use targeted searches.

**Detailed guides:**
- **Project overview**: `README.md`
- **Quick reference**: `SUMMARY.md`
- **Configuration**: `config/scripts.json`
- **Version history**: `CHANGELOG.md`
- **Migration/verification**: `docs/VERIFICATION_REPORT.md`, `docs/MIGRATION_VERIFICATION.md`
- **Project structure**: `docs/PROJECT_STRUCTURE.md`
- **Troubleshooting**: `docs/` folder for script-specific guides

## Protected Resources
**Do not modify without explicit confirmation:**
- `config/scripts.json` (critical ETL script configuration)
- Production ETL scripts in `02_ETL_Scripts/` directories (referenced, not stored here)
- Power BI integration paths (OneDrive-based)
- `CHANGELOG.md` (version history - update, don't replace)

## Common Pitfalls
- **Don't** modify production ETL scripts directly - they live in `02_ETL_Scripts/` directories
- **Always** check `config/scripts.json` before adding or modifying script configurations
- **Remember** to verify paths after changes using `.\verify_migration.ps1`
- **Use** dry-run mode (`-DryRun` parameter) to preview execution before running
- **Check** logs in `logs/` directory when troubleshooting script failures
- **Verify** OneDrive sync status before assuming files are available

## Enabled ETL Scripts
1. **Arrests** - `arrest_python_processor.py`
2. **Community Engagement** - `deploy_production.py` (or `src/main_processor.py`)
3. **Overtime TimeOff** - `overtime_timeoff_with_backfill.py`
4. **Response Times** - `response_time_diagnostic.py`
5. **Summons** - `main_orchestrator.py`

## Key Paths
- **Workspace**: `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation`
- **Config**: `config\scripts.json`
- **Logs**: `logs\`
- **PowerBI Drop**: `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports`
- **ETL Scripts**: `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\*`

## Recent Updates (2026-02-09)

### v1.10.0 - Master Automation 100% Operational - All Workflows Fixed
- **Complete Success** - All 6 ETL workflows now operational (100% success rate)
- **Overtime TimeOff Fixed** - Resolved missing personnel file (`Assignment_Master_V2.csv`)
- **Response Times Fixed** - Migrated to timereport hybrid strategy (v2.1.0)
- **Benchmark Directory Cleanup** - Consolidated duplicate directories, simplified structure
- **Execution Time** - 2.04 minutes for all 6 workflows (Arrests: 6.27s, Community: 7.86s, Overtime: 19.92s, Response Times: 76.09s, Summons: 2.06s, Derived: 8.66s)
- **January 2026 Report** - Successfully generated and ready for publication

### Current System Status
- **Version**: 1.10.0
- **Status**: ✅ 100% Operational (6/6 workflows)
- **Last Successful Run**: 2026-02-09 12:55:22 (2.04 minutes)
- **Enabled Scripts**: 6 (All operational with execution times)
- **Recent Major Fixes**: Personnel file dependency, timereport hybrid strategy, Benchmark consolidation

---

## Recent Updates (2026-02-05)

### v1.8.1 - December 2025 Power BI Visual Export Processing & Diagnostics
- **December 2025 Exports Organized** - Processed and organized 36 CSV exports into 16 categories
- **Critical Issues Documented** - Identified 3 data quality issues (2 blank exports, 1 data gap)
- **Comprehensive Diagnostics** - Created 3 detailed reports with troubleshooting guides and fix options
- **Export Workflow Enhanced** - Created validation checklist for future monthly exports
- **Files Organized**: 53 files across arrests, summons, response_time, community_engagement, use_of_force, nibrs, patrol, traffic, detective, crime_suppression, training, records, safe_streets, drones, school, chief

### Critical Issues Identified:
1. **Engagement Initiatives by Bureau** - Blank export (expected 22 events) - Root cause: `TODAY()` date filter
2. **Chief's Projects & Initiatives** - Blank export - Same date filter issue
3. **Department-Wide Summons** - Missing 4 months (03-25, 07-25, 10-25, 11-25) - Source data gap

### Documentation Created:
- `DECEMBER_2025_VISUAL_EXPORT_DIAGNOSTIC_REPORT.md` - Full analysis
- `ENGAGEMENT_INITIATIVES_BLANK_EXPORT_INVESTIGATION.md` - Technical guide with 7-step troubleshooting
- `DECEMBER_2025_EXPORT_QUICK_SUMMARY.md` - Quick reference

## Recent Updates (2026-02-04)

### v1.8.0 - Major Directory Consolidation & Cleanup
- **Root Directory Cleanup** - Reduced from 91 files to 7 essential files (92% reduction)
- **Directory Consolidation** - Merged `output/` → `outputs/`, merged `verification_reports/` → `verifications/reports/`
- **Documentation Consolidation** - Merged README, CHANGELOG, SUMMARY from desktop and laptop versions
- **Organized Structure** - Created 9 new subdirectories under `outputs/` for proper organization
- **Temporary File Cleanup** - Deleted 50 Claude Code marker files + 6 unnecessary temp files
- **All Data Preserved** - 100% of files preserved, just better organized

### Current System Status
- **Version**: 1.10.0
- **Status**: ✅ 100% Operational (6/6 workflows)
- **Last Successful Run**: 2026-02-09 12:55:22 (2.04 minutes)
- **Enabled Scripts**: 6 (All operational)
- **Root Directory**: Clean and professional (7 essential files only)
- **Recent Major Fixes**: Personnel file dependency, timereport hybrid strategy, Benchmark consolidation

---
*Last updated: 2026-02-09 | Format version: 3.2*