// 🕒 2026-02-21-01-00-00 (EST)
// # overtime/___Overtime_Timeoff_v3.m
// # Author: R. A. Carucci
// # Purpose: Load Overtime and TimeOff monthly accrual data with personnel merge and 13-month window.

let
    ReportMonth = pReportMonth,
    /* =========================
       Paths & Config
       ========================= */
    OutputFolder     = "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Overtime_TimeOff\output",
    AnalyticsFolder  = "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Overtime_TimeOff\analytics_output",

    // Anchoring config: only anchor periods before cutover
    UseAnchoring     = true,
    CutoverLabel     = "09-25",  // Raw values from 09-25 onward

    // Convert CutoverLabel to a real date for proper comparison
    CutoverDate =
        let
            cYear  = Number.FromText("20" & Text.End(CutoverLabel, 2)),
            cMonth = Number.FromText(Text.Start(CutoverLabel, 2))
        in
#date(cYear, cMonth, 1),

    /* =========================
       Rolling 13-month window (exclude current month)
       ========================= */
    NowDT   = DateTime.From(ReportMonth),
    CurrY   = Date.Year(NowDT),
    CurrM   = Date.Month(NowDT),
    EndY    = if CurrM = 1 then CurrY - 1 else CurrY,
    EndM    = if CurrM = 1 then 12 else CurrM - 1,
    StartY  = EndY - 1,
    StartM  = EndM,

    StartDate = #date(StartY, StartM, 1),
    EndDate   = #date(EndY,   EndM,   1),

    // List of month starts within window
    MonthList = List.Generate(
        () => StartDate,
        each _ <= EndDate,
        each Date.AddMonths(_, 1)
    ),

    // Period keys: YYYY-MM and display labels: MM-YY
    PeriodKeysYYYYMM = List.Transform(MonthList, each
        Text.From(Date.Year(_)) & "-" & Text.PadStart(Text.From(Date.Month(_)), 2, "0")),
    PeriodLabelsMMYY = List.Transform(MonthList, each
        Text.PadStart(Text.From(Date.Month(_)), 2, "0") & "-" & Text.End(Text.From(Date.Year(_)), 2)),

    /* =========================
       Load latest FIXED_monthly_breakdown (legacy totals)
       ========================= */
    OutFiles      = Folder.Files(OutputFolder),
    FixedFiltered = Table.SelectRows(OutFiles, each Text.Contains([Name], "FIXED_monthly_breakdown") and Text.EndsWith([Name], ".csv")),
    FixedSorted   = Table.Sort(FixedFiltered, {{"Date modified", Order.Descending}}),
    FixedContent  = if Table.RowCount(FixedSorted) > 0 then FixedSorted{0}[Content] else null,
    FixedCsv      = if FixedContent <> null
                    then Csv.Document(FixedContent, [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv])
                    else #table({}, {}),

    FixedHeaders = Table.PromoteHeaders(FixedCsv, [PromoteAllScalars=true]),

    // Force canonical column order to prevent drift
    FixedReordered = Table.ReorderColumns(
        FixedHeaders,
        {"Year","Month","Month_Name","Period","Date",
         "Accrued_Comp_Time","Accrued_Overtime_Paid",
         "Employee_Sick_Time_Hours","Used_SAT_Time_Hours","Vacation_Hours",
         "Used_Comp_Time","Military_Leave_Hours","Injured_on_Duty_Hours"}
    ),

    FixedTypes = Table.TransformColumnTypes(
        FixedReordered,
        {{"Year", Int64.Type}, {"Month", Int64.Type}, {"Month_Name", type text},
         {"Period", type text}, {"Date", type date},
         {"Accrued_Comp_Time", type number}, {"Accrued_Overtime_Paid", type number},
         {"Employee_Sick_Time_Hours", type number}, {"Used_SAT_Time_Hours", type number},
         {"Vacation_Hours", type number}, {"Used_Comp_Time", type number},
         {"Military_Leave_Hours", type number}, {"Injured_on_Duty_Hours", type number}}
    ),

    // Filter to 13-month window (by YYYY-MM)
    Fixed13 = Table.SelectRows(FixedTypes, each List.Contains(PeriodKeysYYYYMM, [Period])),

    // Legacy (NON-accrual) categories only
    LegacySelect =
        Table.SelectColumns(
            Fixed13,
            {"Period","Employee_Sick_Time_Hours","Used_SAT_Time_Hours","Vacation_Hours",
             "Used_Comp_Time","Military_Leave_Hours","Injured_on_Duty_Hours"}
        ),

    LegacyUnpivot =
        Table.Unpivot(
            LegacySelect,
            {"Employee_Sick_Time_Hours","Used_SAT_Time_Hours","Vacation_Hours",
             "Used_Comp_Time","Military_Leave_Hours","Injured_on_Duty_Hours"},
            "Orig","Value"
        ),

    NameMap =
#table(
            {"Orig", "Time_Category"},
            {
                {"Employee_Sick_Time_Hours","Employee Sick Time (Hours)"},
                {"Used_SAT_Time_Hours","Used SAT Time (Hours)"},
                {"Vacation_Hours","Vacation (Hours)"},
                {"Used_Comp_Time","Comp (Hours)"},
                {"Military_Leave_Hours","Military Leave (Hours)"},
                {"Injured_on_Duty_Hours","Injured on Duty (Hours)"}
            }
        ),

    LegacyJoin  = Table.NestedJoin(LegacyUnpivot, {"Orig"}, NameMap, {"Orig"}, "Lk", JoinKind.LeftOuter),
    LegacyNamed = Table.TransformColumns(LegacyJoin, {{"Lk", each if _ <> null and Table.RowCount(_) > 0 then _{0}[Time_Category] else null}}),
    LegacyPrep  =
        Table.TransformColumns(
            Table.RenameColumns(LegacyNamed, {{"Lk","Time_Category"}}),
            {{"Value", each if _ = null then 0 else _, type number}}
        ),

    // Add display PeriodLabel (MM-yy) for consistent joining
    LegacyWithLabel =
        Table.AddColumn(
            LegacyPrep, "PeriodLabel",
            each Date.ToText(Date.FromText([Period] & "-01"), "MM-yy"),
            type text
        ),

    /* =========================
       Load sworn-split monthly_breakdown (analytics_output)
       ========================= */
    AFiles = Folder.Files(AnalyticsFolder),
    MBFile = Table.SelectRows(AFiles, each [Name] = "monthly_breakdown.csv"),
    MBCont = if Table.RowCount(MBFile) > 0 then MBFile{0}[Content] else null,
    MBCsv  = if MBCont <> null
             then Csv.Document(MBCont,[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv])
             else #table({},{}),

    MBHeaders = Table.PromoteHeaders(MBCsv, [PromoteAllScalars=true]),
    MBTypes   = Table.TransformColumnTypes(
        MBHeaders,
        {{"YearMonth", type text}, {"Class", type text}, {"Metric", type text}, {"Hours", type number}}
    ),

    // Keep window + only accrual metrics
    MBWindow  = Table.SelectRows(MBTypes, each List.Contains(PeriodKeysYYYYMM, [YearMonth])),
    MBAccrual = Table.SelectRows(MBWindow, each [Metric] = "Accrued Comp. Time" or [Metric] = "Accrued Overtime"),

    MBWithLabel =
        Table.AddColumn(
            MBAccrual, "PeriodLabel",
            each let d = Date.FromText([YearMonth] & "-01") in Date.ToText(d, "MM-yy"),
            type text
        ),

    MBWithCat =
        Table.AddColumn(
            MBWithLabel, "Time_Category",
            each if [Metric] = "Accrued Comp. Time"
                 then "Accrued Comp. Time - " & (if [Class] = "Sworn" then "Sworn" else "Non-Sworn")
                 else "Accrued Overtime - " & (if [Class] = "Sworn" then "Sworn" else "Non-Sworn"),
            type text
        ),

    WithBaseMetric =
        Table.AddColumn(
            MBWithCat,
            "BaseMetric",
            each if Text.StartsWith([Time_Category], "Accrued Comp. Time") then "Accrued Comp. Time"
                 else if Text.StartsWith([Time_Category], "Accrued Overtime") then "Accrued Overtime"
                 else null,
            type text
        ),

    /* =========================
       Optional anchor: use last published summary to force exact totals
       ========================= */
    Candidates =
        Table.SelectRows(
            AFiles,
            each Text.Contains([Name], "Monthly_Accrual_and_Usage_Summary") and Text.EndsWith([Name], ".csv")
        ),

    IsPriorFile = (content as binary) as logical =>
        let
            Raw  = Csv.Document(content,[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),
            T    = Table.PromoteHeaders(Raw, [PromoteAllScalars=true]),
            Cols = List.RemoveItems(Table.ColumnNames(T), {"Time Category"})
        in
            List.Contains(Cols, "08-25") and not List.Contains(Cols, "09-25"),

    WithFlag    = Table.AddColumn(Candidates, "IsPrior", each IsPriorFile([Content]), type logical),
    Filtered    = Table.SelectRows(WithFlag, each [IsPrior] = true),
    PriorSorted = Table.Sort(Filtered, {{"Date modified", Order.Descending}}),
    PriorCont   = if Table.RowCount(PriorSorted) > 0 then PriorSorted{0}[Content] else null,
    PriorCsvRaw = if PriorCont <> null then Csv.Document(PriorCont, [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]) else #table({},{}),
    PriorCsv    = Table.PromoteHeaders(PriorCsvRaw, [PromoteAllScalars=true]),
    HasTimeCategory = List.Contains(Table.ColumnNames(PriorCsv), "Time Category"),

    PriorAccruals =
        if HasTimeCategory then
            let
                Keep = Table.SelectRows(PriorCsv, each [#"Time Category"] = "Accrued Comp. Time" or [#"Time Category"] = "Accrued Overtime"),
                Unp  = Table.UnpivotOtherColumns(Keep, {"Time Category"}, "Period", "Total"),
                Ren  = Table.RenameColumns(Unp, {{"Time Category","Metric"}}),
                Typ  = Table.TransformColumnTypes(Ren, {{"Total", type number}})
            in
                Typ
        else
#table({"Metric", "Period", "Total"}, {}),

    PriorAccrualsNorm =
        let
            Trimmed  = Table.TransformColumns(PriorAccruals, {{"Metric", Text.Trim, type text}, {"Period", Text.Trim, type text}}),
            WithLabel =
                Table.AddColumn(
                    Trimmed, "PeriodLabel",
                    each let
                        mm = Text.Start([Period], 2),
                        yy = Text.End([Period], 2),
                        y  = Number.FromText("20" & yy),
                        m  = Number.FromText(mm),
                        d  = #date(y, m, 1)
                    in
                        Date.ToText(d, "MM-yy"),
                    type text
                ),
            KeepCols = Table.SelectColumns(WithLabel, {"Metric","PeriodLabel","Total"})
        in
            KeepCols,

    ForScaleOnly = Table.SelectRows(WithBaseMetric, each [BaseMetric] <> null),

    NewTotals =
        Table.Group(
            ForScaleOnly,
            {"BaseMetric","PeriodLabel"},
            {{"NewTotal", each List.Sum([Hours]), type number}}
        ),

    PriorJoin =
        Table.NestedJoin(
            NewTotals, {"BaseMetric","PeriodLabel"},
            PriorAccrualsNorm, {"Metric","PeriodLabel"},
            "Prior", JoinKind.LeftOuter
        ),

    WithFactor =
        Table.AddColumn(
            PriorJoin, "Scale",
            each let
                pYear  = Number.FromText("20" & Text.End([PeriodLabel], 2)),
                pMonth = Number.FromText(Text.Start([PeriodLabel], 2)),
                pDate  = #date(pYear, pMonth, 1),

                apply = UseAnchoring and pDate < CutoverDate,

                has   = [Prior] <> null and Table.RowCount([Prior]) > 0,
                prior = if has then [Prior]{0}[Total] else null,
                newv  = [NewTotal]
            in
                if apply and has and newv <> null and newv <> 0 then prior / newv else 1.0,
            type number
        ),

    MBJoin =
        Table.NestedJoin(
            WithBaseMetric, {"BaseMetric","PeriodLabel"},
            WithFactor,     {"BaseMetric","PeriodLabel"},
            "F", JoinKind.LeftOuter
        ),

    MBScaled =
        Table.AddColumn(
            MBJoin, "Value",
            each let
                isAccrual = [BaseMetric] <> null,
                ftable    = [F]
            in
                if isAccrual then
                    [Hours] * (
                        if ftable <> null and Table.RowCount(ftable) > 0 and Value.Is(ftable{0}[Scale], Number.Type)
                        then ftable{0}[Scale] else 1.0
                    )
                else
                    [Hours],
            type number
        ),

    MBFinal = Table.SelectColumns(MBScaled, {"PeriodLabel","Time_Category","Value"}),

    /* =========================
       Combine long tables
       ========================= */
    LegacyLong = Table.SelectColumns(LegacyWithLabel, {"PeriodLabel","Time_Category","Value"}),

    // Remove Vacation (Hours)
    LegacyLongFiltered = Table.SelectRows(LegacyLong, each [Time_Category] <> "Vacation (Hours)"),

    CombinedLong = Table.Combine({LegacyLongFiltered, MBFinal}),

    /* =========================
       Output as LONG table (no MM-YY pivot columns)
       Builds full 13-month grid per Time_Category and fills missing values with 0
       Adds PeriodDate + DateSortKey (yyyyMMdd)
       ========================= */
    PeriodDim =
        let
            T0 = Table.FromList(PeriodLabelsMMYY, Splitter.SplitByNothing(), {"PeriodLabel"}, null, ExtraValues.Error),
            T1 = Table.AddColumn(
                    T0, "PeriodDate",
                    each #date(
                        2000 + Number.FromText(Text.End([PeriodLabel], 2)),
                        Number.FromText(Text.Start([PeriodLabel], 2)),
                        1
                    ),
                    type date
                 ),
            T2 = Table.AddColumn(T1, "PeriodKey", each Date.ToText([PeriodDate], "yyyy-MM"), type text),
            T3 = Table.AddColumn(T2, "DateSortKey", each Number.FromText(Date.ToText([PeriodDate], "yyyyMMdd")), Int64.Type)
        in
            T3,

    Categories =
        Table.Distinct(
            Table.SelectColumns(CombinedLong, {"Time_Category"})
        ),

    Grid =
        Table.AddColumn(Categories, "Periods", each PeriodDim, type table),

    ExpandedGrid =
        Table.ExpandTableColumn(
            Grid,
            "Periods",
            {"PeriodLabel","PeriodDate","PeriodKey","DateSortKey"},
            {"PeriodLabel","PeriodDate","PeriodKey","DateSortKey"}
        ),

    Joined =
        Table.NestedJoin(
            ExpandedGrid,
            {"Time_Category","PeriodLabel"},
            CombinedLong,
            {"Time_Category","PeriodLabel"},
            "J",
            JoinKind.LeftOuter
        ),

    WithValue =
        Table.AddColumn(
            Joined,
            "Value",
            each if [J] <> null and Table.RowCount([J]) > 0 then [J]{0}[Value] else 0,
            type number
        ),

    RemovedJoin = Table.RemoveColumns(WithValue, {"J"}),

    Reordered =
        Table.ReorderColumns(
            RemovedJoin,
            {"Time_Category","PeriodLabel","PeriodDate","PeriodKey","DateSortKey","Value"}
        ),

    Sorted = Table.Sort(Reordered, {{"DateSortKey", Order.Ascending}, {"Time_Category", Order.Ascending}})
in
    Sorted
