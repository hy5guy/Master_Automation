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
- `scripts/run_all_etl.ps1` - Main PowerShell orchestrator (runs all enabled ETL scripts; uses $OneDriveBase for paths; Visual Export Normalization phase)
- `scripts/run_all_etl.bat` - Batch file wrapper for easy execution
- `scripts/run_etl_script.ps1` - Helper script to run individual scripts
- `scripts/path_config.py` - Centralized get_onedrive_root() (ONEDRIVE_BASE / ONEDRIVE_HACKENSACK)
- `scripts/overtime_timeoff_with_backfill.py` - Overtime/TimeOff monthly wrapper (strict file discovery, validate_fixed_schema)
- `scripts/validate_exports.py` - Pre-flight check for OT/TimeOff Excel exports
- `scripts/validate_outputs.py` - FIXED CSV schema validation
- `scripts/test_pipeline.bat` - Overtime/TimeOff test suite (validate → dry-run → validate outputs)
- `scripts/summons_backfill_merge.py` - Merge gap months (03-25, 07-25, 10-25, 11-25) into summons df
- `scripts/normalize_visual_export_for_backfill.py` - Normalize visual exports for backfill (13-month window, PeriodLabel for OT; uses path_config)
- `scripts/process_powerbi_exports.py` - Process Power BI exports from _DropExports using mapping (match_pattern, enforce_13_month)
- `scripts/validate_13_month_window.py` - Validate CSV has exactly 13-month rolling window (single file or folder scan)
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
- `requirements.txt` - Python deps (pandas, openpyxl) for validate_exports and summons_backfill_merge
- `README.md` - Main project documentation
- `SUMMARY.md` - Project summary and quick reference
- `CHANGELOG.md` - Version history and updates
- `docs/` - Detailed documentation (guides, reports, troubleshooting)
- `docs/VISUAL_EXPORT_NORMALIZATION_AND_SUMMONS_BACKFILL.md` - Normalization phase + Summons follow-up
- `docs/SUMMONS_BACKFILL_INJECTION_POINT.md` - Where to call merge_missing_summons_months, dependencies, caveats
- `docs/13_MONTH_WINDOW_IMPLEMENTATION_GUIDE.md` - 13-month rolling window deployment, flow, validation
- `docs/13_MONTH_WINDOW_CORRECTIONS.md` - Selective enforcement (24 vs 8 visuals), NIBRS pattern matching
- `docs/13_MONTH_QUICK_REFERENCE.md` - Which visuals have 13-month enforcement, quick test

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
Paths are portable: set `ONEDRIVE_BASE` (or `ONEDRIVE_HACKENSACK`) to override the default. Python uses `path_config.get_onedrive_root()`; PowerShell uses `$OneDriveBase`.
- **Workspace**: `Master_Automation` (default under OneDrive)
- **Config**: `config\scripts.json`
- **Logs**: `logs\`
- **PowerBI Drop**: `<OneDrive>\PowerBI_Date\_DropExports`
- **ETL Scripts**: `<OneDrive>\02_ETL_Scripts\*`

## Recent Updates (2026-02-12)

### v1.15.0 - 13-Month Rolling Window for Visual Exports ✅
- **13-month enforcement** – Exports for 24 specified visuals contain exactly 13 full months ending with the previous month (never current month). Window recalculates from today each run.
- **Normalizer** – `scripts/normalize_visual_export_for_backfill.py`: `--enforce-13-month` flag; `calculate_13_month_window()`, `enforce_13_month_window()`; keeps **PeriodLabel** for Overtime/TimeOff backfill.
- **Process script** – `scripts/process_powerbi_exports.py`: **match_pattern** (regex) for dynamic visual names (e.g. NIBRS date range); **enforce_13_month_window** from mapping passed to normalizer; dry-run and production pass `--enforce-13-month` when mapping says so.
- **Mapping** – `Standards/config/powerbi_visuals/visual_export_mapping.json`: 32 visuals; 24 with `enforce_13_month_window: true`, 8 with `false` (Arrests, Top 5 Summons, All Bureaus Summons, In-Person Training, Incident Distribution). NIBRS uses `match_pattern: "^13-Month NIBRS Clearance Rate Trend"`.
- **Validation** – `scripts/validate_13_month_window.py`: validate single file or scan folder for 13-month window.
- **Docs** – `docs/13_MONTH_WINDOW_IMPLEMENTATION_GUIDE.md`, `docs/13_MONTH_WINDOW_CORRECTIONS.md`, `docs/13_MONTH_QUICK_REFERENCE.md`.

### v1.14.0 - Path Centralization, Overtime/TimeOff Hardening, Summons Backfill Prep
- **Path portability** – `scripts/path_config.py` and `$OneDriveBase` in run_all_etl.ps1; all path-using scripts respect ONEDRIVE_BASE/ONEDRIVE_HACKENSACK
- **Overtime/TimeOff hardening** – Strict YYYY_MM file discovery; validate_exports.py (pre-flight), validate_outputs.py (FIXED schema), validate_fixed_schema in wrapper; test_pipeline.bat
- **Visual Export Normalization** – run_all_etl.ps1 normalizes *Monthly Accrual and Usage Summary*.csv in _DropExports before summary
- **Summons backfill** – summons_backfill_merge.py (full merge for gap months 03-25, 07-25, 10-25, 11-25); injection point and caveats in docs/SUMMONS_BACKFILL_INJECTION_POINT.md
- **requirements.txt** – pandas, openpyxl; README and docs note Python env requirement

## Recent Updates (2026-02-13)

### v1.15.2 - STACP Visual 13-Month Rolling Window Fixed ✅ **DEPLOYED**

**STACP Power BI Visual** - Fixed three critical issues preventing 13-month data display

#### Three Critical Fixes:
1. **Year Detection Bug** - Hardcoded for "24"/"25" → now works for any 2-digit year
   - Dynamic year validation (future-proof for 2024-2099+)
   - Enhanced month validation (1-12 range check)
   - Handles both M-YY and MM-YY column formats
   
2. **Month Format Handling** - Enhanced to accept single-digit (3-25) and padded (03-25)
   - Excel analysis confirmed all columns properly formatted (MM-YY)
   - Added robust validation for future compatibility
   
3. **Window Calculation Bug** - Fixed rolling 13-month window logic ⭐ **Main Issue**
   - **Before**: `StartMonth = EndMonth - 1` → only 2 months (12-25, 01-26)
   - **After**: `StartMonth = EndMonth` → 13 months (01-25 through 01-26)
   - Window now correctly: same month, one year earlier

#### Diagnostic Tools Created:
- `m_code/stacp/STACP_DIAGNOSTIC.m` - Column detection & window verification
- `m_code/stacp/STACP_pt_1_2_FIXED.m` - Fixed query (deployed)
- `scripts/analyze_stacp_workbook.py` - Excel structure analyzer
- `docs/STACP_TROUBLESHOOTING_GUIDE.md` - Comprehensive troubleshooting

#### Documentation:
- `docs/STACP_YEAR_DETECTION_FIX_2026_02_13.md` - Year detection details
- `docs/STACP_INCONSISTENT_DATE_FORMAT_FIX.md` - Format handling
- `docs/STACP_WINDOW_CALCULATION_FIX.md` - Window logic fix
- `docs/STACP_FIX_QUICK_REF.md` - Quick reference

**Status**: Deployed and verified - all 13 months displaying correctly ✅

---

## Recent Updates (2026-02-12)

### v1.15.1 - Smart Date Inference Deployed ✅ **PRODUCTION READY**

**Data-Driven Date Inference** - Power BI visual export processing now reads CSV data to infer dates! **95% accuracy vs 70% filename-only method**

#### Smart Date Inference:
- **13-Month Visuals** - Uses LAST period column (most recent month in rolling window)
  - Example: Columns `["01-25", "02-25", ..., "01-26"]` → uses `"01-26"` → `2026_01`
  - Works for: Monthly Accrual, Patrol Division, Social Media Posts, Training Cost, etc.
- **Single-Month Visuals** - Reads Period/Month_Year column value
  - Example: `Period="11-25"` → `2025_11_patrol_division_activity.csv`
  - Works for: Arrests, Traffic, Drone Performance, etc.
- **Fallback** - Filename pattern or previous month
  - Ensures always returns valid YYYY_MM
- **Unicode Safe** - Handles special characters in filenames gracefully
- **Transparent** - Logs show data source for each inference

#### Test Results:
- Processed 16 CSV files from `_DropExports`
- 100% accuracy (16/16 files correctly dated)
- 4 files normalized with 13-month enforcement
- 4 files copied to Backfill for ETL consumption
- Pattern matching works for dynamic visual names (NIBRS)

---

## Recent Updates (2026-02-09)

### v1.11.0 - Response Time Power BI M Code Fixed ✅ **DEPLOYED**

**Power BI M Code Fix** - Response Time query 31% error rate resolved! **Production Ready**

#### Critical Power BI Fix:
- **Response Time Calculator M Code (v2.8.0)** - Fixed type conversion errors
  - Root cause: `type text` annotation conflicted with Power Query auto-typing
  - Fixed decimal precision: 2.87, 2.92 now convert correctly to MM:SS
  - Fixed unpivot column reference (MM-YY only, not Month-Year)
  - Column quality: 100% valid (up from 69% valid, 31% errors)
  - All formats supported: MM:SS, M:SS, HH:MM:SS, decimal minutes
  - File: `m_code\___ResponseTimeCalculator.m` (v2.8.0, 358 lines)
  - **Status**: Tested with production data - 0% errors achieved ✅

#### AI Collaboration:
- **Claude**: Identified root cause, delivered comprehensive 7-point fix
- **Gemini**: Type-agnostic pattern (`Value.Is()`), locale safety enhancements

### v1.12.0 - Response Time Backfill Baseline Established

**Formal Backfill Structure Created** - Response Time data now organized and validated

#### What Was Done:
- **Backfill Directory Structure** - Created 13 monthly directories (Jan 2025 - Jan 2026)
  - Location: `PowerBI_Date\Backfill\YYYY_MM\response_time\`
  - Files: One CSV per month with 3 rows (Emergency, Routine, Urgent)
  - Populated from current validated visual export data
  - M code now prioritizes Backfill folder as primary source

- **M Code Updated to v2.8.3** - Restored Backfill priority
  - Priority: Backfill > visual_export > outputs > _DropExports
  - Ensures validated data with January 14 methodology (deduplication + filtering)
  - Maintains 0% error rate from v2.8.0 fix

- **Fresh Calculator Disabled** - Experimental approach disabled
  - Missing January 14 deduplication/filtering logic
  - Script available for future enhancement: `scripts\response_time_fresh_calculator.py`
  - Can be re-enabled once validated methodology is implemented

#### Monthly Workflow Established:
1. Run ETL for new month
2. Refresh Power BI
3. Export Response Time visual to CSV
4. Save to: `Backfill\YYYY_MM\response_time\YYYY_MM_Average_Response_Times__Values_are_in_mmss.csv`
5. Next month: Power BI automatically loads it

#### Documentation:
- `docs/RESPONSE_TIME_v2.8.3_BACKFILL_RESTORE.md` - Revert decision and reasoning
- `docs/BACKFILL_BASELINE_CREATED_2026_02_09.md` - Baseline creation details
- `docs/RESPONSE_TIME_FINAL_STATUS_2026_02_09.md` - Final status checklist

**Status:** Backfill baseline established, monthly workflow documented

---

### v1.10.0 - Master Automation 100% Operational - All Workflows Fixed
- **Complete Success** - All 6 ETL workflows now operational (100% success rate)
- **Overtime TimeOff Fixed** - Resolved missing personnel file (`Assignment_Master_V2.csv`)
- **Response Times Fixed** - Migrated to timereport hybrid strategy (v2.1.0)
- **Benchmark Directory Cleanup** - Consolidated duplicate directories, simplified structure
- **Execution Time** - 2.04 minutes for all 6 workflows (Arrests: 6.27s, Community: 7.86s, Overtime: 19.92s, Response Times: 76.09s, Summons: 2.06s, Derived: 8.66s)
- **January 2026 Report** - Successfully generated and ready for publication

### Current System Status
- **Version**: 1.15.4
- **Status**: ✅ 100% Operational (6/6 ETL workflows + Power BI queries + Detective Queries Fixed + CSB Workbook Ready)
- **Enabled Scripts**: 6 (All operational)
- **Power BI Queries**: Response Time M code fixed (v2.8.0), STACP 13-month window fixed, Detective queries restructured and working
- **Excel Workbooks**: CSB workbook 2026 setup complete (templates + XLOOKUP formulas ready)
- **Recent Major Updates**: CSB workbook 2026 preparation (templates + XLOOKUP), Detective queries Excel structure fix (YY-MMM parsing + rolling window), STACP 13-month rolling window (3 fixes), Smart date inference (95% accuracy), 13-month rolling window enforcement (24 visuals), process_powerbi_exports (match_pattern + enforce_13_month), path centralization, Overtime/TimeOff hardening, Visual Export Normalization, Summons backfill prep

---

## Recent Updates (2026-02-13)

### v1.15.4 - CSB Workbook 2026 Setup Complete ✅
- **Complete Success** - CSB workbook fully prepared for 2026 monthly data entry
- **Work by Claude in Excel**: Sheet renaming (YY_MM format), XLOOKUP formulas for all 2026 months, data restoration for 2025 + Jan 2026, template creation for Feb-Dec 2026
- **Structure**: Monthly sheets with "Tracked Items" + "Total" columns (26 crime categories per sheet)
- **XLOOKUP on MoM Sheet**: Columns Q-AH reference individual month sheets directly (e.g., `'26_02'!$A:$A`)
- **Status**: All 11 remaining 2026 month templates created, formulas auto-update when data entered
- **Integration**: Structure compatible with future Power BI M code queries (similar to Detective workbook)
- **Documentation**: `docs/CSB_WORKBOOK_2026_SETUP_COMPLETE.md`, chatlog in `docs/chatlogs/claude_excel_csb_update/`

### v1.15.3 - Detective Queries Excel Structure Fix ✅
- **Complete Success** - Detective Division Power BI queries now import data correctly
- **Root Cause**: Excel structure differed from Claude Excel add-on's plan (historical YY-MMM data vs expected 2026-only MM-YY)
- **Three Critical Fixes**:
  1. **Date Parsing** - YY-MMM format parsing with month abbreviation lookup (`"Jan"` → 1, `"Feb"` → 2)
  2. **Rolling Window** - Dynamic 13-month calculation (was hardcoded to 2026-only, excluded all data)
  3. **Month Display** - Normalized YY-MMM to MM-YY format (`26-Jan` → `01-26` for visuals)
- **Additional Fix**: Row label exact matching for CCD query (double spaces in Excel)
- **Queries Updated**: `___Detectives` (40 categories), `___Det_case_dispositions_clearance` (10 dispositions)
- **Current Window**: Jan 2025 - Dec 2025 (will auto-show Jan 2026 when data entered)
- **Diagnostic Tools**: 4 Python scripts for workbook analysis and verification
- **Documentation**: 5 detailed guides including root cause analysis and deployment steps

### v1.15.2 - STACP Visual 13-Month Rolling Window Fixed ✅

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

---

*Last updated: 2026-02-13 | Format version: 3.7*