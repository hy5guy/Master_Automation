// 🕒 2026-02-21-01-00-00 (EST)
// # ssocc/TAS_Dispatcher_Incident.m
// # Author: R. A. Carucci
// # Purpose: Load TAS dispatcher incident summary data from SSOCC workbook.

let
    ReportMonth = pReportMonth,
    // =========================
    // Configuration
    // =========================
    FilePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_CAD\tas\yearly\2025\2025_01_to_2026_02_13_Hackensack_CAD_Data.xlsx",
    SheetName = "Sheet1",  // ⚠️ CHANGE THIS to match your actual sheet name
    
    // Valid dispatchers (normalized to lowercase)
    ValidDispatchers = {"carucci_r", "marino_b", "rios_a", "iannacone_a", "polson_r"},
    
    // Valid incident types (normalized)
    ValidIncidents = {
        "TAS Alert - Missing Person",
        "TAS Alert - Stolen License Plate", 
        "TAS Alert - Stolen Vehicle",
        "TAS Alert - Wanted Person",
        "Virtual - Patrol"
    },

    // =========================
    // Load Excel Workbook (FIXED)
    // =========================
    Source = Excel.Workbook(
        File.Contents(FilePath),
        null, 
        true
    ),
    
    // Load the specified sheet
    SheetData = Source{[Item=SheetName,Kind="Sheet"]}[Data],
    
    // Promote headers
    Promoted = Table.PromoteHeaders(SheetData, [PromoteAllScalars=true]),
    
    // ⚠️ DIAGNOSTIC: Check actual column names
    // Uncomment this line temporarily to see all column names:
    // ColumnNames = Table.ColumnNames(Promoted),
    
    // =========================
    // Map to expected column names (FLEXIBLE)
    // =========================
    // Try to find dispatcher column (could be "Dispatcher", "DispatcherNew", "Dispatcher Name", etc.)
    ColumnNames = Table.ColumnNames(Promoted),
    
    DispatcherCol = 
        if List.Contains(ColumnNames, "DispatcherNew") then "DispatcherNew"
        else if List.Contains(ColumnNames, "Dispatcher") then "Dispatcher"
        else if List.Contains(ColumnNames, "DispatcherName") then "DispatcherName"
        else null,
    
    IncidentCol = 
        if List.Contains(ColumnNames, "Incident") then "Incident"
        else if List.Contains(ColumnNames, "Incident Type") then "Incident Type"
        else if List.Contains(ColumnNames, "IncidentType") then "IncidentType"
        else null,
    
    TimeCol = 
        if List.Contains(ColumnNames, "Time of Call") then "Time of Call"
        else if List.Contains(ColumnNames, "TimeOfCall") then "TimeOfCall"
        else if List.Contains(ColumnNames, "CallTime") then "CallTime"
        else if List.Contains(ColumnNames, "Time") then "Time"
        else null,
    
    // Error if required columns not found
    CheckColumns = 
        if DispatcherCol = null then error "Required column not found: Dispatcher (tried: DispatcherNew, Dispatcher, DispatcherName)"
        else if IncidentCol = null then error "Required column not found: Incident (tried: Incident, Incident Type, IncidentType)"
        else if TimeCol = null then error "Required column not found: Time (tried: Time of Call, TimeOfCall, CallTime, Time)"
        else true,
    
    // Rename columns to standard names
    Renamed = Table.RenameColumns(
        Promoted,
        {
            {DispatcherCol, "DispatcherNew"},
            {IncidentCol, "Incident"},
            {TimeCol, "Time of Call"}
        }
    ),

    // =========================
    // Normalize DispatcherNew to lowercase
    // =========================
    LowercaseDispatcher = Table.TransformColumns(
        Renamed,
        {{"DispatcherNew", each if _ = null then null else Text.Lower(Text.Trim(_)), type text}}
    ),

    // =========================
    // Filter to valid dispatchers only
    // =========================
    FilteredDispatchers = Table.SelectRows(
        LowercaseDispatcher,
        each [DispatcherNew] <> null and List.Contains(ValidDispatchers, [DispatcherNew])
    ),

    // =========================
    // Normalize Incident column
    // =========================
    NormalizedIncident = Table.AddColumn(
        FilteredDispatchers,
        "Incident_Normalized",
        each 
            let 
                incident = if [Incident] = null then "" else Text.Trim([Incident]),
                normalized = Text.Lower(Text.Replace(Text.Replace(incident, "  ", " "), " - ", " - ")),
                matched = List.First(
                    List.Select(
                        ValidIncidents,
                        each Text.Lower(Text.Replace(Text.Replace(_, "  ", " "), " - ", " - ")) = normalized
                    ),
                    null
                )
            in
                if matched <> null then matched else "Other",
        type text
    ),

    FilteredIncidents = NormalizedIncident,

    // =========================
    // Extract month from "Time of Call"
    // =========================
    WithDate = Table.AddColumn(
        FilteredIncidents,
        "CallDate",
        each 
            let 
                timeOfCall = [#"Time of Call"],
                dateTimeValue = try DateTime.FromText(Text.From(timeOfCall)) otherwise null,
                dateValue = if dateTimeValue <> null then Date.From(dateTimeValue) else null
            in
                dateValue,
        type date
    ),

    // =========================
    // Calculate rolling 13-month window
    // =========================
    NowDT = DateTime.From(ReportMonth),
    CurrY = Date.Year(NowDT),
    CurrM = Date.Month(NowDT),
    EndY = if CurrM = 1 then CurrY - 1 else CurrY,
    EndM = if CurrM = 1 then 12 else CurrM - 1,
    
    EndDate = #date(EndY, EndM, 1),
    StartDate = Date.AddMonths(EndDate, -12),
    
    MonthList = List.Generate(
        () => StartDate,
        each _ <= EndDate,
        each Date.AddMonths(_, 1)
    ),
    
    PeriodLabelsMMYY = List.Transform(
        MonthList,
        each Text.PadStart(Text.From(Date.Month(_)), 2, "0") & "-" & Text.End(Text.From(Date.Year(_)), 2)
    ),

    // =========================
    // Add Period (MM-YY) column
    // =========================
    WithPeriod = Table.AddColumn(
        WithDate,
        "Period",
        each 
            if [CallDate] <> null then
                let 
                    y = Date.Year([CallDate]),
                    m = Date.Month([CallDate]),
                    period = Text.PadStart(Text.From(m), 2, "0") & "-" & Text.End(Text.From(y), 2)
                in
                    period
            else
                null,
        type text
    ),

    FilteredPeriod = Table.SelectRows(
        WithPeriod,
        each [Period] <> null and List.Contains(PeriodLabelsMMYY, [Period])
    ),

    // =========================
    // Group and count
    // =========================
    Grouped = Table.Group(
        FilteredPeriod,
        {"DispatcherNew", "Incident_Normalized", "Period"},
        {{"Count", each Table.RowCount(_), type number}}
    ),

    // =========================
    // Create all combinations
    // =========================
    AllDispatchers = Table.FromList(ValidDispatchers, Splitter.SplitByNothing(), {"DispatcherNew"}),
    AllIncidents = Table.FromList(List.Combine({ValidIncidents, {"Other"}}), Splitter.SplitByNothing(), {"Incident"}),
    AllPeriods = Table.FromList(PeriodLabelsMMYY, Splitter.SplitByNothing(), {"Period"}),

    AllCombinations_Step1 = Table.AddColumn(AllDispatchers, "IncidentTable", each AllIncidents),
    AllCombinations_Step2 = Table.ExpandTableColumn(AllCombinations_Step1, "IncidentTable", {"Incident"}, {"Incident"}),
    AllCombinations_Step3 = Table.AddColumn(AllCombinations_Step2, "PeriodTable", each AllPeriods),
    AllCombinations = Table.ExpandTableColumn(AllCombinations_Step3, "PeriodTable", {"Period"}, {"Period"}),

    AllCombinationsWithSort = Table.AddColumn(
        AllCombinations,
        "Month_Sort",
        each 
            let 
                mm = Number.FromText(Text.Start([Period], 2)),
                yy = Number.FromText(Text.End([Period], 2)),
                yyyy = if yy < 70 then 2000 + yy else 1900 + yy
            in
                yyyy * 100 + mm,
        Int64.Type
    ),

    AllCombinationsRenamed = Table.RenameColumns(AllCombinationsWithSort, {{"Period", "Month"}}),

    // =========================
    // Join and fill zeros
    // =========================
    GroupedRenamed = Table.RenameColumns(
        Grouped,
        {{"Incident_Normalized", "Incident"}, {"Period", "Month"}}
    ),

    Joined = Table.NestedJoin(
        AllCombinationsRenamed,
        {"DispatcherNew", "Incident", "Month"},
        GroupedRenamed,
        {"DispatcherNew", "Incident", "Month"},
        "GroupedData",
        JoinKind.LeftOuter
    ),

    Expanded = Table.ExpandTableColumn(Joined, "GroupedData", {"Count"}, {"Count"}),
    WithZeros = Table.ReplaceValue(Expanded, null, 0, Replacer.ReplaceValue, {"Count"}),

    // =========================
    // Final formatting
    // =========================
    Reordered = Table.ReorderColumns(
        WithZeros,
        {"DispatcherNew", "Incident", "Month", "Month_Sort", "Count"}
    ),

    Typed = Table.TransformColumnTypes(
        Reordered,
        {
            {"DispatcherNew", type text},
            {"Incident", type text},
            {"Month", type text},
            {"Month_Sort", Int64.Type},
            {"Count", type number}
        }
    )

in
    Typed
