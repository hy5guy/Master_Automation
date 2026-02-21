// 🕒 2026-02-17-14-30-00
// # Master_Automation/m_code/___Top_5_Arrests_DIAGNOSTIC.m
// # Author: R. A. Carucci
// # Purpose: Diagnostic query to identify where arrest data is lost in pipeline.

let
    // ═══ DIAGNOSTIC: Check folder and files ═══════════════════════
    FolderFiles = Folder.Files("C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\ARREST_DATA\Power_BI"),
    
    PowerBIFiles = Table.SelectRows(
        FolderFiles,
        each [Extension] = ".xlsx" and Text.Contains([Name], "PowerBI_Ready")
    ),
    
    // DIAGNOSTIC INFO: How many PowerBI_Ready files found?
    FileCount = Table.RowCount(PowerBIFiles),
    
    Sorted = Table.Sort(PowerBIFiles, {{"Date modified", Order.Descending}}),
    
    // DIAGNOSTIC INFO: Latest file name and date
    LatestFileName = if FileCount > 0 then Sorted{0}[Name] else "NO FILES FOUND",
    LatestFileDate = if FileCount > 0 then Sorted{0}[Date modified] else null,

    // Load the latest file
    Source = if FileCount > 0 then
        Excel.Workbook(Sorted{0}[Content], null, true){0}[Data]
    else
        error "No Power BI ready files found",

    // ═══ DIAGNOSTIC: Check raw data ═══════════════════════════════
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    
    // DIAGNOSTIC INFO: Total rows BEFORE any filtering
    TotalRowsBeforeFilter = Table.RowCount(Headers),
    
    // DIAGNOSTIC INFO: What columns are actually in the data?
    ActualColumns = Table.ColumnNames(Headers),

    // Check if columns exist and rename safely
    SafeRename = if Table.HasColumns(Headers, "Officer of Record") then
        Table.RenameColumns(Headers, {{"Officer of Record", "OfficerOfRecord"}})
    else if Table.HasColumns(Headers, "Officer_of_Record") then
        Table.RenameColumns(Headers, {{"Officer_of_Record", "OfficerOfRecord"}})
    else if Table.HasColumns(Headers, "OfficerOfRecord") then
        Headers
    else
        error "Officer column not found in data",

    SafeRename2 = if Table.HasColumns(SafeRename, "Arrest Date") then
        Table.RenameColumns(SafeRename, {{"Arrest Date", "ArrestDate"}})
    else if Table.HasColumns(SafeRename, "Arrest_Date") then
        Table.RenameColumns(SafeRename, {{"Arrest_Date", "ArrestDate"}})
    else if Table.HasColumns(SafeRename, "ArrestDate") then
        SafeRename
    else
        error "Arrest Date column not found in data",

    // ═══ DIAGNOSTIC: Check date filtering ═════════════════════════
    Current = Date.From(DateTime.LocalNow()),
    PreviousMonth = Date.AddMonths(Current, -1),
    TargetYear = Date.Year(PreviousMonth),
    TargetMonth = Date.Month(PreviousMonth),
    MonthYearDisplay = Date.MonthName(PreviousMonth) & " " & Text.From(TargetYear),
    
    // DIAGNOSTIC INFO: What dates are we looking for?
    DiagnosticInfo = #table(
        {"Metric", "Value"},
        {
            {"Latest File", LatestFileName},
            {"File Modified Date", Text.From(LatestFileDate)},
            {"Total Files Found", Text.From(FileCount)},
            {"Total Rows in Source", Text.From(TotalRowsBeforeFilter)},
            {"Columns in Data", Text.Combine(ActualColumns, ", ")},
            {"Target Year", Text.From(TargetYear)},
            {"Target Month", Text.From(TargetMonth)},
            {"Target Month Name", MonthYearDisplay},
            {"Current Date", Text.From(Current)}
        }
    ),

    // ═══ Check sample dates from the data ═════════════════════════
    ToDate = (x) => if x = null or x = "" then
        null
    else
        try Date.From(x) otherwise try Date.FromText(Text.From(x)) otherwise null,
    
    // Add a column showing what dates actually parsed
    WithParsedDates = Table.AddColumn(
        SafeRename2,
        "Parsed_Date",
        each ToDate([ArrestDate]),
        type nullable date
    ),
    
    // Add year and month columns to see what we actually have
    WithDateParts = Table.AddColumn(
        Table.AddColumn(
            WithParsedDates,
            "Year_From_Data",
            each try Date.Year([Parsed_Date]) otherwise null,
            type number
        ),
        "Month_From_Data",
        each try Date.Month([Parsed_Date]) otherwise null,
        type number
    ),
    
    // DIAGNOSTIC: Show date distribution
    DateDistribution = Table.Group(
        WithDateParts,
        {"Year_From_Data", "Month_From_Data"},
        {{"Count", each Table.RowCount(_), Int64.Type}}
    ),

    PreviousMonthOnly = Table.SelectRows(
        SafeRename2,
        each let d = ToDate([ArrestDate]) in d <> null and Date.Year(d) = TargetYear and Date.Month(d) = TargetMonth
    ),
    
    // DIAGNOSTIC INFO: Rows after date filter
    RowsAfterDateFilter = Table.RowCount(PreviousMonthOnly),
    
    // Return DIAGNOSTIC INFO instead of empty table
    FinalOutput = #table(
        {"Metric", "Value"},
        {
            {"Latest File", LatestFileName},
            {"File Modified Date", Text.From(LatestFileDate)},
            {"Total Files Found", Text.From(FileCount)},
            {"Total Rows in Source", Text.From(TotalRowsBeforeFilter)},
            {"Columns in Data", Text.Combine(ActualColumns, ", ")},
            {"Target Year", Text.From(TargetYear)},
            {"Target Month", Text.From(TargetMonth)},
            {"Target Month Name", MonthYearDisplay},
            {"Rows After Date Filter", Text.From(RowsAfterDateFilter)},
            {"Date Distribution", "See DateDistribution query below"}
        }
    )

in
    FinalOutput
