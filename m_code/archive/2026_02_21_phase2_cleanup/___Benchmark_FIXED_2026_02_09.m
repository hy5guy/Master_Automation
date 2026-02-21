// 🕒 2026-02-17-14-30-00
// # Master_Automation/m_code/___Benchmark_FIXED_2026_02_09.m
// # Author: R. A. Carucci
// # Purpose: Load Benchmark event types from 05_EXPORTS\Benchmark with DAX-compatible column names.

// This query loads all three Benchmark event types with proper column names
// and data types to work with the DAX measures in benchmark_r13.dax
//
// File structure:
//   Benchmark\
//   ├── show_force\
//   ├── use_force\
//   └── vehicle_pursuit\
//
// KEY FIXES:
// - EventType column (no space) for DAX compatibility
// - MonthStart column added (first day of month from Incident Date)
// - Proper type conversions for dates
// - Report Key column for unique incident counting

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
    // This creates first-of-month date (required by DAX measures)
    AddMonthStart = if List.Contains(Table.ColumnNames(FixIncidentDate), "MonthStart")
        then FixIncidentDate  // Column already exists, skip
        else Table.AddColumn(FixIncidentDate, "MonthStart", 
            each Date.StartOfMonth([Incident Date]), type date),
    
    // STEP 3: Add Report Key column ONLY if it doesn't already exist
    // (Some CSV exports already include this column)
    AddReportKey = if List.Contains(Table.ColumnNames(AddMonthStart), "Report Key")
        then AddMonthStart  // Column already exists, skip this step
        else Table.AddColumn(AddMonthStart, "Report Key", each [Report Number], type text),
    
    // Type conversions (CRITICAL - adjust column names to match your CSV structure)
    // Note: Incident Date already fixed, MonthStart already typed
    TypedColumns = Table.TransformColumnTypes(AddReportKey, {
        {"EventType", type text},
        {"Source File", type text},
        {"Report Number", type text},
        {"Report Key", type text}
        // Add more columns as needed:
        // {"# of Officers Involved", Int64.Type},
        // {"# of Subjects", Int64.Type},
        // {"Officer Name", type text},
        // {"Badge Number", type text}
    }),
    
    // Return the final data
    Result = TypedColumns
in
    Result
