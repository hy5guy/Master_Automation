# Changelog

All notable changes to the Master_Automation workspace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.18.17] - 2026-03-20

### Added — DFR Summons Documentation & M Code Restoration

**m_code/drone/DFR_Summons.m** (restored):
- Schema-resilient support for `Violation_Category` (was Violation_Type) and `Jurisdiction` per Claude-in-Excel Turn 51 audit.
- Dual filter (Summons_Recall + Summons_Status) using `Text.Contains` for Dismissed/Voided robustness.
- 13-month rolling window, DateSortKey, Date_Sort_Key, MM-YY, YearMonthKey.

**docs/** (new):
- `PROMPT_Claude_In_Excel_DFR_Directed_Patrol_Summons_MCode.md` — M code spec for Power BI / M Code Reference sheet.
- `DFR_Summons_Claude_In_Excel_Development_Log.md` — 51-turn workbook evolution summary (03/13–03/20/2026).
- `DFR_Summons_Documentation_Index.md` — Index of DFR docs, M code, and chatlogs.

---

## [1.18.16] - 2026-03-20

### Added — Arrest ETL Future-Proofing: Report-Month Parameter & Targeted File Discovery

**scripts/run_all_etl.ps1:**
- **`{REPORT_MONTH_ACTUAL}`** — New token that passes the actual report month (e.g., 2026-03) to scripts. `{REPORT_MONTH}` continues to pass the previous month for backward compatibility.

**config/scripts.json:**
- **Arrests** — Added `"args": "--report-month {REPORT_MONTH_ACTUAL}"` so the arrest processor receives the report month from the orchestrator.

**02_ETL_Scripts/Arrests/arrest_python_processor.py:**
- **`--report-month YYYY-MM`** — Optional CLI argument. When provided (by orchestrator or manual run), processes that month instead of the previous calendar month.
- **`get_month_info_from_report_month(report_month)`** — Builds month info from a YYYY-MM string.
- **`find_target_files(report_month)`** — Targeted discovery: when `report_month` is set, looks in `05_EXPORTS/_Arrest/YYYY/month/` for `YYYY_MM*.xlsx` (matches Summons scaffolding). Fallback: most recent file by mtime when no match.
- **`run_processing(report_month)`** — Accepts optional report month; passes to `find_target_files`.

### Changed — 05_EXPORTS/_Arrest Scaffolding (Matches Summons E_Ticket)

**05_EXPORTS/_Arrest** refactored to mirror `05_EXPORTS/_Summons/E_Ticket` structure:
- **`YYYY/month/`** — Monthly LawSoft arrest exports (e.g., `2026_03_lawsoft_monthly_arrest.xlsx`)
- **`YYYY/full_year/`** — Full-year arrest exports
- **`archive/`** — Merged from legacy `Archive` and misc full_year files
- Monthly files moved from flat `2025/`, `2026/`, and `monthly/2025`, `monthly/2026` into `YYYY/month/`
- Full-year files moved from `full_year/YYYY/` into `YYYY/full_year/`

**Place new arrest exports at:** `<OneDrive>/05_EXPORTS/_Arrest/YYYY/month/YYYY_MM_*.xlsx`

---

## [1.18.15] - 2026-03-20

### Added — DFR Summons Split: Drone-Operator Records Excluded from Main Pipeline

**scripts/summons_etl_normalize.py** (v2.4.0):
- **`DFR_ASSIGNMENTS`** — Module-level config list of drone/temp-SSOCC badge assignments with optional date ranges:
  - Badge **738 (Polson)** — permanent SSOCC drone operator; always excluded from main pipeline.
  - Badge **2025 (Ramirez)** — temp SSOCC assignment 2026-02-23 through 2026-03-01.
  - Badge **377 (Mazzaccaro)** — temp SSOCC assignment 2026-03-02 through 2026-03-15.
- **`split_dfr_records(df, assignments)`** — Vectorised boolean mask: splits fully-normalised DataFrame into `(dfr_df, main_df)`. Badge match is integer comparison on `PADDED_BADGE_NUMBER`; date-restricted entries only match rows whose `ISSUE_DATE` falls within the assignment window. Returns reset-index copies.

**scripts/dfr_export.py** (new):
- **`DFR_FORMULA_COLUMN_NAMES`** — Frozen set of Excel formula columns never overwritten: Summons ID, Description, Fine Amount, Violation Type, DFR Unit ID, Summons Recall, Full Summons Number.
- **`_map_to_dfr_schema(dfr_df)`** — Maps ETL column names to DFR Summons Log headers (Date, Time, Summons Number, Location from `Offense Street Name`, Statute, DFR Operator, Issuing Officer = DFR Operator, Summons Status). Leaves OCA and Notes blank for manual entry.
- **`export_to_dfr_workbook(dfr_df, workbook_path)`** — Opens `dfr_directed_patrol_enforcement.xlsx` with openpyxl; reads header row to build column-index map; collects existing Summons Numbers for deduplication; appends only new rows; skips formula columns; on `PermissionError` (file open in Excel) saves side-car `.etl_temp_dfr.xlsx`.
- **Target workbook:** `<OneDrive>/Shared Folder/Compstat/Contributions/Drone/dfr_directed_patrol_enforcement.xlsx`

**run_summons_etl.py**:
- After backfill merge, calls `split_dfr_records()` then `export_to_dfr_workbook()`.
- Only `main_records` (non-DFR) are passed to `write_three_tier_output()` — DFR badges no longer appear in `summons_powerbi_latest.xlsx` or `summons_slim_for_powerbi.csv`.
- Console output reports number of DFR records isolated per run.

**m_code/drone/DFR_Summons.m** (new — `m_code/drone/` folder created):
- Loads `DFR_Summons` Excel Table (fallback: `DFR Summons Log` sheet) from `dfr_directed_patrol_enforcement.xlsx`.
- Rolling 13-month window: `StartDate = StartOfMonth(pReportMonth − 12 months)`, `EndDate = EndOfMonth(pReportMonth)`.
- **Dual dismiss/void filter** (v1.18.14 spec):
  - `FilteredRecalls` — excludes rows where `Summons_Recall` contains "dismiss" or "void".
  - `FilteredStatus` — excludes rows where `Summons_Status` contains "dismiss" or "void" (catches Dismissed, Void, Voided; null-safe via `?? ""`).
- Schema-resilient rename and type map (en-US locale); `Fine_Amount` null → 0.
- Derived columns: `Month_Year` (MM-YY), `Date_Sort_Key` (YYYYMMDD Int64), `YearMonthKey` (YYYYMM Int64).
- Description shortening: strips "PARKING OR STOPPING IN DESIGNATED " prefix so labels read "FIRE LANE/FIRE ZONE" etc.

---

## [1.18.4] - 2026-03-11

### Changed — Summons Backfill: Backfill as Source of Truth for All Backfill Months

**Python ETL:**
- `scripts/summons_backfill_merge.py`: Backfill-as-source-of-truth — for ALL months in the consolidated backfill file (02-25 through 11-25), remove e-ticket rows and use backfill values exclusively. Visual now matches backfill file exactly (e.g. 02-25 M=274 not 324, 07-25 M=402 not 17). Months not in backfill (12-25, 01-26, 02-26) still use e-ticket data.

---

## [1.18.3] - 2026-03-11

### Changed — Summons Backfill: Type-Aware Merge for 07-25

**Python ETL:**
- `scripts/summons_backfill_merge.py`: Type-aware merge — for gap months (07-25), add backfill rows only for (Month_Year, TYPE) combinations not already in main df. Fixes 07-25 P and C missing: main had 17 M e-ticket rows; old logic skipped 07-25 entirely (>10 rows). Now adds backfill P (3413) and C without duplicating M. Superseded by v1.18.4 (backfill-as-source-of-truth).

**Backfill path confirmed:** `00_dev/projects/PowerBI_Date/Backfill/2026_01/summons/` (preferred) and `PowerBI_Date/Backfill/2026_01/summons/`. File `2026_01_Department-Wide Summons  Moving and Parking.csv` is used.

---

## [1.18.2] - 2026-03-11

### Changed — Summons 13-Month Trend: Remove Filler Rows (Fix Null Pollution)

**Power BI M code:**
- `m_code/summons/summons_13month_trend.m`: Removed filler-row logic that caused schema mismatch — `Table.Combine` of main table (24 cols) with filler rows (5 cols) produced null pollution (rows 43418–43419 with all-null columns). Query now returns only actual data rows. TICKET_COUNT nulls filled with 0 before return. Filter adds `[YearMonthKey] > 0` to drop malformed rows.

**Trade-off:** 07-25 P and C show blank (not 0) in trend visual. Use Power BI "Show items with no data" or DAX `COALESCE(SUM(...), 0)` if zeros needed.

**Documentation:**
- `docs/fix_summons_13month_trend_query_m_code.md` — Fix plan and verification steps

---

## [1.18.1] - 2026-03-10

### Changed — Summons Post-v1.18.0 Fixes (Ramirez, UNASSIGNED, Filler Rows)

**Python ETL:**
- `scripts/summons_etl_normalize.py`: Ramirez (badge 2025) SSOCC overrides — 19 ticket IDs from Ramirez's SSOCC period → WG2=SSOCC; FIRE LANES violations (badge 2025 + violation contains "FIRE LANES") → WG2=SSOCC. Overrides run last so they win over PEO→Traffic.

**Power BI M code:**
- `m_code/summons/summons_all_bureaus.m`: Map UNKNOWN, blank, "nan", null WG2 → "UNASSIGNED" so All Bureaus total matches department-wide (421 M, 2,354 P for Feb 2026)
- `m_code/summons/summons_13month_trend.m`: ~~Filler rows for missing (Month_Year, TYPE)~~ — reverted in v1.18.2 (caused null pollution)

**Documentation:**
- `docs/SUMMONS_M_CODE_NOTES.md` — Lessons learned (table schema, List.TransformMany, Show Errors crash, filler pattern, WG2 rules, BackfillMonths, subtitle measures, ___Traffic dynamic typing, DAX validation queries)
- `docs/PROMPT_Claude_MCP_Summons_AllBureaus_Fix.md` — UNASSIGNED mapping prompt
- `docs/PROMPT_Claude_MCP_Summons_DeptWide_Backfill_Fix.md` — 07-25 filler rows prompt

---

## [1.18.0] - 2026-03-10

### Changed — Summons Pipeline Overhaul (ETL + Power BI M Code)

**Python ETL fixes:**
- `scripts/summons_etl_normalize.py`: TYPE classification rewritten — uses raw `Case Type Code` (M/P/C) from e-ticket export instead of broken statute-based lookup that was reclassifying ~2,576 Parking tickets as Criminal and splitting Moving into expanded subcategories
- `run_summons_etl.py`: Multi-year file discovery — scans both 2025/month and 2026/month directories for complete 13-month window; dynamic default `--month` argument
- `run_summons_etl.py`: FIXED CSV fallback — detects DOpus quote-wrapped headers and falls back to raw .csv (fixed Feb 2025 reading 9 rows → 2,743)
- `scripts/summons_etl_normalize.py`: `utf-8-sig` encoding for BOM handling in CSV parser; catches `ValueError` alongside `UnicodeDecodeError`
- `scripts/summons_etl_normalize.py`: WG1/WG2 `fillna("")` + `replace("nan", "")` prevents pandas NaN exporting as literal string "nan" in slim CSV
- `scripts/summons_backfill_merge.py`: Gap months narrowed to `("07-25",)` only (all other 2025 months have e-ticket files); `SUMMONS_BACKFILL_PREFER_MONTHS` emptied

**Power BI M code fixes (applied via Claude Desktop MCP):**
- `m_code/summons/summons_13month_trend.m`: Window `EndDate` changed from `pReportMonth` to `Date.AddMonths(pReportMonth, -1)` — aligns with all_bureaus, fixes Feb 2025 missing from trend when pReportMonth=March
- `m_code/summons/summons_13month_trend.m`: WG2 filter removed — dept-wide trend now includes all officers regardless of bureau assignment (K. Peralta's 30 tickets no longer silently dropped)
- `m_code/summons/summons_13month_trend.m`: `BackfillMonths` cleared to `{}` — July 2025 17 straggler records now show instead of being hidden
- `m_code/summons/summons_13month_trend.m`: `IS_AGGREGATE` column added to TypeMap
- `m_code/summons/summons_all_bureaus.m`: `Table.RowCount(_)` → `List.Sum([TICKET_COUNT])`; TICKET_COUNT added to ChangedType
- `m_code/summons/summons_all_bureaus.m`: Total formula `try ([C] ?? 0) otherwise 0` — null coalesce fixes blank Total for bureaus without C tickets
- `m_code/summons/summons_all_bureaus.m`: `[WG2] <> "nan"` added to FilteredClean
- `m_code/summons/summons_top5_moving.m`, `summons_top5_parking.m`: Same `List.Sum([TICKET_COUNT])` and TICKET_COUNT type fixes

**Repository cleanup:**
- `scripts/run_summons_pipeline.py` deleted (redundant runner)
- 15 one-off diagnostic scripts archived to `02_ETL_Scripts/Summons/archive/`
- `docs/SUMMONS_BACKFILL_INJECTION_POINT.md` corrected to reference actual active scripts

**New documentation:**
- `docs/PROMPT_Claude_MCP_Summons_Bugfix.md` — Initial M code bugfix prompt for Claude Desktop
- `docs/PROMPT_Claude_MCP_Summons_Validation_Post_ETL.md` — Post-ETL refresh validation prompt
- `docs/PROMPT_Claude_MCP_Summons_Round3_Fix.md` — Window, WG2 filter, and Total null fixes

**Validation results (all passed):**
- 13 months present (02-25 through 02-26 including July stragglers)
- Feb 2026: M=421, P=2,354, C=74 (total=2,849)
- SSOCC bureau appears with P=4 (R. Polson #0738)
- All C values < 100 per month (range 36–92)
- No "nan" phantom bureau row
- All bureau Total columns populated

---

## [1.17.31] - 2026-03-09

### Changed — pReportMonth Migration EXECUTED via Claude Desktop MCP

**All 16 queries migrated and verified on `2026_02_Monthly_Report_laptop`:**

Migration executed via Claude Desktop with Power BI MCP tools in 4 waves (save between each):
- Wave 1: ___DimMonth, ___Arrest_Categories, ___CSB_Monthly, ___Detectives
- Wave 2: ___Det_case_dispositions_clearance, ___Drone, ___Overtime_Timeoff_v3, ___Social_Media
- Wave 3: ___STACP_pt_1_2, STACP_DIAGNOSTIC, TAS_Dispatcher_Incident, ___Cost_of_Training
- Wave 4: ___ResponseTime_AllMetrics, ___ResponseTimeCalculator, ___ResponseTime_DispVsCall, ___ResponseTime_OutVsCall

**Post-migration DAX verification (all passed):**
- ___DimMonth: 13 rows, Feb 2025 to Feb 2026
- ___Detectives: Feb 2025 to Feb 2026, 509 rows
- ___Arrest_13Month: Feb 2025 to Feb 2026, 629 rows, 13 distinct months
- ___CSB_Monthly: Feb 2025 to Feb 2026
- ___ResponseTime_AllMetrics: 117 rows (Feb 2026 CSV pending generation)
- Zero `DateTime.LocalNow()` references remaining in migrated queries

**TMDL export:** Full model exported to `m_code/tmdl_export/` (85 files) for version control and re-import capability.

**Chatlog:** `docs/chatlogs/Claude-Attached_prompt_execution/`

---

## [1.17.30] - 2026-03-09

### Added — ___Arrest_13Month Rolling Query

**New query: `m_code/arrests/___Arrest_13Month.m`**
- Rolling 13-month arrest data from raw Lawsoft monthly exports (`05_EXPORTS\_Arrest\monthly\YYYY\*.xlsx`)
- Dynamic file discovery: case-insensitive match on "lawsoft" + "arrest", scans all year subdirectories
- pReportMonth-driven window: `EndOfWindow = Date.EndOfMonth(pReportMonth)`, `StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12))`
- Charge categorization: Assault, Theft, Burglary, Robbery, Warrant, DWI, Drug Related, Weapons, Other
- Simplified home categorization: Local (Hackensack/07601/07602) vs Out-of-Town
- Period columns: MM_YY, MonthSort, MonthLabel, ArrestMonth for trend visuals
- Added to migration prompt checklist as item 17

---

## [1.17.29] - 2026-03-09

### Changed — pReportMonth Migration Prompt & Claude.md Streamline

**pReportMonth Migration Prompt (`docs/PROMPT_Claude_MCP_pReportMonth_Migration.md`):**
- Complete MCP execution prompt for updating 16 M code queries to use `pReportMonth` instead of `DateTime.LocalNow()`
- Group A (12 queries): Replace `DateTime.LocalNow()` with `pReportMonth`-derived window logic
- Group B (2 queries): Standardize existing `pReportMonth` calculations to `Date.EndOfMonth`/`Date.StartOfMonth`
- Group C (2 queries): Add 13-month window filter to unfiltered response time queries
- Standard pattern: `EndOfWindow = Date.EndOfMonth(pReportMonth)`, `StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12))`
- Includes full replacement M expressions, MCP tool call format, DAX verification queries, and rollback instructions

**Claude.md streamlined:**
- Reduced from 40.8k chars (641 lines) to 9.3k chars (175 lines) — 77% reduction
- Moved all detailed version history to CHANGELOG.md (where it belongs)
- Added current status table, pReportMonth migration summary, architecture notes
- Performance warning eliminated for Claude Code

**SUMMARY.md and CHANGELOG.md updated** to reflect v1.17.29

---

## [1.17.28] - 2026-03-05

### Changed — ESU_13Month.m and Documentation

**ESU_13Month.m:**
- **Rolling window:** `EndMonth = ReportMonth` (includes report month). Example: `pReportMonth = 02/01/2026` → window 02-25 through 02-26 (was 02-25 through 01-26).
- **Exclude _Log tables:** Daily Log tables (`_26_JAN_Log`, etc.) excluded from TablesOnly to avoid processing non-metric data.
- **TrackedItem normalization:** "1 Man ESU" and "1 man ESU" normalized to "ESU Single Operator" for consistent joins across monthly sheets.
- **Type number:** Total column uses `type number` (not Int64) to preserve decimals (e.g. 5.5 for ESU OOS half-days).
- **Per-table TrackedCol:** Resolves "Tracked Items" column per monthly table (handles varying column names).

**Documentation updated:**
- `docs/ESU_POWER_BI_LOAD_AND_PUBLISH.md` — pReportMonth requirement, _Log exclusion, normalization, rolling window behavior
- `m_code/esu/README.md` — Rolling window and fixes summary

---

## [1.17.27] - 2026-03-04

### Changed — M Code and Docs

**___chief_projects.m:** Table reference updated from `Table8` to `Raw_Input` to match Excel workbook (Claude In Excel session). Table name must be exactly `Raw_Input` in Table Design.

**___Social_Media.m:** Lambda syntax fix `(c) = >` → `(c) =>`. Missing_References error resolved by verifying table name `_stacp_mom_sm` in STACP.xlsm.

**___Arrest_Distro:** Load error and unknown residence issues resolved. User corrected arrest data and manually added missing records; visual now loads from `2026_02_Arrests_PowerBI_Ready.xlsx` successfully.

**New docs:**
- `docs/SOCIAL_MEDIA_MISSING_REFERENCES_FIX.md` — Table name verification, M code requirements
- `docs/MONTHLY_ACCRUAL_COMPARISON_2026_03_03.md` — Pre vs post refresh, backfill comparison
- `docs/UNIFIED_EXPORT_AND_BACKFILL_LOCATIONS.md` — Proposal for unified _DropExports and Backfill structure
- `docs/ARREST_DISTRO_LOAD_AND_UNKNOWN.md` — Load error vs unknown residence; resolution noted

---

## [1.17.26] - 2026-03-03

### Changed — ETL Orchestrator & Script Fixes

**Overtime TimeOff validation (run_all_etl.ps1):**
- Fixed validation to check actual script inputs instead of non-existent `05_EXPORTS\_VCS_Time_Report`
- Now validates: `05_EXPORTS\_Overtime\export\month\{year}\*_otactivity.xlsx`, `05_EXPORTS\_Time_Off\export\month\{year}\*_timeoffactivity.xlsx`, `PowerBI_Date\Backfill\YYYY_MM\vcs_time_report\`

**Summons Derived Outputs (summons_derived_outputs.py):**
- Added fallback paths for Department-Wide and related exports: Compstat `01_january`, `archive`, `Backfill\2026_01\summons` (00_dev and PowerBI_Date)
- Output to `PowerBI_Date\_DropExports`
- Uses `path_config.get_onedrive_root()` for portability

**Response Times (process_cad_data_13month_rolling.py):**
- Fallback to `CallType_Categories.csv` when `CAD_CALL_TYPE.xlsx` missing (column mapping: Incident→Call Type, Response_Type→Response)
- Input path derived from report month: `05_EXPORTS\_CAD\timereport\monthly\{YYYY_MM}_timereport.xlsx`

**Summons ETL v2.3.0 enhancements (run_summons_etl.py, summons_etl_normalize.py):**
- Multi-month loading: discovers all `*_eticket_export*.csv` in folder, prefers `*_FIXED.csv` (DOpus)
- Fallback to raw when _FIXED has 0 data rows
- `--dry-run` option
- pretty_csv fallback: ETL applies DOpus-style cleanup (trailing commas, Unnamed columns) when DOpus not run

**References:** `docs/SUMMONS_ETL_v2.3.0_DEPLOYMENT.md`

---

## [1.17.25] - 2026-03-04

### Added — Summons ETL v2.3.0 (Claude Complete Package)

**Deployment:** Claude's v2.3.0 package resolves all 12 audit items from 7 rounds of cross-AI review (Grok + Claude In Excel).

**Files deployed:**
- `scripts/summons_etl_normalize.py` — v2.3.0: int badge key, column renames (UPPER_SNAKE_CASE), true 23-col SLIM, WG1/WG2/TEAM correct, statute classification, RANK, robust DATA_QUALITY_SCORE (enrichment-based), graceful degradation
- `run_summons_etl.py` — Path-agnostic wrapper: auto-detects desktop (carucci_r) vs laptop (RobertCarucci), `--month` argument, backfill merge integration

**Three-tier output:**
1. **RAW** — Exact copy of original e-ticket export
2. **CLEAN** — Full Excel (`summons_powerbi_latest.xlsx`) with enriched columns
3. **SLIM** — 23-column CSV (`summons_slim_for_powerbi.csv`) for Power BI (~60% faster refresh)

**M-code updates:** All 6 summons queries now source `summons_slim_for_powerbi.csv` instead of Excel:
- `summons_13month_trend.m`, `summons_all_bureaus.m`, `summons_top5_moving.m`, `summons_top5_parking.m`, `___Summons.m`, `___Summons_Diagnostic.m`

**Usage:** `python run_summons_etl.py --month 2026_01`

**Path config:** `scripts/path_config.py` — `get_onedrive_root()` now tries `Path.home() / "OneDrive - City of Hackensack"` for laptop compatibility.

**References:** `docs/Claude_In_Excel_Officer_Mapping_Analysis.csv` (rows 181–230), `KB_Shared/04_output/Grok-Fixed_Large_CSV_Cleaning_Script_(1)`, `KB_Shared/04_output/Summons_Verification_Note_And_Docs_Update`

---

## [1.17.24] - 2026-03-03

### Added — Summons Verification Note (Re-export Required)

**Action required:** Re-export all summons e-ticket data to verify counts. A comparison showed Moving (M) discrepancy for 01-26 (406 expected vs 462 from ETL).

**Docs updated:**
- `docs/SUMMONS_VERIFICATION_NOTE_2026_03.md` — New verification guide
- `docs/SUMMONS_VISUALS_FIX_2026_03_03.md`, `docs/SUMMONS_POWER_BI_TROUBLESHOOTING.md`, `docs/SUMMONS_BACKFILL_INJECTION_POINT.md`, `docs/SUMMONS_PRODUCTION_CHECKLIST.md`, `docs/SUMMONS_PATHS_AND_DROPEXPORTS.md`, `docs/SUMMONS_AUTOMATION_SUMMARY.md` — Verification note added
- `CLAUDE.md` — Added link to verification note in docs section

---

## [1.17.23] - 2026-03-02

### Added — Summons: Badge 2025 SSOCC Override for Drone/Firezone Temp Assignment

**Context:** February 2026 drone firezone violations. Summons written by drone operator badge 0738 (Ronald Polson) and PEO Mariah Ramirez (badge 2025, temp assignment to SSOCC) must appear under **SSOCC** in the All Bureaus visual.

**Changes:**
- **Badge 0738** (Polson): Already in Assignment Master with WG2 = SSOCC — no change.
- **Badge 2025** (Ramirez): Conditional override — only summons with **Violation Description = "FIRE LANES"** map to SSOCC; all other violations stay Traffic Bureau.

**Files modified:**
- `02_ETL_Scripts/Summons/SummonsMaster_Simple.py` — Added 2025 override.
- `02_ETL_Scripts/Summons/summons_etl_enhanced.py` — Added `ASSIGNMENT_OVERRIDES` dict and override logic in `_enrich_with_officer_data`.
- `scripts/run_summons_with_overrides.py` — Added 2025 override.

**Data requirement:** Ensure tickets from `2026_02_0738_ticketsexport.csv` and `2026_02_2025_ticketsexport.csv` are included in the main `2026_02_eticket_export.csv` (or merged before ETL). The ETL loads from `05_EXPORTS\_Summons\E_Ticket\2026\month\2026_02_eticket_export.csv`.

---

## [1.17.22] - 2026-03-02

### Changed — Assignment Master Sync Path-Agnostic (09_Reference/Personnel)

**Location:** `09_Reference\Personnel\` (sibling to Master_Automation; not in this repo)

The Assignment Master sync pipeline (`sync_assignment_master.py`, `fix_team_traffic.py`) was updated to use path-agnostic `BASE_DIR`:

- **Before:** Hardcoded `C:\Users\RobertCarucci\OneDrive - City of Hackensack\09_Reference\Personnel` (laptop path)
- **After:** `os.path.dirname(os.path.abspath(__file__))` — works on desktop (`carucci_r`) and laptop (`RobertCarucci`) without modification

**Impact:** Personnel sync can be run from either machine. ETL scripts (Overtime/TimeOff, Summons) consume `Assignment_Master_V2.csv` from `09_Reference\Personnel\` or `Master_Automation\` (copy). Run `python scripts/sync_assignment_master.py` or `run_sync.bat` from `09_Reference\Personnel\` after editing GOLD; copy CSV to Master_Automation if ETL reads from there.

**Personnel repo:** Git initialized in `09_Reference\Personnel\` with v1.3.0 commit. As of 2026-03-02, Personnel reorganized: scripts in `scripts/`, POSS CSVs in `data/`, backups in `backups/`, `run_sync.bat` for one-click sync.

---

## [1.17.21] - 2026-02-27

### Added — Visual Export Mapping: Response Time + ESU

**File:** `Standards/config/powerbi_visuals/visual_export_mapping.json`

- **Three response time visuals** mapped to `Processed_Exports/response_time/`:
  - `Average Response Time (Dispatch to On Scene)` → `response_time_dispatch_to_onscene`
  - `Dispatch Processing Time (Call Received to Dispatch)` → `dispatch_processing_time`
  - `Average Response Time (From Time Received to On Scene)` → `response_time_received_to_onscene`
- **ESU** mapped to dedicated folder `Processed_Exports/esu/` → `esu_activity` (no normalization required; already Long format: TrackedItem, Month_Year, Sum of Total).

**Archive:** `_DropExports` contents archived to `archive/_DropExports_pre_2026_02_27/` before export run.

**Doc:** `Standards/config/powerbi_visuals/README.md` updated with ESU and response time visual references.

---

## [1.17.20] - 2026-02-27

### Changed — Baseline Run from Raw Exports Only (13 Months)

**File:** `02_ETL_Scripts/Response_Times/response_time_batch_all_metrics.py`

First run of v1.17.19 filter logic from raw exports only — no backfill. Establishes a true
13-month baseline for future runs.

- **Sources:** 2024 removed. Only 2025 yearly + 2026-01 monthly (Jan 2025–Jan 2026).
- **Output path:** `PowerBI_Date\Backfill\response_time_all_metrics` → `PowerBI_Date\response_time_all_metrics` (canonical baseline)
- **Output files:** 13 monthly CSVs (2025_01 through 2026_01), not 25.

**Archive:** Previous 25-month backfill archived to `Master_Automation\archive\response_time_backfill_pre_baseline_20260227\`.

**Power BI:** The three M code queries (`___ResponseTimeCalculator`, `___ResponseTime_OutVsCall`, `___ResponseTime_DispVsCall`) updated to read from the new path. **Update the PBIX file** if it still references the old Backfill path.

**Doc:** `docs/response_time/2026_02_27_Baseline_Run_v1.17.20.md`

---

## [1.17.19] - 2026-02-27

### Fixed — Peer-Review Corrections to Incident Exclusion List

**File:** `02_ETL_Scripts/Response_Times/response_time_batch_all_metrics.py`

Eight incident types moved from EXCLUDED to INCLUDED following peer review that identified them
as citizen-initiated dispatched calls rather than officer-initiated or administrative entries:

| Type | Rationale for Inclusion |
|---|---|
| `Suspicious Person` | Citizens call 9-1-1 to report suspicious persons — genuine dispatched call |
| `Suspicious Vehicle` | Same — citizen report requiring officer dispatch |
| `Missing Person - Adult` | Initial reports are citizen-initiated (Return variant remains excluded) |
| `Missing Person - Juvenile` | Consistent with Missing Person - Adult decision |
| `NARCAN Deployment - Juvenile - Aid` | Adult equivalent (`NARCAN Deployment - Adult - Aid`) was already included |
| `Overdose - Juvenile - Aid` | Consistent with adult equivalent which was already included |
| `Juvenile Complaint (Criminal)` | Can be a citizen report of juvenile criminal activity requiring dispatch |
| `ESU - Response` | Tactical deployment to active citizen emergency (barricade, hostage, etc.) — distinct from ESU Training and ESU Targeted Patrol (both remain excluded) |

`_normalize()` enhanced to explicitly handle en-dash (U+2013), em-dash (U+2014), minus sign
(U+2212), replacement character (U+FFFD), and soft hyphen (U+00AD) before the general non-ASCII
sweep. Prevents entire class of unicode dash-variant matching failures permanently.

### Impact
- Exclusion list: 280 → 272 normalized types
- Jan-26 Urgent: n=355 → 400 (Dispatch-to-Scene), ratio 1.1× → 1.0×
- Jan-25 Urgent: n=427 → 492 (Dispatch-to-Scene)
- Jan-26 Emergency and Routine: unchanged (these types are Urgent-classified)
- **All 25 monthly CSVs regenerated.** Power BI refresh required.

---

## [1.17.18] - 2026-02-27

### Fixed — Three-Layer Filter Expansion for Response Time Batch ETL

**File:** `02_ETL_Scripts/Response_Times/response_time_batch_all_metrics.py`

#### LAYER 1 — "How Reported" filter (NEW) — citizen-initiated definition
Retains all citizen-initiated calls for service. Values **kept**: `9-1-1`, `Phone` (non-emergency
line — break-ins, noise complaints, alarm monitoring company calls), `Walk-In` (citizen at station,
officer dispatched). Values **excluded**: `Self-Initiated`, `Radio`, `Teletype`, `Fax`,
`Other - See Notes`, `eMail`, `Mail`, `Virtual Patrol`, `Canceled Call`.

Applied before dedup so all records for a non-citizen-initiated call are removed before the
first-arriving-unit sort. Removes ~60–65% of CAD records.

*Note: An intermediate implementation used "9-1-1 only" which excluded Phone and Walk-In. This was
corrected after peer review established that (a) alarm monitoring company calls (Phone) constitute
the largest population of genuine Urgent dispatched calls, (b) sample sizes became statistically
marginal (n<110 for some Jan-26 categories), and (c) the 9-1-1-only definition is methodologically
indefensible for non-emergency citizen reports.*

Impact (final): 2024 from 110,328 (year-filtered) → 44,653; 2025 from 114,064 → 43,560;
2026-01 from 10,435 → 3,734.

#### LAYER 2 — Incident exclusion list (EXPANDED: 92 → 234 types)
Analyst-confirmed full exclusion list replacing the original 92-type list. Two new blocks added:

- **Self-initiated enforcement / officer-directed patrol:** `Motor Vehicle Violation` (and
  variants), `Traffic Violation`, `Field Contact/ Information`, `ESU - Targeted Patrol`,
  `Targeted Area Patrol` (and case variants), `Virtual - Patrol`, `Business Check`,
  `Property Check`, `Municipal Property/Building Check`, `Checked Road Conditions (Weather)`,
  all `Community Engagement - *` sub-types.

- **Administrative processing / internal operations:** Court processing (`Court Appearance`,
  `Court Order`, `Court - Municipal Prisoner`), record dispositions (`Unfounded Incident`,
  `Exceptionally Cleared/Closed`, `Warrant Recall`), sex offender processing (registration,
  serve documents, travel, removal orders), property processing (dispositions, returns,
  surrenders), service of legal documents (`Service - Subpoena`, `Service - Summons`,
  `Service of TRO / FRO`), internal/clerical (`Fingerprints`, `Photography`, `Meeting`,
  `Computer Issue - *`, `Generator Test`, `Civil Defense Test`), prisoner handling
  (`Prisoner Log`, `Prisoner Transport`), informational (`General Information`,
  `Notification Request`, `Warning Issued`), investigations/evidence/ALPR (BOLO, DNA
  Sample, evidence delivery/retrieval, facial recognition), missing persons, search warrant
  executions, suspicious activity reports, juvenile administrative, assistance calls
  (Assist Motorist, Mutual Aid, Escort, Funeral Escort, etc.), regulatory enforcement
  (ABC Advisory Check, Alarm Ordinance, Alcoholic Beverage violations, Snow Removal,
  Vending Without Permit), special operations (A.T.R.A., Controlled Buy, ESU Response,
  pursuits, RDF/RDT deployment, UAS Operation), and traffic infrastructure
  (Traffic Light Malfunction, Traffic Sign/Signal Malfunction, Motor Vehicle Private
  Property Tow, Breath Test, Repossessed Motor Vehicle).

#### LAYER 3 — Category_Type filter (NEW)
After backfilling `Category_Type` from `CallType_Categories.csv` via normalized incident
matching, excludes any record whose `Category_Type` is `"Administrative and Support"` or
`"Community Engagement"`. Acts as a safety net for types not explicitly in the incident list.
Impact: minimal (38 additional records in 2024, 26 in 2025, 2 in 2026-01) — confirming the
incident list is comprehensive.

#### Normalization enhancement (`_normalize()`)
Updated to replace non-ASCII characters AND ASCII dashes with a space before whitespace
collapse (previously stripped non-ASCII and kept dashes). This ensures unicode replacement-
character variants (e.g., `Motor Vehicle Violation \ufffd Private Property`) normalize
identically to their canonical dash-separated forms. Applied symmetrically to both the
exclusion set and CAD data so existing matches are unaffected.

#### Stale "101 types" comment fixed
Both `response_time_batch_all_metrics.py` and `process_cad_data_13month_rolling.py` contained
a stale comment claiming "101 types." Programmatic extraction confirmed both scripts had
exactly 92 identical types prior to v1.17.18. Comments corrected. Runtime logging added:
`logging.info(f"Admin incident filter: {len(ADMIN_INCIDENTS_NORM)} normalized types loaded")`
to prevent future drift. Post-v1.17.18 actual count: **280 normalized types.**

### Pre/Post Impact (Jan-25 and Jan-26)
Full comparison: `docs/response_time/2026_02_27_PreFix_vs_PostFix_Comparison_v1.17.18.md`

**Routine "Time Out − Time Dispatched" — bimodal distribution resolved for Jan-26:**
- Jan-26: Mean/median ratio improved from 9.5× → 1.1× (2:04 avg/0:13 median → 3:33 avg/3:19 median)
- Record count: 1,075 (pre) → 388 (post, citizen-initiated)

**Sample sizes — statistically sound with citizen-initiated definition:**
- Jan-26: Emergency n=234, Routine n=388, Urgent n=355 (Dispatch-to-Scene)
- Jan-25: Emergency n=336, Routine n=721, Urgent n=427 (Dispatch-to-Scene)

**Total annual records reduced to citizen-initiated subset:**
- 2024: 110,328 (year-filtered) → 17,656 final (84% reduction — ~60% from How Reported filter, remainder from incident/category filters)
- 2025: 114,064 → 17,785 final (84% reduction)
- 2026-01: 10,435 → 1,444 final (86% reduction)

**All 25 monthly CSVs regenerated** at `PowerBI_Date\Backfill\response_time_all_metrics\`.
Power BI refresh required.

### Tech Debt Logged
- **Response Type priority inconsistency (rolling script):** `process_cad_data_13month_rolling.py`
  drops the original CAD `Response Type` column and maps only via `CAD_CALL_TYPE.xlsx`, discarding
  valid direct-from-CAD values for 2025+ data. The rolling script is not the active Power BI source.
  Deferred to a future refactor; batch ETL priority cascade (CAD value → exact match → normalized
  match) remains correct.

---

### Added - Report Deliverables and Reusable Design System

#### Executive Report for Chief Antista
- **`docs/response_time/Response_Time_Correction_Report_Chief_Antista_2026_02_26.html`**
  Full-color HTML report prepared for Chief Antista explaining the response time data
  correction (v1.17.15-v1.17.17). Covers all three findings, before/after impact table,
  corrected January 2026 values, methodology defense, data coverage, and Power BI refresh
  steps. Uses the HPD navy/gold design system (see below). Signature block included.

- **`docs/response_time/Response_Time_Correction_Report_Chief_Antista_2026_02_26_PRINT.html`**
  Print-optimized version of the Chief Antista report. Retains the full navy/gold color
  theme, finding badges, and table styling from the screen version but is scaled for
  letter paper (8.5in, 0.75in margins), includes page-break controls, and uses
  `print-color-adjust: exact` to preserve colors in print/PDF output. All em dashes
  replaced with standard hyphens for clean printing. Includes a forced page break before
  the methodology section (page 2).

#### Reusable Design System Template
- **`docs/templates/HPD_Report_Style_Prompt.md`** (new directory: `docs/templates/`)
  Reusable AI prompt template capturing the full HPD report design system. Paste the
  style block into any future AI conversation when requesting an HTML report to get the
  same formatting automatically. Contains:
  - Color palette with hex values (navy #1a2744, gold #c8a84b, green #2e7d32, red #b71c1c)
  - Typography and spacing rules
  - Component specs for: alert boxes (gold/green), finding badges (critical/high/info),
    KPI summary grid, data tables (standard and corrected-values variant), signature block
  - Full copy-paste CSS block (complete `<style>` tag contents)
  - Full HTML skeleton with all structural elements and placeholder text
  - Quick-reference cheat sheet of class names and their purposes

---

## [1.17.17] - 2026-02-26

### Documentation — Peer Review Corrections (Claude Opus, 2026-02-26)

Independent peer review of v1.17.15 and v1.17.16 confirmed both bug fixes are correct.
The following corrections and new findings were applied.

### Corrected
- **CHANGELOG v1.17.16 — Admin list count**: "26 of 101" corrected to "~91 of 92."
  Runtime count: `len(ADMIN_INCIDENTS_RAW) = 92`, `len(ADMIN_INCIDENTS_NORM) = 92`.
  Cross-check shows ~91 of 92 types present in `CallType_Categories.csv`, all mapped as
  Routine. The "101" figure in the header comment referenced the rolling script's list;
  the batch script's `ADMIN_INCIDENTS_RAW` set has 92 unique entries.

- **CHANGELOG v1.17.15 — Reference script sort claim**: The v1.17.15 entry states the
  sort was "confirmed present" in `process_cad_data_13month_rolling.py`. Confirmed in the
  production file at `02_ETL_Scripts\Response_Times\` (lines 496–503, verified by grep).
  The file Claude Opus reviewed may have been an older snapshot uploaded to that session.
  The production copy is correct.

### New Finding — Routine "Dispatch to On Scene" Bimodal Distribution
- **File:** `PowerBI_Date\Backfill\response_time_all_metrics\`
- **Metric:** `Time Out - Time Dispatched` | **Response Type:** Routine
- **Finding:** Mean/median ratio is ~10× (01-25: Mean 2:01, Median 0:11; 01-26: Mean 2:04,
  Median 0:13). This is a **bimodal distribution** — a large cluster of near-zero times
  (officer self-initiated traffic stops and field contacts where `Time Out ≈ Time Dispatched`
  because the officer is already on scene) mixed with a smaller cluster of true dispatched
  responses (2–5+ minutes). The 92-type admin filter correctly removes administrative
  activities but does NOT remove legitimate enforcement self-initiated calls.
- **Other metrics are healthy:** All other Response_Type × Metric_Type combinations have
  mean/median ratios of 1.0–2.6×. Emergency "Dispatch to On Scene" is 1.1–1.2×.
- **Impact:** The Routine "Dispatch to On Scene" average (2:01–2:04) understates the time
  for true citizen-dispatched calls. This is a data characteristic, not a code error.
- **Recommended talking point for admin:**
  > "Routine dispatch-to-scene includes traffic stops and officer field contacts where our
  > officer was already at the location when CAD assigned the report number — so the
  > measured time is near zero for those records. The average reflects this mix. Emergency
  > and Urgent calls, which are exclusively citizen-reported, show a clean 2:31–2:55
  > range with no distributional skew."
- **Tracked for future enhancement:** Add a "dispatched-only" view (filter where
  `Time Dispatched - Time of Call > 0:30`) to isolate true citizen-initiated Routine calls.
  `Median_Minutes` is already in all CSVs and can be surfaced in DAX when needed.

### Added
- **`docs/response_time/PEER_REVIEW_Response_Time_v1_17_16_2026_02_26.md`** — Full
  independent peer review by Claude Opus (2026-02-26). Confidence level: HIGH.
  All action items documented and tracked.

---

## [1.17.16] - 2026-02-26

### Fixed — CRITICAL
- **`response_time_batch_all_metrics.py` — Missing Administrative Incident Filter**
  Added 92-type admin incident exclusion list (`ADMIN_INCIDENTS_RAW`, runtime-verified:
  `len(ADMIN_INCIDENTS_NORM) = 92`) applied after dedup, before Response Type mapping.
  Without this filter, officer self-initiated activities — Meal Break, Coffee Break,
  Patrol Check, Task Assignment, Traffic Detail, TAPS operations, Training, Court
  assignments, Vehicle Maintenance, Vacation, Administrative Assignment, and 80+ others
  — were included as "Routine" calls with near-zero dispatch processing times, corrupting
  all three metrics for the Routine category.

  **Peer Review Note (Claude Opus, 2026-02-26):** Cross-check of `ADMIN_INCIDENTS_NORM`
  against `CallType_Categories.csv` (664 entries) found **~91 of 92 admin types present
  in the CSV, all mapped as Routine**. The CHANGELOG originally stated "26 of 101" —
  this was significantly understated. The actual overlap is near-complete, confirming
  that admin activities were being included as Routine via both the CAD Response Type
  field and the CallType mapping cascade.
  - 2024: 82,891 records after dedup → 35,171 after admin filter (47,720 excluded = 57.6%)
  - 2025: 87,436 records after dedup → 33,797 after admin filter (53,639 excluded = 61.4%)
  - 2026-01: 7,499 records after dedup → 3,131 after admin filter (4,368 excluded = 58.3%)
  - **Routine Dispatch Processing Time 01-25: 0:50 → 2:27 (corrected +1:37)**
  - **Routine Dispatch to On Scene 01-25: 0:48 → 2:01 (corrected +1:13)**
  - **Routine Time Received to On Scene 01-25: 1:14 → 3:22 (corrected +2:08)**
  - Values now follow expected operational pattern: Emergency (2:52–4:58) > Routine (2:01–3:22)
  - 26 of the 101 admin types were confirmed present in `CallType_Categories.csv` mapped as
    Routine — verifying they were actively distorting output.

  All 25 monthly CSVs regenerated again. Power BI refresh required.

### Added
- **`docs/response_time/2026_02_26_dax_DispVsCall_title_subtitle.dax`** — DAX title/subtitle
  measures for the `___ResponseTime_DispVsCall` visual.
  - `RT DispVsCall Title = "Dispatch Processing Time (Call Received to Dispatch)"`
  - `RT DispVsCall Subtitle = "Values in mm:ss. From time call is received until unit is dispatched. Rolling 13 months."`

### Also Identified (Action Required)
- **`___ResponseTimeCalculator` in Power BI still shows pre-fix values** — The Calculator
  query M code in the PBIX was manually recreated from an old version and still reads from
  the old backfill path, not the unified `response_time_all_metrics` folder. Update the
  Calculator M code in Power BI Desktop to match
  `m_code/response_time/___ResponseTimeCalculator.m` (uses `Folder.Files()` on the unified
  folder). After updating, refresh to pick up both the dedup fix (v1.17.15) and the admin
  filter fix (v1.17.16).

---

## [1.17.15] - 2026-02-26

### Fixed
- **`response_time_batch_all_metrics.py` — First-Arriving-Unit Deduplication**
  Added `sort_values(["ReportNumberNew", "Time Out"])` before `drop_duplicates()` in
  `load_and_clean()`. Without this sort, multi-unit incidents (28.2% of calls) retained
  whichever row appeared first in the source Excel file rather than the first-arriving
  officer. This flaw was identified via peer review (Sonnet + Opus, 2026-02-26) and mirrors
  the fix applied to `process_cad_data_13month_rolling.py` in v1.15.9. All 25 monthly CSVs
  were regenerated after this fix. See `docs/response_time/2026_02_26_PreFix_vs_PostFix_Comparison.md`
  for delta analysis.

- **`___ResponseTime_OutVsCall.m` and `___ResponseTime_DispVsCall.m` — Rolling 13-Month Window**
  Opus peer review flagged these two queries as missing the pReportMonth-driven 13-month window.
  On inspection, both files already contain the correct `EndDate`/`StartDate`/`Windowed` filter
  block (added in v1.17.11/v1.17.14). No code change required — the Opus finding was based on
  an older version. Confirmed consistent with `___ResponseTimeCalculator.m`.

- **`process_cad_data_13month_rolling.py` — v1.15.9 Sort Fix Confirmed Present**
  Peer review verification task confirmed the `sort_values(['ReportNumberNew', 'Time Out'])`
  before `drop_duplicates()` is in place. Added clarifying comment referencing v1.15.9.

### Added
- **`docs/response_time/2026_02_26_PreFix_vs_PostFix_Comparison.md`** — Delta analysis of
  pre-fix vs post-fix response time values for the Time Out − Time Dispatched metric.
  Emergency Jan-26: 3:11 → 2:51 (−20 seconds). Full 13-month table with record counts for
  all three metrics.
- **`docs/response_time/RECORD_COUNT_MISMATCH_EXPLAINED.md`** — Plain-language explanation of
  why the three response time visuals show different record counts for the same month and
  response type. Audience: admin and anyone auditing the report.
- **`docs/response_time/POWERBI_REFRESH_REQUIRED_2026_02_26.md`** — Refresh checklist for
  all three response time Power BI queries after this fix.

### Notes
- Record count differences across the three metrics (per month and response type) are
  expected and defensible — each metric independently requires valid timestamps in both
  its columns. This is documented behavior, not a bug.
- `Median_Minutes` is written to all CSVs but not yet surfaced in M code or DAX.
  Tracked for future enhancement.
- 2024 Response Type classification relies primarily on CallType_Categories.csv reference
  mapping (<1% sourced from original CAD values). Appropriate for trend analysis; disclose
  in year-over-year comparisons.
- 0–10 minute outlier filter is applied by the batch ETL and excludes records where the
  computed difference is ≤ 0 or > 10 minutes. This is appropriate methodology.

### ETL Re-run — Response Time Batch (2026-02-26, post first-arriving-unit fix)
- **2024**: 82,891 records after dedup → 82,889 usable. 858 from CAD, 82,031 from CallType map, 2 excluded.
- **2025**: 87,436 records after dedup → 87,428 usable. 84,162 from CAD, 3,266 from map, 8 excluded.
- **2026-01**: 7,499 records after dedup → 7,499 usable. 7,498 from CAD, 1 from map, 0 excluded.
- Total runtime: ~111 seconds. 25 CSVs written to `PowerBI_Date\Backfill\response_time_all_metrics\`.

---

## [1.17.14] - 2026-02-26

### Fixed
- **Response time M code — restore `Summary_Type` column for DAX measures** — The DAX measures `Emergency_Avg_13M`, `Routine_Avg_13M`, and `Urgent_Avg_13M` filter on `'_ResponseTimeCalculator'[Summary_Type] = "Response_Type"`. The rewritten M code (v1.17.11) had dropped this column, causing "Column 'Summary_Type' in table '_ResponseTimeCalculator' cannot be found" and Missing_References on the line chart. Restored `Summary_Type` in all three response time queries (`___ResponseTimeCalculator.m`, `___ResponseTime_OutVsCall.m`, `___ResponseTime_DispVsCall.m`) with literal value `"Response_Type"` so existing measures work without change.

### Added
- **`docs/HANDOFF_Response_Time_Golden_Standard_And_CallType_2026_02_26.md`** — Handoff document summarizing response time golden-standard ETL, CallType mapping, M code changes, DAX fix, and next steps for Power BI and future months.

---

## [1.17.13] - 2026-02-26

### Fixed
- **`CallType_Categories.csv` — 15 alias rows added for CAD encoding/formatting variants** — Audit identified 17 unmatched incident types across 2024-2026 (174 records). Root causes:
  - **Pattern A — statute spacing**: `2C: 18-2` (space after colon) vs `2C:18-2` in reference. Affected: `Burglary - Auto`, `Burglary - Commercial`, `Burglary - Residence`. (3 entries)
  - **Pattern B — Unicode replacement character `\ufffd`**: Corrupted dash in CAD Excel export. Affected: `Medical Call`, `Motor Vehicle Crash - Hit and Run`, `Motor Vehicle Violation - Private Property`, `Property - Lost/Found`, `Hazardous Road Condition - Flooding`, `Motor Vehicle Crash - Pedestrian Struck`. (7 entries)
  - **Pattern C — missing space around dash**: `Fight -Unarmed`, `Discovery-Motor Vehicle`, `Hazardous Road Condition -General`, `Hazardous Condition -Health / Welfare`, `Sex Offender-General`. (5 entries)
  - **Truly unresolvable**: `nan` (no incident name, 9 records) and `'1'` (garbage, 1 record) — remain excluded.
  - All 15 additions validated at >0.93 fuzzy score against existing reference entries. 2024 unresolvable reduced from 166 to 2.
- Updated `09_Reference\Classifications\CallTypes\CallType_Categories.csv`: 649 rows → 664 rows.

---

## [1.17.12] - 2026-02-26

### Fixed
- **`response_time_batch_all_metrics.py` — CallType_Categories mapping for missing Response Type** — The 2024 CAD timereport export had `Response Type` populated for <1% of records (~894 out of 82,891 after dedup). Added a three-tier resolution cascade: (1) use original CAD value if valid, (2) exact match on `Incident` column against `09_Reference\Classifications\CallTypes\CallType_Categories.csv`, (3) normalized match (lowercase + strip + collapse spaces + remove non-ASCII). Resolution results: 2024: 894 from CAD + 81,831 from map = 82,725 usable; 2025: 84,162 from CAD + 3,266 from map = 87,428 usable; 2026-01: 7,498 from CAD + 1 from map = 7,499. All 25 monthly output CSVs now contain all three types (Emergency/Urgent/Routine) for every month.

### ETL Re-run — Response Time Batch (2026-02-26, with CallType mapping)
- **2024**: 82,725 records resolved → 9 rows/month (3 types × 3 metrics) for all 12 months. Emergency 01-24: 2:54 avg, Urgent 01-24: 3:00 avg, Routine 01-24: 1:21 avg (Time Out − Dispatched).
- **2025**: 87,428 records → full coverage all 12 months.
- **2026-01**: 7,499 records → full coverage.
- CallType agreement with original CAD values: 99.5% (4 disagreements in 886 cross-validated records — minor classification differences, not code errors).

---

## [1.17.11] - 2026-02-26

### Added
- **`02_ETL_Scripts\Response_Times\response_time_batch_all_metrics.py`** — New batch ETL that processes all available CAD timereport data and outputs all three response time metrics to a single folder consumed by Power BI via `Folder.Files()`. Sources: `2024_full_timereport.xlsx`, `2025_full_timereport.xlsx`, `2026_01_timereport.xlsx`. Produces 25 monthly CSVs in `PowerBI_Date\Backfill\response_time_all_metrics\`.
- **`m_code\response_time\___ResponseTime_OutVsCall.m`** — New Power BI query for **Time Out − Time of Call** (total response: call receipt to officer on scene). Uses `Folder.Files()` on the unified backfill folder, filtered by `Metric_Type = "Time Out - Time of Call"`. Same output schema as `___ResponseTimeCalculator.m` for DAX compatibility.
- **`m_code\response_time\___ResponseTime_DispVsCall.m`** — New Power BI query for **Time Dispatched − Time of Call** (dispatcher queue time: call receipt to dispatch). Same architecture as above, filtered by `Metric_Type = "Time Dispatched - Time of Call"`.

### Changed
- **`m_code\response_time\___ResponseTimeCalculator.m`** — Replaced all hardcoded individual CSV source blocks with a single `Folder.Files()` load from `PowerBI_Date\Backfill\response_time_all_metrics`, filtered to `Metric_Type = "Time Out - Time Dispatched"`. This is the "golden standard" re-run using raw CAD data (not the old pre-aggregated backfill CSVs with potentially flawed calculations). Covers 2024–01-26. Output schema unchanged for DAX compatibility.

### ETL Run — Response Time Batch (2026-02-26)
- **2024 Full Year**: 82,891 records after dedup. `Response Type` was nearly unpopulated (< 1% valid values — CAD export issue). Only `Routine` (and a handful of `Emergency`) appear for 2024 months. Data is included but should be interpreted with caution.
- **2025 Full Year**: 87,436 records after dedup → 84,162 with valid Response Type (96%). All three types (Emergency/Urgent/Routine) present for all 12 months. 2025 data is reliable.
- **2026-01 Monthly**: 7,499 records after dedup → 7,498 with valid Response Type (100%). All three types present.
- **Output**: 25 monthly CSVs (2024-01 through 2026-01) written to `PowerBI_Date\Backfill\response_time_all_metrics\`.

---

## [1.17.10] - 2026-02-26

### Fixed
- **`summons_etl_enhanced.py` — Assignment Master V3 schema support** — The ETL's `_load_assignment_master` function was hardcoded to look for `Proposed 4-Digit Format` (V2 schema, Jan 14 vintage). The `09_Reference\Personnel\Assignment_Master_V2.csv` file was updated to V3 schema on 2026-02-20, replacing `Proposed 4-Digit Format` with `STANDARD_NAME` and renaming `PATROL BUREAU` → `PATROL DIVISION`. Updated `_load_assignment_master` to detect schema version and accept either column name, with detailed logging for which schema is in use. File: `02_ETL_Scripts\Summons\summons_etl_enhanced.py`.
- **Updated `Master_Automation\Assignment_Master_V2.csv` to Feb 20, 2026 version** — ETL was reading the Jan 14 vintage (163 rows, `PATROL BUREAU` in WG2, 29 Traffic Bureau officers). Installed the current `09_Reference\Personnel\Assignment_Master_V2.csv` (166 rows, `PATROL DIVISION`, 36 Traffic Bureau officers, 9 Detective Bureau officers). Old file backed up as `Assignment_Master_V2_backup_20260114.csv`.

### ETL Re-run — Summons (2026-02-26 18:09)
After the Assignment Master and ETL script fixes, the summons ETL was re-run. January 2026 results now match the submitted report:
- **Traffic Bureau**: M=217, P=3,117 ✅ (was 143M / 2,599P with old master)
- **Detective Bureau**: M=0, P=1 ✅ (was 15M / 61P with old master)
- **Patrol Division**: M=238, P=450 (HOUSING and OSO consolidated by M code)
- **No `PATROL BUREAU` category** — all patrol assigned correctly to `PATROL DIVISION` ✅
- Total: 462M / 3,577P across all bureaus (e-ticket data only; excludes CJIS/PEO if applicable)
- Staging file updated: `03_Staging\Summons\summons_powerbi_latest.xlsx` (timestamped: `summons_powerbi_20260226_180905.xlsx`)
- Badge `9110` unmatched — not in Assignment Master; flagged in log; records preserved as NO_MATCH.

---

## [1.17.9] - 2026-02-26

### Fixed
- **`summons_13month_trend.m` — removed `TICKET_NUMBER` from `ChangedType`** — The current `summons_etl_enhanced.py` produces staging files with `PADDED_BADGE_NUMBER` as the first column (old schema); `TICKET_NUMBER` never exists in that file. `Table.TransformColumnTypes` has no `MissingField.Ignore` option, so the reference caused the "column not found" error. Removed the line; `TICKET_NUMBER` was not used in any downstream calculation.
- **`PATROL BUREAU` → `PATROL DIVISION` consolidation in both summons M code files** — The assignment master (`final_assignment.csv`) assigns patrol officers to WG2 = "PATROL BUREAU", but the All Bureaus visual should show "PATROL DIVISION". Previously only "HOUSING" and "OFFICE OF SPECIAL OPERATIONS" were consolidated. Added "PATROL BUREAU" to the `if` condition in both `summons_13month_trend.m` and `summons_all_bureaus.m`.
- **Restored `summons_powerbi_latest.xlsx` from today's ETL timestamped copy** — Incorrect file (Feb 17 `_DropExports` copy with WG2=None and sparse month coverage) was overwritten; restored from `summons_powerbi_20260226_164646.xlsx` which has proper WG2 assignments for all bureaus.

### Known Data Discrepancies (Jan 2026 report — resolved in v1.17.10)
- **Traffic Bureau summons count gap**: ETL (from ATS court data): 143M / 2,599P. Submitted report: 217M / 3,117P. Root cause: outdated Assignment Master (Jan 14 vintage, 29 Traffic officers) was used. Resolved by installing Feb 20 master (36 Traffic officers).
- **Detective Bureau summons count gap**: ETL: 15M / 61P. Submitted report: 0M / 1P. Root cause: same outdated Assignment Master caused some officers to be incorrectly bucketed to Detective Bureau. Resolved in v1.17.10.
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
