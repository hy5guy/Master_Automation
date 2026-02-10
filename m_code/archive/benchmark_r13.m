// 🕒 2026_01_12_14_40_58
// Project: Benchmark/benchmark_r13
// Author: R. A. Carucci
// Purpose: 
let
    // Read pre-filtered rolling 13-month dataset
    Source = Csv.Document(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Benchmark\by_time_period\rolling_13month\current_window.csv"),
        [ Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv ]),

    // Promote headers
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    // Type conversions
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders, {{"Officer Name", type text},
                          {"Badge Number", Int64.Type},
                          {"Rank", type text},
                          {"Organization", type text},
                          {"Incident Number", type text},
                          {"Report Number", type text},
                          {"Incident Date", type datetime},
                          {"Location", type text},
                          {"Initial Contact", type text},
                          {"# of Officers Involved", Int64.Type},
                          {"# of Subjects", Int64.Type},
                          {"Subject type", type text},
                          {"Report Key", type text},
                          {"EventType", type text}}),

    // Add month-based columns for reporting
    AddMonthStart = Table.AddColumn(
        TypedColumns, "MonthStart",
        each Date.StartOfMonth(Date.From([Incident Date])), type date),

    AddMonthLabel =
        Table.AddColumn(AddMonthStart, "MonthLabel",
                        each Date.ToText([MonthStart], "MM-yy"), type text),

    AddMonthSort = Table.AddColumn(AddMonthLabel, "MonthSort",
                                   each Date.Year([MonthStart]) * 100 +
                                       Date.Month([MonthStart]),
                                   Int64.Type),

    // Replace nulls with 0 in numeric columns
    ReplaceNullNumeric =
        Table.ReplaceValue(AddMonthSort, null, 0, Replacer.ReplaceValue,
                           {"Badge Number", "# of Officers Involved",
                            "# of Subjects"}) in ReplaceNullNumeric