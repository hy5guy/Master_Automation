// Query name: OT_FIXED  (use this exact name so main query finds it)
// Paste this entire file into one Power Query (Blank Query). Rename the query to OT_FIXED.
let
    BasePath     = "C:\Users\carucci_r\OneDrive - City of Hackensack",
    OutputFolder = BasePath & "\02_ETL_Scripts\Overtime_TimeOff\output",
    OutFiles     = Folder.Files(OutputFolder),
    FixedFiltered = Table.SelectRows(OutFiles, each Text.Contains([Name], "FIXED_monthly_breakdown") and Text.EndsWith([Name], ".csv")),
    FixedSorted   = Table.Sort(FixedFiltered, {{"Date modified", Order.Descending}}),
    FixedContent  = if Table.RowCount(FixedSorted) > 0 then FixedSorted{0}[Content] else null,
    FixedCsv      = if FixedContent <> null then Csv.Document(FixedContent, [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]) else #table({}, {}),
    FixedHeaders  = Table.PromoteHeaders(FixedCsv, [PromoteAllScalars=true]),
    FixedReordered = Table.ReorderColumns(FixedHeaders, {"Year","Month","Month_Name","Period","Date", "Accrued_Comp_Time","Accrued_Overtime_Paid", "Employee_Sick_Time_Hours","Used_SAT_Time_Hours","Vacation_Hours", "Used_Comp_Time","Military_Leave_Hours","Injured_on_Duty_Hours"}),
    FixedTypes    = Table.TransformColumnTypes(FixedReordered, {{"Year", Int64.Type}, {"Month", Int64.Type}, {"Month_Name", type text}, {"Period", type text}, {"Date", type date}, {"Accrued_Comp_Time", type number}, {"Accrued_Overtime_Paid", type number}, {"Employee_Sick_Time_Hours", type number}, {"Used_SAT_Time_Hours", type number}, {"Vacation_Hours", type number}, {"Used_Comp_Time", type number}, {"Military_Leave_Hours", type number}, {"Injured_on_Duty_Hours", type number}})
in
    FixedTypes
