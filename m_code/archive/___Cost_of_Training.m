// 🕒 2026-01-12-20-03-48
// POLICY_TRAINING_ANALYTICS / Training_Log_Vertical
// Purpose: Unpivot Delivery_Cost_By_Month so months run DOWN the page
// (vertical) Filters to rolling 13-month window (excludes current month)
// NOTE: Do NOT auto-format this file - file paths will break

let Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of "
                      "Hackensack\02_ETL_Scripts\Policy_Training_"
                      "Monthly\output\policy_training_outputs.xlsx"),
        null, true),
    Tbl = Source{[Item = "Delivery_Cost_By_Month", Kind = "Sheet"]}[Data],
    Promoted = Table.PromoteHeaders(Tbl, [PromoteAllScalars = true]),

    // Strong types for wide table
    TypedWide =
        if Table.HasColumns(Promoted, {"Delivery_Type", "Total"})
            then Table.TransformColumnTypes(
                Promoted,
                List.Combine(
                    {{{"Delivery_Type", type text}, {"Total", type number}},
                     List.Transform(
                         List.RemoveItems(Table.ColumnNames(Promoted),
                                          {"Delivery_Type", "Total"}),
                         each{_, type number})})) else Promoted,

    // Calculate rolling 13-month window (exclude current month)
    // End Date = last complete month before today
    // Start Date = 12 months before End Date (inclusive, gives 13 months total)
    // Example: If today is Jan 12, 2026:
    //   - EndDate = Dec 2025 (12-25)
    //   - StartDate = Dec 2024 (12-24)
    //   - Window: 12-24 through 12-25 (13 months)
    NowDT = DateTime.LocalNow(), CurrY = Date.Year(NowDT),
    CurrM = Date.Month(NowDT), EndY = if CurrM = 1 then CurrY - 1 else CurrY,
    EndM = if CurrM = 1 then 12 else CurrM - 1,

    // Calculate end date first, then subtract 12 months to get start
    EndDate = #date(EndY, EndM, 1), StartDate = Date.AddMonths(EndDate, -12),

    // Generate 13 months: from StartDate (inclusive) through EndDate
    // (inclusive) Note: List.Generate includes both start and end dates when
    // condition is <=
    MonthList = List.Generate(() = > StartDate, each _ <= EndDate,
                              each Date.AddMonths(_, 1)),

    // Convert dates to MM-YY format (e.g., "12-25" for December 2025)
    PeriodLabelsMMYY = List.Transform(
        MonthList, each Text.PadStart(Text.From(Date.Month(_)), 2, "0") & "-" &
                       Text.End(Text.From(Date.Year(_)), 2)),

    // Unpivot all month columns -> Period, Cost
    MonthCols = List.Difference(Table.ColumnNames(TypedWide),
                                {"Delivery_Type", "Total"}),
    Unpivoted = Table.Unpivot(TypedWide, MonthCols, "Period", "Cost"),

    // Filter to only periods in the 13-month window
    // Note: This ensures we only show the rolling 13-month window (excludes
    // current month)
    Filtered = Table.SelectRows(Unpivoted,
                                each List.Contains(PeriodLabelsMMYY, [Period])),

    // Add sort key so Period (MM-YY) sorts chronologically
    WithSort = Table.AddColumn(
        Filtered, "Period_Sort",
        each let mm = Number.FromText(Text.Start([Period], 2)),
        yy = Number.FromText(Text.End([Period], 2)),
        yyyy = if yy < 70 then 2000 + yy else 1900 + yy in yyyy * 100 + mm,
        Int64.Type),

    // Final types
    Final = Table.TransformColumnTypes(WithSort, {{"Delivery_Type", type text},
                                                  {"Period", type text},
                                                  {"Cost", type number},
                                                  {"Period_Sort", Int64.Type}})
                in Final