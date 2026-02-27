// 🕒 2026-02-26-20-00-00 (EST)
// # response_time/___ResponseTime_DispVsCall.m
// # Author: R. A. Carucci
// # Metric: Time Dispatched − Time of Call  (call processing / dispatcher queue time)
// # Source: PowerBI_Date\Backfill\response_time_all_metrics\  (all months 2024–present)

let
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

    // ── Filter to this metric only ─────────────────────────────────────────────
    Filtered = Table.SelectRows(AllData, each [Metric_Type] = "Time Dispatched - Time of Call"),

    // ── Standardize column types ───────────────────────────────────────────────
    Typed = Table.TransformColumnTypes(
        Filtered,
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
            mm = parts{0},
            yy = "20" & parts{1}
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
    WithDate    = Table.AddColumn(WithDateKey, "Date", each [Date_Sort_Key], type date),
    WithAvgRT   = Table.AddColumn(WithDate, "Average_Response_Time", each [Avg_Minutes], type number),
    WithCategory = Table.AddColumn(WithAvgRT, "Category", each [Response_Type], type text),

    RenamedMMSS = Table.RenameColumns(WithCategory, {{"First_Response_Time_MMSS", "Response_Time_MMSS"}}),

    Result = Table.SelectColumns(
        RenamedMMSS,
        {
            "YearMonth", "Date_Sort_Key", "Date",
            "Response_Type", "Category",
            "Average_Response_Time", "Response_Time_MMSS",
            "MM-YY", "Record_Count", "Metric_Type"
        }
    )

in
    Result
