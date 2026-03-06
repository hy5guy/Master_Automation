# Prompt for Claude — Create ___ResponseTime_AllMetrics in Power BI

**Status:** ✅ Implemented in live PBI model 2026-03-06. Use below for new reports or template deployment.

**Copy everything below the line and paste into Claude (with Power BI Desktop open and MCP connected).**

---

Create a new Power Query in my open Power BI model named `___ResponseTime_AllMetrics`. Use this M code:

```m
let
    EndDate   = Date.AddMonths(DateTime.Date(pReportMonth), -1),
    StartDate = Date.AddMonths(EndDate, -12),
    EndYM     = Date.Year(EndDate)   * 100 + Date.Month(EndDate),
    StartYM   = Date.Year(StartDate) * 100 + Date.Month(StartDate),

    AllFiles = Folder.Files("C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\response_time_all_metrics"),
    CSVFiles = Table.SelectRows(AllFiles, each Text.EndsWith([Name], "_response_times.csv")),
    WithFullPath = Table.AddColumn(CSVFiles, "FullPath", each [Folder Path] & [Name], type text),

    LoadCSV = (filePath as text) =>
        let
            raw      = Csv.Document(File.Contents(filePath), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
            promoted = Table.PromoteHeaders(raw, [PromoteAllScalars=true])
        in promoted,

    AllData = Table.Combine(List.Transform(WithFullPath[FullPath], LoadCSV)),

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

    WithMetricLabel = Table.AddColumn(
        WithDateKey, "Metric_Label",
        each if [Metric_Type] = "Time Out - Time of Call" then "Total Response"
             else if [Metric_Type] = "Time Out - Time Dispatched" then "Travel Time"
             else if [Metric_Type] = "Time Dispatched - Time of Call" then "Dispatch Queue"
             else [Metric_Type],
        type text
    ),

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
```

**Requirements:**
- Ensure `pReportMonth` parameter exists (e.g. `#date(2026, 2, 1)`).
- After creation, validate row count: should equal the sum of rows from the three existing RT tables.
- I will disable load on the three old queries (`___ResponseTimeCalculator`, `___ResponseTime_OutVsCall`, `___ResponseTime_DispVsCall`) once validated.
