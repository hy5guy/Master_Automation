// 🕒 2026-02-17-14-30-00
// # Master_Automation/m_code/___Summons_Top5_Moving.m
// # Author: R. A. Carucci
// # Purpose: Top 5 Moving violations for latest month; depends on ___Summons base query.

let
    // Load main Summons table
    Source = ___Summons,
    
    // Filter to Moving violations only
    FilteredMoving = Table.SelectRows(Source, each ([TYPE] = "M")),
    
    // Find LATEST month using YearMonthKey (integer sorting, not text!)
    LatestKey = List.Max(FilteredMoving[YearMonthKey]),
    
    // Filter to latest month only
    FilteredLatestMonth = Table.SelectRows(FilteredMoving, each [YearMonthKey] = LatestKey),
    
    // Group by violation description and count
    GroupedRows = Table.Group(
        FilteredLatestMonth, 
        {"VIOLATION_DESCRIPTION"}, 
        {{"Count", each Table.RowCount(_), type number}}
    ),
    
    // Sort by count descending
    SortedRows = Table.Sort(GroupedRows, {{"Count", Order.Descending}}),
    
    // Keep top 5
    Top5 = Table.FirstN(SortedRows, 5)
in
    Top5
