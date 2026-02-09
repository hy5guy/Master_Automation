// Benchmark Data Query - Simplified Structure
// Updated: 2026-02-09
// Source: 05_EXPORTS\Benchmark\ (simplified structure)
// 
// This query loads all three Benchmark event types:
// - Show of Force
// - Use of Force  
// - Vehicle Pursuit
//
// File structure:
//   Benchmark\
//   ├── show_force\
//   ├── use_force\
//   └── vehicle_pursuit\

let
    // Base path to simplified Benchmark directory
    BenchmarkBasePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark\",
    
    // Function to load latest file from a folder
    LoadLatestFile = (folderPath as text, eventType as text) =>
        let
            // Get all CSV files in the folder
            Source = Folder.Files(folderPath),
            
            // Filter to CSV files only
            FilteredFiles = Table.SelectRows(Source, 
                each Text.EndsWith([Name], ".csv") or Text.EndsWith([Name], ".xlsx")
            ),
            
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
            
            // Add Event Type column
            AddedEventType = Table.AddColumn(PromotedHeaders, "Event Type", each eventType, type text),
            
            // Add Source File column (for tracking)
            AddedSource = Table.AddColumn(AddedEventType, "Source File", each SortedFiles{0}[Name], type text)
        in
            AddedSource,
    
    // Load each event type
    UseOfForce = try LoadLatestFile(BenchmarkBasePath & "use_force\", "Use of Force") 
                 otherwise #table(type table [Message = text], {{"No Use of Force data found"}}),
    
    ShowOfForce = try LoadLatestFile(BenchmarkBasePath & "show_force\", "Show of Force") 
                  otherwise #table(type table [Message = text], {{"No Show of Force data found"}}),
    
    VehiclePursuit = try LoadLatestFile(BenchmarkBasePath & "vehicle_pursuit\", "Vehicle Pursuit") 
                     otherwise #table(type table [Message = text], {{"No Vehicle Pursuit data found"}}),
    
    // Combine all event types
    CombinedBenchmark = Table.Combine({UseOfForce, ShowOfForce, VehiclePursuit}),
    
    // Optional: Type conversions (adjust based on your actual column names)
    // Uncomment and modify as needed:
    /*
    TypedColumns = Table.TransformColumnTypes(CombinedBenchmark, {
        {"Date", type date},
        {"Officer Name", type text},
        {"Badge Number", type text},
        {"Incident Number", type text},
        {"Event Type", type text}
    })
    */
    
    // Return the combined data
    Result = CombinedBenchmark
in
    Result
