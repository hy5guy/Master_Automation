// summons_top5_moving
// 🕒 2026-01-11 23:30:00 EST
// Project: SummonsMaster/summons_top5_moving
// Author: R. A. Carucci (updated by Claude Code)
// Purpose: Top 5 moving violations officers for the most recent completed month
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
    
    // Set data types (YearMonthKey = 202601 for Jan 2026; use for chronological "latest month")
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"TICKET_COUNT", Int64.Type}, 
        {"IS_AGGREGATE", type logical}, 
        {"PADDED_BADGE_NUMBER", type text}, 
        {"OFFICER_DISPLAY_NAME", type text}, 
        {"OFFICER_NAME_RAW", type text}, 
        {"TYPE", type text}, 
        {"ETL_VERSION", type text}, 
        {"YearMonthKey", Int64.Type},
        {"Month_Year", type text}
    }),
    
    // Filter to e-ticket data only (exclude backfill aggregates)
    #"Filtered E-Ticket Data" = Table.SelectRows(
        #"Changed Type",
        each [ETL_VERSION] <> null and [ETL_VERSION] = "ETICKET_CURRENT" and [IS_AGGREGATE] <> null and [IS_AGGREGATE] = false
    ),
    
    // Exclude "MULTIPLE OFFICERS" records
    #"Exclude Multiple Officers" = Table.SelectRows(
        #"Filtered E-Ticket Data",
        each [OFFICER_DISPLAY_NAME] <> null and [OFFICER_DISPLAY_NAME] <> "MULTIPLE OFFICERS (Historical)"
    ),
    
    // Latest month by chronological order (YearMonthKey), not text - avoids "12-25" > "01-26" lexicographic error
    #"YearMonthKeyList" = List.RemoveNulls(#"Exclude Multiple Officers"[YearMonthKey]),
    #"Latest YearMonthKey" = if List.IsEmpty(#"YearMonthKeyList") then 0 else List.Max(#"YearMonthKeyList"),
    #"Latest Month Row" = Table.FirstN(Table.SelectRows(#"Exclude Multiple Officers", each [YearMonthKey] = #"Latest YearMonthKey"), 1),
    #"Latest Month Raw" = if Table.RowCount(#"Latest Month Row") > 0 then Table.Column(#"Latest Month Row", "Month_Year"){0} else "",
    // Display: "01-26" -> "January 2026" for subtitle
    #"Latest Month" = if Text.Length(#"Latest Month Raw") = 5 and Text.Contains(#"Latest Month Raw", "-") then
        let parts = Text.Split(#"Latest Month Raw", "-"), m = Number.From(parts{0}), y = 2000 + Number.From(parts{1}),
            monthNames = {"January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"}
        in monthNames{m-1} & " " & Text.From(y)
    else #"Latest Month Raw",
    
    // Filter to most recent month and moving violations only
    #"Filtered Recent Month Moving" = Table.SelectRows(
        #"Exclude Multiple Officers",
        each [YearMonthKey] = #"Latest YearMonthKey" and [TYPE] <> null and [TYPE] = "M"
    ),
    
    // Extract non-padded badge number from PADDED_BADGE_NUMBER
    #"Added Non-Padded Badge" = Table.AddColumn(
        #"Filtered Recent Month Moving",
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
                else if displayName <> "" and (Text.Contains(displayName, "(") or Text.Contains(displayName, ",")) then
                    let
                        lastName = Text.Trim(Text.BeforeDelimiter(Text.BeforeDelimiter(displayName, "("), ",")),
                        firstInitial = if rawName <> "" and (Text.Contains(rawName, " A ") or Text.Contains(rawName, " A,")) then
                            "A"
                        else if rawName <> "" and Text.Contains(rawName, " ") then
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
