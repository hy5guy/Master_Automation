// 🕒 2026-02-20-23-48-50
// # summons/summons_13month_trend.m
// # Author: R. A. Carucci
// # Purpose: Load summons data from staging workbook for 13-month trend analysis.

let
    Source = Excel.Workbook(File.Contents("C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"), null, true),
    Summons_Data_Sheet = Source{[Item="Summons_Data",Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders,{
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
        {"POSS_CONTRACT_TYPE", type text}, 
        {"ASSIGNMENT_FOUND", type logical}, 
        {"DATA_QUALITY_SCORE", Int64.Type}, 
        {"TOTAL_PAID_AMOUNT", type text}, 
        {"COST_AMOUNT", Int64.Type}, 
        {"MISC_AMOUNT", Int64.Type}, 
        {"PROCESSING_TIMESTAMP", type datetime}
    }),
    FilteredClean = Table.SelectRows(ChangedType, each [WG2] <> "UNKNOWN"),
    AddConsolidatedBureau = Table.AddColumn(FilteredClean, "Bureau_Consolidated", each if [WG2] = "HOUSING" or [WG2] = "OFFICE OF SPECIAL OPERATIONS" then "PATROL DIVISION" else [WG2], type text)
in
    AddConsolidatedBureau
