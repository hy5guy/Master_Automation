// ___Summons_Top5_Parking (Standalone)
// Updated: 2026-02-17
// Purpose: Top 5 Parking Violations for LATEST MONTH (loads directly from Excel)

let
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