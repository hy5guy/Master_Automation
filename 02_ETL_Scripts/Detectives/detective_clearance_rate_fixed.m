// Det_case_dispositions_clearance — CCD/_CCD_MOM
// Fixed row order • Robust % normalization • Rolling 13-Month window
// Updated: 2026-01-11 - Fixed to include December 2025 (12-25) in the filter
// Updated: 2026-02-21 - Replaced DateTime.LocalNow() with pReportMonth parameter

let
    ReportMonth = pReportMonth,
    // --- Load table ---------------------------------------------------------
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Detectives\detectives_monthly.xlsx"),
        null, true
    ),
    CCD_Table = Source{[Item="_CCD_MOM", Kind="Table"]}[Data],

    // --- Required order (exact labels) -------------------------------------
    RequiredOrder = {
        "Active / Administratively Closed",
        "Arrest",
        "Complaint Signed",
        "Ex Cleared / Closed",
        "Juvenile Complaint",
        "Stationhouse Adjustment",
        "TOT DCP&P",
        "Unfounded / Closed",
        "Monthly Bureau Case Clearance %"
    },

    // --- Shape & keep only the required labels -----------------------------
    ColNames        = Table.ColumnNames(CCD_Table),
    FirstColumnName = ColNames{0},
    MonthColumns    = List.Skip(ColNames, 1),

    KeptRows = Table.SelectRows(
        CCD_Table,
        (r) => List.Contains(RequiredOrder, Record.Field(r, FirstColumnName))
    ),

    // Add Row_Sort and order rows to lock display sequence
    WithRowSort = Table.AddColumn(
        KeptRows, "Row_Sort",
        each List.PositionOf(RequiredOrder, Record.Field(_, FirstColumnName)),
        Int64.Type
    ),
    OrderedRows = Table.Sort(WithRowSort, {{"Row_Sort", Order.Ascending}}),

    // Wide types: keep months as 'any' for now (we'll normalize after unpivot)
    TypedWide = Table.TransformColumnTypes(
        OrderedRows,
        {{FirstColumnName, type text}} & List.Transform(MonthColumns, each {_, type any})
    ),

    // Flag the percent row
    MarkPercentRow = Table.AddColumn(
        TypedWide, "Is_Percent",
        each Record.Field(_, FirstColumnName) = "Monthly Bureau Case Clearance %",
        type logical
    ),

    // --- Unpivot for tidy format -------------------------------------------
    Unpivoted = Table.UnpivotOtherColumns(
        MarkPercentRow,
        {FirstColumnName, "Row_Sort", "Is_Percent"},
        "Month",
        "ValueRaw"
    ),

    // --- Robust normalization ----------------------------------------------
    Normalized = Table.AddColumn(
        Unpivoted, "Value",
        each
            let v = [ValueRaw] in
            if [Is_Percent] then
                if Value.Is(v, type text) then
                    let
                        s   = Text.Trim(v),
                        hasPct = Text.Contains(s, "%"),
                        n0  = try Number.From(Text.Replace(s, "%", "")) otherwise null,
                        n   = if n0 = null then null
                              else if hasPct then n0 / 100
                              else if n0 > 1 then n0 / 100 else n0
                    in  n
                else
                    let
                        n0 = try Number.From(v) otherwise null,
                        n  = if n0 = null then null
                             else if n0 > 1 then n0 / 100 else n0
                    in  n
            else
                try Number.From(v) otherwise null,
        type number
    ),
    Cleaned = Table.RemoveColumns(Normalized, {"ValueRaw"}),

    // --- Date helpers from "MM-YY" -----------------------------------------
    WithDate = Table.AddColumn(Cleaned, "Date", each
        let
            mTxt = [Month],
            mNum = try Value.FromText(Text.Start(mTxt, 2)) otherwise null,
            y2   = try Value.FromText(Text.End(mTxt, 2)) otherwise null,
            y4   = if y2 = null then null else if y2 >= 50 then 1900 + y2 else 2000 + y2
        in
            if mNum = null or y4 = null then null else #date(y4, mNum, 1),
        type date
    ),

    WithMonthYear = Table.AddColumn(WithDate, "Month_Year", each if [Date] = null then null else Date.MonthName([Date]) & " " & Text.From(Date.Year([Date])), type text),
    WithSortOrder = Table.AddColumn(WithMonthYear, "Sort_Order", each if [Date] = null then null else Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type),
    WithAbbrev    = Table.AddColumn(WithSortOrder, "Month_Abbrev", each if [Date] = null then null else Text.PadStart(Text.From(Date.Month([Date])), 2, "0") & "-" & Text.End(Text.From(Date.Year([Date])), 2), type text),

    // Optional grouping
    WithDispCat = Table.AddColumn(WithAbbrev, "Disposition_Category", each
        let disp = Record.Field(_, FirstColumnName)
        in
            if Text.Contains(disp, "Active") or Text.Contains(disp, "Administratively") then "Open Cases"
            else if Text.Contains(disp, "Arrest") or Text.Contains(disp, "Complaint") then "Prosecuted"
            else if Text.Contains(disp, "Cleared") or Text.Contains(disp, "Unfounded") then "Cleared"
            else if disp = "Monthly Bureau Case Clearance %" then "Performance Metric"
            else "Other",
        type text
    ),

    // --- Rolling 13-Month window (include previous completed month) --------
    // Filter includes the previous completed month (December 2025 when current is January 2026)
    CurrentDate     = ReportMonth,
    CurrentYear     = Date.Year(CurrentDate),
    CurrentMonth    = Date.Month(CurrentDate),
    // Previous month: if current is January, previous is December of previous year
    EndYear         = if CurrentMonth = 1 then CurrentYear - 1 else CurrentYear,
    EndMonth        = if CurrentMonth = 1 then 12 else CurrentMonth - 1,
    EndFilterDate   = #date(EndYear, EndMonth, 1),
    StartFilterDate = Date.AddMonths(EndFilterDate, -12),

    FilteredMonths = Table.SelectRows(
        WithDispCat,
        each [Date] <> null and [Date] >= StartFilterDate and [Date] <= EndFilterDate
    ),

    // --- Final types --------------------------------------------------------
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
    }),
    #"Filtered Rows" = Table.SelectRows(Final, each true)
in
    #"Filtered Rows"
