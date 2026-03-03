// ___Arrest_Distro
// 🕒 2025-08-07-14-45-00
// Project: Arrest_Analysis/Arrest_Distro
// Author: R. A. Carucci
// Purpose: Process arrest data from most recent Power BI ready file with
// enhanced null handling Fixed: Resolved all column conflict issues

let
    // 1. Load folder of Power BI ready files
    Source = Folder.Files("C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\ARREST_DATA\Power_BI"),
    
    // 2. Filter for UCR-updated files (CSV or Excel)
    PowerBIFiles = Table.SelectRows(Source, each
        [Attributes]?[Hidden]? <> true and
        (Text.EndsWith([Name], ".xlsx") or Text.EndsWith([Name], ".csv")) and
        (Text.Contains([Name], "ucr_updated") or Text.Contains([Name], "POWERBI_READY") or Text.Contains([Name], "PowerBI_Ready"))
    ),
    
    // 3. Sort by date modified to get the most recent file
    SortedFiles = Table.Sort(PowerBIFiles, {{"Date modified", Order.Descending}}),
    
    // 4. Diagnostic: record which file we're loading
    LatestFile = if Table.RowCount(SortedFiles) > 0 then SortedFiles{0} else error "No Power BI ready files found",
    FileName = LatestFile[Name],
    FileModifiedDate = LatestFile[Date modified],
    DiagnosticInfo = Table.AddColumn(Table.FromRecords({LatestFile}), "FileDebug", each "Processing: " & [Name] & " (Modified: " & Date.ToText([Date modified]) & ")"),
    
    // 5. Load the most recent file
    LoadedData = Table.AddColumn(DiagnosticInfo, "Data", each 
        try 
            if Text.EndsWith([Name], ".csv") then
                let
                    CsvData = Csv.Document([Content], [Delimiter=",", Columns=null, Encoding=1252, QuoteStyle=QuoteStyle.None]),
                    PromotedHeaders = Table.PromoteHeaders(CsvData, [PromoteAllScalars=true])
                in
                    PromotedHeaders
            else
                let
                    ExcelFile = Excel.Workbook([Content], null, true),
                    FirstSheet = ExcelFile{0}[Data],
                    PromotedHeaders = Table.PromoteHeaders(FirstSheet, [PromoteAllScalars=true])
                in
                    PromotedHeaders
        otherwise error "Failed to load file: " & [Name]
    ),
    
    // 6. Extract the data table
    DataTable = LoadedData{0}[Data],
    
    // 7. Remove entirely blank rows
    RemoveNulls = Table.SelectRows(DataTable, each List.NonNullCount(Record.FieldValues(_))>0),
    
    // 8. Default "Not Provided" for missing addresses (only if Address_Defaulted doesn't exist)
    WithDefaultAddress = if Table.HasColumns(RemoveNulls, "Address_Defaulted") then
        RemoveNulls
    else
        Table.AddColumn(RemoveNulls, "Address_Defaulted", each 
            if [Address] = null or [Address] = "" then "Not Provided" else try Text.From([Address]) otherwise "Not Provided"
        , type text),
    
    // 9. Handle ZIP column - use existing if available, otherwise extract from address
    WithZIP = if Table.HasColumns(WithDefaultAddress, "ZIP") then
        // ZIP column already exists, just ensure it's text type
        Table.TransformColumns(WithDefaultAddress, {{"ZIP", each try Text.From(_) otherwise "", type text}})
    else if Table.HasColumns(WithDefaultAddress, "ExtractedZIP") then
        // Use ExtractedZIP and rename it to ZIP
        Table.RenameColumns(WithDefaultAddress, {{"ExtractedZIP", "ZIP"}})
    else
        // Extract ZIP from address
        Table.AddColumn(WithDefaultAddress, "ZIP", each
            let
                addr = [Address_Defaulted],
                tokens = if addr = "Not Provided" then {} else Text.Split(addr, " "),
                candidates = List.Select(tokens, each 
                    let s = Text.Select(_, {"0".."9"})
                    in Text.Length(if Text.Contains(_, "-") then Text.BeforeDelimiter(_, "-") else s)=5
                )
            in
                if List.Count(candidates)>0 
                then Text.Select(if Text.Contains(candidates{0},"-") then Text.BeforeDelimiter(candidates{0},"-") else candidates{0}, {"0".."9"})
                else null
            , type text),
    
    // 10. Flag valid 5-digit ZIPs (only if ValidZIP doesn't exist)
    WithValidZipFlag = if Table.HasColumns(WithZIP, "ValidZIP") then
        WithZIP
    else
        Table.AddColumn(WithZIP, "ValidZIP", each
            let z = try Text.From([ZIP]) otherwise ""
            in Text.Length(z)=5 and Text.Length(Text.Select(z,{"0".."9"}))=5
        , type logical),
    
    // 11. Ensure Arrest Date is a nullable date
    ConvertedDates = if Table.HasColumns(WithValidZipFlag, "Arrest Date") then
        Table.TransformColumns(WithValidZipFlag, {{"Arrest Date", each try Date.From(_) otherwise null, type nullable date}})
    else
        WithValidZipFlag,
    
    // 12. Add final record index (only if it doesn't already exist)
    AddFinalIndex = if Table.HasColumns(ConvertedDates, "RecordIndex") then
        ConvertedDates
    else
        Table.AddIndexColumn(ConvertedDates, "RecordIndex", 1, 1, Int64.Type),
    
    // 13. Load ZIP reference data
    ZIPRef = try Csv.Document(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\GeographicData\ZipCodes\uszips.csv"), [Delimiter=",", Encoding=1252, QuoteStyle=QuoteStyle.None]) otherwise #table({"zip","state_id","county_name"},{}),
    ZIPHeaders = Table.PromoteHeaders(ZIPRef, [PromoteAllScalars=true]),
    ZIPNullHandled = Table.ReplaceValue(ZIPHeaders, null, "", Replacer.ReplaceValue, {"zip","state_id","county_name"}),
    ZIPCleaned = Table.TransformColumnTypes(Table.SelectColumns(ZIPNullHandled,{"zip","state_id","county_name"}), {{"zip", type text}}),
    
    // 14. Join in state_id + county_name (only if they don't already exist)
    JoinZip = if Table.HasColumns(AddFinalIndex, "state_id") and Table.HasColumns(AddFinalIndex, "county_name") then
        AddFinalIndex
    else
        let
            JoinResult = Table.NestedJoin(AddFinalIndex, "ZIP", ZIPCleaned, "zip", "ZipMeta", JoinKind.LeftOuter),
            ExpandResult = Table.ExpandTableColumn(JoinResult, "ZipMeta", {"state_id","county_name"})
        in ExpandResult,
    
    // 15. Uppercase full address for keyword logic (only if FullAddress2 doesn't exist)
    AddFullAddress2 = if Table.HasColumns(JoinZip, "FullAddress2") then
        JoinZip
    else
        Table.AddColumn(JoinZip, "FullAddress2", each 
            if [Address_Defaulted] = "Not Provided" then "" else try Text.Upper([Address_Defaulted]) otherwise ""
        , type text),
    
    // 16. Handle UCR columns (use existing if available, otherwise split)
    WithUCR = if Table.HasColumns(AddFullAddress2, "UCR_Code") and Table.HasColumns(AddFullAddress2, "UCR_Desc") then
        AddFullAddress2
    else if Table.HasColumns(AddFullAddress2, "UCR #") then
        let 
            RemovedExisting = Table.RemoveColumns(AddFullAddress2, {"UCR_Code", "UCR_Desc"}, MissingField.Ignore),
            split1 = Table.SplitColumn(RemovedExisting, "UCR #", Splitter.SplitTextByDelimiter(" ", QuoteStyle.Csv), {"UCR_Code","UCR_Desc"})
        in Table.TransformColumns(split1, {
               {"UCR_Code", each if _ = null then "" else Text.Trim(_), type text},
               {"UCR_Desc", each if _ = null then "" else Text.Trim(_), type text}
           })
    else
        let
            AddUCRCode = if Table.HasColumns(AddFullAddress2, "UCR_Code") then AddFullAddress2 else Table.AddColumn(AddFullAddress2, "UCR_Code", each "", type text),
            AddUCRDesc = if Table.HasColumns(AddUCRCode, "UCR_Desc") then AddUCRCode else Table.AddColumn(AddUCRCode, "UCR_Desc", each "", type text)
        in AddUCRDesc,
    
    // 17. Categorize by home location (only if Home_Category doesn't exist)
    AddHomeCategory = if Table.HasColumns(WithUCR, "Home_Category") then
        WithUCR
    else
        Table.AddColumn(WithUCR, "Home_Category", each
            let
                addr = [FullAddress2],
                st = try Text.From([state_id]) otherwise "",
                cnty = try Text.From([county_name]) otherwise "",
                z = try Text.From([ZIP]) otherwise "",
                localZ = {"07601","07602"},
                isLocalZip = if z = "" then false else List.Contains(localZ, z),
                isHomeless = if addr = "" then false else Text.Contains(addr, "HOMELESS"),
                isHack = if addr = "" then false else Text.Contains(addr, "HACKENSACK"),
                inBergen = if cnty = "" then false else Text.Contains(Text.Upper(cnty), "BERGEN")
            in
                if addr = "" or isLocalZip or isHomeless or isHack then "Local"
                else if st="NJ" and inBergen then "In-County"
                else if st="NJ" then "Out-of-County | " & cnty
                else if st<>"" then "Out-of-State | " & st
                else "Unknown"
        , type text),
    
    // 18. Add diagnostics for the loaded file (only if they don't exist)
    AddDiagnostics = let
        WithSourceFile = if Table.HasColumns(AddHomeCategory, "SourceFile") then
            AddHomeCategory
        else
            Table.AddColumn(AddHomeCategory, "SourceFile", each FileName, type text),
        WithFileDate = if Table.HasColumns(WithSourceFile, "FileModifiedDate") then
            WithSourceFile
        else
            Table.AddColumn(WithSourceFile, "FileModifiedDate", each try Date.ToText(FileModifiedDate) otherwise "Unknown", type text),
        WithTotalRecords = if Table.HasColumns(WithFileDate, "TotalRecordsLoaded") then
            WithFileDate
        else
            Table.AddColumn(WithFileDate, "TotalRecordsLoaded", each Table.RowCount(WithFileDate), type number)
    in WithTotalRecords
in
    AddDiagnostics

// ___Top_5_Arrests
// 🕒 2025-09-03-15-00-00
// Project: Arrest_Analysis/Top_5_Arrest
// Author: R. A. Carucci
// Purpose: Fixed Top 5 Officers analysis with dynamic file loading and better error handling

let
    // ═══ A) Dynamic file discovery (same as your working main query) ═══════
    FolderFiles = Folder.Files(
        "C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\ARREST_DATA\Power_BI"
    ),
    PowerBIFiles = Table.SelectRows(
        FolderFiles,
        each [Extension] = ".xlsx" and 
             Text.Contains([Name], "PowerBI_Ready")
    ),
    Sorted = Table.Sort(PowerBIFiles, {{"Date modified", Order.Descending}}),
    
    // Load the latest file (same logic as working query)
    Source = if Table.RowCount(Sorted) > 0 then
        let
            LatestFile = Sorted{0}[Content],
            ExcelData = Excel.Workbook(LatestFile, null, true),
            FirstSheet = ExcelData{0}[Data]
        in
            FirstSheet
    else
        error "No Power BI ready files found",

    // ═══ B) Promote headers and handle column names ═══════════════════════
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    
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

    // ═══ C) Calculate previous month with better date handling ═════════════
    Current = Date.From(DateTime.LocalNow()),
    PreviousMonth = Date.AddMonths(Current, -1),
    TargetYear = Date.Year(PreviousMonth),
    TargetMonth = Date.Month(PreviousMonth),
    MonthYearDisplay = Date.MonthName(PreviousMonth) & " " & Text.From(TargetYear),
    
    // ═══ D) Filter to previous month with better error handling ════════════
    ToDate = (x) => 
        if x = null or x = "" then null
        else try Date.From(x) otherwise try Date.FromText(Text.From(x)) otherwise null,
    
    PreviousMonthOnly = Table.SelectRows(
        SafeRename2,
        each 
            let d = ToDate([ArrestDate]) in
            d <> null and 
            Date.Year(d) = TargetYear and 
            Date.Month(d) = TargetMonth
    ),
    
    // ═══ E) Verify we have data before proceeding ═════════════════════════
    VerifyData = if Table.RowCount(PreviousMonthOnly) = 0 then
        error ("No arrest data found for " & MonthYearDisplay & ". Check date filters and data availability.")
    else
        PreviousMonthOnly,

    // ═══ F) Clean officer names with simplified logic ═══════════════════════
    CleanOfficerNames = Table.TransformColumns(
        VerifyData,
        {
            {
                "OfficerOfRecord", 
                each 
                    if _ = null or _ = "" then "UNKNOWN OFFICER"
                    else
                        let
                            original = Text.Upper(Text.Trim(Text.From(_))),
                            // Remove common prefixes
                            step1 = Text.Replace(Text.Replace(Text.Replace(Text.Replace(
                                original, "P.O. ", ""), "PO ", ""), "DET. ", ""), "DETECTIVE ", ""),
                            // Clean up whitespace and special characters
                            step2 = Text.Replace(Text.Replace(Text.Replace(Text.Replace(Text.Replace(
                                step1, "  ", " "), " - ", " "), "(", ""), ")", ""), "#", ""),
                            // Simple badge number removal - remove trailing 1-4 digit numbers
                            step3 = Text.Trim(
                                if Text.Length(step2) > 0 then
                                    let
                                        words = Text.Split(step2, " "),
                                        lastWord = if List.Count(words) > 1 then List.Last(words) else "",
                                        isNumber = try Number.From(lastWord) >= 0 otherwise false,
                                        isBadgeNumber = Text.Length(lastWord) <= 4 and isNumber,
                                        cleanWords = if isBadgeNumber then List.RemoveLastN(words, 1) else words
                                    in
                                        Text.Combine(cleanWords, " ")
                                else
                                    step2
                            )
                        in
                            if Text.Length(step3) > 0 then step3 else "UNKNOWN OFFICER",
                type text
            }
        }
    ),
    
    // ═══ G) Group by officer and count arrests ════════════════════════════
    GroupedByOfficer = Table.Group(
        CleanOfficerNames,
        {"OfficerOfRecord"},
        {
            {"Arrest_Count", each Table.RowCount(_), Int64.Type}
        }
    ),
    
    // ═══ H) Sort and get top 5 ═════════════════════════════════════════════
    SortedByCount = Table.Sort(
        GroupedByOfficer, 
        {{"Arrest_Count", Order.Descending}}
    ),
    
    Top5Officers = Table.FirstN(SortedByCount, 5),
    
    // ═══ I) Add metadata and formatting ═══════════════════════════════════
    WithMonthYear = Table.AddColumn(
        Top5Officers,
        "Month_Year",
        each MonthYearDisplay,
        type text
    ),
    
    WithRanking = Table.AddIndexColumn(
        WithMonthYear,
        "Rank",
        1,
        1,
        Int64.Type
    ),
    
    // Rename for final output
    FinalRenamed = Table.RenameColumns(
        WithRanking,
        {
            {"OfficerOfRecord", "Officer_Name_Clean"}
        }
    ),
    
    // ═══ J) Final type enforcement ════════════════════════════════════════
    TypedData = Table.TransformColumnTypes(
        FinalRenamed,
        {
            {"Officer_Name_Clean", type text},
            {"Arrest_Count", Int64.Type},
            {"Month_Year", type text},
            {"Rank", Int64.Type}
        }
    ),
    
    // ═══ K) Add source file info for debugging ════════════════════════════
    WithSourceInfo = if Table.RowCount(Sorted) > 0 then
        Table.AddColumn(
            TypedData,
            "Source_File",
            each Sorted{0}[Name],
            type text
        )
    else
        TypedData

in
    WithSourceInfo

// ___ComprehensiveDateTable
// 🕒 2025-08-17-16-30-45
// Project: PowerBI_DateDimension/ComprehensiveDateTable
// Author: R. A. Carucci
// Purpose: Create a comprehensive date dimension table with multiple date formats including mm/dd/yy

// ComprehensiveDateTable
// Purpose: Create a date dimension table for temporal analysis
let
    StartDate = #date(2020, 1, 1),
    EndDate = #date(2030, 12, 31),
    DateList = List.Dates(StartDate, Duration.Days(EndDate - StartDate) + 1, #duration(1, 0, 0, 0)),
    DateTable = Table.FromList(DateList, Splitter.SplitByNothing(), {"Date"}),
    SetDateType = Table.TransformColumnTypes(DateTable, {{"Date", type date}}),
    AddYear = Table.AddColumn(SetDateType, "Year", each Date.Year([Date]), Int64.Type),
    AddMonth = Table.AddColumn(AddYear, "Month", each Date.Month([Date]), Int64.Type),
    AddMonthName = Table.AddColumn(AddMonth, "MonthName", each Date.MonthName([Date]), type text),
    AddQuarter = Table.AddColumn(AddMonthName, "Quarter", each Date.QuarterOfYear([Date]), Int64.Type),
    AddDayOfMonth = Table.AddColumn(AddQuarter, "DayOfMonth", each Date.Day([Date]), Int64.Type),
    AddDayOfWeek = Table.AddColumn(AddDayOfMonth, "DayOfWeek", each 
        let
            DayNum = Date.DayOfWeek([Date], Day.Monday)
        in
            if DayNum = 0 then 7 else DayNum, Int64.Type),
    AddDayName = Table.AddColumn(AddDayOfWeek, "DayName", each Date.DayOfWeekName([Date]), type text),
    AddWeekOfYear = Table.AddColumn(AddDayName, "WeekOfYear", each Date.WeekOfYear([Date], Day.Monday), Int64.Type),
    AddFiscalYear = Table.AddColumn(AddWeekOfYear, "FiscalYear", each 
        if Date.Month([Date]) >= 7 then Date.Year([Date]) + 1 else Date.Year([Date]), Int64.Type),
    AddFiscalQuarter = Table.AddColumn(AddFiscalYear, "FiscalQuarter", each 
        if Date.Month([Date]) >= 7 then Date.QuarterOfYear(Date.AddMonths([Date], -6))
        else Date.QuarterOfYear(Date.AddMonths([Date], 6)), Int64.Type),
    AddYearMonth = Table.AddColumn(AddFiscalQuarter, "YearMonth", each 
        Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type),
    AddYearQuarter = Table.AddColumn(AddYearMonth, "YearQuarter", each 
        Date.Year([Date]) * 10 + Date.QuarterOfYear([Date]), Int64.Type),
    AddFiscalYearQuarter = Table.AddColumn(AddYearQuarter, "FiscalYearQuarter", each 
        [FiscalYear] * 10 + [FiscalQuarter], Int64.Type),
    AddDateKey = Table.AddColumn(AddFiscalYearQuarter, "DateKey", each 
        Number.From(Date.ToText([Date], "yyyyMMdd")), Int64.Type),
    AddShortDate = Table.AddColumn(AddDateKey, "ShortDate", each 
        Date.ToText([Date], "MM/dd/yy"), type text),
    // NEW: Add mm/dd/yy format column
    AddMMDDYY = Table.AddColumn(AddShortDate, "mm/dd/yy", each 
        Date.ToText([Date], "MM/dd/yy"), type text),
    AddMMYY = Table.AddColumn(AddMMDDYY, "mm-yy", each 
        Text.PadStart(Text.From(Date.Month([Date])), 2, "0") & "-" & 
        Text.End(Text.From(Date.Year([Date])), 2), type text),
    AddMMMYY = Table.AddColumn(AddMMYY, "mmm-yy", each 
        Text.Start(Date.MonthName([Date]), 3) & "-" & 
        Text.End(Text.From(Date.Year([Date])), 2), type text),
    AddMMYYYY = Table.AddColumn(AddMMMYY, "mmm-yyyy", each 
        Text.Start(Date.MonthName([Date]), 3) & "-" & 
        Text.From(Date.Year([Date])), type text),
    AddMMMMYYYY = Table.AddColumn(AddMMYYYY, "mmmm yyyy", each 
        Date.MonthName([Date]) & " " & Text.From(Date.Year([Date])), type text),
    AddMMMM = Table.AddColumn(AddMMMMYYYY, "mmmm", each 
        Date.MonthName([Date]), type text),
    AddDayType = Table.AddColumn(AddMMMM, "DayType", each 
        if Date.DayOfWeek([Date], Day.Monday) >= 5 then "Weekend" else "Weekday", type text),
    
    // Add sort order columns for all date format columns
    AddSortOrders = Table.AddColumn(AddDayType, "mm-yy_Sort_Order", each 
        Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type),
    // NEW: Add sort order for mm/dd/yy format
    AddMMDDYYSort = Table.AddColumn(AddSortOrders, "mm/dd/yy_Sort_Order", each 
        Number.From(Date.ToText([Date], "yyyyMMdd")), Int64.Type),
    AddMMMYYSort = Table.AddColumn(AddMMDDYYSort, "mmm-yy_Sort_Order", each 
        Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type),
    AddMMYYYYSort = Table.AddColumn(AddMMMYYSort, "mmm-yyyy_Sort_Order", each 
        Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type),
    AddMMMMYYYYSort = Table.AddColumn(AddMMYYYYSort, "mmmm yyyy_Sort_Order", each 
        Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type),
    AddMMMMSort = Table.AddColumn(AddMMMMYYYYSort, "mmmm_Sort_Order", each 
        Date.Month([Date]), Int64.Type),
    AddMonthNameSort = Table.AddColumn(AddMMMMSort, "MonthName_Sort_Order", each 
        Date.Month([Date]), Int64.Type),
    AddDayNameSort = Table.AddColumn(AddMonthNameSort, "DayName_Sort_Order", each 
        let
            DayNum = Date.DayOfWeek([Date], Day.Monday)
        in
            if DayNum = 0 then 7 else DayNum, Int64.Type),
    
    // Set explicit data types for all columns to prevent auto-detection issues
    SetDataTypes = Table.TransformColumnTypes(AddDayNameSort, {
        {"Date", type date},
        {"Year", Int64.Type},
        {"Month", Int64.Type},
        {"MonthName", type text},
        {"Quarter", Int64.Type},
        {"DayOfMonth", Int64.Type},
        {"DayOfWeek", Int64.Type},
        {"DayName", type text},
        {"WeekOfYear", Int64.Type},
        {"FiscalYear", Int64.Type},
        {"FiscalQuarter", Int64.Type},
        {"YearMonth", Int64.Type},
        {"YearQuarter", Int64.Type},
        {"FiscalYearQuarter", Int64.Type},
        {"DateKey", Int64.Type},
        {"ShortDate", type text},
        {"mm/dd/yy", type text},
        {"mm-yy", type text},
        {"mmm-yy", type text},
        {"mmm-yyyy", type text},
        {"mmmm yyyy", type text},
        {"mmmm", type text},
        {"DayType", type text},
        {"mm-yy_Sort_Order", Int64.Type},
        {"mm/dd/yy_Sort_Order", Int64.Type},
        {"mmm-yy_Sort_Order", Int64.Type},
        {"mmm-yyyy_Sort_Order", Int64.Type},
        {"mmmm yyyy_Sort_Order", Int64.Type},
        {"mmmm_Sort_Order", Int64.Type},
        {"MonthName_Sort_Order", Int64.Type},
        {"DayName_Sort_Order", Int64.Type}
    })
in
    SetDataTypes

// ___Chief2
let
    // === Load Chief Excel File ===
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Chief\chief_monthly.xlsx"), 
        null, true
    ),
    ChiefTable = Source{[Item="MoM_Chief", Kind="Table"]}[Data],

    // === Set Column Types Dynamically ===
    ColumnNames = Table.ColumnNames(ChiefTable),
    MonthColumns = List.Select(ColumnNames, each Text.Contains(_, "-") and Text.Length(_) >= 4),
    TrackedItemsType = {{"Tracked Items", type text}},
    MonthTypes       = List.Transform(MonthColumns, each {_, Int64.Type}),
    AllTypes         = List.Combine({TrackedItemsType, MonthTypes}),
    ChangedTypes     = Table.TransformColumnTypes(ChiefTable, AllTypes),

    // === Clean Text Data ===
    CleanedText  = Table.TransformColumns(ChangedTypes, {{"Tracked Items", Text.Clean, type text}}),
    TrimmedText  = Table.TransformColumns(CleanedText, {{"Tracked Items", Text.Trim, type text}}),
    FilteredRows = Table.SelectRows(TrimmedText, each [Tracked Items] <> ""),

    // === Classifications ===
    AddedCategory = Table.AddColumn(FilteredRows, "Category", each
        let item = Text.Upper([Tracked Items]) in
        if Text.Contains(item,"MEETING") then "Meetings & Conferences"
        else if Text.Contains(item,"TRAINING") then "Training & Development"
        else "Executive Administration"
    , type text),

    AddedDivision = Table.AddColumn(AddedCategory, "Division/Bureau", each "Chief of Police - Executive Office", type text),

    AddedActivityLevel = Table.AddColumn(AddedDivision, "Activity_Level", each
        let
          cols = MonthColumns,
          recent = List.LastN(cols,3),
          vals = List.Transform(recent, each try Record.Field(_,_) otherwise 0),
          avg3 = if List.Count(vals)>0 then List.Average(vals) else 0
        in
          if avg3>=10 then "High Activity"
          else if avg3>=5 then "Moderate Activity"
          else if avg3>0 then "Low Activity"
          else "No Recent Activity"
    , type text),

    AddedRecentTotal = Table.AddColumn(AddedActivityLevel, "Recent 3 Month Avg", each
        let
          cols = MonthColumns,
          recent = List.LastN(cols,3),
          vals = List.Transform(recent, each try Record.Field(_,_) otherwise 0),
          clean = List.Select(vals, each _<>null),
          a = if List.Count(clean)>0 then List.Average(clean) else 0
        in Number.Round(a,1)
    , type number),

    AddedYoYComparison = Table.AddColumn(AddedRecentTotal, "YoY Change %", each
        let
          cols = MonthColumns,
          sorted = List.Sort(cols),
          curr  = List.Last(sorted),
          parts = Text.Split(curr,"-"),
          mm    = parts{0},
          yy    = Number.From(parts{1}),
          prev  = mm & "-" & Text.From(yy-1),
          cVal  = Record.Field(_,curr),
          pVal  = try Record.Field(_,prev) otherwise 0,
          pct   = if pVal>0 then (cVal - pVal)/pVal*100 else 0
        in Number.Round(pct,1)
    , type number),

    // === NEW: Unpivot + Date + Type + Index ===
    Unpivoted     = Table.Unpivot(AddedYoYComparison, MonthColumns, "Month", "Total"),
    AddDate       = Table.AddColumn(Unpivoted, "PeriodDate", each Date.FromText("01-" & [Month]), type date),
    ChangeType2   = Table.TransformColumnTypes(AddDate, {{"Total", Int64.Type}}),
    AddMonthIndex = Table.AddColumn(ChangeType2, "MonthIndex", each Date.Year([PeriodDate])*100 + Date.Month([PeriodDate]), Int64.Type),

    // === Final columns ===
    Final = Table.SelectColumns(
      AddMonthIndex,
      {
        "Tracked Items",
        "Category",
        "Division/Bureau",
        "Activity_Level",
        "Recent 3 Month Avg",
        "YoY Change %",
        "Month",
        "PeriodDate",
        "Total",
        "MonthIndex"
      }
    )
in
    Final

// ___Drone
// 🕒 2025-08-19-17-30-00
// Project: Drone_Analytics/Final_Duration_Based_Handling
// Author: R. A. Carucci
// Purpose: Properly handle Excel DURATION values for drone metrics

let
    // 1) Load the workbook
    Source = Excel.Workbook(
        File.Contents("C:\Users\RobertCarucci\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Drone_Monthly.xlsx"),
        null, true),

    // ─── DFR Activity sheet ────────────────────────────────────────────────────────
    DFR_Raw = Source{[Name = "DFR Activity", Kind = "Sheet"]}[Data],
    DFR_Headers = Table.PromoteHeaders(DFR_Raw, [PromoteAllScalars = true]),
    DFR_MetricKey = Table.ColumnNames(DFR_Headers){0},
    DFR_PeriodCols = List.Select(Table.ColumnNames(DFR_Headers), each Text.Length(_) = 5 and Text.Middle(_, 2, 1) = "-"),
    DFR_Unpivot = Table.Unpivot(DFR_Headers, DFR_PeriodCols, "Period", "RawValue"),
    DFR_Renamed = Table.RenameColumns(DFR_Unpivot, {{DFR_MetricKey, "Metric"}}),

    // Add ordering for DFR Activity metrics - CORRECTED ORDER
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

    // CORRECTED: Handle DURATION values properly
    DFR_Converted = Table.AddColumn(DFR_WithOrder, "Value", each 
        let
            RawVal = [RawValue],
            MetricName = [Metric]
        in
            if Value.Is(RawVal, type datetime) or Value.Is(RawVal, type time) then
                let
                    // Convert to time to extract duration components
                    TimeVal = if Value.Is(RawVal, type datetime) then Time.From(RawVal) else RawVal,
                    Hours = Time.Hour(TimeVal),
                    Minutes = Time.Minute(TimeVal),
                    Seconds = Time.Second(TimeVal)
                in
                    if Text.Contains(MetricName, "(Mins:Secs)") then
                        // For response times: show total minutes and seconds
                        let
                            TotalMinutes = Hours * 60 + Minutes,
                            DisplaySeconds = Seconds
                        in Text.From(TotalMinutes) & ":" & Text.PadStart(Text.From(DisplaySeconds), 2, "0")
                    else if Text.Contains(MetricName, "(Hours:Mins)") and not Text.Contains(MetricName, "Secs") then
                        // For flight times: show hours and minutes
                        Text.PadStart(Text.From(Hours), 2, "0") & ":" & Text.PadStart(Text.From(Minutes), 2, "0")
                    else if Text.Contains(MetricName, "(Hours:Mins:Secs)") then
                        // For complete time: show hours, minutes, and seconds
                        Text.PadStart(Text.From(Hours), 2, "0") & ":" & Text.PadStart(Text.From(Minutes), 2, "0") & ":" & Text.PadStart(Text.From(Seconds), 2, "0")
                    else
                        Text.From(RawVal)
            else if Value.Is(RawVal, type duration) then
                // Handle actual duration type
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
                    // Handle duration stored as decimal (fraction of day)
                    let
                        TotalSeconds = RawVal * 24 * 60 * 60, // Convert fraction of day to seconds
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

    // ─── Non-DFR sheet ─────────────────────────────────────────────────────────────
    NonDFR_Raw = Source{[Name = "Non-DFR", Kind = "Sheet"]}[Data],
    NonDFR_Headers = Table.PromoteHeaders(NonDFR_Raw, [PromoteAllScalars = true]),
    NonDFR_MetricKey = Table.ColumnNames(NonDFR_Headers){0},
    NonDFR_PeriodCols = List.Select(Table.ColumnNames(NonDFR_Headers), each Text.Length(_) = 5 and Text.Middle(_, 2, 1) = "-"),
    NonDFR_Unpivot = Table.Unpivot(NonDFR_Headers, NonDFR_PeriodCols, "Period", "RawValue"),
    NonDFR_Renamed = Table.RenameColumns(NonDFR_Unpivot, {{NonDFR_MetricKey, "Metric"}}),

    // Add ordering for Non-DFR metrics
    NonDFR_WithOrder = Table.AddColumn(NonDFR_Renamed, "SortOrder", each 
        if [Metric] = "Non-DFR - Flight Time - Calls Responded To (Hours:Mins)" then 1 
        else if [Metric] = "Non-DFR - Flight Time - Trainging Flights (Hours:Mins)" then 2 
        else if [Metric] = "Non-DFR - Total Flight Time (Hours:Mins)" then 3 
        else 99, Int64.Type),

    // Handle Non-DFR duration values the same way
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

    // ─── Combine both tables & add date keys ───────────────────────────────────────
    Combined = Table.Combine({DFR_Tagged, NonDFR_Tagged}),
    WithDate = Table.AddColumn(Combined, "PeriodDate", each
#date(2000 + Number.FromText(Text.End([Period], 2)),                           \
      Number.FromText(Text.Start([Period], 2)), 1),                            \
    type date),
    WithSort = Table.AddColumn(WithDate, "DateSortKey", each 
        Date.Year([PeriodDate]) * 100 + Date.Month([PeriodDate]), Int64.Type),

    // ─── Filter to Rolling 13 Months ───
    Today = DateTime.Date(DateTime.LocalNow()),
    PriorMonth = Date.AddMonths(#date(Date.Year(Today), Date.Month(Today), 1), -1),
    StartMonth = Date.AddMonths(PriorMonth, -12),

    FilteredData = Table.SelectRows(WithSort, each [PeriodDate] >= StartMonth and [PeriodDate] <= PriorMonth),

    // ─── Create totals with proper duration arithmetic ──────────────────────────────────────────────────

    // *** MODIFIED STEP ***
    // We REMOVED the "DataForTotals" step
    // We now group on "FilteredData" and add a special check for the AVG metrics
    AllMetricGroups = Table.Group(FilteredData, {"Metric", "Source", "SortOrder"}, {
        {"TotalValue", each 
            let
                CurrentTable = _,
                MetricName = CurrentTable[Metric]{0}
            in
                // NEW: Check for specific AVG metrics first
                if MetricName = "DRF - AVG Response Times - All Calls (Mins:Secs)" or
                   MetricName = "DRF - AVG Response Times - First on Scene (Mins:Secs)"
                then
                    "N/A" // <-- This is the value that will show in the Total column
                
                // --- Existing logic below ---
                else if Text.Contains(MetricName, "(Mins:Secs)") then
                    // For response times, calculate average
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
                    // For flight times without seconds, sum the time values
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
                    // FIXED: For flight times with seconds, sum the time values properly
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
                    // For all other metrics, sum the values
                    Text.From(Number.Round(List.Sum(List.Transform(CurrentTable[Value], each try Number.From(_) otherwise 0)), 2))
        }
    }),

    // Add required columns for total rows
    TotalsWithPeriod = Table.AddColumn(AllMetricGroups, "Period", each "Total"),
    TotalsWithValue = Table.AddColumn(TotalsWithPeriod, "Value", each [TotalValue]),
    TotalsWithDate = Table.AddColumn(TotalsWithValue, "PeriodDate", each #date(2099, 12, 31), type date),
    TotalsWithSort = Table.AddColumn(TotalsWithDate, "DateSortKey", each 999999, Int64.Type),

    // ─── Combine regular data with all totals ───────────────────────────────────────
    CombinedWithAllTotals = Table.Combine({FilteredData, TotalsWithSort}),

    // ─── Sort by Source, SortOrder, then Date ──────────────────────────────────────
    Sorted = Table.Sort(CombinedWithAllTotals, {
        {"Source", Order.Ascending},
        {"SortOrder", Order.Ascending},
        {"DateSortKey", Order.Ascending}
    }),

    // ─── Keep only the final columns ──────────────────────────────────────────────
    Final = Table.SelectColumns(Sorted, {"Metric", "Period", "Value", "Source", "PeriodDate", "DateSortKey", "SortOrder"})

in Final

// ___Combined_Outreach_All
// 🐍 Combined_Outreach_All — Using Python ETL Output
// Simplified M code that reads from centralized Python ETL CSV output
// Maintains exact same column structure for Power BI compatibility
let
    // === 1. Dynamic File Path Discovery ===
    // Look for the most recent Python ETL output file
    OutputFolder = "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Community_Engagment\output\",
    
    // Try to find the most recent community_engagement_data_*.csv file
    // Pattern: community_engagement_data_YYYYMMDD_HHMMSS.csv
    PythonETLFile = try 
        let
            // Get all CSV files in the output directory
            Source = Folder.Files(OutputFolder),
            FilteredFiles = Table.SelectRows(Source, each Text.StartsWith([Name], "community_engagement_data_") and Text.EndsWith([Name], ".csv")),
            SortedFiles = Table.Sort(FilteredFiles, {{"Date modified", Order.Descending}}),
            LatestFile = if Table.RowCount(SortedFiles) > 0 
                        then OutputFolder & SortedFiles{0}[Name]
                        else error "No Python ETL output files found"
        in
            LatestFile
    otherwise
        // Fallback to a specific filename pattern if dynamic discovery fails
        OutputFolder & "community_engagement_combined_" & Date.ToText(DateTime.Date(DateTime.LocalNow()), "yyyy-MM-dd") & ".csv",

    // === 2. Read Python ETL CSV Output ===
    CSVSource = Csv.Document(File.Contents(PythonETLFile), [Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    HeadersPromoted = Table.PromoteHeaders(CSVSource, [PromoteAllScalars=true]),
    
    // === 3. Data Type Transformations ===
    // Handle datetime strings from Python ETL (format: "YYYY-MM-DD HH:MM:SS")
    DateParsed = Table.TransformColumns(HeadersPromoted, {
        {"date", each 
            if _ = null or _ = "" 
            then null 
            else try DateTime.Date(DateTime.FromText(_)) otherwise Date.FromText(Text.Start(_, 10)), 
        type date}
    }),
    
    // Handle time columns safely (may be in various formats from Python)
    TimeParsed = Table.TransformColumns(DateParsed, {
        {"start_time", each try Time.FromText(_) otherwise null, type time},
        {"end_time", each try Time.FromText(_) otherwise null, type time}
    }),
    
    TypedData = Table.TransformColumnTypes(TimeParsed, {
        {"event_name", type text},
        {"location", type text},
        {"duration_hours", type number},
        {"attendee_count", Int64.Type},
        {"office", type text},
        {"division", type text}
    }),
    
    // Handle any duration_hours conversion issues (Python ETL may have NaNs)
    SafeDuration = Table.TransformColumns(TypedData, {
        {"duration_hours", each 
            if _ = null or _ = "" or Text.From(_) = "nan" 
            then 0.5 
            else try Number.From(_) otherwise 0.5, type number}
    }),
    
    // Handle any attendee_count conversion issues  
    SafeAttendees = Table.TransformColumns(SafeDuration, {
        {"attendee_count", each try Number.From(_) otherwise 1, Int64.Type}
    }),
    
    // === 4. Column Selection and Renaming ===
    // Select only the columns needed for Power BI
    SelectedColumns = Table.SelectColumns(SafeAttendees, {
        "date",
        "duration_hours", 
        "event_name",
        "location",
        "attendee_count",
        "office"
    }),
    
    // Rename columns to match exact Power BI expectations
    RenamedColumns = Table.RenameColumns(SelectedColumns, {
        {"date", "Date"},
        {"duration_hours", "Event Duration (Hours)"},
        {"event_name", "Event Name"}, 
        {"location", "Location of Event"},
        {"attendee_count", "Number of Police Department Attendees"},
        {"office", "Office"}
    }),
    
    // === 5. Data Quality and Filtering ===
    // Remove rows with null dates (same as original M code)
    FilteredData = Table.SelectRows(RenamedColumns, each [Date] <> null),
    
    // Ensure Event Duration is reasonable (0.1 to 24 hours)
    ValidatedDuration = Table.TransformColumns(FilteredData, {
        {"Event Duration (Hours)", each 
            if _ = null or _ <= 0 then 0.5
            else if _ > 24 then 8.0  
            else Number.Round(_, 2), 
        type number}
    }),
    
    // Ensure attendee count is at least 1 if null/zero
    ValidatedAttendees = Table.TransformColumns(ValidatedDuration, {
        {"Number of Police Department Attendees", each 
            if _ = null or _ <= 0 then 1 else _, 
        Int64.Type}
    }),
    
    // === 6. Final Sort and Output ===
    // Sort by date ascending (same as original M code)
    FinalData = if Table.RowCount(ValidatedAttendees) > 0 
                then Table.Sort(ValidatedAttendees, {{"Date", Order.Ascending}}) 
                else ValidatedAttendees

in
    FinalData

// ___CSB_Monthly
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

    //==== Rolling 13-month window logic ======================================================
    // Today -> Current month start
    Today = Date.From(DateTime.LocalNow()),
    CurrentMonthStart = Date.StartOfMonth(Today),

    // EndMonth: last fully completed month (exclude current month)
    EndMonth = Date.AddMonths(CurrentMonthStart, -1),

    // StartMonth: 12 months prior to EndMonth (inclusive range gives 13 total months)
    StartMonth = Date.AddMonths(EndMonth, -12),

    //==== Validate/select only date columns within the window ================================
    // Expecting headers like "MM-YY" (e.g., "08-24")
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
                    ColumnDate <> null and ColumnDate >= StartMonth and ColumnDate <= EndMonth
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

    // Parse "MM-YY" into a proper date at month start
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

    // Exact month index from StartMonth (1..13)
    WithSort =
        Table.AddColumn(
            WithDate,
            "Month_Sort_Order",
            each
                let
                    d = [Date],
                    months =
                        (Date.Year(d) - Date.Year(StartMonth)) * 12
                        + (Date.Month(d) - Date.Month(StartMonth))
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

// ___Detectives
// 🕒 2026-02-13-18-00-00
// # Master_Automation/Detectives/___Detectives.m
// # Author: R. A. Carucci
// # Purpose: Import Detective Division cases from restructured 2026-only
// workbook with rolling 13-month window (01-26 through 12-26).

let
    // =================================================================
    // FILE PATH AND TABLE LOAD
    // =================================================================
    FilePath =
        "C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Detectives\detectives_monthly.xlsx",

    Source = Excel.Workbook(File.Contents(FilePath), null, true),

    // Load _mom_det table (now contains 01-26 through 12-26 only)
    MoM_Det_Table = Source{[Item = "_mom_det", Kind = "Table"]}[Data],

    DetectedTypes = Table.TransformColumnTypes(MoM_Det_Table, {}, "en-US"),

    // =================================================================
    // DATA CLEANING
    // =================================================================
    // Remove completely empty rows
    RemovedEmptyRows = Table.SelectRows(
        DetectedTypes, each not List.IsEmpty(List.RemoveMatchingItems(
                           Record.FieldValues(_), {"", null}))),

    ColumnNames = Table.ColumnNames(RemovedEmptyRows),
    FirstColumn = ColumnNames{0},

    // Filter to rows with at least one month having activity > 0
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
    // Parse MM-YY format (e.g., "01-26") to proper date
    AddedDateInfo = Table.AddColumn(
        UnpivotedData, "Date", each let MonthText = [Month_MM_YY],
        Parts = Text.Split(MonthText, "-"),
        // Parts{0} = MM (month), Parts{1} = YY (year)
        MonthPart = if List.Count(Parts) >= 1 then Parts{0} else "01",
        YearPart = if List.Count(Parts) >= 2 then Parts{1} else "26",

        // Convert 2-digit year to full year
        YearNum = try Number.From(YearPart) otherwise null,
        FullYear = if YearNum = null then null else if YearNum >=
                                50 then 1900 + YearNum else 2000 + YearNum,

        // Convert month to number (01=1, 02=2, etc.)
        MonthNum = try Number.From(MonthPart) otherwise null,

        DateValue = if MonthNum =
            null or FullYear =
                null then null else try #date(FullYear, MonthNum, 1)
                    otherwise null in DateValue,
        type date),

    // Add normalized Month_Normalized column in MM-YY format
    AddedNormalizedMonth = Table.AddColumn(
        AddedDateInfo, "Month_Normalized",
        each if[Date]<> null then Text.PadStart(Text.From(Date.Month([Date])),
                                                2, "0") &
            "-" & Text.End(Text.From(Date.Year([Date])), 2) else[Month_MM_YY],
        type text),

    // Remove old Month_MM_YY and rename Month_Normalized to Month_MM_YY
    RemovedOldMonth =
        Table.RemoveColumns(AddedNormalizedMonth, {"Month_MM_YY"}),
    RenamedMonth = Table.RenameColumns(RemovedOldMonth,
                                       {{"Month_Normalized", "Month_MM_YY"}}),

    // Create numeric sort order (YYYYMM format)
    AddedSortOrder =
        Table.AddColumn(RenamedMonth, "Month_Sort_Order",
                        each if[Date]<> null then Date.Year([Date]) * 100 +
                            Date.Month([Date]) else null,
                        Int64.Type),

    // =================================================================
    // ROLLING 13-MONTH WINDOW LOGIC (WORKS WITH HISTORICAL DATA)
    // =================================================================
    // Table contains historical data from Jun 2023 onwards
    // Show rolling 13 months ending with the previous complete month

    CurrentDate = DateTime.LocalNow(),
    CurrentMonthStart = Date.StartOfMonth(Date.From(CurrentDate)),

    // End date = previous month (complete data only)
    EndFilterDate = Date.AddMonths(CurrentMonthStart, -1),

    // Start date = 13 months before end date (rolling 13-month window)
    StartFilterDate = Date.AddMonths(EndFilterDate, -12),

    // Format reporting period for display
    ReportingPeriod = Date.ToText(StartFilterDate, "MM/yy") & " - " &
                      Date.ToText(EndFilterDate, "MM/yy"),

    // Apply date range filter (show all 2026 data up to previous month)
    FilteredMonths = Table.SelectRows(
        AddedSortOrder, each[Date]<> null and[Date] >=
                            StartFilterDate and[Date] <= EndFilterDate),

    // =================================================================
    // METADATA COLUMNS
    // =================================================================
    // Add reporting period metadata
    AddedReportingMeta = Table.AddColumn(FilteredMonths, "ReportingPeriod",
                                         each ReportingPeriod, type text),

    // Calculate number of unique months in the filtered dataset
    UniqueMonthsCount = Table.RowCount(
        Table.Group(FilteredMonths, {"Date"},
                    {{"Count", each Table.RowCount(_), type number}})),

    // Add month count to all rows
    AddedMonthCount = Table.AddColumn(AddedReportingMeta, "MonthsIncluded",
                                      each UniqueMonthsCount, type number),

    // Classify cases as High Impact or Administrative
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
        each let StartMonth = Date.ToText(StartFilterDate, "MMMM yyyy"),
        EndMonth = Date.ToText(EndFilterDate, "MMMM yyyy"),
        RefreshDate =
            DateTime.ToText(DateTime.LocalNow(), "MM/dd/yyyy hh:mm tt"),
        TodaysDate =
            Date.ToText(Date.From(DateTime.LocalNow()), "MMMM dd, yyyy") in
            "Rolling 13-Month Period: " &
            StartMonth & " - " & EndMonth & " | Today: " & TodaysDate &
            " | Updated: " & RefreshDate,
        type text),

    // Add timestamp for data refresh tracking
    AddedRefreshTime = Table.AddColumn(AddedSubtitle, "DataRefreshTime",
                                       each DateTime.LocalNow(), type datetime)

                           in AddedRefreshTime

// ___Det_case_dispositions_clearance
// 🕒 2026-02-13-18-05-00
// # Master_Automation/Detectives/___Det_case_dispositions_clearance_2026.m
// # Author: R. A. Carucci
// # Purpose: Import Detective case clearance and dispositions from restructured 2026-only workbook (_CCD_MOM table) with rolling 13-month window and robust % normalization.

let
    // =================================================================
    // FILE PATH AND TABLE LOAD
    // =================================================================
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Detectives\detectives_monthly.xlsx"),
        null, true
    ),
    
    // Load _CCD_MOM table (now contains 01-26 through 12-26 only)
    CCD_Table = Source{[Item="_CCD_MOM", Kind="Table"]}[Data],

    // =================================================================
    // REQUIRED ROW ORDER (EXACT LABELS)
    // =================================================================
    // These labels must match Excel exactly (including extra spaces)
    // Note: "Monthly Bureau Case  Clearance % " has DOUBLE space before "Clearance" and trailing space
    RequiredOrder = {
        "Active / Administratively Closed",
        "Arrest",
        "Complaint Signed",
        "Ex Cleared / Closed",
        "Juvenile Complaint",
        "Stationhouse Adjustment",
        "TOT DCP&P",
        "Unfounded / Closed",
        "Monthly Bureau Case  Clearance % ",  // Double space + trailing space (as in Excel)
        "YTD Bureau Case Clearance % "  // Trailing space (as in Excel)
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
    // Keep only rows that match the required order list
    // Note: Now uses exact match (not Text.Trim) to preserve Excel labels
    KeptRows = Table.SelectRows(
        CCD_Table,
        (r) => List.Contains(RequiredOrder, Record.Field(r, FirstColumnName))
    ),

    // =================================================================
    // ADD ROW SORT ORDER
    // =================================================================
    // Add Row_Sort column to maintain display order
    // Note: Now uses exact match (not Text.Trim) to preserve Excel labels
    WithRowSort = Table.AddColumn(
        KeptRows, "Row_Sort",
        each List.PositionOf(RequiredOrder, Record.Field(_, FirstColumnName)),
        Int64.Type
    ),
    
    // Sort rows by the defined order
    OrderedRows = Table.Sort(WithRowSort, {{"Row_Sort", Order.Ascending}}),

    // =================================================================
    // INITIAL TYPE CONVERSION (WIDE FORMAT)
    // =================================================================
    // Keep month columns as 'any' type for now (normalize after unpivot)
    TypedWide = Table.TransformColumnTypes(
        OrderedRows,
        {{FirstColumnName, type text}} & 
        List.Transform(MonthColumns, each {_, type any})
    ),

    // =================================================================
    // FLAG PERCENT ROWS
    // =================================================================
    // Mark rows that contain percentage values for special handling
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
    // Handle multiple formats:
    // - "50%" (text with %) → 0.50
    // - 50 (number > 1) → 0.50
    // - 0.50 (decimal) → 0.50
    // Excel now stores as decimals (per Claude update), but handle all formats
    Normalized = Table.AddColumn(
        Unpivoted, "Value",
        each
            let 
                v = [ValueRaw] 
            in
            if [Is_Percent] then
                // Handle percentage values
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
                        // If already decimal (0.50), keep it; if whole number (50), divide by 100
                        n  = if n0 = null then null
                             else if n0 > 1 then n0 / 100 
                             else n0
                    in  n
            else
                // Handle count values (non-percentage rows)
                try Number.From(v) otherwise null,
        type number
    ),
    
    // Remove the raw value column
    Cleaned = Table.RemoveColumns(Normalized, {"ValueRaw"}),

    // =================================================================
    // DATE PARSING FROM MM-YY FORMAT
    // =================================================================
    // Parse "01-26" → #date(2026, 1, 1)
    WithDate = Table.AddColumn(Cleaned, "Date", each
        let
            mTxt = [Month],
            Parts = Text.Split(mTxt, "-"),
            // Parts{0} = MM (month), Parts{1} = YY (year)
            MonthPart = if List.Count(Parts) >= 1 then Parts{0} else "01",
            YearPart = if List.Count(Parts) >= 2 then Parts{1} else "26",
            
            // Convert 2-digit year to full year
            y2 = try Number.From(YearPart) otherwise null,
            y4 = if y2 = null then null 
                 else if y2 >= 50 then 1900 + y2 
                 else 2000 + y2,
            
            // Convert month to number (01=1, 02=2, etc.)
            mNum = try Number.From(MonthPart) otherwise null
        in
            if mNum = null or y4 = null then null 
            else try #date(y4, mNum, 1) otherwise null,
        type date
    ),

    // =================================================================
    // ADDITIONAL DATE HELPER COLUMNS
    // =================================================================
    // Add normalized Month_Normalized column in MM-YY format
    WithNormalizedMonth = Table.AddColumn(WithDate, "Month_Normalized", each 
        if [Date] <> null then 
            Text.PadStart(Text.From(Date.Month([Date])), 2, "0") & "-" & 
            Text.End(Text.From(Date.Year([Date])), 2)
        else [Month], 
        type text),
    
    // Remove old Month and rename Month_Normalized to Month
    RemovedOldMonth = Table.RemoveColumns(WithNormalizedMonth, {"Month"}),
    RenamedMonth = Table.RenameColumns(RemovedOldMonth, {{"Month_Normalized", "Month"}}),
    
    // Month_Year: "January 2026"
    WithMonthYear = Table.AddColumn(RenamedMonth, "Month_Year", each 
        if [Date] = null then null 
        else Date.MonthName([Date]) & " " & Text.From(Date.Year([Date])), 
        type text),
    
    // Sort_Order: 202601 (numeric YYYYMM)
    WithSortOrder = Table.AddColumn(WithMonthYear, "Sort_Order", each 
        if [Date] = null then null 
        else Date.Year([Date]) * 100 + Date.Month([Date]), 
        Int64.Type),
    
    // Month_Abbrev: "01-26" (normalized format)
    WithAbbrev = Table.AddColumn(WithSortOrder, "Month_Abbrev", each 
        if [Date] = null then null 
        else Text.PadStart(Text.From(Date.Month([Date])), 2, "0") & "-" & 
             Text.End(Text.From(Date.Year([Date])), 2), 
        type text),

    // =================================================================
    // DISPOSITION CATEGORY GROUPING
    // =================================================================
    // Group dispositions into logical categories for analysis
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
    // DATE RANGE FILTER (ROLLING 13-MONTH WINDOW)
    // =================================================================
    // Table contains historical data from Jun 2023 onwards
    // Show rolling 13 months ending with the previous complete month
    
    CurrentDate     = Date.From(DateTime.LocalNow()),
    EndFilterDate   = Date.AddMonths(Date.StartOfMonth(CurrentDate), -1),
    
    // Start date = 13 months before end date (rolling 13-month window)
    StartFilterDate = Date.AddMonths(EndFilterDate, -12),

    // Filter to only rows within the date range
    FilteredMonths = Table.SelectRows(
        WithDispCat,
        each [Date] <> null and 
             [Date] >= StartFilterDate and 
             [Date] <= EndFilterDate
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

// ___STACP_pt_1_2
// 🕒 2026-02-13-16-30-00
// # Master_Automation/STACP/STACP_pt_1_2_FIXED.m
// # Author: R. A. Carucci
// # Purpose: Future-proof STACP high activity query with dynamic year detection for 13-month rolling window (works 2024-2099+).

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

// ___Patrol
let
    Source = Excel.Workbook(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Patrol\patrol_monthly.xlsm"), null, true),
    _mom_patrol_Table = Source{[Item="_mom_patrol",Kind="Table"]}[Data],
#"Changed Type" = Table.TransformColumnTypes(                                  \
    _mom_patrol_Table, {{"Tracked Items", type text },                         \
                         {"06-23", Int64.Type },                               \
                          {"07-23", Int64.Type },                              \
                           {"08-23", Int64.Type },                             \
                            {"09-23", Int64.Type },                            \
                             {"10-23", Int64.Type },                           \
                              {"11-23", Int64.Type },                          \
                               {"12-23", Int64.Type },                         \
                                {"01-24", Int64.Type },                        \
                                 {"02-24", Int64.Type },                       \
                                  {"03-24", Int64.Type },                      \
                                   {"04-24", Int64.Type },                     \
                                    {"05-24", Int64.Type },                    \
                                     {"06-24", Int64.Type },                   \
                                      {"07-24", Int64.Type },                  \
                                       {"08-24", Int64.Type },                 \
                                        {"09-24", Int64.Type },                \
                                         {"10-24", Int64.Type },               \
                                          {"11-24", Int64.Type },              \
                                           {"12-24", Int64.Type },             \
                                            {"01-25", Int64.Type },            \
                                             {"02-25", Int64.Type },           \
                                              {"03-25", Int64.Type },          \
                                               {"04-25", Int64.Type },         \
                                                {"05-25", Int64.Type },        \
                                                 {"06-25", Int64.Type },       \
                                                  {"07-25", Int64.Type },      \
                                                   {"08-25", Int64.Type },     \
                                                    {"09-25", Int64.Type },    \
                                                     {"10-25", Int64.Type },   \
                                                      {"11-25", Int64.Type },  \
                                                       {"12-25",               \
                                                        Int64.Type } })
in
#"Changed Type"

// ___REMU
let
    // 1. Load Excel & table
    WorkbookPath  = "C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\REMU\REMU_Monthly.xlsx",
    TableName     = "_mom_remu",
    Source        = Excel.Workbook(File.Contents(WorkbookPath), null, true),
    REMU_MoM      = Source{[Item=TableName,Kind="Table"]}[Data],

    // 2. Clean “Tracked Items”
    Cleaned       = Table.TransformColumns(
                      REMU_MoM,
                      {{"Tracked Items", each Text.Trim(Text.Clean(_)), type text}}
                    ),
    Filtered      = Table.SelectRows(
                      Cleaned,
                      each [Tracked Items] <> null and [Tracked Items] <> ""
                    ),

    // 3. Unpivot all “MM-YY” columns into [Month] & [Total]
    MonthCols     = List.Select(
                      Table.ColumnNames(Filtered),
                      each Text.Length(_) = 5 and Text.Contains(_,"-")
                    ),
    Unpivoted     = Table.Unpivot(
                      Filtered,
                      MonthCols,
                      "Month",
                      "Total"
                    ),

    // 4. Parse “MM-YY” → first-of-month date
    AddDate       = Table.AddColumn(
                      Unpivoted,
                      "PeriodDate",
                      each Date.FromText("01-" & [Month]),
                      type date
                    ),

    // 5. Convert Total to number
    ChangeType    = Table.TransformColumnTypes(
                      AddDate,
                      {{"Total", Int64.Type}}
                    ),

    // 6. Add MonthIndex (YYYYMM) for chronological sorting
    AddMonthIndex = Table.AddColumn(
                      ChangeType,
                      "MonthIndex",
                      each Date.Year([PeriodDate]) * 100 + Date.Month([PeriodDate]),
                      Int64.Type
                    ),

    // 7. Select only the final five columns
    Final         = Table.SelectColumns(
                      AddMonthIndex,
                      {
                        "Tracked Items",
                        "Month",
                        "PeriodDate",
                        "Total",
                        "MonthIndex"
                      }
                    )
in
    Final

// ___Benchmark
// ___Benchmark - FIXED for DAX compatibility
// Required by DAX measures: EventType (no space), MonthStart, MonthLabel
// Relationships: ___Benchmark[MonthStart] -> ___DimMonth[MonthStart], ___Benchmark[EventType] -> ___DimEventType[EventType]
//
// Source: 05_EXPORTS\Benchmark\ (use_force, show_force, vehicle_pursuit)

let
    BenchmarkBasePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark\",
    
    LoadLatestFile = (folderPath as text, eventType as text) =>
        let
            Source = Folder.Files(folderPath),
            FilteredFiles = Table.SelectRows(Source, each Text.EndsWith([Name], ".csv") or Text.EndsWith([Name], ".xlsx")),
            SortedFiles = Table.Sort(FilteredFiles, {{"Date modified", Order.Descending}}),
            LatestFile = if Table.RowCount(SortedFiles) > 0 then SortedFiles{0}[Content] else error "No files found in " & folderPath,
            LoadedData = if Text.EndsWith(SortedFiles{0}[Name], ".csv")
                then Csv.Document(LatestFile, [Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None])
                else Excel.Workbook(LatestFile){0}[Data],
            PromotedHeaders = Table.PromoteHeaders(LoadedData, [PromoteAllScalars=true]),
            // FIX: Use "EventType" (no space) - matches ___DimEventType and DAX
            AddedEventType = Table.AddColumn(PromotedHeaders, "EventType", each eventType, type text),
            AddedSource = Table.AddColumn(AddedEventType, "SourceFile", each SortedFiles{0}[Name], type text)
        in
            AddedSource,
    
    UseOfForce = try LoadLatestFile(BenchmarkBasePath & "use_force\", "Use of Force") 
                 otherwise #table(type table [Message = text], {{"No Use of Force data found"}}),
    ShowOfForce = try LoadLatestFile(BenchmarkBasePath & "show_force\", "Show of Force") 
                  otherwise #table(type table [Message = text], {{"No Show of Force data found"}}),
    VehiclePursuit = try LoadLatestFile(BenchmarkBasePath & "vehicle_pursuit\", "Vehicle Pursuit") 
                     otherwise #table(type table [Message = text], {{"No Vehicle Pursuit data found"}}),
    
    CombinedBenchmark = Table.Combine({UseOfForce, ShowOfForce, VehiclePursuit}),
    
    // FIX: Add MonthStart (required by DAX - Total Incidents Rolling 13, BM_Rolling13_Count, etc.)
    IncidentDateTyped = Table.TransformColumnTypes(CombinedBenchmark, {{"Incident Date", type datetime}}),
    AddMonthStart = Table.AddColumn(IncidentDateTyped, "MonthStart", each Date.StartOfMonth(Date.From([Incident Date])), type date),
    AddMonthLabel = Table.AddColumn(AddMonthStart, "MonthLabel", each Date.ToText([MonthStart], "MM-yy"), type text),
    AddMonthSort = Table.AddColumn(AddMonthLabel, "MonthSort", each Date.Year([MonthStart]) * 100 + Date.Month([MonthStart]), Int64.Type),
    
    // Type conversions for numeric columns used by DAX
    Typed = Table.TransformColumnTypes(AddMonthSort, {
        {"Badge Number", Int64.Type},
        {"# of Officers Involved", Int64.Type},
        {"# of Subjects", Int64.Type}
    }, "en-US"),
    
    Result = Typed,
#"Sorted Rows" = Table.Sort(Result, {{"MonthLabel", Order.Ascending } })
in
#"Sorted Rows"

// ___DimMonth
let
    Today = DateTime.Date(DateTime.LocalNow()),
    LastFullMonth = Date.EndOfMonth(Date.AddMonths(Today, -1)),
    FirstMonthStart = Date.StartOfMonth(Date.AddMonths(LastFullMonth, -12)),
    MonthStarts = List.Generate(() => FirstMonthStart, each _ <= LastFullMonth, each Date.AddMonths(_, 1)),
    ToTable = Table.FromList(MonthStarts, Splitter.SplitByNothing(), {"MonthStart"}),
    TypedDate = Table.TransformColumnTypes(ToTable, {{"MonthStart", type date}}),
    AddLabel = Table.AddColumn(TypedDate, "MonthLabel", each Date.ToText([MonthStart], "MM-yy"), type text),
    AddSort = Table.AddColumn(AddLabel, "MonthSort", each Date.Year([MonthStart]) * 100 + Date.Month([MonthStart]), Int64.Type)
in
    AddSort

// ___DimEventType
// Name this query: DimEventType
let
    Source = #table(
        {"EventType"},
        {
            {"Show of Force"},
            {"Use of Force"},
            {"Vehicle Pursuit"}
        }
    ),
    Typed = Table.TransformColumnTypes(Source, {{"EventType", type text}})
in
    Typed

// ___Overtime_Timeoff_v3
let
    /* =========================
       Paths & Config
       ========================= */
    OutputFolder     = "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Overtime_TimeOff\output",
    AnalyticsFolder  = "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Overtime_TimeOff\analytics_output",

    // Anchoring config: only anchor periods before cutover
    UseAnchoring     = true,
    CutoverLabel     = "09-25",  // Raw values from 09-25 onward

    // Convert CutoverLabel to a real date for proper comparison
    CutoverDate =
        let
            cYear  = Number.FromText("20" & Text.End(CutoverLabel, 2)),
            cMonth = Number.FromText(Text.Start(CutoverLabel, 2))
        in
#date(cYear, cMonth, 1),

    /* =========================
       Rolling 13-month window (exclude current month)
       ========================= */
    NowDT   = DateTime.LocalNow(),
    CurrY   = Date.Year(NowDT),
    CurrM   = Date.Month(NowDT),
    EndY    = if CurrM = 1 then CurrY - 1 else CurrY,
    EndM    = if CurrM = 1 then 12 else CurrM - 1,
    StartY  = EndY - 1,
    StartM  = EndM,

    StartDate = #date(StartY, StartM, 1),
    EndDate   = #date(EndY,   EndM,   1),

    // List of month starts within window
    MonthList = List.Generate(
        () => StartDate,
        each _ <= EndDate,
        each Date.AddMonths(_, 1)
    ),

    // Period keys: YYYY-MM and display labels: MM-YY
    PeriodKeysYYYYMM = List.Transform(MonthList, each
        Text.From(Date.Year(_)) & "-" & Text.PadStart(Text.From(Date.Month(_)), 2, "0")),
    PeriodLabelsMMYY = List.Transform(MonthList, each
        Text.PadStart(Text.From(Date.Month(_)), 2, "0") & "-" & Text.End(Text.From(Date.Year(_)), 2)),

    /* =========================
       Load latest FIXED_monthly_breakdown (legacy totals)
       ========================= */
    OutFiles      = Folder.Files(OutputFolder),
    FixedFiltered = Table.SelectRows(OutFiles, each Text.Contains([Name], "FIXED_monthly_breakdown") and Text.EndsWith([Name], ".csv")),
    FixedSorted   = Table.Sort(FixedFiltered, {{"Date modified", Order.Descending}}),
    FixedContent  = if Table.RowCount(FixedSorted) > 0 then FixedSorted{0}[Content] else null,
    FixedCsv      = if FixedContent <> null
                    then Csv.Document(FixedContent, [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv])
                    else #table({}, {}),

    FixedHeaders = Table.PromoteHeaders(FixedCsv, [PromoteAllScalars=true]),

    // Force canonical column order to prevent drift
    FixedReordered = Table.ReorderColumns(
        FixedHeaders,
        {"Year","Month","Month_Name","Period","Date",
         "Accrued_Comp_Time","Accrued_Overtime_Paid",
         "Employee_Sick_Time_Hours","Used_SAT_Time_Hours","Vacation_Hours",
         "Used_Comp_Time","Military_Leave_Hours","Injured_on_Duty_Hours"}
    ),

    FixedTypes = Table.TransformColumnTypes(
        FixedReordered,
        {{"Year", Int64.Type}, {"Month", Int64.Type}, {"Month_Name", type text},
         {"Period", type text}, {"Date", type date},
         {"Accrued_Comp_Time", type number}, {"Accrued_Overtime_Paid", type number},
         {"Employee_Sick_Time_Hours", type number}, {"Used_SAT_Time_Hours", type number},
         {"Vacation_Hours", type number}, {"Used_Comp_Time", type number},
         {"Military_Leave_Hours", type number}, {"Injured_on_Duty_Hours", type number}}
    ),

    // Filter to 13-month window (by YYYY-MM)
    Fixed13 = Table.SelectRows(FixedTypes, each List.Contains(PeriodKeysYYYYMM, [Period])),

    // Legacy (NON-accrual) categories only
    LegacySelect =
        Table.SelectColumns(
            Fixed13,
            {"Period","Employee_Sick_Time_Hours","Used_SAT_Time_Hours","Vacation_Hours",
             "Used_Comp_Time","Military_Leave_Hours","Injured_on_Duty_Hours"}
        ),

    LegacyUnpivot =
        Table.Unpivot(
            LegacySelect,
            {"Employee_Sick_Time_Hours","Used_SAT_Time_Hours","Vacation_Hours",
             "Used_Comp_Time","Military_Leave_Hours","Injured_on_Duty_Hours"},
            "Orig","Value"
        ),

    NameMap =
#table(
            {"Orig", "Time_Category"},
            {
                {"Employee_Sick_Time_Hours","Employee Sick Time (Hours)"},
                {"Used_SAT_Time_Hours","Used SAT Time (Hours)"},
                {"Vacation_Hours","Vacation (Hours)"},
                {"Used_Comp_Time","Comp (Hours)"},
                {"Military_Leave_Hours","Military Leave (Hours)"},
                {"Injured_on_Duty_Hours","Injured on Duty (Hours)"}
            }
        ),

    LegacyJoin  = Table.NestedJoin(LegacyUnpivot, {"Orig"}, NameMap, {"Orig"}, "Lk", JoinKind.LeftOuter),
    LegacyNamed = Table.TransformColumns(LegacyJoin, {{"Lk", each if _ <> null and Table.RowCount(_) > 0 then _{0}[Time_Category] else null}}),
    LegacyPrep  =
        Table.TransformColumns(
            Table.RenameColumns(LegacyNamed, {{"Lk","Time_Category"}}),
            {{"Value", each if _ = null then 0 else _, type number}}
        ),

    // Add display PeriodLabel (MM-yy) for consistent joining
    LegacyWithLabel =
        Table.AddColumn(
            LegacyPrep, "PeriodLabel",
            each Date.ToText(Date.FromText([Period] & "-01"), "MM-yy"),
            type text
        ),

    /* =========================
       Load sworn-split monthly_breakdown (analytics_output)
       ========================= */
    AFiles = Folder.Files(AnalyticsFolder),
    MBFile = Table.SelectRows(AFiles, each [Name] = "monthly_breakdown.csv"),
    MBCont = if Table.RowCount(MBFile) > 0 then MBFile{0}[Content] else null,
    MBCsv  = if MBCont <> null
             then Csv.Document(MBCont,[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv])
             else #table({},{}),

    MBHeaders = Table.PromoteHeaders(MBCsv, [PromoteAllScalars=true]),
    MBTypes   = Table.TransformColumnTypes(
        MBHeaders,
        {{"YearMonth", type text}, {"Class", type text}, {"Metric", type text}, {"Hours", type number}}
    ),

    // Keep window + only accrual metrics
    MBWindow  = Table.SelectRows(MBTypes, each List.Contains(PeriodKeysYYYYMM, [YearMonth])),
    MBAccrual = Table.SelectRows(MBWindow, each [Metric] = "Accrued Comp. Time" or [Metric] = "Accrued Overtime"),

    MBWithLabel =
        Table.AddColumn(
            MBAccrual, "PeriodLabel",
            each let d = Date.FromText([YearMonth] & "-01") in Date.ToText(d, "MM-yy"),
            type text
        ),

    MBWithCat =
        Table.AddColumn(
            MBWithLabel, "Time_Category",
            each if [Metric] = "Accrued Comp. Time"
                 then "Accrued Comp. Time - " & (if [Class] = "Sworn" then "Sworn" else "Non-Sworn")
                 else "Accrued Overtime - " & (if [Class] = "Sworn" then "Sworn" else "Non-Sworn"),
            type text
        ),

    WithBaseMetric =
        Table.AddColumn(
            MBWithCat,
            "BaseMetric",
            each if Text.StartsWith([Time_Category], "Accrued Comp. Time") then "Accrued Comp. Time"
                 else if Text.StartsWith([Time_Category], "Accrued Overtime") then "Accrued Overtime"
                 else null,
            type text
        ),

    /* =========================
       Optional anchor: use last published summary to force exact totals
       ========================= */
    Candidates =
        Table.SelectRows(
            AFiles,
            each Text.Contains([Name], "Monthly_Accrual_and_Usage_Summary") and Text.EndsWith([Name], ".csv")
        ),

    IsPriorFile = (content as binary) as logical =>
        let
            Raw  = Csv.Document(content,[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),
            T    = Table.PromoteHeaders(Raw, [PromoteAllScalars=true]),
            Cols = List.RemoveItems(Table.ColumnNames(T), {"Time Category"})
        in
            List.Contains(Cols, "08-25") and not List.Contains(Cols, "09-25"),

    WithFlag    = Table.AddColumn(Candidates, "IsPrior", each IsPriorFile([Content]), type logical),
    Filtered    = Table.SelectRows(WithFlag, each [IsPrior] = true),
    PriorSorted = Table.Sort(Filtered, {{"Date modified", Order.Descending}}),
    PriorCont   = if Table.RowCount(PriorSorted) > 0 then PriorSorted{0}[Content] else null,
    PriorCsvRaw = if PriorCont <> null then Csv.Document(PriorCont, [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]) else #table({},{}),
    PriorCsv    = Table.PromoteHeaders(PriorCsvRaw, [PromoteAllScalars=true]),
    HasTimeCategory = List.Contains(Table.ColumnNames(PriorCsv), "Time Category"),

    PriorAccruals =
        if HasTimeCategory then
            let
                Keep = Table.SelectRows(PriorCsv, each [#"Time Category"] = "Accrued Comp. Time" or [#"Time Category"] = "Accrued Overtime"),
                Unp  = Table.UnpivotOtherColumns(Keep, {"Time Category"}, "Period", "Total"),
                Ren  = Table.RenameColumns(Unp, {{"Time Category","Metric"}}),
                Typ  = Table.TransformColumnTypes(Ren, {{"Total", type number}})
            in
                Typ
        else
#table({"Metric", "Period", "Total"}, {}),

    PriorAccrualsNorm =
        let
            Trimmed  = Table.TransformColumns(PriorAccruals, {{"Metric", Text.Trim, type text}, {"Period", Text.Trim, type text}}),
            WithLabel =
                Table.AddColumn(
                    Trimmed, "PeriodLabel",
                    each let
                        mm = Text.Start([Period], 2),
                        yy = Text.End([Period], 2),
                        y  = Number.FromText("20" & yy),
                        m  = Number.FromText(mm),
                        d  = #date(y, m, 1)
                    in
                        Date.ToText(d, "MM-yy"),
                    type text
                ),
            KeepCols = Table.SelectColumns(WithLabel, {"Metric","PeriodLabel","Total"})
        in
            KeepCols,

    ForScaleOnly = Table.SelectRows(WithBaseMetric, each [BaseMetric] <> null),

    NewTotals =
        Table.Group(
            ForScaleOnly,
            {"BaseMetric","PeriodLabel"},
            {{"NewTotal", each List.Sum([Hours]), type number}}
        ),

    PriorJoin =
        Table.NestedJoin(
            NewTotals, {"BaseMetric","PeriodLabel"},
            PriorAccrualsNorm, {"Metric","PeriodLabel"},
            "Prior", JoinKind.LeftOuter
        ),

    WithFactor =
        Table.AddColumn(
            PriorJoin, "Scale",
            each let
                pYear  = Number.FromText("20" & Text.End([PeriodLabel], 2)),
                pMonth = Number.FromText(Text.Start([PeriodLabel], 2)),
                pDate  = #date(pYear, pMonth, 1),

                apply = UseAnchoring and pDate < CutoverDate,

                has   = [Prior] <> null and Table.RowCount([Prior]) > 0,
                prior = if has then [Prior]{0}[Total] else null,
                newv  = [NewTotal]
            in
                if apply and has and newv <> null and newv <> 0 then prior / newv else 1.0,
            type number
        ),

    MBJoin =
        Table.NestedJoin(
            WithBaseMetric, {"BaseMetric","PeriodLabel"},
            WithFactor,     {"BaseMetric","PeriodLabel"},
            "F", JoinKind.LeftOuter
        ),

    MBScaled =
        Table.AddColumn(
            MBJoin, "Value",
            each let
                isAccrual = [BaseMetric] <> null,
                ftable    = [F]
            in
                if isAccrual then
                    [Hours] * (
                        if ftable <> null and Table.RowCount(ftable) > 0 and Value.Is(ftable{0}[Scale], Number.Type)
                        then ftable{0}[Scale] else 1.0
                    )
                else
                    [Hours],
            type number
        ),

    MBFinal = Table.SelectColumns(MBScaled, {"PeriodLabel","Time_Category","Value"}),

    /* =========================
       Combine long tables
       ========================= */
    LegacyLong = Table.SelectColumns(LegacyWithLabel, {"PeriodLabel","Time_Category","Value"}),

    // Remove Vacation (Hours)
    LegacyLongFiltered = Table.SelectRows(LegacyLong, each [Time_Category] <> "Vacation (Hours)"),

    CombinedLong = Table.Combine({LegacyLongFiltered, MBFinal}),

    /* =========================
       Output as LONG table (no MM-YY pivot columns)
       Builds full 13-month grid per Time_Category and fills missing values with 0
       Adds PeriodDate + DateSortKey (yyyyMMdd)
       ========================= */
    PeriodDim =
        let
            T0 = Table.FromList(PeriodLabelsMMYY, Splitter.SplitByNothing(), {"PeriodLabel"}, null, ExtraValues.Error),
            T1 = Table.AddColumn(
                    T0, "PeriodDate",
                    each #date(
                        2000 + Number.FromText(Text.End([PeriodLabel], 2)),
                        Number.FromText(Text.Start([PeriodLabel], 2)),
                        1
                    ),
                    type date
                 ),
            T2 = Table.AddColumn(T1, "PeriodKey", each Date.ToText([PeriodDate], "yyyy-MM"), type text),
            T3 = Table.AddColumn(T2, "DateSortKey", each Number.FromText(Date.ToText([PeriodDate], "yyyyMMdd")), Int64.Type)
        in
            T3,

    Categories =
        Table.Distinct(
            Table.SelectColumns(CombinedLong, {"Time_Category"})
        ),

    Grid =
        Table.AddColumn(Categories, "Periods", each PeriodDim, type table),

    ExpandedGrid =
        Table.ExpandTableColumn(
            Grid,
            "Periods",
            {"PeriodLabel","PeriodDate","PeriodKey","DateSortKey"},
            {"PeriodLabel","PeriodDate","PeriodKey","DateSortKey"}
        ),

    Joined =
        Table.NestedJoin(
            ExpandedGrid,
            {"Time_Category","PeriodLabel"},
            CombinedLong,
            {"Time_Category","PeriodLabel"},
            "J",
            JoinKind.LeftOuter
        ),

    WithValue =
        Table.AddColumn(
            Joined,
            "Value",
            each if [J] <> null and Table.RowCount([J]) > 0 then [J]{0}[Value] else 0,
            type number
        ),

    RemovedJoin = Table.RemoveColumns(WithValue, {"J"}),

    Reordered =
        Table.ReorderColumns(
            RemovedJoin,
            {"Time_Category","PeriodLabel","PeriodDate","PeriodKey","DateSortKey","Value"}
        ),

    Sorted = Table.Sort(Reordered, {{"DateSortKey", Order.Ascending}, {"Time_Category", Order.Ascending}})
in
    Sorted

// ___ResponseTimeCalculator
// ==============================================================================
// RESPONSE TIMES M CODE - COMPLETE FIX WITH DATE SORT KEY
// Query Name: ___ResponseTimeCalculator
// ==============================================================================
// FIXES:
// 1. Ensures Average_Response_Time column exists (fixes measure errors)
// 2. Adds Date_Sort_Key for proper chronological sorting
// 3. Properly handles column naming and types
// ==============================================================================

let
    // ========================================================================
    // LOAD BACKFILL DATA (Nov 2024 - Oct 2025)
    // ========================================================================
    
    BackfillRaw = Csv.Document(
        File.Contents("C:\Dev\PowerBI_Date\Backfill\2025_10\response_time\2025_10_Average Response Times  Values are in mmss.csv"),
        [Delimiter=",", Encoding=1252, QuoteStyle=QuoteStyle.None]
    ),
    BackfillHeaders = Table.PromoteHeaders(BackfillRaw, [PromoteAllScalars=true]),
    
    // Rename columns - handle both possible column names
    BackfillRenamed = Table.RenameColumns(
        BackfillHeaders,
        {
            {"Response Type", "Response_Type"},
            {"First Response_Time_MMSS", "Response_Time_MMSS"},
            {"MM-YY", "MM-YY"}
        },
        MissingField.Ignore
    ),
    
    // Ensure MM-YY column exists (may already be named correctly)
    BackfillWithMMYY = if Table.HasColumns(BackfillRenamed, "MM-YY") then
        BackfillRenamed
    else if Table.HasColumns(BackfillRenamed, "MM_YY") then
        Table.RenameColumns(BackfillRenamed, {{"MM_YY", "MM-YY"}})
    else
        BackfillRenamed,
    
    // Calculate Average_Response_Time from MM:SS format (CRITICAL - measures need this!)
    BackfillWithAvg = Table.AddColumn(
        BackfillWithMMYY,
        "Average_Response_Time",
        each let
            timeStr = Text.Trim(Text.From([Response_Time_MMSS])),
            parts = Text.Split(timeStr, ":"),
            minutes = if List.Count(parts) >= 2 then
                let
                    mins = Number.From(parts{0}),
                    secs = Number.From(parts{1}),
                    totalMins = mins + (secs / 60.0)
                in
                    totalMins
            else
                null
        in
            minutes,
        type number
    ),
    
    // Add YearMonth from MM-YY (e.g., "11-24" -> "2024-11")
    BackfillWithYearMonth = Table.AddColumn(
        BackfillWithAvg,
        "YearMonth",
        each let
            mmYY = Text.Trim(Text.From([#"MM-YY"])),
            parts = Text.Split(mmYY, "-"),
            yearMonth = if List.Count(parts) >= 2 then
                let
                    mm = parts{0},
                    yy = "20" & parts{1},
                    yearMonthStr = yy & "-" & Text.PadStart(mm, 2, "0")
                in
                    yearMonthStr
            else
                null
        in
            yearMonth,
        type text
    ),
    
    // Add Date_Sort_Key - proper date format (yyyy-mm-dd) for sorting
    // For monthly data, use first day of month (yyyy-mm-01)
    BackfillWithDateKey = Table.AddColumn(
        BackfillWithYearMonth,
        "Date_Sort_Key",
        each let
            yearMonth = [YearMonth],
            // Convert "2024-11" to proper Date format "2024-11-01"
            dateValue = try 
                let
                    // Ensure format is yyyy-mm-dd
                    dateStr = yearMonth & "-01",
                    parsed = Date.FromText(dateStr)
                in
                    parsed
            otherwise null
        in
            dateValue,
        type date
    ),
    
    // ========================================================================
    // LOAD NOVEMBER 2025 DATA (ETL Output)
    // ========================================================================
    
    Nov2025Raw = Csv.Document(
        File.Contents("C:\Dev\PowerBI_Date\Backfill\2025_12\response_time\2025_12_Average_Response_Times__Values_are_in_mmss.csv"),
        [Delimiter=",", Encoding=1252, QuoteStyle=QuoteStyle.None]
    ),
    Nov2025Headers = Table.PromoteHeaders(Nov2025Raw, [PromoteAllScalars=true]),
    
    // Rename columns
    Nov2025Renamed = Table.RenameColumns(
        Nov2025Headers,
        {
            {"Response Type", "Response_Type"},
            {"First Response_Time_MMSS", "Response_Time_MMSS"},
            {"MM-YY", "MM-YY"}
        },
        MissingField.Ignore
    ),
    
    // Ensure MM-YY column exists
    Nov2025WithMMYY = if Table.HasColumns(Nov2025Renamed, "MM-YY") then
        Nov2025Renamed
    else if Table.HasColumns(Nov2025Renamed, "MM_YY") then
        Table.RenameColumns(Nov2025Renamed, {{"MM_YY", "MM-YY"}})
    else
        Nov2025Renamed,
    
    // Calculate Average_Response_Time (CRITICAL - measures need this!)
    Nov2025WithAvg = Table.AddColumn(
        Nov2025WithMMYY,
        "Average_Response_Time",
        each let
            timeStr = Text.Trim(Text.From([Response_Time_MMSS])),
            parts = Text.Split(timeStr, ":"),
            minutes = if List.Count(parts) >= 2 then
                let
                    mins = Number.From(parts{0}),
                    secs = Number.From(parts{1}),
                    totalMins = mins + (secs / 60.0)
                in
                    totalMins
            else
                null
        in
            minutes,
        type number
    ),
    
    // Add YearMonth
    Nov2025WithYearMonth = Table.AddColumn(
        Nov2025WithAvg,
        "YearMonth",
        each let
            mmYY = Text.Trim(Text.From([#"MM-YY"])),
            parts = Text.Split(mmYY, "-"),
            yearMonth = if List.Count(parts) >= 2 then
                let
                    mm = parts{0},
                    yy = "20" & parts{1},
                    yearMonthStr = yy & "-" & Text.PadStart(mm, 2, "0")
                in
                    yearMonthStr
            else
                null
        in
            yearMonth,
        type text
    ),
    
    // Add Date_Sort_Key - proper date format (yyyy-mm-dd) for sorting
    // For monthly data, use first day of month (yyyy-mm-01)
    Nov2025WithDateKey = Table.AddColumn(
        Nov2025WithYearMonth,
        "Date_Sort_Key",
        each let
            yearMonth = [YearMonth],
            // Convert "2025-11" to proper Date format "2025-11-01"
            dateValue = try 
                let
                    // Ensure format is yyyy-mm-dd
                    dateStr = yearMonth & "-01",
                    parsed = Date.FromText(dateStr)
                in
                    parsed
            otherwise null
        in
            dateValue,
        type date
    ),
    
    // ========================================================================
    // COMBINE DATASETS
    // ========================================================================
    
    Combined = Table.Combine({BackfillWithDateKey, Nov2025WithDateKey}),
    
    // ========================================================================
    // ENSURE ALL REQUIRED COLUMNS EXIST AND ARE CORRECT TYPE
    // ========================================================================
    
    // Verify Average_Response_Time exists (this fixes the measure errors)
    Verified = if Table.HasColumns(Combined, "Average_Response_Time") then
        // Ensure it's numeric type
        Table.TransformColumnTypes(
            Combined,
            {{"Average_Response_Time", type number}},
            "en-US"
        )
    else
        // If somehow missing, add it (shouldn't happen but safety check)
        Table.AddColumn(Combined, "Average_Response_Time", each null, type number),
    
    // Ensure Response_Type is text and Average_Response_Time is number
    Typed = Table.TransformColumnTypes(
        Verified,
        {
            {"Response_Type", type text},
            {"Response_Time_MMSS", type text},
            {"MM-YY", type text},
            {"YearMonth", type text},
            {"Date_Sort_Key", type date},
            {"Average_Response_Time", type number}  // Explicitly ensure type is set
        },
        "en-US"
    ),
    
    // ========================================================================
    // ADD COLUMNS THAT DAX MEASURES EXPECT (Summary_Type, Category, Date)
    // ========================================================================
    
    // Add Summary_Type and Category columns (for DAX compatibility)
    WithDAXColumns = Table.AddColumn(
        Table.AddColumn(
            Typed,
            "Summary_Type",
            each "Response_Type",
            type text
        ),
        "Category",
        each [Response_Type],
        type text
    ),
    
    // Add Date column (alias for Date_Sort_Key for DAX compatibility)
    WithDateColumn = Table.AddColumn(
        WithDAXColumns,
        "Date",
        each [Date_Sort_Key],
        type date
    ),
    
    // ========================================================================
    // SELECT FINAL COLUMNS IN CORRECT ORDER
    // ========================================================================
    
    // Final verification: Ensure Average_Response_Time exists before selecting
    FinalVerified = if Table.HasColumns(WithDateColumn, "Average_Response_Time") then
        WithDateColumn
    else
        // Emergency fallback: Add the column if missing
        Table.AddColumn(
            WithDateColumn,
            "Average_Response_Time",
            each null,
            type number
        ),
    
    // Select columns - include all columns needed for DAX measures
    Result = Table.SelectColumns(
        FinalVerified,
        {
            "YearMonth",
            "Date_Sort_Key",      // Date sort key for chronological sorting
            "Date",               // Date column (alias) for DAX measures
            "Response_Type",
            "Summary_Type",       // For DAX compatibility
            "Category",           // For DAX compatibility (matches Response_Type)
            "Average_Response_Time",  // ← THIS COLUMN FIXES THE MEASURE ERRORS!
            "Response_Time_MMSS",
            "MM-YY"
        }
    )
    
in
    Result

// ==============================================================================
// KEY POINTS:
// 1. Average_Response_Time column is CREATED and VERIFIED to exist
// 2. Date_Sort_Key added as proper Date type in yyyy-mm-dd format
//    - For monthly aggregated data, uses first day of month (yyyy-mm-01)
//    - Example: "2024-11" becomes Date(2024-11-01)
// 3. Date column added as alias to Date_Sort_Key (for DAX measure compatibility)
// 4. Summary_Type and Category columns added (for DAX measure compatibility)
// 5. Column types are explicitly set to ensure compatibility
// 6. All required columns are selected in final output
// ==============================================================================

// ___Traffic
// 🕒 2025-09-08-15-30-00
// Project: Traffic/Traffic_Monthly.xlsx
// Author: R. A. Carucci
// Purpose: Traffic data with corrected totals calculation

let
    Source = Excel.Workbook(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Traffic\Traffic_Monthly.xlsx"), null, true),
    _mom_traffic_Table = Source{[Item="_mom_traffic",Kind="Table"]}[Data],
#"Changed Type" = Table.TransformColumnTypes(                                  \
    _mom_traffic_Table, {{"Tracked Items", type text },                        \
                          {"06-23", Int64.Type },                              \
                           {"07-23", Int64.Type },                             \
                            {"08-23", Int64.Type },                            \
                             {"09-23", Int64.Type },                           \
                              {"10-23", Int64.Type },                          \
                               {"11-23", Int64.Type },                         \
                                {"12-23", Int64.Type },                        \
                                 {"01-24", Int64.Type },                       \
                                  {"02-24", Int64.Type },                      \
                                   {"03-24", Int64.Type },                     \
                                    {"04-24", Int64.Type },                    \
                                     {"05-24", Int64.Type },                   \
                                      {"06-24", Int64.Type },                  \
                                       {"07-24", Int64.Type },                 \
                                        {"08-24", Int64.Type },                \
                                         {"09-24", Int64.Type },               \
                                          {"10-24", Int64.Type },              \
                                           {"11-24", Int64.Type },             \
                                            {"12-24", Int64.Type },            \
                                             {"01-25", Int64.Type },           \
                                              {"02-25", Int64.Type },          \
                                               {"03-25", Int64.Type },         \
                                                {"04-25", Int64.Type },        \
                                                 {"05-25", Int64.Type },       \
                                                  {"06-25", Int64.Type },      \
                                                   {"07-25", Int64.Type },     \
                                                    {"08-25", Int64.Type },    \
                                                     {"09-25", Int64.Type },   \
                                                      {"10-25", Int64.Type },  \
                                                       {"11-25", Int64.Type }, \
                                                        {"12-25",              \
                                                         Int64.Type } }),
#"Filtered Rows" = Table.SelectRows(#"Changed Type",                           \
                                    each([Tracked Items]<> "Grand Total")),
    
    // Rolling 13-Month Logic Implementation
    CurrentDate = DateTime.LocalNow(),
    EndDate = Date.AddMonths(Date.StartOfMonth(DateTime.Date(CurrentDate)), -1),
    StartDate = Date.AddMonths(EndDate, -12),
    
    // Unpivot all date columns
    DateColumns = List.RemoveItems(Table.ColumnNames(#"Filtered Rows"), {"Tracked Items"}),
#"Unpivoted Columns" = Table.UnpivotOtherColumns(#"Filtered Rows",             \
                                                 {"Tracked Items" }, "Period", \
                                                  "Value"),

// Convert Period to proper date for filtering
#"Added Date Column" = Table.AddColumn(#"Unpivoted Columns", "Date", each
        let
            monthPart = Text.Start([Period], 2),
            yearPart = "20" & Text.End([Period], 2),
            fullDate = monthPart & "/01/" & yearPart
        in
            Date.From(fullDate)),

// Apply Rolling 13-Month Filter
#"Filtered Rolling Window" = Table.SelectRows(#"Added Date Column", 
        each [Date] >= StartDate and [Date] <= EndDate),

// Separate arrest details from totals for recalculation
#"Arrest Details Only" = Table.SelectRows(#"Filtered Rolling Window", 
        each [Tracked Items] <> "Total - Arrest(s)"),

// Calculate correct arrest totals by period
#"Arrest Components" = Table.SelectRows(#"Arrest Details Only", each
        [Tracked Items] = "Criminal Warrant Arrest" or
        [Tracked Items] = "DUI Arrest" or 
        [Tracked Items] = "Self-Initiated Arrest" or
        [Tracked Items] = "Motor Vehicle Warrant"),

#"Grouped Arrest Totals" = Table.Group(#"Arrest Components", {"Period" }, 
        {{"Calculated Total", each List.Sum([Value]), type number}}),

#"Added Corrected Totals" = Table.AddColumn(#"Grouped Arrest Totals",          \
                                            "Tracked Items", 
        each "Total - Arrest(s)"),

#"Renamed Total Value" = Table.RenameColumns(#"Added Corrected Totals", 
        {{"Calculated Total", "Value"}}),

#"Reordered Total Columns" = Table.ReorderColumns(#"Renamed Total Value", 
        {"Tracked Items", "Period", "Value"}),

// Add Date column to corrected totals
#"Added Date to Totals" = Table.AddColumn(#"Reordered Total Columns", "Date",  \
                                          each
        let
            monthPart = Text.Start([Period], 2),
            yearPart = "20" & Text.End([Period], 2),
            fullDate = monthPart & "/01/" & yearPart
        in
            Date.From(fullDate)),

// Combine corrected totals with other data
#"Combined Data" = Table.Combine({#"Arrest Details Only",                      \
                                  #"Added Date to Totals" }),

// Add currency flag and other columns
#"Added Currency Flag" = Table.AddColumn(#"Combined Data", "Is Currency", each 
        if [Tracked Items] = "Parking Fees Collected" then "Yes" else "No"),

#"Added Window Info" = Table.AddColumn(#"Added Currency Flag", "Window Info",  \
                                       each
        "Rolling 13-Month Window: " & 
        Date.ToText(StartDate, "MMM yyyy") & " to " & 
        Date.ToText(EndDate, "MMM yyyy")),

#"Added Sort Order" = Table.AddColumn(#"Added Window Info", "Sort Order", each
        Date.Year([Date]) * 100 + Date.Month([Date])),

#"Added Period Label" = Table.AddColumn(#"Added Sort Order", "Period Label",   \
                                        each
        Date.ToText([Date], "MMM yyyy")),

#"Added Rolling Month" = Table.AddColumn(#"Added Period Label",                \
                                         "Rolling Month", each
        let
            MonthDiff = ((Date.Year([Date]) - Date.Year(StartDate)) * 12) + 
                       (Date.Month([Date]) - Date.Month(StartDate)) + 1
        in
            MonthDiff),

// Fix values: whole numbers for non-parking, keep precision for parking
#"Updated Values" = Table.AddColumn(#"Added Rolling Month", "Final Value", each
        if [Tracked Items] = "Parking Fees Collected" then 
            [Value]
        else 
            Number.RoundUp([Value], 0)),

#"Removed Original" = Table.RemoveColumns(#"Updated Values", {"Value" }),
#"Renamed Value" = Table.RenameColumns(#"Removed Original", {{"Final Value",   \
                                                              "Value" } })
in
#"Renamed Value"

// ___Social_Media
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
            (c) => if c = "Platform" then {
  c, type text} else {c, Int64.Type}
        ),
#"Changed Type" = Table.TransformColumnTypes(_stacp_mom_sm_Table, TypeList),

    // === ROLLING 13-MONTH WINDOW (full months only) ===
    // Today
    Today = Date.From(DateTime.LocalNow()),

    // End of window = start of last complete month (exclude current month)
    // Example: if Today = 2025-10-02, EndMonth = 2025-09-01
    EndMonth = Date.StartOfMonth(Date.AddMonths(Today, -1)),

    // Start of window = 12 months before EndMonth (inclusive, total = 13 months)
    // Example: StartMonth = 2024-09-01  → months: Sep-2024 ... Sep-2025
    StartMonth = Date.StartOfMonth(Date.AddMonths(EndMonth, -12)),

    // Build ordered list of the 13 month keys in "MM-yy" format to match your columns
    MonthDates = List.Transform({0..12}, each Date.AddMonths(StartMonth, _)),
    MonthKeys  = List.Transform(MonthDates, each Date.ToText(_, "MM-yy")),

    // Desired column order: Platform, [13 month keys], Total (if present)
    DesiredOrder = {"Platform"} & MonthKeys & {"Total"},

    // Some workbooks may be missing a month or Total—keep only columns that actually exist
    ExistingInOrder = List.Select(DesiredOrder, each List.Contains(ColumnNames, _)),

// Select (and order) the rolling 13-month columns
#"Selected Columns" = Table.SelectColumns(#"Changed Type", ExistingInOrder,    \
                                          MissingField.Ignore)

in
#"Selected Columns"

// ___SSOCC_Data
// 🕒 2025-08-18-01-19-11
// SSOCC/Service_Analysis_MoM_Tables_Fixed_v2
// Author: R. A. Carucci
// Purpose: Robust MoM table ingest, safe typing, correct month parsing (YY-MMM and MM-YY)

let
    // =================================================================
    // STEP 1: SOURCE
    // =================================================================
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\SSOCC\Archive\_SSOCC - Service Log.xlsx"),
        null,
        true
    ),

    // =================================================================
    // STEP 2: HELPERS
    // =================================================================
    MonthMap = [
        Jan = 1, Feb = 2, Mar = 3, Apr = 4, May = 5, Jun = 6,
        Jul = 7, Aug = 8, Sep = 9, Oct = 10, Nov = 11, Dec = 12
    ],

    IsMonthColumn = (c as text) as logical =>
        let
            t = Text.Trim(c),
            parts = Text.Split(t, "-"),
            ok =
                List.Count(parts) = 2 and
                (try Number.FromText(Text.Trim(parts{0})) otherwise null) <> null and
                (
                    (try Record.Field(MonthMap, Text.Proper(Text.Start(Text.Trim(parts{1}), 3))) otherwise null) <> null
                    or
                    (try Number.FromText(Text.Trim(parts{1})) otherwise null) <> null
                )
        in
            ok,

    ParsePeriodToDate = (p as nullable text) as nullable date =>
        let
            raw = if p = null then null else Text.Trim(p),
            parts = if raw = null then {
} else Text.Split(raw, "-"),
            d =
                if List.Count(parts) <> 2 then
                    null
                else
                    let
                        aTxt = Text.Trim(parts{0}),
                        bTxt = Text.Trim(parts{1}),
                        aNum = try Number.FromText(aTxt) otherwise null,
                        bNum = try Number.FromText(bTxt) otherwise null,

                        d1 =
                            if aNum <> null and aNum <= 12 and bNum <> null then
#date(2000 + bNum, aNum, 1)
                            else
                                null,

                        d2 =
                            if d1 = null and aNum <> null then
                                let
                                    monKey = Text.Proper(Text.Start(bTxt, 3)),
                                    monNum = try Record.Field(MonthMap, monKey) otherwise null
                                in
                                    if monNum <> null then #date(2000 + aNum, monNum, 1) else null
                            else
                                null
                    in
                        if d1 <> null then d1 else d2
        in
            d,

    EnsureText = (x as any) as text =>
        Text.Trim(Text.From(x)),

    EnsureInt64 = (x as any) as number =>
        let
            n = try Number.From(x) otherwise null
        in
            if n = null then 0 else Int64.From(n),

    StandardizeMoMTable = (tableName as text, sourceLabel as text) as table =>
        let
            Raw = try Source{[Item = tableName, Kind = "Table"]}[Data] otherwise null,
            Output =
                if Raw = null or Table.ColumnCount(Raw) = 0 then
#table(
                        {"Service/Product", "Service_Normalized", "Source_Table"},
                        {}
                    )
                else
                    let
                        Cols = Table.ColumnNames(Raw),

                        ServiceCol = Cols{0},

                        HasNorm = List.Contains(Cols, "ServiceName_Normalized"),
                        NormCol =
                            if HasNorm then
                                "ServiceName_Normalized"
                            else if List.Count(Cols) >= 2 then
                                Cols{1}
                            else
                                null,

                        MonthCols = List.Select(Cols, each IsMonthColumn(_)),

                        KeepCols =
                            if NormCol <> null then
                                List.Combine({{ServiceCol, NormCol}, MonthCols})
                            else
                                List.Combine({{ServiceCol}, MonthCols}),

                        Kept = Table.SelectColumns(Raw, KeepCols, MissingField.UseNull),

                        Renamed1 = Table.RenameColumns(Kept, {{ServiceCol, "Service/Product"}}, MissingField.Ignore),
                        Renamed2 =
                            if NormCol <> null then
                                Table.RenameColumns(Renamed1, {{NormCol, "Service_Normalized"}}, MissingField.Ignore)
                            else
                                Table.AddColumn(Renamed1, "Service_Normalized", each null, type text),

                        CleanTextCols = Table.TransformColumns(
                            Renamed2,
                            {
                                {"Service/Product", each EnsureText(_), type text},
                                {"Service_Normalized", each if _ = null then null else EnsureText(_), type text}
                            },
                            null,
                            MissingField.UseNull
                        ),

                        MonthTyped = Table.TransformColumns(
                            CleanTextCols,
                            List.Transform(MonthCols, each {_, each EnsureInt64(_), Int64.Type}),
                            null,
                            MissingField.UseNull
                        ),

                        Tagged = Table.AddColumn(MonthTyped, "Source_Table", each sourceLabel, type text)
                    in
                        Tagged
        in
            Output,

    // =================================================================
    // STEP 3: LOAD + STANDARDIZE TABLES
    // =================================================================
    T_ANALYSIS = StandardizeMoMTable("_ANALYSIS", "Priority Services"),
    T_TRAIN    = StandardizeMoMTable("_TRAIN",    "Training & Education"),
    T_SUR      = StandardizeMoMTable("_SUR",      "Technical Services"),
    T_MAIN     = StandardizeMoMTable("_MAIN",     "Support Services"),
    T_MEET     = StandardizeMoMTable("_MEET",     "Operational Services"),
    T_ADMIN    = StandardizeMoMTable("_ADMIN",    "Administrative Services"),

    CombinedTables = Table.Combine({T_ANALYSIS, T_TRAIN, T_SUR, T_MAIN, T_MEET, T_ADMIN}),

    // =================================================================
    // STEP 4: PRIORITY FLAG + CATEGORY
    // =================================================================
    PrioritySet = {
        "ANALYSIS FOR DETECTIVES",
        "ANALYSIS - DETECTIVES",
        "ANALYSIS FOR PATROL",
        "ANALYSIS - PATROL",
        "AVIGILON FLAG REVIEW",
        "CCTV SITE ANALYSIS",
        "ANALYSIS FOR CSB",
        "ANALYSIS - CSB"
    },

    AddedPriorityFlag = Table.AddColumn(
        CombinedTables,
        "Is_Priority_Service",
        each
            let
                svc  = Text.Upper(EnsureText([#"Service/Product"])),
                norm = if [Service_Normalized] = null then "" else Text.Upper(EnsureText([Service_Normalized]))
            in
                List.Contains(PrioritySet, svc) or List.Contains(PrioritySet, norm),
        type logical
    ),

    AddedServiceCategoryFinal = Table.AddColumn(
        AddedPriorityFlag,
        "Service_Category_Final",
        each if [Is_Priority_Service] then "Priority Services" else [Source_Table],
        type text
    ),

    AddedEmergencyServices = Table.AddColumn(
        AddedServiceCategoryFinal,
        "Service_Category",
        each
            let
                s = Text.Upper(EnsureText([#"Service/Product"]))
            in
                if Text.Contains(s, "EMERGENCY") or Text.Contains(s, "911") then "Emergency Services"
                else [Service_Category_Final],
        type text
    ),

    CleanedColumns = Table.RemoveColumns(AddedEmergencyServices, {"Service_Category_Final"}),

    // =================================================================
    // STEP 5: UNPIVOT
    // =================================================================
    UnpivotedData = Table.UnpivotOtherColumns(
        CleanedColumns,
        {"Service/Product", "Service_Normalized", "Source_Table", "Is_Priority_Service", "Service_Category"},
        "Period",
        "Value"
    ),

    // =================================================================
    // STEP 6: DATE + SORT KEYS
    // =================================================================
    AddedDate = Table.AddColumn(
        UnpivotedData,
        "Date",
        each ParsePeriodToDate([Period]),
        type date
    ),

    AddedMonthSort = Table.AddColumn(
        AddedDate,
        "Month_Sort_Order",
        each if [Date] = null then null else (Date.Year([Date]) * 100 + Date.Month([Date])),
        Int64.Type
    ),

    AddedFormattedDate = Table.AddColumn(
        AddedMonthSort,
        "Formatted_Date",
        each if [Date] = null then null else Date.ToText([Date], "MM-yy"),
        type text
    ),

    ValueFixed = Table.TransformColumns(
        AddedFormattedDate,
        {{"Value", each EnsureInt64(_), Int64.Type}},
        null,
        MissingField.UseNull
    ),

    // =================================================================
    // STEP 7: FINAL METADATA + TYPES
    // =================================================================
    AddedCategory   = Table.AddColumn(ValueFixed, "Category", each "SSOCC Services", type text),
    AddedDepartment = Table.AddColumn(AddedCategory, "Department", each "Police Department", type text),
    AddedUnit       = Table.AddColumn(AddedDepartment, "Unit", each "SSOCC", type text),

    SortedData = Table.Sort(
        AddedUnit,
        {
            {"Is_Priority_Service", Order.Descending},
            {"Service_Category", Order.Ascending},
            {"Month_Sort_Order", Order.Ascending},
            {"Service/Product", Order.Ascending}
        }
    ),

    FinalDataTypes = Table.TransformColumnTypes(
        SortedData,
        {
            {"Service/Product", type text},
            {"Service_Normalized", type text},
            {"Source_Table", type text},
            {"Is_Priority_Service", type logical},
            {"Service_Category", type text},
            {"Period", type text},
            {"Value", Int64.Type},
            {"Date", type date},
            {"Month_Sort_Order", Int64.Type},
            {"Formatted_Date", type text},
            {"Category", type text},
            {"Department", type text},
            {"Unit", type text}
        }
    ),
#"Sorted Rows" = Table.Sort(FinalDataTypes, {{"Period", Order.Ascending } }),
#"Filtered Rows" = Table.SelectRows(#"Sorted Rows", each true)
in
#"Filtered Rows"

// ___NIBRS_Monthly_Report
// 🕒 2025-09-03-16-15-00
// Project: NIBRS_Analysis/13_Month_Rolling_Clean
// Author: R. A. Carucci
// Purpose: Clean 13-month rolling NIBRS analysis without variable conflicts

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

// ___In_Person_Training
// 🕒 2025-11-10-17-30-00
// Project: Policy_Training / In_Person_Training
// Author: R. A. Carucci
// Purpose: Load In-Person training list from ETL output, preserving individual
// event records with dates

let
    // Load ETL workbook/sheet
    Source = Excel.Workbook(
        File.Contents("C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\02_ETL_Scripts\\Policy_Training_Monthly\\output\\policy_training_outputs.xlsx"),
        null, true),
    Tbl = Source{[Item = "InPerson_Prior_Month_List", Kind = "Sheet"]}[Data],
    Promoted = Table.PromoteHeaders(Tbl, [PromoteAllScalars = true]),

    // Handle either naming convention (with/without spaces)
    Aliases = {{"CourseDuration", "Course Duration"},
               {"TotalCost", "Total Cost"},
               {"AttendeesCount", "Attendees Count"}},
    Standardized = List.Accumulate(
        Aliases, Promoted,
        (state, pair) => // <--- ERROR WAS HERE
            if Table.HasColumns(state, {pair{0}}) and
            not Table.HasColumns(state, {pair{1}})
                    then Table.RenameColumns(state, {pair}) else state),

    // Keep expected columns (now includes dates to preserve individual events)
    Kept = Table.SelectColumns(Standardized,
                               {"Start date", "End date", "Course Name",
                                "Course Duration", "Total Cost",
                                "Attendees Count"},
                               MissingField.Ignore),

    // Strong typing + safe numeric coercion (ensures totals will sum)
    Coerced = Table.TransformColumns(
        Kept,
        {{"Start date", each try DateTime.From(_) otherwise null,
          type nullable datetime},
         {"End date", each try DateTime.From(_) otherwise null,
          type nullable datetime},
         {"Course Name", each if _ = null then "" else Text.From(_), type text},
         {"Course Duration",
          each try Number.RoundDown(Number.From(_)) otherwise 0, Int64.Type},
         {"Total Cost", each try Number.From(_) otherwise 0, type number},
         {"Attendees Count",
          each try Number.RoundDown(Number.From(_)) otherwise 0, Int64.Type}}),

    // Sort by Start date to match visual expectations
    Sorted = Table.Sort(Coerced, {{"Start date", Order.Ascending}}),

    // Create deterministic event identifier to keep duplicate course names
    // distinct in visuals
    WithEventId = Table.AddColumn(
        Sorted, "Event Id",
        each Text.Combine(
            {
                if                 [Start date]<> null then DateTime.ToText(
                    [Start date], "yyyy-MM-ddTHH:mm:ss") else "",
                    Text.Trim([Course Name]), Text.From([Course Duration]),
                    Text.From([Attendees Count]),
                    Text.From(Number.From([Total Cost]))
            },
            "|"),
        type text),
#"Changed Type" = Table.TransformColumnTypes(WithEventId,                      \
                                             {{"End date", type date },        \
                                               {"Start date", type date } })
in
    #"Changed Type"

// ___Cost_of_Training
// POLICY_TRAINING_ANALYTICS / Training_Log_Vertical
// Purpose: Unpivot Delivery_Cost_By_Month so months run DOWN the page (vertical).
// Filters to rolling 13-month window: same month one year earlier through previous month
// (e.g. Feb 2026 → 01-25 through 01-26). Matches project standard (Training Cost by Delivery Method).

let Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Policy_Training_Monthly\output\policy_training_outputs.xlsx"),
        null, true),
    Tbl = Source{[Item = "Delivery_Cost_By_Month", Kind = "Sheet"]}[Data],
    Promoted = Table.PromoteHeaders(Tbl, [PromoteAllScalars = true]),

    // Strong types for wide table
    TypedWide =
        if Table.HasColumns(Promoted, {"Delivery_Type", "Total"})
            then Table.TransformColumnTypes(
                Promoted,
                List.Combine(
                    {{{"Delivery_Type", type text}, {"Total", type number}},
                     List.Transform(
                         List.RemoveItems(Table.ColumnNames(Promoted),
                                          {"Delivery_Type", "Total"}),
                         each{_, type number})})) else Promoted,

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
    MonthList = List.Generate(() => Report_Start_Date, each _ <= Report_End_Date, each Date.AddMonths(_, 1)),
    PeriodLabelsMMYY = List.Transform(MonthList, each Text.PadStart(Text.From(Date.Month(_)), 2, "0") & "-" & Text.End(Text.From(Date.Year(_)), 2)),

    // Unpivot all month columns -> Period, Cost
    MonthCols = List.Difference(Table.ColumnNames(TypedWide),
                                {"Delivery_Type", "Total"}),
    Unpivoted = Table.Unpivot(TypedWide, MonthCols, "Period", "Cost"),

    // Keep only periods in the 13-month window (e.g. 01-25 through 01-26)
    Filtered = Table.SelectRows(Unpivoted, each List.Contains(PeriodLabelsMMYY, [Period])),

    // Add sort key so Period (MM-YY) sorts chronologically
    WithSort = Table.AddColumn(
        Filtered, "Period_Sort",
        each let mm = Number.FromText(Text.Start([Period], 2)),
        yy = Number.FromText(Text.End([Period], 2)),
        yyyy = if yy < 70 then 2000 + yy else 1900 + yy in yyyy * 100 + mm,
        Int64.Type),

    // Final types
    Final = Table.TransformColumnTypes(WithSort, {{"Delivery_Type", type text},
                                                  {"Period", type text},
                                                  {"Cost", type number},
                                                  {"Period_Sort", Int64.Type}})
                in Final

// ___chief_projects
let
    Source = Excel.Workbook(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Chief\chief_monthly.xlsx"), null, true),
    Table8_Table = Source{[Item="Table8",Kind="Table"]}[Data],
#"Changed Type" = Table.TransformColumnTypes(Table8_Table,                     \
                                             {{"Date", type date },            \
                                               {"Event", type text },          \
                                                {"Notes", type any },          \
                                                 {"Duration", type any },      \
                                                  {"Location", type any } }),

// Remove parentheses and numbers from Event column
#"Replaced Value" = Table.ReplaceValue(#"Changed Type", each[Event], each 
        if Text.Contains([Event], " (") then 
            Text.BeforeDelimiter([Event], " (")
        else 
            [Event]
    , Replacer.ReplaceValue, {"Event"})
in
#"Replaced Value"

// RootExportPath
"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Benchmark" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]

// EtlRootPath
"C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Benchmark" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]

// SourceMode
"Excel" meta [IsParameterQuery=true, List={"Excel", "Folder"}, DefaultValue="Excel", Type="Text", IsParameterQueryRequired=true]

// RangeStart
#datetime(2024, 1, 1, 0, 0, 0) meta[IsParameterQuery = true,                   \
                               Type = "DateTime",                              \
                               IsParameterQueryRequired = true]

// RangeEnd
#datetime(2099, 12, 31, 0, 0, 0) meta[IsParameterQuery = true,                 \
                                 Type = "DateTime",                            \
                                 IsParameterQueryRequired = true]

// RequiredTypes
let
    RequiredTypes = type table [
#"Officer Name" = text,
#"Badge Number" = Int64.Type,
        Rank = text,
        Organization = text,
#"Incident Number" = text,
#"Report Number" = text,
#"Incident Date" = datetime,
        Location = text,
#"Initial Contact" = text,
#"# of Officers Involved" = Int64.Type,
#"# of Subjects" = Int64.Type,
#"Subject type" = text,
#"Report Key" = text,
        SourceFile = text,
        SourceModified = datetime,
        EventType = text
    ]
in
    RequiredTypes

// fnGetFiles
(eventFolder as text) as table =>
let
    folderPath = RootExportPath & "\" & eventFolder,
    files = Folder.Files(folderPath),
    csv   = Table.SelectRows(files, each Text.Lower([Extension]) = ".csv"),
    keep  = Table.SelectColumns(csv, {"Content","Name","Date modified"})
in
    keep

// fnReadCsv
(content as binary, fileName as text, fileModified as datetime) as table =>
let
    src     = Csv.Document(content, [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    headers = Table.PromoteHeaders(src, [PromoteAllScalars=true]),
    typed   = Table.TransformColumnTypes(headers, {
                {"Badge Number", Int64.Type},
                {"# of Officers Involved", Int64.Type},
                {"# of Subjects", Int64.Type},
                {"Incident Date", type datetime}
             }, "en-US"),
    withSF  = Table.AddColumn(typed, "SourceFile", each fileName, type text),
    withSM  = Table.AddColumn(withSF, "SourceModified", each fileModified, type datetime)
in
    withSM

// fnEnsureColumns
(tbl as table, required as type) as table =>
let
    flds    = Type.RecordFields(required),
    names   = Record.FieldNames(flds),
    ensure  = List.Accumulate(names, tbl, (state, col) =>
                if Table.HasColumns(state, {col})
                then state
                else Table.AddColumn(state, col, each null, Value.Type(Record.Field(flds, col)[Type]))),
    casted  = Table.TransformColumnTypes(
                ensure,
                List.Transform(names, each {_, Value.Type(Record.Field(flds, _)[Type])}),
                "en-US")
in
    casted

// fnApplyRenameMap
(tbl as table, renameMap as list) as table =>
let
    renamed = if List.Count(renameMap)=0 then tbl else Table.RenameColumns(tbl, renameMap, MissingField.Ignore)
in
    renamed

// fnLoadRaw
(eventFolder as text, eventTypeName as text, renameMap as list) as table =>
let
    files    = fnGetFiles(eventFolder),
    rows     = List.Transform(Table.ToRecords(files), each fnReadCsv([Content],[Name],[Date modified])),
    combined = if List.Count(rows) = 0 then #table({}, {}) else Table.Combine(rows),
    renamed  = fnApplyRenameMap(combined, renameMap),
    withType = if Table.HasColumns(renamed, {"EventType"}) then renamed else Table.AddColumn(renamed, "EventType", each eventTypeName, type text),
    aligned  = fnEnsureColumns(withType, RequiredTypes),
    sorted   = Table.Sort(aligned, {{"Report Key", Order.Ascending}, {"SourceModified", Order.Descending}}),
    deduped  = Table.Distinct(sorted, {"Report Key"})
in
    deduped

// Parameters_Check
#table(
    {"Parameter","Value"},
    {
        {"RootExportPath", RootExportPath},
        {"EtlRootPath",    EtlRootPath},
        {"SourceMode",     SourceMode},
        {"RangeStart",     DateTime.ToText(RangeStart)},
        {"RangeEnd",       DateTime.ToText(RangeEnd)}
    }
)

// summons_13month_trend
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

// summons_top5_parking
// ___Summons_Top5_Parking (Standalone)
// Updated: 2026-02-17
// Purpose: Top 5 Parking Violations for LATEST MONTH (loads directly from Excel)

let
    // Load directly from Excel file
    Source = Excel.Workbook(
        File.Contents("C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"),
        null, 
        true
    ),
    
    // Get Summons_Data sheet
    Summons_Data_Sheet = Source{[Item="Summons_Data", Kind="Sheet"]}[Data],
    
    // Promote headers
    PromotedHeaders = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    
    // Change YearMonthKey to number type
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{"YearMonthKey", Int64.Type}, {"TYPE", type text}}),
    
    // Filter to Parking violations only
    FilteredParking = Table.SelectRows(ChangedType, each ([TYPE] = "P")),
    
    // Find LATEST month using YearMonthKey (integer sorting, not text!)
    LatestKey = List.Max(FilteredParking[YearMonthKey]),
    
    // Filter to latest month only
    FilteredLatestMonth = Table.SelectRows(FilteredParking, each [YearMonthKey] = LatestKey),
    
    // Group by OFFICER and count summons
    GroupedRows = Table.Group(
        FilteredLatestMonth, 
        {"OFFICER_DISPLAY_NAME", "Month_Year"}, 
        {{"Count", each Table.RowCount(_), type number}}
    ),
    
    // Sort by count descending
    SortedRows = Table.Sort(GroupedRows, {{"Count", Order.Descending}}),
    
    // Keep top 5
    Top5 = Table.FirstN(SortedRows, 5),
    
    // RENAME COLUMNS TO MATCH VISUAL EXPECTATIONS
    RenamedColumns = Table.RenameColumns(Top5, {
        {"OFFICER_DISPLAY_NAME", "Officer"}
    })
in
    RenamedColumns

// summons_all_bureaus
// ___Summons_All_Bureaus (Standalone)
// Updated: 2026-02-17
// Purpose: Summons by Bureau and Type for PREVIOUS COMPLETE MONTH (matches Top 5 Moving/Parking)

let
    // Previous complete month (e.g. in Feb 2026 show Jan 2026)
    PrevDate = Date.AddMonths(DateTime.Date(DateTime.LocalNow()), -1),
    PreviousMonthKey = Date.Year(PrevDate) * 100 + Date.Month(PrevDate),

    // Load directly from Excel file
    Source = Excel.Workbook(
        File.Contents("C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"),
        null, 
        true
    ),
    
    Summons_Data_Sheet = Source{[Item="Summons_Data", Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{"YearMonthKey", Int64.Type}, {"TYPE", type text}, {"WG2", type text}}),
    
    // Filter out UNKNOWN / blank WG2
    FilteredClean = Table.SelectRows(ChangedType, each [WG2] <> "UNKNOWN" and [WG2] <> null and [WG2] <> ""),
    
    // Filter to PREVIOUS COMPLETE MONTH (same as Top 5 Moving/Parking)
    FilteredLatestMonth = Table.SelectRows(FilteredClean, each [YearMonthKey] = PreviousMonthKey),
    
    // Group by Bureau (WG2) and Type - COMBINE HOUSING & OSO WITH PATROL
    GroupedRows = Table.Group(
        FilteredLatestMonth, 
        {"WG2", "TYPE"}, 
        {{"Count", each Table.RowCount(_), type number}}
    ),
    
    // Consolidate bureaus before pivot
    ConsolidatedBureaus = Table.TransformColumns(
        GroupedRows,
        {
  "WG2", each if _ = "HOUSING" or _ = "OFFICE OF SPECIAL OPERATIONS" then
                                      "PATROL DIVISION" else _}
    ),
    
    // Re-group after consolidation
    RegroupedRows = Table.Group(
        ConsolidatedBureaus,
        {"WG2", "TYPE"},
        {{"Count", each List.Sum([Count]), type number}}
    ),
    
    // Pivot by TYPE to get M, P columns (C might not exist after reclassification)
    PivotedColumn = Table.Pivot(
        RegroupedRows, 
        List.Distinct(RegroupedRows[TYPE]), 
        "TYPE", 
        "Count", 
        List.Sum
    ),
    
    // Add M column if missing
    AddM = if Table.HasColumns(PivotedColumn, "M") then PivotedColumn else Table.AddColumn(PivotedColumn, "M", each 0, Int64.Type),
    
    // Add P column if missing
    AddP = if Table.HasColumns(AddM, "P") then AddM else Table.AddColumn(AddM, "P", each 0, Int64.Type),
    
    // Replace null with 0 in M and P columns
    ReplacedValue = Table.ReplaceValue(AddP, null, 0, Replacer.ReplaceValue, {"M", "P"}),
    
    // Add total column (C might not exist, so use try/otherwise)
    AddedTotal = Table.AddColumn(
        ReplacedValue, 
        "Total", 
        each [M] + [P] + (try [C] otherwise 0),
        type number
    )
in
    AddedTotal

// ___Summons_Diagnostic
// ___Summons_Diagnostic
// Diagnostic query to see what's actually in the summons data
// Use this temporarily to understand the data structure

let
    Source = Excel.Workbook(
        File.Contents(
            "C:/Users/carucci_r/OneDrive - City of Hackensack/03_Staging/Summons/summons_powerbi_latest.xlsx"
        ),
        null,
        true
    ),
    ATS_Court_Data_Sheet = Source{[Item = "Summons_Data", Kind = "Sheet"]}[Data],
#"Promoted Headers" = 
        Table.PromoteHeaders(ATS_Court_Data_Sheet, [PromoteAllScalars = true]),
    
    // Get column names
    ColumnNames = Table.ColumnNames(#"Promoted Headers"),
    
    // Most recent month
    MaxYearMonthKey = List.Max(#"Promoted Headers"[YearMonthKey]),
    Recent = Table.SelectRows(#"Promoted Headers", each [YearMonthKey] = MaxYearMonthKey),
    
    // Show distinct TYPE values
    DistinctTypes = Table.Distinct(Table.SelectColumns(Recent, {"TYPE"})),
    
    // Show distinct WG2 values
    DistinctWG2 = Table.Distinct(Table.SelectColumns(Recent, {"WG2"})),
    
    // Count by TYPE
    TypeCounts = Table.Group(
        Recent,
        {"TYPE"},
        {{"Count", each Table.RowCount(_), Int64.Type}}
    ),
    
    // Sample of recent data
    Sample = Table.FirstN(Recent, 10)
in
    Sample

// summons_top5_moving
// ___Summons_Top5_Moving (Standalone)
// Updated: 2026-02-17
// Purpose: Top 5 Moving Violations for PREVIOUS COMPLETE MONTH (so "January export" shows 01-26, not partial Feb)

let
    // Previous complete month (e.g. in Feb 2026 show Jan 2026 = 01-26)
    PrevDate = Date.AddMonths(DateTime.Date(DateTime.LocalNow()), -1),
    PrevYear = Date.Year(PrevDate),
    PrevMonth = Date.Month(PrevDate),
    PreviousMonthKey = PrevYear * 100 + PrevMonth,
    MonthYearText = Text.PadStart(Number.ToText(PrevMonth), 2, "0") & "-" & Text.End(Number.ToText(PrevYear), 2),

    // Load directly from Excel file
    Source = Excel.Workbook(
        File.Contents("C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"),
        null, 
        true
    ),
    
    // Get Summons_Data sheet
    Summons_Data_Sheet = Source{[Item="Summons_Data", Kind="Sheet"]}[Data],
    
    // Promote headers
    PromotedHeaders = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    
    // Ensure TITLE column exists (ETL adds it from Assignment Master; if missing, add null)
    WithTitle = if Table.HasColumns(PromotedHeaders, "TITLE") then PromotedHeaders else Table.AddColumn(PromotedHeaders, "TITLE", each null, type text),
    
    // Change YearMonthKey and TYPE; TITLE as text
    ChangedType = Table.TransformColumnTypes(WithTitle, {{"YearMonthKey", Int64.Type}, {"TYPE", type text}, {"TITLE", type text}}),
    
    // Filter to Moving violations only
    FilteredMoving = Table.SelectRows(ChangedType, each ([TYPE] = "M")),
    
    // EXCLUDE PEO: by TITLE = "PEO" (Assignment Master); fallback on display name
    FilteredMovingNoPEO = Table.SelectRows(FilteredMoving, each 
        ( [TITLE] = null or Text.Trim(Text.Upper([TITLE] ?? "")) <> "PEO" ) and
        ( [OFFICER_DISPLAY_NAME] = null or not (Text.StartsWith([OFFICER_DISPLAY_NAME], "PEO ") or Text.StartsWith([OFFICER_DISPLAY_NAME], "PEO,") or Text.StartsWith([OFFICER_DISPLAY_NAME], "PEO.")) )
    ),
    
    // Filter to PREVIOUS COMPLETE MONTH (not "max in file" — so January export shows 01-26)
    FilteredLatestMonth = Table.SelectRows(FilteredMovingNoPEO, each [YearMonthKey] = PreviousMonthKey),
    
    // Group by badge: Count = number of Moving rows per officer for that month (from staging file)
    GroupedRows = Table.Group(
        FilteredLatestMonth, 
        {"PADDED_BADGE_NUMBER", "Month_Year"}, 
        {
            {"Count", each Table.RowCount(_), type number},
            {"Officer", each List.First([OFFICER_DISPLAY_NAME]), type text}
        }
    ),
    
    RemovedBadge = Table.RemoveColumns(GroupedRows, {"PADDED_BADGE_NUMBER"}),
    SortedRows = Table.Sort(RemovedBadge, {{"Count", Order.Descending}}),
    Top5 = Table.FirstN(SortedRows, 5),
    // Ensure Month_Year label matches previous month (e.g. 01-26)
    SetMonthLabel = Table.TransformColumns(Top5, {{"Month_Year", each MonthYearText, type text}})
in
    SetMonthLabel

// STACP_DIAGNOSTIC
// 🕒 2026-02-13-17-15-00
// # Master_Automation/STACP/STACP_DIAGNOSTIC.m
// # Author: R. A. Carucci
// # Purpose: Diagnostic query to troubleshoot STACP column detection - shows what columns Power BI sees and which are selected.

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

// TAS_Dispatcher_Incident
// 🕒 2026-02-14-15-30-00
// # TAS/Virtual_Patrol/TAS_Dispatcher_Incident_Summary_Fixed.m
// # Author: R. A. Carucci
// # Purpose: Import TAS/Virtual Patrol data from Excel workbook, normalize incidents and dispatchers, count by dispatcher/incident/month for rolling 13-month window

let
    // =========================
    // Configuration
    // =========================
    FilePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\tas\yearly\2025\2025_01_to_2026_02_13_Hackensack_CAD_Data.xlsx",
    SheetName = "Sheet1",  // ⚠️ CHANGE THIS to match your actual sheet name
    
    // Valid dispatchers (normalized to lowercase)
    ValidDispatchers = {"carucci_r", "marino_b", "rios_a", "iannacone_a", "polson_r"},
    
    // Valid incident types (normalized)
    ValidIncidents = {
        "TAS Alert - Missing Person",
        "TAS Alert - Stolen License Plate", 
        "TAS Alert - Stolen Vehicle",
        "TAS Alert - Wanted Person",
        "Virtual - Patrol"
    },

    // =========================
    // Load Excel Workbook (FIXED)
    // =========================
    Source = Excel.Workbook(
        File.Contents(FilePath),
        null, 
        true
    ),
    
    // Load the specified sheet
    SheetData = Source{[Item=SheetName,Kind="Sheet"]}[Data],
    
    // Promote headers
    Promoted = Table.PromoteHeaders(SheetData, [PromoteAllScalars=true]),
    
    // ⚠️ DIAGNOSTIC: Check actual column names
    // Uncomment this line temporarily to see all column names:
    // ColumnNames = Table.ColumnNames(Promoted),
    
    // =========================
    // Map to expected column names (FLEXIBLE)
    // =========================
    // Try to find dispatcher column (could be "Dispatcher", "DispatcherNew", "Dispatcher Name", etc.)
    ColumnNames = Table.ColumnNames(Promoted),
    
    DispatcherCol = 
        if List.Contains(ColumnNames, "DispatcherNew") then "DispatcherNew"
        else if List.Contains(ColumnNames, "Dispatcher") then "Dispatcher"
        else if List.Contains(ColumnNames, "DispatcherName") then "DispatcherName"
        else null,
    
    IncidentCol = 
        if List.Contains(ColumnNames, "Incident") then "Incident"
        else if List.Contains(ColumnNames, "Incident Type") then "Incident Type"
        else if List.Contains(ColumnNames, "IncidentType") then "IncidentType"
        else null,
    
    TimeCol = 
        if List.Contains(ColumnNames, "Time of Call") then "Time of Call"
        else if List.Contains(ColumnNames, "TimeOfCall") then "TimeOfCall"
        else if List.Contains(ColumnNames, "CallTime") then "CallTime"
        else if List.Contains(ColumnNames, "Time") then "Time"
        else null,
    
    // Error if required columns not found
    CheckColumns = 
        if DispatcherCol = null then error "Required column not found: Dispatcher (tried: DispatcherNew, Dispatcher, DispatcherName)"
        else if IncidentCol = null then error "Required column not found: Incident (tried: Incident, Incident Type, IncidentType)"
        else if TimeCol = null then error "Required column not found: Time (tried: Time of Call, TimeOfCall, CallTime, Time)"
        else true,
    
    // Rename columns to standard names
    Renamed = Table.RenameColumns(
        Promoted,
        {
            {DispatcherCol, "DispatcherNew"},
            {IncidentCol, "Incident"},
            {TimeCol, "Time of Call"}
        }
    ),

    // =========================
    // Normalize DispatcherNew to lowercase
    // =========================
    LowercaseDispatcher = Table.TransformColumns(
        Renamed,
        {{"DispatcherNew", each if _ = null then null else Text.Lower(Text.Trim(_)), type text}}
    ),

    // =========================
    // Filter to valid dispatchers only
    // =========================
    FilteredDispatchers = Table.SelectRows(
        LowercaseDispatcher,
        each [DispatcherNew] <> null and List.Contains(ValidDispatchers, [DispatcherNew])
    ),

    // =========================
    // Normalize Incident column
    // =========================
    NormalizedIncident = Table.AddColumn(
        FilteredDispatchers,
        "Incident_Normalized",
        each 
            let 
                incident = if [Incident] = null then "" else Text.Trim([Incident]),
                normalized = Text.Lower(Text.Replace(Text.Replace(incident, "  ", " "), " - ", " - ")),
                matched = List.First(
                    List.Select(
                        ValidIncidents,
                        each Text.Lower(Text.Replace(Text.Replace(_, "  ", " "), " - ", " - ")) = normalized
                    ),
                    null
                )
            in
                if matched <> null then matched else "Other",
        type text
    ),

    FilteredIncidents = NormalizedIncident,

    // =========================
    // Extract month from "Time of Call"
    // =========================
    WithDate = Table.AddColumn(
        FilteredIncidents,
        "CallDate",
        each 
            let 
                timeOfCall = [#"Time of Call"],
                dateTimeValue = try DateTime.FromText(Text.From(timeOfCall)) otherwise null,
                dateValue = if dateTimeValue <> null then Date.From(dateTimeValue) else null
            in
                dateValue,
        type date
    ),

    // =========================
    // Calculate rolling 13-month window
    // =========================
    NowDT = DateTime.LocalNow(),
    CurrY = Date.Year(NowDT),
    CurrM = Date.Month(NowDT),
    EndY = if CurrM = 1 then CurrY - 1 else CurrY,
    EndM = if CurrM = 1 then 12 else CurrM - 1,
    
    EndDate = #date(EndY, EndM, 1),
    StartDate = Date.AddMonths(EndDate, -12),
    
    MonthList = List.Generate(
        () => StartDate,
        each _ <= EndDate,
        each Date.AddMonths(_, 1)
    ),
    
    PeriodLabelsMMYY = List.Transform(
        MonthList,
        each Text.PadStart(Text.From(Date.Month(_)), 2, "0") & "-" & Text.End(Text.From(Date.Year(_)), 2)
    ),

    // =========================
    // Add Period (MM-YY) column
    // =========================
    WithPeriod = Table.AddColumn(
        WithDate,
        "Period",
        each 
            if [CallDate] <> null then
                let 
                    y = Date.Year([CallDate]),
                    m = Date.Month([CallDate]),
                    period = Text.PadStart(Text.From(m), 2, "0") & "-" & Text.End(Text.From(y), 2)
                in
                    period
            else
                null,
        type text
    ),

    FilteredPeriod = Table.SelectRows(
        WithPeriod,
        each [Period] <> null and List.Contains(PeriodLabelsMMYY, [Period])
    ),

    // =========================
    // Group and count
    // =========================
    Grouped = Table.Group(
        FilteredPeriod,
        {"DispatcherNew", "Incident_Normalized", "Period"},
        {{"Count", each Table.RowCount(_), type number}}
    ),

    // =========================
    // Create all combinations
    // =========================
    AllDispatchers = Table.FromList(ValidDispatchers, Splitter.SplitByNothing(), {"DispatcherNew"}),
    AllIncidents = Table.FromList(List.Combine({ValidIncidents, {"Other"}}), Splitter.SplitByNothing(), {"Incident"}),
    AllPeriods = Table.FromList(PeriodLabelsMMYY, Splitter.SplitByNothing(), {"Period"}),

    AllCombinations_Step1 = Table.AddColumn(AllDispatchers, "IncidentTable", each AllIncidents),
    AllCombinations_Step2 = Table.ExpandTableColumn(AllCombinations_Step1, "IncidentTable", {"Incident"}, {"Incident"}),
    AllCombinations_Step3 = Table.AddColumn(AllCombinations_Step2, "PeriodTable", each AllPeriods),
    AllCombinations = Table.ExpandTableColumn(AllCombinations_Step3, "PeriodTable", {"Period"}, {"Period"}),

    AllCombinationsWithSort = Table.AddColumn(
        AllCombinations,
        "Month_Sort",
        each 
            let 
                mm = Number.FromText(Text.Start([Period], 2)),
                yy = Number.FromText(Text.End([Period], 2)),
                yyyy = if yy < 70 then 2000 + yy else 1900 + yy
            in
                yyyy * 100 + mm,
        Int64.Type
    ),

    AllCombinationsRenamed = Table.RenameColumns(AllCombinationsWithSort, {{"Period", "Month"}}),

    // =========================
    // Join and fill zeros
    // =========================
    GroupedRenamed = Table.RenameColumns(
        Grouped,
        {{"Incident_Normalized", "Incident"}, {"Period", "Month"}}
    ),

    Joined = Table.NestedJoin(
        AllCombinationsRenamed,
        {"DispatcherNew", "Incident", "Month"},
        GroupedRenamed,
        {"DispatcherNew", "Incident", "Month"},
        "GroupedData",
        JoinKind.LeftOuter
    ),

    Expanded = Table.ExpandTableColumn(Joined, "GroupedData", {"Count"}, {"Count"}),
    WithZeros = Table.ReplaceValue(Expanded, null, 0, Replacer.ReplaceValue, {"Count"}),

    // =========================
    // Final formatting
    // =========================
    Reordered = Table.ReorderColumns(
        WithZeros,
        {"DispatcherNew", "Incident", "Month", "Month_Sort", "Count"}
    ),

    Typed = Table.TransformColumnTypes(
        Reordered,
        {
            {"DispatcherNew", type text},
            {"Incident", type text},
            {"Month", type text},
            {"Month_Sort", Int64.Type},
            {"Count", type number}
        }
    )

in
    Typed

// ESU_13Month
// 🕒 2026-02-17-14-30-00
// # Master_Automation/m_code/esu/ESU_13Month.m
// # Author: R. A. Carucci
// # Purpose: Single query — load ESU.xlsx monthly Tables only; rolling 13 months (no helper queries).

let
    ESUPath = "C:\Users\RobertCarucci\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\ESU\ESU.xlsx",

    Source = Excel.Workbook(File.Contents(ESUPath), null, true),

    // Lookup Status and ItemKey from _mom_hacsoc (dimension table)
    MoMRow = try Source{[Name="_mom_hacsoc", Kind="Table"]} otherwise try Source{[Item="_mom_hacsoc", Kind="Table"]} otherwise Source{[Name="_mom_hacsoc", Kind="Sheet"]},
    MoM = MoMRow[Data],
    MoMCols = Table.ColumnNames(MoM),
    MoMTrackedCol = List.First(List.Select(MoMCols, each Text.Trim(Text.Replace(_, Character.FromNumber(160), " ")) = "Tracked Items"), "Tracked Items"),
    Norm = each Text.Lower(Text.Trim(Text.Replace(_, Character.FromNumber(160), " "))),
    StatusCol = List.First(List.Select(MoMCols, each Norm(_) = "status"), "Status"),
    ItemKeyCol = List.First(List.Select(MoMCols, each Norm(_) = "itemkey"), "ItemKey"),
    MoMWithItem = Table.AddColumn(MoM, "TrackedItem", each Text.Trim(Text.Replace(Text.From(Record.Field(_, MoMTrackedCol)), Character.FromNumber(160), " ")), type text),
    LookupStatusItemKey = Table.RenameColumns(
        Table.SelectColumns(MoMWithItem, {"TrackedItem", StatusCol, ItemKeyCol}),
        {{StatusCol, "Status"}, {ItemKeyCol, "ItemKey"}}
    ),

    // Use structured Tables only — Sheet [Data] does not expand correctly with named columns
    TablesOnly = Table.SelectRows(Source, each
        [Kind] = "Table"
        and Text.StartsWith([Name], "_")
        and [Name] <> "_mom_hacsoc"
    ),

    MonthMap = [JAN=1, FEB=2, MAR=3, APR=4, MAY=5, JUN=6, JUNE=6, JUL=7, JULY=7, AUG=8, SEP=9, OCT=10, NOV=11, DEC=12],

    // Parse table name _YY_MMM → MonthKey (Text.Middle / AfterDelimiter are safer than position-based)
    AddMonthKey = Table.AddColumn(TablesOnly, "MonthKey", each
        let
            n = Text.Upper([Name]),
            yy = try Number.FromText(Text.Middle(n, 1, 2)) otherwise null,
            afterFirst = Text.AfterDelimiter(n, "_", 0),
            mmm = Text.AfterDelimiter(afterFirst, "_", 0),
            m = try Record.Field(MonthMap, mmm) otherwise null
        in
            if yy = null or m = null then null else #date(2000 + yy, m, 1),
        type nullable date
    ),

    ValidMonths = Table.SelectRows(AddMonthKey, each [MonthKey] <> null),

    // Resolve "Tracked Items" column (handles trailing or non-breaking space)
    FirstDataTable = if Table.RowCount(AddMonthKey) = 0 then #table({"Tracked Items"}, {}) else AddMonthKey[Data]{0},
    TrackedCol = List.First(
        List.Select(Table.ColumnNames(FirstDataTable), each Text.Trim(Text.Replace(_, Character.FromNumber(160), " ")) = "Tracked Items"),
        "Tracked Items"
    ),

    Expanded = Table.ExpandTableColumn(ValidMonths, "Data", {TrackedCol, "Total"}, {"TrackedItem", "Total"}),

    CleanItem = Table.TransformColumns(Expanded, {{
        "TrackedItem",
        each Text.Trim(Text.Replace(Text.From(_), Character.FromNumber(160), " ")),
        type text
    }}),

    // Force null/blank to 0 so matrix shows 0 instead of blank (Number.From(null) returns null, not error)
    TotalNum = Table.TransformColumns(CleanItem, {{"Total", each if _ = null or _ = "" then 0 else try Number.From(_) otherwise 0, Int64.Type}}),

    Keep = Table.SelectColumns(TotalNum, {"MonthKey", "TrackedItem", "Total"}),

    MergedLookup = Table.NestedJoin(Keep, {"TrackedItem"}, LookupStatusItemKey, {"TrackedItem"}, "Lookup", JoinKind.LeftOuter),
    ExpandLookup = Table.ExpandTableColumn(MergedLookup, "Lookup", {"Status", "ItemKey"}, {"Status", "ItemKey"}),

    AddMonthYear = Table.AddColumn(ExpandLookup, "Month_Year", each Date.ToText([MonthKey], "MM-yy"), type text),
    AddSortKey = Table.AddColumn(AddMonthYear, "SortKey", each Date.ToText([MonthKey], "yyyy-MM-dd"), type text),

    // Rolling 13 complete months
    EndMonth = Date.StartOfMonth(Date.AddMonths(DateTime.Date(DateTime.LocalNow()), -1)),
    StartMonth = Date.AddMonths(EndMonth, -12),
    Filter13 = Table.SelectRows(AddSortKey, each [MonthKey] >= StartMonth and [MonthKey] <= EndMonth),

    // Fill missing (TrackedItem, Month) combinations with 0 so matrix shows 0, not blank
    AllMonths = List.Sort(List.Distinct(Filter13[MonthKey])),
    AllItems = List.Distinct(Filter13[TrackedItem]),
    CrossList = List.Combine(List.Transform(AllMonths, (m) => List.Transform(AllItems, (it) => [MonthKey = m, TrackedItem = it]))),
    Skeleton = Table.FromRecords(CrossList),
    MergedFull = Table.NestedJoin(Skeleton, {"MonthKey", "TrackedItem"}, Filter13, {"MonthKey", "TrackedItem"}, "Data", JoinKind.LeftOuter),
    ExpandFull = Table.ExpandTableColumn(MergedFull, "Data", {"Total", "Status", "ItemKey", "Month_Year", "SortKey"}, {"Total", "Status", "ItemKey", "Month_Year", "SortKey"}),
    FillZeros = Table.TransformColumns(ExpandFull, {{"Total", each if _ = null then 0 else _, Int64.Type}}),
    MonthYearF = Table.AddColumn(FillZeros, "Month_YearF", each if [Month_Year] = null then Date.ToText([MonthKey], "MM-yy") else [Month_Year], type text),
    SortKeyF = Table.AddColumn(MonthYearF, "SortKeyF", each if [SortKey] = null then Date.ToText([MonthKey], "yyyy-MM-dd") else [SortKey], type text),
    RenameMySk = Table.RenameColumns(Table.RemoveColumns(SortKeyF, {"Month_Year", "SortKey"}), {{"Month_YearF", "Month_Year"}, {"SortKeyF", "SortKey"}}),
    // Restore Status/ItemKey from lookup for rows that were missing (null after expand)
    MergedLookup2 = Table.NestedJoin(RenameMySk, {"TrackedItem"}, LookupStatusItemKey, {"TrackedItem"}, "Lookup2", JoinKind.LeftOuter),
    ExpandLookup2 = Table.ExpandTableColumn(MergedLookup2, "Lookup2", {"Status", "ItemKey"}, {"StatusNew", "ItemKeyNew"}),
    StatusFinal = Table.AddColumn(ExpandLookup2, "StatusF", each if [Status] = null then [StatusNew] else [Status], type text),
    ItemKeyFinal = Table.AddColumn(StatusFinal, "ItemKeyF", each if [ItemKey] = null then [ItemKeyNew] else [ItemKey], type text),
    DropTemp = Table.RemoveColumns(ItemKeyFinal, {"Status", "StatusNew", "ItemKey", "ItemKeyNew"}),
    RenameFinal = Table.RenameColumns(DropTemp, {{"StatusF", "Status"}, {"ItemKeyF", "ItemKey"}}),

    Result = if Table.RowCount(Filter13) > 0 then RenameFinal else AddSortKey
in
    Result