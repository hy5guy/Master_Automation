// Benchmark Data Query - DIAGNOSTIC VERSION
// Use this to see what's actually in your Incident Date column

let
    // Base path
    BenchmarkBasePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark\",
    
    // Load just one file to test
    TestFile = Folder.Files(BenchmarkBasePath & "use_force\"),
    FilteredFiles = Table.SelectRows(TestFile, each Text.EndsWith([Name], ".csv")),
    SortedFiles = Table.Sort(FilteredFiles, {{"Date modified", Order.Descending}}),
    LatestFile = SortedFiles{0}[Content],
    
    // Load without any transformations
    RawData = Csv.Document(LatestFile, [Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    
    // Promote headers but DON'T type anything yet
    PromotedHeaders = Table.PromoteHeaders(RawData, [PromoteAllScalars=true]),
    
    // Add a column to show the TYPE of Incident Date
    AddTypeCheck = Table.AddColumn(PromotedHeaders, "IncidentDate_Type", 
        each Value.Type([Incident Date]), type text),
    
    // Add a column to show if it's text, datetime, or date
    AddFormatCheck = Table.AddColumn(AddTypeCheck, "IncidentDate_Format", 
        each if [Incident Date] is datetime then "datetime"
             else if [Incident Date] is date then "date"
             else if [Incident Date] is text then "text"
             else "unknown", type text),
    
    // Keep just first 10 rows for testing
    FirstRows = Table.FirstN(AddFormatCheck, 10)
in
    FirstRows
