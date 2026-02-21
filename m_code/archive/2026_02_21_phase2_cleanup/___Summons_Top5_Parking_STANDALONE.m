// 🕒 2026-02-17-14-30-00
// # Master_Automation/m_code/___Summons_Top5_Parking_STANDALONE.m
// # Author: R. A. Carucci
// # Purpose: Top 5 Parking violations for previous complete month; load from summons_powerbi_latest.xlsx.

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
    
    // Group by OFFICER ID (badge number) to consolidate split names, then get display name
    GroupedRows = Table.Group(
        FilteredLatestMonth, 
        {"PADDED_BADGE_NUMBER", "Month_Year"}, 
        {
            {"Count", each Table.RowCount(_), type number},
            {"Officer", each List.First([OFFICER_DISPLAY_NAME]), type text}
        }
    ),
    
    // Remove badge number column (not needed in output)
    RemovedBadge = Table.RemoveColumns(GroupedRows, {"PADDED_BADGE_NUMBER"}),
    
    // Sort by count descending
    SortedRows = Table.Sort(RemovedBadge, {{"Count", Order.Descending}}),
    
    // Keep top 5
    Top5 = Table.FirstN(SortedRows, 5)
in
    Top5
