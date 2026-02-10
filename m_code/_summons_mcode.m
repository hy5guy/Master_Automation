// ___Summons
// 🕒 2025-09-08-15-45-00
// Summons_Analytics/ATS_Court_Data_Enhanced
// Author: R. A. Carucci
// Purpose: Load the enhanced summons dataset processed by ETL script

let
    // Load the enhanced dataset from your ETL output
    Source = Excel.Workbook(
        File.Contents(
            "C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"),
        null, true),

    // Select the Summons_Data sheet
    ATS_Court_Data_Sheet = Source{[Item = "Summons_Data",
                                   Kind = "Sheet"]}[Data],

// Promote headers
#"Promoted Headers" =
    Table.PromoteHeaders(ATS_Court_Data_Sheet, [PromoteAllScalars = true]),

// Helper: Filter column type list to only include columns that exist
ColumnTypes = {
    {"PADDED_BADGE_NUMBER", type text}, 
    {"OFFICER_DISPLAY_NAME", type text}, 
    {"WG1", type text}, {"WG2", type text}, {"WG3", type text}, {"WG4", type text}, {"WG5", type text}, 
    {"TICKET_NUMBER", type text}, 
    {"ISSUE_DATE", type datetime}, 
    {"VIOLATION_NUMBER", type text}, 
    {"VIOLATION_TYPE", type text}, 
    {"TYPE", type text}, 
    {"STATUS", type text}, 
    {"TOTAL_PAID_AMOUNT", type number}, 
    {"FINE_AMOUNT", type number}, 
    {"COST_AMOUNT", type number}, 
    {"MISC_AMOUNT", type number}, 
    {"Year", type number}, 
    {"Month", type number}, 
    {"YearMonthKey", type number}, 
    {"Month_Year", type text}, 
    {"ASSIGNMENT_FOUND", type logical}, 
    {"DATA_QUALITY_SCORE", type number}, 
    {"DATA_QUALITY_TIER", type text}, 
    {"SOURCE_FILE", type text}, 
    {"PROCESSING_TIMESTAMP", type datetime}, 
    {"ETL_VERSION", type text}, 
    {"TICKET_COUNT", Int64.Type}
},
ExistingColumns = Table.ColumnNames(#"Promoted Headers"),
FilteredTypes = List.Select(ColumnTypes, each List.Contains(ExistingColumns, _{0})),

// Set data types based on your enhanced dataset structure (only for existing columns)
#"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", FilteredTypes)

in
#"Changed Type"