// summons_all_bureaus
// 🕒 2026-01-11 20:42:30 EST
// Project: SummonsMaster/summons_all_bureaus
// Author: R. A. Carucci (updated by Claude Code)
// Purpose: Load summons data grouped by bureau (WG2) for the most recent month
// Updated: January 2026 - Creates bureau-level summary for All Bureaus visual
// Updated: January 2026 - OFFICE OF SPECIAL OPERATIONS now combines with Patrol Division, displays as "ESU"

let
    // Load the main summons output file
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"),
        null,
        true
    ),
    
    // Get the Summons_Data sheet
    Summons_Data_Sheet = Source{[Item="Summons_Data",Kind="Sheet"]}[Data],
    
    // Promote headers
    #"Promoted Headers" = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    
    // Set data types
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"TICKET_NUMBER", type text}, 
        {"TICKET_COUNT", Int64.Type}, 
        {"IS_AGGREGATE", type logical}, 
        {"PADDED_BADGE_NUMBER", type text}, 
        {"OFFICER_DISPLAY_NAME", type text}, 
        {"OFFICER_NAME_RAW", type text}, 
        {"ISSUE_DATE", type datetime}, 
        {"VIOLATION_NUMBER", type text}, 
        {"VIOLATION_DESCRIPTION", type text}, 
        {"VIOLATION_TYPE", type text}, 
        {"TYPE", type text}, 
        {"STATUS", type text}, 
        {"LOCATION", type text}, 
        {"WARNING_FLAG", type text}, 
        {"SOURCE_FILE", type text}, 
        {"ETL_VERSION", type text}, 
        {"Year", Int64.Type}, 
        {"Month", Int64.Type}, 
        {"YearMonthKey", Int64.Type}, 
        {"Month_Year", type text}, 
        {"TEAM", type text}, 
        {"WG1", type text}, 
        {"WG2", type text}, 
        {"WG3", type text}, 
        {"WG4", type text}, 
        {"WG5", type text}, 
        {"POSS_CONTRACT_TYPE", type text}, 
        {"ASSIGNMENT_FOUND", type logical}, 
        {"DATA_QUALITY_SCORE", type number}, 
        {"DATA_QUALITY_TIER", type text}, 
        {"TOTAL_PAID_AMOUNT", type number}, 
        {"FINE_AMOUNT", type number}, 
        {"COST_AMOUNT", type number}, 
        {"MISC_AMOUNT", type number}, 
        {"PROCESSING_TIMESTAMP", type datetime}
    }),
    
    // Get the most recent month from e-ticket data (use YearMonthKey for chronological order)
    #"Filtered E-Ticket Data" = Table.SelectRows(
        #"Changed Type",
        each [ETL_VERSION] = "ETICKET_CURRENT" and [IS_AGGREGATE] = false
    ),
    
    #"YearMonthKeyList" = List.RemoveNulls(#"Filtered E-Ticket Data"[YearMonthKey]),
    #"Latest YearMonthKey" = if List.IsEmpty(#"YearMonthKeyList") then 0 else List.Max(#"YearMonthKeyList"),
    #"Latest Month Row" = Table.FirstN(Table.SelectRows(#"Filtered E-Ticket Data", each [YearMonthKey] = #"Latest YearMonthKey"), 1),
    #"Latest Month Raw" = if Table.RowCount(#"Latest Month Row") > 0 then Table.Column(#"Latest Month Row", "Month_Year"){0} else "",
    // Display: "01-26" -> "January 2026" for subtitle
    #"Latest Month" = if Text.Length(#"Latest Month Raw") = 5 and Text.Contains(#"Latest Month Raw", "-") then
        let parts = Text.Split(#"Latest Month Raw", "-"), m = Number.From(parts{0}), y = 2000 + Number.From(parts{1}),
            monthNames = {"January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"}
        in monthNames{m-1} & " " & Text.From(y)
    else #"Latest Month Raw",
    
    // Filter to most recent month - e-ticket data only
    #"Filtered Recent Month" = Table.SelectRows(
        #"Filtered E-Ticket Data",
        each [YearMonthKey] = #"Latest YearMonthKey"
    ),
    
    // Filter out records with blank/null WG2 (bureau) and UNKNOWN values
    #"Filtered Blank WG2" = Table.SelectRows(
        #"Filtered Recent Month",
        each [WG2] <> null and [WG2] <> "" and [WG2] <> "UNKNOWN"
    ),
    
    // Replace OFFICE OF SPECIAL OPERATIONS with PATROL BUREAU (so it combines with Patrol Division)
    // Note: After ETL runs with updated Assignment_Master_V2.csv, this should be rare/historical
    #"Replaced OFFICE OF SPECIAL OPERATIONS" = Table.ReplaceValue(
        #"Filtered Blank WG2",
        "OFFICE OF SPECIAL OPERATIONS",
        "PATROL BUREAU",
        Replacer.ReplaceText,
        {"WG2"}
    ),
    
    // Replace PATROL BUREAU with PATROL DIVISION to combine them
    #"Replaced PATROL BUREAU" = Table.ReplaceValue(
        #"Replaced OFFICE OF SPECIAL OPERATIONS",
        "PATROL BUREAU",
        "PATROL DIVISION",
        Replacer.ReplaceText,
        {"WG2"}
    ),
    
    // Group by WG2 (Bureau) and TYPE; sum TICKET_COUNT for Moving (TYPE=M) and Parking (TYPE=P)
    // Use column names "Moving" and "Parking" (not "M"/"P") to avoid Power BI "Fields that need to be fixed" / reserved M
    #"Grouped by Bureau and Type" = Table.Group(
        #"Replaced PATROL BUREAU",
        {"WG2"},
        {
            {"Moving", each List.Sum(List.RemoveNulls(Table.SelectRows(_, each [TYPE] = "M")[TICKET_COUNT])), Int64.Type},
            {"Parking", each List.Sum(List.RemoveNulls(Table.SelectRows(_, each [TYPE] = "P")[TICKET_COUNT])), Int64.Type}
        }
    ),
    
    // Replace null with 0 so visuals show 0 instead of blank
    #"Replaced Value Moving" = Table.ReplaceValue(#"Grouped by Bureau and Type", null, 0, Replacer.ReplaceValue, {"Moving"}),
    #"Replaced Value Parking" = Table.ReplaceValue(#"Replaced Value Moving", null, 0, Replacer.ReplaceValue, {"Parking"}),
    
    // Rename WG2 to Bureau/Division for clarity
    #"Renamed Columns" = Table.RenameColumns(#"Replaced Value Parking", {{"WG2", "Bureau/Division"}}),
    
    // Sort by Bureau/Division name
    #"Sorted Rows" = Table.Sort(#"Renamed Columns", {{"Bureau/Division", Order.Ascending}}),
    
    // Add Month_Year column for subtitle
    #"Added Month" = Table.AddColumn(#"Sorted Rows", "Month_Year", each #"Latest Month", type text)
in
    #"Added Month"
