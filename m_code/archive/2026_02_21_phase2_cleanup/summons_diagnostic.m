// 🕒 2026-02-17-14-30-00
// # Master_Automation/m_code/summons/summons_diagnostic.m
// # Author: R. A. Carucci
// # Purpose: Diagnostic query to inspect summons data structure.

let
    Source = Excel.Workbook(
        File.Contents(
            "C:/Users/carucci_r/OneDrive - City of Hackensack/03_Staging/Summons/summons_powerbi_latest.xlsx"
        ),
        null,
        true
    ),
    ATS_Court_Data_Sheet = Source{[Item = "Summons_Data", Kind = "Sheet"]}[Data],
    #"Promoted Headers" = 
        Table.PromoteHeaders(ATS_Court_Data_Sheet, [PromoteAllScalars = true]),
    
    // Get column names
    ColumnNames = Table.ColumnNames(#"Promoted Headers"),
    
    // Most recent month
    MaxYearMonthKey = List.Max(#"Promoted Headers"[YearMonthKey]),
    Recent = Table.SelectRows(#"Promoted Headers", each [YearMonthKey] = MaxYearMonthKey),
    
    // Show distinct TYPE values
    DistinctTypes = Table.Distinct(Table.SelectColumns(Recent, {"TYPE"})),
    
    // Show distinct WG2 values
    DistinctWG2 = Table.Distinct(Table.SelectColumns(Recent, {"WG2"})),
    
    // Count by TYPE
    TypeCounts = Table.Group(
        Recent,
        {"TYPE"},
        {{"Count", each Table.RowCount(_), Int64.Type}}
    ),
    
    // Sample of recent data
    Sample = Table.FirstN(Recent, 10)
in
    Sample
