// 🕒 2026-02-20-23-48-50
// # stacp/STACP_DIAGNOSTIC.m
// # Author: R. A. Carucci
// # Purpose: Diagnostic query to verify STACP column detection and 13-month window logic.

/* =================================================================
   STACP DIAGNOSTIC QUERY
   Purpose: Verify column detection and window filtering logic
   Use: Create this as a NEW query in Power BI to diagnose the issue
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
    // DIAGNOSTIC: Show window dates
    // =================================================================
    WindowInfo = #table(
        {"Parameter", "Value"},
        {
            {"Today", DateTime.ToText(Today)},
            {"Report_Start_Date", Date.ToText(Report_Start_Date)},
            {"Report_End_Date", Date.ToText(Report_End_Date)},
            {"Start Period (MM-YY)", Text.PadStart(Text.From(StartMonth), 2, "0") & "-" & Text.End(Text.From(StartYear), 2)},
            {"End Period (MM-YY)", Text.PadStart(Text.From(EndMonth), 2, "0") & "-" & Text.End(Text.From(EndYear), 2)}
        }
    ),
    
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
    // DIAGNOSTIC: Show all columns
    // =================================================================
    AllColumnsTable = #table(
        {"Column_Index", "Column_Name", "Has_Hyphen", "Length"},
        List.Transform(
            List.Positions(ColumnNames),
            each {
                _ + 1,
                ColumnNames{_},
                Text.Contains(ColumnNames{_}, "-"),
                Text.Length(ColumnNames{_})
            }
        )
    ),
    
    // =================================================================
    // DYNAMIC MONTH COLUMN DETECTION
    // =================================================================
    AllMonthColumns = List.Select(ColumnNames, each 
        let
            ColumnName = _,
            Parts = Text.Split(ColumnName, "-"),
            IsDatePattern = List.Count(Parts) = 2,
            MonthPart = if IsDatePattern then Parts{0} else "",
            IsMonthValid = Text.Length(MonthPart) >= 1 and Text.Length(MonthPart) <= 2 and 
                           (try Number.From(MonthPart) >= 1 and Number.From(MonthPart) <= 12 otherwise false),
            YearPart = if IsDatePattern then Parts{1} else "",
            IsYearValid = Text.Length(YearPart) = 2 and (try Number.From(YearPart) otherwise -1) >= 0,
            IsNotFirstColumn = ColumnName <> FirstColumnName
        in
            IsDatePattern and IsMonthValid and IsYearValid and IsNotFirstColumn
    ),
    
    // =================================================================
    // DIAGNOSTIC: Show detected month columns
    // =================================================================
    DetectedMonthsTable = #table(
        {"Column_Name", "Month_Num", "Year_Num", "Column_Date", "In_Window"},
        List.Transform(
            AllMonthColumns,
            each 
                let
                    Parts = Text.Split(_, "-"),
                    MonthNum = Number.From(Parts{0}),
                    YearNum = Number.From("20" & Parts{1}),
                    ColumnDate = #date(YearNum, MonthNum, 1),
                    IsWithinWindow = ColumnDate >= Report_Start_Date and ColumnDate <= Report_End_Date
                in
                    {_, MonthNum, YearNum, ColumnDate, IsWithinWindow}
        )
    ),
    
    // Filter to 13-month window
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
    
    // =================================================================
    // DIAGNOSTIC: Summary table
    // =================================================================
    DiagnosticSummary = #table(
        {"Metric", "Count", "Details"},
        {
            {"Total Columns in MoMTotals", List.Count(ColumnNames), Text.Combine(ColumnNames, ", ")},
            {"Detected Month Columns", List.Count(AllMonthColumns), Text.Combine(AllMonthColumns, ", ")},
            {"Columns in 13-Month Window", List.Count(FilteredMonthColumns), Text.Combine(FilteredMonthColumns, ", ")},
            {"First Column Name", 1, FirstColumnName}
        }
    )

in
    DiagnosticSummary
