// POLICY_TRAINING_ANALYTICS / Training_Log_Vertical
// Purpose: Unpivot Delivery_Cost_By_Month so months run DOWN the page (vertical).
// Filters to rolling 13-month window: same month one year earlier through previous month
// (e.g. Feb 2026 → 01-25 through 01-26). Matches project standard (Training Cost by Delivery Method).

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

    // Rolling 13-month window: end = previous month, start = same month one year earlier
    Today = DateTime.LocalNow(),
    CurrentMonth = Date.Month(Today),
    CurrentYear = Date.Year(Today),
    EndMonth = if CurrentMonth = 1 then 12 else CurrentMonth - 1,
    EndYear = if CurrentMonth = 1 then CurrentYear - 1 else CurrentYear,
    StartMonth = EndMonth,
    StartYear = EndYear - 1,
    Report_Start_Date = #date(StartYear, StartMonth, 1),
    Report_End_Date = #date(EndYear, EndMonth, 1),
    MonthList = List.Generate(() => Report_Start_Date, each _ <= Report_End_Date, each Date.AddMonths(_, 1)),
    PeriodLabelsMMYY = List.Transform(MonthList, each Text.PadStart(Text.From(Date.Month(_)), 2, "0") & "-" & Text.End(Text.From(Date.Year(_)), 2)),

    // Unpivot all month columns -> Period, Cost
    MonthCols = List.Difference(Table.ColumnNames(TypedWide),
                                {"Delivery_Type", "Total"}),
    Unpivoted = Table.Unpivot(TypedWide, MonthCols, "Period", "Cost"),

    // Keep only periods in the 13-month window (e.g. 01-25 through 01-26)
    Filtered = Table.SelectRows(Unpivoted, each List.Contains(PeriodLabelsMMYY, [Period])),

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