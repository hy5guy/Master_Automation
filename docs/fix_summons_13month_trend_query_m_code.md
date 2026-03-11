**Fix applied 2026-03-11 (v1.18.2).** Original issue: summons_13month_trend query had errors — Row Number	TICKET_NUMBER	STATUS	ISSUE_DATE	STATUTE	VIOLATION_DESCRIPTION	OFFICER_DISPLAY_NAME	PADDED_BADGE_NUMBER	TYPE	WG1	WG2	YearMonthKey	Month_Year	Year	Month	TICKET_COUNT	IS_AGGREGATE	ETL_VERSION	DATA_QUALITY_SCORE	OFFICER_NAME_RAW	SOURCE_FILE	PROCESSING_TIMESTAMP	TITLE	RANK	Bureau_Consolidated
43418	null	null		null	null	null	null	P	null	null	202507	07-25	null	null	0	null	null	null	null	null	null	null	null	null
43419	null	null		null	null	null	null	C	null	null	202507	07-25	null	null	0	null	null	null	null	null	null	null	null	null

Current m code:
// 🕒 2026-03-03
// # summons/summons_13month_trend.m
// # Author: R. A. Carucci
// # Purpose: Load summons data from staging workbook for 13-month trend analysis.
// # Rolling 13-month window driven by pReportMonth: EndDate = pReportMonth - 1 (previous complete month),
// #   StartDate = 12 months before EndDate. E.g. pReportMonth=03/01/2026 → 02-25 through 02-26.
// # Filters out blank/malformed Month_Year (fixes "02-25 no header" and wrong values).

let
    // 13-month window ending at previous complete month (pReportMonth - 1), spanning 12 months back.
    // e.g. pReportMonth=03/01/2026 → EndDate=Feb 2026, StartDate=Feb 2025 → 02-25 through 02-26
    EndDate = Date.AddMonths(DateTime.Date(pReportMonth), -1),
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
    // No WG2 filter here — this is the department-wide trend; all officers count regardless of bureau assignment.
    // Bureau-level filtering happens in summons_all_bureaus.m only.
    // Filter to 13-month window; exclude null YearMonthKey (fixes blank header / wrong values)
    FilteredMonthYear = Table.SelectRows(ChangedType, each
        [YearMonthKey] <> null and [YearMonthKey] >= StartYM and [YearMonthKey] <= EndYM
    ),
    // Backfill filtering: no gap months currently need special handling.
    // 07-25 has 17 straggler e-ticket records (no backfill file exists). Show them as-is rather than hiding them.
    // If a backfill CSV is added for July 2025 in the future, add "07-25" to BackfillMonths below.
    BackfillMonths = {},
    FilteredPreferBackfill = Table.SelectRows(FilteredMonthYear, each
        if List.Contains(BackfillMonths, [Month_Year])
        then Text.Upper(Text.From([IS_AGGREGATE] ?? "false")) = "TRUE"
        else true
    ),
    // TICKET_COUNT: use from source if present (ETL v2.1+ and backfill); else add 1 per row
    WithTicketCount = if Table.HasColumns(FilteredPreferBackfill, "TICKET_COUNT")
        then Table.TransformColumnTypes(FilteredPreferBackfill, {{"TICKET_COUNT", Int64.Type}})
        else Table.AddColumn(FilteredPreferBackfill, "TICKET_COUNT", each 1, Int64.Type),
    AddConsolidatedBureau = Table.AddColumn(WithTicketCount, "Bureau_Consolidated", each if [WG2] = "HOUSING" or [WG2] = "OFFICE OF SPECIAL OPERATIONS" or [WG2] = "PATROL BUREAU" then "PATROL DIVISION" else [WG2], type text),

    // Append filler rows for missing (Month_Year, TYPE) so 07-25 P shows 0 not blank (backfill gap fix)
    Grouped = Table.Group(AddConsolidatedBureau, {"Month_Year", "TYPE"}, {{"TICKET_COUNT", each List.Sum([TICKET_COUNT]), type number}}),
    MonthYMs = List.Generate(() => StartYM, each _ <= EndYM, each Number.RoundDown(_ / 100) * 100 + Number.Mod(_, 100) + (if Number.Mod(_, 100) = 12 then 89 else 1)),
    MonthYearLabels = List.Transform(MonthYMs, each Date.ToText(#date(Number.RoundDown(_ / 100), Number.Mod(_, 100), 1), "MM-yy")),
    AllTypes = {"M", "P", "C"},
    FullCross = List.TransformMany(MonthYearLabels, each AllTypes, (my, t) => [Month_Year = my, TYPE = t]),
    CrossTable = Table.FromRecords(FullCross),
    Merged = Table.NestedJoin(CrossTable, {"Month_Year", "TYPE"}, Grouped, {"Month_Year", "TYPE"}, "Grp", JoinKind.LeftOuter),
    Expanded = Table.ExpandTableColumn(Merged, "Grp", {"TICKET_COUNT"}, {"TICKET_COUNT"}),
    FilledZeros = Table.ReplaceValue(Expanded, null, 0, Replacer.ReplaceValue, {"TICKET_COUNT"}),
    MissingRows = Table.SelectRows(FilledZeros, each [TICKET_COUNT] = 0),
    AddIssueDate = Table.AddColumn(MissingRows, "ISSUE_DATE", each
        let parts = Text.Split([Month_Year], "-"),
            m = Number.From(parts{0}),
            y = 2000 + Number.From(parts{1})
        in #date(y, m, 1), type datetime),
    AddYearMonthKey = Table.AddColumn(AddIssueDate, "YearMonthKey", each Date.Year([ISSUE_DATE]) * 100 + Date.Month([ISSUE_DATE]), Int64.Type),
    FillerRows = Table.SelectColumns(AddYearMonthKey, {"Month_Year", "TYPE", "TICKET_COUNT", "ISSUE_DATE", "YearMonthKey"}),
    Combined = Table.Combine({AddConsolidatedBureau, FillerRows})
in
    Combined

Finial M Code
// 🕒 2026-03-11
// # summons/summons_13month_trend.m
// # Author: R. A. Carucci
// # Purpose: Load summons data from staging CSV for 13-month trend analysis.
// # Rolling 13-month window driven by pReportMonth: EndDate = pReportMonth - 1 (previous complete month),
// #   StartDate = 12 months before EndDate. E.g. pReportMonth=03/01/2026 → 02-25 through 02-26.
// # No filler rows — missing month/type combinations show blank; use visual settings or DAX COALESCE for 0.

let
    // 13-month window ending at previous complete month
    EndDate   = Date.AddMonths(DateTime.Date(pReportMonth), -1),
    StartDate = Date.AddMonths(EndDate, -12),
    EndYM     = Date.Year(EndDate)   * 100 + Date.Month(EndDate),
    StartYM   = Date.Year(StartDate) * 100 + Date.Month(StartDate),

    Source = Csv.Document(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_slim_for_powerbi.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    // Schema-resilient: only transform columns that actually exist in the CSV
    ExistingCols = Table.ColumnNames(PromotedHeaders),
    TypeMap = {
        {"PADDED_BADGE_NUMBER",   type text},
        {"OFFICER_DISPLAY_NAME",  type text},
        {"OFFICER_NAME_RAW",      type text},
        {"ISSUE_DATE",            type datetime},
        {"TYPE",                  type text},
        {"ETL_VERSION",           type text},
        {"IS_AGGREGATE",          type text},
        {"Year",                  Int64.Type},
        {"Month",                 Int64.Type},
        {"YearMonthKey",          Int64.Type},
        {"Month_Year",            type text},
        {"WG2",                   type text},
        {"DATA_QUALITY_SCORE",    Int64.Type}
    },
    FilteredTypes = List.Select(TypeMap, each List.Contains(ExistingCols, _{0})),
    ChangedType   = Table.TransformColumnTypes(PromotedHeaders, FilteredTypes),

    // Filter to 13-month window; drop rows with null/zero YearMonthKey (malformed CSV rows)
    FilteredMonthYear = Table.SelectRows(ChangedType, each
        [YearMonthKey] <> null and [YearMonthKey] > 0
        and [YearMonthKey] >= StartYM
        and [YearMonthKey] <= EndYM
    ),

    // BackfillMonths: months where BOTH backfill aggregate and e-ticket rows exist.
    // Keep only IS_AGGREGATE=TRUE rows for those months to avoid double-counting.
    // Currently empty — no gap months require backfill filtering.
    // To add a month: BackfillMonths = {"01-25", "02-25"}
    BackfillMonths = {},
    FilteredPreferBackfill = Table.SelectRows(FilteredMonthYear, each
        if List.Contains(BackfillMonths, [Month_Year])
        then Text.Upper(Text.From([IS_AGGREGATE] ?? "false")) = "TRUE"
        else true
    ),

    // TICKET_COUNT: use from CSV if present; add 1 per row otherwise.
    // Also fill nulls with 0 to prevent null propagation in DAX SUM.
    WithTicketCount = if Table.HasColumns(FilteredPreferBackfill, "TICKET_COUNT")
        then Table.ReplaceValue(
            Table.TransformColumnTypes(FilteredPreferBackfill, {{"TICKET_COUNT", Int64.Type}}),
            null, 0, Replacer.ReplaceValue, {"TICKET_COUNT"}
        )
        else Table.AddColumn(FilteredPreferBackfill, "TICKET_COUNT", each 1, Int64.Type),

    // Bureau consolidation: Housing, OSO, and Patrol Bureau → Patrol Division
    AddConsolidatedBureau = Table.AddColumn(
        WithTicketCount,
        "Bureau_Consolidated",
        each if [WG2] = "HOUSING"
                or [WG2] = "OFFICE OF SPECIAL OPERATIONS"
                or [WG2] = "PATROL BUREAU"
             then "PATROL DIVISION"
             else [WG2],
        type text
    )
in
    AddConsolidatedBureau 

Critical Files

m_code/summons/summons_13month_trend.m — only file that changes
Source data: 03_Staging\Summons\summons_slim_for_powerbi.csv (not modified)

What This Fixes
BeforeAfterRows 43418, 43419 exist with all-null columns and TICKET_COUNT=0No filler rows; only actual data rows in tableTable.Combine schema mismatch → null pollutionNo Table.Combine → no schema mismatchTICKET_COUNT can be null for real data rows (propagates to SUM)TICKET_COUNT null → 0 filled before returningBackfillMonths = {} was a no-op with no commentKept with explanatory comment on how to populate it
What This Does NOT Fix (By Design)

07-25 Parking (P) and Court (C) will show blank (not 0) in the trend visual for those types. Fix in Power BI: on the trend visual, turn on "Show items with no data" for the Month_Year axis, or create a DAX measure: Total Tickets = COALESCE(SUM(summons_13month_trend[TICKET_COUNT]), 0)
March 2025 (03-25) is still a data gap — no e-ticket or backfill CSV exists for it

Verification

In Power Query Editor, paste the new M code into Advanced Editor for summons_13month_trend
Click Done — confirm no red error banners
In the query preview, verify:

No rows with all-null columns and TICKET_COUNT=0
Total row count is lower than before (14 filler rows removed)
Row count for 07-25 is only the 17 existing M-type e-ticket records, no P=0 or C=0 rows
YearMonthKey is numeric (e.g., 202507, 202601) — not null
TICKET_COUNT contains no nulls (0 for rows that were null)


Click Close & Apply
In the trend visual: confirm 07-25 bar still appears (for M records); P and C bars for 07-25 may be absent or 0 depending on visual "show items with no data" setting
Confirm no [blank] entries appear in WG2 or OFFICER_DISPLAY_NAME slicers caused by the old null rows