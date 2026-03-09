# Project: Master_Automation - ETL Script Orchestration & Power BI Integration

## What This Is
Centralized orchestration hub that runs all Python ETL scripts feeding into Power BI reports. Provides automated execution, error handling, logging, and Power BI integration for multiple data processing workflows including Arrests, Community Engagement, Overtime/TimeOff, Response Times, and Summons.

## First Time Here?
1. Read `README.md` for high-level overview
2. Check `SUMMARY.md` for quick reference and enabled scripts
3. Review `config/scripts.json` for script configuration
4. Run verification: `.\verify_migration.ps1` to check paths

## Tech Stack
- **Languages**: PowerShell, Python
- **Orchestration**: PowerShell scripts (run_all_etl.ps1)
- **Data Processing**: Python ETL scripts
- **Output Format**: CSV files
- **Reporting**: Power BI (via _DropExports folder)
- **Storage**: OneDrive (cloud-backed)
- **Configuration**: JSON (config/scripts.json)
- **Parameter**: `pReportMonth` controls all rolling windows (static snapshot per .pbix)

## HTML Report Styles

When generating formatted HTML reports for Hackensack PD, use the design system in **`docs/templates/HPD_Report_Style_Prompt.md`**. That file is the canonical source for:

- **Color palette**: Navy (#1a2744), gold (#c8a84b), dark green (#2e7d32), dark red (#b71c1c)
- **Typography**: Georgia, serif, 13.5px body; h2 with gold underline
- **Structure**: Header band (navy + gold border) -> Meta bar -> Content -> Footer
- **Components**: `.alert`, `.alert.green`, `.summary-grid`, `.summary-box`, `.finding`, tables with navy headers

**Rule**: Always use self-contained HTML. No external stylesheets, fonts, or scripts. All CSS inline in `<style>` block. Include `@media print` for clean printing.

## Current Status

| Item | Value |
|------|-------|
| **Version** | 1.17.31 |
| **Status** | pReportMonth migration COMPLETE; all queries verified |
| **pReportMonth** | `#date(2026, 2, 1)` |
| **Enabled Scripts** | 5 (Arrests, Community, Overtime, Response Times, Summons) |
| **Power BI Queries** | 46+ queries; all use `pReportMonth` (zero `DateTime.LocalNow()`) |
| **Report Template** | `15_Templates\Monthly_Report_Template.pbix` |
| **TMDL Export** | `m_code/tmdl_export/` (85 files, full model snapshot) |

### pReportMonth Migration (COMPLETE)
All 16 M code queries migrated from `DateTime.LocalNow()` to `pReportMonth` via Claude Desktop MCP on 2026-03-09. Each `.pbix` is now an immutable snapshot -- changing `pReportMonth` and saving-as produces a new month's report without altering historical files.

Standard window pattern applied uniformly:
```
EndOfWindow   = Date.EndOfMonth(pReportMonth)
StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12))
```

Migration prompt preserved at `docs/PROMPT_Claude_MCP_pReportMonth_Migration.md` for reference.

### Response Time ETL (updated)
- `response_time_batch_all_metrics.py` v1.17.21 -- dynamic source discovery, NaT coercion monitoring, per-type configurable bounds
- Data dictionary: `09_Reference/Standards/ResponseTime_AllMetrics_DataDictionary.md` (and `.json`)

## Project Map

### Active Code
- `scripts/run_all_etl.ps1` - Main PowerShell orchestrator
- `scripts/run_all_etl.bat` - Batch wrapper
- `scripts/run_etl_script.ps1` - Individual script runner
- `scripts/path_config.py` - Centralized get_onedrive_root() (ONEDRIVE_BASE / ONEDRIVE_HACKENSACK)
- `scripts/overtime_timeoff_with_backfill.py` - Overtime/TimeOff monthly wrapper
- `scripts/validate_exports.py` - Pre-flight check for OT/TimeOff exports
- `scripts/validate_outputs.py` - CSV schema validation
- `scripts/test_pipeline.bat` - Overtime/TimeOff test suite
- `scripts/summons_etl_normalize.py` - Summons ETL v2.3.0
- `run_summons_etl.py` - Path-agnostic summons wrapper
- `scripts/summons_backfill_merge.py` - Merge gap months into summons
- `scripts/normalize_visual_export_for_backfill.py` - Visual export normalization
- `scripts/process_powerbi_exports.py` - Power BI export processing
- `scripts/validate_13_month_window.py` - 13-month window validator
- `verify_migration.ps1` - Path verification

### Data Directories
- `config/` - Configuration (scripts.json, response_time_filters.json)
- `scripts/` - Execution scripts and Python helpers
- `logs/` - ETL execution logs (auto-created)
- `docs/` - Documentation, prompts, chatlogs
- `m_code/` - Power BI M code queries (46 queries across 20 subfolders)
  - `arrests/`, `benchmark/`, `chief/`, `community/`, `csb/`, `detectives/`, `drone/`, `esu/`, `functions/`, `nibrs/`, `overtime/`, `parameters/`, `patrol/`, `remu/`, `response_time/`, `shared/`, `social_media/`, `ssocc/`, `stacp/`, `summons/`, `traffic/`, `training/`
  - `archive/` - Superseded M code versions
- `outputs/` - Organized output files (arrests, visual_exports, summons_validation, metadata, community_engagement, misc, large_exports)
- `verifications/` - ETL verification framework

### Key Documentation
- `README.md` - Project overview
- `SUMMARY.md` - Quick reference
- `CHANGELOG.md` - Full version history (detailed logs live here, not in this file)
- `docs/PROMPT_Claude_MCP_pReportMonth_Migration.md` - 16-query M code migration prompt
- `docs/13_MONTH_WINDOW_IMPLEMENTATION_GUIDE.md` - Rolling window deployment
- `docs/M_CODE_DATETIME_FIX_GUIDE.md` - DateTime.LocalNow() audit
- `docs/MONTHLY_REPORT_TEMPLATE_WORKFLOW.md` - Template workflow and checklist
- `docs/ESU_POWER_BI_LOAD_AND_PUBLISH.md` - ESU query docs
- `docs/templates/HPD_Report_Style_Prompt.md` - HTML report design system
- `09_Reference/Standards/ResponseTime_AllMetrics_DataDictionary.md` - Response Time schema

## How to Work on This Project

### Before Making Changes
1. Check `config/scripts.json` for script configurations
2. Review `SUMMARY.md` for enabled scripts
3. Review relevant docs in `docs/` for context
4. Run `.\verify_migration.ps1` to ensure paths are correct

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
- **Core orchestration**: `scripts/run_all_etl.ps1`, `scripts/run_etl_script.ps1`
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

## Enabled ETL Scripts
1. **Arrests** - `arrest_python_processor.py`
2. **Community Engagement** - `src/main_processor.py` (Patrol v2, attendee_names column)
3. **Overtime TimeOff** - `overtime_timeoff_with_backfill.py`
4. **Response Times** - `response_time_diagnostic.py`
5. **Summons** - `main_orchestrator.py`

## Key Paths
Paths are portable: set `ONEDRIVE_BASE` (or `ONEDRIVE_HACKENSACK`) to override. Python uses `path_config.get_onedrive_root()`; PowerShell uses `$OneDriveBase`.

| Path | Purpose |
|------|---------|
| `Master_Automation` | Workspace root |
| `config\scripts.json` | ETL configuration |
| `logs\` | Execution logs |
| `<OneDrive>\PowerBI_Date\_DropExports` | Power BI drop folder |
| `<OneDrive>\02_ETL_Scripts\*` | ETL script directories |
| `<OneDrive>\15_Templates\Monthly_Report_Template.pbix` | Gold copy template |
| `<OneDrive>\Shared Folder\Compstat\Monthly Reports\YYYY\MM_monthname\` | Published reports |
| `<OneDrive>\09_Reference\Standards\` | Schema standards and data dictionaries |

## Architecture Notes

### Laptop Path Junction
M code references `C:\Users\carucci_r\...` (desktop). Laptop has `C:\Users\RobertCarucci\...`. A Windows junction (`mklink /J`) enables path compatibility without modifying M code.

### Personnel Master
`Assignment_Master_V3_FINAL.xlsx` (25 cols, 166 records). Schema at `09_Reference/Personnel/Assignment_Master_SCHEMA.md`. Sync scripts in `09_Reference/Personnel/scripts/`.

### 13-Month Rolling Window
24 of 32 Power BI visuals enforce exactly 13 full months. Config at `Standards/config/powerbi_visuals/visual_export_mapping.json`. Validation script: `scripts/validate_13_month_window.py`.

---

*Last updated: 2026-03-09 | Format version: 4.0*
