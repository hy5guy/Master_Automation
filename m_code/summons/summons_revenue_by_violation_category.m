// 🕒 2026-03-21-23-00-00 (EST)
// # summons/summons_revenue_by_violation_category.m
// # Author: R. A. Carucci
// # Purpose: Aggregate YTD summons revenue (FINE_AMOUNT) by VIOLATION_CATEGORY
// #          for the reporting year defined by pReportMonth.
// # Note: pReportMonth is a Date type (#date(YYYY,M,1)); YTD window = Jan 1 of
// #       pReportMonth year through previous complete month.
// # Depends on: summons_slim_for_powerbi.csv v1.19.1+ (25-column schema with VIOLATION_CATEGORY)
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
        {{"YearMonthKey", Int64.Type}, {"FINE_AMOUNT", type number}, {"VIOLATION_CATEGORY", type text}}
    ),

    // Filter out null / blank / "nan" VIOLATION_CATEGORY
    FilteredClean = Table.SelectRows(
        ChangedType,
        each [VIOLATION_CATEGORY] <> null and [VIOLATION_CATEGORY] <> "" and [VIOLATION_CATEGORY] <> "nan"
    ),
    // Filter to YTD range (YearStartKey through PrevMonthKey)
    FilteredYTD = Table.SelectRows(
        FilteredClean,
        each [YearMonthKey] >= YearStartKey and [YearMonthKey] <= PrevMonthKey
    ),

    // Sum FINE_AMOUNT by VIOLATION_CATEGORY
    GroupedByCategory = Table.Group(
        FilteredYTD,
        {"VIOLATION_CATEGORY"},
        {{"Revenue", each List.Sum([FINE_AMOUNT]), type number}}
    ),
    SortedTable = Table.Sort(GroupedByCategory, {{"Revenue", Order.Descending}})
in
    SortedTable
