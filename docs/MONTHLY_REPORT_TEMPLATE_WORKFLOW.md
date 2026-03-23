# Monthly Report Template Workflow

**Created:** 2026-02-21
**Author:** R. A. Carucci
**Template Location:** `...\08_Templates\Monthly_Report_Template.pbix` (some setups use `15_Templates\`; same gold-copy file under the OneDrive root)
**Source:** Copied from `2026_01_Monthly_Report.pbix` (January 2026 report)
**Last MCP Update:** 2026-03-19 — Directory consolidation path corrections + DAX subtitle fixes (see `POWERBI_TEMPLATE_MCP_UPDATE_2026_03_19.md`)
**Last pipeline sync:** 2026-03-23 — Summons slim CSV: `apply_fine_amount_and_violation_category` + extended columns (**`CHANGELOG.md` [1.19.2]**). Training: **`___In_Person_Training.m`** → **`Policy_Training_Monthly.xlsx`** (full log; YTD in DAX); **`___Cost_of_Training.m`** → union of 13-month rolling labels and calendar YTD through **`pReportMonth`**.

---

## Overview

The Monthly Report Template is the gold-copy PBIX file used to generate each month's CompStat report. All M code fixes (pReportMonth parameter, hardcoded path corrections, List.Max bug fixes) must be deployed to this template. Monthly reports are created by opening the template, updating the report month parameter, and saving to the target month folder.

---

## Monthly Cycle Steps

1. **Open the template**
   - `08_Templates\Monthly_Report_Template.pbix`

2. **Update `pReportMonth` parameter**
   - In Power BI Desktop: Home > Transform data > Edit Parameters
   - Set `pReportMonth` to the first day of the report month
   - Example for February 2026: `2/1/2026`
   - This single change drives all rolling windows and previous-month filters

3. **Save As to the target month folder**
   - Path: `Shared Folder\Compstat\Monthly Reports\YYYY\MM_monthname\YYYY_MM_Monthly_Report.pbix`
   - Example: `Monthly Reports\2026\02_february\2026_02_Monthly_Report.pbix`

4. **Run ETL**
   - `.\scripts\run_all_etl.ps1 -ReportMonth YYYY-MM`
   - Verify the manifest in `_DropExports\_manifest.json`

5. **Refresh all queries in Power BI**
   - Close & Apply in Power Query, or Refresh All from the ribbon
   - Verify data windows show the correct 13-month range

6. **Publish / export visuals**
   - Export visual data as needed
   - Run `scripts/process_powerbi_exports.py` for standardized exports

---

## Template Update Rules

- Only update the template when M code changes have been **validated and deployed**
- Never edit a monthly copy and assume changes propagate back to the template
- After updating the template, test by refreshing with the current `pReportMonth` value
- Keep the workspace `m_code/` directory as the source of truth for all query code

---

## M Code Deployment Checklist

When deploying corrected M code into the template, paste each query into Power BI's Advanced Editor. Deploy **parameters first**, then queries in any order.

### Parameters (deploy first)

| Query Name | Source File | Notes |
|------------|------------|-------|
| pReportMonth | `m_code/parameters/pReportMonth.m` | **Deploy first** -- all date-dependent queries reference this |
| EtlRootPath | `m_code/parameters/EtlRootPath.m` | Benchmark ETL root |
| RootExportPath | `m_code/parameters/RootExportPath.m` | Benchmark export root |
| RangeStart | `m_code/parameters/RangeStart.m` | Benchmark date range |
| RangeEnd | `m_code/parameters/RangeEnd.m` | Benchmark date range |
| SourceMode | `m_code/parameters/SourceMode.m` | Excel/Folder toggle |

### Data Queries with pReportMonth (20 queries)

These queries use `ReportMonth = pReportMonth` for date calculations and must be deployed to replace any `DateTime.LocalNow()` patterns in the template.

| Query Name | Source File | Category |
|------------|------------|----------|
| ___Arrest_Categories | `m_code/arrests/___Arrest_Categories.m` | Previous-month filter |
| ___Top_5_Arrests | `m_code/arrests/___Top_5_Arrests.m` | Previous-month filter |
| ___Combined_Outreach_All | `m_code/community/___Combined_Outreach_All.m` | Filename generation |
| ___CSB_Monthly | `m_code/csb/___CSB_Monthly.m` | Rolling window |
| ___Detectives | `m_code/detectives/___Detectives.m` | Rolling window + timestamp |
| ___Det_case_dispositions_clearance | `m_code/detectives/___Det_case_dispositions_clearance.m` | Rolling window |
| ___Drone | `m_code/drone/___Drone.m` | Rolling window |
| ESU_13Month | `m_code/esu/ESU_13Month.m` | Rolling window (includes report month; excludes _Log tables) |
| MonthlyActivity | `m_code/esu/MonthlyActivity.m` | Rolling window |
| ___Overtime_Timeoff_v3 | `m_code/overtime/___Overtime_Timeoff_v3.m` | Rolling window |
| ___DimMonth | `m_code/shared/___DimMonth.m` | Rolling window |
| TAS_Dispatcher_Incident | `m_code/ssocc/TAS_Dispatcher_Incident.m` | Rolling window |
| ___STACP_pt_1_2 | `m_code/stacp/___STACP_pt_1_2.m` | Rolling window |
| ___Social_Media | `m_code/stacp/___Social_Media.m` | Rolling window |
| STACP_DIAGNOSTIC | `m_code/stacp/STACP_DIAGNOSTIC.m` | Rolling window (optional) |
| summons_all_bureaus | `m_code/summons/summons_all_bureaus.m` | Previous-month filter |
| summons_top5_moving | `m_code/summons/summons_top5_moving.m` | Previous-month filter |
| ___Cost_of_Training | `m_code/training/___Cost_of_Training.m` | Rolling 13-month (end = month before `pReportMonth`) **∪** calendar YTD months through report month (for YTD cost DAX) |
| ___Traffic | `m_code/traffic/___Traffic.m` | Rolling window |
| summons_top5_parking | `m_code/summons/summons_top5_parking.m` | Previous-month filter |

### Data Queries without Date Logic (18 queries)

These do not use `DateTime.LocalNow()` but should still be deployed to ensure the template has the latest version.

| Query Name | Source File |
|------------|------------|
| ___Arrest_Distro | `m_code/arrests/___Arrest_Distro.m` |
| ___chief_projects | `m_code/community/___chief_projects.m` |
| ___Benchmark | `m_code/benchmark/___Benchmark.m` |
| ___NIBRS_Monthly_Report | `m_code/nibrs/___NIBRS_Monthly_Report.m` |
| ___Chief2 | `m_code/patrol/___Chief2.m` |
| ___Patrol | `m_code/patrol/___Patrol.m` |
| ___REMU | `m_code/patrol/___REMU.m` |
| ___ResponseTime_AllMetrics | `m_code/response_time/___ResponseTime_AllMetrics.m` |
| ___ComprehensiveDateTable | `m_code/shared/___ComprehensiveDateTable.m` |
| ___DimEventType | `m_code/shared/___DimEventType.m` |
| Parameters_Check | `m_code/shared/Parameters_Check.m` |
| RequiredTypes | `m_code/shared/RequiredTypes.m` |
| ___SSOCC_Data | `m_code/ssocc/___SSOCC_Data.m` |
| TrackedItems | `m_code/esu/TrackedItems.m` |
| summons_13month_trend | `m_code/summons/summons_13month_trend.m` |
| ___Summons_Diagnostic | `m_code/summons/___Summons_Diagnostic.m` |
| ___In_Person_Training | `m_code/training/___In_Person_Training.m` | Source: **`Policy_Training_Monthly.xlsx`** (`Training_Log` / `Training_Log_Clean`); no month slice in M — use DAX YTD on **`Start date`** |

### Helper Functions (5 queries)

| Query Name | Source File |
|------------|------------|
| fnCleanText | `m_code/esu/fnCleanText.m` |
| fnMonthKeyFromTableName | `m_code/esu/fnMonthKeyFromTableName.m` |
| fnApplyRenameMap | `m_code/functions/fnApplyRenameMap.m` |
| fnEnsureColumns | `m_code/functions/fnEnsureColumns.m` |
| fnGetFiles | `m_code/functions/fnGetFiles.m` |
| fnLoadRaw | `m_code/functions/fnLoadRaw.m` |
| fnReadCsv | `m_code/functions/fnReadCsv.m` |

---

## Verification After Deployment

After pasting all queries into the template and refreshing:

1. Confirm `pReportMonth` shows the correct date in Edit Parameters
2. Spot-check 2-3 rolling-window queries (e.g., Overtime, Detectives, STACP) -- verify 13 months of data appear
3. Spot-check 1-2 previous-month queries (e.g., Arrest Categories, summons_all_bureaus) -- verify they show the previous complete month
4. Confirm no `DataSource.NotFound` errors in any query
5. Save the template

---

## Directory Structure

```
08_Templates\
  Monthly_Report_Template.pbix    <-- Gold copy (update M code here)

Shared Folder\Compstat\Monthly Reports\
  2026\
    01_january\
      2026_01_Monthly_Report.pbix <-- January output (do not edit)
    02_february\
      2026_02_Monthly_Report.pbix <-- February output (Save As from template)
```
