// 🕒 2026-02-17-14-30-00
// # Master_Automation/m_code/___Summons_All_Bureaus.m
// # Author: R. A. Carucci
// # Purpose: Summons by bureau (WG2) and type for latest month; depends on ___Summons base query.

let
    // Load main Summons table
    Source = ___Summons,
    
    // Find LATEST month using YearMonthKey (integer sorting, not text!)
    LatestKey = List.Max(Source[YearMonthKey]),
    
    // Filter to latest month only
    FilteredLatestMonth = Table.SelectRows(Source, each [YearMonthKey] = LatestKey),
    
    // Group by Bureau (WG2) and Type
    GroupedRows = Table.Group(
        FilteredLatestMonth, 
        {"WG2", "TYPE"}, 
        {{"Count", each Table.RowCount(_), type number}}
    ),
    
    // Pivot by TYPE to get M, P, C columns
    PivotedColumn = Table.Pivot(
        GroupedRows, 
        List.Distinct(GroupedRows[TYPE]), 
        "TYPE", 
        "Count", 
        List.Sum
    ),
    
    // Replace null with 0
    ReplacedValue = Table.ReplaceValue(
        PivotedColumn, 
        null, 
        0, 
        Replacer.ReplaceValue, 
        {"M", "P", "C"}
    ),
    
    // Add total column (handle cases where C column might not exist)
    AddedTotal = Table.AddColumn(
        ReplacedValue, 
        "Total", 
        each [M] + [P] + (try [C] otherwise 0),
        type number
    )
in
    AddedTotal
