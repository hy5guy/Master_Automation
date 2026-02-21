// 🕒 2026-02-21-01-00-00 (EST)
// # detectives/___Det_case_dispositions_clearance.m
// # Author: R. A. Carucci
// # Purpose: Load case disposition and clearance rates for Detective Division with 13-month window.

let
    ReportMonth = pReportMonth,
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
    // These labels must match Excel exactly (including extra spaces)
    // Note: "Monthly Bureau Case  Clearance % " has DOUBLE space before "Clearance" and trailing space
    RequiredOrder = {
        "Active / Administratively Closed",
        "Arrest",
        "Complaint Signed",
        "Ex Cleared / Closed",
        "Juvenile Complaint",
        "Stationhouse Adjustment",
        "TOT DCP&P",
        "Unfounded / Closed",
        "Monthly Bureau Case  Clearance % ",  // Double space + trailing space (as in Excel)
        "YTD Bureau Case Clearance % "  // Trailing space (as in Excel)
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
    // Note: Now uses exact match (not Text.Trim) to preserve Excel labels
    KeptRows = Table.SelectRows(
        CCD_Table,
        (r) => List.Contains(RequiredOrder, Record.Field(r, FirstColumnName))
    ),

    // =================================================================
    // ADD ROW SORT ORDER
    // =================================================================
    // Add Row_Sort column to maintain display order
    // Note: Now uses exact match (not Text.Trim) to preserve Excel labels
    WithRowSort = Table.AddColumn(
        KeptRows, "Row_Sort",
        each List.PositionOf(RequiredOrder, Record.Field(_, FirstColumnName)),
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
            Parts = Text.Split(mTxt, "-"),
            // Parts{0} = MM (month), Parts{1} = YY (year)
            MonthPart = if List.Count(Parts) >= 1 then Parts{0} else "01",
            YearPart = if List.Count(Parts) >= 2 then Parts{1} else "26",
            
            // Convert 2-digit year to full year
            y2 = try Number.From(YearPart) otherwise null,
            y4 = if y2 = null then null 
                 else if y2 >= 50 then 1900 + y2 
                 else 2000 + y2,
            
            // Convert month to number (01=1, 02=2, etc.)
            mNum = try Number.From(MonthPart) otherwise null
        in
            if mNum = null or y4 = null then null 
            else try #date(y4, mNum, 1) otherwise null,
        type date
    ),

    // =================================================================
    // ADDITIONAL DATE HELPER COLUMNS
    // =================================================================
    // Add normalized Month_Normalized column in MM-YY format
    WithNormalizedMonth = Table.AddColumn(WithDate, "Month_Normalized", each 
        if [Date] <> null then 
            Text.PadStart(Text.From(Date.Month([Date])), 2, "0") & "-" & 
            Text.End(Text.From(Date.Year([Date])), 2)
        else [Month], 
        type text),
    
    // Remove old Month and rename Month_Normalized to Month
    RemovedOldMonth = Table.RemoveColumns(WithNormalizedMonth, {"Month"}),
    RenamedMonth = Table.RenameColumns(RemovedOldMonth, {{"Month_Normalized", "Month"}}),
    
    // Month_Year: "January 2026"
    WithMonthYear = Table.AddColumn(RenamedMonth, "Month_Year", each 
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
    // DATE RANGE FILTER (ROLLING 13-MONTH WINDOW)
    // =================================================================
    // Table contains historical data from Jun 2023 onwards
    // Show rolling 13 months ending with the previous complete month
    
    CurrentDate     = ReportMonth,
    EndFilterDate   = Date.AddMonths(Date.StartOfMonth(CurrentDate), -1),
    
    // Start date = 13 months before end date (rolling 13-month window)
    StartFilterDate = Date.AddMonths(EndFilterDate, -12),

    // Filter to only rows within the date range
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
