// 🕒 2026-03-05
// # Master_Automation/m_code/esu/ESU_13Month.m
// # Author: R. A. Carucci
// # Purpose: Single query — load ESU.xlsx monthly Tables only; rolling 13 months.
// # Fixes: Per-table TrackedCol, type number, exclude _Log tables, normalize 1 Man ESU→ESU Single Operator.

let
    ReportMonth = pReportMonth,
    ESUPath = "C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\ESU\ESU.xlsx",

    Source = Excel.Workbook(File.Contents(ESUPath), null, true),

    // Lookup Status and ItemKey from _mom_hacsoc (dimension table)
    MoMRow = try Source{[Name="_mom_hacsoc", Kind="Table"]} otherwise try Source{[Item="_mom_hacsoc", Kind="Table"]} otherwise Source{[Name="_mom_hacsoc", Kind="Sheet"]},
    MoM = MoMRow[Data],
    MoMCols = Table.ColumnNames(MoM),
    MoMTrackedCol = List.First(List.Select(MoMCols, each Text.Trim(Text.Replace(_, Character.FromNumber(160), " ")) = "Tracked Items"), "Tracked Items"),
    Norm = each Text.Lower(Text.Trim(Text.Replace(_, Character.FromNumber(160), " "))),
    StatusCol = List.First(List.Select(MoMCols, each Norm(_) = "status"), "Status"),
    ItemKeyCol = List.First(List.Select(MoMCols, each Norm(_) = "itemkey"), "ItemKey"),
    MoMWithItem = Table.AddColumn(MoM, "TrackedItem", each Text.Trim(Text.Replace(Text.From(Record.Field(_, MoMTrackedCol)), Character.FromNumber(160), " ")), type text),
    LookupStatusItemKey = Table.RenameColumns(
        Table.SelectColumns(MoMWithItem, {"TrackedItem", StatusCol, ItemKeyCol}),
        {{StatusCol, "Status"}, {ItemKeyCol, "ItemKey"}}
    ),

    // Use structured Tables only — exclude _mom_hacsoc and _Log (Daily Log) tables
    TablesOnly = Table.SelectRows(Source, each
        [Kind] = "Table"
        and Text.StartsWith([Name], "_")
        and [Name] <> "_mom_hacsoc"
        and not Text.Contains([Name], "_Log")
    ),

    MonthMap = [JAN=1, FEB=2, MAR=3, APR=4, MAY=5, JUN=6, JUNE=6, JUL=7, JULY=7, AUG=8, SEP=9, OCT=10, NOV=11, DEC=12],

    // Parse table name _YY_MMM → MonthKey (Text.Middle / AfterDelimiter are safer than position-based)
    AddMonthKey = Table.AddColumn(TablesOnly, "MonthKey", each
        let
            n = Text.Upper([Name]),
            yy = try Number.FromText(Text.Middle(n, 1, 2)) otherwise null,
            afterFirst = Text.AfterDelimiter(n, "_", 0),
            mmm = Text.AfterDelimiter(afterFirst, "_", 0),
            m = try Record.Field(MonthMap, mmm) otherwise null
        in
            if yy = null or m = null then null else #date(2000 + yy, m, 1),
        type nullable date
    ),

    ValidMonths = Table.SelectRows(AddMonthKey, each [MonthKey] <> null),

    // FIX 1: Per-table TrackedCol resolution (not single global)
    ExpandedPerTable = Table.AddColumn(ValidMonths, "ExpandedData", each
        let
            dt = [Data],
            cols = Table.ColumnNames(dt),
            tc = List.First(
                List.Select(cols, each Text.Trim(Text.Replace(_, Character.FromNumber(160), " ")) = "Tracked Items"),
                "Tracked Items"
            ),
            selected = Table.SelectColumns(dt, {tc, "Total"}),
            renamed = Table.RenameColumns(selected, {{tc, "TrackedItem"}, {"Total", "Total"}})
        in renamed
    ),
    Expanded = Table.ExpandTableColumn(ExpandedPerTable, "ExpandedData", {"TrackedItem", "Total"}, {"TrackedItem", "Total"}),

    CleanItem = Table.TransformColumns(Expanded, {{
        "TrackedItem",
        each
            let
                cleaned = Text.Trim(Text.Replace(Text.From(_), Character.FromNumber(160), " ")),
                normalized = if cleaned = "1 Man ESU" or cleaned = "1 man ESU" then "ESU Single Operator" else cleaned
            in normalized,
        type text
    }}),

    // FIX 2: Use type number instead of Int64.Type to preserve decimals (e.g., 5.5 for ESU OOS half-days)
    TotalNum = Table.TransformColumns(CleanItem, {{"Total", each if _ = null or _ = "" then 0 else try Number.From(_) otherwise 0, type number}}),

    Keep = Table.SelectColumns(TotalNum, {"MonthKey", "TrackedItem", "Total"}),

    MergedLookup = Table.NestedJoin(Keep, {"TrackedItem"}, LookupStatusItemKey, {"TrackedItem"}, "Lookup", JoinKind.LeftOuter),
    ExpandLookup = Table.ExpandTableColumn(MergedLookup, "Lookup", {"Status", "ItemKey"}, {"Status", "ItemKey"}),

    AddMonthYear = Table.AddColumn(ExpandLookup, "Month_Year", each Date.ToText([MonthKey], "MM-yy"), type text),
    AddSortKey = Table.AddColumn(AddMonthYear, "SortKey", each Date.ToText([MonthKey], "yyyy-MM-dd"), type text),

    // Rolling 13 months — include report month (e.g. pReportMonth=02/01/2026 → 02-25 through 02-26)
    EndMonth = Date.StartOfMonth(ReportMonth),
    StartMonth = Date.AddMonths(EndMonth, -12),
    Filter13 = Table.SelectRows(AddSortKey, each [MonthKey] >= StartMonth and [MonthKey] <= EndMonth),

    // FIX 3: AllItems = _mom_hacsoc items + any in Filter13 (ensures full dimension coverage)
    AllMonths = List.Sort(List.Distinct(Filter13[MonthKey])),
    MoMItems = List.Distinct(LookupStatusItemKey[TrackedItem]),
    AllItems = List.Distinct(List.Combine({MoMItems, List.Distinct(Filter13[TrackedItem])})),
    CrossList = List.Combine(List.Transform(AllMonths, (m) => List.Transform(AllItems, (it) => [MonthKey = m, TrackedItem = it]))),
    Skeleton = Table.FromRecords(CrossList),
    MergedFull = Table.NestedJoin(Skeleton, {"MonthKey", "TrackedItem"}, Filter13, {"MonthKey", "TrackedItem"}, "Data", JoinKind.LeftOuter),
    ExpandFull = Table.ExpandTableColumn(MergedFull, "Data", {"Total", "Status", "ItemKey", "Month_Year", "SortKey"}, {"Total", "Status", "ItemKey", "Month_Year", "SortKey"}),
    FillZeros = Table.TransformColumns(ExpandFull, {{"Total", each if _ = null then 0 else _, type number}}),
    MonthYearF = Table.AddColumn(FillZeros, "Month_YearF", each if [Month_Year] = null then Date.ToText([MonthKey], "MM-yy") else [Month_Year], type text),
    SortKeyF = Table.AddColumn(MonthYearF, "SortKeyF", each if [SortKey] = null then Date.ToText([MonthKey], "yyyy-MM-dd") else [SortKey], type text),
    RenameMySk = Table.RenameColumns(Table.RemoveColumns(SortKeyF, {"Month_Year", "SortKey"}), {{"Month_YearF", "Month_Year"}, {"SortKeyF", "SortKey"}}),
    // Restore Status/ItemKey from lookup for rows that were missing (null after expand)
    MergedLookup2 = Table.NestedJoin(RenameMySk, {"TrackedItem"}, LookupStatusItemKey, {"TrackedItem"}, "Lookup2", JoinKind.LeftOuter),
    ExpandLookup2 = Table.ExpandTableColumn(MergedLookup2, "Lookup2", {"Status", "ItemKey"}, {"StatusNew", "ItemKeyNew"}),
    StatusFinal = Table.AddColumn(ExpandLookup2, "StatusF", each if [Status] = null then [StatusNew] else [Status], type text),
    ItemKeyFinal = Table.AddColumn(StatusFinal, "ItemKeyF", each if [ItemKey] = null then [ItemKeyNew] else [ItemKey], type text),
    DropTemp = Table.RemoveColumns(ItemKeyFinal, {"Status", "StatusNew", "ItemKey", "ItemKeyNew"}),
    RenameFinal = Table.RenameColumns(DropTemp, {{"StatusF", "Status"}, {"ItemKeyF", "ItemKey"}}),

    Result = if Table.RowCount(Filter13) > 0 then RenameFinal else AddSortKey
in
    Result
