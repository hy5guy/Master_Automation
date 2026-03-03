// Benchmark Data Query - DAX-Compatible Version (v1.1 - Duplicate Column Fix)
// Updated: 2026-02-09 (Fixed duplicate column error)
// Source: 05_EXPORTS\Benchmark\ (simplified structure)
// 
// This query loads all three Benchmark event types with proper column names
// and data types to work with the DAX measures in benchmark_r13.dax
//
// v1.1 Changes:
// - Fixed: Checks if Report Key already exists before adding
// - Fixed: Checks if MonthStart already exists before adding
// - Handles CSV exports that already include these columns
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
            
            // Add EventType column (NO SPACE - matches DAX expectations)
            AddedEventType = Table.AddColumn(PromotedHeaders, "EventType", each eventType, type text),
            
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
    
    // STEP 1: Fix Incident Date FIRST (before using it to create MonthStart)
    // Handles datetime format: 2020-10-05T18:37:00.000
    FixIncidentDate = Table.TransformColumns(CombinedBenchmark, {
        {"Incident Date", each 
            if _ is datetime then DateTime.Date(_)  // Already datetime, extract date
            else if _ is date then _  // Already date, keep as-is
            else Date.From(_),  // Parse from text
        type date}
    }),
    
    // STEP 2: Now create MonthStart from the fixed Incident Date
    // Check if it already exists to avoid duplicates
    AddMonthStart = if List.Contains(Table.ColumnNames(FixIncidentDate), "MonthStart")
        then FixIncidentDate  // Column already exists, skip
        else Table.AddColumn(FixIncidentDate, "MonthStart", 
            each Date.StartOfMonth([Incident Date]), type date),
    
    // STEP 3: Add Report Key column ONLY if it doesn't already exist
    AddReportKey = if List.Contains(Table.ColumnNames(AddMonthStart), "Report Key")
        then AddMonthStart  // Column already exists, skip
        else if List.Contains(Table.ColumnNames(AddMonthStart), "Report Number")
            then Table.AddColumn(AddMonthStart, "Report Key", each [Report Number], type text)
            else AddMonthStart,  // No Report Number to copy from, skip
    
    // Type conversions for other columns
    // Note: Incident Date and MonthStart already fixed and typed above
    TypedColumns = Table.TransformColumnTypes(AddReportKey, {
        {"EventType", type text},
        {"Source File", type text}
    }),
    
    // Return the final data
    Result = TypedColumns
in
    Result
