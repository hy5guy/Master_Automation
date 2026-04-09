# PLAN MODE — March 2026 CompStat Power BI Diagnostic & Fix

## Context

After running the March 2026 ETL cycle, multiple Power BI visuals are missing data or erroring. Preflight validation did not catch the CSB gap. This plan covers 8 issues (A through F) across preflight scripts, M code queries, DAX, ETL Python, and Excel workbooks.

---

## Diagnostic Summary Table

| Issue | Most Likely Failure Point | Checks to Run | Tool | Evidence That Confirms | Priority |
|-------|--------------------------|---------------|------|----------------------|----------|
| **A) Preflight — CSB** | No CSB check exists in `Pre_Flight_Validation.py` at all | Read lines 192-306 of `Pre_Flight_Validation.py` — no CSB reference | Manual / code read | Confirmed: zero CSB checks in script | **HIGH** |
| **B) Training Cost window** | `___Cost_of_Training.m` line 30: `EndMonth = CurrentMonth - 1` excludes report month; if pReportMonth = `#date(2026,3,1)`, window ends at 02-26, not 03-26 | 1) Check pReportMonth value in .pbix; 2) Check if `Delivery_Cost_By_Month` sheet has a `03-26` column | PBI MCP + Claude in Excel | Window ends 02-26; 03-26 column missing from output or excluded by window math | **HIGH** |
| **C) ResponseTime path** | **Line 20 typo: `PowerBI_Date` instead of `PowerBI_Data`** — folder doesn't exist | 1) Verify path in live .pbix query; 2) Check if `response_time_all_metrics/` has `*03-26*` CSV | PBI MCP + filesystem check | Folder.Files errors or returns 0 rows; also EndDate = month before pReportMonth excludes 03-26 | **CRITICAL** |
| **D) Combined Outreach empty** | No 13-month window in M code (loads all data) — likely no March output file, OR Office field mismatch, OR stale relationship | 1) Check output folder for latest file date; 2) Check Office values vs visual filter; 3) Check relationship status | PBI MCP + filesystem | Latest file predates March, or Office values don't match expected dimension | **HIGH** |
| **E1) DFR date parse error** | `Table.TransformColumnTypes` at line 79 fails on non-date text in Date column — no try/otherwise wrapper | Open DFR workbook, check Date column for text, blanks, or non-US formats | Claude in Excel | Cells with text dates, "NULL", blanks, or DD/MM/YYYY format found | **HIGH** |
| **E2) DFR workbook filter** | Summons ID column has blank/space-only values or corrupted table range; phantom filter hides all rows | Check table range, Summons ID blanks, hidden filters | Claude in Excel | Table range doesn't cover all rows, or AutoFilter criteria on Summons ID | **MEDIUM** |
| **E3) SSOCC summons missing** | `split_dfr_records()` routes DFR officer summons out of main pipeline; non-DFR SSOCC officers may have WG2=UNKNOWN in Assignment Master | 1) Check Assignment_Master for SSOCC WG2 entries; 2) Check slim CSV for SSOCC rows | grep + CSV inspection | Officers with SSOCC assignment have WG2 blank/UNKNOWN, get filtered at line 18 of `summons_all_bureaus.m` | **MEDIUM** |
| **F) CSB workbook audit** | MoM sheet missing `03-26` column header (data not entered by contributor, or column label mismatch) | Open `csb_monthly.xlsm`, inspect MoM sheet column headers | Claude in Excel | No `03-26` column on MoM sheet, or column exists but uses different format | **HIGH** |

---

## Key Findings from Code Exploration

### Critical: ResponseTime Path Typo (Issue C)
`___ResponseTime_AllMetrics.m` line 20:
```
"C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\response_time_all_metrics"
```
Should be `PowerBI_Data` — this is the **documented typo** from CLAUDE.md. If this typo is in the live .pbix, the query fails silently (Folder.Files returns nothing) or throws an error.

### Critical: Window Logic Inconsistency (Issues B, C)
Three queries use "previous complete month" pattern (excluding pReportMonth):
- `___CSB_Monthly.m` line 29: `EndMonth = Date.AddMonths(CurrentMonthStart, -1)`
- `___Cost_of_Training.m` line 30: `EndMonth = CurrentMonth - 1`
- `___ResponseTime_AllMetrics.m` line 15: `EndDate = Date.AddMonths(pReportMonth, -1)`

But the **project standard** documented in CLAUDE.md is:
```
EndOfWindow   = Date.EndOfMonth(pReportMonth)
StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12))
```

This means: if pReportMonth = `#date(2026,3,1)`, these queries show **02-25 through 02-26** (13 months ending Feb). To show 03-26 data, pReportMonth must be set to `#date(2026,4,1)` — OR the M code must be aligned to the project standard.

### No CSB Preflight Check (Issue A)
`Pre_Flight_Validation.py` checks: Personnel, ETL config, E-Ticket, Response Time CAD, Drop Folder, Visual Export Mapping, Arrests, Overtime, TimeOff, Community Engagement config. **CSB is completely absent.**

### DFR Summons Date Coercion (Issue E1)
Line 79 uses bulk `Table.TransformColumnTypes` with `"en-US"` locale. If ANY cell in the Date column contains non-parseable text (e.g., formula errors, "NULL", DD-MM-YYYY), the entire query errors with `DataFormat.Error`.

### SSOCC Summons Routing (Issue E3)
`split_dfr_records()` removes badges 738, 2025, 377 from main pipeline. Other SSOCC officers NOT in `DFR_ASSIGNMENTS` stay in main pipeline BUT their WG2 classification depends on Assignment Master. If WG2 = "UNKNOWN" or blank, line 18 of `summons_all_bureaus.m` filters them out.

---

## Prioritized Execution Order

1. **C) ResponseTime path typo** — CRITICAL, likely blocking the entire visual. Fix path in live .pbix via PBI MCP. Also address window logic.
2. **F) CSB workbook audit** — HIGH, determines whether Issue A fix is the only gap or if data entry is also needed. Use Claude in Excel.
3. **A) Preflight CSB check** — HIGH, add to `Pre_Flight_Validation.py` so this never recurs.
4. **B) Training Cost window** — HIGH, align to project standard or confirm pReportMonth setting.
5. **E1) DFR date parse** — HIGH, add defensive date parsing to M code.
6. **D) Combined Outreach** — HIGH, diagnose empty visual (file freshness + Office field + relationships).
7. **E2) DFR workbook repair** — MEDIUM, Claude in Excel table/filter repair.
8. **E3) SSOCC summons** — MEDIUM, check Assignment Master WG2 for SSOCC officers.

---

## High-Confidence Fixes

1. **C — Path fix**: Change `PowerBI_Date` to `PowerBI_Data` on line 20 of `___ResponseTime_AllMetrics.m` (and in live .pbix via PBI MCP)
2. **A — Add CSB preflight**: New `check_csb()` function in `Pre_Flight_Validation.py` that opens `csb_monthly.xlsm`, reads MoM sheet, checks for report-month column header
3. **E1 — Defensive date parse**: Replace bulk `Table.TransformColumnTypes` Date coercion with per-row `try Date.From(...) otherwise null` + filter nulls

## Open Verification Points (Must Check Before Implementing)

1. **What is pReportMonth set to in the live .pbix?** If `#date(2026,3,1)`, then all "previous month" queries correctly show up to 02-26. If the user expects 03-26 in the window, pReportMonth should be `#date(2026,4,1)` — or the M code window logic must change to include the report month.
2. **Does the CSB MoM sheet have a `03-26` column?** If not, the contributor hasn't entered data yet — no code fix needed, just data entry.
3. **Is the `PowerBI_Date` typo in the live .pbix or only in the on-disk .m file?** Must check via PBI MCP.
4. **What is the latest Community Engagement output file?** Check `02_ETL_Scripts/Community_Engagement/output/` for a file with March 2026 data.
5. **Which SSOCC officer(s) are missing from the summons visual?** Need name/badge to check Assignment Master WG2.

---

# IMPLEMENTATION MODE

## Checklist

| Issue | Root Cause | Confirm | Fix | Validate |
|-------|-----------|---------|-----|----------|
| A | No CSB check in preflight | Read `Pre_Flight_Validation.py` — confirmed zero CSB refs | Add `check_csb()` with openpyxl to read MoM sheet headers | Run `python Pre_Flight_Validation.py --report-month 2026-03` and verify CSB FAIL |
| B | Window ends month before pReportMonth; `Delivery_Cost_By_Month` may lack 03-26 column | Check pReportMonth value; check ETL output sheet | Align M code to project standard OR update pReportMonth to April | Refresh query, confirm 03-25 through 03-26 visible |
| C | Path typo `PowerBI_Date` + window excludes report month | Check path in live .pbix; list CSV files on disk | Fix path to `PowerBI_Data`; align window to project standard | Refresh, confirm 03-26 row appears |
| D | No March data in ETL output OR Office field mismatch | Check latest output file; check Office values | Re-run CE ETL if needed; fix Office mapping if mismatched | Refresh, confirm Bureau breakdown populated |
| E1 | Bulk type coercion fails on bad Date values | Open DFR workbook, inspect Date column | Add `try/otherwise null` date parsing per row | Refresh DFR_Summons query, no error |
| E2 | Corrupted table range or phantom filter on Summons ID | Claude in Excel: inspect table range, filters, blanks | Clear filters, extend table range, TRIM/CLEAN Summons ID | Filter on Summons ID works, all rows visible |
| E3 | SSOCC officer WG2 missing/UNKNOWN in Assignment Master | Check Assignment_Master for badge; check slim CSV | Add/fix WG2 entry in Assignment Master; re-run summons ETL | SSOCC rows appear in `summons_all_bureaus` visual |
| F | MoM sheet lacks 03-26 column (contributor hasn't entered) | Claude in Excel: list column headers on MoM sheet | If MISSING: provide template row. If FORMAT: fix label. If STRUCTURAL: repair table | 03-26 column visible, CSB query loads 13 months |

---

## A) Preflight — CSB Missing Month Detection

### Root Cause
`Pre_Flight_Validation.py` has no CSB check. The script validates 10 other sources but CSB was never added.

### How to Confirm
Already confirmed — lines 192-306 contain checks for E-Ticket, CAD timereport, Drop Folder, Arrests, Overtime, TimeOff, CE config. Zero references to CSB or `csb_monthly`.

### Exact Fix
Add a `check_csb()` function after `check_visual_export_mapping()`. The function:
1. Checks `csb_monthly.xlsm` exists and is > 1KB
2. Opens with openpyxl (read-only), reads `MoM` sheet
3. Scans row 1 (headers) for a column matching the report month in `MM-YY` format
4. If found, checks that at least one data cell below it is non-empty and non-zero
5. Returns FAIL with actionable message if any check fails

**File**: `scripts/Pre_Flight_Validation.py`

```python
def check_csb(root: Path, year: int, month: int) -> dict:
    """Validate CSB monthly workbook has data for the report month."""
    mm_yy = f"{month:02d}-{str(year)[-2:]}"
    csb_path = root / "Shared Folder" / "Compstat" / "Contributions" / "CSB" / "csb_monthly.xlsm"
    result = {"name": "CSB Monthly Data", "status": "PASS", "path": str(csb_path), "detail": ""}

    if not csb_path.is_file():
        result["status"] = "FAIL"
        result["detail"] = "MISSING"
        return result

    if csb_path.stat().st_size < MIN_EXCEL_BYTES:
        result["status"] = "FAIL"
        result["detail"] = f"File too small ({csb_path.stat().st_size} bytes)"
        return result

    try:
        import openpyxl
        wb = openpyxl.load_workbook(str(csb_path), read_only=True, data_only=True)
        if "MoM" not in wb.sheetnames:
            result["status"] = "FAIL"
            result["detail"] = "MoM worksheet not found"
            wb.close()
            return result

        ws = wb["MoM"]
        headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
        wb.close()

        # CSB M code expects MM-YY column headers (e.g., "03-26")
        # Also check previous month (what the 13-month window actually needs)
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        prev_mm_yy = f"{prev_month:02d}-{str(prev_year)[-2:]}"

        header_strs = [str(h).strip() if h is not None else "" for h in headers]

        if mm_yy not in header_strs and prev_mm_yy not in header_strs:
            result["status"] = "FAIL"
            result["detail"] = (
                f"PREFLIGHT FAIL - CSB: No column for {mm_yy} or {prev_mm_yy} "
                f"in csb_monthly.xlsm MoM sheet. "
                f"Contact CSB contributor before running ETL."
            )
            return result

        target = mm_yy if mm_yy in header_strs else prev_mm_yy
        result["detail"] = f"Column '{target}' found in MoM headers"

    except ImportError:
        result["status"] = "WARN"
        result["detail"] = "openpyxl not installed - cannot validate CSB content"
    except Exception as exc:
        result["status"] = "WARN"
        result["detail"] = f"Could not read workbook: {exc}"

    return result
```

Add call in `validate_system()` after the CE config check (~line 306):
```python
results.append(check_csb(root, year, month))
```

### Validation
```bash
python scripts/Pre_Flight_Validation.py --report-month 2026-03
```
Expected: `[FAIL] CSB Monthly Data — PREFLIGHT FAIL - CSB: No column for 03-26...` (if data truly missing) or `[PASS]` (if column exists).

---

## B) Policy & Training — Training Cost by Delivery Method

### Root Cause
`___Cost_of_Training.m` lines 28-35 compute a "previous complete month" window:
```
CurrentMonth = Date.Month(Today)       // 3 (March)
EndMonth = CurrentMonth - 1            // 2 (February)
EndYear = CurrentYear                  // 2026
StartMonth = EndMonth                  // 2 (February)
StartYear = EndYear - 1               // 2025
Report_Start_Date = #date(2025, 2, 1)
Report_End_Date = #date(2026, 2, 1)
```
So with pReportMonth = `#date(2026,3,1)`, the window is **02-25 through 02-26** — 03-26 is excluded.

This conflicts with the project standard (`EndOfMonth(pReportMonth)`). Two possible fixes depending on intent:

**Option 1 (Align to project standard)**: Change M code to include pReportMonth in the window. Window becomes 03-25 through 03-26.

**Option 2 (Keep "previous month" pattern)**: Set pReportMonth = `#date(2026,4,1)` to show March data. This is the pattern CSB and ResponseTime also use.

### How to Confirm
1. **PBI MCP**: Check current pReportMonth value in the live .pbix
2. **Claude in Excel**: Open `policy_training_outputs.xlsx`, sheet `Delivery_Cost_By_Month`, check if a `03-26` column header exists
3. **Decision**: Does user want the window to INCLUDE pReportMonth or exclude it?

### Exact Fix — Option 1 (Recommended: Align to Project Standard)
Replace lines 26-46 of `___Cost_of_Training.m`:

```m
// Rolling 13-month window: start = 12 months before pReportMonth, end = pReportMonth
Today = DateTime.From(ReportMonth),
CurrentYear = Date.Year(Today),
CurrentMonth = Date.Month(Today),
Report_End_Date = Date.StartOfMonth(Today),
Report_Start_Date = Date.AddMonths(Report_End_Date, -12),
MonthList = List.Generate(() => Report_Start_Date, each _ <= Report_End_Date, each Date.AddMonths(_, 1)),
PeriodLabelsMMYY = List.Transform(MonthList, each Text.PadStart(Text.From(Date.Month(_)), 2, "0") & "-" & Text.End(Text.From(Date.Year(_)), 2)),

// Calendar YTD through report month
YTDStart = #date(CurrentYear, 1, 1),
YTDEnd = Date.StartOfMonth(Today),
YTDMonthList = List.Generate(() => YTDStart, each _ <= YTDEnd, each Date.AddMonths(_, 1)),
YTDLabels = List.Transform(
    YTDMonthList,
    each Text.PadStart(Text.From(Date.Month(_)), 2, "0") & "-" & Text.End(Text.From(Date.Year(_)), 2)),
AllPeriodLabels = List.Distinct(List.Combine({PeriodLabelsMMYY, YTDLabels})),
```

This gives window **03-25 through 03-26** when pReportMonth = `#date(2026,3,1)`.

### Validation
After applying in PBI MCP: refresh `___Cost_of_Training` query, check that Period column contains `03-25` through `03-26` (13 values).

---

## C) ResponseTime_AllMetrics

### Root Cause — Two Issues
1. **Path typo** (line 20): `PowerBI_Date` should be `PowerBI_Data`
2. **Window logic** (line 15): `EndDate = Date.AddMonths(pReportMonth, -1)` excludes 03-26

### How to Confirm
1. **PBI MCP**: Read the `___ResponseTime_AllMetrics` query source in the live .pbix — check if path says `PowerBI_Date` or `PowerBI_Data`
2. **Filesystem**: `ls "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\response_time_all_metrics\"` — look for `*03-26*` or `*2026_03*` CSV files
3. If path is correct in live .pbix but wrong in the .m file on disk, the disk copy is stale (informational only)

### Exact Fix
**Line 20** — fix path:
```m
AllFiles = Folder.Files("C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\response_time_all_metrics"),
```

**Lines 15-18** — align to project standard (include pReportMonth):
```m
EndDate   = DateTime.Date(pReportMonth),
StartDate = Date.AddMonths(EndDate, -12),
EndYM     = Date.Year(EndDate)   * 100 + Date.Month(EndDate),
StartYM   = Date.Year(StartDate) * 100 + Date.Month(StartDate),
```

Apply via PBI MCP in the live .pbix. Update `m_code/response_time/___ResponseTime_AllMetrics.m` on disk to match.

### Validation
1. Refresh query — should load without error
2. Check data: YearMonth column should include `2026-03`
3. Audit query (add temporarily to PBI as a new blank query):
```m
let
    Source = ___ResponseTime_AllMetrics,
    Months = Table.Distinct(Table.SelectColumns(Source, {"YearMonth"}))
in
    Table.Sort(Months, {{"YearMonth", Order.Ascending}})
```

---

## D) Combined_Outreach_All (Community Engagement)

### Root Cause (Ranked)
1. **Most likely**: ETL output file doesn't contain March 2026 data (ETL not re-run for March)
2. **Possible**: Office field values don't match visual filter/slicer expectations
3. **Less likely**: Relationship to date table broken or inactive

### How to Confirm
1. **Filesystem**: Check `02_ETL_Scripts/Community_Engagement/output/` — what's the newest file? Does it contain March 2026 dates?
2. **PBI MCP**: Check `___Combined_Outreach_All` table — query `DISTINCT [Office]` values; check if any visual has a filter on Office
3. **PBI MCP**: Check relationship status between `___Combined_Outreach_All[Date]` and the auto date table

### Exact Fix
Depends on confirmation:
- **If no March data in output**: Re-run Community Engagement ETL: `python src/main_processor.py` from `02_ETL_Scripts/Community_Engagement/`
- **If Office mismatch**: The M code renames `office` to `Office` (line 105). Check if the visual uses `Office` or a different field name. If a Bureau dimension table exists, ensure Office values match.
- **If relationship issue**: Via PBI MCP, verify the auto date table relationship is active and set to single-direction cross-filter

**DAX YTD measure** (uses pReportMonth, not TODAY()):
```dax
Community YTD Count = 
VAR _ReportMonth = MAX('___DimMonth'[MonthStart])
VAR _YTDStart = DATE(YEAR(_ReportMonth), 1, 1)
VAR _YTDEnd = EOMONTH(_ReportMonth, 0)
RETURN
    CALCULATE(
        COUNTROWS('___Combined_Outreach_All'),
        '___Combined_Outreach_All'[Date] >= _YTDStart,
        '___Combined_Outreach_All'[Date] <= _YTDEnd
    )
```

If no `___DimMonth` table exists, use pReportMonth directly (loaded as a 1-row table or using `SELECTEDVALUE`).

### Validation
After fix: refresh, confirm "Engagement Initiatives by Bureau" shows data; YTD columns show counts (not "---").

---

## E1) DFR Directed Patrol Summons — Date Parse Error

### Root Cause
`DFR_Summons.m` line 79: `Table.TransformColumnTypes(RenamedCols, FilteredTypes, "en-US")` applies bulk type coercion. If ANY cell in the Date column contains unparseable text (e.g., "NULL", formula error, blank string, DD/MM format), the entire query fails with `DataFormat.Error`.

### How to Confirm
**Claude in Excel**: Open `dfr_directed_patrol_enforcement.xlsx`, inspect the Date column in the `DFR Summons Log` sheet (or `DFR_Summons` table). Look for:
- Cells with text instead of date values
- Formula errors (#REF!, #VALUE!, #N/A)
- Dates in DD/MM/YYYY format
- Blank cells or cells with only spaces
- The string "NULL" or "N/A"

### Exact Fix
Replace lines 54-79 with defensive per-column date parsing:

```m
// === SCHEMA-RESILIENT TYPE MAPPING (en-US; Date parsed defensively) ===
ExistingCols = Table.ColumnNames(RenamedCols),

// Apply all non-Date types first
NonDateTypeMap = {
    {"Summons_ID", type text},
    {"Time", type text},
    {"Summons_Number", type text},
    {"Location", type text},
    {"Statute", type text},
    {"Description", type text},
    {"Fine_Amount", type number},
    {"Source_Type", type text},
    {"Violation_Type", type text},
    {"Violation_Category", type text},
    {"DFR_Operator", type text},
    {"Issuing_Officer", type text},
    {"Summons_Status", type text},
    {"DFR_Unit_ID", type text},
    {"Notes", type text},
    {"OCA", type text},
    {"Summons_Recall", type text},
    {"Full_Summons_Number", type text},
    {"Jurisdiction", type text}
},
FilteredNonDateTypes = List.Select(NonDateTypeMap, each List.Contains(ExistingCols, _{0})),
TypedNonDate = Table.TransformColumnTypes(RenamedCols, FilteredNonDateTypes, "en-US"),

// Parse Date column defensively (per-row try/otherwise)
ChangedType = if List.Contains(ExistingCols, "Date") then
    Table.TransformColumns(TypedNonDate, {
        {"Date", each
            if _ = null or _ = "" then null
            else if _ is date then _
            else if _ is datetime then Date.From(_)
            else if _ is number then Date.AddDays(#date(1899, 12, 30), Number.From(_))
            else try Date.FromText(Text.From(_), [Format="M/d/yyyy", Culture="en-US"])
                 otherwise try Date.From(_)
                 otherwise null,
        type date}
    })
else TypedNonDate,
```

Also add a diagnostic query to isolate bad rows (temporary, for debugging):
```m
let
    Source = Excel.Workbook(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Drone\dfr_directed_patrol_enforcement.xlsx"), null, true),
    RawData = try Source{[Item = "DFR_Summons", Kind = "Table"]}[Data] otherwise Table.PromoteHeaders(Source{[Name = "DFR Summons Log", Kind = "Sheet"]}[Data], [PromoteAllScalars = true]),
    WithFlag = Table.AddColumn(RawData, "DateValid", each try (Date.From([Date]) <> null) otherwise false, type logical),
    BadRows = Table.SelectRows(WithFlag, each [DateValid] = false and [Date] <> null)
in
    BadRows
```

### Validation
Refresh DFR_Summons query — no `DataFormat.Error`. Check row count matches expected.

---

## E2) DFR Workbook — Summons ID Filter Issue

### Root Cause (Ranked)
1. Excel formula columns (Summons ID is a formula per `dfr_export.py` line 27-36) returning blanks due to broken references
2. Table range doesn't cover all data rows
3. Phantom AutoFilter criteria on Summons ID column

### How to Confirm
**Claude in Excel** workflow:
1. Open `dfr_directed_patrol_enforcement.xlsx`
2. Check: Is `DFR_Summons` a named Table (ListObject)? What's its range?
3. Check: Does the Summons ID column use formulas? What formula? Any errors?
4. Check: Are there active AutoFilter criteria? On which columns?
5. Check: Any merged cells or hidden rows?

### Exact Fix (Claude in Excel steps)
1. **Clear all filters**: Data > Clear (removes all AutoFilter criteria)
2. **Check table range**: If table ends before last data row, click any cell in the table > Table Design > Resize Table > extend to cover all rows
3. **Inspect Summons ID formulas**: If formulas reference other sheets/cells and return blank, identify the broken reference
4. **Clean Summons ID values**: In a helper column:
   ```excel
   =IF(ISBLANK(A2),"",TRIM(CLEAN(A2)))
   ```
   Then paste-values over the original column if needed
5. **Remove non-printing characters**: `=SUBSTITUTE(CLEAN(TRIM(A2)),CHAR(160),"")` catches non-breaking spaces

### Validation
After repair: filter on Summons ID — records should appear. Count should match expected (~40+ records per user notes).

---

## E3) Missing SSOCC Summons

### Root Cause
Two mechanisms could exclude SSOCC officer summons:

1. **DFR split**: `split_dfr_records()` removes badges 738 (Polson), 2025 (Ramirez in date range), 377 (Mazzaccaro in date range) from main pipeline. These go to DFR workbook ONLY.
2. **WG2 filtering**: `summons_all_bureaus.m` line 18 removes rows where `WG2 = "UNKNOWN"`. If an SSOCC officer's badge isn't in Assignment Master, their WG2 defaults to UNKNOWN and they're filtered out.

### How to Confirm
1. Identify the missing officer(s) by badge number
2. Check `Assignment_Master_GOLD.xlsx` / `Assignment_Master_V2.csv` for that badge — is WG2 populated? What value?
3. Check `summons_slim_for_powerbi.csv` — do rows exist for that officer? What WG2 value?
4. If WG2 = "SSOCC", check whether `summons_all_bureaus.m` consolidation logic (lines 28-33) handles it — currently it only consolidates HOUSING, OSO, PATROL BUREAU. SSOCC would pass through as its own bureau, which is correct.

### Exact Fix
- **If badge missing from Assignment Master**: Add the officer to `Assignment_Master_GOLD.xlsx` with correct WG2 (likely "SSOCC" or the appropriate bureau). Re-run `/sync-personnel` then re-run summons ETL.
- **If WG2 = UNKNOWN**: Update the WG2 value in Assignment Master to the correct bureau.
- **If DFR split is too broad**: Check if the officer should be in `DFR_ASSIGNMENTS`. If their summons are NOT drone-related, remove them from `DFR_ASSIGNMENTS` in `summons_etl_normalize.py` or narrow the date range.

### Validation
After fix: re-run summons ETL, refresh Power BI, check "Summons | Moving & Parking | All Bureaus" — SSOCC row should appear (or the officer's correct bureau should show increased counts).

---

## F) CSB Workbook Investigation

### Root Cause
The CSB M code reads `csb_monthly.xlsm`, sheet `MoM`, and looks for column headers in `MM-YY` format. If there's no `03-26` column (or `02-26` depending on window logic), the data won't appear.

The CSB M code window (line 29): `EndMonth = Date.AddMonths(CurrentMonthStart, -1)` — with pReportMonth = `#date(2026,3,1)`, EndMonth = Feb 2026. So it actually needs column `02-26` as the latest month, not `03-26`.

**However**, if the user expects to see March 2026 data, either:
- pReportMonth should be set to `#date(2026,4,1)`, OR
- The M code window should be aligned to the project standard

### How to Confirm — Claude in Excel Audit
1. Open `csb_monthly.xlsm`
2. Go to `MoM` sheet
3. List all column headers in row 1 (especially the date columns)
4. Check: Is `03-26` present? Is `02-26` present?
5. Check: Are the values under the latest month column non-blank, non-zero?
6. Check: Is the table range (if any) covering all columns through the latest month?
7. Check: Are there merged cells, hidden columns, or phantom filters?

### Exact Fix
**If MISSING (no 03-26 or 02-26 column)**:
Contact CSB contributor. Provide template: add column header `03-26` (or next needed month) to MoM sheet after the last date column. Each row should have a numeric value for that month's tracked item count.

**If FORMAT mismatch** (column exists but uses different format like "Mar-26" or "2026-03"):
Rename the column header to match `MM-YY` format (e.g., `03-26`).

**If STRUCTURAL** (table range doesn't include new column):
Extend the Excel Table range to include the new column.

**If M CODE issue** (data exists, correct format, but excluded by window):
Align `___CSB_Monthly.m` to project standard — replace lines 28-32:
```m
// EndMonth: include the report month (project standard)
EndMonth = Date.StartOfMonth(CurrentMonthStart),
StartMonth = Date.AddMonths(EndMonth, -12),
```

### Prevention
Add Excel Data Validation / Conditional Formatting to MoM sheet:
- In a helper cell, calculate expected next month from the last date column header
- Conditional formatting rule: highlight the header row yellow if the expected month column is missing
- This alerts the contributor visually when data entry is due

### Validation
After fix: refresh `___CSB_Monthly` in Power BI. Run audit query:
```m
let Source = ___CSB_Monthly, Months = Table.Distinct(Table.SelectColumns(Source, {"Month_MM_YY"})) in Table.Sort(Months, {{"Month_MM_YY", Order.Ascending}})
```
Should show 13 consecutive months ending at the expected month.

---

## Cross-Cutting Decision Required

**Window logic alignment**: Issues B, C, and F all share the same question — should the 13-month window INCLUDE pReportMonth or exclude it (showing the previous complete month)?

- **Current behavior** (B, C, F): Window ends at month BEFORE pReportMonth
- **Project standard** (CLAUDE.md): `EndOfMonth(pReportMonth)` — includes pReportMonth
- **DFR_Summons.m**: Already uses `EndOfMonth(ReportMonth)` — includes pReportMonth

**Recommendation**: Align all queries to the project standard (include pReportMonth). This means setting pReportMonth = `#date(2026,3,1)` shows data through 03-26. This is consistent with DFR_Summons.m and the documented standard.

If aligned, the window for pReportMonth = `#date(2026,3,1)` would be:
- Start: `#date(2025,3,1)` (03-25)
- End: `#date(2026,3,31)` (end of 03-26)
- 13 months: 03-25, 04-25, ..., 02-26, 03-26
