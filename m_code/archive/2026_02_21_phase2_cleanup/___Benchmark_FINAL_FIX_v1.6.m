// ___Benchmark Query - FINAL FIX v1.6
// Updated: 2026-02-09 (Post-Diagnostic)
// Source: 05_EXPORTS\Benchmark\
//
// This query loads all three Benchmark event types with ROBUST datetime parsing
//
// CRITICAL FIX: Handles ISO 8601 datetime text format (2020-10-05T18:37:00.000)

let
    // Base path to simplified Benchmark directory
    BenchmarkBasePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark\",
    
    // Function to load and process latest file from a folder
    LoadAndProcessLatest = (folderPath as text, eventType as text) =>
        let
            // Get all CSV files in the folder
            Source = Folder.Files(folderPath),
            
            // Filter to CSV files only
            FilteredFiles = Table.SelectRows(Source, each Text.EndsWith([Name], ".csv") or Text.EndsWith([Name], ".xlsx")),
            
            // Sort by Date modified (most recent first)
            SortedFiles = Table.Sort(FilteredFiles, {{"Date modified", Order.Descending}}),
            
            // Get the first (most recent) file
            LatestFile = if Table.RowCount(SortedFiles) > 0 
                then SortedFiles{0}[Content] 
                else error "No files found in " & folderPath,
            
            // Load the file content
            LoadedData = if Text.EndsWith(SortedFiles{0}[Name], ".csv") 
                then Csv.Document(LatestFile, [Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None])
                else Excel.Workbook(LatestFile){0}[Data],
            
            // Promote headers
            PromotedHeaders = Table.PromoteHeaders(LoadedData, [PromoteAllScalars=true]),
            
            // CRITICAL DATETIME FIX: Convert text datetime to actual date
            // Step 1: Convert ISO 8601 text to datetime, then extract date
            FixIncidentDate = Table.TransformColumns(PromotedHeaders, {
                {"Incident Date", each 
                    try 
                        // Try to parse as DateTime first
                        if _ is datetime then DateTime.Date(_)
                        else if _ is date then _
                        else if _ is text then 
                            // Parse ISO 8601 text format: "2020-10-05T18:37:00.000"
                            DateTime.Date(DateTime.FromText(_))
                        else Date.From(_)
                    otherwise null,
                type date}
            }),
            
            // Step 2: Now add MonthStart (from the clean Incident Date)
            AddMonthStart = if List.Contains(Table.ColumnNames(FixIncidentDate), "MonthStart")
                then FixIncidentDate
                else Table.AddColumn(FixIncidentDate, "MonthStart", each 
                    if [Incident Date] <> null 
                    then Date.StartOfMonth([Incident Date])
                    else null, 
                type date),
            
            // Step 3: Add Report Key (conditionally)
            AddReportKey = if List.Contains(Table.ColumnNames(AddMonthStart), "Report Key")
                then AddMonthStart
                else Table.AddColumn(AddMonthStart, "Report Key", each [Report Number], type text),
            
            // Step 4: Add EventType column (no space!)
            AddedEventType = Table.AddColumn(AddReportKey, "EventType", each eventType, type text),
            
            // Step 5: Add Source File column (for tracking)
            AddedSource = Table.AddColumn(AddedEventType, "Source File", each SortedFiles{0}[Name], type text)
        in
            AddedSource,
    
    // Load each event type with error handling
    UseOfForce = try LoadAndProcessLatest(BenchmarkBasePath & "use_force\", "Use of Force") 
        otherwise #table(type table [Message = text], {{"No Use of Force data found"}}),
    
    ShowOfForce = try LoadAndProcessLatest(BenchmarkBasePath & "show_force\", "Show of Force") 
        otherwise #table(type table [Message = text], {{"No Show of Force data found"}}),
    
    VehiclePursuit = try LoadAndProcessLatest(BenchmarkBasePath & "vehicle_pursuit\", "Vehicle Pursuit") 
        otherwise #table(type table [Message = text], {{"No Vehicle Pursuit data found"}}),
    
    // Combine all event types
    CombinedBenchmark = Table.Combine({UseOfForce, ShowOfForce, VehiclePursuit}),
    
    // Return the combined data
    Result = CombinedBenchmark
in
    Result
