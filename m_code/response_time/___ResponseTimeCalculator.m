// 🕒 2026-02-26-21-00-00 (EST)
// # response_time/___ResponseTimeCalculator.m
// # Author: R. A. Carucci
// # Metric: Time Out − Time Dispatched
// # Source: PowerBI_Date\Backfill\response_time_all_metrics\
//
// Rolling 13-Month Window (driven by pReportMonth):
//   pReportMonth = #date(YYYY, M, 1)  — first day of the report's month
//   End   = month BEFORE pReportMonth  (last complete month)
//   Start = 12 months before End       (13 months total, inclusive)
//   Example: pReportMonth = #date(2026,2,1) → window = Jan-25 through Jan-26
//
// Using pReportMonth (not TODAY()) ensures historical monthly report files
// always display the correct 13-month window for their report period.

let
    // ── Rolling 13-month window boundaries ────────────────────────────────────
    EndDate   = Date.AddMonths(DateTime.Date(pReportMonth), -1),  // last complete month
    StartDate = Date.AddMonths(EndDate, -12),                      // 13 months total
    EndYM     = Date.Year(EndDate)   * 100 + Date.Month(EndDate),
    StartYM   = Date.Year(StartDate) * 100 + Date.Month(StartDate),

    // ── Load all monthly CSVs from the unified backfill folder ─────────────────
    AllFiles = Folder.Files("C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\response_time_all_metrics"),
    CSVFiles = Table.SelectRows(AllFiles, each Text.EndsWith([Name], "_response_times.csv")),
    WithFullPath = Table.AddColumn(CSVFiles, "FullPath", each [Folder Path] & [Name], type text),

    LoadCSV = (filePath as text) =>
        let
            raw      = Csv.Document(File.Contents(filePath), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
            promoted = Table.PromoteHeaders(raw, [PromoteAllScalars=true])
        in promoted,

    AllData = Table.Combine(List.Transform(WithFullPath[FullPath], LoadCSV)),

    // ── Filter to this metric and the rolling 13-month window ─────────────────
    FilteredMetric = Table.SelectRows(AllData, each [Metric_Type] = "Time Out - Time Dispatched"),
    Windowed = Table.SelectRows(FilteredMetric, each
        let
            parts = Text.Split(Text.Trim([#"MM-YY"]), "-"),
            mm    = Number.FromText(parts{0}),
            yy    = 2000 + Number.FromText(parts{1}),
            ym    = yy * 100 + mm
        in ym >= StartYM and ym <= EndYM
    ),

    // ── Standardize column types ───────────────────────────────────────────────
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

    // ── Build sort key from MM-YY ("01-25" → Date 2025-01-01) ─────────────────
    WithYearMonth = Table.AddColumn(
        Typed,
        "YearMonth",
        each let
            parts = Text.Split(Text.Trim([#"MM-YY"]), "-"),
            mm = parts{0}, yy = "20" & parts{1}
        in yy & "-" & Text.PadStart(mm, 2, "0"),
        type text
    ),

    WithDateKey = Table.AddColumn(
        WithYearMonth,
        "Date_Sort_Key",
        each try Date.FromText([YearMonth] & "-01") otherwise null,
        type date
    ),

    // ── Alias / compatibility columns for DAX measures ─────────────────────────
    WithDate     = Table.AddColumn(WithDateKey,  "Date",                  each [Date_Sort_Key], type date),
    WithAvgRT    = Table.AddColumn(WithDate,     "Average_Response_Time", each [Avg_Minutes],   type number),
    WithCategory = Table.AddColumn(WithAvgRT,    "Category",              each [Response_Type], type text),
    WithSummary  = Table.AddColumn(WithCategory, "Summary_Type",          each "Response_Type", type text),

    RenamedMMSS = Table.RenameColumns(WithSummary, {{"First_Response_Time_MMSS", "Response_Time_MMSS"}}),

    // ── Count and MonthName for line chart / template compatibility ─────────────
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
            "Average_Response_Time", "Response_Time_MMSS",
            "MM-YY", "Record_Count", "Metric_Type",
            "Count", "MonthName"
        }
    )

in
    Result
