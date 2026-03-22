// 🕒 2026-03-21-23-00-00 (EST)
// # summons/summons_revenue_by_bureau.m
// # Author: R. A. Carucci
// # Purpose: Aggregate YTD summons revenue (FINE_AMOUNT) by bureau (WG2)
// #          for the reporting year defined by pReportMonth.
// # Note: pReportMonth is a Date type (#date(YYYY,M,1)); YTD window = Jan 1 of
// #       pReportMonth year through previous complete month.
// # Depends on: summons_slim_for_powerbi.csv v1.19.1+ (25-column schema with FINE_AMOUNT)
// # Resolves: Issue #6
let
    // YTD window: Jan 1 of pReportMonth year through previous complete month
    PrevDate = Date.AddMonths(DateTime.Date(pReportMonth), -1),
    YearStart = Date.StartOfYear(PrevDate),
    YearStartKey = Date.Year(YearStart) * 100 + 1,
    PrevMonthKey = Date.Year(PrevDate) * 100 + Date.Month(PrevDate),

    Source = Csv.Document(
        File.Contents("C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\03_Staging\\Summons\\summons_slim_for_powerbi.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedType = Table.TransformColumnTypes(
        PromotedHeaders,
        {{"YearMonthKey", Int64.Type}, {"FINE_AMOUNT", type number}, {"WG2", type text}}
    ),

    // Filter out UNKNOWN / blank / "nan" WG2
    FilteredClean = Table.SelectRows(
        ChangedType,
        each [WG2] <> "UNKNOWN" and [WG2] <> "nan" and [WG2] <> null and [WG2] <> ""
    ),
    // Filter to YTD range (YearStartKey through PrevMonthKey)
    FilteredYTD = Table.SelectRows(
        FilteredClean,
        each [YearMonthKey] >= YearStartKey and [YearMonthKey] <= PrevMonthKey
    ),

    // Consolidate HOUSING, OSO, and PATROL BUREAU into PATROL DIVISION
    ConsolidatedBureaus = Table.TransformColumns(
        FilteredYTD,
        {"WG2", each if _ = "HOUSING" or _ = "OFFICE OF SPECIAL OPERATIONS" or _ = "PATROL BUREAU"
                     then "PATROL DIVISION" else _}
    ),

    // Sum FINE_AMOUNT by bureau
    GroupedRevenue = Table.Group(
        ConsolidatedBureaus,
        {"WG2"},
        {{"Revenue", each List.Sum([FINE_AMOUNT]), type number}}
    ),
    RenamedColumns = Table.RenameColumns(GroupedRevenue, {{"WG2", "Bureau"}}),
    SortedTable = Table.Sort(RenamedColumns, {{"Revenue", Order.Descending}})
in
    SortedTable
