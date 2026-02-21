// 🕒 2026-02-21-01-00-00 (EST)
// # detectives/___Detectives.m
// # Author: R. A. Carucci
// # Purpose: Load Detective Division monthly activity from workbook with rolling 13-month window.

let
    ReportMonth = pReportMonth,
    // =================================================================
    // FILE PATH AND TABLE LOAD
    // =================================================================
    FilePath =
        "C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Detectives\detectives_monthly.xlsx",

    Source = Excel.Workbook(File.Contents(FilePath), null, true),

    // Load _mom_det table (now contains 01-26 through 12-26 only)
    MoM_Det_Table = Source{[Item = "_mom_det", Kind = "Table"]}[Data],

    DetectedTypes = Table.TransformColumnTypes(MoM_Det_Table, {}, "en-US"),

    // =================================================================
    // DATA CLEANING
    // =================================================================
    // Remove completely empty rows
    RemovedEmptyRows = Table.SelectRows(
        DetectedTypes, each not List.IsEmpty(List.RemoveMatchingItems(
                           Record.FieldValues(_), {"", null}))),

    ColumnNames = Table.ColumnNames(RemovedEmptyRows),
    FirstColumn = ColumnNames{0},

    // Filter to rows with at least one month having activity > 0
    FilteredToActiveCases = Table.SelectRows(
        RemovedEmptyRows, each let CategoryName = Record.Field(_, FirstColumn),
        RowValues = List.Skip(Record.FieldValues(_), 1),
        HasActivity = List.AnyTrue(List.Transform(
            RowValues, each try(_ <> null and _ <> "" and Number.From(_) > 0)
                           otherwise false)) in HasActivity),

    // =================================================================
    // UNPIVOT TO LONG FORMAT
    // =================================================================
    UnpivotedData = Table.UnpivotOtherColumns(
        FilteredToActiveCases, {FirstColumn}, "Month_MM_YY", "Value"),

    // =================================================================
    // DATE PARSING AND SORT ORDER
    // =================================================================
    // Parse MM-YY format (e.g., "01-26") to proper date
    AddedDateInfo = Table.AddColumn(
        UnpivotedData, "Date", each let MonthText = [Month_MM_YY],
        Parts = Text.Split(MonthText, "-"),
        // Parts{0} = MM (month), Parts{1} = YY (year)
        MonthPart = if List.Count(Parts) >= 1 then Parts{0} else "01",
        YearPart = if List.Count(Parts) >= 2 then Parts{1} else "26",

        // Convert 2-digit year to full year
        YearNum = try Number.From(YearPart) otherwise null,
        FullYear = if YearNum = null then null else if YearNum >=
                                50 then 1900 + YearNum else 2000 + YearNum,

        // Convert month to number (01=1, 02=2, etc.)
        MonthNum = try Number.From(MonthPart) otherwise null,

        DateValue = if MonthNum =
            null or FullYear =
                null then null else try #date(FullYear, MonthNum, 1)
                    otherwise null in DateValue,
        type date),

    // Add normalized Month_Normalized column in MM-YY format
    AddedNormalizedMonth = Table.AddColumn(
        AddedDateInfo, "Month_Normalized",
        each if[Date]<> null then Text.PadStart(Text.From(Date.Month([Date])),
                                                2, "0") &
            "-" & Text.End(Text.From(Date.Year([Date])), 2) else[Month_MM_YY],
        type text),

    // Remove old Month_MM_YY and rename Month_Normalized to Month_MM_YY
    RemovedOldMonth =
        Table.RemoveColumns(AddedNormalizedMonth, {"Month_MM_YY"}),
    RenamedMonth = Table.RenameColumns(RemovedOldMonth,
                                       {{"Month_Normalized", "Month_MM_YY"}}),

    // Create numeric sort order (YYYYMM format)
    AddedSortOrder =
        Table.AddColumn(RenamedMonth, "Month_Sort_Order",
                        each if[Date]<> null then Date.Year([Date]) * 100 +
                            Date.Month([Date]) else null,
                        Int64.Type),

    // =================================================================
    // ROLLING 13-MONTH WINDOW LOGIC (WORKS WITH HISTORICAL DATA)
    // =================================================================
    // Table contains historical data from Jun 2023 onwards
    // Show rolling 13 months ending with the previous complete month

    CurrentDate = DateTime.From(ReportMonth),
    CurrentMonthStart = Date.StartOfMonth(Date.From(CurrentDate)),

    // End date = previous month (complete data only)
    EndFilterDate = Date.AddMonths(CurrentMonthStart, -1),

    // Start date = 13 months before end date (rolling 13-month window)
    StartFilterDate = Date.AddMonths(EndFilterDate, -12),

    // Format reporting period for display
    ReportingPeriod = Date.ToText(StartFilterDate, "MM/yy") & " - " &
                      Date.ToText(EndFilterDate, "MM/yy"),

    // Apply date range filter (show all 2026 data up to previous month)
    FilteredMonths = Table.SelectRows(
        AddedSortOrder, each[Date]<> null and[Date] >=
                            StartFilterDate and[Date] <= EndFilterDate),

    // =================================================================
    // METADATA COLUMNS
    // =================================================================
    // Add reporting period metadata
    AddedReportingMeta = Table.AddColumn(FilteredMonths, "ReportingPeriod",
                                         each ReportingPeriod, type text),

    // Calculate number of unique months in the filtered dataset
    UniqueMonthsCount = Table.RowCount(
        Table.Group(FilteredMonths, {"Date"},
                    {{"Count", each Table.RowCount(_), type number}})),

    // Add month count to all rows
    AddedMonthCount = Table.AddColumn(AddedReportingMeta, "MonthsIncluded",
                                      each UniqueMonthsCount, type number),

    // Classify cases as High Impact or Administrative
    AddedCaseType = Table.AddColumn(
        AddedMonthCount, "Case_Type",
        each let CategoryName = Record.Field(_, FirstColumn),
        HighImpactCategories = {"ABC Investigation(s)", "Background Check(s)",
                                "Firearm Background Check(s)",
                                "Criminal Mischief", "Fraud",
                                "Generated Complaint(s)", "BWC Review(s)",
                                "Aggravated Assault", "Animal Cruelty",
                                "Burglary - Auto", "Domestic Violence",
                                "Drug Investigation(s)", "Harassment",
                                "Motor Vehicle Theft"},
        CaseType = if List.Contains(HighImpactCategories, CategoryName) then
                   "High Impact" else "Administrative" in CaseType,
        type text),

    // =================================================================
    // FINAL TYPE CONVERSIONS
    // =================================================================
    FinalDataTypes = Table.TransformColumnTypes(
        AddedCaseType, {{FirstColumn, type text},
                        {"Month_MM_YY", type text},
                        {"Value", type number},
                        {"Date", type date},
                        {"Month_Sort_Order", Int64.Type},
                        {"Case_Type", type text}}),

    // =================================================================
    // REPORT TITLE AND SUBTITLE
    // =================================================================
    AddedTitle = Table.AddColumn(
        FinalDataTypes, "ReportTitle",
        each "Detective Division - Comprehensive Case Analysis", type text),

    AddedSubtitle = Table.AddColumn(
        AddedTitle, "ReportSubtitle",
        each let StartMonth = Date.ToText(StartFilterDate, "MMMM yyyy"),
        EndMonth = Date.ToText(EndFilterDate, "MMMM yyyy"),
        RefreshDate =
            DateTime.ToText(DateTime.From(ReportMonth), "MM/dd/yyyy hh:mm tt"),
        TodaysDate =
            Date.ToText(ReportMonth, "MMMM dd, yyyy") in
            "Rolling 13-Month Period: " &
            StartMonth & " - " & EndMonth & " | Today: " & TodaysDate &
            " | Updated: " & RefreshDate,
        type text),

    // Add timestamp for data refresh tracking
    AddedRefreshTime = Table.AddColumn(AddedSubtitle, "DataRefreshTime",
                                       each DateTime.From(ReportMonth), type datetime)

                           in AddedRefreshTime
