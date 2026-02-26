# Changelog

All notable changes to the Master_Automation workspace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.17.9] - 2026-02-26

### Fixed
- **`summons_13month_trend.m` — removed `TICKET_NUMBER` from `ChangedType`** — The current `summons_etl_enhanced.py` produces staging files with `PADDED_BADGE_NUMBER` as the first column (old schema); `TICKET_NUMBER` never exists in that file. `Table.TransformColumnTypes` has no `MissingField.Ignore` option, so the reference caused the "column not found" error. Removed the line; `TICKET_NUMBER` was not used in any downstream calculation.
- **`PATROL BUREAU` → `PATROL DIVISION` consolidation in both summons M code files** — The assignment master (`final_assignment.csv`) assigns patrol officers to WG2 = "PATROL BUREAU", but the All Bureaus visual should show "PATROL DIVISION". Previously only "HOUSING" and "OFFICE OF SPECIAL OPERATIONS" were consolidated. Added "PATROL BUREAU" to the `if` condition in both `summons_13month_trend.m` and `summons_all_bureaus.m`.
- **Restored `summons_powerbi_latest.xlsx` from today's ETL timestamped copy** — Incorrect file (Feb 17 `_DropExports` copy with WG2=None and sparse month coverage) was overwritten; restored from `summons_powerbi_20260226_164646.xlsx` which has proper WG2 assignments for all bureaus.

### Known Data Discrepancies (Jan 2026 report, requires investigation)
- **Traffic Bureau summons count gap**: ETL (from ATS court data): 143M / 2,599P. Submitted report: 217M / 3,117P. Delta: +74M +518P. Likely explained by `data/traffic_peo_additions_2026_02_17.csv` (untracked) containing PEO parking tickets not yet fed into the summons ETL.
- **Detective Bureau summons count gap**: ETL: 15M / 61P. Submitted report: 0M / 1P. Investigation needed — possible assignment master change reclassified some patrol officers as Detective Bureau since the submitted report was generated.
- **OT/TO July and August 2025 drift**: FIXED_monthly_breakdown reprocessed from raw data. Small positive differences vs submitted report (July sick +24h, July SAT +32h, August SAT +4h). Likely caused by retroactively-added raw records in the export files. These reflect more accurate data than was submitted; not a bug.

---

## [1.17.8] - 2026-02-26

### Fixed
- **`summons_powerbi_latest.xlsx` staging schema mismatch** — The staging file at `03_Staging\Summons\summons_powerbi_latest.xlsx` retained the OLD schema (first column `PADDED_BADGE_NUMBER`, no `TICKET_NUMBER`), while the M code in `summons_13month_trend` expects `TICKET_NUMBER` as the first column. Fix: copied the ETL-fresh `PowerBI_Date\_DropExports\summons_powerbi_latest.xlsx` (new schema with `TICKET_NUMBER` first) over the staging copy. The staging file now matches the M code schema and resolves the "The column 'TICKET_NUMBER' of the table wasn't found" refresh error.
- **`___ResponseTimeCalculator.m` missing January 2026 source** — The M code was hardcoded to only two backfill CSV files (Oct 2025 and Dec 2025), so `01-26` never appeared in Response Time visuals after refresh. Added a third source block loading `PowerBI_Date\Backfill\2026_01\response_time\2026_01_Average_Response_Times__Values_are_in_mmss.csv` and included it in `Table.Combine`. File: `m_code/response_time/___ResponseTimeCalculator.m`.

### ETL Refresh Validation (2026-02-26 Power BI refresh)
- **Summons — Moving & Parking (All Bureaus)**: ✅ Data populated after refresh. CSB: 5M/0P, Detective Bureau: 15M/61P, Patrol Bureau: 255M/628P, Traffic Bureau: 143M/2599P.
- **Top 5 Moving Violations**: ✅ M. Jacobsen #0138 (84), M. O'Neill #0327 (48), D. Francavilla #0329 (39)...
- **Top 5 Parking Violations**: ✅ K. Torres #2027 (678), G. Gallorini #0256 (415), D. Rizzi #2030 (382)...
- **Monthly Accrual and Usage Summary (Overtime/TimeOff)**: ✅ January 2026 (`01-26`) data present both before and after refresh; SAT: 497.5h, Sick: 1635h.
- **Average Response Times (mm:ss)**: ❌ Still ends at `12-25` — Jan 2026 data requires the `___ResponseTimeCalculator` M code update above to be pasted into Power BI Advanced Editor, then refresh again.
- **summons_13month_trend**: ❌ TICKET_NUMBER error — resolved by staging file fix above; re-refresh required.
- **Community Engagement (___Combined_Outreach_All)**: ⚠️ 0 records for January 2026 — not a bug. The source data (`community_engagement_data_*.csv`) only contains events through November 2025. No January 2026 community engagement events have been entered in the source system. Re-run ETL once source data is available.

---

## [1.17.7] - 2026-02-26

### Fixed
- **`{REPORT_MONTH}` token scoping bug in `run_all_etl.ps1`** — Variables `$year` and `$monthNum` are defined only inside the `Save-MonthlyReport` function and were out of scope when the token replacement ran during the script-execution loop, causing the substitution to produce `"-"` instead of `"2026-01"`. Fixed by computing `$prevMonthToken` directly from the `$ReportMonth` parameter using `[datetime]::ParseExact` at the point of substitution. File: `scripts/run_all_etl.ps1` (lines ~517–526).
- **`DEFAULT_INPUT_PATH` double-extension and wrong folder in Response Times script** — Hardcoded default was `monthly_export\2025\2025_11_Monthly_CAD.xlsx.xlsx` (dead path post-reorganization + double `.xlsx` extension). Updated to `timereport\monthly\2026_01_timereport.xlsx` to match the current file structure. File: `02_ETL_Scripts\Response_Times\process_cad_data_13month_rolling.py` (line 45).
- **`POWERBI_OUTPUT_DIR` dead `C:\Dev` path in Response Times script** — Secondary copy target pointed to `C:\Dev\PowerBI_Date\Backfill\2025_12\response_time` (dead since 2026-02-24 reorganization). Updated to the production drop folder `PowerBI_Date\_DropExports`. File: `02_ETL_Scripts\Response_Times\process_cad_data_13month_rolling.py` (line 48).

### ETL Run — February 2026 Cycle (2026-02-26)
- **Arrests** ✅ — 42 January 2026 records from `2026_01_LAWSOFT_ARREST.xlsx`; output `2026_01_Arrests_PowerBI_Ready.xlsx`.
- **Community Engagement** ✅ — 2 files copied to drop folder.
- **Overtime / TimeOff** ✅ — 13-month window 2025-01 → 2026-01; 10,060 rows; 30 output files.
- **Response Times** ✅ *(manual re-run after orchestrator fix)* — 1,991 records, all 3 response types validated. `2026_01_Average_Response_Times__Values_are_in_mmss.csv` copied to drop folder and backfill (`PowerBI_Date\Backfill\2026_01\response_time\`).
- **Summons** ✅ — 7 files including refreshed `summons_powerbi_latest_summons_data.csv` copied to drop folder.
- **Summons Derived Outputs** ❌ *(expected — not a blocker)* — Requires Power BI visual export (`Department-Wide Summons Moving and Parking.csv`) to exist in the monthly reports folder before this script can run. Re-run after Power BI refresh + export step.

### Notes
- February file `2026_02_LAWSOFT_ARREST.xlsx` was temporarily renamed `.hold` before the ETL run and restored after to prevent the arrest ETL from picking up a partial-month file via mtime-based selection.
- Monthly report template saved to `Shared Folder\Compstat\Monthly Reports\2026\01_january\2026_01_Monthly_Report.pbix`. Open in Power BI Desktop and refresh all connections before publishing.

---

## [1.17.6] - 2026-02-26

### Fixed
- **`___Traffic.m` backslash syntax errors** — Removed all M code backslash line-continuation characters (invalid in Power BI Advanced Editor); query now pastes cleanly. Also fixed indentation and removed string-concatenation split across lines in `File.Contents()` path. File: `m_code/traffic/___Traffic.m`
- **Dead `C:\Dev\PowerBI_Date` path in config** — `C:\Dev\PowerBI_Date` was moved to `04_PowerBI/PowerBI_Date_Dev` during 2026-02-24 directory reorganization. Updated `PD_BCI_LTP` override in `config/scripts.json` and `config/scripts-PD_BCI_LTP.json` to point to the standard OneDrive production path. Laptop junction (`C:\Users\carucci_r` → `C:\Users\RobertCarucci`) makes this override unnecessary in practice.

### Context
- **2026-02-24 Directory Reorganization** — `C:\Dev` consolidated into OneDrive numbered directory structure. Key moves affecting Master_Automation:
  - `C:\Dev\PowerBI_Date` → `04_PowerBI/PowerBI_Date_Dev` (archived Dev copy; production `PowerBI_Date` remains at OneDrive root — unaffected)
  - `C:\Dev\Power_BI_Data` → `04_PowerBI/Power_BI_Data_Dev`
  - `C:\Dev\overtime_timeoff`, `response_times`, `summons`, etc. → `00_dev/projects/` (dev copies; production ETL scripts remain in `02_ETL_Scripts\` — unaffected)
  - Migration scripts → `14_Workspace/scripts/`
  - All active M code files confirmed clean (no `C:\Dev` references)

---

## [Unreleased]

### Planned
- [ ] Refresh `summons_powerbi_latest.xlsx` staging file with Oct 2025 – Jan 2026 data (next ETL run)
- [ ] Enhance `arrest_python_processor.py` — match input file to target month by filename pattern instead of newest-by-mtime
- [ ] Implement 3-metric Response Time tables (Travel Time, Total Response, Processing Time)
- [ ] Monitor March 2026 execution for continued validation

---

## [1.17.5] - 2026-02-23

### Completed — Surgical Template Update (All Queries Loading, No DAX Errors)

Successfully applied surgical M code edits to the February 2026 Power BI template. All queries load without errors. Close & Apply completes cleanly.

### Added
- **`pReportMonth` parameter** — Created in template (Type: Date, Value: 2/1/2026)
- **`___Summons` query** — Re-created as new blank query; DAX model had 12 measures referencing this table but it was missing from the template. Includes dynamic column typing (`ExistingColumns` / `FilteredTypes` pattern), plus computed `TICKET_COUNT` (each 1) and `ASSIGNMENT_FOUND` (each true) columns required by DAX measures
- **`___ResponseTimeCalculator` columns** — Added `Count` (each 1, Int64) and `MonthName` (derived from YearMonth, e.g. "November 2024") to satisfy DAX SUMMARIZE measures

### Changed
- **Path fixes (4 queries):**
  - `ESU_13Month` — `C:\Users\RobertCarucci` → `C:\Users\carucci_r`
  - `summons_top5_parking` — `C:\Users\RobertCarucci` → `C:\Users\carucci_r`
  - `summons_top5_moving` — `C:\Users\RobertCarucci` → `C:\Users\carucci_r`
  - `___ResponseTimeCalculator` — `C:\Dev\PowerBI_Date` → `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date` (2 file paths)
- **DateTime.LocalNow() → pReportMonth (6 queries):**
  - `summons_top5_moving`, `summons_all_bureaus`, `___Drone`, `___Traffic`, `___Social_Media`
  - `summons_top5_moving` also had a stray `DateTime.LocalNow()` concatenated to the final `in` clause — removed
- **`summons_13month_trend`** — Removed 4 non-existent columns from `ChangedType` (`TICKET_COUNT`, `IS_AGGREGATE`, `POSS_CONTRACT_TYPE`, `ASSIGNMENT_FOUND`); added `TICKET_COUNT` as computed column (each 1); added `Table.Distinct` dedup on `TICKET_NUMBER` to fix relationship uniqueness constraint

### Removed
- **4 orphaned DAX calculated tables** — `Arrests`, `Demographics`, `Distribution of Arrests by County, City and Gender`, `Top_5_Officers_Table` (all referenced non-existent `Arrest_Top` table; pre-existing issue in January template)

### Known Issues
- **Summons staging data gap** — `summons_powerbi_latest.xlsx` only contains data through September 2025. Queries that filter by `pReportMonth` (January 2026) return empty results. Summons visuals (Top 5 Moving, All Bureaus, Department-Wide trend) will populate correctly once the staging file is refreshed by the next ETL run
- **`summons_top5_parking`** uses `List.Max(YearMonthKey)` instead of `pReportMonth` — shows September 2025 data (latest available) while subtitle says "January 2026". Will self-correct when staging data is updated
- **Department-Wide Summons** missing March 2025 — gap in staging source data

---

## [1.17.4] - 2026-02-23

### Failed — Bulk M Code Paste into Template (Second Attempt)

Attempted to paste repo M code into all 11 queries in the refreshed January 2026 template. Queries loaded data successfully (Drone 74.7 KB, Patrol 222 KB, ResponseTimeCalculator 268 bytes) but cascading DAX model errors occurred during Close & Apply.

**Root Cause: Schema mismatch between repo M code and PBIX DAX model.**

### Reverted
- **All 11 template query changes discarded** — Used Power BI "Discard changes" to revert all queries back to original January M code. Template is back to clean state.

### Documented
- **Surgical approach plan created** — `plans/surgical_template_update_8b5a8e70.plan.md`
- Key lesson: Do NOT replace entire query bodies with repo M code. Only make minimal edits that preserve the original output schema.

---

## [1.17.3] - 2026-02-22

### Changed
- **Report template refreshed** — Old template had cascading Power BI model errors after bulk M code paste; archived as `Monthly_Report_Template_ARCHIVED_2026_02_22.pbix`
- **New template** — Copied from January 2026 published report (`2026_01_Monthly_Report.pbix`) to `15_Templates\Monthly_Report_Template.pbix`; clean baseline with latest formatting, DAX model, and all working queries

### Added
- **Laptop path junction** — Created Windows junction `C:\Users\carucci_r` → `C:\Users\RobertCarucci` so M code data sources resolve on both desktop and laptop without modifying M code files

---

## [1.17.2] - 2026-02-22

### Changed
- **M Code folder reorganization** — Expanded from 17 to 20 page-based subfolders for clearer navigation
  - `patrol/` — Now contains only `___Patrol.m` (was: Patrol, Chief2, REMU)
  - `remu/` — New folder for `___REMU.m` (moved from patrol/)
  - `chief/` — New folder for `___Chief2.m` (from patrol/) and `___chief_projects.m` (from community/)
  - `community/` — Now contains only `___Combined_Outreach_All.m` (was: Outreach + Chief Projects)
  - `social_media/` — New folder for `___Social_Media.m` (moved from stacp/)
  - `stacp/` — Now contains only `___STACP_pt_1_2.m` and `STACP_DIAGNOSTIC.m`
- **Visual export mapping** — Updated `visual_export_mapping.json` target_folder values to match new m_code structure
  - Chief Projects: `chief_projects` → `chief`
  - Chief Law Enforcement Duties: `law_enforcement_duties` → `chief`
  - Social Media Posts: `social_media_and_time_report` → `social_media`
  - Monthly Accrual: remains at `social_media_and_time_report` (unchanged)
- **ESU simplified** — `MonthlyActivity` and `TrackedItems` queries removed from template; `ESU_13Month.m` is the sole ESU query

### Fixed
- **___Drone.m syntax error** — Removed invalid backslash `\` line continuation characters on lines 159-160 (M code does not support C-style line continuations)
- **___Social_Media.m syntax error** — Same backslash issue on line 49; `Table.SelectColumns` call now on single line
- **___chief_projects.m syntax error** — Same backslash issue on lines 9-14 in `ChangedType` step; fixed during folder move
- **summons_13month_trend.m column error** — Removed 4 non-existent column declarations from `ChangedType` step (`TICKET_COUNT`, `IS_AGGREGATE`, `POSS_CONTRACT_TYPE`, `ASSIGNMENT_FOUND`); these columns do not exist in the staging workbook
- **summons_top5_moving.m blank table** — Switched from `pReportMonth`-based month filtering to `List.Max(YearMonthKey)` approach (matching the working `summons_top5_parking.m`); PEO exclusion logic retained

### Documentation
- Updated CLAUDE.md, CHANGELOG.md, SUMMARY.md, README.md with new 20-folder m_code structure
- Updated m_code file headers (// # path) to reflect new folder locations

---

## [1.17.1] - 2026-02-21

### Changed
- **pReportMonth advanced** — Updated `m_code/parameters/pReportMonth.m` from `#date(2026, 1, 1)` to `#date(2026, 2, 1)` for February 2026 reporting cycle
- All 20 M code queries now filter for January 2026 data (previous month from pReportMonth)

### Fixed
- **___Arrest_Categories blank table** — Root cause: pReportMonth=Jan filtered for Dec 2025 data (missing); advancing to Feb cycle resolves by finding Jan 2026 data (42 records in `2026_01_Arrests_PowerBI_Ready.xlsx`)
- **Arrest .tab file conversion** — Converted `2026_02_Lawsoft_Monthly_Arrest.tab` (headerless, tab-delimited, 39 records) to `2026_02_LAWSOFT_ARREST.xlsx` with proper column headers derived from January export

### Documented
- Arrest ETL picks latest `.xlsx` by modification time regardless of month — can cause wrong-file selection when multiple month exports exist
- Lawsoft exports arrive as `.tab` format (no column headers) requiring conversion before ETL processing

---

## [1.17.0] - 2026-02-21

### Added
- **M Code page-based folder structure** — Reorganized `m_code/` from flat directory into 17 page-based subfolders matching Power BI report pages: `arrests/`, `benchmark/`, `community/`, `csb/`, `detectives/`, `drone/`, `esu/`, `functions/`, `nibrs/`, `overtime/`, `parameters/`, `patrol/`, `response_time/`, `shared/`, `ssocc/`, `stacp/`, `summons/`, `traffic/`, `training/`
- **PBIX baseline export** — Extracted all 45 Power Query M code queries from `2026_01_Monthly_Report.pbix` into `all_m_code_26_january_monthly.m` (4,197 lines), then split into individual `.m` files with standardized headers
- **Standardized M code headers** — All 45 `.m` files now have: timestamp (EST), file path, Author: R. A. Carucci, AI-generated purpose line
- **Splitter script** — `scripts/split_mcode.py` parses consolidated M code and distributes to page folders with headers
- **PBIX export script** — `Downloads/PBIX_Exports/2026_02_21/Export-PbixData.ps1` for automated PBIX extraction (ADOMD.NET via DAX Studio)
- **Pre-Flight Validation rewrite** — `scripts/Pre_Flight_Validation.py` now accepts `--report-month YYYY-MM`, validates visual export mapping (36 total, 25 enforced), checks evidence (file size, row count), outputs structured GO/NO-GO JSON gate
- **Response Times dedup fix** — `scripts/response_time_fresh_calculator.py` v3.1.0: argparse, path_config, sort by Time Out before dedup (first-arriving unit)
- **ReportMonth freeze** — Created `m_code/parameters/pReportMonth.m` parameter; all 20 M code files with `DateTime.LocalNow()` now use `ReportMonth = pReportMonth` binding (25 occurrences replaced)
- **Orchestrator manifest** — `scripts/run_all_etl.ps1` now accepts `-ReportMonth YYYY-MM` and writes `_manifest.json` + `_manifest.csv` to `_DropExports` after copy phase

### Changed
- **m_code/ structure** — From 76 files (11 in root + mixed archive) to 49 clean files across 17 subfolders, 1 file per PBIX query
- **Query naming** — Removed `_FIXED`, `_2026`, `_STANDALONE` suffixes; files now match PBIX query names exactly (e.g., `___Arrest_Categories.m` not `___Arrest_Categories_FIXED.m`)

### Fixed
- **m_code clutter** — Archived 53 stale files (date-stamped snapshots, superseded versions, benchmark iterations, OT staging files) into `m_code/archive/2026_02_21_phase2_cleanup/`
- **Corrupted workspace script** — Replaced `scripts/process_cad_data_13month_rolling.py` (contained PowerShell) with redirect stub to production location
- **Summons hardcoded paths and filenames** — `scripts/summons_derived_outputs_simple.py` now uses `path_config`, dynamic `YYYY_MM` filenames, adds `IS_AGGREGATE` and `TICKET_COUNT` columns
- **Hardcoded M code paths** — Replaced 9 instances of `C:\Users\RobertCarucci` and `C:\Dev` paths across 8 M code files with correct `C:\Users\carucci_r` OneDrive paths

### Documentation
- CHANGELOG, README, SUMMARY, CLAUDE.md updated to reflect new folder structure, query inventory (45 queries: 25 data, 5 parameters, 5 functions, 10 other), and Phase 2 roadmap

### Discovered (Phase 2 inputs)
- PBIX already has `RootExportPath` and `EtlRootPath` parameters (no need to create `pRootPath` from scratch)
- PBIX has `RangeStart`/`RangeEnd` parameters that may complement `pReportMonth`
- 7 queries have broken paths: 4 use `C:\Users\RobertCarucci\...`, 2 use `C:\Dev\...`, 1 uses wrong month
- Warning icons on 6 queries: `___Drone`, `___ResponseTimeCalculator`, `summons_13month_trend`, `summons_top5_parking`, `summons_top5_moving`, `ESU_13Month`

---

## [1.16.0] - 2026-02-19

### Added
- **Desktop Configuration Support** – Full validation and troubleshooting guide for cross-machine ETL execution
- **Dynamic Argument Passing** – Enhanced `run_all_etl.ps1` orchestrator with token replacement system for script arguments
- **Environment Variable Path Resolution** – Improved `path_config.py` with `ONEDRIVE_BASE` environment variable support for portability
- **Comprehensive Documentation** – `docs/DESKTOP_CONFIGURATION_TROUBLESHOOTING.md` and `docs/FEBRUARY_2026_ETL_CYCLE_SUMMARY.md`

### Changed
- **Response Times ETL** – Restored to operational status with proper `--report-month` argument passing via `config/scripts.json`
- **Summons Derived Outputs** – Complete rewrite using Power BI exports as authoritative source for improved reliability and performance
- **Path Resolution** – All scripts now support environment variable-based path resolution for cross-machine compatibility

### Fixed
- **Response Times Script Failure** – Fixed exit code 2 error by implementing dynamic argument passing in orchestrator
- **Summons Schema Mismatch** – Resolved `IS_AGGREGATE` and `TICKET_COUNT` column issues with new processing approach
- **Cross-Machine Path Issues** – Eliminated hardcoded path dependencies through environment variable implementation

### Documentation
- **ESU** – Updated all ESU docs: `docs/ESU_POWER_BI_LOAD_AND_PUBLISH.md` and `m_code/esu/README.md` for single-query ESU_13Month (MonthKey, TrackedItem, Total, Status, ItemKey, Month_Year); Tables-only and _mom_hacsoc lookup; workbook requirements and optional 4-query approach. SUMMARY, CLAUDE.md, and directory structure updated to reference ESU and ESU docs.
- **Desktop Configuration** – Complete troubleshooting guide with machine-specific setup instructions
- **ETL Cycle Documentation** – Comprehensive execution summary with lessons learned and recommendations

---

## [1.15.8] - 2026-02-16

### Added
- **Policy Training: Cost of Training visual 13-month window** – `m_code/___Cost_of_Training.m` now filters to rolling 13-month window (same month one year earlier through previous month, e.g. 01-25 through 01-26). Fixes visual showing 12-24–12-25 instead of 01-25–01-26.
- **Policy Training docs** – `docs/POLICY_TRAINING_AUTOMATION_AND_COST_VISUAL.md`: where the ETL runs, how to run it, why 01-26 can be missing (source workbook must include that column), and In-Person Training visual / source cost columns (zeros when source has no cost; ETL imputation and **Cost Per Attendee** alias in ETL project).

### Changed
- **SUMMARY** – Policy Training section: reference to Policy Training doc; note that 01-26 appears after ETL run and source has cost/alias for imputation.

### Documentation
- Cost of Training M code: 13-month window logic and deploy steps in POLICY_TRAINING doc. In-Person Training visual correctness and ETL alias for "Cost Per Attendee" (in `02_ETL_Scripts\Policy_Training_Monthly\src\policy_training_etl.py`) documented.

---

## [1.15.7] - 2026-02-13

### Added
- **Benchmark source data diagnostic** – `scripts/diagnose_benchmark_data.py` analyzes source CSVs in `05_EXPORTS\Benchmark` (or override path) and reports date coverage and scenario (A/B/C).
- **README** – Listed `diagnose_benchmark_data.py` in scripts directory structure.

### Changed
- **SUMMARY** – Documented Benchmark diagnostic run result (Scenario B): source data confirmed good (multi-month coverage); issue is in Power BI (MonthStart, relationships, date types). Pointers to `docs/BENCHMARK_VISUAL_DIAGNOSTIC.md` steps 3, 5, 7.

### Documentation
- Benchmark diagnostic outcome recorded in SUMMARY and CLAUDE.md; next steps remain in Power BI (handoff doc and diagnostic guide).

---

## [1.15.6] - 2026-02-14

### Added
- **Benchmark Power BI diagnostics and handoff**
  - `docs/BENCHMARK_VISUALS_HANDOFF_PROMPT.md` – Handoff doc for AI-assisted troubleshooting (context, fixes attempted, diagnostic steps, prompt)
  - `02_ETL_Scripts/Benchmark/` – README merge, CHANGELOG, SUMMARY, ___Benchmark_FIXED.m, ___DimMonth_dynamic.m, Benchmark_DAX_Measures.dax, IncidentCount_Matrix

### Changed
- **Benchmark DAX** – BM_YoY_Change fixed (DATEADD → EDATE for scalar dates)
- **Benchmark consolidation** – Moved 02_06 CSVs from _Benchmark_ARCHIVE_2026_02_09 to 05_EXPORTS\Benchmark; removed old 01_07 files

### Documentation
- Benchmark README, CHANGELOG, SUMMARY in 02_ETL_Scripts/Benchmark; handoff prompt for broken visuals

---

## [1.15.5] - 2026-02-13

### Added
- **Visual Export Config – Gemini Enhancement** – Merged Gemini metadata and fixed Monthly Accrual backfill path
  - **backfill_folder override** – Mappings can now specify `backfill_folder` to override `target_folder` when copying to Backfill (e.g. Monthly Accrual → `vcs_time_report`)
  - **Monthly Accrual fix** – `backfill_folder: "vcs_time_report"` so Overtime/TimeOff automation finds the file in `Backfill/YYYY_MM/vcs_time_report/`
  - **Gemini metadata** – `page_name`, `date_column`, `data_format`, `time_period` added to mappings for documentation and future smart inference
  - **New visuals** – Officer Summons Activity, SSOCC Virtual Patrol TAS Alert and Incident Activity; Chief's Projects alias added

### Changed
- **process_powerbi_exports.py** – Uses `backfill_folder` when set for Backfill copy path; otherwise uses `target_folder`
- **visual_export_mapping.json** – Enhanced with Gemini config merge; Monthly Accrual now has `normalizer_format: "monthly_accrual"` and `backfill_folder: "vcs_time_report"`

### Documentation
- **POWERBI_VISUAL_EXPORT_PIPELINE_FAQ.md** – Updated "Where files are moved" to document backfill_folder; Monthly Accrual now copies to vcs_time_report
- **docs/VISUAL_EXPORT_CONFIG_GEMINI_ENHANCEMENT.md** – New doc describing Gemini config merge and backfill_folder behavior

---

## [1.15.4] - 2026-02-13

### Added
- **CSB Workbook 2026 Setup** - Completed preparation of CSB (Crime Suppression Bureau) Excel workbook for 2026
  - Created empty template sheets for Feb-Dec 2026 (26_02 through 26_12)
  - Each template has proper structure: "Tracked Items" (Column A) and "Total" (Column B) with 26 crime categories
  - Consistent formatting matching existing 2025 sheets
  - Ready for monthly data entry

### Changed
- **CSB Workbook Structure** (work done by Claude in Excel in previous sessions):
  - Sheet naming: All 2025/2026 sheets renamed to YY_MM format (e.g., 25_01, 26_01)
  - XLOOKUP formulas: Added to MoM sheet columns Q-AH for all 2026 months
  - Formula format: References sheet columns directly (e.g., `'26_02'!$A:$A, '26_02'!$B:$B`)
  
### Documentation
- **New CSB Documentation**:
  - `docs/CSB_WORKBOOK_2026_SETUP_COMPLETE.md` - Complete workbook setup guide
  - `docs/chatlogs/claude_excel_csb_update/` - Claude in Excel session chatlog
  
### Notes
- **Data Status**: 2025 fully backfilled (25_01 through 25_12), Jan 2026 complete (26_01), Feb-Dec 2026 awaiting data
- **Integration Ready**: Workbook structure compatible with future Power BI M code queries (similar to Detective workbook pattern)
- **Auto-Update**: MoM sheet XLOOKUP formulas automatically pull data when entered in monthly sheets

---

## [1.15.3] - 2026-02-13

### Fixed
- **Detective Queries - Excel Structure Mismatch** - Fixed both Detective M code queries returning empty tables
  - **Root Cause**: Excel workbook structure differed from Claude Excel add-on's planned restructuring
    - Expected: 2026-only data with MM-YY headers (e.g., `01-26`, `02-26`)
    - Actual: Historical data (Jun 2023 - Dec 2026) with YY-MMM headers (e.g., `26-Jan`, `25-Dec`)
  - **Fix #1**: Date parsing logic - Changed from MM-YY to YY-MMM format with month abbreviation lookup
  - **Fix #2**: Rolling window calculation - Changed from hardcoded 2026-only to dynamic 13-month rolling window
  - **Fix #3**: Month display normalization - Convert YY-MMM to MM-YY format for consistent Power BI visuals
  - **Fix #4**: Row label exact matching - Handle double spaces in Excel labels for CCD query
  - **Result**: Queries now load data correctly, showing Jan 2025 - Dec 2025 (13 months)

### Changed
- **M Code Updates**:
  - `m_code/detectives/___Detectives_2026.m` - Date parsing, rolling window, month normalization
  - `m_code/detectives/___Det_case_dispositions_clearance_2026.m` - Date parsing, rolling window, month normalization, label matching
  
### Added
- **Detective Diagnostic Tools**:
  - `scripts/analyze_detective_workbook.py` - Full workbook structure analysis (sheets, tables, headers)
  - `scripts/check_detective_tables.py` - Quick table name verification
  - `scripts/check_detective_table_data.py` - Detailed table data inspection
  - `scripts/check_jan_26_data.py` - Verify 26-Jan column data status

### Documentation
- **New Detective Documentation**:
  - `docs/DETECTIVES_EXCEL_STRUCTURE_MISMATCH_FIX.md` - Root cause analysis and detailed fix explanation
  - `docs/DETECTIVES_2026_UPDATE_GUIDE.md` - Original deployment guide (now superseded by mismatch fix)
  - `docs/DETECTIVES_2026_QUICK_REF.md` - Quick reference for fixes
  - `docs/DETECTIVES_CRITICAL_FIXES_2026_02_13.md` - Summary of critical fixes
  - `docs/DETECTIVES_VERIFICATION_CHECKLIST.md` - Manual verification steps for Power BI Desktop

---

## [1.15.2] - 2026-02-13

### Fixed
- **STACP Visual - 13-Month Rolling Window** - Fixed three critical issues preventing proper data display
  - **Issue #1**: Year detection hardcoded for "24" or "25" - now works for any 2-digit year (future-proof)
  - **Issue #2**: Enhanced month validation to handle both M-YY and MM-YY formats (1-12 validation)
  - **Issue #3**: Fixed rolling window calculation - `StartMonth = EndMonth` (was `EndMonth - 1`)
  - **Result**: Visuals now correctly show all 13 months (01-25 through 01-26) instead of only 2 months

### Added
- **STACP Diagnostic Tools**
  - `m_code/stacp/STACP_DIAGNOSTIC.m` - Diagnostic query to verify column detection and window filtering
  - `scripts/analyze_stacp_workbook.py` - Python script to analyze Excel workbook structure
  - `docs/STACP_TROUBLESHOOTING_GUIDE.md` - Comprehensive troubleshooting guide

### Documentation
- **New STACP Documentation**:
  - `docs/STACP_YEAR_DETECTION_FIX_2026_02_13.md` - Year detection fix details
  - `docs/STACP_INCONSISTENT_DATE_FORMAT_FIX.md` - Date format handling
  - `docs/STACP_WINDOW_CALCULATION_FIX.md` - Window calculation fix (main issue)
  - `docs/STACP_FIX_QUICK_REF.md` - Quick reference for all fixes

### Changed
- **M Code Standards** - Added standard headers to STACP M code files per project conventions

---

## [1.15.1] - 2026-02-13

### Added
- **Smart Date Inference** - Data-driven date detection for Power BI visual exports (~95% accuracy vs ~70% filename-only)
  - **13-month visuals**: Reads CSV, uses LAST period column (most recent month in rolling window)
  - **Single-month visuals**: Reads Period/Month_Year column value from data
  - **Fallback chain**: Data → Filename pattern → Previous month
  - **Functions**: `infer_yyyymm_smart()`, `infer_yyyymm_from_data()`, `infer_yyyymm_from_path()`
  - **Examples**: Monthly Accrual reads `PeriodLabel` column → `2026_01`; Patrol Division uses last period `'11-25'` → `2025_11`

### Changed
- **`process_powerbi_exports.py`** - Integrated smart date inference
  - Replaces filename-regex-only approach with data reading
  - For 13-month visuals: uses `enforce_13_month` flag to trigger last-column logic
  - For others: searches for Period/Month_Year/PeriodLabel/Date/Month columns
  - Logs clearly show inference source: `[DATA]` or `[FALLBACK]`
- **Unicode handling** - Added `_safe_print()` helper for filenames with special characters

### Fixed
- **Unicode print errors** - Windows console encoding issues with thin space character (`\u2009`)
- **Date accuracy** - No longer depends on manual filename prefixes

### Test Results
- Processed 16 CSV files successfully (100% accuracy)
- All files dated correctly from data
- 4 files normalized with 13-month enforcement
- 4 files copied to Backfill
- Pattern matching works for dynamic names (NIBRS)

---

## [1.15.0] - 2026-02-12

### Added
- **13-month rolling window enforcement** for Power BI visual exports
  - **Normalizer** (`scripts/normalize_visual_export_for_backfill.py`): `calculate_13_month_window()`, `enforce_13_month_window()`, CLI `--enforce-13-month`; keeps **PeriodLabel** for Overtime/TimeOff backfill; period column detection order: PeriodLabel, Period, Month_Year
  - **Process script** (`scripts/process_powerbi_exports.py`): **match_pattern** (regex) in `find_mapping_for_file()` for dynamic visual names (e.g. NIBRS); **enforce_13_month** parameter in `run_normalize()`; dry-run and production pass `enforce_13_month_window` from mapping to normalizer
  - **Mapping** (`Standards/config/powerbi_visuals/visual_export_mapping.json`): 32 visuals; 24 with `enforce_13_month_window: true`, 8 with `false` (Arrests, Top 5 Summons, All Bureaus Summons, In-Person Training, Incident Distribution); NIBRS entry has `match_pattern: "^13-Month NIBRS Clearance Rate Trend"`
  - **Validation** (`scripts/validate_13_month_window.py`): validate single file or `--scan-folder` for 13-month window
- **Documentation**
  - `docs/13_MONTH_WINDOW_IMPLEMENTATION_GUIDE.md` – Deployment, data flow, validation, troubleshooting
  - `docs/13_MONTH_WINDOW_CORRECTIONS.md` – Selective enforcement, NIBRS pattern matching
  - `docs/13_MONTH_QUICK_REFERENCE.md` – List of 24 vs 8 visuals, quick test

### Changed
- **Normalizer** – Replaced with v2 logic (13-month window, PeriodLabel preserved for monthly accrual)
- **Process script** – In-place patches: match_pattern support, run_normalize(enforce_13_month), call sites pass enforce_window from mapping

---

## [1.14.0] - 2026-02-12

### Added
- **Path centralization (portability)**
  - `scripts/path_config.py` – `get_onedrive_root()` using `ONEDRIVE_BASE` or `ONEDRIVE_HACKENSACK`; fallback for local dev
  - All Python scripts that use paths now import or fall back to this (overtime_timeoff_with_backfill, validate_exports, validate_outputs, summons_backfill_merge, normalize_visual_export_for_backfill)
  - `run_all_etl.ps1` – `$OneDriveBase` from env, all validation and Save-MonthlyReport paths use `Join-Path $OneDriveBase`
- **Overtime/TimeOff hardening**
  - `scripts/validate_exports.py` – Pre-flight check for `YYYY_MM_otactivity.xlsx` and `YYYY_MM_timeoffactivity.xlsx` (existence, readable Excel, required columns Date/Hours/Employee/Group); retry on OneDrive sync lock
  - `scripts/validate_outputs.py` – Validates FIXED CSV schema (YearMonth, Class, Metric, Hours; 13 months; numeric Hours)
  - `scripts/overtime_timeoff_with_backfill.py` – Strict file discovery (exact `YYYY_MM_*.xlsx` only), distinct .xls→.xlsx conversion step; `validate_fixed_schema()` before exit
  - `scripts/test_pipeline.bat` – Runs validate_exports → overtime --dry-run → validate_outputs
- **Visual Export Normalization in orchestrator**
  - `run_all_etl.ps1` – New phase before summary: scans `_DropExports` for `*Monthly Accrual and Usage Summary*.csv`, runs `normalize_visual_export_for_backfill.py --input <path> --output <path>` (in-place); supports -DryRun
- **Summons backfill (gap months 03-25, 07-25, 10-25, 11-25)**
  - `scripts/summons_backfill_merge.py` – Full implementation: load backfill CSVs, normalize columns (RENAME_MAP), filter by gap month, align to main df, concat; MM-YY validation; Wide-format detection and warning
  - `docs/SUMMONS_BACKFILL_INJECTION_POINT.md` – Injection point for `main_orchestrator.py`, dependencies, caveats (date format, schema drift)
- **Dependencies**
  - `requirements.txt` – pandas, openpyxl for validate_exports and summons_backfill_merge
  - README and docs updated: Python environment must have these for orchestrator-run scripts

### Changed
- **Overtime/TimeOff** – Removed multi-pattern/fallback file search; paths built from `get_onedrive_root()`; `--backfill-root` default is now under OneDrive root
- **normalize_visual_export_for_backfill.py** – Default backfill root from `path_config` (`_default_backfill_root()`); `--backfill-root` optional
- **Documentation** – `docs/VISUAL_EXPORT_NORMALIZATION_AND_SUMMONS_BACKFILL.md` (normalization phase + Summons follow-up); README Quick Start: Python environment + `pip install -r requirements.txt`

### Fixed
- Orchestrator and validation no longer rely on hardcoded user paths when `ONEDRIVE_BASE` (or `ONEDRIVE_HACKENSACK`) is set

---

## [1.13.0] - 2026-02-10

### Added
- **Overtime/TimeOff – Visual backfill and normalization**
  - `data/backfill/` – Backfill CSVs from visual export (2025_12 primary, image-extracted 11-25 patch, README)
  - `scripts/normalize_visual_export_for_backfill.py` – Normalize Power BI default export (Long/Wide) for backfill; optional Long→Wide pivot; writes to `Backfill\YYYY_MM\vcs_time_report\`
  - `m_code/2026_02_10_Overtime_Timeoff_v3_CONSOLIDATED.m` – Single-query M for ___Overtime_Timeoff_v3 (no staging refs; Time_Category kept for visual binding)
  - `m_code/2026_02_10_Overtime_Timeoff_v3.m` – Main query referencing staging; `OT_FIXED_Staged.m`, `OT_MonthlyBreakdown_Staged.m`, `OT_PriorAnchor_Staged.m` for Formula Firewall separation
- **Documentation**
  - `docs/VISUAL_BACKFILL_AND_EXPORTS_FINDINGS_2026_02_10.md` – Visual/backfill/export findings (01-26 zeros, backfill flow, CSV structure)
  - `docs/VISUAL_EXPORT_COMPARISON_2026_02_10.md` – Comparison of visual exports (18_24_36 vs image vs earlier export)
  - `docs/VISUAL_EXPORT_NORMALIZE_AND_BACKFILL.md` – Why and how to normalize default visual exports (Long vs Wide, script usage, optional watchdog)
  - `docs/OVERTIME_TIMEOFF_RERUN_AFTER_BACKFILL.md` – Steps to re-run pipeline and refresh Power BI after backfill update

### Changed
- **Backfill** – Primary backfill for Monthly Accrual and Usage Summary is 2025_12 visual export (12-24 through 12-25); deployed to `PowerBI_Date\Backfill\2025_12\vcs_time_report\` and `data/backfill/`
- **Restore/pipeline** – Already accept Long format and "Sum of Value"; no code change required for default export

### Fixed
- **Visual "Fields that need to be fixed: Time_Category"** – CONSOLIDATED M keeps column name `Time_Category` so existing visual binding works
- **"Matches no exports"** – Single-query CONSOLIDATED M avoids staging query references

- [ ] Consider implementing hybrid strategy for Arrests workflow
- [ ] Document monthly execution procedures
- [ ] Create automated testing for critical workflows
- [ ] Enhanced Fresh Calculator with January 14 validation logic
- [ ] Enhanced error reporting and recovery
- [ ] Performance monitoring and optimization
- [ ] Automated testing suite
- [ ] Integration with Power BI refresh scheduling

---

## [1.12.0] - 2026-02-09

### Added
- **Response Time Backfill Baseline** - Created formal Backfill directory structure
  - Created 13 monthly directories (Jan 2025 - Jan 2026) in `PowerBI_Date\Backfill\YYYY_MM\response_time\`
  - Populated with current validated data (3 rows per month: Emergency, Routine, Urgent)
  - Established repeatable monthly workflow for adding new months
  - M code now prioritizes Backfill folder as primary data source

### Changed
- **Response Time M Code (v2.8.0 → v2.8.3)** - Backfill priority restored
  - v2.8.1: Integrated Fresh Calculator priority (_DropExports first)
  - v2.8.2: Single source only (_DropExports exclusive)
  - v2.8.3: Reverted to multi-path with Backfill priority (restored validated data)
  - Priority order: Backfill > visual_export > outputs > _DropExports
  - Ensures loading of validated data with January 14 deduplication/filtering logic

- **Response Times Fresh Calculator** - Disabled
  - Set `enabled: false` in `config\scripts.json`
  - Reason: Missing January 14, 2026 deduplication and enhanced filtering logic
  - Can be re-enabled once enhanced to match validated methodology
  - Python script remains available: `scripts\response_time_fresh_calculator.py`

### Documentation
- **New Session Documentation:**
  - `docs/RESPONSE_TIME_v2.8.2_SINGLE_SOURCE_FIX.md` - Single source approach documentation
  - `docs/RESPONSE_TIME_v2.8.3_BACKFILL_RESTORE.md` - Revert decision guide
  - `docs/BACKFILL_BASELINE_CREATED_2026_02_09.md` - Backfill structure documentation
  - `docs/RESPONSE_TIME_COMPLETE_SESSION_SUMMARY_2026_02_09.md` - Complete session summary
  - `docs/RESPONSE_TIME_FINAL_STATUS_2026_02_09.md` - Final status and checklist

### Decision Points
- **Fresh Calculator vs Validated Backfill**
  - Fresh Calculator recalculates from raw timereport data but lacks:
    - January 14 deduplication by ReportNumberNew
    - Enhanced filtering for self-initiated activities
    - Administrative task exclusions
    - Validated incident classification
  - Decision: Use validated Backfill data (January 14 methodology)
  - Future: Can enhance Fresh Calculator if needed for full recalculation

### Results
- October 2025 baseline values confirmed:
  - Emergency: 02:49 (from validated data)
  - Routine: 02:11 (from validated data)
  - Urgent: 02:52 (from validated data)
- 13-month rolling averages calculated correctly by DAX measures
- Visual 1 and Visual 2 both working with correct data
- 0% errors maintained across all months

---

## [1.11.0] - 2026-02-09

### Fixed
- **Response Time Power BI M Code (v2.8.0)** - ✅ PRODUCTION READY - Fixed 31% type conversion errors
  - Removed `type text` annotation from `Table.TransformColumns` tuple (primary fix)
  - Added `Response_Time_MMSS` to final `Typed` step for explicit column typing
  - Wrapped entire Step4 lambda in `try...otherwise "00:00"` for safety
  - Added `Number.RoundDown(Number.Round(rawSecs, 0))` for guaranteed integer seconds
  - Fixed decimal precision handling: 2.87, 2.92 now convert correctly to MM:SS format
  - Fixed unpivot column reference: removed "Month-Year" (already renamed to "MM-YY")
  - Column quality improved from 69% valid/31% errors to 100% valid/0% errors
  - **Status**: Tested with production data - 0% errors achieved ✅

### Root Cause Analysis
- **Primary Issue**: `type text` annotation in `Table.TransformColumns` caused Power Query type engine conflict
  - Power Query's auto-typing (`PromoteAllScalars = true`) typed CSV values as Number (2.87 → type number)
  - Type annotation tried to validate original Number values against declared `type text` during lazy evaluation
  - 2-decimal precision values (2.87, 2.92) triggered edge case in PQ's internal coercion pipeline
  - 1-decimal values (1.3, 2.5) passed through cleanly

- **Secondary Issue**: `Response_Time_MMSS` missing from final `Typed` step
  - `Table.Combine` lost per-file column type metadata
  - Column reverted to inferred numeric type instead of text
  - Combined with primary issue to cause 31% error rate

### Changed
- **M Code Structure** (v2.7.1 → v2.8.0)
  - Step4: Transformation lambda now outputs untyped values (no `type text` annotation)
  - Typed step: Added `{"Response_Time_MMSS", type text}` for explicit typing after combine
  - Decimal conversion: Enhanced with `Number.RoundDown()` for clean integer output
  - Time format handling: Added AM/PM stripping for time-typed values
  - Locale safety: Added `en-US` to ALL `Text.From` calls (mins, secs)
  - Empty table schema: Added `Response_Time_MMSS` column to prevent combine errors

### Test Results
| Input | Auto-Type | v2.7.1 (Before) | v2.8.0 (After) | Expected MM:SS | Expected Decimal |
|-------|-----------|-----------------|----------------|----------------|------------------|
| "2:39" | Duration | ✅ "02:39" | ✅ "02:39" | 02:39 | 2.65 |
| 1.3 | Number | ✅ "01:18" | ✅ "01:18" | 01:18 | 1.30 |
| 2.5 | Number | ✅ "02:30" | ✅ "02:30" | 02:30 | 2.50 |
| 2.87 | Number | ❌ ERROR | ✅ "02:52" | 02:52 | 2.87 |
| 2.92 | Number | ❌ ERROR | ✅ "02:55" | 02:55 | 2.92 |
| null | null | ✅ "00:00" | ✅ "00:00" | 00:00 | 0.00 |

### Documentation
- **New Session Documentation:**
  - `docs/SESSION_HANDOFF_2026_02_09.md` - Complete handoff for v2.8.0 implementation
  - `docs/CLAUDE_DEBUG_PROMPT_v2.7.1_Errors.md` - Comprehensive debugging prompt template
  - `docs/RESPONSE_TIME_PRODUCTION_READY_v2.7.1.md` - Production deployment guide (pre-v2.8.0)
  - `m_code/___ResponseTimeCalculator.m` - Updated to v2.8.0 (382 lines with full documentation)

### AI Collaboration
- **Claude Contributions** (v2.8.0 fix):
  - Identified root cause: type annotation conflict with auto-typing
  - Discovered missing column in Typed step
  - Delivered 7-point comprehensive fix
  - Created debugging prompt template for future sessions

- **Gemini Contributions** (v2.6.0-v2.7.1):
  - Identified locale safety issues (v2.6.0)
  - Introduced `Value.Is()` type-agnostic pattern (v2.7.0)
  - Enhanced locale independence with `Text.From(..., "en-US")` (v2.7.1)

### Implementation Status
- ✅ **v2.8.0 M Code Ready**: Available at `m_code\___ResponseTimeCalculator.m`
- ✅ **Production Deployment Complete**: Tested and verified with production data
- ✅ **Result Confirmed**: 0% errors, 100% valid data across all formats
- ✅ **Backup Available**: v2.7.1 backup retained for rollback if needed
- ✅ **Verification Checklist Created**: Column quality validation steps documented

---

## [1.10.0] - 2026-02-09

### Fixed
- **Overtime TimeOff Workflow Restored** 
  - Resolved missing personnel file dependency (`Assignment_Master_V2.csv`)
  - Copied file from `outputs\summons_validation\` to Master_Automation root
  - Script now successfully processes all workflows and generates 30 output files
  - Execution time: 19.92 seconds
  
- **Response Times Workflow Restored**
  - Migrated from archived `response_time` path to new `timereport` structure
  - Updated script from v2.0.0 to v2.1.0 with hybrid loading strategy
  - Implemented dual-source loading: yearly files + monthly files
  - Successfully combines 114,070 records (2025 full year) + 10,440 records (Jan 2026)
  - Generates 13 monthly CSVs covering Jan 2025 through Jan 2026
  - Execution time: 76.09 seconds

### Added
- **Response Times Hybrid Loading Strategy**
  - New function: `load_timereport_hybrid()` (110 lines)
  - Automatically loads from `timereport\yearly\YYYY\YYYY_full_timereport.xlsx`
  - Supplements with `timereport\monthly\YYYY_MM_timereport.xlsx` for current year
  - Handles year transitions automatically
  - Removes duplicates between sources
  - Configurable date range (currently Jan 2025 - Jan 2026)

- **Benchmark Directory Cleanup**
  - Consolidated duplicate directories (`_Benchmark` vs `Benchmark`)
  - Created simplified flat structure: `show_force\`, `use_force\`, `vehicle_pursuit\`
  - Archived old complex nested structure (`_Benchmark_ARCHIVE_2026_02_09`)
  - Created new M code with automatic latest file selection
  - PowerShell cleanup script: `scripts\Cleanup-BenchmarkDirectories.ps1`

- **Enhanced Validation Logic**
  - Updated `run_all_etl.ps1` Response Times validation with fallback paths
  - Updated `run_all_etl.ps1` Summons validation with fallback paths
  - Improved error messages showing all checked paths
  - Lists available files when expected file not found

### Changed
- **Response Times Script Structure**
  - `DEFAULT_INPUT_PATH` → `DEFAULT_TIMEREPORT_BASE`
  - Date range: 2024-12 to 2025-12 → 2025-01 to 2026-01 (13-month rolling window)
  - Main function now uses `load_timereport_hybrid()` instead of `load_cad_data()`
  - Version display updated to v2.1.0 (Hybrid Strategy)
  - Fixed docstring escape sequence warning

- **Power BI M Code**
  - Created `m_code\_benchmark2026_02_09.m` for simplified Benchmark structure
  - Created `m_code\_benchmark_simple.m` for easier readability
  - Both versions support automatic latest file selection
  - Include error handling for missing folders

### Documentation
- **New Session Documentation:**
  - `docs/SESSION_2026_02_09_COMPLETE_SUCCESS.md` - Complete session summary and metrics
  - `docs/RESPONSE_TIME_TIMEREPORT_MIGRATION_2026_02_09.md` - Detailed migration guide
  - `docs/BENCHMARK_CLEANUP_STRATEGY_2026_02_09.md` - Cleanup strategy and phases
  - `docs/BENCHMARK_M_CODE_IMPLEMENTATION_2026_02_09.md` - M code implementation guide
  - `docs/FINAL_GO_NO_GO_DECISION_2026_02_09.md` - Pre-run decision analysis
  - `docs/IMPLEMENTATION_CHECKLIST_2026_02_09.md` - Implementation checklist
  - `docs/QUICK_REFERENCE_2026_02_09.md` - Quick reference guide

### Results
- **Execution Success:** 100% (6/6 workflows operational)
- **Total Execution Time:** 2.04 minutes (129.9 seconds)
- **Files Generated:** 60 total output files
- **Monthly Report:** `2026_01_Monthly_FINAL_LAP.pbix` successfully saved

### Workflow Performance
- Arrests: 6.27s (2 files)
- Community Engagement: 7.86s (2 files)
- Overtime TimeOff: 19.92s (30 files) **FIXED**
- Response Times: 76.09s (15 files) **FIXED**
- Summons: 2.06s (7 files)
- Summons Derived Outputs: 8.66s (4 files)

---

## [1.9.0] - 2026-02-09

### Added
- **December 2025 Power BI Visual Export Processing**
  - Processed and organized 36 CSV exports from December 2025 monthly report
  - Created comprehensive diagnostic reports for data quality issues
  - Added `2025_12_` prefix to all exported files for organization
  - Organized 53 total files into 16 categorized subdirectories
  
### Documentation
- **New Reports Created:**
  - `docs/DECEMBER_2025_VISUAL_EXPORT_DIAGNOSTIC_REPORT.md` - Full analysis of 53 exported files
  - `docs/ENGAGEMENT_INITIATIVES_BLANK_EXPORT_INVESTIGATION.md` - Technical troubleshooting guide with 7-step investigation plan
  - `docs/DECEMBER_2025_EXPORT_QUICK_SUMMARY.md` - Quick reference action guide and validation checklist
  
### Issues Identified
- **Critical Data Quality Issues (3 total):**
  1. **Engagement Initiatives by Bureau** - Blank CSV export despite showing 22 events in PDF report
     - Expected: 22 events, 71 attendees, 15.5 hours
     - Actual: Only headers, 0 data rows (83 bytes)
     - Root cause: Date filter using `TODAY()` or relative date logic
     - Affects all 3 .pbix copies
  
  2. **Chief Michael Antista's Projects and Initiatives** - Blank CSV export
     - Expected: Data rows
     - Actual: Only headers, 0 data rows (15 bytes)
     - Same root cause as Issue #1
  
  3. **Department-Wide Summons | Moving and Parking** - Missing 4 months of 2025 data
     - Missing: March, July, October, November 2025
     - Present: 9 of 13 months (12-24, 01-25, 02-25, 04-25, 05-25, 06-25, 08-25, 09-25, 12-25)
     - Root cause: Source data gap, not export issue
  
### Changed
- **File Organization Structure:**
  - Cleaned `PowerBI_Date\_DropExports\` folder after organizing exports
  - Created `PowerBI_Date\Backfill\2025_12\` with 16 subdirectories
  - Files distributed across: arrests (3), summons (11), response_time (10), community_engagement (2),
    use_of_force (3), nibrs (2), patrol (1), traffic (4), detective (4), crime_suppression (1),
    training (2), records (1), safe_streets (2), drones (2), school (2), chief (3)

### Fixed
- **Export Workflow Issues Documented:**
  - Identified date filter logic causing blank exports
  - Provided 4 fix options with DAX/M code examples
  - Created step-by-step troubleshooting guide
  - Documented export validation checklist for future use

### Recommendations
- **Power BI Report Fixes Needed:**
  - Replace `TODAY()` functions in date filters with explicit dates or parameters
  - Create month/year parameter for dynamic report filtering
  - Test exports immediately after PDF generation
  - Implement file size validation checks before archiving

---

## [1.8.0] - 2026-02-04

### Changed
- **Major Directory Consolidation and Cleanup**
  - Consolidated duplicate directories: merged `output/` into `outputs/`, merged `verification_reports/` into `verifications/reports/`
  - Cleaned root directory from 91 files to 7 essential files (92% reduction)
  - Organized 84 files into appropriate subdirectories
  - Deleted 50 temporary Claude Code marker files (`tmpclaude-*-cwd`)
  - Deleted 6 unnecessary temporary files (Untitled files, VERSION, error logs, etc.)
  
- **Documentation Consolidation**
  - Merged README.md versions (desktop + laptop `-PD_BCI_LTP` versions)
  - Merged CHANGELOG.md versions (consolidated all version history v1.0.0 → v1.7.0)
  - Merged SUMMARY.md versions (desktop + laptop versions)
  - Deleted redundant documentation files: `README-PD_BCI_LTP.md`, `CHANGELOG-PD_BCI_LTP.md`, `SUMMARY-PD_BCI_LTP.md`, `CHANGELOG1.md`

### Added
- **New Directory Structure**
  - `docs/response_time/` - Response Time documentation and reports (13 files)
  - `docs/archived_workflows/` - Archived workflow files
  - `outputs/arrests/` - Arrest-related exports (3 files)
  - `outputs/visual_exports/` - Power BI visual exports (23 files)
  - `outputs/summons_validation/` - Summons testing data (11 files)
  - `outputs/metadata/` - Configuration and verification metadata (6 files)
  - `outputs/community_engagement/` - Community engagement data (6 files)
  - `outputs/misc/` - Miscellaneous output files (9 files)
  - `outputs/large_exports/` - Large Excel exports (2 files, 37MB)
  - `scripts/_testing/` - Benchmark and debug scripts (4 files)
  - `verifications/reports/` - Verification markdown reports (2 files)

### Fixed
- **Directory Organization**
  - Eliminated confusion between `output/` and `outputs/` directories
  - Grouped all verification code and reports in single `verifications/` directory
  - Maintained `m_code/` in root for Power BI query access (industry standard)

### Documentation
- Created `docs/DOCUMENTATION_CONSOLIDATION_2026_02_04.md` - Documentation merge summary
- Created `docs/TEMP_FILES_CLEANUP_2026_02_04.md` - Temporary files cleanup log
- Created `docs/ROOT_CLEANUP_PLAN_2026_02_04.md` - Root cleanup plan
- Created `docs/ROOT_CLEANUP_COMPLETE_2026_02_04.md` - Root cleanup completion report
- Created `docs/DIRECTORY_CONSOLIDATION_PLAN_2026_02_04.md` - Directory consolidation plan
- Created `docs/DIRECTORY_CONSOLIDATION_COMPLETE_2026_02_04.md` - Consolidation completion report
- Updated `verifications/README.md` - Documented new reports/ subdirectory structure
- Updated `.gitignore` - Added patterns for temporary files and output directories

### Infrastructure
- **Root Directory**: Reduced from 91 files to 7 essential files
- **Documentation**: Consolidated from 6 versions to 3 canonical files
- **Directory Structure**: Professional organization with clear separation of concerns
- **M Code Location**: Confirmed as standalone in root (Power BI-specific, frequently accessed)

---

## [1.7.0] - 2026-01-14

### Added
- **Response Time ETL Enhanced Filtering (v2.0.0)**
  - New JSON configuration file (`config/response_time_filters.json`) for centralized filter rules
  - Added `load_filter_config()` function for JSON configuration loading with validation
  - Updated `load_mapping_file()` to return Category_Type mapping along with Response_Type
  - Added "How Reported" filter - excludes "Self-Initiated" records from response time calculations
  - Added Category_Type filtering with inclusion override logic
  - Added specific incident filtering from configuration file
  - Added comprehensive data verification step (Step 7) with quality checks
  - Added `--config` command line argument for custom filter configuration path

### Changed
- **Response Time Monthly Generator Script (v1.0.0 → v2.0.0)**
  - Script: `02_ETL_Scripts/Response_Times/response_time_monthly_generator.py`
  - Updated `process_cad_data()` signature to accept new filter parameters
  - Processing pipeline expanded from 6 steps to 12 steps for enhanced filtering
  - Changed unmapped incident handling from error to warning (allows processing to continue)
  - Category_Type now mapped alongside Response_Type for better categorization

### Filter Logic
- **How Reported Filter**: Excludes "Self-Initiated" records (exact match, case-sensitive)
- **Category_Type Filter**: Excludes entire categories:
  - Regulatory and Ordinance
  - Administrative and Support
  - Investigations and Follow-Ups
  - Community Engagement
- **Inclusion Overrides**: 14 incidents kept despite category exclusion (Suspicious Person, Missing Person, etc.)
- **Specific Incident Filter**: 42 specific incidents excluded from non-filtered categories

### Processing Pipeline (12 Steps)
1. Deduplication by ReportNumberNew
2. How Reported filter (exclude "Self-Initiated")
3. YearMonth creation from cYear/cMonth
4. Date range filter (2024-12 to 2025-12)
5. Admin incident filter (existing)
6. Response time calculation
7. Time window filter (0-10 minutes)
8. Response Type + Category_Type mapping
9. Category_Type filter (with inclusion overrides)
10. Specific incident filter
11. Data verification
12. Final validation (valid Response_Type only)

### Configuration Files
- **New**: `config/response_time_filters.json` - JSON configuration for all filter rules
- **Updated**: Response Time ETL script now reads from configuration file

---

## [1.6.0] - 2026-01-14

### Fixed
- **Response Time ETL and Power BI Query Update**
  - Updated M code (`m_code/response_time_calculator.m`) to use correct OneDrive paths
  - Changed base path from `C:\Dev\PowerBI_Date\` to `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\`
  - Expanded data coverage from 2 months to full 13-month range (Dec 2024 - Dec 2025)
  - Added graceful handling for missing monthly files
  - Fixed deduplication to prevent double-counting when files overlap
  - Updated query name reference from `___ResponseTimeCalculator` to `response_time_calculator`

### Added
- **New Response Time Monthly Generator Script**
  - Created `02_ETL_Scripts/Response_Times/response_time_monthly_generator.py`
  - Processes consolidated CAD export file (`2024_12_to_2025_12_ResponseTime_CAD.xlsx`)
  - Generates monthly CSV files in the correct Backfill directory structure
  - Includes full pipeline: deduplication by ReportNumberNew, admin filtering, response time calculation
  - Outputs in Power BI expected format: `Response Type, MM-YY, First Response_Time_MMSS`
  - Deduplicates by ReportNumberNew (fixes multiple officer issue)
  - Filters 80+ administrative incident types
  - Calculates response times with fallback logic

### Changed
- **M Code Structure Improvements**
  - Refactored to use helper function (`ProcessCSV`) for cleaner code
  - Added configurable base path and target months list
  - Improved error handling with `try...otherwise` for optional data sources
  - Changed encoding from Windows-1252 to UTF-8 (65001) for better compatibility

### Data Coverage
- Current: December 2024 through November 2025 (12 months)
- December 2025 will be added when CAD source file is synced and ETL is run

---

## [1.5.0] - 2026-01-14

### Fixed
- **Summons ESU Organizational Update**
  - Updated Assignment_Master_V2.csv to map OFFICE OF SPECIAL OPERATIONS to PATROL BUREAU
  - Updated 4 officers (RYAN CONLON 354, MASSIMO DIMARTINO 144, JOHN KNAPP 141, DANE MARBLE 271)
  - ESU (OFFICE OF SPECIAL OPERATIONS) now correctly combined with Patrol Division totals
  - Updated summons_all_bureaus.m M code to combine ESU with Patrol Division
  - Fixed M code syntax errors (removed invalid backslashes, fixed file path formatting)

### Changed
- **Summons Bureau Grouping**
  - OFFICE OF SPECIAL OPERATIONS records now grouped with PATROL BUREAU
  - Combined totals displayed as PATROL DIVISION in Power BI visuals
  - Updated M code query to handle organizational structure changes

---

## [1.4.0] - 2026-01-13

### Fixed
- **December 2025 High Values Issue - Critical Data Integrity Fix**
  - Fixed double/triple counting from file format conversions (Watchdog script converts .xls to .xlsx and .csv)
  - Added file preference logic: process only .xlsx files when multiple formats exist (.xlsx > .csv > .xls)
  - Prevents processing same data multiple times from .xls source file and converted files
  - Removed 32,749 duplicate rows by eliminating .xls and .csv when .xlsx exists

- **Raw Time Off Data Deduplication**
  - Added deduplication with parsed dates/hours and normalized employee names
  - Improved matching by parsing dates and hours before deduplication
  - Removed 41,103 duplicate records from raw Time Off data (61,899 → 20,796 rows)
  - Ensures accurate usage calculations (Sick Time, SAT, Comp, Military, IOD)

- **Status Filtering for Usage Calculations**
  - Added approved-only filtering to raw Time Off data before usage metrics calculation
  - Removed 175 non-approved records from December 2025 usage totals
  - Ensures only approved transactions are counted in final metrics

### Changed
- **File Loading Logic**
  - Updated `load_folder()` to prefer .xlsx files over .csv and .xls for same base filename
  - Updated raw Time Off loading to use same file preference logic
  - Prevents duplicate processing when Watchdog script creates multiple file formats

- **Deduplication Strategy**
  - Main dataframe deduplication: Removed 61,222 duplicates (89,445 → 28,223 rows)
  - Raw Time Off deduplication: Removed 41,103 duplicates using parsed dates/hours
  - Deduplication now happens after parsing dates and hours for accurate matching

---

---

## [1.3.0] - 2025-12-11 - PowerBI_Date Migration to OneDrive

### Added
- **Migration verification script** (`verify_migration.ps1`)
  - Automated 8-point verification checklist
  - Validates config paths, directory structure, junctions, and script references
  - Provides detailed status report

- **Documentation**
  - `MIGRATION_VERIFICATION.md` - Comprehensive verification guide with manual check procedures
  - `VERIFICATION_SUMMARY.md` - Quick reference summary and testing steps
  - `CHANGELOG.md` - This file, for tracking all changes
  - `CURSOR_AI_PROMPT.md` - AI assistant prompt for workspace verification

### Changed
- **Configuration (`config\scripts.json`)**
  - Updated `powerbi_drop_path` from `C:\Dev\PowerBI_Date\_DropExports` to `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports`
  - Backup created: `config\scripts.json.bak`

- **Scripts**
  - `scripts\run_all_etl.ps1` - Updated next-step instructions with new PowerBI_Date path
  - Removed all references to old `C:\Dev\PowerBI_Date` paths

- **Documentation**
  - `README.md` - Updated with migration information, new directory structure, and recent updates section
  - `QUICK_START.md` - Updated all path references to new OneDrive location

### Fixed
- All path references updated to reflect OneDrive migration
- Script file path handling verified for OneDrive paths with spaces
- Documentation consistency across all files

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

### Known Issues
- ⚠️ ETL script filenames may differ from `main.py` - verification needed
  - Action: Check actual script files and update `config\scripts.json` if needed
  - Common alternatives: `arrest_python_processor.py`, `process_*.py`, `run.py`

---

## [1.2.0] - 2025-12-10 - Response Times Script Update & Full System Testing

### Added
- **MISSING_DATA_EXPORTS.md**: Documentation of ETL execution results and data export requirements
- Monthly export file support for Response Times script
- Documentation for two-phase data processing approach (backfill + monthly ETL)

### Changed
- **Response Times Script**: Updated `process_cad_data_for_powerbi_FINAL.py`
  - Changed from loading 3 historical Excel files to loading single monthly export
  - Now processes: `monthly_export\2025\2025_11_Monthly_CAD.xlsx.xlsx`
  - Script now handles only current month (November 2025)
  - Historical data (Nov 2024 - Oct 2025) handled via Power BI M code with backfill CSV files
- **Overtime TimeOff Script**: Previously corrected from v11 to v10 (confirmed working)
- **ACTION_ITEMS.md**: Updated with Response Times testing requirements and M code update needs
- **M_CODE_UPDATE_GUIDE.md**: Enhanced with Response Times specific templates

### Fixed
- Response Times script now successfully processes monthly export files
- All 7 enabled scripts tested and verified working
- File discovery in subdirectories working correctly (previous fix confirmed)

### Tested
- **Full ETL Execution**: All 7 enabled scripts executed successfully
  - Execution time: ~8 minutes
  - Files generated: 268 files
  - Scripts tested: Arrests, Community Engagement, Overtime TimeOff, Policy Training Monthly, Response Times, Summons, Arrest Data Source
- **Response Times Script**: Successfully loaded and processed November 2025 monthly export
  - Generated 66 output files
  - Completed in 6.18 seconds
- **Power BI Organization**: Successfully executed `organize_backfill_exports.ps1`
  - Organized 178 files into `Backfill\2025_12\`
  - Created categorized folder structure

### Documentation
- Updated README.md with latest status
- Updated SUMMARY.md with test results and current operational status
- Created comprehensive execution summary in MISSING_DATA_EXPORTS.md

---

## [1.1.0] - 2025-12-09 - Script Path Verification & Configuration Update

### Added
- **VERIFICATION_REPORT.md**: Comprehensive verification report documenting all script path checks
- **SUMMARY.md**: Quick reference summary of project status
- `notes` field to all script entries in `config/scripts.json` documenting path corrections

### Changed
- **Script Path Corrections**: Updated all script entry points in `config/scripts.json`:
  - **Arrests**: Changed from `main.py` → `arrest_python_processor.py`
  - **Community Engagement**: Changed from `main.py` → `src\main_processor.py`
  - **Overtime TimeOff**: Changed from `main.py` → `overtime_timeoff_13month_sworn_breakdown_v11.py` (later corrected to v10)
  - **Policy Training Monthly**: Changed from `main.py` → `src\policy_training_etl.py`
  - **Response Times**: Changed from `main.py` → `scripts\process_cad_data_for_powerbi_FINAL.py`
  - **Summons**: Changed from `main.py` → `SummonsMaster.py`
  - **Arrest Data Source**: Changed from `main.py` → `Analysis_Scripts\arrest_python_processor.py`
- **Overtime TimeOff**: Updated to use v10 instead of v11 (v11 was template, v10 is production-ready)
- **README.md**: Updated configuration examples and documentation to reflect actual script paths
- **README.md**: Added reference to verification report and updated directory structure

### Fixed
- All script paths now point to valid, existing Python files
- Script paths verified to exist on filesystem
- PowerShell script enhanced to search subdirectories for output files (`-Recurse` added to `Get-ChildItem`)

### Disabled
- **NIBRS**: Script disabled (`enabled: false`) - No Python processing script found in directory
  - Directory exists but contains only `.txt` and `.xlsx` files
  - Requires Python script creation or removal from config

### Verification Results
- ✅ **8/8 directories verified** - All paths exist
- ✅ **7/8 scripts corrected** - Valid Python entry points found and configured
- ⚠️ **0 scripts use `main.py`** - All scripts use specific entry point files
- ❌ **1 script disabled** - NIBRS has no Python script

### Notes
- None of the ETL scripts use a standard `main.py` entry point
- Each script uses project-specific filenames based on their actual implementation
- Configuration now includes `notes` field documenting the corrections

---

## [1.0.0] - 2025-12-09 - Initial Setup

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

### Under Consideration
- [ ] Web-based dashboard for ETL status
- [ ] Email notifications for failures
- [ ] Retry logic for transient errors
- [ ] Parallel script execution option
- [ ] Configuration UI

---

## Notes

- All paths are now OneDrive-synced for cloud backup and multi-device access
- Junction link allows seamless access to Master_Automation from PowerBI_Date directory
- Verification script should be run after any configuration changes
- Logs directory is auto-created on first ETL run

---

**Maintained by:** R. A. Carucci  
**Last Updated:** 2026-02-23  
**Version:** 1.17.5

## [1.15.9] - 2026-02-18

### Fixed
- **Response Time Multi-Unit Deduplication** - Critical fix to use first-arriving unit instead of file order
  - Modified `step1_deduplicate()` in `process_cad_data_13month_rolling.py`
  - Added sort by `['ReportNumberNew', 'Time Out']` before deduplication
  - Ensures accurate response times for multi-unit incidents (28.2% of calls)
  - Aligns with industry standard (NFPA 1710, CALEA) for emergency response metrics

### Added
- **Response Time Metric Definitions** - Clarified three distinct time measurements
  - Response Time (Primary): `Time Out - Time of Call` (total response time)
  - Travel Time: `Time Out - Time Dispatched` (unit travel time)
  - Processing Time: `Time Dispatched - Time of Call` (call processing time)
- **CAD Call Type Mapping File** - Created `CAD_CALL_TYPE.xlsx` from CSV source
  - Converted `CallType_Categories.csv` to Excel format with proper schema
  - Columns: `Call Type`, `Response` (649 incident type mappings)
  - Enables Response_Type classification for filtering

### Changed
- **February 2026 ETL Cycle Validation** - Implemented comprehensive pre-flight framework
  - Infrastructure validation (Python 3.14.2, dependencies, paths)
  - Source data validation (January 2026 CAD timereport available)
  - Visual export mapping audit (25/36 visuals enforce 13-month windows)
  - Quality assurance checks and multi-unit rate monitoring

### Results
- **January 2026 Response Times** (with corrected methodology):
  - Emergency: 3:11 min (347 calls, median 2:49)
  - Urgent: 2:54 min (843 calls, median 2:32)
  - Routine: 2:48 min (853 calls, median 2:02)
- **Processing Pipeline**: 10,440 → 7,501 → 2,851 → 2,043 valid records
- **Multi-unit Rate**: 28.2% (2,939 duplicate units removed)

### Documentation
- **Response Time Analysis** - Executive summaries showing multi-unit impact
- **ETL Cycle Framework** - Validation and audit procedures
- **Methodology Standards** - First-arriving unit protocol documented
- **Quality Safeguards** - Monthly multi-unit rate audits and CAD validation

---

## 2026-02-17
- Consolidated Power BI visual export mapping into one file.
- Primary path: Standards\config\powerbi_visuals\visual_export_mapping.json
- Archived prior mapping files under scripts\_archive\visual_export_mapping\2026_02_17_173019\
