// 🕒 2026-02-26-18-30-00 (EST)
// # summons/summons_all_bureaus.m
// # Author: R. A. Carucci
// # Purpose: Aggregate summons counts by bureau for moving and parking violations (report month).
// # Note: Uses pReportMonth ("YYYY-MM") instead of List.Max to avoid partial next-month records
// #   bleeding into the visual when the staging file contains early tickets from the following month.

let
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"),
        null, true
    ),
    Summons_Data_Sheet = Source{[Item="Summons_Data", Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{"YearMonthKey", Int64.Type}, {"TYPE", type text}, {"WG2", type text}}),

    // Derive target YearMonthKey from pReportMonth ("YYYY-MM" -> YYYYMM integer)
    ReportMonthParts = Text.Split(pReportMonth, "-"),
    ReportYearMonthKey = Number.From(ReportMonthParts{0} & ReportMonthParts{1}),

    // Filter to report month only (prevents partial next-month spillover from affecting totals)
    FilteredLatestMonth = Table.SelectRows(ChangedType, each [YearMonthKey] = ReportYearMonthKey),
    FilteredClean = Table.SelectRows(FilteredLatestMonth, each
        [WG2] <> null and [WG2] <> "" and [WG2] <> "UNKNOWN"),

    // Group by Bureau and Type
    GroupedRows = Table.Group(FilteredClean, {"WG2", "TYPE"},
        {{"Count", each Table.RowCount(_), type number}}),

    // Consolidate HOUSING, OSO, and PATROL BUREAU into PATROL DIVISION
    ConsolidatedBureaus = Table.TransformColumns(GroupedRows,
        {"WG2", each if _ = "HOUSING" or _ = "OFFICE OF SPECIAL OPERATIONS" or _ = "PATROL BUREAU"
            then "PATROL DIVISION" else _}),

    // Re-group after consolidation
    RegroupedRows = Table.Group(ConsolidatedBureaus, {"WG2", "TYPE"},
        {{"Count", each List.Sum([Count]), type number}}),

    // Pivot by TYPE to get M, P columns
    PivotedColumn = Table.Pivot(RegroupedRows,
        List.Distinct(RegroupedRows[TYPE]), "TYPE", "Count", List.Sum),

    AddM = if Table.HasColumns(PivotedColumn, "M") then PivotedColumn
        else Table.AddColumn(PivotedColumn, "M", each 0, Int64.Type),
    AddP = if Table.HasColumns(AddM, "P") then AddM
        else Table.AddColumn(AddM, "P", each 0, Int64.Type),

    ReplacedValue = Table.ReplaceValue(AddP, null, 0, Replacer.ReplaceValue, {"M", "P"}),

    AddedTotal = Table.AddColumn(ReplacedValue, "Total",
        each [M] + [P] + (try [C] otherwise 0), type number),

    // Rename WG2 to Bureau for cleaner visual display
    RenamedBureau = Table.RenameColumns(AddedTotal, {{"WG2", "Bureau"}})
in
    RenamedBureau
