// 🕒 2026-02-20-23-48-50
// # remu/___REMU.m
// # Author: R. A. Carucci
// # Purpose: Load REMU monthly activity metrics from contribution workbook.

let
    // 1. Load Excel & table
    WorkbookPath  = "C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\REMU\REMU_Monthly.xlsx",
    TableName     = "_mom_remu",
    Source        = Excel.Workbook(File.Contents(WorkbookPath), null, true),
    REMU_MoM      = Source{[Item=TableName,Kind="Table"]}[Data],

    // 2. Clean "Tracked Items"
    Cleaned       = Table.TransformColumns(
                      REMU_MoM,
                      {{"Tracked Items", each Text.Trim(Text.Clean(_)), type text}}
                    ),
    Filtered      = Table.SelectRows(
                      Cleaned,
                      each [Tracked Items] <> null and [Tracked Items] <> ""
                    ),

    // 3. Unpivot all "MM-YY" columns into [Month] & [Total]
    MonthCols     = List.Select(
                      Table.ColumnNames(Filtered),
                      each Text.Length(_) = 5 and Text.Contains(_,"-")
                    ),
    Unpivoted     = Table.Unpivot(
                      Filtered,
                      MonthCols,
                      "Month",
                      "Total"
                    ),

    // 4. Parse "MM-YY" → first-of-month date
    AddDate       = Table.AddColumn(
                      Unpivoted,
                      "PeriodDate",
                      each Date.FromText("01-" & [Month]),
                      type date
                    ),

    // 5. Convert Total to number
    ChangeType    = Table.TransformColumnTypes(
                      AddDate,
                      {{"Total", Int64.Type}}
                    ),

    // 6. Add MonthIndex (YYYYMM) for chronological sorting
    AddMonthIndex = Table.AddColumn(
                      ChangeType,
                      "MonthIndex",
                      each Date.Year([PeriodDate]) * 100 + Date.Month([PeriodDate]),
                      Int64.Type
                    ),

    // 7. Select only the final five columns
    Final         = Table.SelectColumns(
                      AddMonthIndex,
                      {
                        "Tracked Items",
                        "Month",
                        "PeriodDate",
                        "Total",
                        "MonthIndex"
                      }
                    )
in
    Final
