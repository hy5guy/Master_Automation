// 🕒 2026-02-13-18-05-00
// # Master_Automation/Detectives/___Det_case_dispositions_clearance_2026.m
// # Author: R. A. Carucci
// # Purpose: Import Detective case clearance and dispositions from restructured 2026-only workbook (_CCD_MOM table) with rolling 13-month window and robust % normalization.

let
    // =================================================================
    // FILE PATH AND TABLE LOAD
    // =================================================================
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Detectives\detectives_monthly.xlsx"),
        null, true
    ),
    
    // Load _CCD_MOM table (now contains 01-26 through 12-26 only)
    CCD_Table = Source{[Item="_CCD_MOM", Kind="Table"]}[Data],

    // =================================================================
    // REQUIRED ROW ORDER (EXACT LABELS)
    // =================================================================
    // These labels must match Excel exactly (including spaces)
    RequiredOrder = {
        "Active / Administratively Closed",
        "Arrest",
        "Complaint Signed",
        "Ex Cleared / Closed",
        "Juvenile Complaint",
        "Stationhouse Adjustment",
        "TOT DCP&P",
        "Unfounded / Closed",
        "Monthly Bureau Case Clearance %",
        "YTD Bureau Case Clearance %"  // Added per Claude recommendation
    },

    // =================================================================
    // COLUMN NAME DETECTION
    // =================================================================
    ColNames        = Table.ColumnNames(CCD_Table),
    FirstColumnName = ColNames{0},
    MonthColumns    = List.Skip(ColNames, 1),

    // =================================================================
    // FILTER TO REQUIRED ROWS ONLY
    // =================================================================
    // Keep only rows that match the required order list
    // Note: Handles trailing/double spaces in Excel labels
    KeptRows = Table.SelectRows(
        CCD_Table,
        (r) => List.Contains(RequiredOrder, Text.Trim(Record.Field(r, FirstColumnName)))
    ),

    // =================================================================
    // ADD ROW SORT ORDER
    // =================================================================
    // Add Row_Sort column to maintain display order
    WithRowSort = Table.AddColumn(
        KeptRows, "Row_Sort",
        each List.PositionOf(RequiredOrder, Text.Trim(Record.Field(_, FirstColumnName))),
        Int64.Type
    ),
    
    // Sort rows by the defined order
    OrderedRows = Table.Sort(WithRowSort, {{"Row_Sort", Order.Ascending}}),

    // =================================================================
    // INITIAL TYPE CONVERSION (WIDE FORMAT)
    // =================================================================
    // Keep month columns as 'any' type for now (normalize after unpivot)
    TypedWide = Table.TransformColumnTypes(
        OrderedRows,
        {{FirstColumnName, type text}} & 
        List.Transform(MonthColumns, each {_, type any})
    ),

    // =================================================================
    // FLAG PERCENT ROWS
    // =================================================================
    // Mark rows that contain percentage values for special handling
    MarkPercentRow = Table.AddColumn(
        TypedWide, "Is_Percent",
        each Text.Contains(Record.Field(_, FirstColumnName), "%"),
        type logical
    ),

    // =================================================================
    // UNPIVOT TO LONG FORMAT
    // =================================================================
    Unpivoted = Table.UnpivotOtherColumns(
        MarkPercentRow,
        {FirstColumnName, "Row_Sort", "Is_Percent"},
        "Month",
        "ValueRaw"
    ),

    // =================================================================
    // ROBUST PERCENTAGE NORMALIZATION
    // =================================================================
    // Handle multiple formats:
    // - "50%" (text with %) → 0.50
    // - 50 (number > 1) → 0.50
    // - 0.50 (decimal) → 0.50
    // Excel now stores as decimals (per Claude update), but handle all formats
    Normalized = Table.AddColumn(
        Unpivoted, "Value",
        each
            let 
                v = [ValueRaw] 
            in
            if [Is_Percent] then
                // Handle percentage values
                if Value.Is(v, type text) then
                    let
                        s   = Text.Trim(v),
                        hasPct = Text.Contains(s, "%"),
                        n0  = try Number.From(Text.Replace(s, "%", "")) otherwise null,
                        n   = if n0 = null then null
                              else if hasPct then n0 / 100
                              else if n0 > 1 then n0 / 100 
                              else n0
                    in  n
                else
                    let
                        n0 = try Number.From(v) otherwise null,
                        // If already decimal (0.50), keep it; if whole number (50), divide by 100
                        n  = if n0 = null then null
                             else if n0 > 1 then n0 / 100 
                             else n0
                    in  n
            else
                // Handle count values (non-percentage rows)
                try Number.From(v) otherwise null,
        type number
    ),
    
    // Remove the raw value column
    Cleaned = Table.RemoveColumns(Normalized, {"ValueRaw"}),

    // =================================================================
    // DATE PARSING FROM MM-YY FORMAT
    // =================================================================
    // Parse "01-26" → #date(2026, 1, 1)
    WithDate = Table.AddColumn(Cleaned, "Date", each
        let
            mTxt = [Month],
            // Extract first 2 characters for month
            mStr = Text.Start(mTxt, 2),
            mNum = try Number.From(mStr) otherwise null,
            // Extract last 2 characters for year
            yStr = Text.End(mTxt, 2),
            y2   = try Number.From(yStr) otherwise null,
            // Assume 50+ = 19xx, else 20xx (only if y2 is valid number)
            y4   = if y2 = null then null 
                   else if y2 >= 50 then 1900 + y2 
                   else 2000 + y2
        in
            if mNum = null or y4 = null then null 
            else try #date(y4, mNum, 1) otherwise null,
        type date
    ),

    // =================================================================
    // ADDITIONAL DATE HELPER COLUMNS
    // =================================================================
    // Month_Year: "January 2026"
    WithMonthYear = Table.AddColumn(WithDate, "Month_Year", each 
        if [Date] = null then null 
        else Date.MonthName([Date]) & " " & Text.From(Date.Year([Date])), 
        type text),
    
    // Sort_Order: 202601 (numeric YYYYMM)
    WithSortOrder = Table.AddColumn(WithMonthYear, "Sort_Order", each 
        if [Date] = null then null 
        else Date.Year([Date]) * 100 + Date.Month([Date]), 
        Int64.Type),
    
    // Month_Abbrev: "01-26" (normalized format)
    WithAbbrev = Table.AddColumn(WithSortOrder, "Month_Abbrev", each 
        if [Date] = null then null 
        else Text.PadStart(Text.From(Date.Month([Date])), 2, "0") & "-" & 
             Text.End(Text.From(Date.Year([Date])), 2), 
        type text),

    // =================================================================
    // DISPOSITION CATEGORY GROUPING
    // =================================================================
    // Group dispositions into logical categories for analysis
    WithDispCat = Table.AddColumn(WithAbbrev, "Disposition_Category", each
        let 
            disp = Record.Field(_, FirstColumnName)
        in
            if Text.Contains(disp, "Active") or Text.Contains(disp, "Administratively") 
                then "Open Cases"
            else if Text.Contains(disp, "Arrest") or Text.Contains(disp, "Complaint") 
                then "Prosecuted"
            else if Text.Contains(disp, "Cleared") or Text.Contains(disp, "Unfounded") 
                then "Cleared"
            else if Text.Contains(disp, "%") 
                then "Performance Metric"
            else "Other",
        type text
    ),

    // =================================================================
    // ROLLING 13-MONTH WINDOW FILTER
    // =================================================================
    // Exclude current month (incomplete data)
    CurrentDate     = Date.From(DateTime.LocalNow()),
    EndFilterDate   = Date.AddMonths(Date.StartOfMonth(CurrentDate), -1),
    StartFilterDate = Date.AddMonths(EndFilterDate, -12),

    // Filter to only rows within the 13-month window
    FilteredMonths = Table.SelectRows(
        WithDispCat,
        each [Date] <> null and 
             [Date] >= StartFilterDate and 
             [Date] <= EndFilterDate
    ),

    // =================================================================
    // FINAL TYPE CONVERSIONS
    // =================================================================
    Final = Table.TransformColumnTypes(FilteredMonths, {
        {FirstColumnName, type text},
        {"Month", type text},
        {"Value", type number},
        {"Date", type date},
        {"Month_Year", type text},
        {"Sort_Order", Int64.Type},
        {"Month_Abbrev", type text},
        {"Disposition_Category", type text},
        {"Row_Sort", Int64.Type},
        {"Is_Percent", type logical}
    })
    
in
    Final
