// Benchmark Data Query - v1.4 ROBUST VERSION
// Updated: 2026-02-09
// Completely rewritten to handle datetime formats robustly
//
// This version:
// - Lets Power Query auto-detect datetime on CSV import
// - Extracts date from datetime immediately after import
// - Handles text, date, and datetime formats
// - Creates MonthStart from clean dates

let
    // Base path to Benchmark directory
    BenchmarkBasePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark\",
    
    // Function to load and process latest file from a folder
    LoadAndProcessLatest = (folderPath as text, eventType as text) =>
        let
            // Get all files
            Source = Folder.Files(folderPath),
            
            // Filter to CSV/Excel
            FilteredFiles = Table.SelectRows(Source, 
                each Text.EndsWith([Name], ".csv") or Text.EndsWith([Name], ".xlsx")
            ),
            
            // Sort by date (most recent first)
            SortedFiles = Table.Sort(FilteredFiles, {{"Date modified", Order.Descending}}),
            
            // Get latest file
            LatestFile = if Table.RowCount(SortedFiles) > 0 
                then SortedFiles{0}[Content]
                else error "No files found in " & folderPath,
            
            // Load file - let Power Query auto-detect types
            LoadedData = if Text.EndsWith(SortedFiles{0}[Name], ".csv")
                then Csv.Document(LatestFile, [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None])
                else Excel.Workbook(LatestFile){0}[Data],
            
            // Promote headers
            PromotedHeaders = Table.PromoteHeaders(LoadedData, [PromoteAllScalars=true]),
            
            // IMMEDIATELY fix Incident Date if it exists
            // This must happen BEFORE we try to use it for anything
            FixIncidentDateIfExists = if List.Contains(Table.ColumnNames(PromotedHeaders), "Incident Date")
                then Table.TransformColumns(PromotedHeaders, {
                    "Incident Date", 
                    each try 
                        (if _ is datetime then DateTime.Date(_) 
                         else if _ is date then _ 
                         else if _ is text then Date.From(_)
                         else _)
                    otherwise null,
                    type date
                })
                else PromotedHeaders,
            
            // Add EventType column
            AddedEventType = Table.AddColumn(FixIncidentDateIfExists, "EventType", 
                each eventType, type text),
            
            // Add Source File column
            AddedSource = Table.AddColumn(AddedEventType, "Source File", 
                each SortedFiles{0}[Name], type text)
        in
            AddedSource,
    
    // Load all three event types
    UseOfForce = try LoadAndProcessLatest(BenchmarkBasePath & "use_force\", "Use of Force") 
                 otherwise #table({"Message"}, {{"No Use of Force data found"}}),
    
    ShowOfForce = try LoadAndProcessLatest(BenchmarkBasePath & "show_force\", "Show of Force") 
                  otherwise #table({"Message"}, {{"No Show of Force data found"}}),
    
    VehiclePursuit = try LoadAndProcessLatest(BenchmarkBasePath & "vehicle_pursuit\", "Vehicle Pursuit") 
                     otherwise #table({"Message"}, {{"No Vehicle Pursuit data found"}}),
    
    // Combine all event types
    CombinedBenchmark = Table.Combine({UseOfForce, ShowOfForce, VehiclePursuit}),
    
    // Now add MonthStart from the already-fixed Incident Date
    AddMonthStart = if List.Contains(Table.ColumnNames(CombinedBenchmark), "MonthStart")
        then CombinedBenchmark
        else if List.Contains(Table.ColumnNames(CombinedBenchmark), "Incident Date")
            then Table.AddColumn(CombinedBenchmark, "MonthStart", 
                each try Date.StartOfMonth([Incident Date]) otherwise null, 
                type date)
            else CombinedBenchmark,
    
    // Add Report Key if needed
    AddReportKey = if List.Contains(Table.ColumnNames(AddMonthStart), "Report Key")
        then AddMonthStart
        else if List.Contains(Table.ColumnNames(AddMonthStart), "Report Number")
            then Table.AddColumn(AddMonthStart, "Report Key", 
                each [Report Number], type text)
            else AddMonthStart,
    
    // Return final result
    Result = AddReportKey
in
    Result
