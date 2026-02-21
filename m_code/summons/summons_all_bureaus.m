// 🕒 2026-02-21-01-00-00 (EST)
// # summons/summons_all_bureaus.m
// # Author: R. A. Carucci
// # Purpose: Aggregate summons counts by bureau for moving and parking violations.

let
    ReportMonth = pReportMonth,

    // Previous complete month (e.g. in Feb 2026 show Jan 2026)
    PrevDate = Date.AddMonths(ReportMonth, -1),
    PreviousMonthKey = Date.Year(PrevDate) * 100 + Date.Month(PrevDate),

    // Load directly from Excel file
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"),
        null, 
        true
    ),
    
    Summons_Data_Sheet = Source{[Item="Summons_Data", Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{"YearMonthKey", Int64.Type}, {"TYPE", type text}, {"WG2", type text}}),
    
    // Filter out UNKNOWN / blank WG2
    FilteredClean = Table.SelectRows(ChangedType, each [WG2] <> "UNKNOWN" and [WG2] <> null and [WG2] <> ""),
    
    // Filter to PREVIOUS COMPLETE MONTH (same as Top 5 Moving/Parking)
    FilteredLatestMonth = Table.SelectRows(FilteredClean, each [YearMonthKey] = PreviousMonthKey),
    
    // Group by Bureau (WG2) and Type - COMBINE HOUSING & OSO WITH PATROL
    GroupedRows = Table.Group(
        FilteredLatestMonth, 
        {"WG2", "TYPE"}, 
        {{"Count", each Table.RowCount(_), type number}}
    ),
    
    // Consolidate bureaus before pivot
    ConsolidatedBureaus = Table.TransformColumns(
        GroupedRows,
        {
  "WG2", each if _ = "HOUSING" or _ = "OFFICE OF SPECIAL OPERATIONS" then
                                      "PATROL DIVISION" else _}
    ),
    
    // Re-group after consolidation
    RegroupedRows = Table.Group(
        ConsolidatedBureaus,
        {"WG2", "TYPE"},
        {{"Count", each List.Sum([Count]), type number}}
    ),
    
    // Pivot by TYPE to get M, P columns (C might not exist after reclassification)
    PivotedColumn = Table.Pivot(
        RegroupedRows, 
        List.Distinct(RegroupedRows[TYPE]), 
        "TYPE", 
        "Count", 
        List.Sum
    ),
    
    // Add M column if missing
    AddM = if Table.HasColumns(PivotedColumn, "M") then PivotedColumn else Table.AddColumn(PivotedColumn, "M", each 0, Int64.Type),
    
    // Add P column if missing
    AddP = if Table.HasColumns(AddM, "P") then AddM else Table.AddColumn(AddM, "P", each 0, Int64.Type),
    
    // Replace null with 0 in M and P columns
    ReplacedValue = Table.ReplaceValue(AddP, null, 0, Replacer.ReplaceValue, {"M", "P"}),
    
    // Add total column (C might not exist, so use try/otherwise)
    AddedTotal = Table.AddColumn(
        ReplacedValue, 
        "Total", 
        each [M] + [P] + (try [C] otherwise 0),
        type number
    )
in
    AddedTotal
