// 🕒 2026-02-13-18-00-00
// # Master_Automation/Detectives/___Detectives.m
// # Author: R. A. Carucci
// # Purpose: Import Detective Division cases from restructured 2026-only workbook with rolling 13-month window (01-26 through 12-26).

let
    // =================================================================
    // FILE PATH AND TABLE LOAD
    // =================================================================
    FilePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Detectives\detectives_monthly.xlsx",
    
    Source = Excel.Workbook(File.Contents(FilePath), null, true),
    
    // Load _mom_det table (now contains 01-26 through 12-26 only)
    MoM_Det_Table = Source{[Item = "_mom_det", Kind = "Table"]}[Data],
    
    DetectedTypes = Table.TransformColumnTypes(MoM_Det_Table, {}, "en-US"),
    
    // =================================================================
    // DATA CLEANING
    // =================================================================
    // Remove completely empty rows
    RemovedEmptyRows = Table.SelectRows(DetectedTypes, each 
        not List.IsEmpty(List.RemoveMatchingItems(Record.FieldValues(_), {"", null}))),
    
    ColumnNames = Table.ColumnNames(RemovedEmptyRows),
    FirstColumn = ColumnNames{0},
    
    // Filter to rows with at least one month having activity > 0
    FilteredToActiveCases = Table.SelectRows(RemovedEmptyRows, each 
        let 
            CategoryName = Record.Field(_, FirstColumn),
            RowValues = List.Skip(Record.FieldValues(_), 1),
            HasActivity = List.AnyTrue(List.Transform(RowValues, 
                each try (_ <> null and _ <> "" and Number.From(_) > 0) otherwise false))
        in HasActivity),
    
    // =================================================================
    // UNPIVOT TO LONG FORMAT
    // =================================================================
    UnpivotedData = Table.UnpivotOtherColumns(FilteredToActiveCases, {FirstColumn}, "Month_MM_YY", "Value"),
    
    // =================================================================
    // DATE PARSING AND SORT ORDER
    // =================================================================
    // Parse MM-YY format to proper date
    AddedDateInfo = Table.AddColumn(UnpivotedData, "Date", each 
        let 
            MonthText = [Month_MM_YY],
            Parts = Text.Split(MonthText, "-"),
            MonthNum = if List.Count(Parts) >= 1 then Parts{0} else "01",
            YearNum = if List.Count(Parts) >= 2 then Parts{1} else "26",
            // Assume 50+ = 19xx, else 20xx
            FullYear = if Value.FromText(YearNum) >= 50 then 1900 + Value.FromText(YearNum) else 2000 + Value.FromText(YearNum),
            DateValue = try #date(FullYear, Value.FromText(MonthNum), 1) otherwise null
        in DateValue, 
        type date),
    
    // Create numeric sort order (YYYYMM format)
    AddedSortOrder = Table.AddColumn(AddedDateInfo, "Month_Sort_Order", each 
        if [Date] <> null then Date.Year([Date]) * 100 + Date.Month([Date]) else null, 
        Int64.Type),
    
    // =================================================================
    // ROLLING 13-MONTH WINDOW LOGIC
    // =================================================================
    // Current date and month calculations
    CurrentDate = DateTime.LocalNow(),
    CurrentMonthStart = Date.StartOfMonth(Date.From(CurrentDate)),
    
    // End date = previous month (complete data only)
    EndFilterDate = Date.AddMonths(CurrentMonthStart, -1),
    
    // Start date = 12 months before end date (13 total months)
    StartFilterDate = Date.AddMonths(EndFilterDate, -12),
    
    // Format reporting period for display
    ReportingPeriod = Date.ToText(StartFilterDate, "MM/yy") & " - " & Date.ToText(EndFilterDate, "MM/yy"),
    
    // Apply 13-month rolling window filter
    FilteredMonths = Table.SelectRows(AddedSortOrder, each 
        [Date] <> null and 
        [Date] >= StartFilterDate and 
        [Date] <= EndFilterDate),
    
    // =================================================================
    // METADATA COLUMNS
    // =================================================================
    // Add reporting period metadata
    AddedReportingMeta = Table.AddColumn(FilteredMonths, "ReportingPeriod", each ReportingPeriod, type text),
    
    // Calculate number of months included (should be 13 or less if data incomplete)
    AddedMonthCount = Table.AddColumn(AddedReportingMeta, "MonthsIncluded", each 
        let
            UniqueMonths = Table.Group(FilteredMonths, {"Date"}, 
                {{"Count", each Table.RowCount(_), type number}}),
            MonthCount = Table.RowCount(UniqueMonths)
        in MonthCount, 
        type number),
    
    // Classify cases as High Impact or Administrative
    AddedCaseType = Table.AddColumn(AddedMonthCount, "Case_Type", each 
        let 
            CategoryName = Record.Field(_, FirstColumn),
            HighImpactCategories = {
                "ABC Investigation(s)", 
                "Background Check(s)", 
                "Firearm Background Check(s)", 
                "Criminal Mischief", 
                "Fraud", 
                "Generated Complaint(s)", 
                "BWC Review(s)", 
                "Aggravated Assault", 
                "Animal Cruelty", 
                "Burglary - Auto", 
                "Domestic Violence", 
                "Drug Investigation(s)", 
                "Harassment", 
                "Motor Vehicle Theft"
            },
            CaseType = if List.Contains(HighImpactCategories, CategoryName) 
                       then "High Impact" 
                       else "Administrative"
        in CaseType, 
        type text),
    
    // =================================================================
    // FINAL TYPE CONVERSIONS
    // =================================================================
    FinalDataTypes = Table.TransformColumnTypes(AddedCaseType, {
        {FirstColumn, type text}, 
        {"Month_MM_YY", type text}, 
        {"Value", type number}, 
        {"Date", type date}, 
        {"Month_Sort_Order", Int64.Type}, 
        {"Case_Type", type text}
    }),
    
    // =================================================================
    // REPORT TITLE AND SUBTITLE
    // =================================================================
    AddedTitle = Table.AddColumn(FinalDataTypes, "ReportTitle", each 
        "Detective Division - Comprehensive Case Analysis", 
        type text),
    
    AddedSubtitle = Table.AddColumn(AddedTitle, "ReportSubtitle", each 
        let 
            StartMonth = Date.ToText(StartFilterDate, "MMMM yyyy"),
            EndMonth = Date.ToText(EndFilterDate, "MMMM yyyy"),
            RefreshDate = DateTime.ToText(DateTime.LocalNow(), "MM/dd/yyyy hh:mm tt"),
            TodaysDate = Date.ToText(Date.From(DateTime.LocalNow()), "MMMM dd, yyyy")
        in "Rolling 13-Month Period: " & StartMonth & " - " & EndMonth & 
           " | Today: " & TodaysDate & 
           " | Updated: " & RefreshDate, 
        type text),
    
    // Add timestamp for data refresh tracking
    AddedRefreshTime = Table.AddColumn(AddedSubtitle, "DataRefreshTime", each 
        DateTime.LocalNow(), 
        type datetime)

in 
    AddedRefreshTime
