// # drone/DFR_Summons.m
// # Author: R. A. Carucci
// # Purpose: Load DFR_Summons table from dfr_directed_patrol_enforcement.xlsx
// #          Apply rolling 13-month window driven by pReportMonth parameter.
// #          Standardize column names, types; add DateSortKey, Date_Sort_Key, MM-YY, YearMonthKey.
// #          Description: shorten "Parking...designated X" -> "X"; source is ALL CAPS from Excel.
// #          Filter out summons marked Dismiss/Void in Summons_Recall or Summons_Status.
// # Violation_Type/Violation_Category (from Excel): P=Parking/Reg/Equipment/Fire, M=Moving (reserved), C=Complaint (Parks & Rec)
// # Source: C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Drone\dfr_directed_patrol_enforcement.xlsx
// # Last updated: 2026-03-20 (schema-resilient Violation_Category, Jurisdiction; dual filter Text.Contains)
let
    // === PARAMETERS ===
    ReportMonth = Date.From(pReportMonth),
    EndDate = Date.EndOfMonth(ReportMonth),
    StartDate = Date.StartOfMonth(Date.AddMonths(ReportMonth, -12)),

    // === SOURCE: Load Excel workbook ===
    FilePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Drone\dfr_directed_patrol_enforcement.xlsx",
    Source = Excel.Workbook(File.Contents(FilePath), null, true),

    // === TABLE/SHEET FALLBACK: Try named Table first, then Sheet ===
    RawData =
        let
            TableResult = try Source{[Item = "DFR_Summons", Kind = "Table"]}[Data]
        in
            if TableResult[HasError] then
                let
                    SheetData = Source{[Name = "DFR Summons Log", Kind = "Sheet"]}[Data]
                in
                    Table.PromoteHeaders(SheetData, [PromoteAllScalars = true])
            else
                TableResult[Value],

    // === RENAME COLUMNS: Standardize spaces to underscores (schema-resilient: Violation_Type or Violation_Category, Jurisdiction) ===
    RenameMap = {
        {"Summons ID", "Summons_ID"},
        {"Summons Number", "Summons_Number"},
        {"Fine Amount", "Fine_Amount"},
        {"Source Type", "Source_Type"},
        {"Violation Type", "Violation_Type"},
        {"Violation Category", "Violation_Category"},
        {"DFR Operator", "DFR_Operator"},
        {"Issuing Officer", "Issuing_Officer"},
        {"Summons Status", "Summons_Status"},
        {"DFR Unit ID", "DFR_Unit_ID"},
        {"Summons Recall", "Summons_Recall"},
        {"Full Summons Number", "Full_Summons_Number"},
        {"Jurisdiction", "Jurisdiction"}
    },
    ExistingColsForRename = Table.ColumnNames(RawData),
    FilteredRenames = List.Select(RenameMap, each List.Contains(ExistingColsForRename, _{0})),
    RenamedCols = Table.RenameColumns(RawData, FilteredRenames),

    /* === SCHEMA-RESILIENT TYPE MAPPING (en-US; Date parsed defensively per row) === */
    ExistingCols = Table.ColumnNames(RenamedCols),

    /* Apply all non-Date types via bulk coercion (safe — all text/number) */
    NonDateTypeMap = {
        {"Summons_ID", type text},
        {"Time", type text},
        {"Summons_Number", type text},
        {"Location", type text},
        {"Statute", type text},
        {"Description", type text},
        {"Fine_Amount", type number},
        {"Source_Type", type text},
        {"Violation_Type", type text},
        {"Violation_Category", type text},
        {"DFR_Operator", type text},
        {"Issuing_Officer", type text},
        {"Summons_Status", type text},
        {"DFR_Unit_ID", type text},
        {"Notes", type text},
        {"OCA", type text},
        {"Summons_Recall", type text},
        {"Full_Summons_Number", type text},
        {"Jurisdiction", type text}
    },
    FilteredNonDateTypes = List.Select(NonDateTypeMap, each List.Contains(ExistingCols, _{0})),
    TypedNonDate = Table.TransformColumnTypes(RenamedCols, FilteredNonDateTypes, "en-US"),

    /* Parse Date column defensively: try/otherwise null prevents DataFormat.Error on bad rows */
    ChangedType = if List.Contains(ExistingCols, "Date") then
        Table.TransformColumns(TypedNonDate, {
            {"Date", each
                if _ = null or _ = "" then null
                else if _ is date then _
                else if _ is datetime then Date.From(_)
                else if _ is number then Date.AddDays(#date(1899, 12, 30), Number.From(_))
                else try Date.FromText(Text.From(_), [Format="M/d/yyyy", Culture="en-US"])
                     otherwise try Date.From(_)
                     otherwise null,
            type date}
        })
    else TypedNonDate,

    // === CLEAN: Replace null Fine_Amount with 0 for DAX compatibility ===
    CleanedFines =
        if List.Contains(ExistingCols, "Fine_Amount") then
            Table.ReplaceValue(ChangedType, null, 0, Replacer.ReplaceValue, {"Fine_Amount"})
        else
            ChangedType,

    // === FILTER: Remove rows with no Date (empty formula rows in Excel table) ===
    FilteredBlanks = Table.SelectRows(CleanedFines, each [Date] <> null),

    // === FILTER: Exclude Voided or Dismissed summons (Summons_Recall contains "Dismiss" or "Void") ===
    FilteredRecalls =
        if List.Contains(Table.ColumnNames(FilteredBlanks), "Summons_Recall") then
            Table.SelectRows(FilteredBlanks, each
                let recall = [Summons_Recall] in
                recall = null or recall = ""
                or (not Text.Contains(Text.Lower(recall), "dismiss") and not Text.Contains(Text.Lower(recall), "void"))
            )
        else
            FilteredBlanks,

    // === FILTER: Exclude Dismissed/Void/Voided status (Summons_Status; Text.Contains catches all variants) ===
    FilteredStatus =
        if List.Contains(Table.ColumnNames(FilteredRecalls), "Summons_Status") then
            Table.SelectRows(FilteredRecalls, each
                let status = [Summons_Status],
                    cleaned = Text.Trim(Text.Lower(status ?? ""))
                in
                status = null or status = ""
                or (not Text.Contains(cleaned, "dismiss") and not Text.Contains(cleaned, "void"))
            )
        else
            FilteredRecalls,

    // === FILTER: Rolling 13-month window (report month + 12 months prior) ===
    FilteredData = Table.SelectRows(FilteredStatus, each [Date] >= StartDate and [Date] <= EndDate),

    // === STANDARDIZE: Shorten "Parking or stopping in designated X" -> "X" (source is ALL CAPS from Excel) ===
    ShortenPrefix = "Parking or stopping in designated ",
    ShortenedDescription = Table.TransformColumns(FilteredData, {
        {"Description", each
            if _ = null or _ = "" then _
            else if Text.StartsWith(Text.Lower(_), Text.Lower(ShortenPrefix)) then
                Text.Upper(Text.Middle(_, Text.Length(ShortenPrefix)))
            else Text.Upper(_),
        type text}
    }),

    // === ADD: DateSortKey (YYYYMMDD integer, e.g., 20260316) for row-level sorting ===
    AddedDateSortKey = Table.AddColumn(ShortenedDescription, "DateSortKey",
        each Date.Year([Date]) * 10000 + Date.Month([Date]) * 100 + Date.Day([Date]), Int64.Type),

    // === ADD: Date_Sort_Key (first of month) for MM-YY column sort-by in Power BI ===
    AddedDateSortKeyCol = Table.AddColumn(AddedDateSortKey, "Date_Sort_Key", each Date.StartOfMonth([Date]), type date),

    // === ADD: MM-YY (text, e.g., "03-26") for matrix column display; sorts by Date_Sort_Key ===
    AddedMMYY = Table.AddColumn(AddedDateSortKeyCol, "MM-YY",
        each Text.PadStart(Text.From(Date.Month([Date])), 2, "0") & "-" & Text.End(Text.From(Date.Year([Date])), 2),
        type text),

    // === ADD: YearMonthKey (e.g., 202603) for grouping/trending; backward compat for visuals ===
    AddedYearMonthKey = Table.AddColumn(AddedMMYY, "YearMonthKey",
        each Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type),

    // === SELECT: Final column order (schema-resilient: Violation_Type or Violation_Category, Jurisdiction) ===
    FinalColumns = Table.SelectColumns(
        AddedYearMonthKey,
        List.Select(
            {
                "Summons_ID",
                "Date",
                "DateSortKey",
                "Date_Sort_Key",
                "MM-YY",
                "Time",
                "Summons_Number",
                "Location",
                "Statute",
                "Description",
                "Fine_Amount",
                "Source_Type",
                "Violation_Type",
                "Violation_Category",
                "Jurisdiction",
                "DFR_Operator",
                "Issuing_Officer",
                "Summons_Status",
                "DFR_Unit_ID",
                "Notes",
                "OCA",
                "Summons_Recall",
                "Full_Summons_Number",
                "YearMonthKey"
            },
            each List.Contains(Table.ColumnNames(AddedYearMonthKey), _)
        )
    )
in
    FinalColumns
