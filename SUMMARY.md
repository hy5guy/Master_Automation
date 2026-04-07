# 06_Workspace_Management Project Summary

**Last Updated:** 2026-04-07
**Status:** ✅ v1.22.0 — `/find-stale-sources` skill + `check_source_freshness.py` helper (10 pipeline sources, content-first evidence). v1.21.1: Skill hardening (all 6 skills T9=1); Personnel v1.6.0. v1.21.0: 7 Claude Skills framework.
**Version:** 1.22.0 (see CHANGELOG)

---

## Project Overview

06_Workspace_Management is a centralized orchestration hub for running all Python ETL scripts that feed into Power BI reports. It provides automated execution, error handling, logging, and Power BI integration for multiple data processing workflows.

---

## Quick Facts

| Item | Details |
|------|---------|
| **Location** | `C:\Users\carucci_r\OneDrive - City of Hackensack\06_Workspace_Management` |
| **Purpose** | ETL Script Orchestration & Power BI Integration |
| **Language** | PowerShell, Python |
| **Status** | ✅ v1.21.1: Skill hardening + Personnel v1.6.0 (173 records, BADGE_NUMBER coercion, CAD parser). v1.21.0: 7 Claude Skills. v1.20.2: PBI MCP — Outreach + Summons WG3/WG4/TEAM (36 cols). |
| **Version** | 1.21.1 |
| **ETL Scripts** | 5 Enabled, 3 Disabled |
| **Root Files** | Key automation: `verify_migration.ps1`, **`etl_orchestrator.py`**, `run_summons_etl.py`, `config.json`, etc. |

---

## Key Features

✅ **Sequential Execution** - Runs scripts in specified order  
✅ **Error Handling** - Continues on errors, logs failures  
✅ **Logging** - Detailed logs for each script execution  
✅ **Power BI Integration** - Automatically copies outputs to Power BI drop folder  
✅ **Selective Execution** - Run all, or specific scripts  
✅ **Status Reporting** - Summary of what succeeded/failed  
✅ **Dry Run Mode** - Preview what would execute  
✅ **Python ETL orchestrator** — `python etl_orchestrator.py` from repo root: **`--list`**, **`--dry-run`**, **`--run --script "Name"`**, **`--parse-logs`**, **`--validate`**, **`--scorecard`**; uses **`scripts/path_config.py`** (same OneDrive / `PowerBI_Data` resolution as other Python tools). On **Windows desktop**, run `set PYTHONIOENCODING=utf-8` first if the console raises Unicode errors. Audit trail: **`docs/ETL_SKILL_MEMORY.md`**. Complements **`scripts/run_all_etl.ps1`**; does not replace it.  
✅ **Input Validation** - Validates required export files before execution  
✅ **OneDrive Sync** - All paths synced for cloud backup  
✅ **Path portability** - `ONEDRIVE_BASE` / `ONEDRIVE_HACKENSACK` env vars (Python `path_config.py`, PowerShell `$OneDriveBase`); **`get_onedrive_root()`** prefers `C:\Users\carucci_r\OneDrive - City of Hackensack` when it exists (canonical desktop; laptop uses junction). **`get_powerbi_data_dir()`** reads repo **`config.json`** key `"PowerBI"` (default `PowerBI_Data`)  
✅ **Processed_Exports pipeline** - `processed_exports_routing.py` + `process_powerbi_exports.py`: canonical folder aliases, archive previous CSV under `archive/YYYY_MM/`, idempotent identical-file skip; mapping targets include `monthly_accrual_and_usage`, consolidated `detectives` / `stacp`, MVA → `traffic`; optional `--scan-processed-exports-inbox`; `--report-month` drives `--13m-window-ends` in normalizer (drops partial tail month). **`canonicalize_processed_exports_layout.py`** — optional on-disk merge/rename to lowercase canonical folders (see README).  
✅ **Validation CLIs** - `validate_response_time_exports.py` (response_time CSV shapes); `validate_13_month_window.py` with `--report-month`, `--accept-warn`, partial future-month WARN  
✅ **Unit tests** - `cd scripts; python -m unittest discover -s tests -p "test_*.py" -v`  
✅ **Overtime/TimeOff hardening** - Pre-flight validation, strict file discovery, output schema check, test_pipeline.bat; **`config/scripts.json`** points **`overtime_timeoff_with_backfill.py`** at **`06_Workspace_Management\scripts`**; optional **`--end-month YYYY-MM`** aligns the 13-month window (passes **`--asof`** to v10)  
✅ **Visual export normalization** - Orchestrator normalizes "Monthly Accrual and Usage Summary" CSVs in _DropExports before organize_backfill  
✅ **Summons backfill** - `summons_backfill_merge.py` uses backfill as source of truth for all months in consolidated file (02-25 through 11-25); injection point at `docs/SUMMONS_BACKFILL_INJECTION_POINT.md`
✅ **DFR summons split** - `split_dfr_records()` isolates drone/temp-SSOCC records (Polson 0738 always; Ramirez 2025 Feb–Mar 26; Mazzaccaro 0377 Mar 26) and routes them to `dfr_directed_patrol_enforcement.xlsx` via `dfr_export.py`; DFR backfill auto-runs after export; main pipeline sees only non-DFR records
✅ **Fee/fine enrichment** — After backfill merge, `apply_fine_amount_and_violation_category` sets `FINE_AMOUNT` from e-ticket **Penalty** (if &gt; 0) else **`09_Reference/LegalCodes/data/Title39/municipal-violations-bureau-schedule.json`** on **STATUTE** (with normalization); sets **`VIOLATION_CATEGORY`**; extended **`summons_slim_for_powerbi.csv`** (financial + category columns). Uses **`_load_statute_lookups()`** (Title39 + City Ordinance JSON under `09_Reference/LegalCodes/data/...`). Requires fee schedule JSON on OneDrive for statute-based amounts when Penalty is 0.
✅ **DFR Power BI query** - `m_code/drone/DFR_Summons.m` loads DFR workbook with 13-month rolling window, dual dismiss/void filter (Summons_Recall + Summons_Status), schema-resilient Violation_Category/Jurisdiction, Date_Sort_Key, MM-YY, YearMonthKey
✅ **Arrest ETL future-proofed** - `--report-month YYYY-MM` (via `{REPORT_MONTH_ACTUAL}`); targeted file discovery in `05_EXPORTS/_Arrest/YYYY/month/`; outputs `YYYY_MM_Arrests_PowerBI_Ready.xlsx` to `01_DataSources/ARREST_DATA/Power_BI/`
✅ **13-month rolling window** - 24 Power BI visuals enforced to exactly 13 months (end = previous month); `process_powerbi_exports.py` (match_pattern, enforce_13_month), `validate_13_month_window.py`; docs in `docs/13_MONTH_*.md`
✅ **Assignment Master sync path-agnostic** - `09_Reference/Personnel/scripts/sync_assignment_master.py` (or `run_sync.bat`); uses BASE_DIR = parent of scripts/; normalizes `BADGE_NUMBER` (strips `.0`) and `PADDED_BADGE_NUMBER` (4-digit zero-pad); `parse_cad_assignment.py` compares CAD shift exports against Master; works on desktop (**carucci_r**) and laptop (**junction** `carucci_r` → profile or `ONEDRIVE_BASE`)
✅ **Claude Code Skills** — 8 slash commands in `.claude/commands/` for guided ETL workflows (see table below)

---

## Claude Code Skills (Slash Commands)

| Command | Purpose |
|---------|---------|
| `/diagnose-pipeline` | Targeted diagnostics for any ETL pipeline |
| `/fix-excel` | Safe zip-level XML surgery for Excel workbooks |
| `/monthly-cycle` | Full monthly ETL cycle: preflight → exports → execution → validation |
| `/preflight` | Pre-flight validation gate for source data, config, and personnel |
| `/process-exports` | Route Power BI visual exports from `_DropExports` |
| `/sync-personnel` | Assignment Master validation, sync, and gap detection |
| `/find-stale-sources` | Identify source files not updated through target report month |
| `/validate-window` | 13-month rolling window completeness checks |

Details: `docs/CLAUDE_SKILLS_ANALYSIS_REPORT.md`

---

## Enabled ETL Scripts

| # | Script Name | Filename | Status |
|---|-------------|----------|--------|
| 1 | Arrests | `arrest_python_processor.py` (--report-month {REPORT_MONTH_ACTUAL}; targeted discovery in YYYY/month/) | ✅ Enabled |
| 2 | Community Engagement | `deploy_production.py` | ✅ Enabled |
| 3 | Overtime TimeOff | `overtime_timeoff_with_backfill.py` | ✅ Enabled (validation: 05_EXPORTS\_Overtime, _Time_Off, PowerBI_Data\Backfill\vcs_time_report) |
| 4 | Response Times | `process_cad_data_13month_rolling.py` | ✅ Enabled (CallType_Categories.csv fallback; input from report month) |
| 5 | Summons | `run_summons_etl.py`; `summons_etl_normalize.py` v2.5.0; DFR split → `dfr_export.py` → `dfr_directed_patrol_enforcement.xlsx` | ✅ Enabled |

### Disabled Scripts

| Script Name | Reason |
|-------------|--------|
| Arrest Data Source | Only test files found |
| NIBRS | No Python files found |

---

## Directory Structure

```
06_Workspace_Management/
├── README.md                    # Main documentation
├── SUMMARY.md                   # This file
├── CHANGELOG.md                 # Version history
├── Claude.md                    # AI assistant guide
├── etl_orchestrator.py          # Python CLI: --list / --dry-run / --run / --parse-logs / --validate / --scorecard
├── verify_migration.ps1         # Migration verification
├── 06_Workspace_Management.code-workspace  # VS Code workspace
├── .gitignore                   # Git ignore rules
├── config.json                  # Optional: Power BI root folder name for get_powerbi_data_dir()
├── requirements.txt             # Python deps (pandas, openpyxl) for validation & summons backfill
├── .claude/                     # Claude Code configuration
│   ├── commands/               # 7 slash command skills (diagnose-pipeline, fix-excel, monthly-cycle, preflight, process-exports, sync-personnel, validate-window)
│   └── settings.local.json     # Tool permission allowlist
├── config/                      # Configuration files
│   ├── scripts.json            # ETL script configuration
│   ├── response_time_filters.json  # Response Time filters
│   └── scripts.json.bak        # Backup configuration
├── scripts/                     # PowerShell execution scripts
│   ├── run_all_etl.ps1         # Main orchestrator
│   ├── run_all_etl.bat         # Batch wrapper
│   ├── run_etl_script.ps1      # Single script runner
│   ├── path_config.py          # get_onedrive_root(), get_powerbi_data_dir(), get_powerbi_paths()
│   ├── processed_exports_routing.py  # Processed_Exports canonical dirs + archive helper
│   ├── canonicalize_processed_exports_layout.py  # Merge legacy Processed_Exports dirs → canonical names
│   ├── validate_exports.py     # Pre-flight OT/TimeOff export check
│   ├── validate_outputs.py     # FIXED CSV schema validation
│   ├── test_pipeline.bat       # Overtime/TimeOff test: validate → dry-run → validate outputs
│   ├── summons_backfill_merge.py  # Merge gap months into summons df
│   ├── summons_etl_normalize.py   # Core summons ETL v2.5.0: DFR split, fee/fine + VIOLATION_CATEGORY
│   ├── dfr_export.py              # DFR workbook export: schema map, append, dedup, formula-col guard
│   ├── dfr_backfill_descriptions.py # DFR description/fine backfill (cascading statute lookup)
│   ├── normalize_visual_export_for_backfill.py  # Normalize visual exports (13-month window, PeriodLabel for OT)
│   ├── process_powerbi_exports.py               # _DropExports → Processed_Exports + Backfill (routing, archive)
│   ├── validate_13_month_window.py              # 13-month window; report-month, accept-warn, partial tail
│   ├── validate_response_time_exports.py        # Response_time export CSV checks
│   ├── tests/                   # unittest (routing, archive, validators)
│   ├── (other helper Python scripts)
│   └── _testing/               # Benchmark/debug scripts (4 files)
├── docs/                        # Documentation files
│   ├── ETL_SKILL_MEMORY.md     # etl_orchestrator scorecard / evidence log
│   ├── SSOCC_Service_Log_Excel_And_Power_BI_Rework_2026_03.md  # SSOCC Option B migration
│   ├── cursor_prompt_fix_duration_and_attendees.md  # Community ETL duration + STACP attendees
│   ├── response_time/          # Response Time docs (15 files incl. Chief Antista reports)
│   ├── templates/              # Reusable AI prompt templates (HPD design system)
│   ├── archived_workflows/     # Archived workflows
│   └── (migration guides, reports, troubleshooting)
├── m_code/                      # Power BI M code (47+ queries, 20 page folders)
│   ├── arrests/               # 4 queries (Categories, Distro, Top 5, 13Month)
│   ├── benchmark/             # 1 query
│   ├── chief/                 # 2 queries (Chief2, chief_projects)
│   ├── community/             # 1 query (Combined_Outreach_All)
│   ├── csb/                   # 1 query
│   ├── detectives/            # 2 queries (Detectives, CCD)
│   ├── drone/                 # 2 queries: ___Drone + DFR_Summons (new — 13-month, dual dismiss/void filter)
│   ├── esu/                   # 1 query (ESU_13Month)
│   ├── functions/             # 5 shared functions (fnGetFiles, fnReadCsv, etc.)
│   ├── nibrs/                 # 1 query
│   ├── overtime/              # 1 query (v3)
│   ├── parameters/            # 6 parameters (RootExportPath, EtlRootPath, pReportMonth, etc.)
│   ├── patrol/                # 1 query (Patrol)
│   ├── remu/                  # 1 query (REMU)
│   ├── response_time/         # 1 query (ResponseTimeCalculator)
│   ├── shared/                # 6 queries (DateTable, DimMonth, DimEventType, etc.)
│   ├── social_media/          # 1 query (Social_Media)
│   ├── ssocc/                 # ___SSOCC_Data, FactServiceLog, DimServiceGroup, TAS_Dispatcher (4 .m sources)
│   ├── stacp/                 # 2 queries (STACP_pt_1_2, STACP_DIAGNOSTIC)
│   ├── summons/               # 5 queries (13month, top5_parking, top5_moving, all_bureaus, dept_wide)
│   ├── traffic/               # 1 query
│   ├── training/              # 2 queries (Cost, In-Person)
│   ├── tmdl_export/           # Full TMDL model export (85 files, re-importable)
│   └── archive/               # Archived/superseded M code (53+ files)
├── outputs/                     # Organized output files
│   ├── arrests/                # Arrest exports (3 files)
│   ├── visual_exports/         # Power BI exports (23 files)
│   ├── summons_validation/     # Summons data (11 files)
│   ├── metadata/               # Config/verification (6 files)
│   ├── community_engagement/   # Community data (6 files)
│   ├── misc/                   # Miscellaneous (9 files)
│   └── large_exports/          # Large files (2 files, 37MB)
├── verifications/               # ETL verification framework
│   ├── reports/                # Verification reports (2 files)
│   ├── (5 Python verifier files)
│   └── __pycache__/
├── logs/                        # ETL execution logs
└── chatlogs/                    # AI chat logs
```

---

## Quick Start

### Python environment
Install dependencies for validation and Summons backfill (env used by `config/scripts.json`):
```powershell
pip install -r requirements.txt
```

### Run All ETL Scripts

```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\06_Workspace_Management"
.\scripts\run_all_etl.ps1
```

### Run Specific Script

```powershell
.\scripts\run_etl_script.ps1 -ScriptName "Arrests"
```

### Dry Run (Preview)

```powershell
.\scripts\run_all_etl.ps1 -DryRun
```

### Verify Configuration

```powershell
.\verify_migration.ps1
```

---

## Configuration

**Main Config File:** `config\scripts.json`

**Key Settings:**
- `powerbi_drop_path` - Where ETL outputs are copied
- `python_executable` - Python command to use
- `continue_on_error` - Whether to stop on errors
- `log_directory` - Where logs are saved

**Script Configuration:**
- `name` - Display name
- `path` - Script directory path
- `script` - Python filename
- `enabled` - Whether script runs
- `order` - Execution order
- `timeout_minutes` - Maximum execution time

---

## Workflow

1. **Configure** - Edit `config\scripts.json` with script paths
2. **Run** - Execute `run_all_etl.ps1` or `run_all_etl.bat`
3. **Process** - Scripts execute in order, outputs logged
4. **Integrate** - Successful outputs copied to **PowerBI_Data** (`_DropExports` / `Backfill` per `config/scripts.json`)
5. **Organize** - Run `organize_backfill_exports.ps1` in PowerBI_Data
6. **Review** - Check logs for any failures or warnings

---

## Overtime TimeOff (Backfill + Processed Month)

The 13-month “Monthly Accrual and Usage Summary” visual is built from **two inputs**:

- **Legacy usage rows** (Comp/Sick/IOD/Mil/SAT) from:  
  `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Overtime_TimeOff\output\FIXED_monthly_breakdown_*.csv`
- **Accrual rows** (Accrued Comp/OT split by Sworn/NonSworn) from:  
  `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Overtime_TimeOff\analytics_output\monthly_breakdown.csv`

To prevent “null/0” in prior months, the wrapper `scripts/overtime_timeoff_with_backfill.py`:
- runs the production v10 script for the current month
- restores historical months into the FIXED file from `PowerBI_Data\Backfill\YYYY_MM\vcs_time_report\...`
- backfills `monthly_breakdown.csv` for the prior 12 months from the same backfill export (preserving the current month from v10)

Validation tool:
- `scripts/compare_vcs_time_report_exports.py` compares a refreshed export against a known-good baseline (e.g., Oct-24 monthly export) for the prior 12 months.

**v1.13.0 (2026-02-10):**
- Primary backfill: 2025_12 visual export in `data/backfill/` and `PowerBI_Data\Backfill\2025_12\vcs_time_report\`
- `scripts/normalize_visual_export_for_backfill.py` normalizes default Power BI export (Long/Wide) and writes to backfill folder
- Single-query M: `m_code/2026_02_10_Overtime_Timeoff_v3_CONSOLIDATED.m` (use in ___Overtime_Timeoff_v3 if staging refs fail); see `docs/VISUAL_EXPORT_NORMALIZE_AND_BACKFILL.md` and `docs/OVERTIME_TIMEOFF_RERUN_AFTER_BACKFILL.md`

---

## Policy Training Monthly (Backfill + Current Month)

Policy Training is managed in its own project folder (enabled in `config/scripts.json`):
- `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Policy_Training_Monthly`

Key output:
- `...\output\policy_training_outputs.xlsx` (sheets: `Delivery_Cost_By_Month`, `InPerson_Prior_Month_List`, `Training_Log_Clean`, etc.)

Expected behavior:
- Backfill months match the prior-month backfill export (e.g., `PowerBI_Data\Backfill\2025_10\policy_training\...`)
- ETL computes rolling 13-month window; **01-26** (and later months) appear in Cost by Delivery Method visual after ETL run when source workbook has that period.
- **Power BI `___In_Person_Training` (repo M):** loads **`Policy_Training_Monthly.xlsx`** (full **`Training_Log`** / **`Training_Log_Clean`**), not only `InPerson_Prior_Month_List`. YTD cards filter in DAX. See **`docs/POLICY_TRAINING_AUTOMATION_AND_COST_VISUAL.md`**.

Doc:
- `docs/POLICY_TRAINING_AUTOMATION_AND_COST_VISUAL.md` – Run location, Cost of Training 13-month fix, In-Person source and error handling.

Validation helper:
- `scripts/compare_policy_training_delivery.py` (visual export vs ETL output; history vs backfill)

---

## Summons (Backfill + Current Month From E-Ticket)

**Status (2025-12-12):** ✅ All Issues Resolved - System Healthy

**⚠️ Verification Note (2026-03-03):** Re-export all summons e-ticket data to verify counts. See `docs/SUMMONS_VERIFICATION_NOTE_2026_03.md`.

**v1.18.6 (2026-03-13):** All four summons visuals (13month_trend, all_bureaus, top5_moving, top5_parking) use **report month** in window/filter — for Feb 2026 report, 02-26 data included.

**v1.18.1 (2026-03-10):** Ramirez SSOCC overrides in ETL; UNASSIGNED mapping in all_bureaus; 07-25 filler rows in 13month_trend; `docs/SUMMONS_M_CODE_NOTES.md` for lessons learned.

Power BI source (`run_summons_etl.py`, v2.5.0+):
- `C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_slim_for_powerbi.csv` — extended SLIM CSV (36 columns: **WG1–WG4**, **TEAM**, **`FINE_AMOUNT`**, **`VIOLATION_CATEGORY`**, **`DATA_QUALITY_TIER`**, financials, etc.); primary source for **`___Summons.m`** and related summons queries
- **WG3/WG4/TEAM** populated from `Assignment_Master_V2.csv` (WG5 removed — never existed in source). M code `___Summons` updated 2026-03-28.

Current month source:
- `C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\YYYY\YYYY_MM_eticket_export.csv`
- Example: `2025\2025_12_eticket_export.csv` for December 2025

History/backfill source:
- `PowerBI_Data\Backfill\YYYY_MM\summons\...` (e.g. Dept-Wide Moving/Parking CSVs)

**Recent Fixes (2025-12-12):**
- ✅ WG2 column: Fixed - 134,144 rows populated (42.52%), 181,363 null (historical - expected)
- ✅ M Code queries: All 3 queries working correctly, handling missing columns dynamically
- ✅ Missing columns: TICKET_COUNT and ASSIGNMENT_FOUND correctly don't exist (each row = 1 ticket)
- ✅ Top 5 queries: Returning data correctly for Moving and Parking violations
- ✅ DAX measure: Corrected to `___Total Tickets = COUNTROWS('___Summons')`
- ⚠️ Missing months: 03-25, 10-25, 11-25 identified - ETL script needs to merge backfill + current month

**Data Validation (2025-12-12):**
- Total rows: 315,507
- Moving violations (M): 311,588 (98.76%)
- Parking violations (P): 3,910 (1.24%)
- Other violations (C): 9 (0.00%)
- Most recent month: September 2025 (4,599 tickets)

Validation helpers:
- `scripts/compare_summons_deptwide.py` (Dept-Wide visual export vs backfill history + ETL current month)
- `scripts/compare_summons_all_bureaus.py` (All Bureaus visual vs ETL output)
- `scripts/diagnose_benchmark_data.py` (analyze Benchmark source CSVs; date coverage, scenario A/B/C for Power BI visuals)
- `scripts/diagnose_summons_blank_bureau.py` (find blank `WG2` rows → blank Bureau in visuals)
- `scripts/diagnose_summons_assignment_mapping.py` (diagnose WG2 assignment mapping issues)
- `scripts/diagnose_summons_missing_months.py` (identify missing months in staging workbook)
- `scripts/diagnose_summons_top5_vs_deptwide.py` (validate Top 5 queries vs Dept-Wide data)
- `scripts/fix_summons_wg2_from_assignment.py` (fix WG2 column from WG2_ASSIGN)

Operational helper:
- `scripts/run_summons_with_overrides.py` injects badge overrides (e.g. badge 1711 mapped to Traffic Bureau) and regenerates the workbook prior to refresh.

Documentation:
- `claude_code_summons.md` - Comprehensive troubleshooting guide
- `SUMMONS_DIAGNOSTIC_REPORT_2025_12_12.md` - Complete diagnostic report
- `SUMMONS_DAX_MEASURES_CORRECTED.txt` - Corrected DAX measure instructions

---

## Output Integration

**ETL Outputs:**
- Written to: `PowerBI_Data\_DropExports\`
- Format: CSV files
- Naming: As specified by each ETL script

**Organization:**
- Run `PowerBI_Data\tools\organize_backfill_exports.ps1`
- Files moved to: `Backfill\YYYY_MM\category\`
- Files renamed with month prefix

---

## Logging

**Log Location:** `logs\`

**Log Files:**
- `YYYY-MM-DD_HH-MM-SS_ETL_Run.log` - Overall execution log
- `YYYY-MM-DD_HH-MM-SS_[ScriptName].log` - Individual script logs

**Log Contents:**
- Execution start/end times
- Script paths and configurations
- Success/failure status
- Error messages
- Output file information

---

## Error Handling

- Scripts run independently (failure of one doesn't stop others)
- Errors logged with details
- Summary report shows success/failure status
- Failed scripts can be re-run individually
- `continue_on_error` setting controls behavior

---

## Migration Status

✅ **Complete** - PowerBI_Data migrated to OneDrive

**Migration Details:**
- **From:** `C:\Dev\PowerBI_Data_Merged`
- **To:** `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data`
- **Date:** 2025-12-11
- **Status:** All paths updated and verified

**Verification:**
- ✅ Config paths correct
- ✅ Script paths updated
- ✅ Junction created
- ✅ Documentation updated
- ✅ Script filenames verified

---

## Key Paths

| Purpose | Path |
|---------|------|
| **Workspace** | `C:\Users\carucci_r\OneDrive - City of Hackensack\06_Workspace_Management` |
| **Config** | `config\scripts.json` |
| **Logs** | `logs\` |
| **PowerBI Drop** | `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\_DropExports` |
| **ETL Scripts** | `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\*` |
| **Data Sources** | `C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\*` |
| **Report Template** | `C:\Users\carucci_r\OneDrive - City of Hackensack\08_Templates\Monthly_Report_Template.pbix` |
| **Monthly Reports** | `C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Monthly Reports\YYYY\MM_monthname\` |

---

## Documentation

**Main Documentation:**
- `README.md` - Project overview and quick start
- `SUMMARY.md` - This file (project summary)
- `CHANGELOG.md` - Version history

**Detailed Documentation (in `docs\`):**
- `MONTHLY_REPORT_TEMPLATE_WORKFLOW.md` - Template location, monthly cycle steps, M code deployment checklist (49 queries)
- `ESU_POWER_BI_LOAD_AND_PUBLISH.md` - ESU 13-month: single query (ESU_13Month.m), output columns (Status, ItemKey, Month_Year), workbook requirements, optional 4-query approach
- `BENCHMARK_VISUALS_HANDOFF_PROMPT.md` - AI handoff for Benchmark Power BI visuals troubleshooting
- **Benchmark diagnostic (2026-02-13):** `diagnose_benchmark_data.py` run confirmed **Scenario B** — source CSVs in `05_EXPORTS\Benchmark` have good multi-month coverage (use_force 61, show_force 22, vehicle_pursuit 11 months); issue is in Power BI (MonthStart, relationships, or date types). See `docs/BENCHMARK_VISUAL_DIAGNOSTIC.md` steps 3, 5, 7.
- `QUICK_START.md` - Quick reference guide
- `VERIFICATION_REPORT.md` - Migration verification details
- `MIGRATION_VERIFICATION.md` - Migration verification guide
- `PROJECT_STRUCTURE.md` - Directory structure details

---

## Troubleshooting

### Script Not Found
- Check path in `config\scripts.json`
- Verify script file exists at specified path
- Check filename matches configuration

### Python Not Found
- Set `python_executable` in config
- Options: `python`, `python3`, `py`, or full path
- Verify Python is in PATH

### Timeout Issues
- Increase `timeout_minutes` for slow scripts
- Check script execution time in logs
- Verify script is actually running

### Output Not Copied
- Check `powerbi_drop_path` exists
- Verify OneDrive sync status
- Check file permissions

---

## Recent Updates (2026-03-19)

### v1.18.13 — Directory Consolidation Complete; Power BI Template MCP Injection ✅

**Claude Desktop MCP session** successfully updated `08_Templates\Monthly_Report_Template.pbix`:

- **M-Code Paths:** 4 Response Time partitions (`___ResponseTime_DispVsCall`, `___ResponseTime_OutVsCall`, `___ResponseTimeCalculator`, `___ResponseTime_AllMetrics`) — `PowerBI_Date` → `PowerBI_Data` injected.
- **DAX Subtitles:** 13 lagged subtitle measures rewritten to use standardized 13-month rolling format based on `___DimMonth`; fixes stale dates, `FIRSTNONBLANK` error in `Subtitle_V3_Accrual`, missing column in `Metrics Qual Subtitle`.
- **New Measure:** `Subtitle_DeptWide_Summons` on `summons_13month_trend`.
- **Use of Force Fix:** `IncidentCount_13Month` — `EDATE` end-of-month bug excluded Feb 2025; rewritten to start-of-month (75 → 78 count resolved).
- **Cosmetic Deferral:** `STACP_DIAGNOSTIC` comment header updated to `06_Workspace_Management`; `___STACP_pt_1_2`, `___Detectives`, `ESU_13Month` deferred (local source files already correct).

---

## Recent Updates (2026-03-09)

### v1.17.31 — pReportMonth Migration EXECUTED via Claude Desktop MCP ✅

- **All 16 queries migrated** from `DateTime.LocalNow()` to `pReportMonth` on `2026_02_Monthly_Report_laptop`
- **Executed in 4 waves** (save between each) to manage memory constraints
- **Post-migration DAX verification passed**: DimMonth (13 rows), Detectives (509 rows), Arrest_13Month (629 rows, 13 months), CSB_Monthly, Drone, RT_AllMetrics (117 rows)
- **Zero `DateTime.LocalNow()` remaining** in any migrated query
- **TMDL export**: Full model exported to `m_code/tmdl_export/` (85 files) for version control
- **Chatlog**: `docs/chatlogs/Claude-Attached_prompt_execution/`

### v1.17.30 — ___Arrest_13Month Rolling Query Added ✅

- New `m_code/arrests/___Arrest_13Month.m` — rolling 13-month arrest data from raw Lawsoft monthly exports
- Dynamic file discovery, pReportMonth-driven window, charge + home enrichment

---

## Recent Updates (2026-02-13)

### v1.15.4 - CSB Workbook 2026 Setup Complete ✅
- **Complete Success** - CSB (Crime Suppression Bureau) workbook fully prepared for 2026 data entry
- **Work by Claude in Excel**:
  - Renamed all 2025/2026 sheets to YY_MM format (25_01, 26_01, etc.)
  - Created XLOOKUP formulas on MoM sheet for all 2026 months (columns Q-AH)
  - Restored 2025 data (25_01 through 25_12) and Jan 2026 (26_01)
  - Created empty template sheets for Feb-Dec 2026 (26_02 through 26_12)
- **Structure**: Each monthly sheet has "Tracked Items" (column A) and "Total" (column B) with 26 crime categories
- **XLOOKUP Formulas**: Reference sheet columns directly (e.g., `'26_02'!$A:$A`) - fully working
- **Ready for Data Entry**: All 11 remaining 2026 months have templates, MoM auto-updates when data entered
- **Integration Note**: Structure compatible with Power BI M code queries (similar to Detective workbook)
- **Documentation**: `docs/CSB_WORKBOOK_2026_SETUP_COMPLETE.md`
- **Status**: Complete - workbook ready for monthly data entry, no Power BI queries needed yet

### v1.15.3 - Detective Queries Excel Structure Fix ✅ **DEPLOYED**
- **Complete Success** - Detective Division Power BI queries now import data correctly from restructured workbook
- **Root Cause**: Excel workbook structure differed from Claude Excel add-on's planned restructuring
  - Expected: 2026-only data with MM-YY headers (e.g., `01-26`, `02-26`)
  - Actual: Historical data (Jun 2023 - Dec 2026) with YY-MMM headers (e.g., `26-Jan`, `25-Dec`)
- **Three Critical Fixes**:
  1. **Date Parsing** - Changed from MM-YY to YY-MMM format parsing
     - Added month abbreviation lookup (`"Jan"` → 1, `"Feb"` → 2, etc.)
     - Handles 2-digit year conversion (26 → 2026, 25 → 2025)
  2. **Rolling Window Logic** - Fixed from hardcoded 2026-only to proper 13-month rolling
     - Old: `StartFilterDate = #date(2026, 1, 1)` (excluded all historical data)
     - New: `StartFilterDate = Date.AddMonths(EndFilterDate, -12)` (dynamic 13-month window)
  3. **Month Display Format** - Normalized YY-MMM to MM-YY for consistent visual display
     - Excel headers: `26-Jan`, `25-Dec` → Power BI columns: `01-26`, `12-25`
     - Added column transformation to convert parsed dates back to MM-YY format
- **Additional Fixes**:
  - Row label exact matching for CCD query (handles double spaces in Excel)
  - `"Monthly Bureau Case  Clearance % "` (double space + trailing space)
  - `"YTD Bureau Case Clearance % "` (trailing space)
- **Queries Updated**:
  - `___Detectives` - Detective case tracking (40 categories × 13 months)
  - `___Det_case_dispositions_clearance` - Case dispositions and clearance rates (10 rows × 13 months)
- **Current Data Window**: Jan 2025 - Dec 2025 (13 months)
  - Will automatically show Jan 2026 once data is entered in Excel
- **Diagnostic Tools Created**:
  - `scripts/analyze_detective_workbook.py` - Full workbook structure analysis
  - `scripts/check_detective_tables.py` - Quick table name verification
  - `scripts/check_detective_table_data.py` - Detailed table data inspection
  - `scripts/check_jan_26_data.py` - Verify 26-Jan column status
- **Documentation Created**:
  - `docs/DETECTIVES_EXCEL_STRUCTURE_MISMATCH_FIX.md` - Root cause analysis and fixes
  - `docs/DETECTIVES_2026_UPDATE_GUIDE.md` - Original deployment guide (now superseded)
  - `docs/DETECTIVES_2026_QUICK_REF.md` - Quick reference
  - `docs/DETECTIVES_CRITICAL_FIXES_2026_02_13.md` - Fix summary
  - `docs/DETECTIVES_VERIFICATION_CHECKLIST.md` - Manual verification steps
- **Status**: Deployed and verified - data loading correctly with proper MM-YY format ✅

### v1.15.2 - STACP Visual 13-Month Rolling Window Fixed ✅ **DEPLOYED**

- **Complete Success** - STACP Power BI visual now displays all 13 months of data correctly
- **Three Critical Issues Fixed**:
  1. **Year Detection Bug** - Hardcoded year check ("24" or "25") now replaced with dynamic validation
     - Works for any 2-digit year (24, 25, 26, 27... future-proof)
     - Enhanced month validation (1-12 range check)
     - Handles both M-YY and MM-YY column formats
  2. **Month Format Handling** - Enhanced to accept both single-digit (3-25) and padded (03-25) formats
     - Excel file analysis confirmed all columns properly formatted (MM-YY)
     - Added robust validation anyway for future compatibility
  3. **Window Calculation Bug** - Fixed rolling 13-month window logic
     - **Root Cause**: `StartMonth = EndMonth - 1` only gave 2 months (12-25, 01-26)
     - **Solution**: `StartMonth = EndMonth` (same month, one year earlier)
     - **Result**: Window now correctly spans 13 months (01-25 through 01-26)
- **Diagnostic Tools Created**:
  - `m_code/stacp/STACP_DIAGNOSTIC.m` - Diagnostic query showing column detection and window filtering
  - `scripts/analyze_stacp_workbook.py` - Python script to analyze Excel structure
  - `docs/STACP_TROUBLESHOOTING_GUIDE.md` - Comprehensive troubleshooting guide
- **Documentation Created**:
  - `docs/STACP_YEAR_DETECTION_FIX_2026_02_13.md` - Year detection fix details
  - `docs/STACP_INCONSISTENT_DATE_FORMAT_FIX.md` - Date format handling
  - `docs/STACP_WINDOW_CALCULATION_FIX.md` - Window calculation fix (primary issue)
  - `docs/STACP_FIX_QUICK_REF.md` - Quick reference for all fixes
- **Status**: Deployed and verified - all 13 months displaying correctly ✅

---

## Recent Updates (2026-02-09)

### v1.11.0 - Response Time Power BI M Code Fixed (31% Error Rate → 0%) ✅ **DEPLOYED**

- **Complete Success** - Response Time Power BI query now fully operational with 0% errors
- **Power BI M Code v2.8.0** - Fixed 31% type conversion errors in `Response_Time_MMSS` column
- **Root Cause Identified** - `type text` annotation in `Table.TransformColumns` conflicted with auto-typing
- **Decimal Precision Fixed** - Values like 2.87, 2.92 now convert correctly to MM:SS format
- **Column Quality Improved** - From 69% valid/31% errors to 100% valid/0% errors
- **All Formats Supported** - MM:SS, M:SS, HH:MM:SS, and decimal minutes (1.3, 2.87, 2.92)
- **Production Tested** - Verified with actual data files (wide and long formats)
- **Status**: Deployed and operational ✅

### v1.10.0 - Master Automation 100% Operational - All Workflows Fixed ✅

- **Complete Success** - All 6 ETL workflows now operational (100% success rate)
- **Overtime TimeOff Fixed** - Resolved missing personnel file (`Assignment_Master_V2.csv`)
- **Response Times ETL Fixed** - Migrated to timereport hybrid strategy (v2.1.0)
  - Implemented hybrid loading: yearly files (`2025_full_timereport.xlsx`) + monthly files (`2026_01_timereport.xlsx`)
  - Successfully combined 114,070 records (2025) + 10,440 records (Jan 2026) = 124,510 total
  - Generated 13 monthly CSVs (Jan 2025 - Jan 2026) in 76 seconds
- **Benchmark Directory Cleanup** - Consolidated duplicate directories, archived complex structure
- **Power BI M Code Updated** - Created `_benchmark2026_02_09.m` for simplified structure
- **January 2026 Monthly Report** - Successfully generated and saved
- **Execution Time** - 2.04 minutes (129.9 seconds) for all 6 workflows
- **Files Generated** - 60 total output files across all workflows

### Critical Fixes (2026-02-09):
1. **Overtime TimeOff** - Copied `Assignment_Master_V2.csv` to 06_Workspace_Management root (19.92s, 30 files)
2. **Response Times ETL** - Updated script from v2.0.0 → v2.1.0 with hybrid timereport loading (76.09s, 15 files)
3. **Response Times Power BI** - Updated M code from v2.7.1 → v2.8.0 fixing type conversion errors (0% errors)
4. **Validation Updates** - Enhanced `run_all_etl.ps1` with fallback path logic for Response Times and Summons

### Workflow Status (2026-02-09):
| Workflow | Status | Time | Files |
|----------|--------|------|-------|
| Arrests | ✅ Success | 6.27s | 2 |
| Community Engagement | ✅ Success | 7.86s | 2 |
| Overtime TimeOff | ✅ Success | 19.92s | 30 |
| Response Times | ✅ Success | 76.09s | 15 |
| Summons | ✅ Success | 2.06s | 7 |
| Summons Derived | ✅ Success | 8.66s | 4 |

---

## Recent Updates (2026-02-05)

### v1.8.1 - December 2025 Power BI Visual Export Processing & Diagnostics
- ✅ **December 2025 Export Organization** - Processed and organized 36 CSV exports from December 2025 monthly report
- ✅ **File Categorization** - Organized 53 total files into 16 categories in `PowerBI_Data\Backfill\2025_12\`
- ✅ **Data Quality Issues Identified** - Documented 3 critical issues (2 blank exports, 1 data gap)
- ✅ **Comprehensive Diagnostics** - Created 3 detailed reports with root cause analysis and fix recommendations
- ⚠️ **Action Required** - Fix Power BI date filters before January 2026 export

### Critical Issues Documented:
1. **Engagement Initiatives by Bureau** - Blank export (expected 22 events)
   - Root cause: Date filter using `TODAY()` function
   - Status: Documented with 4 fix options
   
2. **Chief's Projects & Initiatives** - Blank export
   - Same root cause as Issue #1
   - Status: Fix applies to both visuals
   
3. **Department-Wide Summons** - Missing 4 months (03-25, 07-25, 10-25, 11-25)
   - Root cause: Source data gap
   - Status: Requires ETL backfill investigation

### Reports Created:
- `DECEMBER_2025_VISUAL_EXPORT_DIAGNOSTIC_REPORT.md` - Full analysis
- `ENGAGEMENT_INITIATIVES_BLANK_EXPORT_INVESTIGATION.md` - Technical guide
- `DECEMBER_2025_EXPORT_QUICK_SUMMARY.md` - Quick reference

---

## Recent Updates (2026-02-04)

### v1.8.0 - Major Directory Consolidation & Cleanup
- ✅ **Root Directory Cleanup** - Reduced from 91 files to 7 essential files (92% cleaner)
- ✅ **Directory Consolidation** - Merged duplicate directories (`output/` → `outputs/`, `verification_reports/` → `verifications/reports/`)
- ✅ **Documentation Consolidation** - Merged README, CHANGELOG, SUMMARY from desktop + laptop versions
- ✅ **Organized Structure** - Created 9 new subdirectories for proper file organization
- ✅ **Temporary File Cleanup** - Deleted 50 Claude Code marker files + 6 unnecessary temp files
- ✅ **All Data Preserved** - 100% of files preserved, just better organized
- ✅ **Professional Structure** - Industry-standard directory layout with clear separation of concerns

### Recent System Status
- **Version**: 1.17.6
- **Status**: ✅ Template Updated — Staging Data Refresh Pending
- **pReportMonth**: `#date(2026, 2, 1)` in both repo and template
- **ETL Workflows**: 5/5 enabled scripts operational
- **Power BI Queries**: 45+ queries loading cleanly; all use `pReportMonth` parameter
- **Report Template**: Surgical edits complete — all queries load, Close & Apply succeeds with zero errors
- **Staging Data Gap**: `summons_powerbi_latest.xlsx` only has data through Sep 2025; summons visuals empty for Jan 2026. Will auto-populate after next ETL run refreshes the staging file
- **Laptop Junction**: `C:\Users\carucci_r` → `C:\Users\RobertCarucci` for cross-machine M code path compatibility
- **Phase 2 Remediation**: COMPLETE (A-F) in repo; template deployment COMPLETE
- **Arrest Data**: January 2026 processed (42 records); February partial export converted from .tab
- **Critical Lesson**: Repo M code output schemas have diverged from PBIX DAX model expectations. Do NOT replace entire query bodies. Only make targeted edits that preserve the original output schema.

---

## Recent Updates (2026-01-14)

### 2026-01-14: v1.7.0
- ✅ **Response Time ETL Enhanced Filtering** - Updated `response_time_monthly_generator.py` to v2.0.0
- ✅ Added JSON configuration file (`config/response_time_filters.json`) for centralized filter rules
- ✅ Added "How Reported" filter - excludes "Self-Initiated" records from response time calculations
- ✅ Added Category_Type filtering with inclusion override logic (14 incidents kept despite category exclusion)
- ✅ Added specific incident filtering (42 incidents excluded from non-filtered categories)
- ✅ Added comprehensive data verification step with quality checks
- ✅ Processing pipeline expanded from 6 steps to 12 steps for enhanced filtering
- ✅ Added `--config` command line argument for custom filter configuration path

### 2026-01-14: v1.5.0
- ✅ Fixed Summons ESU organizational structure update
- ✅ Updated Assignment_Master_V2.csv: OFFICE OF SPECIAL OPERATIONS → PATROL BUREAU (4 officers)
- ✅ Updated summons_all_bureaus.m M code to combine ESU with Patrol Division
- ✅ Fixed M code syntax errors (removed invalid backslashes, fixed file path formatting)
- ✅ ESU totals now correctly combined with Patrol Division in Power BI visuals

### 2026-01-13: v1.4.0
- ✅ Fixed December 2025 high values issue (file format conversion duplicates)
- ✅ Added file preference logic (process .xlsx only when multiple formats exist)
- ✅ Improved deduplication with parsed dates/hours for accurate matching
- ✅ Removed 32,749 duplicate rows preventing double/triple counting

### 2025-12-11
- ✅ Migrated PowerBI_Data to OneDrive
- ✅ Updated all path references
- ✅ Verified script filenames
- ✅ Created folder structure (docs, chatlogs)
- ✅ Organized documentation
- ✅ Initialized git repository
- ✅ Stabilized Overtime TimeOff: backfill + processed-month combined correctly (FIXED + monthly_breakdown)
- ✅ Verified Policy Training Delivery Cost: history matches backfill; ETL computes 11-25
- ✅ Verified Summons Dept-Wide Moving/Parking: history matches backfill; ETL computes 11-25 from e-ticket
- ✅ Fixed Summons blank Bureau row by injecting badge override for 1711 (WG2)

### 2025-12-09
- ✅ Initial workspace setup
- ✅ ETL orchestrator scripts created
- ✅ Configuration file created
- ✅ Basic documentation added

---

## Phase 2 Remediation Status — COMPLETE (2026-02-21)

| Priority | Task | Status |
|----------|------|--------|
| 0 | M Code `DateTime.LocalNow()` → `pReportMonth` parameter (20 files, 25 occurrences) | ✅ COMPLETE (repo + template) |
| 1 | Community Engagement validation | ✅ COMPLETE |
| 2 | Summons Derived Outputs (`IS_AGGREGATE`, `TICKET_COUNT`) | ✅ COMPLETE |
| 3 | Hardcoded paths in M Code — 9 instances fixed | ✅ COMPLETE (repo + template) |
| 4 | Hardcoded column lists — `___Patrol` & `___Traffic` missing `01-26` column | ✅ COMPLETE (repo) |
| 5 | Response Times historical backfill (Nov 2024 – Dec 2025) | PENDING |
| 6 | Deploy fixes to PBIX template (surgical approach) | ✅ **COMPLETE** |
| 7 | Refresh `summons_powerbi_latest.xlsx` with Oct 2025 – Jan 2026 data | **PENDING** (next ETL run) |

**Template deployment COMPLETE.** All surgical edits applied successfully. Staging data refresh needed for summons visuals.

---

## Support

**Configuration Issues:** Check `config\scripts.json`  
**Path Issues:** Run `.\verify_migration.ps1`  
**Script Issues:** Check logs in `logs\`  
**Documentation:** See `docs\` folder  

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

**Maintained by:** R. A. Carucci  
**Last Updated:** 2026-03-19  
**Version:** 1.18.14

---

## Recent Updates (2026-02-27)

### v1.17.19 — Peer-Review Corrections to Incident Exclusion List

- **9 types moved from EXCLUDED to INCLUDED:** Suspicious Person, Suspicious Vehicle, Missing Person - Adult, Missing Person - Juvenile, NARCAN Deployment - Juvenile - Aid, Overdose - Juvenile - Aid, Juvenile Complaint (Criminal), ESU - Response. All are citizen-initiated dispatched calls.
- **Juvenile NARCAN/Overdose inconsistency resolved:** Juvenile versions now consistent with adult equivalents (included).
- **`_normalize()` enhanced:** Explicit en-dash, em-dash, replacement-char handling added before non-ASCII sweep.
- Exclusion list: 280 → **272 normalized types**. Jan-26 Urgent: n=355 → 400, ratio 1.0×. All 18 metrics clean.
- **All 25 monthly CSVs regenerated.**

### v1.17.18 — Response Time Three-Layer Filter Expansion (Analyst Specification)

- **"How Reported" filter (NEW):** Retains citizen-initiated calls for service: 9-1-1, Phone (non-emergency line — alarms, break-ins, noise complaints), Walk-In. Excludes Self-Initiated, Radio, eMail, Fax, Mail, Virtual Patrol, Teletype, Other - See Notes, Canceled Call. Applied before dedup. Removes ~60–65% of CAD records.
- **Incident exclusion list expanded: 92 → ~234 types** — Analyst-confirmed list adds self-initiated enforcement (MV Violations, Traffic Violations, Field Contacts, targeted patrol variants), administrative processing, regulatory enforcement, special operations, and traffic infrastructure types.
- **Category_Type filter (NEW):** Safety-net filter excludes incidents mapping to "Administrative and Support" or "Community Engagement" in `CallType_Categories.csv`.
- **`_normalize()` updated:** Dashes and non-ASCII characters now replaced with space before whitespace collapse.
- **"101 types" stale comment fixed** in both scripts; runtime count logged at startup.
- **All 25 monthly CSVs regenerated.** Total annual records: 2025: 114,064 → 18,502 final (citizen-initiated).
- **Routine bimodal distribution resolved for Jan-26:** mean/median ratio 9.5× → 1.1× (median 0:13 → 3:19, n=1,075 → 388).
- **Comparison doc:** `docs/response_time/2026_02_27_PreFix_vs_PostFix_Comparison_v1.17.18.md`
- **Power BI refresh required.**

---

## Recent Updates (2026-02-26)

### v1.17.15 — First-Arriving-Unit Dedup Fix + ETL Re-run (Peer Review Findings)

- **Bug fixed: `response_time_batch_all_metrics.py`** — Added `sort_values(["ReportNumberNew", "Time Out"])` before `drop_duplicates()` in `load_and_clean()`. For the 28.2% of calls with multiple responding units, the script previously kept whichever row appeared first in the source Excel file instead of the first-arriving officer. Identified via Sonnet + Opus peer review (2026-02-26).
- **All 25 monthly CSVs regenerated** — `response_time_all_metrics\` 2024-01 through 2026-01 regenerated with corrected dedup logic. Emergency 01-26 Dispatch to On Scene corrected from 3:11 → 2:51 (−20 seconds). Routine values stable (1–3 second changes).
- **M code confirmed correct** — Both `___ResponseTime_OutVsCall.m` and `___ResponseTime_DispVsCall.m` already had the 13-month pReportMonth window (Opus Bug 2 finding was based on an older version; current files are correct). No code change required.
- **`process_cad_data_13month_rolling.py` confirmed** — v1.15.9 sort fix already present; added clarifying comment.
- **New docs created:**
  - `docs/response_time/2026_02_26_PreFix_vs_PostFix_Comparison.md` — Full delta table pre/post fix
  - `docs/response_time/RECORD_COUNT_MISMATCH_EXPLAINED.md` — Admin-facing explanation for different record counts per metric
  - `docs/response_time/POWERBI_REFRESH_REQUIRED_2026_02_26.md` — Refresh checklist (⏳ PENDING)
- **Power BI refresh required** — All three response time queries must be refreshed to reflect corrected CSVs.

---

## Recent Updates (2026-02-21)

### v1.17.1 — February 2026 Cycle Activation & Arrest .tab Support

- **pReportMonth advanced** — Updated from `#date(2026, 1, 1)` to `#date(2026, 2, 1)` for February reporting cycle
- **Arrest .tab conversion** — Lawsoft exports arrive as `.tab` (no headers); converted `2026_02_Lawsoft_Monthly_Arrest.tab` to `.xlsx` using January column headers (39 records, Feb 1–9)
- **___Arrest_Categories resolved** — Was blank because pReportMonth=Jan looked for Dec 2025 data (missing); advancing to Feb cycle now correctly finds Jan 2026 data (42 records)
- **___Overtime_Timeoff_v3 confirmed** — Populating correctly with pReportMonth parameter
- **ETL file discovery documented** — `arrest_python_processor.py` picks latest `.xlsx` by modification time; can grab wrong month if newer file exists

### v1.17.0 — M Code Reorganization and PBIX Baseline Export

- **M code folder restructure** — Reorganized `m_code/` from flat 76-file directory into 17 page-based subfolders matching Power BI report pages (arrests, benchmark, community, csb, detectives, drone, esu, functions, nibrs, overtime, parameters, patrol, response_time, shared, ssocc, stacp, summons, traffic, training)
- **PBIX baseline export** — Extracted all 45 Power Query M code queries from January 2026 monthly report PBIX into consolidated file (`all_m_code_26_january_monthly.m`, 4,197 lines), then split into individual `.m` files
- **Standardized headers** — All 45 `.m` files now include: EST timestamp, file path, Author: R. A. Carucci, purpose line
- **Archived stale files** — 53 superseded files (date-stamped snapshots, `_FIXED`/`_STANDALONE` variants, benchmark iterations) moved to `m_code/archive/2026_02_21_phase2_cleanup/`
- **Phase 2 discovery** — PBIX already has `RootExportPath` and `EtlRootPath` parameters; 7 queries have hardcoded broken paths (`C:\Dev` or `C:\Users\RobertCarucci`); 6 queries show warning icons in Power Query
- **Splitter script** — `scripts/split_mcode.py` automates consolidated M code parsing and distribution to page folders with headers
- **Pre-Flight Validation rewrite** — `scripts/Pre_Flight_Validation.py`: argparse `--report-month`, visual export mapping validation (36/25), evidence checks (file size, row count), GO/NO-GO JSON gate, path_config portability
- **Response Times stability** — `scripts/response_time_fresh_calculator.py` v3.1.0: argparse, path_config, first-arriving unit dedup fix (sort by Time Out before drop_duplicates)
- **Summons derived outputs** — `scripts/summons_derived_outputs_simple.py`: argparse, path_config, dynamic YYYY_MM filenames, IS_AGGREGATE column, TICKET_COUNT normalization, optional input warnings
- **Corrupted script fix** — `scripts/process_cad_data_13month_rolling.py` replaced with redirect stub (production at 02_ETL_Scripts/Response_Times/)
- **ReportMonth freeze (Phase 2 Task A)** — Created `pReportMonth` parameter; fixed 20 M code files (25 `DateTime.LocalNow()` occurrences); fixed 9 hardcoded paths; historical reports now frozen to their reporting period
- **Orchestrator manifest (Phase 2 Task C)** — `run_all_etl.ps1` accepts `-ReportMonth`, auto-calculates previous month, writes `_manifest.json` and `_manifest.csv` to `_DropExports`
- **Phase 2 Remediation COMPLETE** — All 6 tasks (A through F) finished; no `DateTime.LocalNow()` or hardcoded user paths remain in active M code

---

## Recent Updates (2026-02-20)

### v1.16.0 — Phase 2 Diagnostics, Assignment_Master V3, Schema Standards

#### Assignment_Master_V2 — Major Cleanup (Claude-in-Excel, 12 turns)
- **V3_FINAL.xlsx** created from `Assignment_Master_V2.csv` via 12-turn Claude-in-Excel session
- **Schema reduced**: 42 columns → 25 columns; 6 duplicate PEO rows removed; 166 active records
- **Renamed**: `POSS_CONTRACT_TYPE` → `CONTRACT_TYPE`, `Proposed 4-Digit Format` → `STANDARD_NAME`
- **Deleted**: `WG5`, `DEP_CHIEF`, seniority cols (×10), workgroup cols (×2), `FullName`, `Badge`, `Notes`
- **RANK**: 100% populated (28 blanks filled from TITLE; all values standardized)
- **TEAM**: 138 updates from POSS_EMPLOYEE merge; TC/DESK distinction added for platoon officers
- **Script fix**: `run_summons_with_overrides.py` updated — `WG5` removed, `POSS_CONTRACT_TYPE` → `CONTRACT_TYPE`
- **Archived**: `add_traffic_officers.py` moved to `scripts/_archive/` (deprecated one-off)

#### M Code DateTime.LocalNow() — Critical Architectural Issue Identified
- **Problem**: 20 M code files (35+ occurrences) use `DateTime.LocalNow()` for rolling windows
- **Impact**: Historical monthly reports show different data on each refresh — breaks data integrity
- **Fix**: Replace with `ReportMonth = #date(YYYY, M, 1)` parameter locked per reporting cycle
- **Guide**: `docs/M_CODE_DATETIME_FIX_GUIDE.md` — full audit table + Claude AI prompt ready
- **Scope**: `___Overtime_Timeoff_v3`, `___Arrest_Categories_FIXED`, `___Cost_of_Training`, ESU, STACP, Detectives, Summons standalone files, and the consolidated `2026_02_19_jan_m_codes.m`

#### Schema Standards Infrastructure
- `09_Reference/Personnel/Assignment_Master_SCHEMA.md` — fully rewritten (V2)
- `09_Reference/Standards/Personnel/` — new subdirectory created
- `09_Reference/Standards/Personnel/Assignment_Master_SCHEMA.md` — canonical mirror
- `09_Reference/Standards/Personnel/assignment_master.schema.json` — formal JSON Schema

---

## Recent Updates (2026-02-18)

### v1.15.9 — February 2026 ETL Cycle Response Times Fix ✅ DEPLOYED

- **Multi-Unit Deduplication**: Fixed `process_cad_data_13month_rolling.py` — sort by `['ReportNumberNew', 'Time Out']` before dedup (first-arriving unit, not file order)
- **January 2026 Results**: Emergency 3:11 (347 calls), Urgent 2:54 (843 calls), Routine 2:48 (853 calls)
- **Multi-unit Rate**: 28.2% — 2,939 duplicate units removed from 10,440 CAD records
- **CAD Mapping**: Created `CAD_CALL_TYPE.xlsx` from `CallType_Categories.csv` (649 mappings)
- **Visual Mapping**: 25/36 visuals enforce 13-month windows ✅

---

## Recent Updates (2026-02-23)

### v1.17.5 — Surgical Template Update COMPLETE

**All queries loading cleanly** — Close & Apply completes with zero errors.

**Changes applied to template:**
- Created `pReportMonth` parameter (Date, 2/1/2026)
- Fixed file paths in 4 queries (`ESU_13Month`, `summons_top5_parking`, `summons_top5_moving`, `___ResponseTimeCalculator`)
- Replaced `DateTime.LocalNow()` with `pReportMonth` in 6 queries (`summons_top5_moving`, `summons_all_bureaus`, `___Drone`, `___Traffic`, `___Social_Media`)
- Re-created missing `___Summons` query (fixes 12 DAX measure errors) with computed `TICKET_COUNT` and `ASSIGNMENT_FOUND` columns
- Added `Count` and `MonthName` columns to `___ResponseTimeCalculator` (fixes DAX SUMMARIZE errors)
- Fixed `summons_13month_trend`: removed 4 non-existent columns, added `TICKET_COUNT` computed column, deduplicated by `TICKET_NUMBER`
- Deleted 4 orphaned DAX calculated tables referencing non-existent `Arrest_Top` table

**Pending: Staging data refresh** — `summons_powerbi_latest.xlsx` only has data through September 2025. Summons visuals will populate correctly once the staging file is refreshed with Oct 2025 – Jan 2026 data by the next ETL run.

### v1.17.4 — Bulk M Code Paste Failed; Surgical Approach Executed

**Second bulk paste failed** — DAX schema mismatch. All changes discarded. Surgical approach successfully applied (see v1.17.5 above).

---

## Recent Updates (2026-02-22)

### v1.17.3 — Template Refresh & Laptop Path Resolution
- **Report template refreshed** from January 2026 published report; old broken template archived
- **Laptop path junction**: `C:\Users\carucci_r` → `C:\Users\RobertCarucci` for cross-machine compatibility
- **M code reorganization** (v1.17.2): 20 page-based subfolders; Drone/Social Media/Summons syntax fixes

---

## Recent Updates (2026-02-17)

- Consolidated Power BI visual export mapping into one canonical file
- Primary path: `Standards\config\powerbi_visuals\visual_export_mapping.json`
- Archived prior mapping files under `scripts\_archive\visual_export_mapping\2026_02_17_173019\`
