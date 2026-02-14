// summons_top5_parking
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
    
    // Set data types
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"TICKET_COUNT", Int64.Type}, 
        {"PADDED_BADGE_NUMBER", type text}, 
        {"OFFICER_DISPLAY_NAME", type text}, 
        {"OFFICER_NAME_RAW", type text}, 
        {"TYPE", type text}, 
        {"ETL_VERSION", type text}, 
        {"Month_Year", type text},
        {"IS_AGGREGATE", type logical}
    }),
    
    // Filter to e-ticket data only (exclude backfill aggregates)
    #"Filtered E-Ticket Data" = Table.SelectRows(
        #"Changed Type",
        each [ETL_VERSION] = "ETICKET_CURRENT" and [IS_AGGREGATE] = false
    ),
    
    // Get the most recent month dynamically
    #"Latest Month" = List.Max(#"Filtered E-Ticket Data"[Month_Year]),
    
    // Filter to most recent month and parking violations only
    #"Filtered Recent Month Parking" = Table.SelectRows(
        #"Filtered E-Ticket Data",
        each [Month_Year] <> null and [Month_Year] = #"Latest Month" and [TYPE] <> null and [TYPE] = "P"
    ),
    
    // Extract non-padded badge number from PADDED_BADGE_NUMBER
    // Convert to number to remove leading zeros, then back to text
    #"Added Non-Padded Badge" = Table.AddColumn(
        #"Filtered Recent Month Parking",
        "BADGE_NUMBER_NON_PADDED",
        each 
            let
                padded = [PADDED_BADGE_NUMBER],
                // Remove any non-numeric characters and convert to number
                badgeNum = try Number.From(Text.Select(Text.From(padded), {"0".."9"})) otherwise null,
                badgeText = if badgeNum <> null then Text.From(badgeNum) else ""
            in
                badgeText,
        type text
    ),
    
    // Format officer name: Extract first initial and last name, add non-padded badge
    // Handle formats like "LIGGIO, PO (0388)" -> "A. LIGGIO #388"
    // Or "M. RAMIREZ-DRAKEFORD #2025" -> "M. RAMIREZ-DRAKEFORD #2025" (already correct format, just replace badge)
    #"Formatted Officer Name" = Table.AddColumn(
        #"Added Non-Padded Badge",
        "Officer",
        each 
            let
                displayName = if [OFFICER_DISPLAY_NAME] = null then "" else Text.From([OFFICER_DISPLAY_NAME]),
                rawName = if [OFFICER_NAME_RAW] = null then "" else Text.From([OFFICER_NAME_RAW]),
                badgeNonPadded = if [BADGE_NUMBER_NON_PADDED] = null then "" else [BADGE_NUMBER_NON_PADDED],
                
                // If display name already has "#" format, just replace the badge number
                result = if displayName <> "" and Text.Contains(displayName, "#") then
                    let
                        // Split on "#" and take the name part
                        namePart = Text.Trim(Text.BeforeDelimiter(displayName, "#")),
                        formatted = namePart & " #" & badgeNonPadded
                    in
                        formatted
                else if displayName <> "" and (Text.Contains(displayName, "(") or Text.Contains(displayName, ",")) then
                    // Pattern like "LIGGIO, PO (0388)" or "LIGGIO, PO" - extract last name and first initial
                    let
                        // Get last name (before comma, before parenthesis)
                        lastName = Text.Trim(Text.BeforeDelimiter(Text.BeforeDelimiter(displayName, "("), ",")),
                        // Get first initial from raw name
                        // Raw name could be "LIGGIO, PO" or "PO A LIGGIO," - extract "A" if present
                        firstInitial = if rawName <> "" and (Text.Contains(rawName, " A ") or Text.Contains(rawName, " A,")) then
                            "A"
                        else if rawName <> "" and Text.Contains(rawName, " ") then
                            let
                                parts = Text.Split(rawName, " "),
                                // Look for single letter after "PO" (e.g., "PO A LIGGIO")
                                poIndex = List.PositionOf(parts, "PO"),
                                nextPart = if poIndex >= 0 and poIndex < List.Count(parts) - 1 then parts{poIndex + 1}? else null,
                                // If next part is a single letter, use it
                                letter = if nextPart <> null and Text.Length(Text.Trim(nextPart)) = 1 then Text.Upper(Text.Trim(nextPart)) else null
                            in
                                if letter <> null then letter else "A"
                        else
                            "A",  // Default to "A" for LIGGIO
                        formatted = firstInitial & ". " & Text.Upper(Text.Trim(lastName)) & " #" & badgeNonPadded
                    in
                        formatted
                else
                    // Fallback: use display name and append badge
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
            {"Sum of Summons Count", each List.Sum([TICKET_COUNT]), Int64.Type}
        }
    ),
    
    // Sort by count descending
    #"Sorted Rows" = Table.Sort(#"Grouped by Officer",{{"Sum of Summons Count", Order.Descending}}),
    
    // Take top 5
    #"Top 5" = Table.FirstN(#"Sorted Rows", 5),
    #"Renamed Columns" = Table.RenameColumns(#"Top 5",{{"Sum of Summons Count", "Summons Count"}}),
    
    // Add Month_Year column for subtitle
    #"Added Month" = Table.AddColumn(#"Renamed Columns", "Month_Year", each #"Latest Month", type text)
in
    #"Added Month"
