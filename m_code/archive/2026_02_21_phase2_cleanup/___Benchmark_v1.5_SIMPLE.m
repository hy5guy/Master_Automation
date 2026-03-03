// Benchmark Data Query - v1.5 ULTRA SIMPLE (No Transformations)
// Use this if v1.4 still doesn't work
// This version just loads data with minimal processing

let
    // Base path
    BenchmarkBasePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark\",
    
    // Simple load function - NO date fixing
    LoadLatest = (folderPath as text, eventType as text) =>
        let
            Source = Folder.Files(folderPath),
            FilteredFiles = Table.SelectRows(Source, each Text.EndsWith([Name], ".csv")),
            SortedFiles = Table.Sort(FilteredFiles, {{"Date modified", Order.Descending}}),
            LatestFile = SortedFiles{0}[Content],
            LoadedData = Csv.Document(LatestFile, [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
            PromotedHeaders = Table.PromoteHeaders(LoadedData, [PromoteAllScalars=true]),
            AddEventType = Table.AddColumn(PromotedHeaders, "EventType", each eventType)
        in
            AddEventType,
    
    // Load files
    UseOfForce = try LoadLatest(BenchmarkBasePath & "use_force\", "Use of Force") 
                 otherwise #table({"Message"}, {{"No data"}}),
    ShowOfForce = try LoadLatest(BenchmarkBasePath & "show_force\", "Show of Force") 
                  otherwise #table({"Message"}, {{"No data"}}),
    VehiclePursuit = try LoadLatest(BenchmarkBasePath & "vehicle_pursuit\", "Vehicle Pursuit") 
                     otherwise #table({"Message"}, {{"No data"}}),
    
    // Combine
    Combined = Table.Combine({UseOfForce, ShowOfForce, VehiclePursuit})
in
    Combined
