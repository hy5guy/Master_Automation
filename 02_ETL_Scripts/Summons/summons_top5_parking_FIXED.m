// 🕒 2026-01-11 23:15:00 EST
// Project: SummonsMaster/summons_top5_parking
// Author: R. A. Carucci (updated by Claude Code)
// Purpose: Top 5 parking violations officers for the most recent completed month
// Updated: January 2026 - Formats officer names with non-padded badge numbers

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
    
    // Set data types - only set types for columns we'll use
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"TICKET_COUNT", Int64.Type}, 
        {"IS_AGGREGATE", type logical}, 
        {"PADDED_BADGE_NUMBER", type text}, 
        {"OFFICER_DISPLAY_NAME", type text}, 
        {"OFFICER_NAME_RAW", type text}, 
        {"TYPE", type text}, 
        {"ETL_VERSION", type text}, 
        {"Month_Year", type text}
    }),
    
    // Filter to e-ticket data only (exclude backfill aggregates)
    // Check for null values first to avoid type conversion errors
    #"Filtered E-Ticket Data" = Table.SelectRows(
        #"Changed Type",
        each [ETL_VERSION] <> null and [ETL_VERSION] = "ETICKET_CURRENT" and [IS_AGGREGATE] <> null and [IS_AGGREGATE] = false
    ),
    
    // Get the most recent month dynamically (integer key for correct chronological comparison)
    #"Latest YearMonthKey" = List.Max(#"Filtered E-Ticket Data"[YearMonthKey]),
    
    // Filter to most recent month and parking violations only
    #"Filtered Recent Month Parking" = Table.SelectRows(
        #"Filtered E-Ticket Data",
        each [YearMonthKey] = #"Latest YearMonthKey" and [TYPE] <> null and [TYPE] = "P"
    ),
    
    // Extract non-padded badge number from PADDED_BADGE_NUMBER
    #"Added Non-Padded Badge" = Table.AddColumn(
        #"Filtered Recent Month Parking",
        "BADGE_NUMBER_NON_PADDED",
        each 
            let
                padded = [PADDED_BADGE_NUMBER],
                badgeNum = try Number.From(Text.Select(Text.From(padded), {"0".."9"})) otherwise null,
                badgeText = if badgeNum <> null then Text.From(badgeNum) else ""
            in
                badgeText,
        type text
    ),
    
    // Format officer name: Extract first initial and last name, add non-padded badge
    #"Formatted Officer Name" = Table.AddColumn(
        #"Added Non-Padded Badge",
        "Officer",
        each 
            let
                displayName = [OFFICER_DISPLAY_NAME],
                rawName = [OFFICER_NAME_RAW],
                badgeNonPadded = [BADGE_NUMBER_NON_PADDED],
                
                result = if Text.Contains(displayName, "#") then
                    let
                        namePart = Text.Trim(Text.BeforeDelimiter(displayName, "#")),
                        formatted = namePart & " #" & badgeNonPadded
                    in
                        formatted
                else if Text.Contains(displayName, "(") or Text.Contains(displayName, ",") then
                    let
                        lastName = Text.Trim(Text.BeforeDelimiter(Text.BeforeDelimiter(displayName, "("), ",")),
                        firstInitial = if Text.Contains(rawName, " A ") or Text.Contains(rawName, " A,") then
                            "A"
                        else if Text.Contains(rawName, " ") then
                            let
                                parts = Text.Split(rawName, " "),
                                poIndex = List.PositionOf(parts, "PO"),
                                nextPart = if poIndex >= 0 and poIndex < List.Count(parts) - 1 then parts{poIndex + 1}? else null,
                                letter = if nextPart <> null and Text.Length(Text.Trim(nextPart)) = 1 then Text.Upper(Text.Trim(nextPart)) else null
                            in
                                if letter <> null then letter else "A"
                        else
                            "A",
                        formatted = firstInitial & ". " & Text.Upper(Text.Trim(lastName)) & " #" & badgeNonPadded
                    in
                        formatted
                else
                    displayName & " #" & badgeNonPadded
            in
                result,
        type text
    ),
    
    // Group by Officer and sum TICKET_COUNT
    #"Grouped by Officer" = Table.Group(
        #"Formatted Officer Name",
        {"Officer"},
        {
            {"Sum of Summons Count", each List.Sum([TICKET_COUNT]), type number}
        }
    ),
    
    // Sort by count descending
    #"Sorted Rows" = Table.Sort(#"Grouped by Officer",{{"Sum of Summons Count", Order.Descending}}),
    
    // Take top 5
    #"Top 5" = Table.FirstN(#"Sorted Rows", 5)
in
    #"Top 5"
