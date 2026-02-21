// 🕒 2026-02-20-23-48-50
// # stacp/___STACP_pt_1_2.m
// # Author: R. A. Carucci
// # Purpose: Load STACP monthly tracked items with rolling 13-month window and dynamic column detection.

/* =================================================================
   STACP HIGH ACTIVITY - FUTURE-PROOF VERSION
   Updated: 2026-02-13
   Changes: Added dynamic year detection and updated window logic
   ================================================================= */

let
    // =================================================================
    // ROLLING 13-MONTH WINDOW CALCULATION
    // =================================================================
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
    
    // =================================================================
    // DATA SOURCE LOADING
    // =================================================================
    Source = Excel.Workbook(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\STACP\STACP.xlsm")),
    MoMTotals_Sheet = Source{[Item="MoMTotals",Kind="Sheet"]}[Data],
    
    // Promote headers
    PromotedHeaders = Table.PromoteHeaders(MoMTotals_Sheet, [PromoteAllScalars=true]),
    ColumnNames = Table.ColumnNames(PromotedHeaders),
    FirstColumnName = if List.IsEmpty(ColumnNames) then "Tracked Items " else ColumnNames{0},
    
    // =================================================================
    // DYNAMIC MONTH COLUMN DETECTION (HANDLES BOTH "3-25" AND "03-25")
    // =================================================================
    AllMonthColumns = List.Select(ColumnNames, each 
        let
            ColumnName = _,
            Parts = Text.Split(ColumnName, "-"),
            // Check if it has a hyphen and exactly two parts (M-YY or MM-YY)
            IsDatePattern = List.Count(Parts) = 2,
            // Check if first part is a 1-2 digit month (1-12)
            MonthPart = if IsDatePattern then Parts{0} else "",
            IsMonthValid = Text.Length(MonthPart) >= 1 and Text.Length(MonthPart) <= 2 and 
                           (try Number.From(MonthPart) >= 1 and Number.From(MonthPart) <= 12 otherwise false),
            // Check if second part is a 2-digit number (The Year)
            YearPart = if IsDatePattern then Parts{1} else "",
            IsYearValid = Text.Length(YearPart) = 2 and (try Number.From(YearPart) otherwise -1) >= 0,
            IsNotFirstColumn = ColumnName <> FirstColumnName
        in
            IsDatePattern and IsMonthValid and IsYearValid and IsNotFirstColumn
    ),
    
    // Filter month columns to only include those within the rolling 13-month window
    FilteredMonthColumns = List.Select(AllMonthColumns, each
        let
            ColumnName = _,
            Parts = Text.Split(ColumnName, "-"),
            MonthNum = Number.From(Parts{0}),
            YearNum = Number.From("20" & Parts{1}),
            ColumnDate = #date(YearNum, MonthNum, 1),
            IsWithinWindow = ColumnDate >= Report_Start_Date and ColumnDate <= Report_End_Date
        in
            IsWithinWindow
    ),
    
    // Fallback logic
    FinalMonthColumns = if List.IsEmpty(FilteredMonthColumns) then AllMonthColumns else FilteredMonthColumns,
    
    ColumnsToSelect = List.Combine({{FirstColumnName}, FinalMonthColumns}),
    
    SelectedColumns = try Table.SelectColumns(PromotedHeaders, ColumnsToSelect) otherwise PromotedHeaders,
    
    // Unpivot month columns
    UnpivotedData = Table.UnpivotOtherColumns(SelectedColumns, {FirstColumnName}, "Month", "Value"),
    
    // Convert Value to number
    ConvertedValues = Table.TransformColumns(UnpivotedData, {
        {"Value", each if _ = null then 0 else try Number.From(_) otherwise 0, type number}
    }),
    
    // Add Metadata Columns
    AddedColumns = Table.AddColumn(ConvertedValues, "Source_Category", each "STACP Core", type text),
    AddedActivityLevel = Table.AddColumn(AddedColumns, "Activity_Level", each "High Activity", type text),
    
    // Normalize Month format (MM-YY) - handles both "3-25" and "03-25" formats
    AddedNormalizedMonth = Table.AddColumn(AddedActivityLevel, "Month_MM_YY", each
        let
            Parts = Text.Split([Month], "-"),
            MonthPart = if List.Count(Parts) >= 1 then Parts{0} else "01",
            YearPart = if List.Count(Parts) >= 2 then Parts{1} else "25",
            Result = Text.PadStart(MonthPart, 2, "0") & "-" & YearPart
        in
            Result, type text
    ),
    
    // Add Date Sort Key (YYYYMMDD)
    AddedDateSortKey = Table.AddColumn(AddedNormalizedMonth, "Date_Sort_Key", each
        let
            Parts = Text.Split([Month_MM_YY], "-"),
            SortKey = "20" & Parts{1} & Parts{0} & "01"
        in
            SortKey, type text
    ),
    
    // Add Report Window Info
    AddedReportDates = Table.AddColumn(AddedDateSortKey, "Report_Start_Date", each Date.ToText(Report_Start_Date, "yyyy-MM-dd"), type text),
    AddedReportEndDate = Table.AddColumn(AddedReportDates, "Report_End_Date", each Date.ToText(Report_End_Date, "yyyy-MM-dd"), type text),
    AddedWindowFilter = Table.AddColumn(AddedReportEndDate, "Is_Within_Window", each true, type logical),
    
    // Calculate Totals per Item (for sorting)
    AddedTotalActivity = Table.Group(AddedWindowFilter, {FirstColumnName}, {{"Total_Activity", each List.Sum([Value]), type number}}),
    JoinedBack = Table.Join(AddedWindowFilter, {FirstColumnName}, AddedTotalActivity, {FirstColumnName}),
    
    // Final Sorting
    SortedFinal = Table.Sort(JoinedBack, {
        {"Total_Activity", Order.Descending},
        {FirstColumnName, Order.Ascending},
        {"Date_Sort_Key", Order.Ascending}
    })

in
    SortedFinal
