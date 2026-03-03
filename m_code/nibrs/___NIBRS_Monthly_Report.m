// 🕒 2026-02-20-23-48-50
// # nibrs/___NIBRS_Monthly_Report.m
// # Author: R. A. Carucci
// # Purpose: Load NIBRS monthly crime statistics with clearance rate calculations.

let
    // Load Excel data
    Source = Excel.Workbook(
        File.Contents(
            "C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\NIBRS\NIBRS_Monthly_Report.xlsx"
        ),
        null,
        true
    ),
    
    NIBRS_Table = Source{[Item="NIBRS_Monthly_Report", Kind="Table"]}[Data],
    
    // Get available month columns dynamically
    AvailableColumns = Table.ColumnNames(NIBRS_Table),
    MonthColumns = List.Select(AvailableColumns, each _ <> "Clearance and Crime Reporting Metrics"),
    
    // Transform all month columns to numbers
    ColumnTransformations = List.Transform(MonthColumns, each {_, type number}),
    
    ChangedType = Table.TransformColumnTypes(
        NIBRS_Table,
        List.Combine({
            {{"Clearance and Crime Reporting Metrics", type text}},
            ColumnTransformations
        })
    ),
    
    // Unpivot all month columns
    Unpivoted = Table.UnpivotOtherColumns(
        ChangedType,
        {"Clearance and Crime Reporting Metrics"},
        "Month",
        "MetricValue"
    ),
    
    // Parse dates
    WithParsedDates = Table.AddColumn(
        Unpivoted,
        "MonthDate",
        each 
            let
                monthNum = Number.FromText(Text.BeforeDelimiter([Month], "-")),
                yearSuffix = Text.AfterDelimiter([Month], "-"),
                fullYear = if Text.Length(yearSuffix) = 2 then 
                    2000 + Number.FromText(yearSuffix) 
                else 
                    Number.FromText(yearSuffix)
            in
#date(fullYear, monthNum, 1),
        type date
    ),
    
    // Get exactly 13 most recent months
    AllDates = List.Sort(List.Distinct(WithParsedDates[MonthDate])),
    Last13Dates = List.LastN(AllDates, 13),
    
    // Filter to exactly 13 most recent months
    Rolling13Months = Table.SelectRows(
        WithParsedDates,
        each List.Contains(Last13Dates, [MonthDate])
    ),
    
    // Add display formatting
    WithDisplayFormatting = Table.AddColumn(
        Rolling13Months,
        "DisplayValue",
        each
            if [#"Clearance and Crime Reporting Metrics"] = "NIBRS Clearance Rate"
            then Number.ToText([MetricValue] * 100, "0.0") & "%"
            else Number.ToText([MetricValue], "0"),
        type text
    ),
    
    // Add MonthYear_Display for chart labels
    WithDisplayLabels = Table.AddColumn(
        WithDisplayFormatting,
        "MonthYear_Display",
        each Date.ToText([MonthDate], "MM-yy"),
        type text
    ),
    
    // Add sort key for proper chronological ordering
    WithSortKey = Table.AddColumn(
        WithDisplayLabels,
        "SortKey",
        each
            Date.Year([MonthDate]) * 10000
            + Date.Month([MonthDate]) * 100
            + Date.Day([MonthDate]),
        Int64.Type
    ),
    
    // Sort chronologically
    SortedData = Table.Sort(WithSortKey, {{"SortKey", Order.Ascending}}),
    
    // Add metadata for debugging
    WithMetadata = Table.AddColumn(
        SortedData,
        "DateRange",
        each 
            let
                FirstDate = List.Min(Last13Dates),
                LastDate = List.Max(Last13Dates)
            in
                Date.ToText(FirstDate, "MM-yy") & " to " & Date.ToText(LastDate, "MM-yy"),
        type text
    ),
    
    // Add clearance rate category
    FinalResult = Table.AddColumn(
        WithMetadata,
        "Clearance Rate",
        each
            if [#"Clearance and Crime Reporting Metrics"] = "NIBRS Clearance Rate" then
                if [MetricValue] >= 0.35 then "High (35%+)"
                else if [MetricValue] >= 0.25 then "Medium (25-34%)"
                else if [MetricValue] >= 0.15 then "Low (15-24%)"
                else "Very Low (<15%)"
            else "N/A",
        type text
    )

in
    FinalResult
