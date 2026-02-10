// DimMonth - Month dimension table for rolling 13-month window
// QUERY NAME: benchmark_dim_month
//
let
    // Calculate dynamic start date (13 months ago from last complete month)
    Today = DateTime.LocalNow(),
    CurrentYear = Date.Year(Today), CurrentMonth = Date.Month(Today),

    EndYear = if CurrentMonth = 1 then CurrentYear - 1 else CurrentYear,
    EndMonth = if CurrentMonth = 1 then 12 else CurrentMonth - 1,
    EndDate = #date(EndYear, EndMonth, 1),

    StartDate = Date.AddMonths(EndDate, -12), MonthCount = 13,

    // Generate list of month starts
    MonthStarts = List.Generate(() => StartDate, each _ <= EndDate,
                                each Date.AddMonths(_, 1)),

    // Convert to table
    ToTable =
        Table.FromList(MonthStarts, Splitter.SplitByNothing(), {"MonthStart"}),

    TypedDate =
        Table.TransformColumnTypes(ToTable, {{"MonthStart", type date}}),

    // Add helper columns
    AddLabel =
        Table.AddColumn(TypedDate, "MonthLabel",
                        each Date.ToText([MonthStart], "MM-yy"), type text),

    AddSort = Table.AddColumn(AddLabel, "MonthSort",
                              each Date.Year([MonthStart]) * 100 +
                                  Date.Month([MonthStart]),
                              Int64.Type),

    AddMonthName = Table.AddColumn(AddSort, "MonthName",
                                   each Date.ToText([MonthStart], "MMMM yyyy"),
                                   type text) in AddMonthName