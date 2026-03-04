// ___Summons
// 🕒 2026-03-03
// # summons/___Summons.m
// # Author: R. A. Carucci
// # Purpose: Load enhanced summons dataset from ETL output
// (summons_powerbi_latest.xlsx). # TICKET_COUNT: use from source if present
// (ETL v2.1+); else add 1 per row.

let
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"),
        null, true
    ),
    ATS_Court_Data_Sheet = Source{[Item = "Summons_Data", Kind = "Sheet"]}[Data],
#"Promoted Headers" =                                                          \
    Table.PromoteHeaders(ATS_Court_Data_Sheet, [PromoteAllScalars = true]),

    ColumnTypes = {
        {"PADDED_BADGE_NUMBER", type text},
        {"OFFICER_DISPLAY_NAME", type text},
        {"WG1", type text}, {"WG2", type text}, {"WG3", type text}, {"WG4", type text}, {"WG5", type text},
        {"TICKET_NUMBER", type text},
        {"ISSUE_DATE", type datetime},
        {"VIOLATION_NUMBER", type text},
        {"VIOLATION_TYPE", type text},
        {"TYPE", type text},
        {"STATUS", type text},
        {"TOTAL_PAID_AMOUNT", type number},
        {"FINE_AMOUNT", type number},
        {"COST_AMOUNT", type number},
        {"MISC_AMOUNT", type number},
        {"Year", type number},
        {"Month", type number},
        {"YearMonthKey", type number},
        {"Month_Year", type text},
        {"DATA_QUALITY_SCORE", type number},
        {"DATA_QUALITY_TIER", type text},
        {"SOURCE_FILE", type text},
        {"PROCESSING_TIMESTAMP", type datetime},
        {"ETL_VERSION", type text}
    },
    ExistingColumns = Table.ColumnNames(#"Promoted Headers"),
    FilteredTypes = List.Select(ColumnTypes, each List.Contains(ExistingColumns, _{0})),
#"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",              \
                                             FilteredTypes),

    // TICKET_COUNT: use from source if present (ETL v2.1+); else add 1 per row
    WithTicketCount = if Table.HasColumns(#"Changed Type", "TICKET_COUNT")
        then Table.TransformColumnTypes(#"Changed Type", {{"TICKET_COUNT", Int64.Type}})
        else Table.AddColumn(#"Changed Type", "TICKET_COUNT", each 1, Int64.Type),

    WithAssignmentFound = if Table.HasColumns(WithTicketCount, "ASSIGNMENT_FOUND")
        then WithTicketCount
        else Table.AddColumn(WithTicketCount, "ASSIGNMENT_FOUND", each true, type logical)
in
    WithAssignmentFound

// pReportMonth
#date(2026, 2, 1) meta[IsParameterQuery = true, Type = "Date",                 \
                  IsParameterQueryRequired = true]

// summons_13month_trend
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

    Source = Excel.Workbook(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"), null, true),
    Summons_Data_Sheet = Source{[Item="Summons_Data",Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    // Only transform columns that exist (schema-resilient; avoids "column not found" errors)
    ExistingCols = Table.ColumnNames(PromotedHeaders),
    TypeMap = {
        {"PADDED_BADGE_NUMBER", type text},
        {"OFFICER_DISPLAY_NAME", type text},
        {"OFFICER_NAME_RAW", type text},
        {"ISSUE_DATE", type datetime},
        {"TYPE", type text},
        {"ETL_VERSION", type text},
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
    // Only for months where backfill was merged (01-25, 02-25), prefer WG2="Department-Wide" to avoid double-count.
    // Gap months 03-25, 07-25, 10-25, 11-25 have e-ticket data only (no backfill); keep bureau rows so they display.
    BackfillMonths = {"01-25", "02-25"},
    FilteredPreferBackfill = Table.SelectRows(FilteredMonthYear, each
        if List.Contains(BackfillMonths, [Month_Year]) then [WG2] = "Department-Wide" else true
    ),
    // TICKET_COUNT: use from source if present (ETL v2.1+ and backfill); else add 1 per row
    WithTicketCount = if Table.HasColumns(FilteredPreferBackfill, "TICKET_COUNT")
        then Table.TransformColumnTypes(FilteredPreferBackfill, {{"TICKET_COUNT", Int64.Type}})
        else Table.AddColumn(FilteredPreferBackfill, "TICKET_COUNT", each 1, Int64.Type),
    AddConsolidatedBureau = Table.AddColumn(WithTicketCount, "Bureau_Consolidated", each if [WG2] = "HOUSING" or [WG2] = "OFFICE OF SPECIAL OPERATIONS" or [WG2] = "PATROL BUREAU" then "PATROL DIVISION" else [WG2], type text)
in
    AddConsolidatedBureau

// summons_all_bureaus
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

    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"),
        null, true
    ),
    Summons_Data_Sheet = Source{[Item="Summons_Data", Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{"YearMonthKey", Int64.Type}, {"TYPE", type text}, {"WG2", type text}}),

    // Filter out UNKNOWN / blank WG2, then filter to previous complete month
    FilteredClean = Table.SelectRows(ChangedType, each [WG2] <> "UNKNOWN" and [WG2] <> null and [WG2] <> ""),
    FilteredLatestMonth = Table.SelectRows(FilteredClean, each [YearMonthKey] = PreviousMonthKey),

    // Group by Bureau (WG2) and Type
    GroupedRows = Table.Group(
        FilteredLatestMonth,
        {"WG2", "TYPE"},
        {{"Count", each Table.RowCount(_), type number}}
    ),

    // Consolidate HOUSING, OSO, and PATROL BUREAU into PATROL DIVISION
    ConsolidatedBureaus = Table.TransformColumns(
        GroupedRows,
        {
  "WG2", each if _ = "HOUSING" or _ =
                         "OFFICE OF SPECIAL OPERATIONS" or _ =
                             "PATROL BUREAU" then "PATROL DIVISION" else _}
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

// ___Summons_Diagnostic
// ___Summons_Diagnostic
// Diagnostic query to see what's actually in the summons data
// Use this temporarily to understand the data structure

let
    Source = Excel.Workbook(
        File.Contents(
            "C:/Users/carucci_r/OneDrive - City of Hackensack/03_Staging/Summons/summons_powerbi_latest.xlsx"
        ),
        null,
        true
    ),
    ATS_Court_Data_Sheet = Source{[Item = "Summons_Data", Kind = "Sheet"]}[Data],
#"Promoted Headers" = 
        Table.PromoteHeaders(ATS_Court_Data_Sheet, [PromoteAllScalars = true]),
    
    // Get column names
    ColumnNames = Table.ColumnNames(#"Promoted Headers"),
    
    // Most recent month
    MaxYearMonthKey = List.Max(#"Promoted Headers"[YearMonthKey]),
    Recent = Table.SelectRows(#"Promoted Headers", each [YearMonthKey] = MaxYearMonthKey),
    
    // Show distinct TYPE values
    DistinctTypes = Table.Distinct(Table.SelectColumns(Recent, {"TYPE"})),
    
    // Show distinct WG2 values
    DistinctWG2 = Table.Distinct(Table.SelectColumns(Recent, {"WG2"})),
    
    // Count by TYPE
    TypeCounts = Table.Group(
        Recent,
        {"TYPE"},
        {{"Count", each Table.RowCount(_), Int64.Type}}
    ),
    
    // Sample of recent data
    Sample = Table.FirstN(Recent, 10)
in
    Sample

// summons_top5_moving
// ___Summons_Top5_Moving (Standalone)
// Updated: 2026-02-17
// Purpose: Top 5 Moving Violations for PREVIOUS COMPLETE MONTH (so "January export" shows 01-26, not partial Feb)

let
    // Previous complete month (e.g. in Feb 2026 show Jan 2026 = 01-26)
    PrevDate = Date.AddMonths(DateTime.Date(pReportMonth), -1),
    PrevYear = Date.Year(PrevDate),
    PrevMonth = Date.Month(PrevDate),
    PreviousMonthKey = PrevYear * 100 + PrevMonth,
    MonthYearText = Text.PadStart(Number.ToText(PrevMonth), 2, "0") & "-" & Text.End(Number.ToText(PrevYear), 2),

    // Load directly from Excel file
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"),
        null,
        true
    ),

    // Get Summons_Data sheet
    Summons_Data_Sheet = Source{[Item="Summons_Data", Kind="Sheet"]}[Data],
    
    // Promote headers
    PromotedHeaders = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars = true]),
    
    // Ensure TITLE column exists (ETL adds it from Assignment Master; if missing, add null)
    WithTitle = if Table.HasColumns(PromotedHeaders, "TITLE") then PromotedHeaders else Table.AddColumn(PromotedHeaders, "TITLE", each null, type text),
    
    // Change YearMonthKey and TYPE; TITLE as text
    ChangedType = Table.TransformColumnTypes(WithTitle, { { "YearMonthKey", Int64.Type}, { "TYPE", type text}, { "TITLE", type text} }),
    
    // Filter to Moving violations only
    FilteredMoving = Table.SelectRows(ChangedType, each([TYPE] = "M")),
    
    // EXCLUDE PEO: by TITLE = "PEO" (Assignment Master); fallback on display name
    FilteredMovingNoPEO = Table.SelectRows(FilteredMoving, each
        ([TITLE] = null or Text.Trim(Text.Upper([TITLE] ?? "")) <> "PEO") and
        ([OFFICER_DISPLAY_NAME] = null or not(Text.StartsWith([OFFICER_DISPLAY_NAME], "PEO ") or Text.StartsWith([OFFICER_DISPLAY_NAME], "PEO,") or Text.StartsWith([OFFICER_DISPLAY_NAME], "PEO.")))
    ),
    
    // Filter to PREVIOUS COMPLETE MONTH (not "max in file" — so January export shows 01-26)
    FilteredLatestMonth = Table.SelectRows(FilteredMovingNoPEO, each[YearMonthKey] = PreviousMonthKey),
    
    // Group by badge: Count = number of Moving rows per officer for that month (from staging file)
    GroupedRows = Table.Group(
        FilteredLatestMonth,
        { "PADDED_BADGE_NUMBER", "Month_Year"}, 
        {
    { "Count", each Table.RowCount(_), type number},
            { "Officer", each List.First([OFFICER_DISPLAY_NAME]), type text}
}
    ),
    
    RemovedBadge = Table.RemoveColumns(GroupedRows, { "PADDED_BADGE_NUMBER"}),
    SortedRows = Table.Sort(RemovedBadge, { { "Count", Order.Descending} }),
    Top5 = Table.FirstN(SortedRows, 5),
    // Ensure Month_Year label matches previous month (e.g. 01-26)
    SetMonthLabel = Table.TransformColumns(Top5, { { "Month_Year", each MonthYearText, type text} })
in
    SetMonthLabel

// summons_top5_parking
// ___Summons_Top5_Parking (Standalone)
// Updated: 2026-02-17
// Purpose: Top 5 Parking Violations for LATEST MONTH (loads directly from Excel)

let
    // Load directly from Excel file
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"),
        null, 
        true
    ),
    
    // Get Summons_Data sheet
    Summons_Data_Sheet = Source{[Item="Summons_Data", Kind="Sheet"]}[Data],
    
    // Promote headers
    PromotedHeaders = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    
    // Change YearMonthKey to number type
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{"YearMonthKey", Int64.Type}, {"TYPE", type text}}),
    
    // Filter to Parking violations only
    FilteredParking = Table.SelectRows(ChangedType, each ([TYPE] = "P")),
    
    // Find LATEST month using YearMonthKey (integer sorting, not text!)
    LatestKey = List.Max(FilteredParking[YearMonthKey]),
    
    // Filter to latest month only
    FilteredLatestMonth = Table.SelectRows(FilteredParking, each [YearMonthKey] = LatestKey),
    
    // Group by OFFICER and count summons
    GroupedRows = Table.Group(
        FilteredLatestMonth, 
        {"OFFICER_DISPLAY_NAME", "Month_Year"}, 
        {{"Count", each Table.RowCount(_), type number}}
    ),
    
    // Sort by count descending
    SortedRows = Table.Sort(GroupedRows, {{"Count", Order.Descending}}),
    
    // Keep top 5
    Top5 = Table.FirstN(SortedRows, 5),
    
    // RENAME COLUMNS TO MATCH VISUAL EXPECTATIONS
    RenamedColumns = Table.RenameColumns(Top5, {
        {"OFFICER_DISPLAY_NAME", "Officer"}
    })
in
    RenamedColumns