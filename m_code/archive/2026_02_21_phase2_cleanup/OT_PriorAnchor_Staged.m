// Query name: OT_Prior  (use this exact name so main query finds it)
// Paste this entire file into one Power Query (Blank Query). Rename the query to OT_Prior.
let
    BasePath        = "C:\Users\carucci_r\OneDrive - City of Hackensack",
    AnalyticsFolder = BasePath & "\02_ETL_Scripts\Overtime_TimeOff\analytics_output",
    AFiles          = Folder.Files(AnalyticsFolder),
    Candidates      = Table.SelectRows(AFiles, each Text.Contains([Name], "Monthly_Accrual_and_Usage_Summary") and Text.EndsWith([Name], ".csv")),
    IsPriorFile     = (content as binary) as logical =>
        let
            Raw  = Csv.Document(content, [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
            T    = Table.PromoteHeaders(Raw, [PromoteAllScalars=true]),
            Cols = List.RemoveItems(Table.ColumnNames(T), {"Time Category"})
        in
            List.Contains(Cols, "08-25") and not List.Contains(Cols, "09-25"),
    WithFlag     = Table.AddColumn(Candidates, "IsPrior", each IsPriorFile([Content]), type logical),
    Filtered    = Table.SelectRows(WithFlag, each [IsPrior] = true),
    PriorSorted = Table.Sort(Filtered, {{"Date modified", Order.Descending}}),
    PriorCont   = if Table.RowCount(PriorSorted) > 0 then PriorSorted{0}[Content] else null,
    PriorCsvRaw = if PriorCont <> null then Csv.Document(PriorCont, [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]) else #table({}, {}),
    PriorCsv    = Table.PromoteHeaders(PriorCsvRaw, [PromoteAllScalars=true]),
    HasTimeCategory = List.Contains(Table.ColumnNames(PriorCsv), "Time Category"),
    PriorAccruals   = if HasTimeCategory then
        let
            Keep = Table.SelectRows(PriorCsv, each [#"Time Category"] = "Accrued Comp. Time" or [#"Time Category"] = "Accrued Overtime"),
            Unp  = Table.UnpivotOtherColumns(Keep, {"Time Category"}, "Period", "Total"),
            Ren  = Table.RenameColumns(Unp, {{"Time Category", "Metric"}}),
            Typ  = Table.TransformColumnTypes(Ren, {{"Total", type number}})
        in Typ
        else #table({"Metric", "Period", "Total"}, {}),
    Trimmed     = Table.TransformColumns(PriorAccruals, {{"Metric", Text.Trim, type text}, {"Period", Text.Trim, type text}}),
    WithLabel   = Table.AddColumn(Trimmed, "PeriodLabel", each let mm = Text.Start([Period], 2), yy = Text.End([Period], 2), y = Number.FromText("20" & yy), m = Number.FromText(mm), d = #date(y, m, 1) in Date.ToText(d, "MM-yy"), type text),
    PriorAccrualsNorm = Table.SelectColumns(WithLabel, {"Metric", "PeriodLabel", "Total"})
in
    PriorAccrualsNorm
