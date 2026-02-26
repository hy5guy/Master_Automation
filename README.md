# Master ETL Automation

Centralized automation hub for running all Python ETL scripts that feed into Power BI reports.

## Overview

This directory orchestrates all Python data processing scripts from various workspaces and manages their output to the Power BI Date repository. 

**Latest Update (2026-02-26)**: v1.17.9 — Summons M code fixes: removed TICKET_NUMBER dependency (not in current ETL schema), added PATROL BUREAU → PATROL DIVISION consolidation. Restored staging file from today's ETL. Known data gaps: Traffic Bureau +74M/+518P vs submitted (PEO additions not yet in ETL); Detective Bureau discrepancy under investigation. OT/TO 7-25/8-25 drift is from retroactive raw-data additions (more accurate, not a bug).

## Directory Structure

```
Master_Automation/
├── README.md                    # This file
├── CHANGELOG.md                 # Version history and updates
├── SUMMARY.md                   # Project summary / quick reference
├── Claude.md                    # AI assistant guide
├── verify_migration.ps1         # Automated verification script
├── Master_Automation.code-workspace  # VS Code workspace
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python deps (pandas, openpyxl) for validation & Summons backfill
├── config/
│   ├── scripts.json            # Configuration for all ETL scripts
│   ├── response_time_filters.json  # Response Time filter configuration
│   └── scripts.json.bak        # Backup of previous config
├── scripts/
│   ├── run_all_etl.ps1         # PowerShell orchestrator (supports dynamic arguments)
│   ├── run_all_etl.bat         # Batch file orchestrator
│   ├── run_etl_script.ps1      # Helper script to run individual scripts
│   ├── path_config.py          # Centralized get_onedrive_root() for portability (env var support)
│   ├── Pre_Flight_Validation.py          # Pre-flight GO/NO-GO gate (argparse, evidence checks, mapping validation)
│   ├── summons_derived_outputs_simple.py  # Summons derived outputs (argparse, dynamic filenames, IS_AGGREGATE)
│   ├── overtime_timeoff_with_backfill.py     # Overtime/TimeOff monthly wrapper (v10 + backfill)
│   ├── validate_exports.py                  # Pre-flight OT/TimeOff export validation
│   ├── validate_outputs.py                   # FIXED CSV schema validation
│   ├── test_pipeline.bat                     # Overtime/TimeOff test suite
│   ├── summons_backfill_merge.py             # Summons gap-month merge (03-25, 07-25, 10-25, 11-25)
│   ├── normalize_visual_export_for_backfill.py  # Normalize visual exports (13-month window, backfill)
│   ├── process_powerbi_exports.py               # Process _DropExports with mapping (match_pattern, 13-month)
│   ├── validate_13_month_window.py              # Validate 13-month rolling window in CSV(s)
│   ├── restore_fixed_from_backfill.py        # Restores history into FIXED_monthly_breakdown
│   ├── compare_vcs_time_report_exports.py    # Diff tool for visual exports/backfill validation
│   ├── compare_policy_training_delivery.py   # Policy Training: visual vs ETL/backfill diff
│   ├── compare_summons_deptwide.py           # Summons Dept-Wide: visual vs ETL/backfill diff
│   ├── diagnose_summons_blank_bureau.py      # Summons: find blank WG2 (Bureau) rows
│   ├── diagnose_benchmark_data.py            # Benchmark: analyze source CSVs (date coverage, scenario A/B/C)
│   ├── run_summons_with_overrides.py         # Summons: run with injected badge overrides
│   └── _testing/                             # Benchmark and debug scripts
├── docs/                        # Project documentation (migration, verification, guides)
│   ├── response_time/          # Response Time documentation and reports
│   ├── archived_workflows/     # Archived workflow files
│   ├── DESKTOP_CONFIGURATION_TROUBLESHOOTING.md  # Desktop setup and troubleshooting guide
│   ├── FEBRUARY_2026_ETL_CYCLE_SUMMARY.md  # Complete ETL cycle execution results
│   ├── chatlogs/               # Session transcripts and troubleshooting logs
│   └── (migration guides, verification reports, troubleshooting docs)
├── m_code/                      # Power BI M code queries (45 queries, 20 page folders)
│   ├── arrests/               # ___Arrest_Categories, ___Arrest_Distro, ___Top_5_Arrests
│   ├── benchmark/             # ___Benchmark
│   ├── chief/                 # ___Chief2, ___chief_projects
│   ├── community/             # ___Combined_Outreach_All
│   ├── csb/                   # ___CSB_Monthly
│   ├── detectives/            # ___Detectives, ___Det_case_dispositions_clearance
│   ├── drone/                 # ___Drone
│   ├── esu/                   # ESU_13Month
│   ├── functions/             # fnGetFiles, fnReadCsv, fnEnsureColumns, fnApplyRenameMap, fnLoadRaw
│   ├── nibrs/                 # ___NIBRS_Monthly_Report
│   ├── overtime/              # ___Overtime_Timeoff_v3
│   ├── parameters/            # RootExportPath, EtlRootPath, pReportMonth, SourceMode, RangeStart, RangeEnd
│   ├── patrol/                # ___Patrol
│   ├── remu/                  # ___REMU
│   ├── response_time/         # ___ResponseTimeCalculator
│   ├── shared/                # ___ComprehensiveDateTable, ___DimMonth, ___DimEventType, etc.
│   ├── social_media/          # ___Social_Media
│   ├── ssocc/                 # ___SSOCC_Data, TAS_Dispatcher_Incident
│   ├── stacp/                 # ___STACP_pt_1_2, STACP_DIAGNOSTIC
│   ├── summons/               # summons_13month_trend, top5_parking/moving, all_bureaus, etc.
│   ├── traffic/               # ___Traffic
│   ├── training/              # ___Cost_of_Training, ___In_Person_Training
│   └── archive/               # Archived/old M code versions
├── outputs/                     # Organized output files
│   ├── arrests/                # Arrest-related exports
│   ├── visual_exports/         # Power BI visual exports
│   ├── summons_validation/     # Summons testing data
│   ├── metadata/               # Configuration and verification metadata
│   ├── community_engagement/   # Community engagement data
│   ├── misc/                   # Miscellaneous output files
│   └── large_exports/          # Large Excel exports
├── verifications/               # ETL verification framework
│   ├── reports/                # Verification markdown reports
│   ├── etl_verification_framework.py
│   ├── arrests_verifier.py
│   ├── overtime_timeoff_verifier.py
│   └── run_all_verifications.py
└── logs/
    └── .gitkeep                # ETL execution logs go here (auto-created)
```

## Quick Start

### Python environment

The orchestrator runs Python scripts using the executable in `config/scripts.json` (`python_executable`). That environment must have `pandas` and `openpyxl` for pre-flight validation and Summons backfill. From the repo root:

```powershell
pip install -r requirements.txt
```

### Run All ETL Scripts

**PowerShell (Recommended):**
```powershell
cd C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation
.\scripts\run_all_etl.ps1
```

**Batch File:**
```batch
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
scripts\run_all_etl.bat
```

### Run Specific Script

```powershell
.\scripts\run_etl_script.ps1 -ScriptName "Arrests"
```

### Preview Execution (Dry Run with Validation)

Preview what would execute and validate required input files:

```powershell
.\scripts\run_all_etl.ps1 -DryRun
```

This will:
- Show which scripts would execute
- Validate that required export files exist (e-ticket exports, CAD exports, etc.)
- Report any missing files before execution

## Configuration

Edit `config/scripts.json` to add, remove, or modify ETL scripts:

```json
{
  "scripts": [
    {
      "name": "Arrests",
      "path": "C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\02_ETL_Scripts\\Arrests",
      "script": "arrest_python_processor.py",
      "enabled": true,
      "output_to_powerbi": true,
      "order": 1
    },
    {
      "name": "Community Engagement",
      "path": "C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\02_ETL_Scripts\\Community_Engagment",
      "script": "deploy_production.py",
      "enabled": true,
      "output_to_powerbi": true,
      "order": 2
    },
    {
      "name": "Overtime TimeOff",
      "path": "C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\Master_Automation\\scripts",
      "script": "overtime_timeoff_with_backfill.py",
      "enabled": true,
      "output_to_powerbi": false,
      "order": 3
    }
  ]
}
```

## Features

- **Sequential Execution:** Runs scripts in specified order
- **Error Handling:** Continues on errors, logs failures
- **Logging:** Detailed logs for each script execution
- **Power BI Integration:** Automatically copies outputs to Power BI drop folder
- **Selective Execution:** Run all, or specific scripts
- **Status Reporting:** Summary of what succeeded/failed
- **Input Validation:** Validates required export files exist before execution (`-ValidateInputs` or automatic with `-DryRun`)
- **Dry Run Mode:** Preview execution without running scripts (`-DryRun`)

## Workflow

1. **Configure:** Edit `config/scripts.json` with your script paths
2. **Run:** Execute `run_all_etl.ps1` or `run_all_etl.bat`
3. **Process:** Scripts execute in order, outputs logged
4. **Integrate:** Successful outputs copied to Power BI Date repository
5. **Review:** Check logs for any failures or warnings

## Output Integration

All successful outputs are automatically:
1. Validated (CSV format, proper structure)
2. Copied to `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports\`
3. Ready for `organize_backfill_exports.ps1` processing

## Logging

Logs are saved to:
- `logs/YYYY-MM-DD_HH-MM-SS_ETL_Run.log` - Overall execution log
- `logs/YYYY-MM-DD_HH-MM-SS_[ScriptName].log` - Individual script logs

## Error Handling

- Scripts run independently (failure of one doesn't stop others)
- Errors logged with details
- Summary report shows success/failure status
- Failed scripts can be re-run individually

## Recent Updates

### 2026-02-09: v1.12.0 - Response Time Backfill Baseline Established ✅

**Backfill Structure Created** - Formal baseline for Response Time data established

#### What Was Done:
- **Backfill Directory Structure Created** - 13 monthly directories (Jan 2025 - Jan 2026)
  - Location: `PowerBI_Date\Backfill\YYYY_MM\response_time\`
  - Files: `YYYY_MM_Average_Response_Times__Values_are_in_mmss.csv`
  - Each file: 3 rows (Emergency, Routine, Urgent) + header
  - Source: Current validated visual export data

- **M Code Updated to v2.8.3** - Restored Backfill priority
  - Priority: Backfill > visual_export > outputs > _DropExports
  - Ensures loading of validated data with January 14 methodology
  - Maintains compatibility with fallback sources

- **Fresh Calculator Disabled** - Marked as experimental
  - Set `enabled: false` in `config\scripts.json`
  - Reason: Missing January 14 deduplication/filtering logic
  - Script available for future enhancement: `scripts\response_time_fresh_calculator.py`

#### October 2025 Baseline Values:
| Type | Value | Source |
|------|-------|--------|
| Emergency | 02:49 | Validated backfill |
| Routine | 02:11 | Validated backfill |
| Urgent | 02:52 | Validated backfill |

#### Monthly Workflow Established:
1. Run ETL for new month
2. Refresh Power BI
3. Export Response Time visual to CSV
4. Save to: `Backfill\YYYY_MM\response_time\YYYY_MM_Average_Response_Times__Values_are_in_mmss.csv`
5. Next month: Power BI automatically picks it up

#### Documentation Created:
- `docs/RESPONSE_TIME_v2.8.3_BACKFILL_RESTORE.md` - Revert decision guide
- `docs/BACKFILL_BASELINE_CREATED_2026_02_09.md` - Baseline creation details
- `docs/RESPONSE_TIME_COMPLETE_SESSION_SUMMARY_2026_02_09.md` - Complete summary
- `docs/RESPONSE_TIME_FINAL_STATUS_2026_02_09.md` - Final status checklist

**Status:** Backfill baseline established, validated data preserved, monthly workflow documented

---

### 2026-02-09: v1.11.0 - Response Time Power BI M Code Fixed (31% Error Rate → 0%) ✅ **DEPLOYED**

**Critical Power BI Fix** - Response Time query fully operational with 0% errors! **PRODUCTION DEPLOYED ✅**

#### Power BI M Code Fix (v2.8.0):
- **Response Time Calculator Query** - Fixed 31% type conversion errors
  - Root cause: `type text` annotation in `Table.TransformColumns` conflicted with Power Query auto-typing
  - Fixed decimal precision handling (2.87, 2.92 now convert correctly to MM:SS format)
  - Added `Response_Time_MMSS` to final `Typed` step for explicit column typing
  - Enhanced error handling with `try...otherwise "00:00"` wrapper
  - Fixed unpivot column reference issue (MM-YY vs Month-Year)
  - All time formats now supported: MM:SS, M:SS, HH:MM:SS, decimal minutes (1.3, 2.87, 2.92)
  - Query now achieves 100% valid data (down from 69% valid, 31% errors)
  - **Tested with production data**: Wide format (Response Times by Priority.csv) and Long format (Average Response Times.csv) both working perfectly

### 2026-02-09: v1.10.0 - Master Automation 100% Operational - All Workflows Fixed ✅

**Complete Success** - All 6 ETL workflows now operational with 100% success rate!

#### Critical Fixes:
1. **Overtime TimeOff Fixed** - Resolved missing personnel file dependency
   - Copied `Assignment_Master_V2.csv` to Master_Automation root
   - Script now successfully processes all 30 output files in 19.92 seconds
   
2. **Response Times ETL Fixed** - Migrated to timereport hybrid strategy (v2.1.0)
   - Updated from archived `response_time` path to new `timereport` structure
   - Implemented hybrid loading: yearly + monthly files
   - Successfully processes 124,510 records → 22,655 filtered records
   - Generates 13 monthly CSVs (Jan 2025 - Jan 2026) in 76 seconds
   
3. **Response Times Power BI Fixed** - M code query type conversion errors resolved (v2.8.0)
   - Fixed 31% type conversion errors in `Response_Time_MMSS` column
   - All decimal values (1.3, 2.87, 2.92) now convert correctly to MM:SS format
   - Column quality: 100% valid (up from 69%)
   
3. **Benchmark Directory Cleanup** - Consolidated duplicate directories
   - Simplified from complex nested structure to flat `show_force`, `use_force`, `vehicle_pursuit`
   - Created new M code query with automatic latest file selection
   - Archived old structure for reference

#### Execution Results:
- **Success Rate:** 100% (6/6 workflows operational)
- **Execution Time:** 2.04 minutes (129.9 seconds)
- **Files Generated:** 60 total output files
- **Monthly Report:** `2026_01_Monthly_FINAL_LAP.pbix` successfully saved

#### Workflow Performance:
| Workflow | Status | Time | Files |
|----------|--------|------|-------|
| Arrests | ✅ Success | 6.27s | 2 |
| Community Engagement | ✅ Success | 7.86s | 2 |
| Overtime TimeOff | ✅ Success | 19.92s | 30 |
| Response Times | ✅ Success | 76.09s | 15 |
| Summons | ✅ Success | 2.06s | 7 |
| Summons Derived | ✅ Success | 8.66s | 4 |

#### Documentation Created:
- `docs/SESSION_2026_02_09_COMPLETE_SUCCESS.md` - Complete session summary
- `docs/RESPONSE_TIME_TIMEREPORT_MIGRATION_2026_02_09.md` - Timereport migration guide
- `docs/BENCHMARK_CLEANUP_STRATEGY_2026_02_09.md` - Benchmark consolidation guide
- `docs/FINAL_GO_NO_GO_DECISION_2026_02_09.md` - Pre-run decision analysis

**Status:** All systems operational and ready for February 2026 processing

---

### 2026-02-09: v1.9.0 - Response Times Source Migration & Validation Updates ✅
- **Response Times Source Path Updated**
  - Updated validation logic in `run_all_etl.ps1` to support new CAD source location
  - Source moved from `05_EXPORTS\_CAD\monthly_export` to `05_EXPORTS\_CAD\timereport`
  - Added support for monthly folder structure: `timereport/monthly/YYYY_MM_timereport.xlsx`
  - Added fallback support for year-based structure: `timereport/YYYY/YYYY_MM_Monthly_CAD.xlsx`
  - Enhanced error messages to show all checked paths and list available files
- **Validation Improvements**
  - Dry-run now correctly validates Response Times Monthly Generator inputs
  - Clear error messages when files are missing (shows both primary and fallback paths checked)
  - Lists available files in monthly folder when expected file not found
- **Directory Structure Best Practices Documented**
  - Recommendation: Keep monthly and yearly exports separated in different subfolders
  - Prevents overlap and double-count risk (same pattern for Arrests)
  - Maintains clean data lineage and reduces duplicate data issues
- **Automation Execution Model Clarified**
  - Sequential execution confirmed (not parallel)
  - One script failure does not stop remaining scripts
  - Parallel execution noted as future enhancement only
- **Comprehensive Documentation Created**
  - `IMPLEMENTATION_CHECKLIST_2026_02_09.md` - Complete implementation guide
  - `RESPONSE_TIME_TIMEREPORT_MIGRATION_2026_02_09.md` - Detailed migration docs
  - `RESPONSE_TIME_FILE_NAMING_RECONCILIATION_2026_02_09.md` - File naming analysis
  - `QUICK_REFERENCE_2026_02_09.md` - Quick reference for key commands and patterns
  - `IMPLEMENTATION_COMPLETE_2026_02_09.md` - Status summary
- **Testing Validated**
  - Dry-run test successful: Response Times Monthly Generator inputs found ✅
  - File discovered at: `timereport/monthly/2026_01_timereport.xlsx`
- **Pending Work**
  - Python script updates for new timereport path (pending review)
  - Power BI M query decision: direct read from timereport vs keep current Backfill flow
  - Arrests directory structure review and potential updates
- **Status:** Validation layer complete, Python scripts pending update

### 2026-02-05: December 2025 Power BI Visual Export Processing & Diagnostics ✅
- **December 2025 Visual Exports Organized**
  - Processed and organized 36 CSV exports from December 2025 Power BI report
  - Added `2025_12_` prefix to all exported files
  - Organized 53 total files into 16 categories in `PowerBI_Date\Backfill\2025_12\`
  - Cleaned `_DropExports\` folder for next monthly export
- **Critical Data Quality Issues Identified**
  - Issue #1: "Engagement Initiatives by Bureau" - Blank export (expected 22 events, 71 attendees)
  - Issue #2: "Chief's Projects & Initiatives" - Blank export
  - Issue #3: "Department-Wide Summons" - Missing 4 months of 2025 data (03-25, 07-25, 10-25, 11-25)
  - Root cause: Date filters using `TODAY()` or relative date logic in Power BI visuals
- **Comprehensive Diagnostic Reports Created**
  - `DECEMBER_2025_VISUAL_EXPORT_DIAGNOSTIC_REPORT.md` - Complete analysis of all issues
  - `ENGAGEMENT_INITIATIVES_BLANK_EXPORT_INVESTIGATION.md` - Technical troubleshooting guide
  - `DECEMBER_2025_EXPORT_QUICK_SUMMARY.md` - Quick reference action guide
  - Documented 4 fix options with DAX/M code examples
  - Created export validation checklist for future use
- **Files Organized:**
  - Arrests (3 files), Summons (11 files), Response Time (10 files)
  - Community Engagement (2 files), Use of Force (3 files), NIBRS (2 files)
  - Patrol (1 file), Traffic (4 files), Detective (4 files)
  - Crime Suppression (1 file), Training (2 files), Records (1 file)
  - Safe Streets (2 files), Drones (2 files), School (2 files), Chief (3 files)
- **Status:** Files organized, issues documented, fixes pending in Power BI

### 2026-02-04: v1.8.0 - Major Directory Consolidation & Cleanup ✅
- **Root Directory Cleanup**
  - Reduced from 91 files to 7 essential files (92% reduction)
  - Organized 84 files into appropriate subdirectories
  - Deleted 50 temporary Claude Code marker files
  - Deleted 6 unnecessary temporary files
- **Directory Consolidation**
  - Merged `output/` → `outputs/` (eliminated duplicate directory)
  - Merged `verification_reports/` → `verifications/reports/`
  - Created organized subdirectory structure under `outputs/`
  - Maintained `m_code/` in root for Power BI query access
- **Documentation Consolidation**
  - Merged README, CHANGELOG, SUMMARY versions (desktop + laptop)
  - Deleted 4 redundant documentation files
  - Created comprehensive cleanup and consolidation reports
- **New Directory Structure:**
  - `docs/response_time/` - Response Time docs (13 files)
  - `outputs/arrests/`, `outputs/visual_exports/`, `outputs/summons_validation/`, etc.
  - `verifications/reports/` - Verification reports (2 files)
  - `scripts/_testing/` - Benchmark/debug scripts (4 files)
- **Updated Documentation:**
  - Updated `.gitignore` for new structure
  - Updated `verifications/README.md`
  - Created 6 new documentation files in `docs/`
- **Status:** Professional directory structure, zero data loss, all files preserved

### 2026-01-14: v1.7.0 - Response Time ETL Enhanced Filtering ✅
- **Response Time ETL Enhanced Filtering**
  - Updated `response_time_monthly_generator.py` to v2.0.0
  - Added JSON configuration file (`config/response_time_filters.json`) for centralized filter rules
  - Added "How Reported" filter - excludes "Self-Initiated" records from response time calculations
  - Added Category_Type filtering with inclusion override logic (14 incidents kept despite category exclusion)
  - Added specific incident filtering (42 incidents excluded from non-filtered categories)
  - Added comprehensive data verification step with quality checks
  - Processing pipeline expanded from 6 steps to 12 steps for enhanced filtering
  - Added `--config` command line argument for custom filter configuration path
- **Status:** Enhanced filtering system with improved data quality controls
- See [docs/CHANGELOG.md](docs/CHANGELOG.md) for full details

### 2026-01-14: v1.5.0 - Summons ESU Organizational Update ✅
- **Fixed Summons ESU organizational structure**
  - Updated Assignment_Master_V2.csv: OFFICE OF SPECIAL OPERATIONS now maps to PATROL BUREAU
  - Updated 4 officers (RYAN CONLON 354, MASSIMO DIMARTINO 144, JOHN KNAPP 141, DANE MARBLE 271)
  - ESU (OFFICE OF SPECIAL OPERATIONS) totals now correctly combined with Patrol Division
  - Updated summons_all_bureaus.m M code to combine ESU with Patrol Division
  - Fixed M code syntax errors (removed invalid backslashes, fixed file path formatting)
- **Status:** ESU now part of Patrol Division, totals combined correctly
- See [docs/CHANGELOG.md](docs/CHANGELOG.md) for full details

### 2025-12-12: Summons Troubleshooting & Fixes ✅
- **Comprehensive diagnostic and troubleshooting completed**
  - Created troubleshooting guide: `claude_code_summons.md`
  - Diagnosed and resolved all Power BI issues (WG2, missing columns, DAX measures)
  - Verified M Code queries working correctly
  - Fixed DAX measure: `___Total Tickets = COUNTROWS('___Summons')`
  - Created diagnostic scripts for ongoing maintenance
- **Status:** All issues resolved - system healthy and working correctly
- **Action Required:** Update DAX measure in Power BI Desktop (2 minutes)

### 2025-12-11: Migration to OneDrive Complete ✅

### Migration to OneDrive Complete ✅
- **PowerBI_Date** moved from `C:\Dev\PowerBI_Date_Merged` to OneDrive location
- All path references updated in configuration and scripts
- Master_Automation junction created for seamless integration
- Verification scripts and documentation added

### New Files Added
- `verify_migration.ps1` - Automated verification script
- `CHANGELOG.md` - Version history
- Documentation moved under `docs/` (migration + verification + guides)

### Configuration Updates
- `powerbi_drop_path` updated to: `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports`
- All script paths verified and updated
- Documentation paths corrected

### Verification
Run `.\verify_migration.ps1` to verify all paths and configurations are correct.

### Overtime TimeOff: Backfill + Processed Month Now Stable ✅
- The Power BI visual requires **two sources** to be fully populated for the 13-month view:
  - `...\Overtime_TimeOff\output\FIXED_monthly_breakdown_*.csv` (legacy usage rows)
  - `...\Overtime_TimeOff\analytics_output\monthly_breakdown.csv` (accrual rows)
- `scripts/overtime_timeoff_with_backfill.py` now:
  - Runs the production v10 script
  - Restores historical months into the FIXED output from `PowerBI_Date\Backfill\YYYY_MM\vcs_time_report\...`
  - Backfills `analytics_output\monthly_breakdown.csv` for prior 12 months from the same export (preserving the current month from v10)
- Validation helper:
  - `scripts/compare_vcs_time_report_exports.py` can diff a refreshed visual export against a known-good baseline (e.g., Oct-24 monthly export)

### Policy Training Monthly: Current Month + Backfill Verified ✅
- ETL project lives in: `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Policy_Training_Monthly`
- Output workbook: `...\output\policy_training_outputs.xlsx` (sheet `Delivery_Cost_By_Month`)
- Validation helper:
  - `scripts/compare_policy_training_delivery.py` can compare a refreshed visual export (Delivery Cost by month) vs ETL output and vs backfill (history months).

### Summons: Current Month From E-Ticket + Backfill Verified ✅
- Power BI source workbook: `C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx`
- Current month is computed from: `...\05_EXPORTS\_Summons\E_Ticket\YY_MM_e_ticketexport.csv`
- History is carried via backfill exports in `PowerBI_Date\Backfill\YYYY_MM\summons\...`
- **Status (2025-12-12):** All issues resolved - system healthy and working correctly
  - WG2 column: 134,144 rows populated (42.52%), 181,363 null (historical aggregates - expected)
  - M Code queries: All 3 queries working correctly, handling missing columns properly
  - DAX measure: Corrected to `___Total Tickets = COUNTROWS('___Summons')`
  - Data validation: 315,507 total rows verified
- Validation helpers:
  - `scripts/compare_summons_deptwide.py` compares Dept-Wide visual export vs backfill history and vs ETL current month
  - `scripts/compare_summons_all_bureaus.py` compares All Bureaus visual vs ETL output
  - `scripts/diagnose_summons_blank_bureau.py` identifies blank `WG2` rows that show up as blank Bureau
  - `scripts/diagnose_summons_assignment_mapping.py` diagnoses WG2 assignment mapping issues
  - `scripts/diagnose_summons_missing_months.py` identifies missing months in staging workbook
  - `scripts/diagnose_summons_top5_vs_deptwide.py` validates Top 5 queries vs Dept-Wide data
  - `scripts/fix_summons_wg2_from_assignment.py` fixes WG2 column from WG2_ASSIGN
  - `scripts/run_summons_with_overrides.py` can inject a badge override (e.g. badge 1711 → Traffic Bureau) and regenerate the workbook before refresh
- Documentation:
  - `claude_code_summons.md` - Comprehensive troubleshooting guide
  - `SUMMONS_DIAGNOSTIC_REPORT_2025_12_12.md` - Complete diagnostic report
  - `SUMMONS_DAX_MEASURES_CORRECTED.txt` - Corrected DAX measure instructions

---

## System Manifest

A comprehensive system manifest (`manifest.json`) is maintained that includes:
- Complete system configuration and settings
- All ETL scripts with their settings, execution order, and status
- Execution statistics and recent log history
- Directory structure and file metadata
- Documentation index

The manifest provides a machine-readable reference for the entire Master Automation system and can be used for system auditing, documentation generation, or integration with other tools.

---

**Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation`  
**Last Updated:** 2026-02-26  
**Version:** 1.17.6  
**Status:** ✅ Template Updated — Staging Data Refresh Pending


## 2026-02-23

### v1.17.5 — Surgical Template Update COMPLETE
- **All queries load cleanly** — Close & Apply succeeds with zero DAX errors
- **Changes applied**: `pReportMonth` parameter created; paths fixed in 4 queries; `DateTime.LocalNow()` replaced in 6 queries; `___Summons` query re-created (12 DAX measures); `___ResponseTimeCalculator` got `Count`/`MonthName` columns; `summons_13month_trend` fixed (dedup, computed columns); 4 orphaned DAX tables deleted
- **Staging data gap**: `summons_powerbi_latest.xlsx` only has data through Sep 2025 — summons visuals will populate after next ETL run refreshes staging with Oct 2025 – Jan 2026 data
- **`summons_top5_parking`** still uses `List.Max(YearMonthKey)` — will self-correct when staging data is refreshed

### v1.17.4 — Bulk M Code Paste Failed
- Bulk paste broke DAX model (schema mismatch); all changes discarded; surgical approach applied (v1.17.5)

---

## 2026-02-22

### v1.17.3 — Template Refresh & Laptop Path Resolution
- **Report template refreshed** from January 2026 published report (`2026_01_Monthly_Report.pbix`); old broken template archived
- **Laptop path junction** created: `C:\Users\carucci_r` → `C:\Users\RobertCarucci` — M code paths resolve on both machines
- **M code reorganization** (v1.17.2): 20 page-based subfolders; Drone/Social Media/Summons syntax fixes

---

## 2026-02-18

### February 2026 ETL Cycle - Response Times Fix Complete ✅

**Major Achievement**: Fixed critical Response Time calculation methodology

#### Response Time Deduplication Fix:
- **Problem**: Multi-unit incidents were deduplicated by file order, not arrival time
- **Solution**: Sort by `['ReportNumberNew', 'Time Out']` before deduplication
- **Impact**: Ensures first-arriving unit defines response time (industry standard)
- **File**: `02_ETL_Scripts/Response_Times/process_cad_data_13month_rolling.py`

#### Response Time Metrics Clarified:
1. **Response Time (Primary)**: Call received to first unit arrival
2. **Travel Time**: Dispatch to first unit arrival  
3. **Processing Time**: Call received to dispatch

#### January 2026 Results (Validated):
- Emergency: 3:11 min (347 incidents)
- Urgent: 2:54 min (843 incidents)
- Routine: 2:48 min (853 incidents)
- Multi-unit rate: 28.2% (realistic for police operations)

#### ETL Cycle Infrastructure:
- **Pre-flight Validation**: Comprehensive dependency and source data checks
- **Visual Export Processing**: 25/36 visuals enforce 13-month windows
- **Quality Assurance**: Multi-unit rate monitoring and CAD validation
- **Documentation**: Executive analysis of multi-unit impact on response times

**Status**: Response Times workflow operational with corrected methodology

---

## 2026-02-17
- Consolidated Power BI visual export mapping into one file.
- Primary path: Standards\config\powerbi_visuals\visual_export_mapping.json
- Archived prior mapping files under scripts\_archive\visual_export_mapping\2026_02_17_173019\
