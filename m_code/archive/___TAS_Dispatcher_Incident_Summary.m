// 🕒 TAS Dispatcher Incident Summary
// Purpose: Import TAS/Virtual Patrol data, normalize incidents and dispatchers,
//          count by dispatcher/incident/month for rolling 13-month window
// Output: Normalized table with columns: DispatcherNew, Incident, Month,
// Month_Sort, Count NOTE: Do NOT auto-format this file - file paths will break

let
    // =========================
    // Configuration
    // =========================
    FilePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\tas\2025\2024_to_2025_12_TAS_and_Vitural_2026_01_07.csv",

    // Valid dispatchers (normalized to lowercase)
    ValidDispatchers = {"carucci_r", "marino_b", "rios_a", "iannacone_a",
                        "polson_r"},

    // Valid incident types (normalized)
    ValidIncidents = {"TAS Alert - Missing Person",
                      "TAS Alert - Stolen License Plate",
                      "TAS Alert - Stolen Vehicle", "TAS Alert - Wanted Person",
                      "Virtual - Patrol"},

    // =========================
    // Load CSV
    // =========================
    Source = Csv.Document(
        File.Contents(FilePath),
        [ Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv ]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    // =========================
    // Normalize DispatcherNew to lowercase
    // =========================
    LowercaseDispatcher = Table.TransformColumns(
        Promoted, {{"DispatcherNew", Text.Lower, type text}}),

    // =========================
    // Filter to valid dispatchers only
    // =========================
    FilteredDispatchers =
        Table.SelectRows(LowercaseDispatcher,
                         each List.Contains(ValidDispatchers, [DispatcherNew])),

    // =========================
    // Normalize Incident column
    // Handle case variations: "Tas Alert" -> "TAS Alert", etc.
    // Map non-matching incidents to "Other"
    // =========================
    NormalizedIncident = Table.AddColumn(
        FilteredDispatchers, "Incident_Normalized",
        each let incident = if [Incident] = null then "" else Text.Trim([Incident]),
        // Normalize: lowercase and standardize spacing
        normalized = Text.Lower(
            Text.Replace(Text.Replace(incident, "  ", " "), " - ", " - ")),
        // Find matching valid incident (case-insensitive comparison)
        matched = List.First(List.Select(
            ValidIncidents,
            each Text.Lower(Text.Replace(Text.Replace(_, "  ", " "), " - ",
                                         " - ")) = normalized), null) in
            if matched <> null then matched else "Other",
        type text),

    // Use normalized incidents (no filtering - "Other" included)
    FilteredIncidents = NormalizedIncident,

    // =========================
    // Extract month from "Time of Call"
    // Format: "MM/DD/YYYY HH:MM" -> extract date, then month
    // =========================
    WithDate = Table.AddColumn(
        FilteredIncidents, "CallDate", each let timeOfCall = [#"Time of Call"],
        // Parse date (handles "MM/DD/YYYY HH:MM" format)
        dateTimeValue = try DateTime.FromText(timeOfCall) otherwise null,
        dateValue = if dateTimeValue <> null then Date.From(dateTimeValue) else null
        in dateValue,
        type date),

    // =========================
    // Calculate rolling 13-month window (exclude current month)
    // =========================
    NowDT = DateTime.LocalNow(), CurrY = Date.Year(NowDT),
    CurrM = Date.Month(NowDT), EndY = if CurrM = 1 then CurrY - 1 else CurrY,
    EndM = if CurrM = 1 then 12 else CurrM - 1,

    // End Date = last day of previous month
    // Start Date = 12 months before End Date (gives 13 months total)
    EndDate = #date(EndY, EndM, 1), StartDate = Date.AddMonths(EndDate, -12),

    // Generate list of month start dates in window
    MonthList = List.Generate(() => StartDate, each _ <= EndDate,
                              each Date.AddMonths(_, 1)), 

    // Convert to MM-YY format for column headers
    PeriodLabelsMMYY = List.Transform(
        MonthList, each Text.PadStart(Text.From(Date.Month(_)), 2, "0") & "-" &
                       Text.End(Text.From(Date.Year(_)), 2)),

    // =========================
    // Add Period (MM-YY) column and filter to window
    // =========================
    WithPeriod = Table.AddColumn(
        WithDate, "Period",
        each if[CallDate]<> null then let y = Date.Year([CallDate]),
        m = Date.Month([CallDate]),
        period = Text.PadStart(Text.From(m), 2, "0") & "-" &
                 Text.End(Text.From(y), 2) in period else null,
        type text),

    // Filter to only periods in the 13-month window
    FilteredPeriod = Table.SelectRows(
        WithPeriod,
        each[Period]<> null and List.Contains(PeriodLabelsMMYY, [Period])),

    // =========================
    // Group and count by DispatcherNew, Incident_Normalized, Period
    // =========================
    Grouped = Table.Group(FilteredPeriod,
                          {"DispatcherNew", "Incident_Normalized", "Period"},
                          {{"Count", each Table.RowCount(_), type number}}),

    // =========================
    // Create all combinations to ensure zeros for missing data
    // =========================
    // Create table of all dispatchers
    AllDispatchers = Table.FromList(ValidDispatchers, Splitter.SplitByNothing(),
                                    {"DispatcherNew"}),

    // Create table of all incidents (including "Other")
    AllIncidents = Table.FromList(List.Combine({ValidIncidents, {"Other"}}),
                                  Splitter.SplitByNothing(), {"Incident"}),

    // Create table of all periods
    AllPeriods =
        Table.FromList(PeriodLabelsMMYY, Splitter.SplitByNothing(), {"Period"}),

    // Create Cartesian product: all dispatchers × all incidents × all periods
    AllCombinations_Step1 = Table.AddColumn(AllDispatchers, "IncidentTable", each AllIncidents),
    AllCombinations_Step2 = Table.ExpandTableColumn(AllCombinations_Step1, "IncidentTable", {"Incident"}, {"Incident"}),
    AllCombinations_Step3 = Table.AddColumn(AllCombinations_Step2, "PeriodTable", each AllPeriods),
    AllCombinations = Table.ExpandTableColumn(AllCombinations_Step3, "PeriodTable", {"Period"}, {"Period"}),

    // Add Month_Sort to all combinations
    AllCombinationsWithSort = Table.AddColumn(
        AllCombinations, "Month_Sort",
        each let mm = Number.FromText(Text.Start([Period], 2)),
        yy = Number.FromText(Text.End([Period], 2)),
        yyyy = if yy < 70 then 2000 + yy else 1900 + yy in yyyy * 100 + mm,
        Int64.Type),

    // Rename Period to Month in all combinations
    AllCombinationsRenamed =
        Table.RenameColumns(AllCombinationsWithSort, {{"Period", "Month"}}),

    // =========================
    // Join grouped data to all combinations (left join)
    // =========================
    // Rename Period to Month in grouped data for join
    GroupedRenamed = Table.RenameColumns(
        Grouped, {{"Incident_Normalized", "Incident"}, {"Period", "Month"}}),

    // Left join: all combinations (left) with grouped data (right)
    Joined = Table.NestedJoin(
        AllCombinationsRenamed, {"DispatcherNew", "Incident", "Month"},
        GroupedRenamed, {"DispatcherNew", "Incident", "Month"}, "GroupedData",
        JoinKind.LeftOuter),

    // Expand the nested table and get Count (or 0 if missing)
    Expanded =
        Table.ExpandTableColumn(Joined, "GroupedData", {"Count"}, {"Count"}),

    // Replace null Count with 0
    WithZeros =
        Table.ReplaceValue(Expanded, null, 0, Replacer.ReplaceValue, {"Count"}),

    // Final table (already has Month column)
    Renamed = WithZeros,

    // Reorder columns: DispatcherNew, Incident, Month, Month_Sort, Count
    Reordered = Table.ReorderColumns(
        Renamed, {"DispatcherNew", "Incident", "Month", "Month_Sort", "Count"}),

    // Set column types
    Typed = Table.TransformColumnTypes(Reordered, {{"DispatcherNew", type text},
                                                   {"Incident", type text},
                                                   {"Month", type text},
                                                   {"Month_Sort", Int64.Type},
                                                   {"Count", type number}})

                in Typed
