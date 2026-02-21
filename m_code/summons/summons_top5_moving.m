// 🕒 2026-02-20-23-48-50
// # summons/summons_top5_moving.m
// # Author: R. A. Carucci
// # Purpose: Compute top 5 moving violation officers for the latest month.

let
    // Previous complete month (e.g. in Feb 2026 show Jan 2026 = 01-26)
    PrevDate = Date.AddMonths(DateTime.Date(DateTime.LocalNow()), -1),
    PrevYear = Date.Year(PrevDate),
    PrevMonth = Date.Month(PrevDate),
    PreviousMonthKey = PrevYear * 100 + PrevMonth,
    MonthYearText = Text.PadStart(Number.ToText(PrevMonth), 2, "0") & "-" & Text.End(Number.ToText(PrevYear), 2),

    // Load directly from Excel file
    Source = Excel.Workbook(
        File.Contents("C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"),
        null, 
        true
    ),
    
    // Get Summons_Data sheet
    Summons_Data_Sheet = Source{[Item="Summons_Data", Kind="Sheet"]}[Data],
    
    // Promote headers
    PromotedHeaders = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    
    // Ensure TITLE column exists (ETL adds it from Assignment Master; if missing, add null)
    WithTitle = if Table.HasColumns(PromotedHeaders, "TITLE") then PromotedHeaders else Table.AddColumn(PromotedHeaders, "TITLE", each null, type text),
    
    // Change YearMonthKey and TYPE; TITLE as text
    ChangedType = Table.TransformColumnTypes(WithTitle, {{"YearMonthKey", Int64.Type}, {"TYPE", type text}, {"TITLE", type text}}),
    
    // Filter to Moving violations only
    FilteredMoving = Table.SelectRows(ChangedType, each ([TYPE] = "M")),
    
    // EXCLUDE PEO: by TITLE = "PEO" (Assignment Master); fallback on display name
    FilteredMovingNoPEO = Table.SelectRows(FilteredMoving, each 
        ( [TITLE] = null or Text.Trim(Text.Upper([TITLE] ?? "")) <> "PEO" ) and
        ( [OFFICER_DISPLAY_NAME] = null or not (Text.StartsWith([OFFICER_DISPLAY_NAME], "PEO ") or Text.StartsWith([OFFICER_DISPLAY_NAME], "PEO,") or Text.StartsWith([OFFICER_DISPLAY_NAME], "PEO.")) )
    ),
    
    // Filter to PREVIOUS COMPLETE MONTH (not "max in file" — so January export shows 01-26)
    FilteredLatestMonth = Table.SelectRows(FilteredMovingNoPEO, each [YearMonthKey] = PreviousMonthKey),
    
    // Group by badge: Count = number of Moving rows per officer for that month (from staging file)
    GroupedRows = Table.Group(
        FilteredLatestMonth, 
        {"PADDED_BADGE_NUMBER", "Month_Year"}, 
        {
            {"Count", each Table.RowCount(_), type number},
            {"Officer", each List.First([OFFICER_DISPLAY_NAME]), type text}
        }
    ),
    
    RemovedBadge = Table.RemoveColumns(GroupedRows, {"PADDED_BADGE_NUMBER"}),
    SortedRows = Table.Sort(RemovedBadge, {{"Count", Order.Descending}}),
    Top5 = Table.FirstN(SortedRows, 5),
    // Ensure Month_Year label matches previous month (e.g. 01-26)
    SetMonthLabel = Table.TransformColumns(Top5, {{"Month_Year", each MonthYearText, type text}})
in
    SetMonthLabel
