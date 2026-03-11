# pReportMonth Migration -- Claude MCP Execution Prompt

> **Purpose:** Update every M code query that uses `DateTime.LocalNow()` to use the `pReportMonth` parameter instead, freezing each saved `.pbix` as an immutable snapshot.
>
> **Model:** `2026_02_Monthly_Report_laptop`
>
> **Parameter:** `pReportMonth = #date(2026, 2, 1)`
>
> **Date:** 2026-03-09

---

## Pre-Flight Checklist

1. Connect to Power BI Desktop via MCP:
   ```
   connection_operations -> ListLocalInstances
   connection_operations -> Connect (use the returned connection string)
   ```
2. Verify `pReportMonth` exists and is set:
   ```
   named_expression_operations -> Get -> pReportMonth
   ```
3. **SAVE the .pbix before starting** -- this is your rollback point.

## Standard Window Pattern

Every query below applies this logic:

```
EndOfWindow   = Date.EndOfMonth(pReportMonth),
StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12)),
```

With `pReportMonth = #date(2026, 2, 1)`:
- `EndOfWindow` = February 28, 2026
- `StartOfWindow` = February 1, 2025
- Window = 13 months inclusive

## MCP Tool Call Format

For **table partitions** (most queries):
```
partition_operations -> Update
  definitions: [{ tableName: "<TABLE>", expression: "<FULL M CODE>" }]
```

For **named expressions** (STACP_DIAGNOSTIC only):
```
named_expression_operations -> Update
  definitions: [{ name: "<NAME>", expression: "<FULL M CODE>" }]
```

---

## Query Updates

---

### 1. ___DimMonth

**What changed:** Replaced `DateTime.Date(DateTime.LocalNow())` -> `pReportMonth`. Window now derived from `EndOfWindow`/`StartOfWindow`.

**Tool:** `partition_operations` Update | **Table:** `___DimMonth`

```m
let
    EndOfWindow = Date.EndOfMonth(pReportMonth),
    StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12)),
    MonthStarts = List.Generate(() => StartOfWindow, each _ <= EndOfWindow, each Date.AddMonths(_, 1)),
    ToTable = Table.FromList(MonthStarts, Splitter.SplitByNothing(), {"MonthStart"}),
    TypedDate = Table.TransformColumnTypes(ToTable, {{"MonthStart", type date}}),
    AddLabel = Table.AddColumn(TypedDate, "MonthLabel", each Date.ToText([MonthStart], "MM-yy"), type text),
    AddSort = Table.AddColumn(AddLabel, "MonthSort", each Date.Year([MonthStart]) * 100 + Date.Month([MonthStart]), Int64.Type)
in
    AddSort
```

---

### 2. ___Arrest_Categories

**What changed:** Replaced `Date.AddMonths(Date.From(DateTime.LocalNow()), -1)` with `pReportMonth` directly. Since `pReportMonth` IS the report month, the single-month arrest filter now shows arrests for that month.

**Tool:** `partition_operations` Update | **Table:** `___Arrest_Categories`

```m
// 🕒 2025-09-03-17-30-00
// Project: Arrest_Analysis/Arrest_Categories
// Author: R. A. Carucci
// Purpose: Simplified M Code that relies on Python preprocessing for geographic
// data
// Updated: pReportMonth-driven (no DateTime.LocalNow)

let
    // ═══ A) Load latest Power BI ready file ═══════════════════════════
    FolderFiles = Folder.Files(
        "C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\ARREST_DATA\Power_BI"
    ),
    PowerBIFiles = Table.SelectRows(
        FolderFiles,
        each [Extension] = ".xlsx" and 
             Text.Contains([Name], "PowerBI_Ready")
    ),
    Sorted = Table.Sort(PowerBIFiles, {{"Date modified", Order.Descending}}),
    
    Source = if Table.RowCount(Sorted) > 0 then
        Excel.Workbook(Sorted{0}[Content], null, true){0}[Data]
    else
        error "No Power BI ready files found",

    // ═══ B) Basic data cleaning ═══════════════════════════════════════
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    
    ToDate = (x) => try Date.From(x) otherwise null,
    ReportDate = pReportMonth,
    PrevY = Date.Year(ReportDate),
    PrevM = Date.Month(ReportDate),
    
    DateFiltered = Table.SelectRows(
        Headers,
        each let d = ToDate([#"Arrest Date"]) in
            d <> null and Date.Year(d) = PrevY and Date.Month(d) = PrevM
    ),

    // ═══ C) Use Python-processed geographic data directly ═══════════
    WithHomeCategory = Table.AddColumn(
        DateFiltered,
        "Home_Category_Final",
        each 
            if Table.HasColumns(DateFiltered, "Home_Category") then 
                [Home_Category]
            else if Text.Contains(Text.Upper([Address] ?? ""), "HACKENSACK") then 
                "Local"
            else 
                "Check Data",
        type text
    ),

    // ═══ D) Simple charge categorization ═════════════════════════════
    AddChargeCategory = Table.AddColumn(
        WithHomeCategory,
        "ChargeCategory",
        each 
            let charge = Text.Upper([Charge] ?? "") in
            if Text.Contains(charge, "ASSAULT") then "Assault"
            else if Text.Contains(charge, "SHOPLIFTING") then "Theft"
            else if Text.Contains(charge, "BURGLARY") then "Burglary"
            else if Text.Contains(charge, "ROBBERY") then "Robbery" 
            else if Text.Contains(charge, "WARRANT") then "Warrant"
            else if Text.Contains(charge, "DWI") then "DWI"
            else if Text.Contains(charge, "DRUG") then "Drug Related"
            else if Text.Contains(charge, "WEAPON") then "Weapons"
            else "Other",
        type text
    ),

    // ═══ E) Data quality indicators ═════════════════════════════════
    AddDataQuality = Table.AddColumn(
        AddChargeCategory,
        "DataQualityScore", 
        each 
            (if [Name] <> null and [Name] <> "" then 1 else 0) +
            (if [Age] <> null and Number.From([Age] ?? 0) > 0 then 1 else 0) +
            (if [Address] <> null and [Address] <> "" then 1 else 0) +
            (if [Charge] <> null and [Charge] <> "" then 1 else 0) +
            (if Table.HasColumns(AddChargeCategory, "ZIP") and [ZIP] <> null then 1 else 0),
        type number
    ),

    // ═══ F) Final type enforcement ═══════════════════════════════════
    TypedData = Table.TransformColumnTypes(
        AddDataQuality,
        {
            {"Age", type number},
            {"DataQualityScore", type number},
            {"Arrest Date", type date}
        }
    ),

    // ═══ G) Add source tracking ═══════════════════════════════════════
    WithSourceInfo = Table.AddColumn(
        TypedData,
        "SourceFile",
        each if Table.RowCount(Sorted) > 0 then Sorted{0}[Name] else "Unknown",
        type text
    )

in
    WithSourceInfo
```

---

### 3. ___CSB_Monthly

**What changed:** Replaced `Date.From(DateTime.LocalNow())` / `CurrentMonthStart` / `EndMonth` / `StartMonth` with `EndOfWindow` / `StartOfWindow` derived from `pReportMonth`.

**Tool:** `partition_operations` Update | **Table:** `___CSB_Monthly`

```m
let
    //==== Source & initial cleanup ============================================================
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\CSB\csb_monthly.xlsm"),
        null, true
    ),
    MoM_Sheet = Source{[Item="MoM",Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(MoM_Sheet, [PromoteAllScalars=true]),
    CleanedData = Table.SelectRows(PromotedHeaders, each [#"Tracked Items"] <> null and [#"Tracked Items"] <> ""),

    //==== Column bookkeeping =================================================================
    ColumnNames = Table.ColumnNames(CleanedData),
    FirstColumnName = ColumnNames{0},
    DateColumns = List.Skip(ColumnNames, 1),

    //==== Rolling 13-month window (pReportMonth-driven) ======================================
    EndOfWindow = Date.EndOfMonth(pReportMonth),
    StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12)),

    //==== Validate/select only date columns within the window ================================
    ValidDateColumns =
        List.Select(
            DateColumns,
            (colName as text) as logical =>
                let
                    parts = Text.Split(colName, "-"),
                    MonthNum =
                        if List.Count(parts) >= 2
                        then try Number.FromText(parts{0}) otherwise null
                        else null,
                    YearTwo =
                        if List.Count(parts) >= 2
                        then try Number.FromText(parts{1}) otherwise null
                        else null,
                    FullYear =
                        if YearTwo <> null
                        then (if YearTwo >= 50 then 1900 + YearTwo else 2000 + YearTwo)
                        else null,
                    ColumnDate =
                        if MonthNum <> null and FullYear <> null
                        then try #date(FullYear, MonthNum, 1) otherwise null
                        else null
                in
                    ColumnDate <> null and ColumnDate >= StartOfWindow and ColumnDate <= EndOfWindow
        ),

    SelectedColumns = List.Combine({ {FirstColumnName}, ValidDateColumns }),
    Pruned = Table.SelectColumns(CleanedData, SelectedColumns),

    //==== Unpivot & enrich ===================================================================
    Unpivoted =
        Table.UnpivotOtherColumns(
            Pruned,
            {FirstColumnName},
            "Month_MM_YY",
            "Value"
        ),
    Renamed = Table.RenameColumns(Unpivoted, {{FirstColumnName, "CSB_Category"}}),

    WithDate =
        Table.AddColumn(
            Renamed,
            "Date",
            each
                let
                    monthText = [Month_MM_YY],
                    parts = Text.Split(monthText, "-"),
                    m = if List.Count(parts) >= 2 then try Number.FromText(parts{0}) otherwise 1 else 1,
                    yy = if List.Count(parts) >= 2 then try Number.FromText(parts{1}) otherwise 25 else 25,
                    yyyy = if yy >= 50 then 1900 + yy else 2000 + yy
                in
                    #date(yyyy, m, 1),
            type date
        ),

    WithSort =
        Table.AddColumn(
            WithDate,
            "Month_Sort_Order",
            each
                let
                    d = [Date],
                    months =
                        (Date.Year(d) - Date.Year(StartOfWindow)) * 12
                        + (Date.Month(d) - Date.Month(StartOfWindow))
                        + 1
                in
                    months,
            Int64.Type
        ),

    WithDisplay =
        Table.AddColumn(WithSort, "Month_Display", each Date.ToText([Date], "MMM yyyy"), type text),

    //==== Sort & types =======================================================================
    Sorted = Table.Sort(WithDisplay, {{"Date", Order.Ascending}}),
    Typed =
        Table.TransformColumnTypes(
            Sorted,
            {
                {"CSB_Category", type text},
                {"Month_MM_YY", type text},
                {"Value", Currency.Type},
                {"Date", type date},
                {"Month_Sort_Order", Int64.Type},
                {"Month_Display", type text}
            }
        ),

    //==== Final hygiene ======================================================================
    Final = Table.SelectRows(Typed, each [CSB_Category] <> null and [CSB_Category] <> "")
in
    Final
```

---

### 4. ___Detectives

**What changed:** Replaced all 4 occurrences of `DateTime.LocalNow()` (CurrentDate, subtitle, DataRefreshTime) with `pReportMonth`-derived logic. Renamed `EndFilterDate`/`StartFilterDate` to `EndOfWindow`/`StartOfWindow`.

**Tool:** `partition_operations` Update | **Table:** `___Detectives`

```m
// 🕒 2026-02-13-18-00-00
// # Master_Automation/Detectives/___Detectives.m
// # Author: R. A. Carucci
// # Purpose: Import Detective Division cases from restructured 2026-only
// workbook with rolling 13-month window (pReportMonth-driven).

let
    // =================================================================
    // FILE PATH AND TABLE LOAD
    // =================================================================
    FilePath =
        "C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Detectives\detectives_monthly.xlsx",

    Source = Excel.Workbook(File.Contents(FilePath), null, true),

    MoM_Det_Table = Source{[Item = "_mom_det", Kind = "Table"]}[Data],

    DetectedTypes = Table.TransformColumnTypes(MoM_Det_Table, {}, "en-US"),

    // =================================================================
    // DATA CLEANING
    // =================================================================
    RemovedEmptyRows = Table.SelectRows(
        DetectedTypes, each not List.IsEmpty(List.RemoveMatchingItems(
                           Record.FieldValues(_), {"", null}))),

    ColumnNames = Table.ColumnNames(RemovedEmptyRows),
    FirstColumn = ColumnNames{0},

    FilteredToActiveCases = Table.SelectRows(
        RemovedEmptyRows, each let CategoryName = Record.Field(_, FirstColumn),
        RowValues = List.Skip(Record.FieldValues(_), 1),
        HasActivity = List.AnyTrue(List.Transform(
            RowValues, each try(_ <> null and _ <> "" and Number.From(_) > 0)
                           otherwise false)) in HasActivity),

    // =================================================================
    // UNPIVOT TO LONG FORMAT
    // =================================================================
    UnpivotedData = Table.UnpivotOtherColumns(
        FilteredToActiveCases, {FirstColumn}, "Month_MM_YY", "Value"),

    // =================================================================
    // DATE PARSING AND SORT ORDER
    // =================================================================
    AddedDateInfo = Table.AddColumn(
        UnpivotedData, "Date", each let MonthText = [Month_MM_YY],
        Parts = Text.Split(MonthText, "-"),
        MonthPart = if List.Count(Parts) >= 1 then Parts{0} else "01",
        YearPart = if List.Count(Parts) >= 2 then Parts{1} else "26",

        YearNum = try Number.From(YearPart) otherwise null,
        FullYear = if YearNum = null then null else if YearNum >=
                                50 then 1900 + YearNum else 2000 + YearNum,

        MonthNum = try Number.From(MonthPart) otherwise null,

        DateValue = if MonthNum =
            null or FullYear =
                null then null else try #date(FullYear, MonthNum, 1)
                    otherwise null in DateValue,
        type date),

    AddedNormalizedMonth = Table.AddColumn(
        AddedDateInfo, "Month_Normalized",
        each if[Date]<> null then Text.PadStart(Text.From(Date.Month([Date])),
                                                2, "0") &
            "-" & Text.End(Text.From(Date.Year([Date])), 2) else[Month_MM_YY],
        type text),

    RemovedOldMonth =
        Table.RemoveColumns(AddedNormalizedMonth, {"Month_MM_YY"}),
    RenamedMonth = Table.RenameColumns(RemovedOldMonth,
                                       {{"Month_Normalized", "Month_MM_YY"}}),

    AddedSortOrder =
        Table.AddColumn(RenamedMonth, "Month_Sort_Order",
                        each if[Date]<> null then Date.Year([Date]) * 100 +
                            Date.Month([Date]) else null,
                        Int64.Type),

    // =================================================================
    // ROLLING 13-MONTH WINDOW (pReportMonth-driven)
    // =================================================================
    EndOfWindow = Date.EndOfMonth(pReportMonth),
    StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12)),

    ReportingPeriod = Date.ToText(StartOfWindow, "MM/yy") & " - " &
                      Date.ToText(EndOfWindow, "MM/yy"),

    FilteredMonths = Table.SelectRows(
        AddedSortOrder, each[Date]<> null and[Date] >=
                            StartOfWindow and[Date] <= EndOfWindow),

    // =================================================================
    // METADATA COLUMNS
    // =================================================================
    AddedReportingMeta = Table.AddColumn(FilteredMonths, "ReportingPeriod",
                                         each ReportingPeriod, type text),

    UniqueMonthsCount = Table.RowCount(
        Table.Group(FilteredMonths, {"Date"},
                    {{"Count", each Table.RowCount(_), type number}})),

    AddedMonthCount = Table.AddColumn(AddedReportingMeta, "MonthsIncluded",
                                      each UniqueMonthsCount, type number),

    AddedCaseType = Table.AddColumn(
        AddedMonthCount, "Case_Type",
        each let CategoryName = Record.Field(_, FirstColumn),
        HighImpactCategories = {"ABC Investigation(s)", "Background Check(s)",
                                "Firearm Background Check(s)",
                                "Criminal Mischief", "Fraud",
                                "Generated Complaint(s)", "BWC Review(s)",
                                "Aggravated Assault", "Animal Cruelty",
                                "Burglary - Auto", "Domestic Violence",
                                "Drug Investigation(s)", "Harassment",
                                "Motor Vehicle Theft"},
        CaseType = if List.Contains(HighImpactCategories, CategoryName) then
                   "High Impact" else "Administrative" in CaseType,
        type text),

    // =================================================================
    // FINAL TYPE CONVERSIONS
    // =================================================================
    FinalDataTypes = Table.TransformColumnTypes(
        AddedCaseType, {{FirstColumn, type text},
                        {"Month_MM_YY", type text},
                        {"Value", type number},
                        {"Date", type date},
                        {"Month_Sort_Order", Int64.Type},
                        {"Case_Type", type text}}),

    // =================================================================
    // REPORT TITLE AND SUBTITLE
    // =================================================================
    AddedTitle = Table.AddColumn(
        FinalDataTypes, "ReportTitle",
        each "Detective Division - Comprehensive Case Analysis", type text),

    AddedSubtitle = Table.AddColumn(
        AddedTitle, "ReportSubtitle",
        each let StartLabel = Date.ToText(StartOfWindow, "MMMM yyyy"),
        EndLabel = Date.ToText(EndOfWindow, "MMMM yyyy"),
        ReportLabel = Date.ToText(pReportMonth, "MMMM yyyy") in
            "Rolling 13-Month Period: " &
            StartLabel & " - " & EndLabel & " | Report Month: " & ReportLabel,
        type text),

    AddedRefreshTime = Table.AddColumn(AddedSubtitle, "DataRefreshTime",
                                       each DateTime.From(pReportMonth), type datetime)

                           in AddedRefreshTime
```

---

### 5. ___Det_case_dispositions_clearance

**What changed:** Replaced `Date.From(DateTime.LocalNow())` / `EndFilterDate` / `StartFilterDate` with `EndOfWindow` / `StartOfWindow` from `pReportMonth`.

**Tool:** `partition_operations` Update | **Table:** `___Det_case_dispositions_clearance`

```m
// 🕒 2026-02-13-18-05-00
// # Master_Automation/Detectives/___Det_case_dispositions_clearance_2026.m
// # Author: R. A. Carucci
// # Purpose: Import Detective case clearance and dispositions from restructured 2026-only workbook (_CCD_MOM table) with rolling 13-month window and robust % normalization.
// Updated: pReportMonth-driven (no DateTime.LocalNow)

let
    // =================================================================
    // FILE PATH AND TABLE LOAD
    // =================================================================
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Detectives\detectives_monthly.xlsx"),
        null, true
    ),
    
    CCD_Table = Source{[Item="_CCD_MOM", Kind="Table"]}[Data],

    // =================================================================
    // REQUIRED ROW ORDER (EXACT LABELS)
    // =================================================================
    RequiredOrder = {
        "Active / Administratively Closed",
        "Arrest",
        "Complaint Signed",
        "Ex Cleared / Closed",
        "Juvenile Complaint",
        "Stationhouse Adjustment",
        "TOT DCP&P",
        "Unfounded / Closed",
        "Monthly Bureau Case  Clearance % ",
        "YTD Bureau Case Clearance % "
    },

    // =================================================================
    // COLUMN NAME DETECTION
    // =================================================================
    ColNames        = Table.ColumnNames(CCD_Table),
    FirstColumnName = ColNames{0},
    MonthColumns    = List.Skip(ColNames, 1),

    // =================================================================
    // FILTER TO REQUIRED ROWS ONLY
    // =================================================================
    KeptRows = Table.SelectRows(
        CCD_Table,
        (r) => List.Contains(RequiredOrder, Record.Field(r, FirstColumnName))
    ),

    // =================================================================
    // ADD ROW SORT ORDER
    // =================================================================
    WithRowSort = Table.AddColumn(
        KeptRows, "Row_Sort",
        each List.PositionOf(RequiredOrder, Record.Field(_, FirstColumnName)),
        Int64.Type
    ),
    
    OrderedRows = Table.Sort(WithRowSort, {{"Row_Sort", Order.Ascending}}),

    // =================================================================
    // INITIAL TYPE CONVERSION (WIDE FORMAT)
    // =================================================================
    TypedWide = Table.TransformColumnTypes(
        OrderedRows,
        {{FirstColumnName, type text}} & 
        List.Transform(MonthColumns, each {_, type any})
    ),

    // =================================================================
    // FLAG PERCENT ROWS
    // =================================================================
    MarkPercentRow = Table.AddColumn(
        TypedWide, "Is_Percent",
        each Text.Contains(Record.Field(_, FirstColumnName), "%"),
        type logical
    ),

    // =================================================================
    // UNPIVOT TO LONG FORMAT
    // =================================================================
    Unpivoted = Table.UnpivotOtherColumns(
        MarkPercentRow,
        {FirstColumnName, "Row_Sort", "Is_Percent"},
        "Month",
        "ValueRaw"
    ),

    // =================================================================
    // ROBUST PERCENTAGE NORMALIZATION
    // =================================================================
    Normalized = Table.AddColumn(
        Unpivoted, "Value",
        each
            let 
                v = [ValueRaw] 
            in
            if [Is_Percent] then
                if Value.Is(v, type text) then
                    let
                        s   = Text.Trim(v),
                        hasPct = Text.Contains(s, "%"),
                        n0  = try Number.From(Text.Replace(s, "%", "")) otherwise null,
                        n   = if n0 = null then null
                              else if hasPct then n0 / 100
                              else if n0 > 1 then n0 / 100 
                              else n0
                    in  n
                else
                    let
                        n0 = try Number.From(v) otherwise null,
                        n  = if n0 = null then null
                             else if n0 > 1 then n0 / 100 
                             else n0
                    in  n
            else
                try Number.From(v) otherwise null,
        type number
    ),
    
    Cleaned = Table.RemoveColumns(Normalized, {"ValueRaw"}),

    // =================================================================
    // DATE PARSING FROM MM-YY FORMAT
    // =================================================================
    WithDate = Table.AddColumn(Cleaned, "Date", each
        let
            mTxt = [Month],
            Parts = Text.Split(mTxt, "-"),
            MonthPart = if List.Count(Parts) >= 1 then Parts{0} else "01",
            YearPart = if List.Count(Parts) >= 2 then Parts{1} else "26",
            
            y2 = try Number.From(YearPart) otherwise null,
            y4 = if y2 = null then null 
                 else if y2 >= 50 then 1900 + y2 
                 else 2000 + y2,
            
            mNum = try Number.From(MonthPart) otherwise null
        in
            if mNum = null or y4 = null then null 
            else try #date(y4, mNum, 1) otherwise null,
        type date
    ),

    // =================================================================
    // ADDITIONAL DATE HELPER COLUMNS
    // =================================================================
    WithNormalizedMonth = Table.AddColumn(WithDate, "Month_Normalized", each 
        if [Date] <> null then 
            Text.PadStart(Text.From(Date.Month([Date])), 2, "0") & "-" & 
            Text.End(Text.From(Date.Year([Date])), 2)
        else [Month], 
        type text),
    
    RemovedOldMonth = Table.RemoveColumns(WithNormalizedMonth, {"Month"}),
    RenamedMonth = Table.RenameColumns(RemovedOldMonth, {{"Month_Normalized", "Month"}}),
    
    WithMonthYear = Table.AddColumn(RenamedMonth, "Month_Year", each 
        if [Date] = null then null 
        else Date.MonthName([Date]) & " " & Text.From(Date.Year([Date])), 
        type text),
    
    WithSortOrder = Table.AddColumn(WithMonthYear, "Sort_Order", each 
        if [Date] = null then null 
        else Date.Year([Date]) * 100 + Date.Month([Date]), 
        Int64.Type),
    
    WithAbbrev = Table.AddColumn(WithSortOrder, "Month_Abbrev", each 
        if [Date] = null then null 
        else Text.PadStart(Text.From(Date.Month([Date])), 2, "0") & "-" & 
             Text.End(Text.From(Date.Year([Date])), 2), 
        type text),

    // =================================================================
    // DISPOSITION CATEGORY GROUPING
    // =================================================================
    WithDispCat = Table.AddColumn(WithAbbrev, "Disposition_Category", each
        let 
            disp = Record.Field(_, FirstColumnName)
        in
            if Text.Contains(disp, "Active") or Text.Contains(disp, "Administratively") 
                then "Open Cases"
            else if Text.Contains(disp, "Arrest") or Text.Contains(disp, "Complaint") 
                then "Prosecuted"
            else if Text.Contains(disp, "Cleared") or Text.Contains(disp, "Unfounded") 
                then "Cleared"
            else if Text.Contains(disp, "%") 
                then "Performance Metric"
            else "Other",
        type text
    ),

    // =================================================================
    // DATE RANGE FILTER (pReportMonth-driven)
    // =================================================================
    EndOfWindow   = Date.EndOfMonth(pReportMonth),
    StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12)),

    FilteredMonths = Table.SelectRows(
        WithDispCat,
        each [Date] <> null and 
             [Date] >= StartOfWindow and 
             [Date] <= EndOfWindow
    ),

    // =================================================================
    // FINAL TYPE CONVERSIONS
    // =================================================================
    Final = Table.TransformColumnTypes(FilteredMonths, {
        {FirstColumnName, type text},
        {"Month", type text},
        {"Value", type number},
        {"Date", type date},
        {"Month_Year", type text},
        {"Sort_Order", Int64.Type},
        {"Month_Abbrev", type text},
        {"Disposition_Category", type text},
        {"Row_Sort", Int64.Type},
        {"Is_Percent", type logical}
    })
    
in
    Final
```

---

### 6. ___Drone

**What changed:** Replaced `DateTime.Date(DateTime.LocalNow())` / `PriorMonth` / `StartMonth` with `EndOfWindow` / `StartOfWindow` from `pReportMonth`.

**Tool:** `partition_operations` Update | **Table:** `___Drone`

```m
// 🕒 2025-08-19-17-30-00
// Project: Drone_Analytics/Final_Duration_Based_Handling
// Author: R. A. Carucci
// Purpose: Properly handle Excel DURATION values for drone metrics
// Updated: pReportMonth-driven (no DateTime.LocalNow)

let
    // 1) Load the workbook
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Drone_Monthly.xlsx"),
        null, true),

    // ─── DFR Activity sheet ──────────────────────────────────────────────────
    DFR_Raw = Source{[Name = "DFR Activity", Kind = "Sheet"]}[Data],
    DFR_Headers = Table.PromoteHeaders(DFR_Raw, [PromoteAllScalars = true]),
    DFR_MetricKey = Table.ColumnNames(DFR_Headers){0},
    DFR_PeriodCols = List.Select(Table.ColumnNames(DFR_Headers), each Text.Length(_) = 5 and Text.Middle(_, 2, 1) = "-"),
    DFR_Unpivot = Table.Unpivot(DFR_Headers, DFR_PeriodCols, "Period", "RawValue"),
    DFR_Renamed = Table.RenameColumns(DFR_Unpivot, {{DFR_MetricKey, "Metric"}}),

    DFR_WithOrder = Table.AddColumn(DFR_Renamed, "SortOrder", each 
        if [Metric] = "DRF - Total Calls Responded To" then 1 
        else if [Metric] = "DRF - Assisted Arrests" then 2 
        else if [Metric] = "DRF - Deployments that Avoided Dispatching a Patrol Unit" then 3 
        else if [Metric] = "DRF - First on Scene Count" then 4 
        else if [Metric] = "DRF - AVG Response Times - First on Scene (Mins:Secs)" then 5 
        else if [Metric] = "DRF - AVG Response Times - All Calls (Mins:Secs)" then 6 
        else if [Metric] = "DRF - Shift (Hours:Mins)" then 7 
        else if [Metric] = "DRF - Flight Time - Calls Responded To (Hours:Mins)" then 8 
        else if [Metric] = "DRF - Flight Time - Training Flights (Hours:Mins)" then 9 
        else if [Metric] = "DRF - Total Flight Time (Hours:Mins:Secs)" then 10 
        else 99, Int64.Type),

    DFR_Converted = Table.AddColumn(DFR_WithOrder, "Value", each 
        let
            RawVal = [RawValue],
            MetricName = [Metric]
        in
            if Value.Is(RawVal, type datetime) or Value.Is(RawVal, type time) then
                let
                    TimeVal = if Value.Is(RawVal, type datetime) then Time.From(RawVal) else RawVal,
                    Hours = Time.Hour(TimeVal),
                    Minutes = Time.Minute(TimeVal),
                    Seconds = Time.Second(TimeVal)
                in
                    if Text.Contains(MetricName, "(Mins:Secs)") then
                        let
                            TotalMinutes = Hours * 60 + Minutes,
                            DisplaySeconds = Seconds
                        in Text.From(TotalMinutes) & ":" & Text.PadStart(Text.From(DisplaySeconds), 2, "0")
                    else if Text.Contains(MetricName, "(Hours:Mins)") and not Text.Contains(MetricName, "Secs") then
                        Text.PadStart(Text.From(Hours), 2, "0") & ":" & Text.PadStart(Text.From(Minutes), 2, "0")
                    else if Text.Contains(MetricName, "(Hours:Mins:Secs)") then
                        Text.PadStart(Text.From(Hours), 2, "0") & ":" & Text.PadStart(Text.From(Minutes), 2, "0") & ":" & Text.PadStart(Text.From(Seconds), 2, "0")
                    else
                        Text.From(RawVal)
            else if Value.Is(RawVal, type duration) then
                if Text.Contains(MetricName, "(Mins:Secs)") then
                    let
                        TotalSeconds = Duration.TotalSeconds(RawVal),
                        TotalMinutes = Number.IntegerDivide(TotalSeconds, 60),
                        RemainderSeconds = Number.Mod(TotalSeconds, 60)
                    in Text.From(TotalMinutes) & ":" & Text.PadStart(Text.From(Number.Round(RemainderSeconds, 0)), 2, "0")
                else if Text.Contains(MetricName, "(Hours:Mins)") then
                    let
                        TotalSeconds = Duration.TotalSeconds(RawVal),
                        TotalHours = Number.IntegerDivide(TotalSeconds, 3600),
                        RemainderMinutes = Number.IntegerDivide(Number.Mod(TotalSeconds, 3600), 60)
                    in Text.PadStart(Text.From(TotalHours), 2, "0") & ":" & Text.PadStart(Text.From(RemainderMinutes), 2, "0")
                else
                    Duration.ToText(RawVal, "h:mm:ss")
            else if Value.Is(RawVal, type number) then
                if Text.Contains(MetricName, "(Mins:Secs)") or Text.Contains(MetricName, "(Hours:Mins)") then
                    let
                        TotalSeconds = RawVal * 24 * 60 * 60,
                        Hours = Number.IntegerDivide(TotalSeconds, 3600),
                        Minutes = Number.IntegerDivide(Number.Mod(TotalSeconds, 3600), 60),
                        Seconds = Number.Round(Number.Mod(TotalSeconds, 60), 0)
                    in
                        if Text.Contains(MetricName, "(Mins:Secs)") then
                            let TotalMinutes = Hours * 60 + Minutes
                            in Text.From(TotalMinutes) & ":" & Text.PadStart(Text.From(Seconds), 2, "0")
                        else
                            Text.PadStart(Text.From(Hours), 2, "0") & ":" & Text.PadStart(Text.From(Minutes), 2, "0")
                else
                    Text.From(RawVal)
            else
                Text.From(RawVal)),
    DFR_Clean = Table.RemoveColumns(DFR_Converted, {"RawValue"}),
    DFR_Tagged = Table.AddColumn(DFR_Clean, "Source", each "DFR Activity"),

    // ─── Non-DFR sheet ───────────────────────────────────────────────────────
    NonDFR_Raw = Source{[Name = "Non-DFR", Kind = "Sheet"]}[Data],
    NonDFR_Headers = Table.PromoteHeaders(NonDFR_Raw, [PromoteAllScalars = true]),
    NonDFR_MetricKey = Table.ColumnNames(NonDFR_Headers){0},
    NonDFR_PeriodCols = List.Select(Table.ColumnNames(NonDFR_Headers), each Text.Length(_) = 5 and Text.Middle(_, 2, 1) = "-"),
    NonDFR_Unpivot = Table.Unpivot(NonDFR_Headers, NonDFR_PeriodCols, "Period", "RawValue"),
    NonDFR_Renamed = Table.RenameColumns(NonDFR_Unpivot, {{NonDFR_MetricKey, "Metric"}}),

    NonDFR_WithOrder = Table.AddColumn(NonDFR_Renamed, "SortOrder", each 
        if [Metric] = "Non-DFR - Flight Time - Calls Responded To (Hours:Mins)" then 1 
        else if [Metric] = "Non-DFR - Flight Time - Trainging Flights (Hours:Mins)" then 2 
        else if [Metric] = "Non-DFR - Total Flight Time (Hours:Mins)" then 3 
        else 99, Int64.Type),

    NonDFR_Converted = Table.AddColumn(NonDFR_WithOrder, "Value", each 
        let
            RawVal = [RawValue],
            MetricName = [Metric]
        in
            if Value.Is(RawVal, type datetime) or Value.Is(RawVal, type time) then
                let
                    TimeVal = if Value.Is(RawVal, type datetime) then Time.From(RawVal) else RawVal,
                    Hours = Time.Hour(TimeVal),
                    Minutes = Time.Minute(TimeVal),
                    Seconds = Time.Second(TimeVal)
                in
                    if Text.Contains(MetricName, "(Hours:Mins)") then
                        Text.PadStart(Text.From(Hours), 2, "0") & ":" & Text.PadStart(Text.From(Minutes), 2, "0")
                    else
                        Text.From(RawVal)
            else if Value.Is(RawVal, type duration) then
                if Text.Contains(MetricName, "(Hours:Mins)") then
                    let
                        TotalSeconds = Duration.TotalSeconds(RawVal),
                        TotalHours = Number.IntegerDivide(TotalSeconds, 3600),
                        RemainderMinutes = Number.IntegerDivide(Number.Mod(TotalSeconds, 3600), 60)
                    in Text.PadStart(Text.From(TotalHours), 2, "0") & ":" & Text.PadStart(Text.From(RemainderMinutes), 2, "0")
                else
                    Duration.ToText(RawVal, "h:mm:ss")
            else if Value.Is(RawVal, type number) then
                if Text.Contains(MetricName, "(Hours:Mins)") then
                    let
                        TotalSeconds = RawVal * 24 * 60 * 60,
                        Hours = Number.IntegerDivide(TotalSeconds, 3600),
                        Minutes = Number.IntegerDivide(Number.Mod(TotalSeconds, 3600), 60)
                    in Text.PadStart(Text.From(Hours), 2, "0") & ":" & Text.PadStart(Text.From(Minutes), 2, "0")
                else
                    Text.From(RawVal)
            else
                Text.From(RawVal)),
    NonDFR_Clean = Table.RemoveColumns(NonDFR_Converted, {"RawValue"}),
    NonDFR_Tagged = Table.AddColumn(NonDFR_Clean, "Source", each "Non-DFR"),

    // ─── Combine both tables & add date keys ─────────────────────────────────
    Combined = Table.Combine({DFR_Tagged, NonDFR_Tagged}),
    WithDate = Table.AddColumn(Combined, "PeriodDate", each 
        #date(2000 + Number.FromText(Text.End([Period], 2)), Number.FromText(Text.Start([Period], 2)), 1), type date),
    WithSort = Table.AddColumn(WithDate, "DateSortKey", each 
        Date.Year([PeriodDate]) * 100 + Date.Month([PeriodDate]), Int64.Type),

    // ─── Filter to Rolling 13 Months (pReportMonth-driven) ───
    EndOfWindow = Date.EndOfMonth(pReportMonth),
    StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12)),

    FilteredData = Table.SelectRows(WithSort, each [PeriodDate] >= StartOfWindow and [PeriodDate] <= EndOfWindow),

    // ─── Create totals with proper duration arithmetic ───────────────────────
    AllMetricGroups = Table.Group(FilteredData, {"Metric", "Source", "SortOrder"}, {
        {"TotalValue", each 
            let
                CurrentTable = _,
                MetricName = CurrentTable[Metric]{0}
            in
                if MetricName = "DRF - AVG Response Times - All Calls (Mins:Secs)" or
                   MetricName = "DRF - AVG Response Times - First on Scene (Mins:Secs)"
                then
                    "N/A"
                else if Text.Contains(MetricName, "(Mins:Secs)") then
                    let 
                        TimeValues = List.Transform(CurrentTable[Value], each 
                            try
                                let 
                                    TimeStr = Text.From(_),
                                    Parts = Text.Split(TimeStr, ":"),
                                    Minutes = if List.Count(Parts) >= 2 then Number.From(Parts{0}) else 0,
                                    Seconds = if List.Count(Parts) >= 2 then Number.From(Parts{1}) else 0,
                                    TotalSeconds = Minutes * 60 + Seconds
                                in TotalSeconds
                            otherwise 0),
                       
                        ValidTimeValues = List.Select(TimeValues, each _ > 0),
                        AvgSeconds = if List.Count(ValidTimeValues) > 0 then List.Average(ValidTimeValues) else 0,
                        AvgMinutes = Number.IntegerDivide(AvgSeconds, 60),
                        AvgSecs = Number.Round(Number.Mod(AvgSeconds, 60), 0)
                    in Text.From(AvgMinutes) & ":" & Text.PadStart(Text.From(AvgSecs), 2, "0")
                else if Text.Contains(MetricName, "(Hours:Mins)") and not Text.Contains(MetricName, "Secs") then
                    let 
                        TimeValues = List.Transform(CurrentTable[Value], each 
                            try
                                let 
                                    TimeStr = Text.From(_),
                                    Parts = Text.Split(TimeStr, ":"),
                                    Hours = if List.Count(Parts) >= 2 then Number.From(Parts{0}) else 0,
                                    Minutes = if List.Count(Parts) >= 2 then Number.From(Parts{1}) else 0
                                in Hours * 60 + Minutes
                            otherwise 0),
                        TotalMinutes = List.Sum(TimeValues),
                        TotalHours = Number.IntegerDivide(TotalMinutes, 60),
                        FinalMinutes = Number.Mod(TotalMinutes, 60)
                    in Text.PadStart(Text.From(TotalHours), 2, "0") & ":" & Text.PadStart(Text.From(FinalMinutes), 2, "0")
                else if Text.Contains(MetricName, "(Hours:Mins:Secs)") then
                    let 
                        TimeValues = List.Transform(CurrentTable[Value], each 
                            try
                                let 
                                    TimeStr = Text.From(_),
                                    Parts = Text.Split(TimeStr, ":"),
                                    Hours = if List.Count(Parts) >= 3 then Number.From(Parts{0}) else 0,
                                    Minutes = if List.Count(Parts) >= 3 then Number.From(Parts{1}) else 0,
                                    Seconds = if List.Count(Parts) >= 3 then Number.From(Parts{2}) else 0
                                in Hours * 3600 + Minutes * 60 + Seconds
                            otherwise 0),
                        TotalSeconds = List.Sum(TimeValues),
                        TotalHours = Number.IntegerDivide(TotalSeconds, 3600),
                        TotalMinutes = Number.IntegerDivide(Number.Mod(TotalSeconds, 3600), 60),
                        FinalSeconds = Number.Round(Number.Mod(TotalSeconds, 60), 0)
                    in Text.PadStart(Text.From(TotalHours), 2, "0") & ":" & Text.PadStart(Text.From(TotalMinutes), 2, "0") & ":" & Text.PadStart(Text.From(FinalSeconds), 2, "0")
                else
                    Text.From(Number.Round(List.Sum(List.Transform(CurrentTable[Value], each try Number.From(_) otherwise 0)), 2))
        }
    }),

    TotalsWithPeriod = Table.AddColumn(AllMetricGroups, "Period", each "Total"),
    TotalsWithValue = Table.AddColumn(TotalsWithPeriod, "Value", each [TotalValue]),
    TotalsWithDate = Table.AddColumn(TotalsWithValue, "PeriodDate", each #date(2099, 12, 31), type date),
    TotalsWithSort = Table.AddColumn(TotalsWithDate, "DateSortKey", each 999999, Int64.Type),

    // ─── Combine regular data with all totals ────────────────────────────────
    CombinedWithAllTotals = Table.Combine({FilteredData, TotalsWithSort}),

    Sorted = Table.Sort(CombinedWithAllTotals, {
        {"Source", Order.Ascending},
        {"SortOrder", Order.Ascending},
        {"DateSortKey", Order.Ascending}
    }),

    Final = Table.SelectColumns(Sorted, {"Metric", "Period", "Value", "Source", "PeriodDate", "DateSortKey", "SortOrder"})

in Final
```

---

### 7. ___Overtime_Timeoff_v3

**What changed:** Replaced `DateTime.LocalNow()` / `NowDT` / `CurrY` / `CurrM` / `EndY` / `EndM` / `StartY` / `StartM` computation block with `pReportMonth`-derived `StartDate` / `EndDate`.

**Tool:** `partition_operations` Update | **Table:** `___Overtime_Timeoff_v3`

> **NOTE:** This is the longest query. Only the rolling-window computation block changes; the rest (anchoring, CSV loading, unpivot, scaling) is preserved verbatim. The full expression is provided below.

Due to the extreme length of this query (~250 lines), apply this targeted replacement via MCP:

1. **Get** the current expression: `partition_operations -> Get -> ___Overtime_Timeoff_v3`
2. **Find** this block (lines near the top):
```m
    NowDT   = DateTime.LocalNow(),
    CurrY   = Date.Year(NowDT),
    CurrM   = Date.Month(NowDT),
    EndY    = if CurrM = 1 then CurrY - 1 else CurrY,
    EndM    = if CurrM = 1 then 12 else CurrM - 1,
    StartY  = EndY - 1,
    StartM  = EndM,

    StartDate = #date(StartY, StartM, 1),
    EndDate   = #date(EndY,   EndM,   1),
```
3. **Replace with:**
```m
    StartDate = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12)),
    EndDate   = Date.StartOfMonth(pReportMonth),
```
4. **Update** via `partition_operations -> Update` with the modified full expression.

---

### 8. ___Social_Media

**What changed:** Replaced `Date.From(DateTime.LocalNow())` / `Today` / `EndMonth` / `StartMonth` with `pReportMonth`-derived logic.

**Tool:** `partition_operations` Update | **Table:** `___Social_Media`

```m
// 🕒 2026-03-04-03-46-11
// # STACP/___Social_Media.m
// # Author: R. A. Carucci
// # Purpose: Load rolling 13-month social media post counts by platform from STACP workbook for Power BI reporting.
// Updated: pReportMonth-driven (no DateTime.LocalNow)

let
    // === SOURCE ===
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\STACP\STACP.xlsm"),
        null,
        true
    ),
    _stacp_mom_sm_Table = Source{[Item="_stacp_mom_sm", Kind="Table"]}[Data],

    // === DYNAMIC TYPES: Platform = text; everything else = Int64 ===
    ColumnNames = Table.ColumnNames(_stacp_mom_sm_Table),
    TypeList =
        List.Transform(
            ColumnNames,
            (c) => if c = "Platform" then {c, type text} else {c, Int64.Type}
        ),
    #"Changed Type" = Table.TransformColumnTypes(_stacp_mom_sm_Table, TypeList),

    // === ROLLING 13-MONTH WINDOW (pReportMonth-driven) ===
    EndOfWindow = Date.EndOfMonth(pReportMonth),
    StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12)),

    MonthDates = List.Generate(() => StartOfWindow, each _ <= EndOfWindow, each Date.AddMonths(_, 1)),
    MonthKeys  = List.Transform(MonthDates, each Date.ToText(_, "MM-yy")),

    DesiredOrder = {"Platform"} & MonthKeys & {"Total"},

    ExistingInOrder = List.Select(DesiredOrder, each List.Contains(ColumnNames, _)),

    #"Selected Columns" = Table.SelectColumns(#"Changed Type", ExistingInOrder, MissingField.Ignore)

in
    #"Selected Columns"
```

---

### 9. ___STACP_pt_1_2

**What changed:** Replaced `DateTime.LocalNow()` / `Today` / `CurrentMonth` / `CurrentYear` / `EndMonth` / `EndYear` / `StartMonth` / `StartYear` with `pReportMonth`-derived `Report_Start_Date` / `Report_End_Date`.

**Tool:** `partition_operations` Update | **Table:** `___STACP_pt_1_2`

Apply this targeted replacement:

1. **Get** the current expression: `partition_operations -> Get -> ___STACP_pt_1_2`
2. **Find** this block:
```m
    Today = DateTime.LocalNow(),
    CurrentMonth = Date.Month(Today),
    CurrentYear = Date.Year(Today),
    
    // Calculate end month (previous month)
    EndMonth = if CurrentMonth = 1 then 12 else CurrentMonth - 1,
    EndYear = if CurrentMonth = 1 then CurrentYear - 1 else CurrentYear,
    
    // Calculate start month (13 months back = same month, one year earlier)
    // For 13-month window: if end is Jan 2026, start is Jan 2025
    StartMonth = EndMonth,
    StartYear = EndYear - 1,
    
    // Generate report date range
    Report_Start_Date = #date(StartYear, StartMonth, 1),
    Report_End_Date = #date(EndYear, EndMonth, 1),
```
3. **Replace with:**
```m
    // Rolling 13-month window (pReportMonth-driven)
    Report_Start_Date = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12)),
    Report_End_Date = Date.StartOfMonth(pReportMonth),
```
4. **Update** via `partition_operations -> Update` with the modified full expression.

---

### 10. STACP_DIAGNOSTIC

**What changed:** Same pattern as STACP_pt_1_2. This is a **named expression**, not a table partition.

**Tool:** `named_expression_operations` Update | **Name:** `STACP_DIAGNOSTIC`

Apply this targeted replacement:

1. **Get** the current expression: `named_expression_operations -> Get -> STACP_DIAGNOSTIC`
2. **Find** this block:
```m
    Today = DateTime.LocalNow(),
    CurrentMonth = Date.Month(Today),
    CurrentYear = Date.Year(Today),
    
    EndMonth = if CurrentMonth = 1 then 12 else CurrentMonth - 1,
    EndYear = if CurrentMonth = 1 then CurrentYear - 1 else CurrentYear,
    
    StartMonth = EndMonth,
    StartYear = EndYear - 1,
    
    Report_Start_Date = #date(StartYear, StartMonth, 1),
    Report_End_Date = #date(EndYear, EndMonth, 1),
```
3. **Replace with:**
```m
    // Rolling 13-month window (pReportMonth-driven)
    Report_Start_Date = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12)),
    Report_End_Date = Date.StartOfMonth(pReportMonth),
```
4. Also find the **WindowInfo** diagnostic table and replace the `Today` row:
   - Old: `{"Today", DateTime.ToText(Today)}`
   - New: `{"pReportMonth", Date.ToText(pReportMonth)}`
5. **Update** via `named_expression_operations -> Update` with the modified full expression.

---

### 11. TAS_Dispatcher_Incident

**What changed:** Replaced `DateTime.LocalNow()` / `NowDT` / `CurrY` / `CurrM` / `EndY` / `EndM` with `pReportMonth`-derived `StartDate` / `EndDate`.

**Tool:** `partition_operations` Update | **Table:** `TAS_Dispatcher_Incident`

Apply this targeted replacement:

1. **Get** the current expression: `partition_operations -> Get -> TAS_Dispatcher_Incident`
2. **Find** this block (in the "Calculate rolling 13-month window" section):
```m
    NowDT = DateTime.LocalNow(),
    CurrY = Date.Year(NowDT),
    CurrM = Date.Month(NowDT),
    EndY = if CurrM = 1 then CurrY - 1 else CurrY,
    EndM = if CurrM = 1 then 12 else CurrM - 1,
    
    EndDate = #date(EndY, EndM, 1),
    StartDate = Date.AddMonths(EndDate, -12),
```
3. **Replace with:**
```m
    // Rolling 13-month window (pReportMonth-driven)
    EndDate = Date.StartOfMonth(pReportMonth),
    StartDate = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12)),
```
4. **Update** via `partition_operations -> Update` with the modified full expression.

---

### 12. ___Cost_of_Training

**What changed:** Replaced `DateTime.LocalNow()` / `Today` / `CurrentMonth` / `CurrentYear` / `EndMonth` / `EndYear` / `StartMonth` / `StartYear` with `pReportMonth`-derived `Report_Start_Date` / `Report_End_Date`.

**Tool:** `partition_operations` Update | **Table:** `___Cost_of_Training`

Apply this targeted replacement:

1. **Get** the current expression: `partition_operations -> Get -> ___Cost_of_Training`
2. **Find** this block:
```m
    // Rolling 13-month window: end = previous month, start = same month one year earlier
    Today = DateTime.LocalNow(),
    CurrentMonth = Date.Month(Today),
    CurrentYear = Date.Year(Today),
    EndMonth = if CurrentMonth = 1 then 12 else CurrentMonth - 1,
    EndYear = if CurrentMonth = 1 then CurrentYear - 1 else CurrentYear,
    StartMonth = EndMonth,
    StartYear = EndYear - 1,
    Report_Start_Date = #date(StartYear, StartMonth, 1),
    Report_End_Date = #date(EndYear, EndMonth, 1),
```
3. **Replace with:**
```m
    // Rolling 13-month window (pReportMonth-driven)
    Report_Start_Date = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12)),
    Report_End_Date = Date.StartOfMonth(pReportMonth),
```
4. **Update** via `partition_operations -> Update` with the modified full expression.

---

### 13. ___ResponseTime_AllMetrics

**What changed:** Standardized `EndDate`/`StartDate` to `EndOfWindow`/`StartOfWindow` with `Date.EndOfMonth`/`Date.StartOfMonth`.

**Tool:** `partition_operations` Update | **Table:** `___ResponseTime_AllMetrics`

Apply this targeted replacement:

1. **Get** the current expression: `partition_operations -> Get -> ___ResponseTime_AllMetrics`
2. **Find** this block (first 4 lines of the `let`):
```m
    EndDate   = DateTime.Date(pReportMonth),
    StartDate = Date.AddMonths(EndDate, -12),
    EndYM     = Date.Year(EndDate)   * 100 + Date.Month(EndDate),
    StartYM   = Date.Year(StartDate) * 100 + Date.Month(StartDate),
```
3. **Replace with:**
```m
    EndOfWindow   = Date.EndOfMonth(pReportMonth),
    StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12)),
    EndYM         = Date.Year(EndOfWindow)   * 100 + Date.Month(EndOfWindow),
    StartYM       = Date.Year(StartOfWindow) * 100 + Date.Month(StartOfWindow),
```
4. **Update** via `partition_operations -> Update` with the modified full expression.

---

### 14. ___ResponseTimeCalculator

**What changed:** Standardized `EndDate`/`StartDate` to `EndOfWindow`/`StartOfWindow`. Removed the `-1` month offset so the window includes `pReportMonth`.

**Tool:** `partition_operations` Update | **Table:** `___ResponseTimeCalculator`

Apply this targeted replacement:

1. **Get** the current expression: `partition_operations -> Get -> ___ResponseTimeCalculator`
2. **Find** this block:
```m
    EndDate   = Date.AddMonths(DateTime.Date(pReportMonth), -1),  // last complete month
    StartDate = Date.AddMonths(EndDate, -12),                      // 13 months total
    EndYM     = Date.Year(EndDate)   * 100 + Date.Month(EndDate),
    StartYM   = Date.Year(StartDate) * 100 + Date.Month(StartDate),
```
3. **Replace with:**
```m
    EndOfWindow   = Date.EndOfMonth(pReportMonth),
    StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12)),
    EndYM         = Date.Year(EndOfWindow)   * 100 + Date.Month(EndOfWindow),
    StartYM       = Date.Year(StartOfWindow) * 100 + Date.Month(StartOfWindow),
```
4. **Update** via `partition_operations -> Update` with the modified full expression.

---

### 15. ___ResponseTime_DispVsCall

**What changed:** Added 13-month rolling window filter (previously loaded all data with no date filter).

**Tool:** `partition_operations` Update | **Table:** `___ResponseTime_DispVsCall`

```m
// 🕒 2026-02-26-20-00-00
// # response_time/___ResponseTime_DispVsCall.m
// # Author: R. A. Carucci
// # Metric: Time Dispatched − Time of Call  (call processing / dispatcher queue time)
// # Source: PowerBI_Date\Backfill\response_time_all_metrics\  (all months 2024–present)
// Updated: pReportMonth-driven 13-month window added

let
    // ── Rolling 13-month window boundaries ──────────────────────────────────
    EndOfWindow   = Date.EndOfMonth(pReportMonth),
    StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12)),
    EndYM         = Date.Year(EndOfWindow)   * 100 + Date.Month(EndOfWindow),
    StartYM       = Date.Year(StartOfWindow) * 100 + Date.Month(StartOfWindow),

    // ── Load all monthly CSVs from the unified backfill folder ───────────────
    AllFiles = Folder.Files("C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\response_time_all_metrics"),

    CSVFiles = Table.SelectRows(AllFiles, each Text.EndsWith([Name], "_response_times.csv")),

    WithFullPath = Table.AddColumn(CSVFiles, "FullPath", each [Folder Path] & [Name], type text),

    LoadCSV = (filePath as text) =>
        let
            raw      = Csv.Document(File.Contents(filePath), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
            promoted = Table.PromoteHeaders(raw, [PromoteAllScalars=true])
        in promoted,

    AllData = Table.Combine(List.Transform(WithFullPath[FullPath], LoadCSV)),

    // ── Filter to this metric only ───────────────────────────────────────────
    Filtered = Table.SelectRows(AllData, each [Metric_Type] = "Time Dispatched - Time of Call"),

    // ── Apply 13-month window ────────────────────────────────────────────────
    Windowed = Table.SelectRows(Filtered, each
        let
            parts = Text.Split(Text.Trim([#"MM-YY"]), "-"),
            mm    = Number.FromText(parts{0}),
            yy    = 2000 + Number.FromText(parts{1}),
            ym    = yy * 100 + mm
        in ym >= StartYM and ym <= EndYM
    ),

    // ── Standardize column types ─────────────────────────────────────────────
    Typed = Table.TransformColumnTypes(
        Windowed,
        {
            {"Response_Type",            type text},
            {"MM-YY",                    type text},
            {"Metric_Type",              type text},
            {"First_Response_Time_MMSS", type text},
            {"Avg_Minutes",              type number},
            {"Record_Count",             Int64.Type}
        }
    ),

    // ── Build sort key from MM-YY ("01-25" → Date 2025-01-01) ────────────────
    WithYearMonth = Table.AddColumn(
        Typed,
        "YearMonth",
        each let
            parts = Text.Split(Text.Trim([#"MM-YY"]), "-"),
            mm = parts{0},
            yy = "20" & parts{1}
        in yy & "-" & Text.PadStart(mm, 2, "0"),
        type text
    ),

    WithDateKey = Table.AddColumn(
        WithYearMonth,
        "Date_Sort_Key",
        each try Date.FromText([YearMonth] & "-01") otherwise null,
        type date
    ),

    // ── Alias / compatibility columns for DAX measures ───────────────────────
    WithDate    = Table.AddColumn(WithDateKey, "Date", each [Date_Sort_Key], type date),
    WithAvgRT   = Table.AddColumn(WithDate, "Average_Response_Time", each [Avg_Minutes], type number),
    WithCategory = Table.AddColumn(WithAvgRT, "Category", each [Response_Type], type text),

    RenamedMMSS = Table.RenameColumns(WithCategory, {{"First_Response_Time_MMSS", "Response_Time_MMSS"}}),

    Result = Table.SelectColumns(
        RenamedMMSS,
        {
            "YearMonth", "Date_Sort_Key", "Date",
            "Response_Type", "Category",
            "Average_Response_Time", "Response_Time_MMSS",
            "MM-YY", "Record_Count", "Metric_Type"
        }
    )

in
    Result
```

---

### 16. ___ResponseTime_OutVsCall

**What changed:** Added 13-month rolling window filter (previously loaded all data with no date filter).

**Tool:** `partition_operations` Update | **Table:** `___ResponseTime_OutVsCall`

```m
// 🕒 2026-02-26-20-00-00
// # response_time/___ResponseTime_OutVsCall.m
// # Author: R. A. Carucci
// # Metric: Time Out − Time of Call  (total response time from first ring to officer on scene)
// # Source: PowerBI_Date\Backfill\response_time_all_metrics\  (all months 2024–present)
// Updated: pReportMonth-driven 13-month window added

let
    // ── Rolling 13-month window boundaries ──────────────────────────────────
    EndOfWindow   = Date.EndOfMonth(pReportMonth),
    StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12)),
    EndYM         = Date.Year(EndOfWindow)   * 100 + Date.Month(EndOfWindow),
    StartYM       = Date.Year(StartOfWindow) * 100 + Date.Month(StartOfWindow),

    // ── Load all monthly CSVs from the unified backfill folder ───────────────
    AllFiles = Folder.Files("C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\response_time_all_metrics"),

    CSVFiles = Table.SelectRows(AllFiles, each Text.EndsWith([Name], "_response_times.csv")),

    WithFullPath = Table.AddColumn(CSVFiles, "FullPath", each [Folder Path] & [Name], type text),

    LoadCSV = (filePath as text) =>
        let
            raw      = Csv.Document(File.Contents(filePath), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
            promoted = Table.PromoteHeaders(raw, [PromoteAllScalars=true])
        in promoted,

    AllData = Table.Combine(List.Transform(WithFullPath[FullPath], LoadCSV)),

    // ── Filter to this metric only ───────────────────────────────────────────
    Filtered = Table.SelectRows(AllData, each [Metric_Type] = "Time Out - Time of Call"),

    // ── Apply 13-month window ────────────────────────────────────────────────
    Windowed = Table.SelectRows(Filtered, each
        let
            parts = Text.Split(Text.Trim([#"MM-YY"]), "-"),
            mm    = Number.FromText(parts{0}),
            yy    = 2000 + Number.FromText(parts{1}),
            ym    = yy * 100 + mm
        in ym >= StartYM and ym <= EndYM
    ),

    // ── Standardize column types ─────────────────────────────────────────────
    Typed = Table.TransformColumnTypes(
        Windowed,
        {
            {"Response_Type",            type text},
            {"MM-YY",                    type text},
            {"Metric_Type",              type text},
            {"First_Response_Time_MMSS", type text},
            {"Avg_Minutes",              type number},
            {"Record_Count",             Int64.Type}
        }
    ),

    // ── Build sort key from MM-YY ("01-25" → Date 2025-01-01) ────────────────
    WithYearMonth = Table.AddColumn(
        Typed,
        "YearMonth",
        each let
            parts = Text.Split(Text.Trim([#"MM-YY"]), "-"),
            mm = parts{0},
            yy = "20" & parts{1}
        in yy & "-" & Text.PadStart(mm, 2, "0"),
        type text
    ),

    WithDateKey = Table.AddColumn(
        WithYearMonth,
        "Date_Sort_Key",
        each try Date.FromText([YearMonth] & "-01") otherwise null,
        type date
    ),

    // ── Alias / compatibility columns for DAX measures ───────────────────────
    WithDate    = Table.AddColumn(WithDateKey, "Date", each [Date_Sort_Key], type date),
    WithAvgRT   = Table.AddColumn(WithDate, "Average_Response_Time", each [Avg_Minutes], type number),
    WithCategory = Table.AddColumn(WithAvgRT, "Category", each [Response_Type], type text),

    RenamedMMSS = Table.RenameColumns(WithCategory, {{"First_Response_Time_MMSS", "Response_Time_MMSS"}}),

    Result = Table.SelectColumns(
        RenamedMMSS,
        {
            "YearMonth", "Date_Sort_Key", "Date",
            "Response_Type", "Category",
            "Average_Response_Time", "Response_Time_MMSS",
            "MM-YY", "Record_Count", "Metric_Type"
        }
    )

in
    Result
```

---

## Post-Update Verification

After all 16 queries are updated, run these DAX queries to verify window boundaries:

```dax
EVALUATE
ROW(
    "DimMonth_Min", MINX('___DimMonth', [MonthStart]),
    "DimMonth_Max", MAXX('___DimMonth', [MonthStart]),
    "DimMonth_Count", COUNTROWS('___DimMonth')
)
```

Expected: Min = 2025-02-01, Max = 2026-02-01, Count = 13

```dax
EVALUATE
ROW(
    "RT_AllMetrics_MinYM", MINX('___ResponseTime_AllMetrics', [YearMonth]),
    "RT_AllMetrics_MaxYM", MAXX('___ResponseTime_AllMetrics', [YearMonth]),
    "RT_AllMetrics_Rows", COUNTROWS('___ResponseTime_AllMetrics')
)
```

```dax
EVALUATE
ROW(
    "Detectives_MinDate", MINX('___Detectives', [Date]),
    "Detectives_MaxDate", MAXX('___Detectives', [Date])
)
```

## Rollback

If any query fails or produces incorrect results:

1. **Close** the `.pbix` WITHOUT saving.
2. **Reopen** from the pre-update backup.
3. The original `DateTime.LocalNow()` expressions will be intact.

Alternatively, use `partition_operations -> Get` to retrieve any query's current expression before updating, and store it as a backup.

---

## Summary Checklist

| # | Query | Type | Status |
|---|-------|------|--------|
| 1 | `___DimMonth` | Full replace | ☐ |
| 2 | `___Arrest_Categories` | Full replace | ☐ |
| 3 | `___CSB_Monthly` | Full replace | ☐ |
| 4 | `___Detectives` | Full replace | ☐ |
| 5 | `___Det_case_dispositions_clearance` | Full replace | ☐ |
| 6 | `___Drone` | Full replace | ☐ |
| 7 | `___Overtime_Timeoff_v3` | FIND/REPLACE | ☐ |
| 8 | `___Social_Media` | Full replace | ☐ |
| 9 | `___STACP_pt_1_2` | FIND/REPLACE | ☐ |
| 10 | `STACP_DIAGNOSTIC` | FIND/REPLACE (named expr) | ☐ |
| 11 | `TAS_Dispatcher_Incident` | FIND/REPLACE | ☐ |
| 12 | `___Cost_of_Training` | FIND/REPLACE | ☐ |
| 13 | `___ResponseTime_AllMetrics` | FIND/REPLACE | ☐ |
| 14 | `___ResponseTimeCalculator` | FIND/REPLACE | ☐ |
| 15 | `___ResponseTime_DispVsCall` | Full replace | ☐ |
| 16 | `___ResponseTime_OutVsCall` | Full replace | ☐ |
| 17 | `___Arrest_13Month` | NEW table (Create) | ☐ |

---

## Appendix: New Query -- ___Arrest_13Month

This is a **new table** (not an update to an existing query). It provides a rolling 13-month arrest dataset from raw Lawsoft monthly exports.

**Tool:** `table_operations` Create (or import via Tabular Editor / Power Query Editor)

**Source:** `05_EXPORTS\_Arrest\monthly\YYYY\*_LAWSOFT_ARREST*.xlsx`

**Already uses `pReportMonth`** -- no migration needed. The full M expression is in `m_code/arrests/___Arrest_13Month.m`.

### Key features:
- Dynamic file discovery across all year subdirectories under `monthly\`
- Case-insensitive file matching (handles `ARREST`, `ARRESTS`, `arrest`)
- `EndOfWindow = Date.EndOfMonth(pReportMonth)`, `StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12))`
- Charge categorization: Assault, Theft, Burglary, Robbery, Warrant, DWI, Drug Related, Weapons, Other
- Simplified home categorization: Local (Hackensack/07601/07602) vs Out-of-Town
- Period columns: `MM_YY`, `MonthSort`, `MonthLabel`, `ArrestMonth` for visuals
