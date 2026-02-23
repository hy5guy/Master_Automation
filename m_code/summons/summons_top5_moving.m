// 🕒 2026-02-21-01-00-00 (EST)
// # summons/summons_top5_moving.m
// # Author: R. A. Carucci
// # Purpose: Compute top 5 moving violation officers for the latest month.

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
    
    // Find LATEST month using YearMonthKey (integer sorting, not text!)
    LatestKey = List.Max(FilteredMovingNoPEO[YearMonthKey]),
    
    // Filter to latest month only
    FilteredLatestMonth = Table.SelectRows(FilteredMovingNoPEO, each [YearMonthKey] = LatestKey),
    
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
