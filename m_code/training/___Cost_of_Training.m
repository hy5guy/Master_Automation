/* 🕒 2026-02-21-01-00-00 (EST) — updated 2026-04-09 (window aligned to project standard) */
/* training/___Cost_of_Training.m */
/* Author: R. A. Carucci */
/* Purpose: Calculate training cost by delivery method with rolling 13-month window. */

let
    ReportMonth = pReportMonth,
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Policy_Training_Monthly\output\policy_training_outputs.xlsx"),
        null, true),
    Tbl = Source{[Item = "Delivery_Cost_By_Month", Kind = "Sheet"]}[Data],
    Promoted = Table.PromoteHeaders(Tbl, [PromoteAllScalars = true]),

    /* Strong types for wide table */
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

    /* Rolling 13-month window (project standard): end = pReportMonth, start = 12 months prior */
    /* Convention: Date.EndOfMonth(pReportMonth) — report month is last month in window */
    Today = DateTime.From(ReportMonth),
    CurrentYear = Date.Year(Today),
    CurrentMonth = Date.Month(Today),
    Report_End_Date = Date.StartOfMonth(Today),
    Report_Start_Date = Date.AddMonths(Report_End_Date, -12),
    MonthList = List.Generate(
        () => Report_Start_Date,
        each _ <= Report_End_Date,
        each Date.AddMonths(_, 1)
    ),
    PeriodLabelsMMYY = List.Transform(
        MonthList,
        each Text.PadStart(Text.From(Date.Month(_)), 2, "0")
             & "-" & Text.End(Text.From(Date.Year(_)), 2)
    ),

    /* Calendar YTD through report month (fixes January reports and YTD cost cards) */
    YTDStart = #date(CurrentYear, 1, 1),
    YTDEnd = Date.StartOfMonth(Today),
    YTDMonthList = List.Generate(
        () => YTDStart,
        each _ <= YTDEnd,
        each Date.AddMonths(_, 1)
    ),
    YTDLabels = List.Transform(
        YTDMonthList,
        each Text.PadStart(Text.From(Date.Month(_)), 2, "0")
             & "-" & Text.End(Text.From(Date.Year(_)), 2)
    ),
    AllPeriodLabels = List.Distinct(List.Combine({PeriodLabelsMMYY, YTDLabels})),

    /* Unpivot all month columns -> Period, Cost */
    MonthCols = List.Difference(Table.ColumnNames(TypedWide),
                                {"Delivery_Type", "Total"}),
    Unpivoted = Table.Unpivot(TypedWide, MonthCols, "Period", "Cost"),

    /* 13-month rolling window OR calendar YTD through pReportMonth (union) */
    Filtered = Table.SelectRows(Unpivoted, each List.Contains(AllPeriodLabels, [Period])),

    /* Add sort key so Period (MM-YY) sorts chronologically */
    WithSort = Table.AddColumn(
        Filtered, "Period_Sort",
        each let mm = Number.FromText(Text.Start([Period], 2)),
        yy = Number.FromText(Text.End([Period], 2)),
        yyyy = if yy < 70 then 2000 + yy else 1900 + yy in yyyy * 100 + mm,
        Int64.Type),

    /* Final types */
    Final = Table.TransformColumnTypes(WithSort, {{"Delivery_Type", type text},
                                                  {"Period", type text},
                                                  {"Cost", type number},
                                                  {"Period_Sort", Int64.Type}})
                in Final
