// 🕒 2026-02-20-23-48-50
// # csb/___CSB_Monthly.m
// # Author: R. A. Carucci
// # Purpose: Load Crime Suppression Bureau monthly tracked items with rolling 13-month window.

let
    //==== Source & initial cleanup ============================================================
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\CSB\csb_monthly.xlsm"),
        null, true
    ),
    MoM_Sheet = Source{[Item="MoM",Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(MoM_Sheet, [PromoteAllScalars=true]),
    CleanedData = Table.SelectRows(PromotedHeaders, each [#"Tracked Items"] <> null and [#"Tracked Items"] <> ""),

    //==== Column bookkeeping =================================================================
    ColumnNames = Table.ColumnNames(CleanedData),
    FirstColumnName = ColumnNames{0},
    DateColumns = List.Skip(ColumnNames, 1),

    //==== Rolling 13-month window logic ======================================================
    // Today -> Current month start
    Today = Date.From(DateTime.LocalNow()),
    CurrentMonthStart = Date.StartOfMonth(Today),

    // EndMonth: last fully completed month (exclude current month)
    EndMonth = Date.AddMonths(CurrentMonthStart, -1),

    // StartMonth: 12 months prior to EndMonth (inclusive range gives 13 total months)
    StartMonth = Date.AddMonths(EndMonth, -12),

    //==== Validate/select only date columns within the window ================================
    // Expecting headers like "MM-YY" (e.g., "08-24")
    ValidDateColumns =
        List.Select(
            DateColumns,
            (colName as text) as logical =>
                let
                    parts = Text.Split(colName, "-"),
                    MonthNum =
                        if List.Count(parts) >= 2
                        then try Number.FromText(parts{0}) otherwise null
                        else null,
                    YearTwo =
                        if List.Count(parts) >= 2
                        then try Number.FromText(parts{1}) otherwise null
                        else null,
                    FullYear =
                        if YearTwo <> null
                        then (if YearTwo >= 50 then 1900 + YearTwo else 2000 + YearTwo)
                        else null,
                    ColumnDate =
                        if MonthNum <> null and FullYear <> null
                        then try #date(FullYear, MonthNum, 1) otherwise null
                        else null
                in
                    ColumnDate <> null and ColumnDate >= StartMonth and ColumnDate <= EndMonth
        ),

    SelectedColumns = List.Combine({ {FirstColumnName}, ValidDateColumns }),
    Pruned = Table.SelectColumns(CleanedData, SelectedColumns),

    //==== Unpivot & enrich ===================================================================
    Unpivoted =
        Table.UnpivotOtherColumns(
            Pruned,
            {FirstColumnName},
            "Month_MM_YY",
            "Value"
        ),
    Renamed = Table.RenameColumns(Unpivoted, {{FirstColumnName, "CSB_Category"}}),

    // Parse "MM-YY" into a proper date at month start
    WithDate =
        Table.AddColumn(
            Renamed,
            "Date",
            each
                let
                    monthText = [Month_MM_YY],
                    parts = Text.Split(monthText, "-"),
                    m = if List.Count(parts) >= 2 then try Number.FromText(parts{0}) otherwise 1 else 1,
                    yy = if List.Count(parts) >= 2 then try Number.FromText(parts{1}) otherwise 25 else 25,
                    yyyy = if yy >= 50 then 1900 + yy else 2000 + yy
                in
#date(yyyy, m, 1),
            type date
        ),

    // Exact month index from StartMonth (1..13)
    WithSort =
        Table.AddColumn(
            WithDate,
            "Month_Sort_Order",
            each
                let
                    d = [Date],
                    months =
                        (Date.Year(d) - Date.Year(StartMonth)) * 12
                        + (Date.Month(d) - Date.Month(StartMonth))
                        + 1
                in
                    months,
            Int64.Type
        ),

    WithDisplay =
        Table.AddColumn(WithSort, "Month_Display", each Date.ToText([Date], "MMM yyyy"), type text),

    //==== Sort & types =======================================================================
    Sorted = Table.Sort(WithDisplay, {{"Date", Order.Ascending}}),
    Typed =
        Table.TransformColumnTypes(
            Sorted,
            {
                {"CSB_Category", type text},
                {"Month_MM_YY", type text},
                {"Value", Currency.Type},
                {"Date", type date},
                {"Month_Sort_Order", Int64.Type},
                {"Month_Display", type text}
            }
        ),

    //==== Final hygiene ======================================================================
    Final = Table.SelectRows(Typed, each [CSB_Category] <> null and [CSB_Category] <> "")
in
    Final
