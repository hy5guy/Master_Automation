// # drone/DFR_Summons.m
// # Author: R. A. Carucci
// # Purpose: Load DFR directed-patrol enforcement summons from dfr_directed_patrol_enforcement.xlsx.
// #          Rolling 13-month window driven by pReportMonth.
// #          Dual filter: excludes rows dismissed or voided via Summons_Recall OR Summons_Status.
// #          Adds YearMonthKey, MM-YY (Month_Year), Date_Sort_Key, and shortened Description.
// # Version: v1.18.14 — FilteredStatus step added (catches Dismissed, Void, Voided variants)
// # Last updated: 2026-03-20

let
    ReportMonth = pReportMonth,
    EndDate   = Date.EndOfMonth(Date.From(ReportMonth)),
    StartDate = Date.StartOfMonth(Date.AddMonths(Date.From(ReportMonth), -12)),

    // ----------------------------------------------------------------
    // Load workbook — try named Table first, fall back to sheet
    // ----------------------------------------------------------------
    Source = Excel.Workbook(
        File.Contents(
            "C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Drone\dfr_directed_patrol_enforcement.xlsx"
        ),
        null,
        true
    ),
    RawData = try Source{[Item = "DFR_Summons", Kind = "Table"]}[Data]
        otherwise Table.PromoteHeaders(
            Source{[Name = "DFR Summons Log", Kind = "Sheet"]}[Data],
            [PromoteAllScalars = true]
        ),

    // Promote headers only when using sheet path (Table path already has them)
    Promoted = if Table.HasColumns(RawData, {"Column1"})
        then Table.PromoteHeaders(RawData, [PromoteAllScalars = true])
        else RawData,

    // ----------------------------------------------------------------
    // Schema-resilient column renames
    // ----------------------------------------------------------------
    ExistingCols = Table.ColumnNames(Promoted),
    RenameMap = {
        {"Summons Number", "Summons_Number"},
        {"Full Summons Number", "Full_Summons_Number"},
        {"DFR Operator", "DFR_Operator"},
        {"Issuing Officer", "Issuing_Officer"},
        {"Summons Status", "Summons_Status"},
        {"Summons Recall", "Summons_Recall"},
        {"Fine Amount", "Fine_Amount"},
        {"Violation Type", "Violation_Type"},
        {"DFR Unit ID", "DFR_Unit_ID"}
    },
    FilteredRenames = List.Select(RenameMap, each List.Contains(ExistingCols, _{0})),
    Renamed = Table.RenameColumns(Promoted, FilteredRenames, MissingField.Ignore),

    // ----------------------------------------------------------------
    // Type mapping (schema-resilient: only transform columns present)
    // ----------------------------------------------------------------
    TypeMap = {
        {"Date",            type date},
        {"Time",            type text},
        {"Summons_Number",  type text},
        {"Location",        type text},
        {"Statute",         type text},
        {"Description",     type text},
        {"Fine_Amount",     type number},
        {"Violation_Type",  type text},
        {"DFR_Operator",    type text},
        {"Issuing_Officer", type text},
        {"Summons_Status",  type text},
        {"Summons_Recall",  type text},
        {"OCA",             type text},
        {"Notes",           type text},
        {"Full_Summons_Number", type text}
    },
    ExistingCols2 = Table.ColumnNames(Renamed),
    FilteredTypes = List.Select(TypeMap, each List.Contains(ExistingCols2, _{0})),
    ChangedType = Table.TransformColumnTypes(Renamed, FilteredTypes, "en-US"),

    // ----------------------------------------------------------------
    // Replace null Fine Amount with 0 for DAX compatibility
    // ----------------------------------------------------------------
    WithFineAmount = if Table.HasColumns(ChangedType, "Fine_Amount")
        then Table.ReplaceValue(ChangedType, null, 0, Replacer.ReplaceValue, {"Fine_Amount"})
        else ChangedType,

    // ----------------------------------------------------------------
    // Filter blank rows (no date and no summons number)
    // ----------------------------------------------------------------
    FilteredBlanks = Table.SelectRows(
        WithFineAmount,
        each not (
            ([Date] = null or [Date] = "")
            and ([Summons_Number] = null or [Summons_Number] = "")
        )
    ),

    // ----------------------------------------------------------------
    // Dual dismiss/void filter
    // Step 1 — FilteredRecalls: Summons_Recall column
    // ----------------------------------------------------------------
    FilteredRecalls = if Table.HasColumns(FilteredBlanks, "Summons_Recall")
        then Table.SelectRows(
            FilteredBlanks,
            each
                let recall = Text.Trim(Text.Lower([Summons_Recall] ?? ""))
                in not (Text.Contains(recall, "dismiss") or Text.Contains(recall, "void"))
        )
        else FilteredBlanks,

    // ----------------------------------------------------------------
    // Step 2 — FilteredStatus: Summons_Status column
    // Catches "Dismissed", "Void", "Voided" and similar variants.
    // Null-safe: uses ?? "" before Text.Lower/Trim.
    // ----------------------------------------------------------------
    FilteredStatus = if Table.HasColumns(FilteredRecalls, "Summons_Status")
        then Table.SelectRows(
            FilteredRecalls,
            each
                let status = Text.Trim(Text.Lower([Summons_Status] ?? ""))
                in not (Text.Contains(status, "dismiss") or Text.Contains(status, "void"))
        )
        else FilteredRecalls,

    // ----------------------------------------------------------------
    // 13-month rolling window filter
    // ----------------------------------------------------------------
    FilteredData = Table.SelectRows(
        FilteredStatus,
        each
            [Date] <> null
            and Date.From([Date]) >= StartDate
            and Date.From([Date]) <= EndDate
    ),

    // ----------------------------------------------------------------
    // Shorten Description: strip verbose parking prefix for cleaner labels
    // e.g. "PARKING OR STOPPING IN DESIGNATED FIRE LANE/FIRE ZONE" → "FIRE LANE/FIRE ZONE"
    // ----------------------------------------------------------------
    ShortenedDescription = if Table.HasColumns(FilteredData, "Description")
        then Table.TransformColumns(
            FilteredData,
            {
                {
                    "Description",
                    each
                        let
                            raw    = Text.Upper(Text.Trim(_ ?? "")),
                            prefix = "PARKING OR STOPPING IN DESIGNATED "
                        in
                            if Text.StartsWith(raw, prefix)
                            then Text.Middle(raw, Text.Length(prefix))
                            else raw,
                    type text
                }
            }
        )
        else FilteredData,

    // ----------------------------------------------------------------
    // Derived columns for trending and matrix sort
    // ----------------------------------------------------------------
    // Date_Sort_Key: YYYYMMDD integer — drives chronological sort on matrix columns
    AddedDateSortKey = Table.AddColumn(
        ShortenedDescription,
        "Date_Sort_Key",
        each
            if [Date] <> null
            then Date.Year([Date]) * 10000 + Date.Month([Date]) * 100 + Date.Day([Date])
            else null,
        Int64.Type
    ),

    // MM-YY formatted label (Month_Year) — matches format used in main Summons tables
    AddedDateFormatted = Table.AddColumn(
        AddedDateSortKey,
        "Month_Year",
        each
            if [Date] <> null
            then
                Text.PadStart(Text.From(Date.Month([Date])), 2, "0")
                & "-"
                & Text.End(Text.From(Date.Year([Date])), 2)
            else null,
        type text
    ),

    // YearMonthKey: YYYYMM integer — links to ___DimMonth for cross-filtering
    AddedYearMonthKey = Table.AddColumn(
        AddedDateFormatted,
        "YearMonthKey",
        each
            if [Date] <> null
            then Date.Year([Date]) * 100 + Date.Month([Date])
            else null,
        Int64.Type
    )

in
    AddedYearMonthKey
