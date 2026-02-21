// 🕒 2026-02-20-23-48-50
// # drone/___Drone.m
// # Author: R. A. Carucci
// # Purpose: Process DFR and Non-DFR drone metrics with duration-based value handling.

let
    // 1) Load the workbook
    Source = Excel.Workbook(
        File.Contents("C:\Users\RobertCarucci\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Drone_Monthly.xlsx"),
        null, true),

    // ─── DFR Activity sheet ────────────────────────────────────────────────────────
    DFR_Raw = Source{[Name = "DFR Activity", Kind = "Sheet"]}[Data],
    DFR_Headers = Table.PromoteHeaders(DFR_Raw, [PromoteAllScalars = true]),
    DFR_MetricKey = Table.ColumnNames(DFR_Headers){0},
    DFR_PeriodCols = List.Select(Table.ColumnNames(DFR_Headers), each Text.Length(_) = 5 and Text.Middle(_, 2, 1) = "-"),
    DFR_Unpivot = Table.Unpivot(DFR_Headers, DFR_PeriodCols, "Period", "RawValue"),
    DFR_Renamed = Table.RenameColumns(DFR_Unpivot, {{DFR_MetricKey, "Metric"}}),

    // Add ordering for DFR Activity metrics - CORRECTED ORDER
    DFR_WithOrder = Table.AddColumn(DFR_Renamed, "SortOrder", each 
        if [Metric] = "DRF - Total Calls Responded To" then 1 
        else if [Metric] = "DRF - Assisted Arrests" then 2 
        else if [Metric] = "DRF - Deployments that Avoided Dispatching a Patrol Unit" then 3 
        else if [Metric] = "DRF - First on Scene Count" then 4 
        else if [Metric] = "DRF - AVG Response Times - First on Scene (Mins:Secs)" then 5 
        else if [Metric] = "DRF - AVG Response Times - All Calls (Mins:Secs)" then 6 
        else if [Metric] = "DRF - Shift (Hours:Mins)" then 7 
        else if [Metric] = "DRF - Flight Time - Calls Responded To (Hours:Mins)" then 8 
        else if [Metric] = "DRF - Flight Time - Training Flights (Hours:Mins)" then 9 
        else if [Metric] = "DRF - Total Flight Time (Hours:Mins:Secs)" then 10 
        else 99, Int64.Type),

    // CORRECTED: Handle DURATION values properly
    DFR_Converted = Table.AddColumn(DFR_WithOrder, "Value", each 
        let
            RawVal = [RawValue],
            MetricName = [Metric]
        in
            if Value.Is(RawVal, type datetime) or Value.Is(RawVal, type time) then
                let
                    // Convert to time to extract duration components
                    TimeVal = if Value.Is(RawVal, type datetime) then Time.From(RawVal) else RawVal,
                    Hours = Time.Hour(TimeVal),
                    Minutes = Time.Minute(TimeVal),
                    Seconds = Time.Second(TimeVal)
                in
                    if Text.Contains(MetricName, "(Mins:Secs)") then
                        // For response times: show total minutes and seconds
                        let
                            TotalMinutes = Hours * 60 + Minutes,
                            DisplaySeconds = Seconds
                        in Text.From(TotalMinutes) & ":" & Text.PadStart(Text.From(DisplaySeconds), 2, "0")
                    else if Text.Contains(MetricName, "(Hours:Mins)") and not Text.Contains(MetricName, "Secs") then
                        // For flight times: show hours and minutes
                        Text.PadStart(Text.From(Hours), 2, "0") & ":" & Text.PadStart(Text.From(Minutes), 2, "0")
                    else if Text.Contains(MetricName, "(Hours:Mins:Secs)") then
                        // For complete time: show hours, minutes, and seconds
                        Text.PadStart(Text.From(Hours), 2, "0") & ":" & Text.PadStart(Text.From(Minutes), 2, "0") & ":" & Text.PadStart(Text.From(Seconds), 2, "0")
                    else
                        Text.From(RawVal)
            else if Value.Is(RawVal, type duration) then
                // Handle actual duration type
                if Text.Contains(MetricName, "(Mins:Secs)") then
                    let
                        TotalSeconds = Duration.TotalSeconds(RawVal),
                        TotalMinutes = Number.IntegerDivide(TotalSeconds, 60),
                        RemainderSeconds = Number.Mod(TotalSeconds, 60)
                    in Text.From(TotalMinutes) & ":" & Text.PadStart(Text.From(Number.Round(RemainderSeconds, 0)), 2, "0")
                else if Text.Contains(MetricName, "(Hours:Mins)") then
                    let
                        TotalSeconds = Duration.TotalSeconds(RawVal),
                        TotalHours = Number.IntegerDivide(TotalSeconds, 3600),
                        RemainderMinutes = Number.IntegerDivide(Number.Mod(TotalSeconds, 3600), 60)
                    in Text.PadStart(Text.From(TotalHours), 2, "0") & ":" & Text.PadStart(Text.From(RemainderMinutes), 2, "0")
                else
                    Duration.ToText(RawVal, "h:mm:ss")
            else if Value.Is(RawVal, type number) then
                if Text.Contains(MetricName, "(Mins:Secs)") or Text.Contains(MetricName, "(Hours:Mins)") then
                    // Handle duration stored as decimal (fraction of day)
                    let
                        TotalSeconds = RawVal * 24 * 60 * 60, // Convert fraction of day to seconds
                        Hours = Number.IntegerDivide(TotalSeconds, 3600),
                        Minutes = Number.IntegerDivide(Number.Mod(TotalSeconds, 3600), 60),
                        Seconds = Number.Round(Number.Mod(TotalSeconds, 60), 0)
                    in
                        if Text.Contains(MetricName, "(Mins:Secs)") then
                            let TotalMinutes = Hours * 60 + Minutes
                            in Text.From(TotalMinutes) & ":" & Text.PadStart(Text.From(Seconds), 2, "0")
                        else
                            Text.PadStart(Text.From(Hours), 2, "0") & ":" & Text.PadStart(Text.From(Minutes), 2, "0")
                else
                    Text.From(RawVal)
            else
                Text.From(RawVal)),
    DFR_Clean = Table.RemoveColumns(DFR_Converted, {"RawValue"}),
    DFR_Tagged = Table.AddColumn(DFR_Clean, "Source", each "DFR Activity"),

    // ─── Non-DFR sheet ─────────────────────────────────────────────────────────────
    NonDFR_Raw = Source{[Name = "Non-DFR", Kind = "Sheet"]}[Data],
    NonDFR_Headers = Table.PromoteHeaders(NonDFR_Raw, [PromoteAllScalars = true]),
    NonDFR_MetricKey = Table.ColumnNames(NonDFR_Headers){0},
    NonDFR_PeriodCols = List.Select(Table.ColumnNames(NonDFR_Headers), each Text.Length(_) = 5 and Text.Middle(_, 2, 1) = "-"),
    NonDFR_Unpivot = Table.Unpivot(NonDFR_Headers, NonDFR_PeriodCols, "Period", "RawValue"),
    NonDFR_Renamed = Table.RenameColumns(NonDFR_Unpivot, {{NonDFR_MetricKey, "Metric"}}),

    // Add ordering for Non-DFR metrics
    NonDFR_WithOrder = Table.AddColumn(NonDFR_Renamed, "SortOrder", each 
        if [Metric] = "Non-DFR - Flight Time - Calls Responded To (Hours:Mins)" then 1 
        else if [Metric] = "Non-DFR - Flight Time - Trainging Flights (Hours:Mins)" then 2 
        else if [Metric] = "Non-DFR - Total Flight Time (Hours:Mins)" then 3 
        else 99, Int64.Type),

    // Handle Non-DFR duration values the same way
    NonDFR_Converted = Table.AddColumn(NonDFR_WithOrder, "Value", each 
        let
            RawVal = [RawValue],
            MetricName = [Metric]
        in
            if Value.Is(RawVal, type datetime) or Value.Is(RawVal, type time) then
                let
                    TimeVal = if Value.Is(RawVal, type datetime) then Time.From(RawVal) else RawVal,
                    Hours = Time.Hour(TimeVal),
                    Minutes = Time.Minute(TimeVal),
                    Seconds = Time.Second(TimeVal)
                in
                    if Text.Contains(MetricName, "(Hours:Mins)") then
                        Text.PadStart(Text.From(Hours), 2, "0") & ":" & Text.PadStart(Text.From(Minutes), 2, "0")
                    else
                        Text.From(RawVal)
            else if Value.Is(RawVal, type duration) then
                if Text.Contains(MetricName, "(Hours:Mins)") then
                    let
                        TotalSeconds = Duration.TotalSeconds(RawVal),
                        TotalHours = Number.IntegerDivide(TotalSeconds, 3600),
                        RemainderMinutes = Number.IntegerDivide(Number.Mod(TotalSeconds, 3600), 60)
                    in Text.PadStart(Text.From(TotalHours), 2, "0") & ":" & Text.PadStart(Text.From(RemainderMinutes), 2, "0")
                else
                    Duration.ToText(RawVal, "h:mm:ss")
            else if Value.Is(RawVal, type number) then
                if Text.Contains(MetricName, "(Hours:Mins)") then
                    let
                        TotalSeconds = RawVal * 24 * 60 * 60,
                        Hours = Number.IntegerDivide(TotalSeconds, 3600),
                        Minutes = Number.IntegerDivide(Number.Mod(TotalSeconds, 3600), 60)
                    in Text.PadStart(Text.From(Hours), 2, "0") & ":" & Text.PadStart(Text.From(Minutes), 2, "0")
                else
                    Text.From(RawVal)
            else
                Text.From(RawVal)),
    NonDFR_Clean = Table.RemoveColumns(NonDFR_Converted, {"RawValue"}),
    NonDFR_Tagged = Table.AddColumn(NonDFR_Clean, "Source", each "Non-DFR"),

    // ─── Combine both tables & add date keys ───────────────────────────────────────
    Combined = Table.Combine({DFR_Tagged, NonDFR_Tagged}),
    WithDate = Table.AddColumn(Combined, "PeriodDate", each
#date(2000 + Number.FromText(Text.End([Period], 2)),                           \
      Number.FromText(Text.Start([Period], 2)), 1),                            \
    type date),
    WithSort = Table.AddColumn(WithDate, "DateSortKey", each 
        Date.Year([PeriodDate]) * 100 + Date.Month([PeriodDate]), Int64.Type),

    // ─── Filter to Rolling 13 Months ───
    Today = DateTime.Date(DateTime.LocalNow()),
    PriorMonth = Date.AddMonths(#date(Date.Year(Today), Date.Month(Today), 1), -1),
    StartMonth = Date.AddMonths(PriorMonth, -12),

    FilteredData = Table.SelectRows(WithSort, each [PeriodDate] >= StartMonth and [PeriodDate] <= PriorMonth),

    // ─── Create totals with proper duration arithmetic ──────────────────────────────────────────────────

    // *** MODIFIED STEP ***
    // We REMOVED the "DataForTotals" step
    // We now group on "FilteredData" and add a special check for the AVG metrics
    AllMetricGroups = Table.Group(FilteredData, {"Metric", "Source", "SortOrder"}, {
        {"TotalValue", each 
            let
                CurrentTable = _,
                MetricName = CurrentTable[Metric]{0}
            in
                // NEW: Check for specific AVG metrics first
                if MetricName = "DRF - AVG Response Times - All Calls (Mins:Secs)" or
                   MetricName = "DRF - AVG Response Times - First on Scene (Mins:Secs)"
                then
                    "N/A" // <-- This is the value that will show in the Total column
                
                // --- Existing logic below ---
                else if Text.Contains(MetricName, "(Mins:Secs)") then
                    // For response times, calculate average
                    let 
                        TimeValues = List.Transform(CurrentTable[Value], each 
                            try
                                let 
                                    TimeStr = Text.From(_),
                                    Parts = Text.Split(TimeStr, ":"),
                                    Minutes = if List.Count(Parts) >= 2 then Number.From(Parts{0}) else 0,
                                    Seconds = if List.Count(Parts) >= 2 then Number.From(Parts{1}) else 0,
                                    TotalSeconds = Minutes * 60 + Seconds
                                in TotalSeconds
                            otherwise 0),
                       
                        ValidTimeValues = List.Select(TimeValues, each _ > 0),
                        AvgSeconds = if List.Count(ValidTimeValues) > 0 then List.Average(ValidTimeValues) else 0,
                        AvgMinutes = Number.IntegerDivide(AvgSeconds, 60),
                        AvgSecs = Number.Round(Number.Mod(AvgSeconds, 60), 0)
                    in Text.From(AvgMinutes) & ":" & Text.PadStart(Text.From(AvgSecs), 2, "0")
                else if Text.Contains(MetricName, "(Hours:Mins)") and not Text.Contains(MetricName, "Secs") then
                    // For flight times without seconds, sum the time values
                    let 
                        TimeValues = List.Transform(CurrentTable[Value], each 
                            try
                                let 
                                    TimeStr = Text.From(_),
                                    Parts = Text.Split(TimeStr, ":"),
                                    Hours = if List.Count(Parts) >= 2 then Number.From(Parts{0}) else 0,
                                    Minutes = if List.Count(Parts) >= 2 then Number.From(Parts{1}) else 0
                                in Hours * 60 + Minutes
                            otherwise 0),
                        TotalMinutes = List.Sum(TimeValues),
                        TotalHours = Number.IntegerDivide(TotalMinutes, 60),
                        FinalMinutes = Number.Mod(TotalMinutes, 60)
                    in Text.PadStart(Text.From(TotalHours), 2, "0") & ":" & Text.PadStart(Text.From(FinalMinutes), 2, "0")
                else if Text.Contains(MetricName, "(Hours:Mins:Secs)") then
                    // FIXED: For flight times with seconds, sum the time values properly
                    let 
                        TimeValues = List.Transform(CurrentTable[Value], each 
                            try
                                let 
                                    TimeStr = Text.From(_),
                                    Parts = Text.Split(TimeStr, ":"),
                                    Hours = if List.Count(Parts) >= 3 then Number.From(Parts{0}) else 0,
                                    Minutes = if List.Count(Parts) >= 3 then Number.From(Parts{1}) else 0,
                                    Seconds = if List.Count(Parts) >= 3 then Number.From(Parts{2}) else 0
                                in Hours * 3600 + Minutes * 60 + Seconds
                            otherwise 0),
                        TotalSeconds = List.Sum(TimeValues),
                        TotalHours = Number.IntegerDivide(TotalSeconds, 3600),
                        TotalMinutes = Number.IntegerDivide(Number.Mod(TotalSeconds, 3600), 60),
                        FinalSeconds = Number.Round(Number.Mod(TotalSeconds, 60), 0)
                    in Text.PadStart(Text.From(TotalHours), 2, "0") & ":" & Text.PadStart(Text.From(TotalMinutes), 2, "0") & ":" & Text.PadStart(Text.From(FinalSeconds), 2, "0")
                else
                    // For all other metrics, sum the values
                    Text.From(Number.Round(List.Sum(List.Transform(CurrentTable[Value], each try Number.From(_) otherwise 0)), 2))
        }
    }),

    // Add required columns for total rows
    TotalsWithPeriod = Table.AddColumn(AllMetricGroups, "Period", each "Total"),
    TotalsWithValue = Table.AddColumn(TotalsWithPeriod, "Value", each [TotalValue]),
    TotalsWithDate = Table.AddColumn(TotalsWithValue, "PeriodDate", each #date(2099, 12, 31), type date),
    TotalsWithSort = Table.AddColumn(TotalsWithDate, "DateSortKey", each 999999, Int64.Type),

    // ─── Combine regular data with all totals ───────────────────────────────────────
    CombinedWithAllTotals = Table.Combine({FilteredData, TotalsWithSort}),

    // ─── Sort by Source, SortOrder, then Date ──────────────────────────────────────
    Sorted = Table.Sort(CombinedWithAllTotals, {
        {"Source", Order.Ascending},
        {"SortOrder", Order.Ascending},
        {"DateSortKey", Order.Ascending}
    }),

    // ─── Keep only the final columns ──────────────────────────────────────────────
    Final = Table.SelectColumns(Sorted, {"Metric", "Period", "Value", "Source", "PeriodDate", "DateSortKey", "SortOrder"})

in Final
