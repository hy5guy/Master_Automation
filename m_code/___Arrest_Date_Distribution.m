// ___Arrest_Date_Distribution
// 🕒 2025-01-05-14-45-00
// Project: Arrest_Analysis/Date_Distribution
// Author: R. A. Carucci
// Purpose: Show what arrest dates are actually in the source data

let
    // Load the latest Power BI ready file (same as main query)
    FolderFiles = Folder.Files("C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\ARREST_DATA\Power_BI"),
    
    PowerBIFiles = Table.SelectRows(
        FolderFiles,
        each [Extension] = ".xlsx" and Text.Contains([Name], "PowerBI_Ready")
    ),
    
    Sorted = Table.Sort(PowerBIFiles, {{"Date modified", Order.Descending}}),
    
    Source = if Table.RowCount(Sorted) > 0 then
        Excel.Workbook(Sorted{0}[Content], null, true){0}[Data]
    else
        error "No Power BI ready files found",

    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    
    // Handle different date column names
    SafeRename = if Table.HasColumns(Headers, "Arrest Date") then
        Table.RenameColumns(Headers, {{"Arrest Date", "ArrestDate"}})
    else if Table.HasColumns(Headers, "Arrest_Date") then
        Table.RenameColumns(Headers, {{"Arrest_Date", "ArrestDate"}})
    else if Table.HasColumns(Headers, "ArrestDate") then
        Headers
    else
        error "Arrest Date column not found",

    // Parse dates
    ToDate = (x) => if x = null or x = "" then
        null
    else
        try Date.From(x) otherwise try Date.FromText(Text.From(x)) otherwise null,
    
    // Add parsed date column
    WithParsedDates = Table.AddColumn(
        SafeRename,
        "Parsed_Date",
        each ToDate([ArrestDate]),
        type nullable date
    ),
    
    // Add year and month
    WithDateParts = Table.AddColumn(
        Table.AddColumn(
            WithParsedDates,
            "Year",
            each try Date.Year([Parsed_Date]) otherwise null,
            type nullable number
        ),
        "Month",
        each try Date.Month([Parsed_Date]) otherwise null,
        type nullable number
    ),
    
    // Add month name for readability
    WithMonthName = Table.AddColumn(
        WithDateParts,
        "Month_Name",
        each if [Month] <> null then
            Date.MonthName(#date([Year], [Month], 1))
        else
            null,
        type nullable text
    ),
    
    // Group by year and month to see distribution
    DateDistribution = Table.Group(
        WithMonthName,
        {"Year", "Month", "Month_Name"},
        {{"Arrest_Count", each Table.RowCount(_), Int64.Type}}
    ),
    
    // Sort by year and month descending to see most recent first
    Sorted_Distribution = Table.Sort(
        DateDistribution,
        {{"Year", Order.Descending}, {"Month", Order.Descending}}
    ),
    
    // Add formatted period column
    WithPeriod = Table.AddColumn(
        Sorted_Distribution,
        "Period",
        each if [Year] <> null and [Month_Name] <> null then
            [Month_Name] & " " & Text.From([Year])
        else
            "Invalid Date",
        type text
    ),
    
    // Reorder columns for better readability
    Reordered = Table.SelectColumns(
        WithPeriod,
        {"Period", "Year", "Month", "Month_Name", "Arrest_Count"}
    )

in
    Reordered
