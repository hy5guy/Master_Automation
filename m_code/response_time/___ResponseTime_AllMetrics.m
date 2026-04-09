// 🕒 2026-03-06 (from Claude-Power_BI_response-time_metrics_implementation transcript)
// # response_time/___ResponseTime_AllMetrics.m
// # Author: R. A. Carucci
// # Purpose: Unified response-time query loading all three metric intervals
//            into one long table for consolidated visualization.
//
// Rolling 13-Month Window (driven by pReportMonth):
//   End   = Date.EndOfMonth(pReportMonth)  (include report month)
//   Start = 12 months before pReportMonth  (13 months total, inclusive)
//
// Metric_Label: "Total Response" | "Travel Time" | "Dispatch Queue"
// Metric_Sort: 1=Dispatch Queue, 2=Travel Time, 3=Total Response

let
    EndDate   = Date.EndOfMonth(DateTime.Date(pReportMonth)),
    StartDate = Date.StartOfMonth(Date.AddMonths(DateTime.Date(pReportMonth), -12)),
    EndYM     = Date.Year(EndDate)   * 100 + Date.Month(EndDate),
    StartYM   = Date.Year(StartDate) * 100 + Date.Month(StartDate),

    AllFiles = Folder.Files("C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\response_time_all_metrics"),
    CSVFiles = Table.SelectRows(AllFiles, each Text.EndsWith([Name], "_response_times.csv")),
    WithFullPath = Table.AddColumn(CSVFiles, "FullPath", each [Folder Path] & [Name], type text),

    LoadCSV = (filePath as text) =>
        let
            raw      = Csv.Document(File.Contents(filePath), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
            promoted = Table.PromoteHeaders(raw, [PromoteAllScalars=true])
        in promoted,

    AllData = Table.Combine(List.Transform(WithFullPath[FullPath], LoadCSV)),

    // ── Keep ALL THREE metrics ────────────────────────────────────────────────
    FilteredMetric = Table.SelectRows(AllData, each
        List.Contains(
            {"Time Out - Time of Call", "Time Out - Time Dispatched", "Time Dispatched - Time of Call"},
            [Metric_Type]
        )
    ),

    Windowed = Table.SelectRows(FilteredMetric, each
        let
            parts = Text.Split(Text.Trim([#"MM-YY"]), "-"),
            mm    = Number.FromText(parts{0}),
            yy    = 2000 + Number.FromText(parts{1}),
            ym    = yy * 100 + mm
        in ym >= StartYM and ym <= EndYM
    ),

    Typed = Table.TransformColumnTypes(
        Windowed,
        {
            {"Response_Type",            type text},
            {"MM-YY",                    type text},
            {"Metric_Type",              type text},
            {"First_Response_Time_MMSS", type text},
            {"Avg_Minutes",              type number},
            {"Record_Count",             Int64.Type}
        }
    ),

    WithYearMonth = Table.AddColumn(
        Typed, "YearMonth",
        each let
            parts = Text.Split(Text.Trim([#"MM-YY"]), "-"),
            mm = parts{0}, yy = "20" & parts{1}
        in yy & "-" & Text.PadStart(mm, 2, "0"),
        type text
    ),

    WithDateKey = Table.AddColumn(
        WithYearMonth, "Date_Sort_Key",
        each try Date.FromText([YearMonth] & "-01") otherwise null,
        type date
    ),

    // ── Friendly metric label ─────────────────────────────────────────────────
    WithMetricLabel = Table.AddColumn(
        WithDateKey, "Metric_Label",
        each if [Metric_Type] = "Time Out - Time of Call" then "Total Response"
             else if [Metric_Type] = "Time Out - Time Dispatched" then "Travel Time"
             else if [Metric_Type] = "Time Dispatched - Time of Call" then "Dispatch Queue"
             else [Metric_Type],
        type text
    ),

    // ── Sort order column for metric stacking ─────────────────────────────────
    WithMetricSort = Table.AddColumn(
        WithMetricLabel, "Metric_Sort",
        each if [Metric_Type] = "Time Dispatched - Time of Call" then 1
             else if [Metric_Type] = "Time Out - Time Dispatched" then 2
             else 3,
        Int64.Type
    ),

    WithDate     = Table.AddColumn(WithMetricSort, "Date", each [Date_Sort_Key], type date),
    WithAvgRT    = Table.AddColumn(WithDate, "Average_Response_Time", each [Avg_Minutes], type number),
    WithCategory = Table.AddColumn(WithAvgRT, "Category", each [Response_Type], type text),
    WithSummary  = Table.AddColumn(WithCategory, "Summary_Type", each "Response_Type", type text),

    RenamedMMSS = Table.RenameColumns(WithSummary, {{"First_Response_Time_MMSS", "Response_Time_MMSS"}}),

    WithCount = Table.AddColumn(RenamedMMSS, "Count", each 1, Int64.Type),

    WithMonthName = Table.AddColumn(WithCount, "MonthName", each
        let
            parts = Text.Split([YearMonth], "-"),
            monthNum = if List.Count(parts) >= 2 then Number.From(parts{1}) else 1,
            monthNames = {"January","February","March","April","May","June","July","August","September","October","November","December"},
            name = if monthNum >= 1 and monthNum <= 12 then monthNames{monthNum - 1} & " " & parts{0} else [YearMonth]
        in name,
        type text
    ),

    Result = Table.SelectColumns(
        WithMonthName,
        {
            "YearMonth", "Date_Sort_Key", "Date",
            "Response_Type", "Category", "Summary_Type",
            "Metric_Type", "Metric_Label", "Metric_Sort",
            "Average_Response_Time", "Response_Time_MMSS",
            "MM-YY", "Record_Count", "Count", "MonthName"
        }
    )

in
    Result
