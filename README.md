# Master ETL Automation

Centralized automation hub for running all Python ETL scripts that feed into Power BI reports.

## Overview

This directory orchestrates all Python data processing scripts from various workspaces and manages their output to the Power BI Date repository.

## Directory Structure

```
Master_Automation/
├── README.md                    # This file
├── CHANGELOG.md                 # Version history and updates
├── verify_migration.ps1         # Automated verification script
├── SUMMARY.md                   # Project summary / quick reference
├── config/
│   ├── scripts.json            # Configuration for all ETL scripts
│   └── scripts.json.bak        # Backup of previous config
├── scripts/
│   ├── run_all_etl.ps1         # PowerShell orchestrator (recommended)
│   ├── run_all_etl.bat         # Batch file orchestrator
│   ├── run_etl_script.ps1      # Helper script to run individual scripts
│   ├── _archive/                # Archived old/unused scripts
│   ├── overtime_timeoff_with_backfill.py     # Overtime/TimeOff monthly wrapper (v10 + backfill)
│   ├── restore_fixed_from_backfill.py        # Restores history into FIXED_monthly_breakdown
│   └── compare_vcs_time_report_exports.py    # Diff tool for visual exports/backfill validation
│   ├── compare_policy_training_delivery.py   # Policy Training: visual vs ETL/backfill diff
│   ├── compare_summons_deptwide.py           # Summons Dept-Wide: visual vs ETL/backfill diff
│   ├── diagnose_summons_blank_bureau.py      # Summons: find blank WG2 (Bureau) rows
│   └── run_summons_with_overrides.py         # Summons: run with injected badge overrides (e.g., 1711)
├── docs/                        # Project documentation (migration, verification, guides)
└── logs/
    └── .gitkeep                # ETL execution logs go here (auto-created)
```

## Quick Start

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

**Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation`  
**Last Updated:** 2025-12-12  
**Migration Status:** ✅ Complete - Ready for Testing

