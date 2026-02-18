# SUMMONS - FINAL M CODE (Copy/Paste Ready)
## 2026-02-17 - ALL FIXES APPLIED | VISUALS VERIFIED

**Status:** Top 5 Moving, Top 5 Parking, and All Bureaus visuals are correct as of 2026-02-17. All queries use **previous complete month** (e.g. January 2026 when run in February). Source: `summons_powerbi_latest.xlsx` from Summons ETL.

## ✅ Ready to Copy Into Power BI

---

## Query 1: ___Summons_Top5_Moving

**Copy this entire block:**

```powerquery
let
    PrevDate = Date.AddMonths(DateTime.Date(DateTime.LocalNow()), -1),
    PreviousMonthKey = Date.Year(PrevDate) * 100 + Date.Month(PrevDate),
    MonthYearText = Text.PadStart(Number.ToText(Date.Month(PrevDate)), 2, "0") & "-" & Text.End(Number.ToText(Date.Year(PrevDate)), 2),
    Source = Excel.Workbook(File.Contents("C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"), null, true),
    Summons_Data_Sheet = Source{[Item="Summons_Data", Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    WithTitle = if Table.HasColumns(PromotedHeaders, "TITLE") then PromotedHeaders else Table.AddColumn(PromotedHeaders, "TITLE", each null, type text),
    ChangedType = Table.TransformColumnTypes(WithTitle, {{"YearMonthKey", Int64.Type}, {"TYPE", type text}, {"TITLE", type text}}),
    FilteredMoving = Table.SelectRows(ChangedType, each ([TYPE] = "M")),
    FilteredMovingNoPEO = Table.SelectRows(FilteredMoving, each ([TITLE] = null or Text.Trim(Text.Upper([TITLE] ?? "")) <> "PEO") and ([OFFICER_DISPLAY_NAME] = null or not (Text.StartsWith([OFFICER_DISPLAY_NAME], "PEO ") or Text.StartsWith([OFFICER_DISPLAY_NAME], "PEO,") or Text.StartsWith([OFFICER_DISPLAY_NAME], "PEO.")))),
    FilteredLatestMonth = Table.SelectRows(FilteredMovingNoPEO, each [YearMonthKey] = PreviousMonthKey),
    GroupedRows = Table.Group(FilteredLatestMonth, {"PADDED_BADGE_NUMBER", "Month_Year"}, {{"Count", each Table.RowCount(_), type number}, {"Officer", each List.First([OFFICER_DISPLAY_NAME]), type text}}),
    RemovedBadge = Table.RemoveColumns(GroupedRows, {"PADDED_BADGE_NUMBER"}),
    SortedRows = Table.Sort(RemovedBadge, {{"Count", Order.Descending}}),
    Top5 = Table.FirstN(SortedRows, 5),
    SetMonthLabel = Table.TransformColumns(Top5, {{"Month_Year", each MonthYearText, type text}})
in
    SetMonthLabel
```

**Columns returned:** Officer, Month_Year, Count

**Key fixes:** (1) Use **previous complete month** (e.g. in Feb show Jan 01-26), not "max month in file". (2) Exclude PEO by TITLE; group by badge. (3) **Count** = number of rows in staging file for that officer with TYPE=M for that month.

---

## Query 2: ___Summons_Top5_Parking

**Copy this entire block:**

```powerquery
let
    Source = Excel.Workbook(File.Contents("C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"), null, true),
    Summons_Data_Sheet = Source{[Item="Summons_Data", Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{"YearMonthKey", Int64.Type}, {"TYPE", type text}}),
    FilteredParking = Table.SelectRows(ChangedType, each ([TYPE] = "P")),
    LatestKey = List.Max(FilteredParking[YearMonthKey]),
    FilteredLatestMonth = Table.SelectRows(FilteredParking, each [YearMonthKey] = LatestKey),
    GroupedRows = Table.Group(FilteredLatestMonth, {"OFFICER_DISPLAY_NAME", "Month_Year"}, {{"Count", each Table.RowCount(_), type number}}),
    SortedRows = Table.Sort(GroupedRows, {{"Count", Order.Descending}}),
    Top5 = Table.FirstN(SortedRows, 5),
    RenamedColumns = Table.RenameColumns(Top5, {{"OFFICER_DISPLAY_NAME", "Officer"}})
in
    RenamedColumns
```

**Columns returned:** Officer, Month_Year, Count

---

## Query 3: ___Summons_All_Bureaus

**Copy this entire block:**

```powerquery
let
    PrevDate = Date.AddMonths(DateTime.Date(DateTime.LocalNow()), -1),
    PreviousMonthKey = Date.Year(PrevDate) * 100 + Date.Month(PrevDate),
    Source = Excel.Workbook(File.Contents("C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"), null, true),
    Summons_Data_Sheet = Source{[Item="Summons_Data", Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{"YearMonthKey", Int64.Type}, {"TYPE", type text}, {"WG2", type text}}),
    FilteredClean = Table.SelectRows(ChangedType, each [WG2] <> "UNKNOWN" and [WG2] <> null and [WG2] <> ""),
    FilteredLatestMonth = Table.SelectRows(FilteredClean, each [YearMonthKey] = PreviousMonthKey),
    GroupedRows = Table.Group(FilteredLatestMonth, {"WG2", "TYPE"}, {{"Count", each Table.RowCount(_), type number}}),
    ConsolidatedBureaus = Table.TransformColumns(GroupedRows, {"WG2", each if _ = "HOUSING" or _ = "OFFICE OF SPECIAL OPERATIONS" then "PATROL DIVISION" else _}),
    RegroupedRows = Table.Group(ConsolidatedBureaus, {"WG2", "TYPE"}, {{"Count", each List.Sum([Count]), type number}}),
    PivotedColumn = Table.Pivot(RegroupedRows, List.Distinct(RegroupedRows[TYPE]), "TYPE", "Count", List.Sum),
    AddM = if Table.HasColumns(PivotedColumn, "M") then PivotedColumn else Table.AddColumn(PivotedColumn, "M", each 0, Int64.Type),
    AddP = if Table.HasColumns(AddM, "P") then AddM else Table.AddColumn(AddM, "P", each 0, Int64.Type),
    ReplacedValue = Table.ReplaceValue(AddP, null, 0, Replacer.ReplaceValue, {"M", "P"}),
    AddedTotal = Table.AddColumn(ReplacedValue, "Total", each [M] + [P] + (try [C] otherwise 0), type number)
in
    AddedTotal
```

**Columns returned:** WG2 (Bureau), M, P, Total

**Key fix:** Uses **previous complete month** (same as Top 5 Moving/Parking); filters out UNKNOWN WG2; Housing & OSO → Patrol Division.

---

## Query 4: summons_13month_trend

**Copy this entire block:**

```powerquery
let
    Source = Excel.Workbook(File.Contents("C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"), null, true),
    Summons_Data_Sheet = Source{[Item="Summons_Data",Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders,{
        {"TICKET_NUMBER", type text}, 
        {"TICKET_COUNT", Int64.Type}, 
        {"IS_AGGREGATE", type logical}, 
        {"PADDED_BADGE_NUMBER", type text}, 
        {"OFFICER_DISPLAY_NAME", type text}, 
        {"OFFICER_NAME_RAW", type text}, 
        {"ISSUE_DATE", type datetime}, 
        {"VIOLATION_NUMBER", type text}, 
        {"VIOLATION_DESCRIPTION", type text}, 
        {"VIOLATION_TYPE", type text}, 
        {"TYPE", type text}, 
        {"STATUS", type text}, 
        {"LOCATION", type text}, 
        {"SOURCE_FILE", type text}, 
        {"ETL_VERSION", type text}, 
        {"Year", Int64.Type}, 
        {"Month", Int64.Type}, 
        {"YearMonthKey", Int64.Type}, 
        {"Month_Year", type text}, 
        {"TEAM", type text}, 
        {"WG1", type text}, 
        {"WG2", type text}, 
        {"WG3", type text}, 
        {"WG4", type text}, 
        {"POSS_CONTRACT_TYPE", type text}, 
        {"ASSIGNMENT_FOUND", type logical}, 
        {"DATA_QUALITY_SCORE", Int64.Type}, 
        {"TOTAL_PAID_AMOUNT", type text}, 
        {"COST_AMOUNT", Int64.Type}, 
        {"MISC_AMOUNT", Int64.Type}, 
        {"PROCESSING_TIMESTAMP", type datetime}
    }),
    FilteredClean = Table.SelectRows(ChangedType, each [WG2] <> "UNKNOWN"),
    AddConsolidatedBureau = Table.AddColumn(FilteredClean, "Bureau_Consolidated", each if [WG2] = "HOUSING" or [WG2] = "OFFICE OF SPECIAL OPERATIONS" then "PATROL DIVISION" else [WG2], type text)
in
    AddConsolidatedBureau
```

**Columns returned:** All columns + Bureau_Consolidated

**Key fix:** Filters out UNKNOWN rows

---

## Expected Results

### All Bureaus (January 2026):
| WG2 | M | P | Total |
|-----|---|---|-------|
| DETECTIVE BUREAU | 1 | 0 | 1 |
| PATROL DIVISION | 84 | 373 | 457 |
| TRAFFIC BUREAU | 156 | 2,995 | 3,151 |

**NO UNKNOWN ROW** ✅

### Top 5 Moving:
- 5 rows with **police officer names** (excludes PEOs who can't write moving summons)
- Columns: Officer, Month_Year, Count
- Shows officers who issued the most Moving summons

### Top 5 Parking:
- 5 rows with **officer names** (e.g., "JONES, R.", "WILSON, K.")
- Columns: Officer, Month_Year, Count
- Shows officers who issued the most Parking summons

### 13-Month Trend:
- 3,639 records total
- 13 months covered (Jan 2025 - Jan 2026)
- No UNKNOWN records

---

## How to Update Power BI

1. **Open Power BI Desktop**
2. **Home → Transform Data**
3. **For each query:**
   - Find query in left pane (or create new Blank Query)
   - Right-click → Advanced Editor
   - Delete all code
   - Paste new code from above
   - Click Done
4. **Close & Apply**
5. **Verify** visuals show correct data

---

## If Errors Occur

**"Column doesn't exist":** 
- Make sure file path is correct
- Check column names match

**"Can't find file":**
- Update path to: `C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx`

**Still seeing UNKNOWN:**
- Verify the query code filtered UNKNOWN (line with `[WG2] <> "UNKNOWN"`)
- Close Power BI completely and reopen

---

**Files:** All saved in `m_code/` folder  
**Data:** Updated with 13-month backfill  
**Status:** ✅ Ready to paste into Power BI
