# Project: 06_Workspace_Management - ETL Script Orchestration & Power BI Integration

## What This Is
Centralized orchestration hub that runs all Python ETL scripts feeding into Power BI reports. Provides automated execution, error handling, logging, and Power BI integration for multiple data processing workflows including Arrests, Community Engagement, Overtime/TimeOff, Response Times, and Summons.

## First Time Here?
1. Read `README.md` for high-level overview
2. Check `SUMMARY.md` for quick reference and enabled scripts
3. Review `config/scripts.json` for script configuration
4. Run verification: `.\verify_migration.ps1` to check paths
5. Optional (desktop / Python): from repo root, `set PYTHONIOENCODING=utf-8` then `python etl_orchestrator.py --scorecard` — confirms `path_config` + config + validator reachability (see `docs/ETL_SKILL_MEMORY.md`)

## Tech Stack
- **Languages**: PowerShell, Python
- **Orchestration**: PowerShell scripts (`run_all_etl.ps1`); Python CLI (`etl_orchestrator.py` — list / dry-run / single-script run / log parse / validate / scorecard; does not replace PowerShell orchestrator)
- **Data Processing**: Python ETL scripts
- **Output Format**: CSV files
- **Reporting**: Power BI (via **PowerBI_Data** `_DropExports`, `Backfill`)
- **Storage**: OneDrive (cloud-backed)
- **Configuration**: JSON (config/scripts.json)
- **Parameter**: `pReportMonth` controls rolling windows in **Power Query (M)** only; in **DAX measures** use `MAX('___DimMonth'[MonthStart])` or a loaded parameters table (see `docs/POWER_BI_YTD_MEASURES_AND_PAGE_INSTRUCTIONS.md`)

## HTML Report Styles

When generating formatted HTML reports for Hackensack PD, use the design system in **`docs/templates/HPD_Report_Style_Prompt.md`**. That file is the canonical source for:

- **Color palette**: Navy (#1a2744), gold (#c8a84b), dark green (#2e7d32), dark red (#b71c1c)
- **Typography**: Segoe UI, Arial, sans-serif, 13.5px body (or Georgia for formal); h2 with gold underline
- **Structure**: Header band (navy + gold border) -> Meta bar -> Content -> Footer
- **Components**: `.alert`, `.alert.green`, `.summary-grid`, `.summary-box`, `.finding`, tables with navy headers
- **Author block**: R. A. Carucci #261 | Principal Analyst | Safe Streets Operations Control Center | Hackensack Police Department
- **Key Findings** (not "Bottom Line") for executive summary callouts
- **Document status colors**: `.status-draft`, `.status-review`, `.status-final`
- **Dynamic KPI arrows**: `.arrow-up` (▲), `.arrow-down` (▼)
- **Key Findings markup**: Use `<span class="alert-icon">&#9654;</span> <strong>Key Findings:</strong>` (icon in separate span to avoid PDF rendering issues)
- **Padding**: Header, meta-bar, content, footer use 24px horizontal padding (not 40px)
- **Line-height**: Body text `line-height: 1.4`
- **Print**: Include `@media print` with page-break rules for `.alert`, `.summary-grid`, `.summary-box`, `.signature`, `.footer`, `.header`, `.meta-bar`; footer overrides (9px font, 8px padding, 1.3 line-height)

**Rule**: Always use self-contained HTML. No external stylesheets, fonts, or scripts. All CSS inline in `<style>` block. Include `@media print` for clean printing.

## Current Status

| Item | Value |
|------|-------|
| **Version** | 1.19.7 |
| **Status** | v1.19.7: Documentation sync (SSOCC Option B M + rework doc, Community CE/STACP duration prompt, ETL_SKILL_MEMORY / handoffs). v1.19.6: Outreach M dual CSV/XLSX + YTD DAX doc. v1.19.5: `etl_orchestrator.py` + scorecard memory. |
| **pReportMonth** | Set per `.pbix` in Power Query (example: `#date(2026, 3, 1)` for March 2026 report) |
| **Enabled Scripts** | 5 (Arrests, Community, Overtime, Response Times, Summons) |
| **Power BI Queries** | 47+ queries; all use `pReportMonth` (zero `DateTime.LocalNow()`) |
| **Report Template** | `Monthly_Report_Template.pbix` under `08_Templates\` or `15_Templates\` (OneDrive layout; same gold-copy file) |
| **TMDL Export** | `m_code/tmdl_export/` (85 files, full model snapshot) |

### pReportMonth Migration (COMPLETE)
All 16 M code queries migrated from `DateTime.LocalNow()` to `pReportMonth` via Claude Desktop MCP on 2026-03-09. Each `.pbix` is now an immutable snapshot -- changing `pReportMonth` and saving-as produces a new month's report without altering historical files.

Standard window pattern applied uniformly:
```
EndOfWindow   = Date.EndOfMonth(pReportMonth)
StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12))
```

Migration prompt and transcripts: `docs/chatlogs/PROMPT_Claude_MCP_pReportMonth_Migration/` (chunked exports + `*_transcript.md`). Older single-file prompt may have been removed; use chatlog folder as source of truth.

### Power BI Desktop MCP (Cursor)
- Optional project file: `.cursor/mcp.json` registers **powerbi-modeling-mcp** for this repo (machine-specific path to `powerbi-modeling-mcp.exe`). User-level config: `%USERPROFILE%\.cursor\mcp.json`. Connect to an open `.pbix` via `localhost:<port>` (discover port with MCP **ListLocalInstances** when Desktop has the model open).

### Response Time ETL (updated)
- `response_time_batch_all_metrics.py` v1.17.21 -- dynamic source discovery, NaT coercion monitoring, per-type configurable bounds
- `___ResponseTime_AllMetrics.m` -- 13-month window uses `EndOfMonth(pReportMonth)` (project standard); X-axis MM-YY; RT Avg Formatted measure for M:SS display
- Data dictionary: `09_Reference/Standards/ResponseTime_AllMetrics_DataDictionary.md` (and `.json`)

### DFR Summons (m_code/drone/DFR_Summons.m)
- **Source:** `dfr_directed_patrol_enforcement.xlsx` (Claude in Excel workbook)
- **Columns:** MM-YY (matrix display), Date_Sort_Key (sort-by-column), DateSortKey (YYYYMMDD), YearMonthKey; Description shortened ("Parking...designated X" → "X"); Violation_Type P/M/C
- **Filter:** Dual filter — (1) Summons_Recall containing "Dismiss" or "Void"; (2) Summons_Status containing "dismiss" or "void" (catches Dismissed, Void, Voided); en-US locale for text parsing
- **ETL population (this repo):** `run_summons_etl.py` → `split_dfr_records()` → **`scripts/dfr_export.py`** appends DFR rows to the workbook (dedup on Summons Number; skips Excel formula columns). Badge/date rules live in **`scripts/summons_etl_normalize.py`** (`DFR_ASSIGNMENTS`). A separate **`02_ETL_Scripts/Summons/summons_etl_enhanced.py`** may exist on disk for other workflows; **orchestrated path here is `run_summons_etl.py`.**
- **Docs:** `docs/DFR_Summons_Claude_Excel_Development_Log.md` (29-turn history); `docs/summons_ETL Enhancement.py` (enhancement plan)

### Policy Training queries (m_code/training/)
- **`___In_Person_Training.m`** — **`Policy_Training_Monthly.xlsx`** under `Shared Folder/Compstat/Contributions/Policy_Training/`; sheet **`Training_Log`** (fallback **`Training_Log_Clean`**). Loads **all** in-person rows; **YTD** = DAX on `Start date` (see `docs/POWER_BI_YTD_MEASURES_AND_PAGE_INSTRUCTIONS.md`).
- **`___Cost_of_Training.m`** — **`02_ETL_Scripts/Policy_Training_Monthly/output/policy_training_outputs.xlsx`**, sheet **`Delivery_Cost_By_Month`**. M keeps **13-month rolling** periods **and** **calendar YTD** months through **`pReportMonth`** so YTD cost cards resolve (incl. January report month).

## Project Map

### Active Code
- `etl_orchestrator.py` (repo root) - Python ETL inspection wrapper: `--list`, `--dry-run`, `--run --script <name>`, `--parse-logs`, `--validate`, `--scorecard`; read-only `config/scripts.json`; paths via `scripts/path_config.py`
- `scripts/run_all_etl.ps1` - Main PowerShell orchestrator
- `scripts/run_all_etl.bat` - Batch wrapper
- `scripts/run_etl_script.ps1` - Individual script runner
- `scripts/path_config.py` - `get_onedrive_root()`, `get_powerbi_data_dir()` (repo `config.json` / `PowerBI_Data`), `get_powerbi_paths()` from `scripts.json`
- `scripts/overtime_timeoff_with_backfill.py` - Overtime/TimeOff monthly wrapper
- `scripts/validate_exports.py` - Pre-flight check for OT/TimeOff exports
- `scripts/validate_outputs.py` - CSV schema validation
- `scripts/test_pipeline.bat` - Overtime/TimeOff test suite
- `scripts/summons_etl_normalize.py` - Summons ETL v2.5.0; `DFR_ASSIGNMENTS` + `split_dfr_records()` + `apply_fine_amount_and_violation_category()` (Penalty + municipal fee schedule on STATUTE)
- `scripts/dfr_export.py` - DFR workbook export; `_map_to_dfr_schema()`, `export_to_dfr_workbook()`
- `scripts/dfr_backfill_descriptions.py` - DFR description/fine backfill; cascading statute lookup
- `run_summons_etl.py` - Path-agnostic summons wrapper; DFR split + export wired in
- `scripts/summons_backfill_merge.py` - Merge gap months into summons
- `scripts/normalize_visual_export_for_backfill.py` - Visual export normalization; `--enforce-13-month` with optional `--13m-window-ends YYYY-MM` (exclude partial months after window end)
- `scripts/process_powerbi_exports.py` - _DropExports → Processed_Exports + Backfill (routing, archive; `--scan-processed-exports-inbox`; `--report-month` → normalizer `--13m-window-ends` for 13-month filter end)
- `scripts/processed_exports_routing.py` - Canonical folder aliases, `resolve_category_directory`, `prepare_destination_file` / archive under `archive/YYYY_MM/` or `undated`
- `scripts/canonicalize_processed_exports_layout.py` - Optional on-disk fix: merge `traffic_mva`/mixed `Traffic` → `traffic`, detective & STACP splits → `detectives` / `stacp`, PascalCase → lowercase (`Benchmark`→`benchmark`, `Drone`→`drone`, etc.)
- `scripts/validate_13_month_window.py` - 13-month validator (`--report-month`, `--accept-warn`, partial tail WARN)
- `scripts/validate_response_time_exports.py` - Response_time CSV structure checks
- `scripts/tests/` - `unittest` for routing, archive, validators (`python -m unittest discover -s tests -p "test_*.py"`)
- `config.json` (repo root, optional) - `"PowerBI": "PowerBI_Data"` for data root folder name
- `verify_migration.ps1` - Path verification

### Data Directories
- `config/` - Configuration (scripts.json, response_time_filters.json)
- `scripts/` - Execution scripts and Python helpers
- `logs/` - ETL execution logs (auto-created)
- `docs/` - Documentation, prompts, chatlogs (incl. `ETL_SKILL_MEMORY.md` — orchestrator scorecard evidence)
- `m_code/` - Power BI M code queries (47+ queries across 20 subfolders)
  - `arrests/`, `benchmark/`, `chief/`, `community/`, `csb/`, `detectives/`, `drone/`, `esu/`, `functions/`, `nibrs/`, `overtime/`, `parameters/`, `patrol/`, `remu/`, `response_time/`, `shared/`, `social_media/`, `ssocc/`, `stacp/`, `summons/`, `traffic/`, `training/`
  - `ssocc/FactServiceLog.m` + `ssocc/DimServiceGroup.m` — SSOCC Option B (row-level logs + dimension); legacy MoM query remains `___SSOCC_Data.m` until `.pbix` migration
  - `drone/DFR_Summons.m` - Rolling 13-month window, dual dismiss/void filter (Recall + Status), schema-resilient Violation_Category/Jurisdiction
  - `archive/` - Superseded M code versions
- `outputs/` - Organized output files (arrests, visual_exports, summons_validation, metadata, community_engagement, misc, large_exports)
- `verifications/` - ETL verification framework

### Key Documentation
- `README.md` - Project overview
- `SUMMARY.md` - Quick reference
- `docs/ETL_SKILL_MEMORY.md` - Python `etl_orchestrator.py` audit trail / scorecard evidence
- `CHANGELOG.md` - Full version history (detailed logs live here, not in this file)
- `docs/chatlogs/PROMPT_Claude_MCP_pReportMonth_Migration/` - pReportMonth M migration transcripts and chunks
- `docs/PROMPT_Claude_Desktop_Monthly_Report_Template_MCP.md` - Claude Desktop prompts for template + MCP
- `docs/handoffs/HANDOFF_PowerBI_MCP_2026_03_23.md` - Session handoff for Power BI MCP, DAX/`pReportMonth`, Arrest YTD matrix
- `docs/handoffs/HANDOFF_Community_Outreach_PBIX_2026_03_25.md` - Community outreach PBIX / Combined_Outreach / CE ETL handoff
- `docs/POST_SESSION_ACTION_ITEMS.md` - After MCP: save pbix, Close & Apply, Summons ETL, manual PQ steps
- `docs/TASKS_A_THROUGH_F_DELIVERABLE.md` - YTD card placement, Summons_YTD page, page renames, Response Time + DFR specs
- `docs/13_MONTH_WINDOW_IMPLEMENTATION_GUIDE.md` - Rolling window deployment
- `docs/M_CODE_DATETIME_FIX_GUIDE.md` - DateTime.LocalNow() audit
- `docs/MONTHLY_REPORT_TEMPLATE_WORKFLOW.md` - Template workflow and checklist
- `docs/SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md` - Summons columns, **`apply_fine_amount_and_violation_category`**, slim CSV
- `docs/SUMMONS_PATHS_AND_DROPEXPORTS.md` - Staging paths vs `_DropExports` (Summons uses `03_Staging`, not DropExports)
- `docs/POLICY_TRAINING_AUTOMATION_AND_COST_VISUAL.md` - Policy Training ETL location; **`___In_Person_Training`** / **`___Cost_of_Training`** M behavior
- `docs/POWER_BI_YTD_MEASURES_AND_PAGE_INSTRUCTIONS.md` - YTD DAX patterns; **`pReportMonth`** not valid bare in DAX; training PQ notes
- `docs/SSOCC_Service_Log_Excel_And_Power_BI_Rework_2026_03.md` - SSOCC Service Log workbook (`T_YYYY_MM`, `DimServiceGroup`), Option B Power Query + DAX migration; source chat: `KB_Shared\04_output\ssocc_claude_in_excel_rework\`
- `docs/cursor_prompt_fix_duration_and_attendees.md` - Community ETL duration → decimal hours + STACP attendee normalization (live code under `02_ETL_Scripts/Community_Engagment/`)
- `docs/ESU_POWER_BI_LOAD_AND_PUBLISH.md` - ESU query docs
- `docs/PROMPT_ETL_Export_Reliability_Diagnostic_Enhanced.md` - ETL export diagnostic prompt (full paths)
- `docs/PROMPT_Claude_MCP_Create_Missing_Visuals_For_Monthly_Report.md` - Claude MCP prompt for Response Time + DFR visuals
- `docs/PROMPT_Claude_MCP_Response_Time_Visuals.md` - Dedicated Response Time prompt (KPI cards, Line chart, Matrix; Option B layout)
- `docs/PROMPT_Claude_MCP_Response_Time_Line_Chart_Time_Format.md` - MCP prompt for line chart M:SS formatting (RT Avg Formatted)
- `docs/Visual_Build_Guide_YYYY_MM.md` - MCP-generated manual build guide (e.g., Visual_Build_Guide_2026_02.md, Visual_Build_Guide_2026_02_v2.md)
- `docs/PROMPT_Claude_In_Excel_DFR_Directed_Patrol_Summons_MCode.md` - DFR Summons M code (13-month window, Dismiss/Void filter)
- `docs/DFR_Summons_Claude_Excel_Development_Log.md` - Claude in Excel development history (29 turns, workbook evolution)
- `docs/templates/HPD_Report_Style_Prompt.md` - HTML report design system
- `09_Reference/Standards/ResponseTime_AllMetrics_DataDictionary.md` - Response Time schema
- `14_Workspace/chatlogs/Directory_Consolidation_Documentation_Update_And_Commit/` - Directory consolidation session (transcript + chunks): canonical path refactors, `PowerBI_Data`, template folder moves (`08_Templates`), Phase 4 M batch context; pair with `_consolidation_project/IMPLEMENTATION_CHECKLIST_Directory_Consolidation.md`

## How to Work on This Project

### Before Making Changes
1. Check `config/scripts.json` for script configurations
2. Review `SUMMARY.md` for enabled scripts
3. Review relevant docs in `docs/` for context
4. Run `.\verify_migration.ps1` to ensure paths are correct
5. After path or config changes on a new machine, run `python etl_orchestrator.py --scorecard` (use `PYTHONIOENCODING=utf-8` on Windows if the console throws Unicode errors)

### Example Workflow
**Task**: Add a new ETL script to the orchestration
1. Read `README.md` for configuration structure
2. Add script entry to `config/scripts.json`
3. Test with: `.\scripts\run_etl_script.ps1 -ScriptName "ScriptName"`
4. Verify output appears in Power BI drop folder
5. Run full suite: `.\scripts\run_all_etl.ps1`
6. Check logs in `logs/`
7. Commit changes

### Code Standards
- Use structured logging
- Implement error handling (scripts run independently)
- Update `CHANGELOG.md` when adding features
- Maintain `config/scripts.json` structure
- Document script-specific details in `docs/`

### Finding Information
- **Core orchestration**: `scripts/run_all_etl.ps1`, `scripts/run_etl_script.ps1`, `etl_orchestrator.py` (Python inspection / scorecard)
- **Configuration**: `config/scripts.json`, `README.md`, `SUMMARY.md`
- **ETL Scripts**: Individual scripts in `02_ETL_Scripts/` (referenced by config)
- **Documentation**: `docs/` folder
- **Full history**: `CHANGELOG.md`

## Protected Resources
**Do not modify without explicit confirmation:**
- `config/scripts.json` (critical ETL config)
- Production ETL scripts in `02_ETL_Scripts/` (referenced, not stored here)
- Power BI integration paths (OneDrive-based)
- `CHANGELOG.md` (append-only)

## Common Pitfalls
- **Don't** modify production ETL scripts directly -- they live in `02_ETL_Scripts/`
- **Always** check `config/scripts.json` before modifying script configurations
- **Remember** to verify paths after changes using `.\verify_migration.ps1`
- **Use** dry-run mode (`-DryRun`) to preview execution before running
- **Verify** OneDrive sync status before assuming files are available
- **Never** use `DateTime.LocalNow()` in M code -- use `pReportMonth` parameter

## Never Do
- Use `DateTime.LocalNow()` in M code — use `pReportMonth` only
- Hardcode OneDrive paths — always use `path_config.get_onedrive_root()`
- Modify `config/scripts.json` without explicit confirmation from user
- Write directly to `02_ETL_Scripts/` — those are production scripts
- Commit `.log` files or `.xlsx` test/diagnostic files to git

## Log File Locations
| Log File | Location |
|----------|----------|
| ETL orchestration | `logs/run_all_etl_YYYYMMDD.log` |
| Summons ETL | `logs/summons_etl.log` |
| Arrest processor | `logs/arrest_processor.log` |
| Tree report errors | `logs/tree_report_error.log` |

All new scripts must write logs to `logs/` — never to the repo root.

## Enabled ETL Scripts
1. **Arrests** - `arrest_python_processor.py` (--report-month {REPORT_MONTH_ACTUAL}; targeted discovery in YYYY/month/)
2. **Community Engagement** - `src/main_processor.py` (Patrol v2, attendee_names column)
3. **Overtime TimeOff** - `overtime_timeoff_with_backfill.py`
4. **Response Times** - `response_time_diagnostic.py`
5. **Summons** - `main_orchestrator.py`

## Key Paths
Paths are portable: set `ONEDRIVE_BASE` (or `ONEDRIVE_HACKENSACK`) to override. Python uses `path_config.get_onedrive_root()`; PowerShell uses `$OneDriveBase`.

### 06_Workspace_Management (workspace root)
| Path | Purpose |
|------|---------|
| `C:\Users\carucci_r\OneDrive - City of Hackensack\06_Workspace_Management` | Workspace root |
| `06_Workspace_Management\config\scripts.json` | ETL configuration; `powerbi_drop_path` |
| `06_Workspace_Management\logs\` | Execution logs |
| `06_Workspace_Management\scripts\process_powerbi_exports.py` | Process _DropExports → Processed_Exports + Backfill |
| `06_Workspace_Management\scripts\normalize_visual_export_for_backfill.py` | Visual export normalization |
| `06_Workspace_Management\scripts\path_config.py` | Path resolution (`get_onedrive_root`, `get_powerbi_data_dir`, `get_powerbi_paths`) |
| `06_Workspace_Management\config.json` | Optional `PowerBI` folder name under OneDrive root |
| `06_Workspace_Management\Standards\config\powerbi_visuals\visual_export_mapping.json` | Export-to-folder mapping |
| `06_Workspace_Management\Standards\config\powerbi_visuals\schema_v2.json` | Archive/cleaning rules |
| `06_Workspace_Management\m_code\` | Power BI M code (47 queries, 87 TMDL export) |
| `06_Workspace_Management\docs\` | Documentation, prompts, chatlogs |

### PowerBI_Data (Power BI data root)
| Path | Purpose |
|------|---------|
| `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data` | Power BI data root |
| `PowerBI_Data\_DropExports` | Power BI visual exports land here (drop zone) |
| `PowerBI_Data\Backfill\{YYYY_MM}\{folder}\` | Backfill copies (vcs_time_report, summons, response_time, etc.) |
| `PowerBI_Data\Archive\{YYYY}\{MonthName}\` | Archived visual exports (with `--archive`) |
| `PowerBI_Data\Backfill\{YYYY_MM}\vcs_time_report\` | Monthly accrual (overtime_timeoff_with_backfill reads) |
| `PowerBI_Data\Backfill\{YYYY_MM}\summons\` | Summons backfill (summons_backfill_merge reads) |

### OneDrive (shared)
| Path | Purpose |
|------|---------|
| `<OneDrive>\09_Reference\Standards\Processed_Exports\{target_folder}\` | Renamed/moved exports (nibrs, arrests, summons, etc.) |
| `<OneDrive>\02_ETL_Scripts\*` | ETL script directories |
| `<OneDrive>\08_Templates\Monthly_Report_Template.pbix` | Gold copy template |
| `<OneDrive>\Shared Folder\Compstat\Monthly Reports\YYYY\MM_monthname\` | Published reports |
| `<OneDrive>\09_Reference\Standards\` | Schema standards and data dictionaries |
| `<OneDrive>\05_EXPORTS\_Arrest\YYYY\month\` | Monthly arrest exports (YYYY_MM_*.xlsx; matches Summons scaffolding) |
| `<OneDrive>\01_DataSources\ARREST_DATA\Power_BI\` | Arrest processor output (YYYY_MM_Arrests_PowerBI_Ready.xlsx) |

## Architecture Notes

### Laptop Path Junction
M code references `C:\Users\carucci_r\...` (desktop). Laptop has `C:\Users\RobertCarucci\...`. A Windows junction (`mklink /J`) enables path compatibility without modifying M code.

### Personnel Master
`Assignment_Master_V3_FINAL.xlsx` (25 cols, 166 records). Schema at `09_Reference/Personnel/Assignment_Master_SCHEMA.md`. Sync scripts in `09_Reference/Personnel/scripts/`.

### 13-Month Rolling Window
24 of 32 Power BI visuals enforce exactly 13 full months. Config at `Standards/config/powerbi_visuals/visual_export_mapping.json`. Validation script: `scripts/validate_13_month_window.py`.

## Path Resolution

OneDrive root resolves via two junctions (created 2026-03-22):
1. Profile junction:
     C:\Users\carucci_r  →  C:\Users\RobertCarucci
2. OneDrive junction (laptop only — must be replicated on desktop):
     C:\Users\RobertCarucci\OneDrive
     →  C:\Users\RobertCarucci\OneDrive - City of Hackensack

Active root returned by path_config.get_onedrive_root():
  C:\Users\carucci_r\OneDrive - City of Hackensack

### Rules for AI agents
- DO NOT change carucci_r to RobertCarucci in scripts or configs
- DO NOT change PowerBI_Data to PowerBI_Date (PowerBI_Date was the typo)
- scripts.json uses carucci_r paths — this is correct and intentional
- path_config.py resolves the correct root at runtime via get_onedrive_root()
- If a path appears broken, check junction status before editing any file

---

*Last updated: 2026-03-25 | Format version: 4.4*
