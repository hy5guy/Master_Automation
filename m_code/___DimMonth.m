// DimMonth - Month Dimension Table for Benchmark Dashboard
// Created: 2026-02-09
// Purpose: Rolling 13-month dimension table for date filtering
//
// Columns:
// - MonthStart: First day of month (date) - use for relationships
// - MonthLabel: MM-yy format (text) - use for display in visuals
// - MonthSort: YYYYMM format (number) - use for sorting
//
// Usage:
// - Create relationship: ___Benchmark[MonthStart] -> ___DimMonth[MonthStart] (many-to-one)
// - Use MonthLabel in visuals for clean "11-24" display format
// - Use MonthSort for proper chronological sorting

let
    // Configuration: Rolling 13-month window
    StartDate = #date(2024, 11, 1),  // Adjust as needed for your reporting period
    MonthCount = 13,                  // Rolling 13 months
    
    // Generate list of first day of each month
    MonthStarts = List.Generate(
        () => StartDate,
        each _ <= Date.AddMonths(StartDate, MonthCount - 1),
        each Date.AddMonths(_, 1)
    ),
    
    // Convert list to table
    ToTable = Table.FromList(MonthStarts, Splitter.SplitByNothing(), {"MonthStart"}),
    
    // Ensure MonthStart is date type
    TypedDate = Table.TransformColumnTypes(ToTable, {{"MonthStart", type date}}),
    
    // Add MonthLabel column (MM-yy format for display)
    AddLabel = Table.AddColumn(TypedDate, "MonthLabel", 
        each Date.ToText([MonthStart], "MM-yy"), type text),
    
    // Add MonthSort column (YYYYMM format for sorting)
    AddSort = Table.AddColumn(AddLabel, "MonthSort", 
        each Date.Year([MonthStart]) * 100 + Date.Month([MonthStart]), Int64.Type)
in
    AddSort
