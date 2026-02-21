// 🕒 2026-02-21-01-00-00 (EST)
// # Master_Automation/m_code/esu/MonthlyActivity.m
// # Author: R. A. Carucci
// # Purpose: Load ESU monthly activity fact from ESU.xlsx; 13-month rolling window; MonthKey and TrackedItem for visuals.

let
    ReportMonth = pReportMonth,

    ESUPath = "C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\ESU\ESU.xlsx",

    Source = Excel.Workbook(
        File.Contents(ESUPath),
        null,
        true
    ),

    // Only monthly tables: _YY_MMM (e.g. _25_JAN); exclude _mom_hacsoc and stray sheets (e.g. R43)
    TablesOnly = Table.SelectRows(
        Source,
        each [Kind] = "Table"
            and Text.StartsWith([Name], "_")
            and [Name] <> "_mom_hacsoc"
            and Text.Length([Name]) >= 6
            and Text.Length([Name]) <= 9
    ),

    AddMonthKey = Table.AddColumn(
        TablesOnly,
        "MonthKey",
        each fnMonthKeyFromTableName([Name]),
        type nullable date
    ),

    RemoveInvalidMonths = Table.SelectRows(AddMonthKey, each [MonthKey] <> null),

    ExpandData = Table.ExpandTableColumn(
        RemoveInvalidMonths,
        "Data",
        {"Tracked Items", "Total"},
        {"Tracked Items", "Total"}
    ),

    AddTrackedItem = Table.AddColumn(
        ExpandData,
        "TrackedItem",
        each fnCleanText([Tracked Items]),
        type text
    ),

    AddTotal = Table.AddColumn(
        AddTrackedItem,
        "TotalNum",
        each try Number.From([Total]) otherwise 0,
        Int64.Type
    ),

    Keep = Table.SelectColumns(
        AddTotal,
        {"MonthKey", "TrackedItem", "TotalNum"}
    ),

    Rename = Table.RenameColumns(
        Keep,
        {{"TotalNum", "Total"}}
    ),

    // 13-month rolling: keep only last 13 complete months (same logic as project 13-month visuals)
    EndMonth = Date.StartOfMonth(Date.AddMonths(ReportMonth, -1)),
    StartMonth = Date.AddMonths(EndMonth, -12),
    Filter13Month = Table.SelectRows(
        Rename,
        each [MonthKey] >= StartMonth and [MonthKey] <= EndMonth
    )
in
    Filter13Month
