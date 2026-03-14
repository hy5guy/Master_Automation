# Claude MCP Prompt: February 2026 Monthly Report Fixes

**Copy-paste this into a Claude conversation with Power BI MCP enabled.**  
Ensure Power BI Desktop has the February 2026 Monthly Report open (e.g. `2026_02_Monthly_Report.pbix`).

---

## Context

Supervisor reviewed the February 2026 monthly report and flagged several issues. You are connected to the .pbix via MCP. Use `user-powerbi-modeling-mcp` tools to inspect and fix what you can. Some items require manual edits outside MCP scope.

---

## Prerequisites

1. **Connect** to Power BI Desktop using `connection_operations` with operation `Connect`, or use the ConnectToPowerBIDesktop prompt with the file name (e.g. `2026_02_Monthly_Report.pbix`).
2. Ensure `pReportMonth` parameter is set to `#date(2026, 2, 1)` for the February report.

---

## Task 1: Page 8 — Department-Wide Summons | Moving and Parking

### Issues
- Chart does not include February 2026 (02-26)
- Numbers for 12-25 and 01-26 do not match January's report

### January Report Reference (source of truth)
| Month | M (Moving) | P (Parking) | Total |
|-------|------------|-------------|-------|
| 12-25 | 436 | 2,874 | 3,310 |
| 01-26 | 241 | 3,368 | 3,609 |

### MCP Actions

1. **List** the `summons_13month_trend` table and its partition(s) using `partition_operations` (operation `List`, filter by tableName) or `table_operations` (operation `Get`).

2. **Get** the partition expression for `summons_13month_trend` to verify:
   - Source: `03_Staging\Summons\summons_slim_for_powerbi.csv`
   - Window: `EndDate = DateTime.Date(pReportMonth)`, `StartDate = Date.AddMonths(EndDate, -12)`
   - Filter: `YearMonthKey >= StartYM and YearMonthKey <= EndYM` (for pReportMonth=02/2026 that is 202502–202602)

3. **Run a DAX query** (if available) to check what data exists:
   - Distinct `YearMonthKey` values in `summons_13month_trend`
   - Sum of TICKET_COUNT by Month_Year and TYPE for 12-25, 01-26, 02-26

4. **Diagnosis**:
   - If 02-26 is missing from the model → the staging CSV lacks February data. **User must run Summons ETL** (`python run_summons_etl.py --month 2026_02`) and refresh.
   - If 12-25/01-26 values differ from the table above → staging was refreshed with different data. **User must reconcile backfill** and re-run ETL.
   - If the M code window logic is wrong (e.g. off-by-one month) → **Update** the partition expression and **Refresh** the table.

5. **Refresh** the `summons_13month_trend` table after any partition update.

---

## Task 2: Page 11 — DFR Slide NOTE Box

### Request
Add a NOTE box with:
> "In February 20 Fire Zone summonses were issued utilizing the drone at 500 South River Street"

### MCP Limitation
**The Power BI MCP operates on the semantic model (tables, partitions, measures), not on report visuals.** Adding text boxes or shapes must be done manually in Power BI Desktop.

### Manual Steps for User
1. Go to Page 11 (DFR / Drone page)
2. Insert → Text box
3. Type the note text above
4. Style as a NOTE box (light background, border)
5. Save

---

## Task 3: Page 12 — Traffic Bureau Parking Fees Total

### Issue
Tina entered $115,293.90 for Parking Fees Collected (February 2026) in the last box before the total, but the total did not update.

### MCP Actions (Power BI Side)

1. **Get** the `___Traffic` table partition expression using `partition_operations` or `table_operations`.

2. **Check** the M code: it loads from `Traffic_Monthly.xlsx` table `_mom_traffic`. The current code types all month columns as `Int64.Type`:
   ```powerquery
   List.Transform(TrafficMonthCols, each {_, Int64.Type})
   ```
   Parking Fees can have decimals. If this causes truncation (115293 instead of 115293.90), update to use `type number` for month columns:
   ```powerquery
   List.Transform(TrafficMonthCols, each {_, type number})
   ```

3. **Update** the partition if needed and **Refresh** the `___Traffic` table.

### MCP Limitation
**The "total did not update" issue is likely in the Excel source** (`Shared Folder\Compstat\Contributions\Traffic\Traffic_Monthly.xlsx`). The `_mom_traffic` table's Total/Grand Total formula may not include the 02-26 column or the Parking Fees row. MCP cannot edit Excel. **User must** open the workbook and fix the formula.

---

## Task 4: Page 20 — REMU

Already updated by the user. No MCP action needed.

---

## Summary: What MCP Can vs Cannot Do

| Item | MCP Can Do | MCP Cannot Do |
|------|------------|---------------|
| Page 8 Summons | Inspect partition, run DAX, update M code, refresh | Fix missing data (run ETL) |
| Page 11 DFR NOTE | — | Add report visuals (manual only) |
| Page 12 Traffic | Update ___Traffic M code for decimal support, refresh | Fix Excel formula in Traffic_Monthly.xlsx |
| Page 20 REMU | — | Already done |

---

## Suggested MCP Workflow

1. **Connect** to Power BI Desktop.
2. **List** tables: `summons_13month_trend`, `___Traffic`.
3. **Get** partition expressions for both; verify logic and data types.
4. **Run DAX** (if tool available) to validate summons 12-25, 01-26, 02-26.
5. **Update** `___Traffic` partition to use `type number` for month columns if Parking Fees decimals are truncated.
6. **Refresh** affected tables.
7. **Report back** what was changed and what the user must do manually (ETL, Excel formula, DFR text box).

---

## Reference Paths

- Summons staging: `C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_slim_for_powerbi.csv`
- Traffic source: `C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Traffic\Traffic_Monthly.xlsx`
- Full action plan: `docs/FEBRUARY_2026_MONTHLY_REPORT_SUPERVISOR_FEEDBACK.md`
