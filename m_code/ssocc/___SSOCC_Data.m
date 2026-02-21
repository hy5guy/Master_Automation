// 🕒 2026-02-20-23-48-50
// # ssocc/___SSOCC_Data.m
// # Author: R. A. Carucci
// # Purpose: Load SSOCC dispatch and alert data with multi-sheet workbook handling.

let
    // =================================================================
    // STEP 1: SOURCE
    // =================================================================
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\SSOCC\Archive\_SSOCC - Service Log.xlsx"),
        null,
        true
    ),

    // =================================================================
    // STEP 2: HELPERS
    // =================================================================
    MonthMap = [
        Jan = 1, Feb = 2, Mar = 3, Apr = 4, May = 5, Jun = 6,
        Jul = 7, Aug = 8, Sep = 9, Oct = 10, Nov = 11, Dec = 12
    ],

    IsMonthColumn = (c as text) as logical =>
        let
            t = Text.Trim(c),
            parts = Text.Split(t, "-"),
            ok =
                List.Count(parts) = 2 and
                (try Number.FromText(Text.Trim(parts{0})) otherwise null) <> null and
                (
                    (try Record.Field(MonthMap, Text.Proper(Text.Start(Text.Trim(parts{1}), 3))) otherwise null) <> null
                    or
                    (try Number.FromText(Text.Trim(parts{1})) otherwise null) <> null
                )
        in
            ok,

    ParsePeriodToDate = (p as nullable text) as nullable date =>
        let
            raw = if p = null then null else Text.Trim(p),
            parts = if raw = null then {
} else Text.Split(raw, "-"),
            d =
                if List.Count(parts) <> 2 then
                    null
                else
                    let
                        aTxt = Text.Trim(parts{0}),
                        bTxt = Text.Trim(parts{1}),
                        aNum = try Number.FromText(aTxt) otherwise null,
                        bNum = try Number.FromText(bTxt) otherwise null,

                        d1 =
                            if aNum <> null and aNum <= 12 and bNum <> null then
#date(2000 + bNum, aNum, 1)
                            else
                                null,

                        d2 =
                            if d1 = null and aNum <> null then
                                let
                                    monKey = Text.Proper(Text.Start(bTxt, 3)),
                                    monNum = try Record.Field(MonthMap, monKey) otherwise null
                                in
                                    if monNum <> null then #date(2000 + aNum, monNum, 1) else null
                            else
                                null
                    in
                        if d1 <> null then d1 else d2
        in
            d,

    EnsureText = (x as any) as text =>
        Text.Trim(Text.From(x)),

    EnsureInt64 = (x as any) as number =>
        let
            n = try Number.From(x) otherwise null
        in
            if n = null then 0 else Int64.From(n),

    StandardizeMoMTable = (tableName as text, sourceLabel as text) as table =>
        let
            Raw = try Source{[Item = tableName, Kind = "Table"]}[Data] otherwise null,
            Output =
                if Raw = null or Table.ColumnCount(Raw) = 0 then
#table(
                        {"Service/Product", "Service_Normalized", "Source_Table"},
                        {}
                    )
                else
                    let
                        Cols = Table.ColumnNames(Raw),

                        ServiceCol = Cols{0},

                        HasNorm = List.Contains(Cols, "ServiceName_Normalized"),
                        NormCol =
                            if HasNorm then
                                "ServiceName_Normalized"
                            else if List.Count(Cols) >= 2 then
                                Cols{1}
                            else
                                null,

                        MonthCols = List.Select(Cols, each IsMonthColumn(_)),

                        KeepCols =
                            if NormCol <> null then
                                List.Combine({{ServiceCol, NormCol}, MonthCols})
                            else
                                List.Combine({{ServiceCol}, MonthCols}),

                        Kept = Table.SelectColumns(Raw, KeepCols, MissingField.UseNull),

                        Renamed1 = Table.RenameColumns(Kept, {{ServiceCol, "Service/Product"}}, MissingField.Ignore),
                        Renamed2 =
                            if NormCol <> null then
                                Table.RenameColumns(Renamed1, {{NormCol, "Service_Normalized"}}, MissingField.Ignore)
                            else
                                Table.AddColumn(Renamed1, "Service_Normalized", each null, type text),

                        CleanTextCols = Table.TransformColumns(
                            Renamed2,
                            {
                                {"Service/Product", each EnsureText(_), type text},
                                {"Service_Normalized", each if _ = null then null else EnsureText(_), type text}
                            },
                            null,
                            MissingField.UseNull
                        ),

                        MonthTyped = Table.TransformColumns(
                            CleanTextCols,
                            List.Transform(MonthCols, each {_, each EnsureInt64(_), Int64.Type}),
                            null,
                            MissingField.UseNull
                        ),

                        Tagged = Table.AddColumn(MonthTyped, "Source_Table", each sourceLabel, type text)
                    in
                        Tagged
        in
            Output,

    // =================================================================
    // STEP 3: LOAD + STANDARDIZE TABLES
    // =================================================================
    T_ANALYSIS = StandardizeMoMTable("_ANALYSIS", "Priority Services"),
    T_TRAIN    = StandardizeMoMTable("_TRAIN",    "Training & Education"),
    T_SUR      = StandardizeMoMTable("_SUR",      "Technical Services"),
    T_MAIN     = StandardizeMoMTable("_MAIN",     "Support Services"),
    T_MEET     = StandardizeMoMTable("_MEET",     "Operational Services"),
    T_ADMIN    = StandardizeMoMTable("_ADMIN",    "Administrative Services"),

    CombinedTables = Table.Combine({T_ANALYSIS, T_TRAIN, T_SUR, T_MAIN, T_MEET, T_ADMIN}),

    // =================================================================
    // STEP 4: PRIORITY FLAG + CATEGORY
    // =================================================================
    PrioritySet = {
        "ANALYSIS FOR DETECTIVES",
        "ANALYSIS - DETECTIVES",
        "ANALYSIS FOR PATROL",
        "ANALYSIS - PATROL",
        "AVIGILON FLAG REVIEW",
        "CCTV SITE ANALYSIS",
        "ANALYSIS FOR CSB",
        "ANALYSIS - CSB"
    },

    AddedPriorityFlag = Table.AddColumn(
        CombinedTables,
        "Is_Priority_Service",
        each
            let
                svc  = Text.Upper(EnsureText([#"Service/Product"])),
                norm = if [Service_Normalized] = null then "" else Text.Upper(EnsureText([Service_Normalized]))
            in
                List.Contains(PrioritySet, svc) or List.Contains(PrioritySet, norm),
        type logical
    ),

    AddedServiceCategoryFinal = Table.AddColumn(
        AddedPriorityFlag,
        "Service_Category_Final",
        each if [Is_Priority_Service] then "Priority Services" else [Source_Table],
        type text
    ),

    AddedEmergencyServices = Table.AddColumn(
        AddedServiceCategoryFinal,
        "Service_Category",
        each
            let
                s = Text.Upper(EnsureText([#"Service/Product"]))
            in
                if Text.Contains(s, "EMERGENCY") or Text.Contains(s, "911") then "Emergency Services"
                else [Service_Category_Final],
        type text
    ),

    CleanedColumns = Table.RemoveColumns(AddedEmergencyServices, {"Service_Category_Final"}),

    // =================================================================
    // STEP 5: UNPIVOT
    // =================================================================
    UnpivotedData = Table.UnpivotOtherColumns(
        CleanedColumns,
        {"Service/Product", "Service_Normalized", "Source_Table", "Is_Priority_Service", "Service_Category"},
        "Period",
        "Value"
    ),

    // =================================================================
    // STEP 6: DATE + SORT KEYS
    // =================================================================
    AddedDate = Table.AddColumn(
        UnpivotedData,
        "Date",
        each ParsePeriodToDate([Period]),
        type date
    ),

    AddedMonthSort = Table.AddColumn(
        AddedDate,
        "Month_Sort_Order",
        each if [Date] = null then null else (Date.Year([Date]) * 100 + Date.Month([Date])),
        Int64.Type
    ),

    AddedFormattedDate = Table.AddColumn(
        AddedMonthSort,
        "Formatted_Date",
        each if [Date] = null then null else Date.ToText([Date], "MM-yy"),
        type text
    ),

    ValueFixed = Table.TransformColumns(
        AddedFormattedDate,
        {{"Value", each EnsureInt64(_), Int64.Type}},
        null,
        MissingField.UseNull
    ),

    // =================================================================
    // STEP 7: FINAL METADATA + TYPES
    // =================================================================
    AddedCategory   = Table.AddColumn(ValueFixed, "Category", each "SSOCC Services", type text),
    AddedDepartment = Table.AddColumn(AddedCategory, "Department", each "Police Department", type text),
    AddedUnit       = Table.AddColumn(AddedDepartment, "Unit", each "SSOCC", type text),

    SortedData = Table.Sort(
        AddedUnit,
        {
            {"Is_Priority_Service", Order.Descending},
            {"Service_Category", Order.Ascending},
            {"Month_Sort_Order", Order.Ascending},
            {"Service/Product", Order.Ascending}
        }
    ),

    FinalDataTypes = Table.TransformColumnTypes(
        SortedData,
        {
            {"Service/Product", type text},
            {"Service_Normalized", type text},
            {"Source_Table", type text},
            {"Is_Priority_Service", type logical},
            {"Service_Category", type text},
            {"Period", type text},
            {"Value", Int64.Type},
            {"Date", type date},
            {"Month_Sort_Order", Int64.Type},
            {"Formatted_Date", type text},
            {"Category", type text},
            {"Department", type text},
            {"Unit", type text}
        }
    ),
#"Sorted Rows" = Table.Sort(FinalDataTypes, {{"Period", Order.Ascending } }),
#"Filtered Rows" = Table.SelectRows(#"Sorted Rows", each true)
in
#"Filtered Rows"
