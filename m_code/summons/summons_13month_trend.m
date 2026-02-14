// summons_13month_trend
// 🕒 2026-01-11 01:28:55 EST
// Project: SummonsMaster/summons_13month_trend
// Author: R. A. Carucci (updated by Claude Code)
// Purpose: Loads all summons data (historical backfill + current month) with all columns for 13-month trend and all bureaus visual
// Updated: January 2026 - Includes all columns from preview table, combines backfill and current month data
// Replaces: ___Summons (was ___Backfill for aggregated version)

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
    
    // Set data types based on your enhanced dataset structure
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
    
    // Filter for 13-Month Data Window
    // Include both historical backfill records (IS_AGGREGATE = true or ETL_VERSION = "HISTORICAL_SUMMARY")
    // and current month individual records (ETICKET_CURRENT)
    #"Filtered 13 Month Data" = Table.SelectRows(
        #"Changed Type",
        each ([IS_AGGREGATE] = true or [ETL_VERSION] = "HISTORICAL_SUMMARY" or [ETL_VERSION] = "ETICKET_CURRENT")
    ),
    
    // Filter out UNKNOWN WG2 records to match All Bureaus visual totals
    // Historical backfill records (IS_AGGREGATE = true) don't have WG2, so keep them
    // Only filter UNKNOWN from current month e-ticket records
    #"Filtered UNKNOWN" = Table.SelectRows(
        #"Filtered 13 Month Data",
        each [IS_AGGREGATE] = true or [ETL_VERSION] = "HISTORICAL_SUMMARY" or ([ETL_VERSION] = "ETICKET_CURRENT" and [WG2] <> null and [WG2] <> "" and [WG2] <> "UNKNOWN")
    )
in
    #"Filtered UNKNOWN"
