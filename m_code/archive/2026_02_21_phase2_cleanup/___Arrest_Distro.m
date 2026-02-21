// 🕒 2026-02-17-14-30-00
// # Master_Automation/m_code/___Arrest_Distro.m
// # Author: R. A. Carucci
// # Purpose: Process arrest data from latest Power BI ready file with enhanced null handling.

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