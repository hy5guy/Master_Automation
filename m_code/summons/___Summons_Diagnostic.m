// 🕒 2026-02-20-23-48-50
// # summons/___Summons_Diagnostic.m
// # Author: R. A. Carucci
// # Purpose: Diagnostic query to validate summons data quality and column structure.

let
    Source = Csv.Document(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_slim_for_powerbi.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    
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
