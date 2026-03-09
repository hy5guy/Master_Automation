// 🕒 2026-03-03
// # summons/___Summons.m
// # Author: R. A. Carucci
// # Purpose: Load enhanced summons dataset from ETL output (summons_powerbi_latest.xlsx).
// # TICKET_COUNT: use from source if present (ETL v2.1+); else add 1 per row.

let
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"),
        null, true
    ),
    ATS_Court_Data_Sheet = Source{[Item = "Summons_Data", Kind = "Sheet"]}[Data],
    #"Promoted Headers" = Table.PromoteHeaders(ATS_Court_Data_Sheet, [PromoteAllScalars = true]),

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
        {"DATA_QUALITY_SCORE", type number},
        {"DATA_QUALITY_TIER", type text},
        {"SOURCE_FILE", type text},
        {"PROCESSING_TIMESTAMP", type datetime},
        {"ETL_VERSION", type text}
    },
    ExistingColumns = Table.ColumnNames(#"Promoted Headers"),
    FilteredTypes = List.Select(ColumnTypes, each List.Contains(ExistingColumns, _{0})),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", FilteredTypes),

    // TICKET_COUNT: use from source if present (ETL v2.1+); else add 1 per row
    WithTicketCount = if Table.HasColumns(#"Changed Type", "TICKET_COUNT")
        then Table.TransformColumnTypes(#"Changed Type", {{"TICKET_COUNT", Int64.Type}})
        else Table.AddColumn(#"Changed Type", "TICKET_COUNT", each 1, Int64.Type),

    WithAssignmentFound = if Table.HasColumns(WithTicketCount, "ASSIGNMENT_FOUND")
        then WithTicketCount
        else Table.AddColumn(WithTicketCount, "ASSIGNMENT_FOUND", each true, type logical),

    // Add financial columns when missing (ETL v2.1 may not output them; DAX measures expect them)
    WithTotalPaid = if Table.HasColumns(WithAssignmentFound, "TOTAL_PAID_AMOUNT") then WithAssignmentFound else Table.AddColumn(WithAssignmentFound, "TOTAL_PAID_AMOUNT", each 0, type number),
    WithFineAmount = if Table.HasColumns(WithTotalPaid, "FINE_AMOUNT") then WithTotalPaid else Table.AddColumn(WithTotalPaid, "FINE_AMOUNT", each 0, type number),
    WithCostAmount = if Table.HasColumns(WithFineAmount, "COST_AMOUNT") then WithFineAmount else Table.AddColumn(WithFineAmount, "COST_AMOUNT", each 0, type number),
    WithMiscAmount = if Table.HasColumns(WithCostAmount, "MISC_AMOUNT") then WithCostAmount else Table.AddColumn(WithCostAmount, "MISC_AMOUNT", each 0, type number)
in
    WithMiscAmount
