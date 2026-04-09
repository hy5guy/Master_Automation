# Hackensack PD CompStat — March 2026 ETL Cycle Handoff
# Date: 2026-04-09 | Analyst: RAC | Receiving: Cursor AI (Sonnet 4.6)

---

## PROJECT CONTEXT

This is the Master Automation project for the Hackensack Police Department
CompStat Power BI report. It is a Python/PowerShell ETL orchestration system
feeding multiple Power BI visuals via a 13-month rolling window.

Base path (all file refs below are relative to this):
  C:\Users\carucci_r\OneDrive - City of Hackensack\

Key conventions — READ BEFORE TOUCHING ANYTHING:
- All rolling windows use pReportMonth (type date, e.g. #date(2026,3,1))
- NEVER use DateTime.LocalNow() or TODAY() for window logic
- Project standard window:
    EndOfWindow   = Date.EndOfMonth(pReportMonth)
    StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12))
- ETL scripts live in 02_ETL_Scripts/ — do NOT write there directly
- Orchestration lives in 06_Workspace_Management/
- config/scripts.json and CHANGELOG.md are protected files
- Badge numbers are strings — preserve leading zeros
- OneDrive paths resolved via scripts/path_config.py at runtime
- Excel workbook edits use zip-level XML surgery (zipfile module)
  NEVER use openpyxl load+save on shared workbooks

---

## WHAT WAS COMPLETED TONIGHT (2026-04-08)

### ETL Cycle — March 2026
- Run command: .\scripts\run_all_etl.ps1 -ReportMonth 2026-03
- Results: 5/7 scripts succeeded
  ✅ Arrests, Community Engagement, Overtime/TimeOff, Response Times, Summons
  ❌ Response Times Fresh Calculator — was dead path (Master_Automation\scripts)
  ❌ Summons Derived Outputs — same dead path issue
- FIXED: Both dead paths corrected in config/scripts.json to
  06_Workspace_Management\scripts\
- 50/55 exports routed to Processed_Exports/ (3 residuals are expected)
- .pbix deployed to:
  Shared Folder\Compstat\Monthly Reports\2026\03_march\
  2026_03_Monthly_Report.pbix

### run_all_etl.ps1 — Save-MonthlyReport function fixes (v1.24.1)
- Fixed $ReportMonth binding (was re-calculating from Get-Date)
- Added canonical config path check before wildcard fallback
- Added idempotent skip if target .pbix already exists
- Added $DryRun gate
- Added $localOD path fallback guard
- scripts/deploy_monthly_template.ps1 marked DEPRECATED

### Documentation
- CHANGELOG.md updated to v1.24.1
- SUMMARY.md, README.md, CLAUDE.md version bumped to v1.24.1

---

## CURRENT STATE — WHAT IS NOT YET DONE

The .pbix has been deployed but NOT fully validated. Power BI has not been
refreshed with March 2026 data yet. Multiple visuals are known to be missing
data or erroring.

pReportMonth in the live .pbix: 03/01/2026 (#date(2026,3,1)) — CONFIRMED OK

---

## OPEN ISSUES — DIAGNOSTIC PLAN IN PROGRESS

Claude Code produced a diagnostic plan (plan mode) that was reviewed and
corrected. The corrected execution order is below. Claude Code was paused
awaiting your confirmation before proceeding.

### Execution Order (corrected)

STEP 0 — Window Convention Decision (DO THIS FIRST)
  Use PBI MCP to read EndDate/EndMonth logic in these three live queries:
    - ___Cost_of_Training
    - ___ResponseTime_AllMetrics
    - ___CSB_Monthly
  Compare against project standard: Date.EndOfMonth(pReportMonth)
  Confirm with RAC which convention to standardize on before changing
  any M code in Issues B, C, or F.

STEP 1 — Issue C: ResponseTime path typo (CRITICAL — safe to fix now)
  File: m_code/response_time/___ResponseTime_AllMetrics.m
  Also fix in live .pbix via PBI MCP.
  TWO bugs:
    Bug 1 — Line 20 path typo:
      WRONG:   PowerBI_Date\response_time_all_metrics
      CORRECT: PowerBI_Data\response_time_all_metrics
    Bug 2 — EndDate excludes report month:
      WRONG:   EndDate = DateTime.Date(pReportMonth)
               (resolves to 2026-03-01, excludes rest of March)
      CORRECT: EndDate = Date.EndOfMonth(DateTime.Date(pReportMonth))

STEP 2 — Issue F: CSB workbook audit (Claude in Excel)
  File: Shared Folder\Compstat\Contributions\CSB\csb_monthly.xlsm
  Open in Claude in Excel. Determine which of these is true:
    MISSING:    No March 2026 data — contributor action required
    FORMAT:     Data exists but wrong column label format
    STRUCTURAL: Table range or merged cells blocking Power Query
    M CODE:     Data exists but window logic excludes it
  Do NOT fix M code until Step 0 window decision is confirmed.

STEP 3 — Issue A: Add CSB preflight check
  File: scripts/Pre_Flight_Validation.py
  Add check_csb() function. Wait for Step 2 result + Step 0 decision
  before implementing — the expected MM-YY label depends on both.
  Required constant (was missing in original plan):
    MIN_EXCEL_BYTES = 1024
  The check must derive the expected month label from pReportMonth
  using the same window logic as the M code — do NOT hardcode both
  03-26 and 02-26.

STEP 4 — Issue B: Training Cost window alignment
  File: m_code/training/___Cost_of_Training.m + live .pbix
  Wait for Step 0 window decision.
  Known bug in original plan M code: // comments are invalid in M.
  Use /* */ block comments only.
  Window currently ends month BEFORE pReportMonth — misses 03-26.

STEP 5 — Issue E1: DFR date parse error
  File: DFR_Summons query in live .pbix
  Source: Shared Folder\Compstat\Contributions\Drone\
          dfr_directed_patrol_enforcement.xlsx
  Error: DataFormat.Error on Date column — bulk TransformColumnTypes
  fails on any unparseable cell.
  Fix: Replace with per-row try/otherwise null date parsing.
  Full corrected M code was produced in the diagnostic plan — reuse it.

STEP 6 — Issue D: Community Engagement empty visuals
  Visuals: "Engagement Initiatives by Bureau" (empty)
           "Engagement Initiatives by Bureau YTD" (all ---)
  Check in order:
    1. Does output file contain March 2026 dates?
       Path: 02_ETL_Scripts/Community_Engagement/output/
    2. Office field values — do they match visual filter expectations?
    3. Relationship status between [Date] and date table in model
  DAX YTD measure must use MAX('___DimMonth'[MonthStart]) not TODAY().

STEP 7 — Issue E2: DFR workbook Summons ID filter
  File: dfr_directed_patrol_enforcement.xlsx
  Problem: Filtering Summons ID hides all records.
  Use Claude in Excel. Check:
    - Formula columns returning blanks
    - Table range not covering all rows
    - Phantom AutoFilter criteria
    - Merged cells / hidden rows

STEP 8 — Issue E3: Missing SSOCC summons
  Visual: "Summons | Moving & Parking | All Bureaus"
  Check: Assignment_Master_V2.csv — find the missing officer(s) badge,
  confirm WG2 value. If WG2 = UNKNOWN or blank, update
  Assignment_Master_GOLD.xlsx, re-run /sync-personnel, re-run
  summons ETL.
  Note: Badges 738 (Polson), 2025 (Ramirez, date-ranged),
  377 (Mazzaccaro, date-ranged) are intentionally routed to DFR
  workbook — do not add them back to main pipeline.

---

## KEY FILE LOCATIONS

| What | Path |
|---|---|
| Orchestrator | 06_Workspace_Management\scripts\run_all_etl.ps1 |
| Config | 06_Workspace_Management\config\scripts.json |
| Preflight | 06_Workspace_Management\scripts\Pre_Flight_Validation.py |
| Personnel (canonical) | 09_Reference\Personnel\Assignment_Master_V2.csv |
| Personnel (source) | 09_Reference\Personnel\Assignment_Master_GOLD.xlsx |
| DFR workbook | Shared Folder\Compstat\Contributions\Drone\dfr_directed_patrol_enforcement.xlsx |
| CSB workbook | Shared Folder\Compstat\Contributions\CSB\csb_monthly.xlsm |
| Deployed .pbix | Shared Folder\Compstat\Monthly Reports\2026\03_march\2026_03_Monthly_Report.pbix |
| Response time CSVs | PowerBI_Data\response_time_all_metrics\ |
| Drop exports | PowerBI_Data\_DropExports\ |
| ETL logs | 06_Workspace_Management\logs\ |
| M code (response time) | m_code\response_time\___ResponseTime_AllMetrics.m |
| M code (training) | m_code\training\___Cost_of_Training.m |
| Changelog | 06_Workspace_Management\CHANGELOG.md (append-only) |

---

## RULES FOR THIS SESSION

1. Do NOT modify config/scripts.json without explicit RAC confirmation
2. Do NOT modify any file in 02_ETL_Scripts/ directly
3. Do NOT use DateTime.LocalNow() or TODAY() anywhere
4. Do NOT use openpyxl load+save on .xlsx/.xlsm files —
   use zipfile XML surgery (see fix-excel.md skill)
5. ALWAYS append to CHANGELOG.md — never edit existing entries
6. Badge numbers are strings — never cast to int
7. All new ETL scripts go in 06_Workspace_Management\scripts\
8. Step 0 (window convention decision) must be confirmed by RAC
   before M code changes to Issues B, C, or F

---

## HOW TO START

Run Step 0 first:
  Use PBI MCP to inspect pReportMonth and the EndDate/EndMonth
  expressions in ___Cost_of_Training, ___ResponseTime_AllMetrics,
  and ___CSB_Monthly in the live .pbix.
  Report findings to RAC and wait for confirmation before proceeding.

Current version: v1.24.1
Report month: 2026-03
pReportMonth in .pbix: #date(2026,3,1) ✅