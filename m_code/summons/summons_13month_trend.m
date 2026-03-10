// 🕒 2026-03-03
// # summons/summons_13month_trend.m
// # Author: R. A. Carucci
// # Purpose: Load summons data from staging workbook for 13-month trend analysis.
// # Rolling 13-month window driven by pReportMonth: EndDate = pReportMonth (includes report month),
// #   StartDate = 12 months before. E.g. pReportMonth=02/01/2026 → 02-25 through 02-26.
// # Filters out blank/malformed Month_Year (fixes "02-25 no header" and wrong values).

let
    // 13-month window: report month through 12 months back (e.g. pReportMonth=02/01/2026 → 02-25 through 02-26)
    EndDate = DateTime.Date(pReportMonth),
    StartDate = Date.AddMonths(EndDate, -12),
    EndYM = Date.Year(EndDate) * 100 + Date.Month(EndDate),
    StartYM = Date.Year(StartDate) * 100 + Date.Month(StartDate),

    Source = Csv.Document(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_slim_for_powerbi.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    // Only transform columns that exist (schema-resilient; avoids "column not found" errors)
    ExistingCols = Table.ColumnNames(PromotedHeaders),
    TypeMap = {
        {"PADDED_BADGE_NUMBER", type text},
        {"OFFICER_DISPLAY_NAME", type text},
        {"OFFICER_NAME_RAW", type text},
        {"ISSUE_DATE", type datetime},
        {"TYPE", type text},
        {"ETL_VERSION", type text},
        {"IS_AGGREGATE", type text},
        {"Year", Int64.Type},
        {"Month", Int64.Type},
        {"YearMonthKey", Int64.Type},
        {"Month_Year", type text},
        {"WG2", type text},
        {"DATA_QUALITY_SCORE", Int64.Type}
    },
    FilteredTypes = List.Select(TypeMap, each List.Contains(ExistingCols, _{0})),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, FilteredTypes),
    FilteredClean = Table.SelectRows(ChangedType, each [WG2] <> null and [WG2] <> "" and [WG2] <> "UNKNOWN"),
    // Filter to 13-month window; exclude null YearMonthKey (fixes blank header / wrong values)
    FilteredMonthYear = Table.SelectRows(FilteredClean, each
        [YearMonthKey] <> null and [YearMonthKey] >= StartYM and [YearMonthKey] <= EndYM
    ),
    // For gap months with no e-ticket data (only backfill aggregates), keep IS_AGGREGATE rows.
    // As of 2026-03-10: only 07-25 is a true gap. All other 2025 months have individual e-ticket data.
    BackfillMonths = {"07-25"},
    FilteredPreferBackfill = Table.SelectRows(FilteredMonthYear, each
        if List.Contains(BackfillMonths, [Month_Year])
        then Text.Upper(Text.From([IS_AGGREGATE] ?? "false")) = "TRUE"
        else true
    ),
    // TICKET_COUNT: use from source if present (ETL v2.1+ and backfill); else add 1 per row
    WithTicketCount = if Table.HasColumns(FilteredPreferBackfill, "TICKET_COUNT")
        then Table.TransformColumnTypes(FilteredPreferBackfill, {{"TICKET_COUNT", Int64.Type}})
        else Table.AddColumn(FilteredPreferBackfill, "TICKET_COUNT", each 1, Int64.Type),
    AddConsolidatedBureau = Table.AddColumn(WithTicketCount, "Bureau_Consolidated", each if [WG2] = "HOUSING" or [WG2] = "OFFICE OF SPECIAL OPERATIONS" or [WG2] = "PATROL BUREAU" then "PATROL DIVISION" else [WG2], type text)
in
    AddConsolidatedBureau
