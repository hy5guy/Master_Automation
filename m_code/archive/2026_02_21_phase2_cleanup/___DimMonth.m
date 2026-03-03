let
    Today = DateTime.Date(DateTime.LocalNow()),
    LastFullMonth = Date.EndOfMonth(Date.AddMonths(Today, -1)),
    FirstMonthStart = Date.StartOfMonth(Date.AddMonths(LastFullMonth, -12)),
    MonthStarts = List.Generate(() => FirstMonthStart, each _ <= LastFullMonth, each Date.AddMonths(_, 1)),
    ToTable = Table.FromList(MonthStarts, Splitter.SplitByNothing(), {"MonthStart"}),
    TypedDate = Table.TransformColumnTypes(ToTable, {{"MonthStart", type date}}),
    AddLabel = Table.AddColumn(TypedDate, "MonthLabel", each Date.ToText([MonthStart], "MM-yy"), type text),
    AddSort = Table.AddColumn(AddLabel, "MonthSort", each Date.Year([MonthStart]) * 100 + Date.Month([MonthStart]), Int64.Type)
in
    AddSort