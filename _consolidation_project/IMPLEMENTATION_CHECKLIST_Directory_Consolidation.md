# Implementation Checklist: Directory Consolidation and Prefix Cleanup

**Project:** Streamline file structure, consolidate templates/themes/styles, fix PowerBI naming, and assign number prefixes.

**Architectural Decisions (Locked):**
1. Use **08_Templates** (not 08_Styles_And_Templates) as the single canonical directory for themes, styles, and templates.
2. **No symlinks/junctions** — hard rename `Master_Automation` → `06_Workspace_Management`; reuse freed `06` prefix (06_Documentation was emptied and deleted). This new folder acts as the master hub for the entire OneDrive workspace.
3. **PowerBI_Date → PowerBI_Data** — rename globally; update `path_config.py` and all dependent scripts.
4. **Archive 04_PowerBI** → `99_Archive\04_PowerBI_Dev_2026_03`.
5. **01_SourceData → 01_Raw_Source_Data** — clarify it is strictly for flat file drops.
6. **Centralized config** — single `config.json` at `06_Workspace_Management\config.json`; relative paths only; both Python and PowerShell parse it. Use `Path.home()` / `$HOME` + `BaseDirectory` for portability across users/machines.
7. **Workspace:** Keep OneDrive root as Cursor workspace for full codebase visibility. All consolidation artifacts live in `06_Workspace_Management\_consolidation_project\`.

---

## Phase 0: Scaffolding (Before Phase 1)

**Execute first.** Creates `_consolidation_project` and relocates project artifacts so they do not clutter the OneDrive root

| Step | Task | Type | Notes |
|------|------|------|-------|
| 0.1 | **Create `_consolidation_project` folder** inside `Master_Automation\` (before rename; after Phase 2 it becomes `06_Workspace_Management\_consolidation_project\`). | **Automated via Cursor** | `mkdir "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\_consolidation_project"` |
| 0.2 | **Move this checklist** from OneDrive root to `Master_Automation\_consolidation_project\IMPLEMENTATION_CHECKLIST_Directory_Consolidation.md`. | **Automated via Cursor** | `Move-Item "C:\...\IMPLEMENTATION_CHECKLIST_Directory_Consolidation.md" "C:\...\Master_Automation\_consolidation_project\"` |
| 0.3 | **Create Find-OldPaths.ps1** in `Master_Automation\_consolidation_project\` (see Appendix A). Update script to export `Path_Refactor_Audit.csv` to `_consolidation_project` folder, not OneDrive root. | **Automated via Cursor** | Script location: `Master_Automation\_consolidation_project\Find-OldPaths.ps1`; CSV output: same folder. |
| 0.4 | **Run Find-OldPaths.ps1** to generate `Path_Refactor_Audit.csv` in `_consolidation_project`. | **Automated via Cursor** | Output: `Master_Automation\_consolidation_project\Path_Refactor_Audit.csv` |

**Note:** After Phase 2 renames `Master_Automation` → `06_Workspace_Management`, the final path is `06_Workspace_Management\_consolidation_project\`.

---

## Phase 1: Pre-requisites & Risk Audit (Manual Tasks)

| Step | Task | Type | Notes |
|------|------|------|-------|
| 1.1 | **Backup OneDrive root** — Create a full backup or snapshot of `C:\Users\carucci_r\OneDrive - City of Hackensack\` before any changes. | **Manual** | Use Windows Backup, robocopy, or OneDrive version history. |
| 1.2 | **Run Find-OldPaths.ps1** — Execute the script in `Master_Automation\_consolidation_project\` (created in Phase 0). CSV outputs to same folder. Use as punch list for Phase 4. | **Automated via Cursor** | Script scans .py, .ps1, .json, .md, etc. for legacy paths. Output: `_consolidation_project\Path_Refactor_Audit.csv`. |
| 1.3 | **Audit dynamic path construction** — Search for patterns that build paths from variables (e.g., `os.path.join(DIR, f"{prefix}_Templates")`, `Join-Path $base "15_Templates"`, `Path(base) / "PowerBI_Date"`). | **Manual** | Grep: `os.path.join`, `Path(`, `Join-Path`, `+ "\\"`, `+ "/"`. Document each file and line. |
| 1.4 | **Audit Windows path escaping** — Search for `\` (single backslash) in path strings that may break in Python/JSON; verify `r"..."` or `\\` usage. | **Manual** | Check: `"C:\Users\..."` (bad) vs `r"C:\Users\..."` or `"C:\\Users\\..."` (good). |
| 1.5 | **List all scripts importing `path_config`** — Identify every Python file that uses `path_config.py` or `get_powerbi_paths()`. | **Automated via Cursor** | Grep: `from path_config import`, `import path_config`, `get_powerbi_paths`, `get_onedrive_root`. |
| 1.6 | **List all scripts referencing `scripts.json`** — Identify every file that reads `config/scripts.json` or `powerbi_drop_path`. | **Automated via Cursor** | Grep: `scripts.json`, `powerbi_drop_path`. |
| 1.7 | **Verify no active OneDrive sync conflicts** — Ensure OneDrive is fully synced and no files are "in use" or pending. | **Manual** | Check OneDrive status icon; close Power BI Desktop, Excel, and any scripts using these paths. |
| 1.8 | **Document M code / Power Query hardcoded paths** — List all `.m` and `.tmdl` files with `Folder.Files(`, `File.Contents(` containing full paths. | **Automated via Cursor** | Grep in `Master_Automation\m_code\` and `Master_Automation\m_code\tmdl_export\` for `OneDrive - City of Hackensack`. |
| 1.9 | **Create risk register** — For each path change, note: affected scripts, M code (requires Power BI Desktop refresh), and docs. Use `Path_Refactor_Audit.csv` from step 1.2. | **Manual** | Use output of steps 1.2–1.8. |

---

## Phase 2: Directory Renames & Moves (Filesystem Tasks)

**Execute in exact order. All tasks are Manual in the Filesystem unless noted.**

| Step | Task | Type | Exact Command / Action |
|------|------|------|-------------------------|
| 2.1 | **Delete empty 06_Documentation** — Remove the now-empty folder to free the `06` prefix. | **Manual** | `Remove-Item "C:\...\06_Documentation" -Recurse -Force` (verify empty first) |
| 2.2 | **Move 04_PowerBI → 99_Archive\04_PowerBI_Dev_2026_03** — Create archive folder if needed, then move. | **Manual** | `mkdir "C:\...\99_Archive\04_PowerBI_Dev_2026_03"` if not exists; `Move-Item "C:\...\04_PowerBI" "C:\...\99_Archive\04_PowerBI_Dev_2026_03\"` |
| 2.3 | **Rename PowerBI_Date → PowerBI_Data** | **Manual** | `Rename-Item "C:\...\PowerBI_Date" "PowerBI_Data"` |
| 2.4 | **Rename 01_SourceData → 01_Raw_Source_Data** | **Manual** | `Rename-Item "C:\...\01_SourceData" "01_Raw_Source_Data"` |
| 2.5 | **Merge 08_Themes into 08_Templates** — Copy (do not move yet) all contents of `08_Themes\` into `08_Templates\`. Resolve duplicates: keep 08_Themes version (more complete: HPD themes v2–v4, CHANGELOG). Structure: `08_Templates\Themes\SCRPA\`, `08_Templates\Themes\HPD\`, `08_Templates\VBA\`. | **Manual** | Copy folders; merge Themes; keep 08_Themes HPD JSON files at `08_Templates\Themes\HPD\` or root. |
| 2.6 | **Merge 15_Templates into 08_Templates** — Copy Themes, VBA from `15_Templates\` into `08_Templates\`. Overwrite only if 08_Themes content is newer/better. Copy any `*.pbix` (Base_Report.pbix, Monthly_Report_Template.pbix) into `08_Templates\` or `08_Templates\PBIX\`. | **Manual** | Copy; dedupe; ensure PBIX files land in 08_Templates. |
| 2.7 | **Move 09_Reference\Report_Styles into 08_Templates** — Move entire `Report_Styles` folder to `08_Templates\Report_Styles\`. | **Manual** | `Move-Item "C:\...\09_Reference\Report_Styles" "C:\...\08_Templates\Report_Styles"` |
| 2.8 | **Delete 08_Themes** (after verifying 08_Templates has all content). | **Manual** | `Remove-Item "C:\...\08_Themes" -Recurse` |
| 2.9 | **Delete 15_Templates** (after verifying 08_Templates has all content). | **Manual** | `Remove-Item "C:\...\15_Templates" -Recurse` |
| 2.10 | **Create 09_Reference\Report_Styles placeholder** (optional) — If any external references expect `09_Reference\Report_Styles`, add a README redirect: "Moved to 08_Templates\Report_Styles". | **Manual** | Create `09_Reference\Report_Styles\README.md` with redirect text. |
| 2.11 | **Rename Master_Automation → 06_Workspace_Management** — Repurpose the freed `06` prefix. This folder becomes the master hub for the entire OneDrive workspace. | **Manual** | `Rename-Item "C:\...\Master_Automation" "06_Workspace_Management"` |
| 2.12 | **Rename KB_Shared → 19_KB_Shared** | **Manual** | `Rename-Item "C:\...\KB_Shared" "19_KB_Shared"` |
| 2.13 | **Rename Shared Folder → 20_Shared_Folder** | **Manual** | `Rename-Item "C:\...\Shared Folder" "20_Shared_Folder"` |
| 2.14 | **Rename SSOCC → 21_SSOCC** | **Manual** | `Rename-Item "C:\...\SSOCC" "21_SSOCC"` |
| 2.15 | **Update internal references to Shared Folder** — `Shared Folder\Compstat\Monthly Reports` becomes `20_Shared_Folder\Compstat\Monthly Reports`. Scripts will be updated in Phase 4. | **N/A** | Deferred to Phase 4. |

---

## Phase 3: Centralized Config Setup (Codebase Tasks)

| Step | Task | Type | Notes |
|------|------|------|-------|
| 3.1 | **Create config.json** at `06_Workspace_Management\config.json`. | **Automated via Cursor** | Schema below. Acts as definitive source of truth. |
| 3.2 | **Populate config.json** with relative paths only. Use forward slashes `/` in JSON to avoid escape-character issues; Python and PowerShell handle `/` on Windows. | **Automated via Cursor** | All paths relative to `$HOME/BaseDirectory`. |
| 3.3 | **Add config.json to .gitignore** (if repo exists) or document that it may contain machine-specific overrides. | **Manual** | Optional; only if using git. |
| 3.4 | **Create Python helper** — Add `load_config()` in `path_config.py` to read config, build `base_dir = Path.home() / config["BaseDirectory"]`, and return `Path` objects for each directory/file. | **Automated via Cursor** | See Appendix B for parsing pattern. |
| 3.5 | **Create PowerShell helper** — Add `Get-OneDriveConfig` function to parse config with `ConvertFrom-Json`, build `$baseDir = Join-Path $HOME $config.BaseDirectory`, and return paths. | **Automated via Cursor** | See Appendix B for parsing pattern. |

**config.json schema (relative paths, forward slashes):**

```json
{
  "Environment": "Production",
  "BaseDirectory": "OneDrive - City of Hackensack",
  "Directories": {
    "Templates": "08_Templates",
    "DataSources": "01_DataSources",
    "RawSourceData": "01_Raw_Source_Data",
    "PowerBI": "PowerBI_Data",
    "WorkspaceManagement": "06_Workspace_Management",
    "KBShared": "KB_Shared",
    "SharedFolder": "Shared Folder",
    "SSOCC": "SSOCC",
    "SCRPAReports": "16_Reports/SCRPA"
  },
  "Files": {
    "SCRPABaseReport": "08_Templates/PBIX/Base_Report.pbix",
    "MonthlyReportTemplate": "08_Templates/PBIX/Monthly_Report_Template.pbix"
  }
}
```

**Bootstrap logic:** To find the config file: `config_path = Path.home() / "OneDrive - City of Hackensack" / "06_Workspace_Management" / "config.json"` (or use `ONEDRIVE_BASE` env var if set). Once loaded, all other paths = `base_dir / config["Directories"]["Templates"]` etc.

---

## Phase 4: Codebase Path Refactor (Codebase Tasks)

**Execute in order. All tasks are Automated via Cursor unless noted.**

### 4.1 Core Path Infrastructure

| Step | File | Task | Type |
|------|------|------|------|
| [x] 4.1.1 | `06_Workspace_Management\scripts\path_config.py` | Refactor to read from `06_Workspace_Management\config.json` (see Appendix B). Use `Path.home() / config["BaseDirectory"]` for base; `get_powerbi_paths()` returns `(base / "PowerBI_Data/_DropExports", base / "PowerBI_Data/Backfill")`. Remove all `PowerBI_Date` fallbacks. | **Automated** |
| [x] 4.1.2 | `06_Workspace_Management\config\scripts.json` | Update `powerbi_drop_path` to `...\PowerBI_Data\_DropExports`. | **Automated** |
| [x] 4.1.3 | `06_Workspace_Management\config\scripts-PD_BCI_LTP.json` | Same as 4.1.2 if it contains `powerbi_drop_path`. | **Automated** |

### 4.2 06_Workspace_Management Scripts

| Step | File | Task | Type |
|------|------|------|------|
| [x] 4.2.1 | `06_Workspace_Management\scripts\run_all_etl.ps1` | Replace `$templatesDir = Join-Path $OneDriveBase "15_Templates"` with `08_Templates`. Replace `Shared Folder` with `20_Shared_Folder`. Add config.json parsing or update `$OneDriveBase` logic. | **Automated** |
| [x] 4.2.2 | `06_Workspace_Management\scripts\process_powerbi_exports.py` | Ensure it uses `path_config.get_powerbi_paths()` (no hardcoded PowerBI_Date). | **Automated** |
| [x] 4.2.3 | `06_Workspace_Management\scripts\overtime_timeoff_with_backfill.py` | Verify uses path_config; update any literal `PowerBI_Date`. | **Automated** |
| [x] 4.2.4 | `06_Workspace_Management\scripts\summons_backfill_merge.py` | Same as 4.2.3. | **Automated** |
| [x] 4.2.5 | `06_Workspace_Management\scripts\merge_powerbi_backfill.py` | Same as 4.2.3. | **Automated** |
| [x] 4.2.6 | `06_Workspace_Management\scripts\restore_fixed_from_backfill.py` | Same as 4.2.3. | **Automated** |
| [x] 4.2.7 | `06_Workspace_Management\scripts\check_summons_backfill.py` | Same as 4.2.3. | **Automated** |
| [x] 4.2.8 | `06_Workspace_Management\scripts\community_engagement_data_flow_check.py` | Same as 4.2.3. | **Automated** |
| [x] 4.2.9 | `06_Workspace_Management\scripts\compare_response_time_results.py` | Same as 4.2.3. | **Automated** |
| [x] 4.2.10 | `06_Workspace_Management\scripts\verify_december_2025_overtime.py` | Same as 4.2.3. | **Automated** |
| [x] 4.2.11 | `06_Workspace_Management\scripts\summons_derived_outputs.py` | Same as 4.2.3. | **Automated** |
| [x] 4.2.12 | `06_Workspace_Management\scripts\response_time_fresh_calculator.py` | Same as 4.2.3. | **Automated** |
| [x] 4.2.13 | `06_Workspace_Management\scripts\Pre_Flight_Validation.py` | Same as 4.2.3. | **Automated** |
| [x] 4.2.14 | `06_Workspace_Management\scripts\diagnose_summons_missing_months.py` | Same as 4.2.3. | **Automated** |
| [x] 4.2.15 | `06_Workspace_Management\scripts\normalize_visual_export_for_backfill.py` | Same as 4.2.3. | **Automated** |
| [x] 4.2.16 | `06_Workspace_Management\scripts\run_all_etl.ps1` | Update `organize_backfill_exports.ps1` path: `PowerBI_Data\tools\` (was `PowerBI_Date\tools\`). | **Automated** |

### 4.3 06_Workspace_Management M Code / TMDL (Power BI)

| Step | File | Task | Type |
|------|------|------|------|
| [x] 4.3.1 | `06_Workspace_Management\m_code\response_time\___ResponseTime_AllMetrics.m` | Replace `PowerBI_Date` with `PowerBI_Data` in `Folder.Files(...)`. | **Automated** |
| [x] 4.3.2 | `06_Workspace_Management\m_code\tmdl_export\tables\___ResponseTime_AllMetrics.tmdl` | Same. | **Automated** |
| [x] 4.3.3 | `06_Workspace_Management\m_code\tmdl_export\tables\___ResponseTimeCalculator.tmdl` | Same. | **Automated** |
| [x] 4.3.4 | `06_Workspace_Management\m_code\tmdl_export\tables\___ResponseTime_OutVsCall.tmdl` | Same. | **Automated** |
| [x] 4.3.5 | `06_Workspace_Management\m_code\tmdl_export\tables\___ResponseTime_DispVsCall.tmdl` | Same. | **Automated** |
| [x] 4.3.6 | `06_Workspace_Management\m_code\arrests\___Arrest_Distro.m` | Update `01_DataSources` path if config changes; else no change. | **Automated** |
| [x] 4.3.7 | `06_Workspace_Management\m_code\arrests\___Arrest_Categories.m` | Same. | **Automated** |
| [x] 4.3.8 | `06_Workspace_Management\m_code\arrests\___Top_5_Arrests.m` | Same. | **Automated** |
| [x] 4.3.9 | `06_Workspace_Management\m_code\nibrs\___NIBRS_Monthly_Report.m` | Same. | **Automated** |
| [x] 4.3.10 | `06_Workspace_Management\m_code\tmdl_export\tables\___Arrest_Distro.tmdl` | Same. | **Automated** |
| [x] 4.3.11 | `06_Workspace_Management\m_code\tmdl_export\tables\___Arrest_Categories.tmdl` | Same. | **Automated** |
| [x] 4.3.12 | `06_Workspace_Management\m_code\tmdl_export\tables\___Top_5_Arrests.tmdl` | Same. | **Automated** |
| [x] 4.3.13 | `06_Workspace_Management\m_code\tmdl_export\tables\___NIBRS_Monthly_Report.tmdl` | Same. | **Automated** |
| [x] 4.3.14 | `06_Workspace_Management\TMDL_SocialMedia_Fix\tables\*.tmdl` | Same updates for PowerBI_Data and 01_DataSources. | **Automated** |
| [x] 4.3.15 | `06_Workspace_Management\m_code\2026_03_09_all_queries.m` | Same. | **Automated** |
| [x] 4.3.16 | `06_Workspace_Management\m_code\2026_02_26_template_m_codes.m` | Same. | **Automated** |

**Note:** After M code changes, open `08_Templates\Monthly_Report_Template.pbix` in Power BI Desktop and refresh to verify paths.

### 4.4 scripts.json (01_Raw_Source_Data)

| Step | File | Task | Type |
|------|------|------|------|
| [x] 4.4.1 | `06_Workspace_Management\config\scripts.json` | If any script path references `01_SourceData`, update to `01_Raw_Source_Data`. | **Automated** (no `01_SourceData` refs; only `01_DataSources`) |
| [x] 4.4.2 | `06_Workspace_Management\config\scripts-PD_BCI_LTP.json` | Same. | **Automated** (no changes needed) |

**Note:** scripts.json references `01_DataSources` (ARREST_DATA, NIBRS) — no change. Only `01_SourceData` → `01_Raw_Source_Data` if referenced.

### 4.5 SCRPA Pipeline

| Step | File | Task | Type |
|------|------|------|------|
| [x] 4.5.1 | `16_Reports\SCRPA\scripts\run_scrpa_pipeline.py` | Change `TEMPLATE_DIR = Path(...\15_Templates)` to `08_Templates`. Update `POWERBI_TEMPLATE` to `08_Templates\Base_Report.pbix` (or `08_Templates\PBIX\Base_Report.pbix`). Prefer reading from config.json. | **Automated** |
| [x] 4.5.2 | `16_Reports\SCRPA\claude.md` | Update HTML template path: `08_Themes\Themes\HTML\scrpa_html.md` → `08_Templates\Themes\HTML\scrpa_html.md`. Update `09_Reference\Report_Styles\html\HPD_Report_Style_Prompt.md` → `08_Templates\Report_Styles\html\HPD_Report_Style_Prompt.md`. | **Automated** |

### 4.6 PowerBI_Data Tools

| Step | File | Task | Type |
|------|------|------|------|
| [x] 4.6.1 | `PowerBI_Data\tools\organize_backfill_exports.ps1` | Update any internal references from `PowerBI_Date` to `PowerBI_Data`. | **Automated** |

### 4.7 ETL Scripts (02_ETL_Scripts)

| Step | File | Task | Type |
|------|------|------|------|
| [x] 4.7.1 | `02_ETL_Scripts\Response_Times\process_cad_data_13month_rolling.py` | Replace any `PowerBI_Date` with `PowerBI_Data` or path_config. | **Automated** |
| [x] 4.7.2 | `02_ETL_Scripts\Response_Times\response_time_batch_all_metrics.py` | Same. | **Automated** |

### 4.8 Documentation (High-Value Only)

| Step | File | Task | Type |
|------|------|------|------|
| [x] 4.8.1 | `06_Workspace_Management\Claude.md` | Replace `PowerBI_Date` → `PowerBI_Data`, `15_Templates` → `08_Templates`, `Master_Automation` → `06_Workspace_Management`. | **Automated** |
| [x] 4.8.2 | `06_Workspace_Management\SUMMARY.md` | Same. | **Automated** |
| [x] 4.8.3 | `06_Workspace_Management\CHANGELOG.md` | Same (for forward-looking entries; historical entries may stay as-is). | **Automated** |
| [x] 4.8.4 | `06_Workspace_Management\docs\MONTHLY_REPORT_TEMPLATE_WORKFLOW.md` | `15_Templates` → `08_Templates`. | **Automated** |
| [x] 4.8.5 | `06_Workspace_Management\docs\PROMPT_Claude_MCP_Correct_Report_Styles.md` | `09_Reference\Report_Styles` → `08_Templates\Report_Styles`. | **Automated** |
| [x] 4.8.6 | `06_Workspace_Management\docs\PROMPT_Claude_MCP_Create_Missing_Visuals_For_Monthly_Report.md` | `15_Templates` → `08_Templates`. | **Automated** |
| [x] 4.8.7 | `06_Workspace_Management\docs\PROMPT_Claude_MCP_Response_Time_Visuals.md` | Same. | **Automated** |
| [x] 4.8.8 | `06_Workspace_Management\docs\response_time\POWERBI_REFRESH_REQUIRED_2026_02_26.md` | Same. | **Automated** |
| [x] 4.8.9 | `06_Workspace_Management\docs\Monthly_Report_Data_Population_Technical_Summary.html` | Same. | **Automated** |
| [x] 4.8.10 | `08_Templates\Report_Styles\README.md` | Update canonical path: `Master_Automation\docs\templates\HPD_Report_Style_Prompt.md` → `06_Workspace_Management\docs\templates\HPD_Report_Style_Prompt.md`. | **Automated** |
| [x] 4.8.11 | `16_Reports\SCRPA\README.md` | `15_Templates` → `08_Templates`. | **Automated** |
| [x] 4.8.12 | `16_Reports\SCRPA\SUMMARY.md` | Same. | **Automated** |
| [x] 4.8.13 | `16_Reports\SCRPA\CHANGELOG.md` | Same. | **Automated** |
| [x] 4.8.14 | `16_Reports\SCRPA\BI_WEEKLY_CYCLE_SETUP.md` | Same. | **Automated** |
| [x] 4.8.15 | `16_Reports\SCRPA\doc\UPDATE_TEMPLATE_INSTRUCTIONS.md` | Same. | **Automated** |
| [x] 4.8.16 | `16_Reports\SCRPA\doc\PRE_SAVE_CHECKLIST.md` | Same. | **Automated** |
| [x] 4.8.17 | `16_Reports\SCRPA\doc\POWER_BI_UPDATE_QUICK_REFERENCE.md` | Same. | **Automated** |
| [x] 4.8.18 | `16_Reports\SCRPA\doc\STEP2_M_CODE_UPDATES.md` | Same. | **Automated** |
| [x] 4.8.19 | `16_Reports\SCRPA\doc\FINAL_VERIFICATION_SUMMARY.md` | Same. | **Automated** |
| [x] 4.8.20 | `16_Reports\SCRPA\doc\VERIFICATION_01_27_2026_REPORT.md` | Same. | **Automated** |
| [x] 4.8.21 | `16_Reports\SCRPA\doc\Fix_SCRPA_Cycle_Data_And_Workflow_Issues.md` | Same. | **Automated** |

**Note:** Chatlogs, transcripts, and historical docs in `doc\chunked\`, `doc\raw\` may be left unchanged to preserve history.

### 4.9 Report_Styles Internal References

| Step | File | Task | Type |
|------|------|------|------|
| [x] 4.9.1 | `08_Templates\Report_Styles\templates\HPD_Report_Style_Prompt.md` | If it references Master_Automation path, update to `06_Workspace_Management`. | **Automated** |

### 4.10 Shared Folder References — CANCELLED

| Step | File | Task | Type |
|------|------|------|------|
| ~~4.10.1~~ | `06_Workspace_Management\scripts\run_all_etl.ps1` | ~~`Shared Folder\Compstat\Monthly Reports` → `20_Shared_Folder\Compstat\Monthly Reports`.~~ | **CANCELLED** (Hub renames aborted; KB_Shared, Shared Folder, SSOCC remain) |
| ~~4.10.2~~ | Any script referencing `Shared Folder` | ~~Grep and replace with `20_Shared_Folder`.~~ | **CANCELLED** |

### 4.11 Verification

| Step | Task | Type |
|------|------|------|
| [x] 4.11.1 | Run `run_scrpa_pipeline.py` (dry run or minimal cycle) to verify template path. | **Manual** |
| [x] 4.11.2 | Run `run_all_etl.ps1` (or monthly report save step) to verify template and Shared Folder paths. | **Manual** |
| [x] 4.11.3 | Run `process_powerbi_exports.py --dry-run` to verify PowerBI_Data paths. | **Manual** |
| [x] 4.11.4 | Open `08_Templates\Monthly_Report_Template.pbix` in Power BI Desktop; refresh all queries to verify M code paths. | **Manual** |

**Completed 2026-03-19:** Power BI template updated via Claude Desktop MCP injection. All 4 Response Time partitions (`___ResponseTime_DispVsCall`, `___ResponseTime_OutVsCall`, `___ResponseTimeCalculator`, `___ResponseTime_AllMetrics`) received `PowerBI_Date` → `PowerBI_Data` path corrections. See `docs/POWERBI_TEMPLATE_MCP_UPDATE_2026_03_19.md`.

---

## Project Close-Out — Directory Consolidation Complete

**Status:** ✅ **CLOSED**  
**Date:** 2026-03-19  
**Final Action:** Claude Desktop MCP injection into `08_Templates\Monthly_Report_Template.pbix` completed the last remaining step (Phase 4.11.4 — Power BI template M code paths).

**Deliverables:**
- All Phase 0–4.10 tasks completed
- Phase 4.11 verification complete (template paths updated via MCP)
- Documentation updated: CHANGELOG v1.18.13, SUMMARY, Power BI docs, `POWERBI_TEMPLATE_MCP_UPDATE_2026_03_19.md`

**MCP Session Additions (beyond path corrections):**
- 13 DAX subtitle measures standardized (13-month rolling format)
- New measure: `Subtitle_DeptWide_Summons`
- Use of Force data discrepancy fixed (`IncidentCount_13Month` EDATE bug)
- `STACP_DIAGNOSTIC` comment header updated; other comment headers deferred

---

## Summary: Task Count by Phase

| Phase | Manual | Automated |
|-------|--------|-----------|
| Phase 0 | 0 | 4 |
| Phase 1 | 5 | 4 |
| Phase 2 | 15 | 0 |
| Phase 3 | 1 | 4 |
| Phase 4 | 4 | 60+ |

---

## Appendix A: Find-OldPaths.ps1 (Hardcoded Path Scanner)

Save as `Find-OldPaths.ps1` in `06_Workspace_Management\_consolidation_project\` (or `Master_Automation\_consolidation_project\` before Phase 2). Exports `Path_Refactor_Audit.csv` to the same folder to avoid cluttering the OneDrive root.

```powershell
<#
.SYNOPSIS
Scans a directory recursively for legacy hardcoded folder paths.

.DESCRIPTION
Searches through .py, .ps1, .json, .md, etc. for old directory names.
Outputs to console and exports Path_Refactor_Audit.csv to the script's folder (_consolidation_project).
#>

$SearchPath = "C:\Users\carucci_r\OneDrive - City of Hackensack"

$TargetStrings = @(
    "08_Templates",
    "08_Themes",
    "15_Templates",
    "09_Reference\Report_Styles",
    "09_Reference/Report_Styles",
    "01_SourceData",
    "04_PowerBI",
    "PowerBI_Date",
    "Master_Automation",
    "KB_Shared",
    "Shared Folder",
    "SSOCC"
)

$IncludeExtensions = @("*.py", "*.ps1", "*.json", "*.md", "*.yaml", "*.bat", "*.txt", "*.env")
$ExcludeFolders = @(".git", "__pycache__", "node_modules", ".venv")

$FilesToScan = Get-ChildItem -Path $SearchPath -Include $IncludeExtensions -Recurse -File |
    Where-Object {
        $path = $_.FullName
        $excludeMatch = $ExcludeFolders | Where-Object { $path -match [regex]::Escape($_) }
        -not $excludeMatch
    }

$Results = @()
foreach ($File in $FilesToScan) {
    foreach ($Target in $TargetStrings) {
        $Matches = Select-String -Path $File.FullName -Pattern $Target -SimpleMatch -ErrorAction SilentlyContinue
        foreach ($Match in $Matches) {
            $Results += [PSCustomObject]@{
                File       = $File.Name
                Directory  = $File.DirectoryName
                LineNumber = $Match.LineNumber
                Matched    = $Target
                LineText   = $Match.Line.Trim()
            }
        }
    }
}

if ($Results.Count -gt 0) {
    $Results | Format-Table File, LineNumber, Matched, LineText -AutoSize
    # Export to script's folder (_consolidation_project) to avoid cluttering OneDrive root
    $ExportPath = Join-Path -Path $PSScriptRoot -ChildPath "Path_Refactor_Audit.csv"
    $Results | Export-Csv -Path $ExportPath -NoTypeInformation
    Write-Host "Saved to: $ExportPath" -ForegroundColor Green
} else {
    Write-Host "No hardcoded legacy paths found." -ForegroundColor Green
}
```

---

## Appendix B: Python and PowerShell Config Parsing

**Python (path_config.py or config_loader.py):**

```python
import json
from pathlib import Path

# Bootstrap: find config (before config defines paths)
def _get_config_path() -> Path:
    base = Path.home() / "OneDrive - City of Hackensack"
    return base / "06_Workspace_Management" / "config.json"

def load_config() -> dict:
    with open(_get_config_path(), "r", encoding="utf-8") as f:
        return json.load(f)

def get_base_dir() -> Path:
    config = load_config()
    return Path.home() / config["BaseDirectory"]

def get_template_dir() -> Path:
    return get_base_dir() / load_config()["Directories"]["Templates"]

def get_powerbi_data_dir() -> Path:
    return get_base_dir() / load_config()["Directories"]["PowerBI"]

def get_scrpa_base_report() -> Path:
    return get_base_dir() / load_config()["Files"]["SCRPABaseReport"]
```

**PowerShell (run_all_etl.ps1 or common.ps1):**

```powershell
function Get-OneDriveConfig {
    $configPath = Join-Path $HOME "OneDrive - City of Hackensack\06_Workspace_Management\config.json"
    $config = Get-Content -Raw -Path $configPath | ConvertFrom-Json
    $baseDir = Join-Path -Path $HOME -ChildPath $config.BaseDirectory

    return @{
        BaseDir     = $baseDir
        Templates   = Join-Path -Path $baseDir -ChildPath $config.Directories.Templates
        PowerBI     = Join-Path -Path $baseDir -ChildPath $config.Directories.PowerBI
        SharedFolder = Join-Path -Path $baseDir -ChildPath $config.Directories.SharedFolder
        SCRPABaseReport = Join-Path -Path $baseDir -ChildPath $config.Files.SCRPABaseReport
        MonthlyReportTemplate = Join-Path -Path $baseDir -ChildPath $config.Files.MonthlyReportTemplate
    }
}
```

---

## Appendix C: Files Requiring 01_Raw_Source_Data Update

If any script reads from `01_SourceData` (e.g., Summons eticket export), update to `01_Raw_Source_Data`. Grep for `01_SourceData` to find references.

---

*Generated: 2026-03-19. Strategic update: Master_Automation → 06_Workspace_Management (reuse freed 06 prefix); Phase 0 scaffolding; config at 06_Workspace_Management\config.json; artifacts in _consolidation_project. Do not make code changes until user approves this checklist.*
