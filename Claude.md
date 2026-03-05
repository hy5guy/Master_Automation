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
- `scripts/summons_etl_normalize.py` - Summons ETL v2.3.0: badge enrichment, statute classification, 3-tier output (RAW/CLEAN/SLIM)
- `run_summons_etl.py` - Path-agnostic wrapper: `python run_summons_etl.py --month 2026_01`
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
- `m_code/` - Power BI M code queries (45 queries across 20 page-based subfolders)
 - `arrests/` - ___Arrest_Categories, ___Arrest_Distro, ___Top_5_Arrests
 - `benchmark/` - ___Benchmark
 - `chief/` - ___Chief2, ___chief_projects (table Raw_Input; was Table8)
 - `community/` - ___Combined_Outreach_All
 - `csb/` - ___CSB_Monthly
 - `detectives/` - ___Detectives, ___Det_case_dispositions_clearance
 - `drone/` - ___Drone
 - `esu/` - ESU_13Month
 - `functions/` - fnGetFiles, fnReadCsv, fnEnsureColumns, fnApplyRenameMap, fnLoadRaw
 - `nibrs/` - ___NIBRS_Monthly_Report
 - `overtime/` - ___Overtime_Timeoff_v3
 - `parameters/` - RootExportPath, EtlRootPath, SourceMode, RangeStart, RangeEnd, pReportMonth
 - `patrol/` - ___Patrol
 - `remu/` - ___REMU
 - `response_time/` - ___ResponseTimeCalculator
 - `shared/` - ___ComprehensiveDateTable, ___DimMonth, ___DimEventType, ___Arrest_Raw_Data_Preview, ___Arrest_Date_Distribution, Parameters_Check
 - `social_media/` - ___Social_Media
 - `ssocc/` - ___SSOCC_Data, TAS_Dispatcher_Incident
 - `stacp/` - ___STACP_pt_1_2, STACP_DIAGNOSTIC
 - `summons/` - summons_13month_trend, summons_top5_parking, summons_top5_moving, summons_all_bureaus, ___Summons
 - `traffic/` - ___Traffic
 - `training/` - ___Cost_of_Training, ___In_Person_Training
 - `archive/` - Archived M code versions (53+ superseded files)
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
- `docs/SUMMONS_VERIFICATION_NOTE_2026_03.md` - ⚠️ Re-export all summons to verify counts (2026-03-03)
- `docs/SUMMONS_ETL_v2.3.0_DEPLOYMENT.md` - v2.3.0 deployment guide (3-tier output, SLIM CSV, 6 M-code updates, multi-month loading, DOpus fallback)
- `docs/SOCIAL_MEDIA_MISSING_REFERENCES_FIX.md` - ___Social_Media Missing_References fix (table name _stacp_mom_sm)
- `docs/UNIFIED_EXPORT_AND_BACKFILL_LOCATIONS.md` - Proposal for unified export/backfill folder structure
- `docs/ARREST_DISTRO_LOAD_AND_UNKNOWN.md` - Load error vs unknown residence; resolution (2026-03-04)
- `docs/MONTHLY_ACCRUAL_COMPARISON_2026_03_03.md` - Pre vs post refresh, backfill comparison
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
- **ESU 13-month**: `docs/ESU_POWER_BI_LOAD_AND_PUBLISH.md`, `m_code/esu/README.md` (single query ESU_13Month.m; Status, ItemKey, Month_Year; workbook requirements)
- **M Code DateTime fix**: `docs/M_CODE_DATETIME_FIX_GUIDE.md` — audit table of all 20 affected files, ReportMonth parameter pattern, deployment checklist
- **Monthly report template**: `docs/MONTHLY_REPORT_TEMPLATE_WORKFLOW.md` — template location, monthly cycle steps, M code deployment checklist (49 queries)
- **Personnel schema**: `09_Reference/Personnel/Assignment_Master_SCHEMA.md` (auto-generated); `09_Reference/Standards/Personnel/assignment_master.schema.json`. Sync scripts in `09_Reference/Personnel/scripts/` (sync_assignment_master.py, fix_team_traffic.py); run `python scripts/sync_assignment_master.py` or `run_sync.bat` from Personnel root. Path-agnostic BASE_DIR — works on desktop (carucci_r) and laptop (RobertCarucci).
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
2. **Community Engagement** - `src/main_processor.py` (Patrol v2, attendee_names column)
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
- **Report Template**: `<OneDrive>\15_Templates\Monthly_Report_Template.pbix` (gold copy; update pReportMonth each cycle)
- **Monthly Reports**: `<OneDrive>\Shared Folder\Compstat\Monthly Reports\YYYY\MM_monthname\`

## Recent Updates (2026-03-05)

### Community Engagement ETL — Patrol Processor v2
- **Patrol processor v2** deployed in `02_ETL_Scripts\Community_Engagment`
  - Enhanced attendee parsing: rank stripping (PO/Sgt/Lt/Det/Cpl/Ofc), expanded delimiters ([,/&;] + "and"), non-name detection
  - New `attendee_names` column in combined output (comma-separated normalized names) for person-level analysis
  - Fallback logic: empty attendee field + valid event data → count=1
  - CSV/Excel export schema: `date`, `start_time`, `end_time`, `event_name`, `location`, `duration_hours`, `attendee_count`, `office`, `division`, `attendee_names`
- **Power BI M query** (`___Combined_Outreach_All.m`) remains backward compatible — ignores unknown columns
- **scripts.json** updated: Community Engagement output_patterns include `output\*.csv` for correct file discovery

---

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
- **Version**: 1.17.6
- **Status**: ✅ Template Updated — Staging Data Refresh Pending
- **Enabled Scripts**: 5 (All operational)
- **Power BI Queries**: 45+ queries loading cleanly; all use `pReportMonth` parameter
- **pReportMonth**: `#date(2026, 2, 1)` in both repo and template
- **M Code Baseline**: All 45 PBIX queries exported, split, headered (Jan 2026 monthly report)
- **Report Template**: Surgical edits complete — all queries load, Close & Apply succeeds with zero DAX errors
- **Staging Data Gap**: `summons_powerbi_latest.xlsx` only has data through Sep 2025; summons visuals empty for Jan 2026. Will populate after next ETL run
- **Personnel Master**: Assignment_Master_V3_FINAL.xlsx (25 cols, 166 records)
- **Phase 2 Status**: ALL TASKS COMPLETE (A-F) in repo. Template deployment COMPLETE.
- **Critical constraint**: Repo M code output schemas have diverged from PBIX DAX model. Cannot replace entire query bodies — only fix paths, DateTime.LocalNow(), and column types.
- **Laptop path junction**: `C:\Users\carucci_r` → `C:\Users\RobertCarucci` (Windows junction enables M code path compatibility between desktop and laptop)

---

## Recent Updates (2026-02-23)

### v1.17.5 — Surgical Template Update COMPLETE

All surgical edits applied successfully to the February 2026 Power BI template. Every query loads without errors and Close & Apply completes cleanly.

#### What was done:
- Created `pReportMonth` parameter (Date, 2/1/2026) in template
- Fixed file paths in 4 queries (`ESU_13Month`, `summons_top5_parking`, `summons_top5_moving`, `___ResponseTimeCalculator`)
- Replaced `DateTime.LocalNow()` with `pReportMonth` in 6 queries
- Re-created `___Summons` query (12 DAX measures referenced it but it was missing); added `TICKET_COUNT` and `ASSIGNMENT_FOUND` columns
- Added `Count` and `MonthName` columns to `___ResponseTimeCalculator` for DAX SUMMARIZE measures
- Fixed `summons_13month_trend`: removed non-existent columns, added `TICKET_COUNT`, deduplicated by `TICKET_NUMBER`
- Deleted 4 orphaned DAX calculated tables (`Arrests`, `Demographics`, etc.) referencing non-existent `Arrest_Top`

#### Pending:
- **Staging data refresh** — `summons_powerbi_latest.xlsx` only has data through Sep 2025. Summons visuals will populate once the ETL runs and refreshes the staging file with Oct 2025 – Jan 2026 data.
- `summons_top5_parking` uses `List.Max(YearMonthKey)` instead of `pReportMonth` — shows stale data until staging is refreshed

### v1.17.4 — Bulk M Code Paste Failed; Surgical Approach Executed
- Bulk paste broke DAX model (schema mismatch). All changes discarded. Surgical approach applied (v1.17.5).

---

## Recent Updates (2026-02-22)

### v1.17.3 — Template Refresh & Laptop Path Resolution

#### Report Template Refreshed from January 2026 Published Report
- **Old template** (`Monthly_Report_Template.pbix`) had cascading model-level errors after bulk M code paste — archived as `Monthly_Report_Template_ARCHIVED_2026_02_22.pbix` in `15_Templates\`
- **New template** copied from `Shared Folder\Compstat\Monthly Reports\2026\01_january\2026_01_Monthly_Report.pbix` — clean, error-free baseline with latest formatting and DAX model

#### Laptop Path Resolution — Windows Junction
- M code references `C:\Users\carucci_r\...` (desktop username); laptop has `C:\Users\RobertCarucci\...`
- Created Windows junction: `mklink /J C:\Users\carucci_r C:\Users\RobertCarucci`
- All M code data sources now resolve correctly on both machines without modifying M code files

#### M Code Folder Reorganization (v1.17.2)
- Expanded from 17 to 20 page-based subfolders: `remu/`, `chief/`, `social_media/` split out from patrol/community/stacp
- Visual export mapping updated to match new folder structure

---

## Recent Updates (2026-02-21)

### v1.17.1 — February 2026 Cycle Activation & Arrest Export .tab Support

#### pReportMonth Advanced to February 2026
- `m_code/parameters/pReportMonth.m` updated from `#date(2026, 1, 1)` to `#date(2026, 2, 1)`
- All 20 M code queries now filter for **January 2026** data (previous month from pReportMonth)
- `___Arrest_Categories` now finds 42 January 2026 records in `2026_01_Arrests_PowerBI_Ready.xlsx`
- `___Overtime_Timeoff_v3` confirmed populating correctly with pReportMonth parameter

#### Arrest Export .tab File Conversion
- Lawsoft exports arrive as `.tab` (tab-delimited, no headers) — ETL only searches for `*.xlsx`
- Converted `2026_02_Lawsoft_Monthly_Arrest.tab` (39 records, Feb 1–9) to `2026_02_LAWSOFT_ARREST.xlsx` with column headers from January export
- Column headers: Address, Age, Arrest Date, blank, Case Number, Charge, DOB, JuvenileFlag, Name, Officer of Record, Place of Arrest StNumber, Place of Arrest Street, Race, ReportCalcSummary, Reviewed, Sex, SS#Calc, UCR #
- February export is partial (Feb 1–9); full month export needed at month-end for March cycle

#### Arrest ETL File Discovery Note
- `arrest_python_processor.py` always targets **previous month** (Jan 2026 from today's date)
- Picks latest `.xlsx` by modification time — may grab wrong month's file if multiple exist
- Workaround: ensure target month's file is most recently modified, or run before adding next month's export

### v1.17.0 — M Code Reorganization and PBIX Baseline Export

#### M Code Folder Restructure
- **17 page-based subfolders** created under `m_code/`: arrests, benchmark, community, csb, detectives, drone, esu, functions, nibrs, overtime, parameters, patrol, response_time, shared, ssocc, stacp, summons, traffic, training
- **45 queries** — 25 data queries, 5 parameters, 5 shared functions, 5 ESU helpers, 5 other
- **53 stale files archived** to `m_code/archive/2026_02_21_phase2_cleanup/` (date-stamped snapshots, `_FIXED`/`_STANDALONE` variants, benchmark iterations)

#### PBIX Baseline Export
- All 45 Power Query M code queries extracted from `2026_01_Monthly_Report.pbix`
- Consolidated into `all_m_code_26_january_monthly.m` (4,197 lines)
- Split into individual `.m` files with standardized headers (timestamp, path, Author: R. A. Carucci, purpose)
- Splitter script: `scripts/split_mcode.py`

#### Phase 2 Discovery
- PBIX already has `RootExportPath` and `EtlRootPath` parameters (reuse for Phase 2 path portability)
- PBIX has `RangeStart`/`RangeEnd` parameters (may complement `pReportMonth`)
- 7 queries have broken hardcoded paths: 4 use `C:\Users\RobertCarucci\...`, 2 use `C:\Dev\...`
- 6 queries show warning icons: `___Drone`, `___ResponseTimeCalculator`, `summons_13month_trend`, `summons_top5_parking`, `summons_top5_moving`, `ESU_13Month`

#### Phase 2 Tasks B, D, E — Completed
- **Pre_Flight_Validation.py** rewritten: argparse `--report-month YYYY-MM`, path_config portability, visual export mapping validation (36 mappings, 25 enforced), evidence checks (file size, row count), GO/NO-GO JSON gate, personnel updated to V3_FINAL.xlsx
- **response_time_fresh_calculator.py** v3.1.0: argparse, path_config, first-arriving unit dedup fix (sort by Time Out)
- **summons_derived_outputs_simple.py**: argparse, path_config, dynamic YYYY_MM filenames, IS_AGGREGATE + TICKET_COUNT columns, optional input warnings
- **process_cad_data_13month_rolling.py**: corrupted workspace copy replaced with redirect stub
- **Phase 2 remaining**: Task A (M code ReportMonth freeze — 13 files), Task C (orchestrator manifest)

#### Phase 2 Tasks A, C — Completed (Final)
- **pReportMonth parameter** created at `m_code/parameters/pReportMonth.m` — update once per monthly cycle
- **20 M code files fixed** — 25 `DateTime.LocalNow()` occurrences replaced with `ReportMonth = pReportMonth` binding; covers overtime, training, esu, stacp, detectives, ssocc, traffic, drone, csb, shared, arrests, summons, community
- **9 hardcoded paths fixed** — `C:\Users\RobertCarucci` (6 files) and `C:\Dev` (1 file) replaced with correct `C:\Users\carucci_r` OneDrive paths
- **Orchestrator manifest** — `run_all_etl.ps1` accepts `-ReportMonth YYYY-MM`, writes `_manifest.json` + `_manifest.csv` to `_DropExports`
- **Phase 2 Remediation COMPLETE** — All tasks A-F finished

---

## Recent Updates (2026-02-20)

### v1.16.0 — Phase 2 Diagnostics, Assignment_Master V3, Schema Standards

#### M Code DateTime.LocalNow() — Critical Architectural Issue Identified
- **Root Cause**: 20 M code files (35+ occurrences) use `DateTime.LocalNow()` to compute rolling windows; refreshing a January 2026 report in March shifts the window forward and loses Jan 2025 data
- **Fix**: Add `ReportMonth = #date(YYYY, M, 1)` at top of each query; replace `DateTime.LocalNow()` with `DateTime.From(ReportMonth)`
- **Affected files**: `___Overtime_Timeoff_v3`, `___Arrest_Categories_FIXED`, `___Top_5_Arrests_FIXED`, `___Cost_of_Training`, `esu/ESU_13Month`, `esu/MonthlyActivity`, `stacp/STACP_pt_1_2_FIXED`, `detectives/___Detectives_2026`, `detectives/___Det_case_dispositions_clearance_2026`, `___Summons_All_Bureaus_STANDALONE`, `___Summons_Top5_Moving_STANDALONE`, `2026_02_16_detectives`, `2026_02_19_jan_m_codes` (15+ occurrences)
- **Guide**: `docs/M_CODE_DATETIME_FIX_GUIDE.md` — full audit table, Claude AI fix prompt, deployment checklist

#### Assignment_Master V3 — Major Cleanup (Claude-in-Excel, 12 turns)
- **V3_FINAL.xlsx**: 42 cols → 25 cols; 6 duplicate PEO rows deleted; 166 records; RANK 100% populated
- **Renamed**: `POSS_CONTRACT_TYPE` → `CONTRACT_TYPE`, `Proposed 4-Digit Format` → `STANDARD_NAME`
- **Script fix**: `run_summons_with_overrides.py` — removed `WG5` key, renamed `POSS_CONTRACT_TYPE` → `CONTRACT_TYPE` in badge 1711 override
- **Archived**: `add_traffic_officers.py` → `scripts/_archive/` (deprecated; officers already added, referenced deleted columns)

#### Schema Standards Infrastructure
- `09_Reference/Personnel/Assignment_Master_SCHEMA.md` fully rewritten (V2 — all 16 sections)
- `09_Reference/Standards/Personnel/` subdirectory created
- `09_Reference/Standards/Personnel/Assignment_Master_SCHEMA.md` — human/AI-readable mirror
- `09_Reference/Standards/Personnel/assignment_master.schema.json` — formal JSON Schema (type/enum/pattern for all 25 columns)

---

## Recent Updates (2026-02-14)

### v1.15.6 - Benchmark Power BI Diagnostics & Handoff
- **Handoff doc** – `docs/BENCHMARK_VISUALS_HANDOFF_PROMPT.md` for AI-assisted troubleshooting (matrix/donut/line chart broken)
- **Benchmark consolidation** – Moved 02_06 CSVs from archive to 05_EXPORTS\Benchmark; removed old 01_07
- **DAX fix** – BM_YoY_Change (DATEADD → EDATE for scalar dates)
- **Benchmark docs** – README merge, CHANGELOG, SUMMARY, ___Benchmark_FIXED.m, ___DimMonth_dynamic.m, Benchmark_DAX_Measures.dax in 02_ETL_Scripts\Benchmark
- **Status**: Visuals still showing zeros for most months; handoff enables continuation

### v1.15.7 - Benchmark Source Data Diagnostic (Scenario B Confirmed)
- **Diagnostic run** – `scripts/diagnose_benchmark_data.py` run against `05_EXPORTS\Benchmark` (default path).
- **Result**: **Scenario B** — source CSVs have good multi-month coverage (use_force 61, show_force 22, vehicle_pursuit 11 months); dates beyond Jan 2025 present; no over-concentration in one month.
- **Conclusion**: Issue is in **Power BI** (MonthStart, model relationships, or date types), not in source data.
- **Next steps**: See `docs/BENCHMARK_VISUAL_DIAGNOSTIC.md` steps 3, 5, 7; handoff prompt `docs/BENCHMARK_VISUALS_HANDOFF_PROMPT.md`.

---

## Recent Updates (2026-02-16)

### v1.15.8 - Policy Training: Cost of Training 13-month window & In-Person doc
- **Cost of Training M code** – `m_code/___Cost_of_Training.m`: 13-month rolling window (01-25 through 01-26); filter to previous month / same month one year earlier.
- **Policy Training doc** – `docs/POLICY_TRAINING_AUTOMATION_AND_COST_VISUAL.md`: where ETL runs, how to run, why 01-26 missing, In-Person Training visual and source cost (zeros when source has no cost; ETL **Cost Per Attendee** alias in Policy_Training_Monthly ETL for imputation).

---

## Recent Updates (2026-02-13)

### v1.15.5 - Visual Export Config Gemini Enhancement ✅
- **Gemini config merge** - Merged metadata from `gemini_visual_export_config logic.json` into `visual_export_mapping.json`
- **backfill_folder override** - Mappings can specify `backfill_folder` for Backfill path (overrides `target_folder` for copy only)
- **Monthly Accrual fix** - `backfill_folder: "vcs_time_report"` so Overtime/TimeOff finds file in `Backfill/YYYY_MM/vcs_time_report/`
- **New visuals** - Officer Summons Activity, SSOCC TAS Alerts; Chief's Projects alias
- **Docs**: `docs/VISUAL_EXPORT_CONFIG_GEMINI_ENHANCEMENT.md`, FAQ updated

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

*Last updated: 2026-03-05 | Format version: 3.12*

## Recent Updates (2026-02-18)

### v1.15.9 - February 2026 ETL Cycle Response Times Fix ✅ **DEPLOYED**

**Response Time Calculation Methodology Fixed** - Critical multi-unit deduplication logic corrected

#### Critical Response Time Fixes:
1. **Multi-Unit Deduplication Logic** - Fixed script to use first-arriving unit instead of first-in-file
   - **Before**: `df.drop_duplicates(subset=['ReportNumberNew'], keep='first')` (file order)
   - **After**: Sort by `['ReportNumberNew', 'Time Out']` then deduplicate (first arriving)
   - **Impact**: Ensures accurate response times for multi-unit incidents
   - **File**: `02_ETL_Scripts/Response_Times/process_cad_data_13month_rolling.py`

2. **Response Time Metric Clarification** - Defined three distinct metrics
   - **Response Time (Primary)**: `Time Out - Time of Call` (total time from call to arrival)
   - **Travel Time**: `Time Out - Time Dispatched` (dispatch to arrival)
   - **Processing Time**: `Time Dispatched - Time of Call` (call to dispatch)
   - **Standard**: Use first-arriving unit for multi-unit incidents

3. **CAD Call Type Mapping** - Fixed mapping file structure
   - **Created**: `CAD_CALL_TYPE.xlsx` from `CallType_Categories.csv`
   - **Schema**: Columns renamed to match script expectations (`Call Type`, `Response`)
   - **Records**: 649 call type mappings for Response_Type classification

#### January 2026 Response Time Results:
- **Emergency**: 3:11 min (347 calls, median 2:49)
- **Urgent**: 2:54 min (843 calls, median 2:32)
- **Routine**: 2:48 min (853 calls, median 2:02)
- **Processing Stats**: 10,440 → 7,501 → 2,851 → 2,043 valid records
- **Multi-unit Rate**: 28.2% (2,939 duplicate units removed)

#### February 2026 ETL Cycle Validation:
- **Infrastructure Validation**: ✅ Python 3.14.2, dependencies verified
- **Visual Export Mapping**: ✅ 25/36 visuals enforce 13-month windows (better than expected 24/32)
- **Source Data**: ✅ January 2026 CAD timereport (10,440 records), E-Ticket missing (backfill available)
- **Pre-Flight Checks**: ✅ All critical dependencies validated
- **Output Generation**: ✅ Response time calculations successful with corrected methodology

#### Documentation Created:
- **Response Time Analysis PDFs**: Executive summaries showing multi-unit impact (+27% to +120% on Routine)
- **ETL Cycle Validation**: Comprehensive pre-flight audit and validation framework
- **Methodology Documentation**: First-arriving unit standard for multi-unit incidents
- **Safeguards**: Monthly multi-unit rate audits and validation checks against raw CAD

#### Tools and Scripts Enhanced:
- `process_cad_data_13month_rolling.py` - Fixed deduplication logic
- `CAD_CALL_TYPE.xlsx` - Created proper mapping file from CSV source
- Pre-flight validation framework for monthly ETL cycles
- Visual export processing with 13-month window enforcement

**Status**: Response Times ETL workflow operational with corrected methodology ✅

---

## Recent Updates (2026-02-17)

- Consolidated Power BI visual export mapping into one canonical file
- Primary path: `Standards\config\powerbi_visuals\visual_export_mapping.json`
- Archived prior mapping files under `scripts\_archive\visual_export_mapping\2026_02_17_173019\`
