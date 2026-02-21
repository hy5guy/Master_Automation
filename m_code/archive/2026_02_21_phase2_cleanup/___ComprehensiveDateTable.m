// 🕒 2025-08-17-16-30-45
// Project: PowerBI_DateDimension/ComprehensiveDateTable
// Author: R. A. Carucci
// Purpose: Create a comprehensive date dimension table with multiple date formats including mm/dd/yy

// ComprehensiveDateTable
// Purpose: Create a date dimension table for temporal analysis
let
    StartDate = #date(2020, 1, 1),
    EndDate = #date(2030, 12, 31),
    DateList = List.Dates(StartDate, Duration.Days(EndDate - StartDate) + 1, #duration(1, 0, 0, 0)),
    DateTable = Table.FromList(DateList, Splitter.SplitByNothing(), {"Date"}),
    SetDateType = Table.TransformColumnTypes(DateTable, {{"Date", type date}}),
    AddYear = Table.AddColumn(SetDateType, "Year", each Date.Year([Date]), Int64.Type),
    AddMonth = Table.AddColumn(AddYear, "Month", each Date.Month([Date]), Int64.Type),
    AddMonthName = Table.AddColumn(AddMonth, "MonthName", each Date.MonthName([Date]), type text),
    AddQuarter = Table.AddColumn(AddMonthName, "Quarter", each Date.QuarterOfYear([Date]), Int64.Type),
    AddDayOfMonth = Table.AddColumn(AddQuarter, "DayOfMonth", each Date.Day([Date]), Int64.Type),
    AddDayOfWeek = Table.AddColumn(AddDayOfMonth, "DayOfWeek", each 
        let
            DayNum = Date.DayOfWeek([Date], Day.Monday)
        in
            if DayNum = 0 then 7 else DayNum, Int64.Type),
    AddDayName = Table.AddColumn(AddDayOfWeek, "DayName", each Date.DayOfWeekName([Date]), type text),
    AddWeekOfYear = Table.AddColumn(AddDayName, "WeekOfYear", each Date.WeekOfYear([Date], Day.Monday), Int64.Type),
    AddFiscalYear = Table.AddColumn(AddWeekOfYear, "FiscalYear", each 
        if Date.Month([Date]) >= 7 then Date.Year([Date]) + 1 else Date.Year([Date]), Int64.Type),
    AddFiscalQuarter = Table.AddColumn(AddFiscalYear, "FiscalQuarter", each 
        if Date.Month([Date]) >= 7 then Date.QuarterOfYear(Date.AddMonths([Date], -6))
        else Date.QuarterOfYear(Date.AddMonths([Date], 6)), Int64.Type),
    AddYearMonth = Table.AddColumn(AddFiscalQuarter, "YearMonth", each 
        Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type),
    AddYearQuarter = Table.AddColumn(AddYearMonth, "YearQuarter", each 
        Date.Year([Date]) * 10 + Date.QuarterOfYear([Date]), Int64.Type),
    AddFiscalYearQuarter = Table.AddColumn(AddYearQuarter, "FiscalYearQuarter", each 
        [FiscalYear] * 10 + [FiscalQuarter], Int64.Type),
    AddDateKey = Table.AddColumn(AddFiscalYearQuarter, "DateKey", each 
        Number.From(Date.ToText([Date], "yyyyMMdd")), Int64.Type),
    AddShortDate = Table.AddColumn(AddDateKey, "ShortDate", each 
        Date.ToText([Date], "MM/dd/yy"), type text),
    // NEW: Add mm/dd/yy format column
    AddMMDDYY = Table.AddColumn(AddShortDate, "mm/dd/yy", each 
        Date.ToText([Date], "MM/dd/yy"), type text),
    AddMMYY = Table.AddColumn(AddMMDDYY, "mm-yy", each 
        Text.PadStart(Text.From(Date.Month([Date])), 2, "0") & "-" & 
        Text.End(Text.From(Date.Year([Date])), 2), type text),
    AddMMMYY = Table.AddColumn(AddMMYY, "mmm-yy", each 
        Text.Start(Date.MonthName([Date]), 3) & "-" & 
        Text.End(Text.From(Date.Year([Date])), 2), type text),
    AddMMYYYY = Table.AddColumn(AddMMMYY, "mmm-yyyy", each 
        Text.Start(Date.MonthName([Date]), 3) & "-" & 
        Text.From(Date.Year([Date])), type text),
    AddMMMMYYYY = Table.AddColumn(AddMMYYYY, "mmmm yyyy", each 
        Date.MonthName([Date]) & " " & Text.From(Date.Year([Date])), type text),
    AddMMMM = Table.AddColumn(AddMMMMYYYY, "mmmm", each 
        Date.MonthName([Date]), type text),
    AddDayType = Table.AddColumn(AddMMMM, "DayType", each 
        if Date.DayOfWeek([Date], Day.Monday) >= 5 then "Weekend" else "Weekday", type text),
    
    // Add sort order columns for all date format columns
    AddSortOrders = Table.AddColumn(AddDayType, "mm-yy_Sort_Order", each 
        Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type),
    // NEW: Add sort order for mm/dd/yy format
    AddMMDDYYSort = Table.AddColumn(AddSortOrders, "mm/dd/yy_Sort_Order", each 
        Number.From(Date.ToText([Date], "yyyyMMdd")), Int64.Type),
    AddMMMYYSort = Table.AddColumn(AddMMDDYYSort, "mmm-yy_Sort_Order", each 
        Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type),
    AddMMYYYYSort = Table.AddColumn(AddMMMYYSort, "mmm-yyyy_Sort_Order", each 
        Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type),
    AddMMMMYYYYSort = Table.AddColumn(AddMMYYYYSort, "mmmm yyyy_Sort_Order", each 
        Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type),
    AddMMMMSort = Table.AddColumn(AddMMMMYYYYSort, "mmmm_Sort_Order", each 
        Date.Month([Date]), Int64.Type),
    AddMonthNameSort = Table.AddColumn(AddMMMMSort, "MonthName_Sort_Order", each 
        Date.Month([Date]), Int64.Type),
    AddDayNameSort = Table.AddColumn(AddMonthNameSort, "DayName_Sort_Order", each 
        let
            DayNum = Date.DayOfWeek([Date], Day.Monday)
        in
            if DayNum = 0 then 7 else DayNum, Int64.Type),
    
    // Set explicit data types for all columns to prevent auto-detection issues
    SetDataTypes = Table.TransformColumnTypes(AddDayNameSort, {
        {"Date", type date},
        {"Year", Int64.Type},
        {"Month", Int64.Type},
        {"MonthName", type text},
        {"Quarter", Int64.Type},
        {"DayOfMonth", Int64.Type},
        {"DayOfWeek", Int64.Type},
        {"DayName", type text},
        {"WeekOfYear", Int64.Type},
        {"FiscalYear", Int64.Type},
        {"FiscalQuarter", Int64.Type},
        {"YearMonth", Int64.Type},
        {"YearQuarter", Int64.Type},
        {"FiscalYearQuarter", Int64.Type},
        {"DateKey", Int64.Type},
        {"ShortDate", type text},
        {"mm/dd/yy", type text},
        {"mm-yy", type text},
        {"mmm-yy", type text},
        {"mmm-yyyy", type text},
        {"mmmm yyyy", type text},
        {"mmmm", type text},
        {"DayType", type text},
        {"mm-yy_Sort_Order", Int64.Type},
        {"mm/dd/yy_Sort_Order", Int64.Type},
        {"mmm-yy_Sort_Order", Int64.Type},
        {"mmm-yyyy_Sort_Order", Int64.Type},
        {"mmmm yyyy_Sort_Order", Int64.Type},
        {"mmmm_Sort_Order", Int64.Type},
        {"MonthName_Sort_Order", Int64.Type},
        {"DayName_Sort_Order", Int64.Type}
    })
in
    SetDataTypes