# Summons M Code Bugfix -- Claude MCP Execution Prompt

> **Purpose:** Fix 3 confirmed bugs in summons Power Query M code that cause missing data and wrong counts in the dashboard.
>
> **Model:** `2026_02_Monthly_Report` (currently open in Power BI Desktop)
>
> **Parameter:** `pReportMonth = #date(2026, 2, 1)`
>
> **Date:** 2026-03-10

---

## What You Are Fixing

There are **3 bugs** across 4 queries. Apply each update exactly as shown.

| Bug | Affected Query | Symptom | Fix |
|-----|---------------|---------|-----|
| FilteredPreferBackfill uses `[WG2] = "Department-Wide"` which matches NO rows, silently dropping all data for backfill months | `summons_13month_trend` | Months show zero/blank in trend | Replace with `IS_AGGREGATE` check; update BackfillMonths to `{"07-25"}` only |
| `Table.RowCount(_)` counts rows instead of summing TICKET_COUNT | `summons_all_bureaus` | Backfill aggregate months show "1" instead of hundreds | Replace with `List.Sum([TICKET_COUNT])`; add TICKET_COUNT to ChangedType |
| Same `Table.RowCount(_)` bug | `summons_top5_moving`, `summons_top5_parking` | Same undercounting | Same fix |

---

## Pre-Flight

1. Connect to Power BI Desktop:
   ```
   connection_operations -> ListLocalInstances
   connection_operations -> Connect (use the returned connection string)
   ```
2. Verify you're in the right model — list the tables and confirm `summons_13month_trend` exists:
   ```
   table_operations -> List
   ```
3. **IMPORTANT:** The user has already saved the .pbix. Proceed with updates.

---

## MCP Tool Call Format

All 4 queries are **table partitions**:
```
partition_operations -> Update
  definitions: [{ tableName: "<TABLE>", expression: "<FULL M CODE>" }]
```

---

## Query Updates

---

### 1. summons_13month_trend

**What changed:**
- Added `IS_AGGREGATE` (type text) to TypeMap
- Changed `BackfillMonths` from `{"01-25", "02-25"}` to `{"07-25"}` (the only true gap month)
- Replaced `[WG2] = "Department-Wide"` (never matches) with `Text.Upper(Text.From([IS_AGGREGATE] ?? "false")) = "TRUE"` (correctly identifies backfill rows)

**Tool:** `partition_operations` Update | **Table:** `summons_13month_trend`

```m
let
    EndDate = DateTime.Date(pReportMonth),
    StartDate = Date.AddMonths(EndDate, -12),
    EndYM = Date.Year(EndDate) * 100 + Date.Month(EndDate),
    StartYM = Date.Year(StartDate) * 100 + Date.Month(StartDate),

    Source = Csv.Document(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_slim_for_powerbi.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ExistingCols = Table.ColumnNames(PromotedHeaders),
    TypeMap = {
        {"PADDED_BADGE_NUMBER", type text},
        {"OFFICER_DISPLAY_NAME", type text},
        {"OFFICER_NAME_RAW", type text},
        {"ISSUE_DATE", type datetime},
        {"TYPE", type text},
        {"ETL_VERSION", type text},
        {"IS_AGGREGATE", type text},
        {"Year", Int64.Type},
        {"Month", Int64.Type},
        {"YearMonthKey", Int64.Type},
        {"Month_Year", type text},
        {"WG2", type text},
        {"DATA_QUALITY_SCORE", Int64.Type}
    },
    FilteredTypes = List.Select(TypeMap, each List.Contains(ExistingCols, _{0})),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, FilteredTypes),
    FilteredClean = Table.SelectRows(ChangedType, each [WG2] <> null and [WG2] <> "" and [WG2] <> "UNKNOWN"),
    FilteredMonthYear = Table.SelectRows(FilteredClean, each
        [YearMonthKey] <> null and [YearMonthKey] >= StartYM and [YearMonthKey] <= EndYM
    ),
    BackfillMonths = {"07-25"},
    FilteredPreferBackfill = Table.SelectRows(FilteredMonthYear, each
        if List.Contains(BackfillMonths, [Month_Year])
        then Text.Upper(Text.From([IS_AGGREGATE] ?? "false")) = "TRUE"
        else true
    ),
    WithTicketCount = if Table.HasColumns(FilteredPreferBackfill, "TICKET_COUNT")
        then Table.TransformColumnTypes(FilteredPreferBackfill, {{"TICKET_COUNT", Int64.Type}})
        else Table.AddColumn(FilteredPreferBackfill, "TICKET_COUNT", each 1, Int64.Type),
    AddConsolidatedBureau = Table.AddColumn(WithTicketCount, "Bureau_Consolidated", each if [WG2] = "HOUSING" or [WG2] = "OFFICE OF SPECIAL OPERATIONS" or [WG2] = "PATROL BUREAU" then "PATROL DIVISION" else [WG2], type text)
in
    AddConsolidatedBureau
```

---

### 2. summons_all_bureaus

**What changed:**
- Added `{"TICKET_COUNT", Int64.Type}` to ChangedType
- Replaced `each Table.RowCount(_)` with `each List.Sum([TICKET_COUNT])` in GroupedRows

**Tool:** `partition_operations` Update | **Table:** `summons_all_bureaus`

```m
let
    PrevDate = Date.AddMonths(DateTime.Date(pReportMonth), -1),
    PreviousMonthKey = Date.Year(PrevDate) * 100 + Date.Month(PrevDate),

    Source = Csv.Document(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_slim_for_powerbi.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{"YearMonthKey", Int64.Type}, {"TICKET_COUNT", Int64.Type}, {"TYPE", type text}, {"WG2", type text}}),

    FilteredClean = Table.SelectRows(ChangedType, each [WG2] <> "UNKNOWN" and [WG2] <> null and [WG2] <> ""),
    FilteredLatestMonth = Table.SelectRows(FilteredClean, each [YearMonthKey] = PreviousMonthKey),

    GroupedRows = Table.Group(
        FilteredLatestMonth,
        {"WG2", "TYPE"},
        {{"Count", each List.Sum([TICKET_COUNT]), type number}}
    ),

    ConsolidatedBureaus = Table.TransformColumns(
        GroupedRows,
        {"WG2", each if _ = "HOUSING" or _ = "OFFICE OF SPECIAL OPERATIONS" or _ = "PATROL BUREAU"
            then "PATROL DIVISION" else _}
    ),

    RegroupedRows = Table.Group(
        ConsolidatedBureaus,
        {"WG2", "TYPE"},
        {{"Count", each List.Sum([Count]), type number}}
    ),

    PivotedColumn = Table.Pivot(
        RegroupedRows,
        List.Distinct(RegroupedRows[TYPE]),
        "TYPE",
        "Count",
        List.Sum
    ),

    AddM = if Table.HasColumns(PivotedColumn, "M") then PivotedColumn
        else Table.AddColumn(PivotedColumn, "M", each 0, Int64.Type),
    AddP = if Table.HasColumns(AddM, "P") then AddM
        else Table.AddColumn(AddM, "P", each 0, Int64.Type),

    ReplacedValue = Table.ReplaceValue(AddP, null, 0, Replacer.ReplaceValue, {"M", "P"}),

    AddedTotal = Table.AddColumn(
        ReplacedValue,
        "Total",
        each [M] + [P] + (try [C] otherwise 0),
        type number
    ),

    RenamedColumns = Table.RenameColumns(AddedTotal, {{"WG2", "Bureau"}})
in
    RenamedColumns
```

---

### 3. summons_top5_moving

**What changed:**
- Added `{"TICKET_COUNT", Int64.Type}` to ChangedType
- Replaced `each Table.RowCount(_)` with `each List.Sum([TICKET_COUNT])` in GroupedRows

**Tool:** `partition_operations` Update | **Table:** `summons_top5_moving`

```m
let
    Source = Csv.Document(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_slim_for_powerbi.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    
    WithTitle = if Table.HasColumns(PromotedHeaders, "TITLE") then PromotedHeaders else Table.AddColumn(PromotedHeaders, "TITLE", each null, type text),
    
    ChangedType = Table.TransformColumnTypes(WithTitle, {{"YearMonthKey", Int64.Type}, {"TICKET_COUNT", Int64.Type}, {"TYPE", type text}, {"TITLE", type text}}),
    
    FilteredMoving = Table.SelectRows(ChangedType, each ([TYPE] = "M")),
    
    FilteredMovingNoPEO = Table.SelectRows(FilteredMoving, each 
        ( [TITLE] = null or Text.Trim(Text.Upper([TITLE] ?? "")) <> "PEO" ) and
        ( [OFFICER_DISPLAY_NAME] = null or not (Text.StartsWith([OFFICER_DISPLAY_NAME], "PEO ") or Text.StartsWith([OFFICER_DISPLAY_NAME], "PEO,") or Text.StartsWith([OFFICER_DISPLAY_NAME], "PEO.")) )
    ),
    
    LatestKey = List.Max(FilteredMovingNoPEO[YearMonthKey]),
    
    FilteredLatestMonth = Table.SelectRows(FilteredMovingNoPEO, each [YearMonthKey] = LatestKey),
    
    GroupedRows = Table.Group(
        FilteredLatestMonth, 
        {"OFFICER_DISPLAY_NAME", "Month_Year"}, 
        {{"Count", each List.Sum([TICKET_COUNT]), type number}}
    ),
    
    SortedRows = Table.Sort(GroupedRows, {{"Count", Order.Descending}}),
    
    Top5 = Table.FirstN(SortedRows, 5),
    
    RenamedColumns = Table.RenameColumns(Top5, {
        {"OFFICER_DISPLAY_NAME", "Officer"}
    })
in
    RenamedColumns
```

---

### 4. summons_top5_parking

**What changed:**
- Added `{"TICKET_COUNT", Int64.Type}` to ChangedType
- Replaced `each Table.RowCount(_)` with `each List.Sum([TICKET_COUNT])` in GroupedRows

**Tool:** `partition_operations` Update | **Table:** `summons_top5_parking`

```m
let
    Source = Csv.Document(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_slim_for_powerbi.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{"YearMonthKey", Int64.Type}, {"TICKET_COUNT", Int64.Type}, {"TYPE", type text}}),
    
    FilteredParking = Table.SelectRows(ChangedType, each ([TYPE] = "P")),
    
    LatestKey = List.Max(FilteredParking[YearMonthKey]),
    
    FilteredLatestMonth = Table.SelectRows(FilteredParking, each [YearMonthKey] = LatestKey),
    
    GroupedRows = Table.Group(
        FilteredLatestMonth, 
        {"OFFICER_DISPLAY_NAME", "Month_Year"}, 
        {{"Count", each List.Sum([TICKET_COUNT]), type number}}
    ),
    
    SortedRows = Table.Sort(GroupedRows, {{"Count", Order.Descending}}),
    
    Top5 = Table.FirstN(SortedRows, 5),
    
    RenamedColumns = Table.RenameColumns(Top5, {
        {"OFFICER_DISPLAY_NAME", "Officer"}
    })
in
    RenamedColumns
```

---

## Mandatory Validation (Run ALL of These After Applying Updates)

After applying all 4 partition updates above, you MUST run every validation step below and report the results. Do not skip any. Show me the actual output from each query so I can confirm the data looks correct.

### Step 1: Check all 4 tables loaded without errors

```
table_operations -> List
```

Look at the 4 tables you just updated. Report: did any show an error state? If yes, use `table_operations -> Get` on that table and show me the full error message.

### Step 2: Verify the 13-month trend has data for every month

```
dax_query_operations -> Execute
query: EVALUATE ADDCOLUMNS(SUMMARIZE('summons_13month_trend', 'summons_13month_trend'[Month_Year]), "Tickets", SUM('summons_13month_trend'[TICKET_COUNT]))
```

**Show me the full result table.** I expect:
- Approximately 13 rows (02-25 through 02-26)
- Each month's Tickets value should be in the **hundreds or thousands** (e.g., Jan 2025 M+P ~2,700)
- If any month shows "1" or "2", the fix did NOT work — tell me which month

### Step 3: Verify summons_all_bureaus has bureau-level counts

```
dax_query_operations -> Execute
query: EVALUATE 'summons_all_bureaus'
```

**Show me the full result table.** I expect:
- Rows for TRAFFIC BUREAU, PATROL DIVISION, DETECTIVE BUREAU, etc.
- M and P columns with counts in the hundreds (not 0 or 1)
- A Total column that is the sum of M + P

### Step 4: Verify summons_top5_moving returns 5 officers

```
dax_query_operations -> Execute
query: EVALUATE 'summons_top5_moving'
```

**Show me the full result table.** I expect:
- 5 rows, each with an Officer name, Month_Year, and Count
- Count values should be > 10
- No PEO officers should appear

### Step 5: Verify summons_top5_parking returns 5 officers

```
dax_query_operations -> Execute
query: EVALUATE 'summons_top5_parking'
```

**Show me the full result table.** I expect:
- 5 rows, each with an Officer name, Month_Year, and Count
- Count values should be > 50

### Step 6: Compare Before vs After — Check a specific month for correct counts

```
dax_query_operations -> Execute
query: EVALUATE ADDCOLUMNS(SUMMARIZE(FILTER('summons_13month_trend', 'summons_13month_trend'[Month_Year] = "01-26"), 'summons_13month_trend'[Month_Year], 'summons_13month_trend'[TYPE]), "Tickets", SUM('summons_13month_trend'[TICKET_COUNT]))
```

**Show me the full result table.** For January 2026 (01-26), I expect:
- TYPE = "M" (Moving) with Tickets around 400-500
- TYPE = "P" (Parking) with Tickets around 3,000-4,000

### Summary

After running all 6 steps, give me a summary like:

| Check | Status | Detail |
|-------|--------|--------|
| Tables loaded | PASS/FAIL | Any errors? |
| 13-month trend | PASS/FAIL | How many months? Any showing 1 or 2? |
| All bureaus | PASS/FAIL | How many bureau rows? Counts reasonable? |
| Top 5 moving | PASS/FAIL | 5 officers returned? |
| Top 5 parking | PASS/FAIL | 5 officers returned? |
| Jan 2026 M/P split | PASS/FAIL | M=??? P=??? |

---

## Do Not

- Do NOT modify `___Summons` or `___Summons_Diagnostic` — those are unchanged.
- Do NOT modify `pReportMonth` — it stays at `#date(2026, 2, 1)`.
- Do NOT create new queries or tables — only update the 4 existing partitions listed above.
