// 🕒 2026-02-26-18-30-00 (EST)
// # summons/summons_13month_trend.m
// # Author: R. A. Carucci
// # Purpose: Load summons data from staging workbook for 13-month trend analysis.
// # Schema note: ETL v2.1 output does not include VIOLATION_NUMBER, VIOLATION_DESCRIPTION,
// #   VIOLATION_TYPE, STATUS, LOCATION, SOURCE_FILE, TEAM, WG1/3/4, TOTAL_PAID_AMOUNT,
// #   COST_AMOUNT, MISC_AMOUNT, or PROCESSING_TIMESTAMP. ChangedType is limited to
// #   columns confirmed present in current staging schema.

let
    Source = Excel.Workbook(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"), null, true),
    Summons_Data_Sheet = Source{[Item="Summons_Data",Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders,{
        {"PADDED_BADGE_NUMBER", type text},
        {"OFFICER_DISPLAY_NAME", type text},
        {"OFFICER_NAME_RAW", type text},
        {"ISSUE_DATE", type datetime},
        {"TYPE", type text},
        {"ETL_VERSION", type text},
        {"Year", Int64.Type},
        {"Month", Int64.Type},
        {"YearMonthKey", Int64.Type},
        {"Month_Year", type text},
        {"WG2", type text},
        {"DATA_QUALITY_SCORE", Int64.Type}
    }),
    FilteredClean = Table.SelectRows(ChangedType, each [WG2] <> null and [WG2] <> "" and [WG2] <> "UNKNOWN"),
    AddConsolidatedBureau = Table.AddColumn(FilteredClean, "Bureau_Consolidated", each if [WG2] = "HOUSING" or [WG2] = "OFFICE OF SPECIAL OPERATIONS" or [WG2] = "PATROL BUREAU" then "PATROL DIVISION" else [WG2], type text)
in
    AddConsolidatedBureau
