// 🕒 2026-02-26-19-00-00 (EST)
// # summons/summons_all_bureaus.m
// # Author: R. A. Carucci
// # Purpose: Aggregate summons counts by bureau for moving and parking violations (previous complete month).
// # Note: pReportMonth is a Date type (#date(YYYY,M,1)); uses AddMonths(-1) to target the previous
// #   complete month so partial next-month records in the staging file cannot bleed into the visual.

let
    // Previous complete month (e.g. pReportMonth=02/01/2026 -> Jan 2026 -> PreviousMonthKey=202601)
    PrevDate = Date.AddMonths(DateTime.Date(pReportMonth), -1),
    PreviousMonthKey = Date.Year(PrevDate) * 100 + Date.Month(PrevDate),

    Source = Csv.Document(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_slim_for_powerbi.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{"YearMonthKey", Int64.Type}, {"TICKET_COUNT", Int64.Type}, {"TYPE", type text}, {"WG2", type text}}),

    // Filter out UNKNOWN / blank WG2, then filter to previous complete month
    FilteredClean = Table.SelectRows(ChangedType, each [WG2] <> "UNKNOWN" and [WG2] <> null and [WG2] <> ""),
    FilteredLatestMonth = Table.SelectRows(FilteredClean, each [YearMonthKey] = PreviousMonthKey),

    // Group by Bureau (WG2) and Type
    GroupedRows = Table.Group(
        FilteredLatestMonth,
        {"WG2", "TYPE"},
        {{"Count", each List.Sum([TICKET_COUNT]), type number}}
    ),

    // Consolidate HOUSING, OSO, and PATROL BUREAU into PATROL DIVISION
    ConsolidatedBureaus = Table.TransformColumns(
        GroupedRows,
        {"WG2", each if _ = "HOUSING" or _ = "OFFICE OF SPECIAL OPERATIONS" or _ = "PATROL BUREAU"
            then "PATROL DIVISION" else _}
    ),

    // Re-group after consolidation to merge any combined rows
    RegroupedRows = Table.Group(
        ConsolidatedBureaus,
        {"WG2", "TYPE"},
        {{"Count", each List.Sum([Count]), type number}}
    ),

    // Pivot by TYPE to get M, P columns
    PivotedColumn = Table.Pivot(
        RegroupedRows,
        List.Distinct(RegroupedRows[TYPE]),
        "TYPE",
        "Count",
        List.Sum
    ),

    AddM = if Table.HasColumns(PivotedColumn, "M") then PivotedColumn
        else Table.AddColumn(PivotedColumn, "M", each 0, Int64.Type),
    AddP = if Table.HasColumns(AddM, "P") then AddM
        else Table.AddColumn(AddM, "P", each 0, Int64.Type),

    ReplacedValue = Table.ReplaceValue(AddP, null, 0, Replacer.ReplaceValue, {"M", "P"}),

    AddedTotal = Table.AddColumn(
        ReplacedValue,
        "Total",
        each [M] + [P] + (try [C] otherwise 0),
        type number
    ),

    // Rename WG2 to Bureau for cleaner visual display
    RenamedColumns = Table.RenameColumns(AddedTotal, {{"WG2", "Bureau"}})
in
    RenamedColumns
