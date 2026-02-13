Query Name: ___Detectives
M Code:
// 🕒 2025-08-19-15-35-00
// Project: Detectives_Analysis/detectives_comprehensive_connection.m
// Author: R. A. Carucci
// Purpose: Connect to ALL Detectives cases from OneDrive shared folder for comprehensive Power BI report with rolling 13-month data window

let
    FilePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Detectives\detectives_monthly.xlsx",
    
    Source = Excel.Workbook(File.Contents(FilePath), null, true),
    
    MoM_Det_Table = Source{[Item = "_mom_det", Kind = "Table"]}[Data],
    
    DetectedTypes = Table.TransformColumnTypes(MoM_Det_Table, {}, "en-US"),
    
    RemovedEmptyRows = Table.SelectRows(DetectedTypes, each not List.IsEmpty(List.RemoveMatchingItems(Record.FieldValues(_), {"", null}))),
    
    ColumnNames = Table.ColumnNames(RemovedEmptyRows),
    FirstColumn = ColumnNames{0},
    
    FilteredToActiveCases = Table.SelectRows(RemovedEmptyRows, each 
        let 
            CategoryName = Record.Field(_, FirstColumn),
            RowValues = List.Skip(Record.FieldValues(_), 1),
            HasActivity = List.AnyTrue(List.Transform(RowValues, each try (_ <> null and _ <> "" and Number.From(_) > 0) otherwise false))
        in HasActivity),
    
    UnpivotedData = Table.UnpivotOtherColumns(FilteredToActiveCases, {FirstColumn}, "Month_MM_YY", "Value"),
    
    AddedDateInfo = Table.AddColumn(UnpivotedData, "Date", each 
        let 
            MonthText = [Month_MM_YY],
            Parts = Text.Split(MonthText, "-"),
            MonthNum = if List.Count(Parts) >= 1 then Parts{0} else "01",
            YearNum = if List.Count(Parts) >= 2 then Parts{1} else "25",
            FullYear = if Value.FromText(YearNum) >= 50 then 1900 + Value.FromText(YearNum) else 2000 + Value.FromText(YearNum),
            DateValue = try #date(FullYear, Value.FromText(MonthNum), 1) otherwise null
        in DateValue, type date),
    
    AddedSortOrder = Table.AddColumn(AddedDateInfo, "Month_Sort_Order", each 
        if [Date] <> null then Date.Year([Date]) * 100 + Date.Month([Date]) else null, Int64.Type),
    
    // Rolling 13-Month Logic Implementation
    // Step 1: Determine End Date - Previous month (complete data only)
    CurrentDate = DateTime.LocalNow(),
    CurrentMonthStart = Date.StartOfMonth(Date.From(CurrentDate)),
    EndFilterDate = Date.AddMonths(CurrentMonthStart, -1),
    
    // Step 2: Determine Start Date - 12 months before End Date (13 total months)
    StartFilterDate = Date.AddMonths(EndFilterDate, -12),
    
    // Step 3: Data Window - Continuous 13-month period
    // Format: Start Month/Year - End Month/Year
    ReportingPeriod = Date.ToText(StartFilterDate, "MM/yy") & " - " & Date.ToText(EndFilterDate, "MM/yy"),
    
    // Apply 13-month rolling window filter
    FilteredMonths = Table.SelectRows(AddedSortOrder, each 
        [Date] <> null and 
        [Date] >= StartFilterDate and 
        [Date] <= EndFilterDate),
    
    // Add reporting period metadata for verification
    AddedReportingMeta = Table.AddColumn(FilteredMonths, "ReportingPeriod", each ReportingPeriod, type text),
    AddedMonthCount = Table.AddColumn(AddedReportingMeta, "MonthsIncluded", each 
        let
            UniqueMonths = Table.Group(FilteredMonths, {"Date"}, {{"Count", each Table.RowCount(_), type number}}),
            MonthCount = Table.RowCount(UniqueMonths)
        in MonthCount, type number),
    
    AddedCaseType = Table.AddColumn(AddedMonthCount, "Case_Type", each 
        let 
            CategoryName = Record.Field(_, FirstColumn),
            HighImpactCategories = {"ABC Investigation(s)", "Background Check(s)", "Firearm Background Check(s)", "Criminal Mischief", "Fraud", "Generated Complaint(s)", "BWC Review(s)", "Aggravated Assault", "Animal Cruelty", "Burglary - Auto", "Domestic Violence", "Drug Investigation(s)", "Harassment", "Motor Vehicle Theft"},
            CaseType = if List.Contains(HighImpactCategories, CategoryName) then "High Impact" else "Administrative"
        in CaseType, type text),
    
    FinalDataTypes = Table.TransformColumnTypes(AddedCaseType, {{FirstColumn, type text}, {"Month_MM_YY", type text}, {"Value", type number}, {"Date", type date}, {"Month_Sort_Order", Int64.Type}, {"Case_Type", type text}}),
    
    AddedTitle = Table.AddColumn(FinalDataTypes, "ReportTitle", each "Detective Division - Comprehensive Case Analysis", type text),
    
    AddedSubtitle = Table.AddColumn(AddedTitle, "ReportSubtitle", each 
        let 
            StartMonth = Date.ToText(StartFilterDate, "MMMM yyyy"),
            EndMonth = Date.ToText(EndFilterDate, "MMMM yyyy"),
            RefreshDate = DateTime.ToText(DateTime.LocalNow(), "MM/dd/yyyy hh:mm tt"),
            TodaysDate = Date.ToText(Date.From(DateTime.LocalNow()), "MMMM dd, yyyy")
        in "Rolling 13-Month Period: " & StartMonth & " - " & EndMonth & " | Today: " & TodaysDate & " | Updated: " & RefreshDate, type text),
    
    AddedRefreshTime = Table.AddColumn(AddedSubtitle, "DataRefreshTime", each DateTime.LocalNow(), type datetime)

in AddedRefreshTime


Query Name: ___Det_case_dispositions_clearance
M Code:
// Det_case_dispositions_clearance — CCD/_CCD_MOM
// Fixed row order • Robust % normalization • Rolling 13-Month window

let
    // --- Load table ---------------------------------------------------------
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Detectives\detectives_monthly.xlsx"),
        null, true
    ),
    CCD_Table = Source{[Item="_CCD_MOM", Kind="Table"]}[Data],

    // --- Required order (exact labels) -------------------------------------
    RequiredOrder = {
        "Active / Administratively Closed",
        "Arrest",
        "Complaint Signed",
        "Ex Cleared / Closed",
        "Juvenile Complaint",
        "Stationhouse Adjustment",
        "TOT DCP&P",
        "Unfounded / Closed",
        "Monthly Bureau Case Clearance %"
    },

    // --- Shape & keep only the required labels -----------------------------
    ColNames        = Table.ColumnNames(CCD_Table),
    FirstColumnName = ColNames{0},
    MonthColumns    = List.Skip(ColNames, 1),

    KeptRows = Table.SelectRows(
        CCD_Table,
        (r) => List.Contains(RequiredOrder, Record.Field(r, FirstColumnName))
    ),

    // Add Row_Sort and order rows to lock display sequence
    WithRowSort = Table.AddColumn(
        KeptRows, "Row_Sort",
        each List.PositionOf(RequiredOrder, Record.Field(_, FirstColumnName)),
        Int64.Type
    ),
    OrderedRows = Table.Sort(WithRowSort, {{"Row_Sort", Order.Ascending}}),

    // Wide types: keep months as 'any' for now (we'll normalize after unpivot)
    TypedWide = Table.TransformColumnTypes(
        OrderedRows,
        {{FirstColumnName, type text}} & List.Transform(MonthColumns, each {_, type any})
    ),

    // Flag the percent row
    MarkPercentRow = Table.AddColumn(
        TypedWide, "Is_Percent",
        each Record.Field(_, FirstColumnName) = "Monthly Bureau Case Clearance %",
        type logical
    ),

    // --- Unpivot for tidy format -------------------------------------------
    Unpivoted = Table.UnpivotOtherColumns(
        MarkPercentRow,
        {FirstColumnName, "Row_Sort", "Is_Percent"},
        "Month",
        "ValueRaw"
    ),

    // --- Robust normalization ----------------------------------------------
    // If Is_Percent:
    //   - "50%" -> 0.50
    //   - 50    -> 0.50
    //   - 0.50  -> 0.50
    // Else:
    //   - counts as numbers
    Normalized = Table.AddColumn(
        Unpivoted, "Value",
        each
            let v = [ValueRaw] in
            if [Is_Percent] then
                if Value.Is(v, type text) then
                    let
                        s   = Text.Trim(v),
                        hasPct = Text.Contains(s, "%"),
                        n0  = try Number.From(Text.Replace(s, "%", "")) otherwise null,
                        n   = if n0 = null then null
                              else if hasPct then n0 / 100
                              else if n0 > 1 then n0 / 100 else n0
                    in  n
                else
                    let
                        n0 = try Number.From(v) otherwise null,
                        n  = if n0 = null then null
                             else if n0 > 1 then n0 / 100 else n0
                    in  n
            else
                try Number.From(v) otherwise null,
        type number
    ),
    Cleaned = Table.RemoveColumns(Normalized, {"ValueRaw"}),

    // --- Date helpers from "MM-YY" -----------------------------------------
    WithDate = Table.AddColumn(Cleaned, "Date", each
        let
            mTxt = [Month],
            mNum = try Value.FromText(Text.Start(mTxt, 2)) otherwise null,
            y2   = try Value.FromText(Text.End(mTxt, 2)) otherwise null,
            y4   = if y2 = null then null else if y2 >= 50 then 1900 + y2 else 2000 + y2
        in
            if mNum = null or y4 = null then null else #date(y4, mNum, 1),
        type date
    ),

    WithMonthYear = Table.AddColumn(WithDate, "Month_Year", each if [Date] = null then null else Date.MonthName([Date]) & " " & Text.From(Date.Year([Date])), type text),
    WithSortOrder = Table.AddColumn(WithMonthYear, "Sort_Order", each if [Date] = null then null else Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type),
    WithAbbrev    = Table.AddColumn(WithSortOrder, "Month_Abbrev", each if [Date] = null then null else Text.PadStart(Text.From(Date.Month([Date])), 2, "0") & "-" & Text.End(Text.From(Date.Year([Date])), 2), type text),

    // Optional grouping
    WithDispCat = Table.AddColumn(WithAbbrev, "Disposition_Category", each
        let disp = Record.Field(_, FirstColumnName)
        in
            if Text.Contains(disp, "Active") or Text.Contains(disp, "Administratively") then "Open Cases"
            else if Text.Contains(disp, "Arrest") or Text.Contains(disp, "Complaint") then "Prosecuted"
            else if Text.Contains(disp, "Cleared") or Text.Contains(disp, "Unfounded") then "Cleared"
            else if disp = "Monthly Bureau Case Clearance %" then "Performance Metric"
            else "Other",
        type text
    ),

    // --- Rolling 13-Month window (exclude current month) -------------------
    CurrentDate     = Date.From(DateTime.LocalNow()),
    EndFilterDate   = Date.AddMonths(Date.StartOfMonth(CurrentDate), -1),
    StartFilterDate = Date.AddMonths(EndFilterDate, -12),

    FilteredMonths = Table.SelectRows(
        WithDispCat,
        each [Date] <> null and [Date] >= StartFilterDate and [Date] <= EndFilterDate
    ),

    // --- Final types --------------------------------------------------------
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