// 🕒 2026-02-17-14-30-00
// # Master_Automation/m_code/___Summons_Top5_Parking.m
// # Author: R. A. Carucci
// # Purpose: Top 5 Parking violations for latest month; depends on ___Summons base query.

let
    // Load main Summons table
    Source = ___Summons,
    
    // Filter to Parking violations only
    FilteredParking = Table.SelectRows(Source, each ([TYPE] = "P")),
    
    // Find LATEST month using YearMonthKey (integer sorting, not text!)
    LatestKey = List.Max(FilteredParking[YearMonthKey]),
    
    // Filter to latest month only
    FilteredLatestMonth = Table.SelectRows(FilteredParking, each [YearMonthKey] = LatestKey),
    
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
