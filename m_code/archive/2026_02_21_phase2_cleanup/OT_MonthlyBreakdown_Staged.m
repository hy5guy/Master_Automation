// Query name: OT_MB  (use this exact name so main query finds it)
// Paste this entire file into one Power Query (Blank Query). Rename the query to OT_MB.
let
    BasePath        = "C:\Users\carucci_r\OneDrive - City of Hackensack",
    AnalyticsFolder = BasePath & "\02_ETL_Scripts\Overtime_TimeOff\analytics_output",
    AFiles          = Folder.Files(AnalyticsFolder),
    MBFile          = Table.SelectRows(AFiles, each [Name] = "monthly_breakdown.csv"),
    MBCont          = if Table.RowCount(MBFile) > 0 then MBFile{0}[Content] else null,
    MBCsv           = if MBCont <> null then Csv.Document(MBCont, [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]) else #table({}, {}),
    MBHeaders       = Table.PromoteHeaders(MBCsv, [PromoteAllScalars=true]),
    MBTypes         = Table.TransformColumnTypes(MBHeaders, {{"YearMonth", type text}, {"Class", type text}, {"Metric", type text}, {"Hours", type number}})
in
    MBTypes
