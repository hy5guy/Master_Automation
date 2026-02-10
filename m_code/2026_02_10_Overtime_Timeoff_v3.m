// 🕒 2026-02-10-17-28-15 EST
// # Master_Automation/m_code/2026_02_10_Overtime_Timeoff_v3.m
// # Author: R. A. Carucci
// # Purpose: Load latest FIXED and monthly_breakdown CSVs, combine legacy usage and accrual rows, and output a long table for the Monthly Accrual and Usage Summary visual.
// # Formula.Firewall fix: data loading is in 3 staging queries; main query only references them.
//
// =============================================================================
// SETUP: Create 4 queries. Staging first (OT_FIXED_Staged.m, OT_MonthlyBreakdown_Staged.m, OT_PriorAnchor_Staged.m).
//   Staging query names must be exactly: OT_FIXED_Staged, OT_MonthlyBreakdown_Staged, OT_PriorAnchor_Staged
//   Main query: ___Overtime_Timeoff_v3. Paste the let below.
// =============================================================================
let
    UseAnchoring = true,
    CutoverLabel = "09-25",
    CutoverDate  = #date(Number.FromText("20" & Text.End(CutoverLabel, 2)), Number.FromText(Text.Start(CutoverLabel, 2)), 1),

    NowDT   = DateTime.LocalNow(),
    CurrY   = Date.Year(NowDT),
    CurrM   = Date.Month(NowDT),
    EndY    = if CurrM = 1 then CurrY - 1 else CurrY,
    EndM    = if CurrM = 1 then 12 else CurrM - 1,
    StartY  = EndY - 1,
    StartM  = EndM,
    StartDate = #date(StartY, StartM, 1),
    EndDate   = #date(EndY, EndM, 1),
    MonthList  = List.Generate(() => StartDate, each _ <= EndDate, each Date.AddMonths(_, 1)),
    PeriodKeysYYYYMM = List.Transform(MonthList, each Text.From(Date.Year(_)) & "-" & Text.PadStart(Text.From(Date.Month(_)), 2, "0")),
    PeriodLabelsMMYY = List.Transform(MonthList, each Text.PadStart(Text.From(Date.Month(_)), 2, "0") & "-" & Text.End(Text.From(Date.Year(_)), 2)),

    FixedTypes = #"OT_FIXED_Staged",
    Fixed13    = Table.SelectRows(FixedTypes, each List.Contains(PeriodKeysYYYYMM, [Period])),
    LegacySelect = Table.SelectColumns(Fixed13, {"Period", "Employee_Sick_Time_Hours", "Used_SAT_Time_Hours", "Vacation_Hours", "Used_Comp_Time", "Military_Leave_Hours", "Injured_on_Duty_Hours"}),
    LegacyUnpivot = Table.Unpivot(LegacySelect, {"Employee_Sick_Time_Hours", "Used_SAT_Time_Hours", "Vacation_Hours", "Used_Comp_Time", "Military_Leave_Hours", "Injured_on_Duty_Hours"}, "Orig", "Value"),
    NameMap = #table({"Orig", "Time_Category"}, {{"Employee_Sick_Time_Hours","Employee Sick Time (Hours)"}, {"Used_SAT_Time_Hours","Used SAT Time (Hours)"}, {"Vacation_Hours","Vacation (Hours)"}, {"Used_Comp_Time","Comp (Hours)"}, {"Military_Leave_Hours","Military Leave (Hours)"}, {"Injured_on_Duty_Hours","Injured on Duty (Hours)"}}),
    LegacyJoin  = Table.NestedJoin(LegacyUnpivot, {"Orig"}, NameMap, {"Orig"}, "Lk", JoinKind.LeftOuter),
    LegacyNamed = Table.TransformColumns(LegacyJoin, {{"Lk", each if _ <> null and Table.RowCount(_) > 0 then _{0}[Time_Category] else null}}),
    LegacyPrep  = Table.TransformColumns(Table.RenameColumns(LegacyNamed, {{"Lk", "Time_Category"}}), {{"Value", each if _ = null then 0 else _, type number}}),
    LegacyWithLabel = Table.AddColumn(LegacyPrep, "PeriodLabel", each Date.ToText(Date.FromText([Period] & "-01"), "MM-yy"), type text),

    MBTypes    = #"OT_MonthlyBreakdown_Staged",
    MBWindow   = Table.SelectRows(MBTypes, each List.Contains(PeriodKeysYYYYMM, [YearMonth])),
    MBAccrual  = Table.SelectRows(MBWindow, each [Metric] = "Accrued Comp. Time" or [Metric] = "Accrued Overtime"),
    MBWithLabel = Table.AddColumn(MBAccrual, "PeriodLabel", each Date.ToText(Date.FromText([YearMonth] & "-01"), "MM-yy"), type text),
    MBWithCat  = Table.AddColumn(MBWithLabel, "Time_Category", each if [Metric] = "Accrued Comp. Time" then "Accrued Comp. Time - " & (if [Class] = "Sworn" then "Sworn" else "Non-Sworn") else "Accrued Overtime - " & (if [Class] = "Sworn" then "Sworn" else "Non-Sworn"), type text),
    WithBaseMetric = Table.AddColumn(MBWithCat, "BaseMetric", each if Text.StartsWith([Time_Category], "Accrued Comp. Time") then "Accrued Comp. Time" else if Text.StartsWith([Time_Category], "Accrued Overtime") then "Accrued Overtime" else null, type text),

    PriorAccrualsNorm = #"OT_PriorAnchor_Staged",
    ForScaleOnly = Table.SelectRows(WithBaseMetric, each [BaseMetric] <> null),
    NewTotals    = Table.Group(ForScaleOnly, {"BaseMetric", "PeriodLabel"}, {{"NewTotal", each List.Sum([Hours]), type number}}),
    PriorJoin    = Table.NestedJoin(NewTotals, {"BaseMetric", "PeriodLabel"}, PriorAccrualsNorm, {"Metric", "PeriodLabel"}, "Prior", JoinKind.LeftOuter),
    WithFactor   = Table.AddColumn(PriorJoin, "Scale", each let pYear = Number.FromText("20" & Text.End([PeriodLabel], 2)), pMonth = Number.FromText(Text.Start([PeriodLabel], 2)), pDate = #date(pYear, pMonth, 1), apply = UseAnchoring and pDate < CutoverDate, has = [Prior] <> null and Table.RowCount([Prior]) > 0, prior = if has then [Prior]{0}[Total] else null, newv = [NewTotal] in if apply and has and newv <> null and newv <> 0 then prior / newv else 1.0, type number),
    MBJoin       = Table.NestedJoin(WithBaseMetric, {"BaseMetric", "PeriodLabel"}, WithFactor, {"BaseMetric", "PeriodLabel"}, "F", JoinKind.LeftOuter),
    MBScaled     = Table.AddColumn(MBJoin, "Value", each let isAccrual = [BaseMetric] <> null, ftable = [F] in if isAccrual then [Hours] * (if ftable <> null and Table.RowCount(ftable) > 0 and Value.Is(ftable{0}[Scale], Number.Type) then ftable{0}[Scale] else 1.0) else [Hours], type number),
    MBFinal      = Table.SelectColumns(MBScaled, {"PeriodLabel", "Time_Category", "Value"}),

    LegacyLong = Table.SelectColumns(LegacyWithLabel, {"PeriodLabel", "Time_Category", "Value"}),
    LegacyLongFiltered = Table.SelectRows(LegacyLong, each [Time_Category] <> "Vacation (Hours)"),
    CombinedLong = Table.Combine({LegacyLongFiltered, MBFinal}),

    PeriodDim = let T0 = Table.FromList(PeriodLabelsMMYY, Splitter.SplitByNothing(), {"PeriodLabel"}, null, ExtraValues.Error), T1 = Table.AddColumn(T0, "PeriodDate", each #date(2000 + Number.FromText(Text.End([PeriodLabel], 2)), Number.FromText(Text.Start([PeriodLabel], 2)), 1), type date), T2 = Table.AddColumn(T1, "PeriodKey", each Date.ToText([PeriodDate], "yyyy-MM"), type text), T3 = Table.AddColumn(T2, "DateSortKey", each Number.FromText(Date.ToText([PeriodDate], "yyyyMMdd")), Int64.Type) in T3,
    Categories = Table.Distinct(Table.SelectColumns(CombinedLong, {"Time_Category"})),
    Grid = Table.AddColumn(Categories, "Periods", each PeriodDim, type table),
    ExpandedGrid = Table.ExpandTableColumn(Grid, "Periods", {"PeriodLabel", "PeriodDate", "PeriodKey", "DateSortKey"}, {"PeriodLabel", "PeriodDate", "PeriodKey", "DateSortKey"}),
    Joined = Table.NestedJoin(ExpandedGrid, {"Time_Category", "PeriodLabel"}, CombinedLong, {"Time_Category", "PeriodLabel"}, "J", JoinKind.LeftOuter),
    WithValue = Table.AddColumn(Joined, "Value", each if [J] <> null and Table.RowCount([J]) > 0 then [J]{0}[Value] else 0, type number),
    RemovedJoin = Table.RemoveColumns(WithValue, {"J"}),
    Reordered = Table.ReorderColumns(RemovedJoin, {"Time_Category", "PeriodLabel", "PeriodDate", "PeriodKey", "DateSortKey", "Value"}),
    // Rename to "Time Category" so visuals and DAX that expect that name keep working
    RenamedForVisual = Table.RenameColumns(Reordered, {{"Time_Category", "Time Category"}}),
    Sorted = Table.Sort(RenamedForVisual, {{"DateSortKey", Order.Ascending}, {"Time Category", Order.Ascending}})
in
    Sorted
