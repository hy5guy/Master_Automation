// 🕒 2026-02-20-23-48-50
// # benchmark/___Benchmark.m
// # Author: R. A. Carucci
// # Purpose: Load use-of-force benchmark data with event type classification and month dimensions.

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
