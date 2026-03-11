# Esu 13Month M Code Fixes And Documentation

**Processing Date:** 2026-03-05 19:29:15
**Source File:** ESU_13Month_M_Code_Fixes_And_Documentation.md
**Total Chunks:** 1

---

# M code update for ESU_13Month
_Exported on 3/5/2026 at 19:29:01 EST from Cursor (2.6.12)_

---

**User**

read @c:\Users\carucci_r\OneDrive - City of Hackensack\KB_Shared\04_output\esu_claude_in_excel_to_add_daily_log
the m code of the esu_13Moth needs updating to fix errors, Token Literal expected. // 🕒 2026-03-05
// # Master_Automation/m_code/esu/ESU_13Month.m
// # Author: R. A. Carucci
// # Purpose: Single query — load ESU.xlsx monthly Tables only; rolling 13 months. // # Fixes: Per-table TrackedCol resolution, type number (not Int64), robust cleaning. let
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

    TablesOnly = Table.SelectRows(Source, each
        [Kind] = "Table"
        and Text.StartsWith([Name], "_")
        and [Name] <> "_mom_hacsoc"
    ),

    MonthMap = [JAN=1, FEB=2, MAR=3, APR=4, MAY=5, JUN=6, JUNE=6, JUL=7, JULY=7, AUG=8, SEP=9, OCT=10, NOV=11, DEC=12],

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

    // ← FIX 1: Per-table TrackedCol resolution (not single global)
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
        each Text.Trim(Text.Replace(Text.From(_), Character.FromNumber(160), " ")),
        type text
    }}),

    // ← FIX 2: Use type number instead of Int64.Type to preserve decimals (e.g., 5.5 for ESU OOS half-days)
    TotalNum = Table.TransformColumns(CleanItem, {{"Total", each if _ = null or _ = "" then 0 else try Number.From(_) otherwise 0, type number}}),

    Keep = Table.SelectColumns(TotalNum, {"MonthKey", "TrackedItem", "Total"}),

    MergedLookup = Table.NestedJoin(Keep, {"TrackedItem"}, LookupStatusItemKey, {"TrackedItem"}, "Lookup", JoinKind.LeftOuter),
    ExpandLookup = Table.ExpandTableColumn(MergedLookup, "Lookup", {"Status", "ItemKey"}, {"Status", "ItemKey"}),

    AddMonthYear = Table.AddColumn(ExpandLookup, "Month_Year", each Date.ToText([MonthKey], "MM-yy"), type text),
    AddSortKey = Table.AddColumn(AddMonthYear, "SortKey", each Date.ToText([MonthKey], "yyyy-MM-dd"), type text),

    // Rolling 13 complete months
    EndMonth = Date.StartOfMonth(Date.AddMonths(DateTime.Date(DateTime.LocalNow()), -1)),
    StartMonth = Date.AddMonths(EndMonth, -12),
    Filter13 = Table.SelectRows(AddSortKey, each [MonthKey] >= StartMonth and [MonthKey] <= EndMonth),

    // ← FIX 3: Filter AllItems to only _mom_hacsoc tracked items (excludes ad-hoc rows like "1 man ESU")
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
    MergedLookup2 = Table.NestedJoin(RenameMySk, {"TrackedItem"}, LookupStatusItemKey, {"TrackedItem"}, "Lookup2", JoinKind.LeftOuter),
    ExpandLookup2 = Table.ExpandTableColumn(MergedLookup2, "Lookup2", {"Status", "ItemKey"}, {"StatusNew", "ItemKeyNew"}),
    StatusFinal = Table.AddColumn(ExpandLookup2, "StatusF", each if [Status] = null then [StatusNew] else [Status], type text),
    ItemKeyFinal = Table.AddColumn(StatusFinal, "ItemKeyF", each if [ItemKey] = null then [ItemKeyNew] else [ItemKey], type text),
    DropTemp = Table.RemoveColumns(ItemKeyFinal, {"Status", "StatusNew", "ItemKey", "ItemKeyNew"}),
    RenameFinal = Table.RenameColumns(DropTemp, {{"StatusF", "Status"}, {"ItemKeyF", "ItemKey"}}),

    Result = if Table.RowCount(Filter13) > 0 then RenameFinal else AddSortKey
in
    Result
</parameter>
<parameter name="explanation">Placeholder - just for the M code display</parameter>
</invoke> 

---

**Cursor**

Searching for causes of "Token Literal expected" in Power Query M:


Applying fixes to `ESU_13Month.m`: per-table TrackedCol resolution, use `type number` instead of `Int64.Type` for decimals (e.g. ESU OOS half-days), and derive AllItems from `_mom_hacsoc` plus Filter13. Updating FIX 3 to match the comment: use only `_mom_hacsoc` items to exclude ad-hoc rows like "1 man ESU". Updated `ESU_13Month.m` with these changes:

## Changes made

1. **FIX 1 – Per-table TrackedCol resolution**  
   Replaced the single `TrackedCol` from the first table with per-table resolution. Each monthly table now resolves its own "Tracked Items" column (including non‑breaking spaces), so tables with different column names or spacing still work. 2. **FIX 2 – `type number` instead of `Int64.Type`**  
   Switched `Total` from `Int64.Type` to `type number` in both `TotalNum` and `FillZeros` so decimal values (e.g. 0.5 for ESU OOS half-days) are preserved. 3. **FIX 3 – AllItems from dimension + data**  
   `AllItems` is now built from `MoMItems` (from `_mom_hacsoc`) plus items in `Filter13`, so the skeleton includes all dimension items and any items that appear in the filtered data. ## About "Token Literal expected"

The error often comes from invalid characters in the M code. In your pasted snippet there were XML-like tags at the end:

```
</parameter>
<parameter name="explanation">Placeholder - just for the M code display</parameter>
</invoke>
```

Those tags are not valid M and cause parse errors. The file in `m_code/esu/ESU_13Month.m` does not contain them. When copying into Power BI or Excel, copy only the M code and avoid any surrounding XML or markup. The query still uses `pReportMonth` for the rolling window, so it remains compatible with the Phase 2 template. ---

**User**

please read @docs/chatlogs/claude_in_excel_update_logic_for_mom_and_month_tables @docs/chatlogs/claude_in_excel_fix_esu_mom_single_operator @docs/chatlogs/esu_claude_in_excel_to_add_daily_log 
the m code below  returns this visual  @c:\Users\carucci_r\Downloads\2026_03_05_ESU.csv and it does not match the data in the mom table@c:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\ESU\ESU.xlsx 


// 🕒 2026-03-05
// # Master_Automation/m_code/esu/ESU_13Month.m
// # Author: R. A. Carucci
// # Purpose: Single query — load ESU.xlsx monthly Tables only; rolling 13 months. // # Fixes: Per-table TrackedCol resolution, type number (not Int64), robust cleaning. let
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

    // Use structured Tables only — Sheet [Data] does not expand correctly with named columns
    TablesOnly = Table.SelectRows(Source, each
        [Kind] = "Table"
        and Text.StartsWith([Name], "_")
        and [Name] <> "_mom_hacsoc"
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
        each Text.Trim(Text.Replace(Text.From(_), Character.FromNumber(160), " ")),
        type text
    }}),

    // FIX 2: Use type number instead of Int64.Type to preserve decimals (e.g., 5.5 for ESU OOS half-days)
    TotalNum = Table.TransformColumns(CleanItem, {{"Total", each if _ = null or _ = "" then 0 else try Number.From(_) otherwise 0, type number}}),

    Keep = Table.SelectColumns(TotalNum, {"MonthKey", "TrackedItem", "Total"}),

    MergedLookup = Table.NestedJoin(Keep, {"TrackedItem"}, LookupStatusItemKey, {"TrackedItem"}, "Lookup", JoinKind.LeftOuter),
    ExpandLookup = Table.ExpandTableColumn(MergedLookup, "Lookup", {"Status", "ItemKey"}, {"Status", "ItemKey"}),

    AddMonthYear = Table.AddColumn(ExpandLookup, "Month_Year", each Date.ToText([MonthKey], "MM-yy"), type text),
    AddSortKey = Table.AddColumn(AddMonthYear, "SortKey", each Date.ToText([MonthKey], "yyyy-MM-dd"), type text),

    // Rolling 13 complete months
    EndMonth = Date.StartOfMonth(Date.AddMonths(ReportMonth, -1)),
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

---

**Cursor**


Running a Python script to read the ESU workbook and compare its structure to the M code:



Checking which tables Power Query sees and whether Log tables are included:



Excluding `_Log` tables (they lack "Tracked Items" and "Total") and adding TrackedItem normalization so "1 Man ESU" maps to "ESU Single Operator". ESU_13Month.m is updated with two changes so the Power BI output matches the MoM table:

## Changes made

### 1. Exclude `_Log` tables
The query was including Daily Log tables (`_26_JAN_Log`, `_26_FEB_Log`, etc. ), which have different columns (Date, Badge, Category, Notes, Impact) and no "Tracked Items" or "Total". That could cause errors or bad data. **Update:** Added `and not Text.Contains([Name], "_Log")` so only the main monthly tables (`_26_JAN`, `_26_FEB`, etc.) are used. ### 2. Normalize "1 Man ESU" → "ESU Single Operator"
After Option A, `_mom_hacsoc` uses "ESU Single Operator" and row 31 ("1 Man ESU") was removed. If any monthly table still has "1 Man ESU" or "1 man ESU", the join would fail and those rows would show 0. **Update:** Added normalization in `CleanItem` so both variants are mapped to "ESU Single Operator" before the join. ## Expected results

With these changes, the query should return:

| TrackedItem           | 01-26 | 02-26 |
|----------------------|-------|-------|
| ESU OOS              | 0     | 5.5   |
| ESU Single Operator  | 2     | 15.5  |

## Checks in Power BI

1. **pReportMonth** – Set to at least `2026-03-01` so the 13‑month window includes 02-26. 2. **Refresh** – Save ESU.xlsx, then in Power BI: Power Query → Refresh preview → Close & Apply → Refresh report. 3. **Source file** – Confirm Power BI is using the correct ESU.xlsx path and the updated workbook. ---

**User**

@c:\Users\carucci_r\Downloads\2026_03_05_19_21_48_ESU.csv updated m code returns this data in the visual 02-26 is not showing I do not see single esu operator either

---

**Cursor**


Checking rolling-window logic and `pReportMonth` usage:



Changing the rolling-window logic to include the report month (02-26) when `pReportMonth` = 02/01/2026. The change is in place. Here’s what was updated and what to expect. ## Change made

**Rolling window logic**

- **Before:** `EndMonth = Date.AddMonths(ReportMonth, -1)` → window ended at the month before the report month  
  - `pReportMonth = 02/01/2026` → window = 02-25 through **01-26** (02-26 excluded)

- **After:** `EndMonth = Date.StartOfMonth(ReportMonth)` → window includes the report month  
  - `pReportMonth = 02/01/2026` → window = 02-25 through **02-26**

This matches the summons logic so the report month is included. ## What you should see after refresh

With `pReportMonth = 02/01/2026`:

| TrackedItem          | 01-26 | 02-26 |
|----------------------|-------|-------|
| ESU OOS              | 0     | 5.5   |
| ESU Single Operator  | 2     | 15.5  |

## Next steps

1. Save the updated M code in Power BI (or paste the latest `ESU_13Month.m` into the query). 2. Refresh the ESU_13Month query. 3. Close & Apply, then refresh the report. The CSV already shows ESU Single Operator in the data (e.g. 2 for 01-26). With 02-26 in the window, the 02-26 column should appear and show 15.5 for ESU Single Operator and 5.5 for ESU OOS. ---

**User**

thanks that worked

---

**Cursor**


Good to hear it’s working. The ESU visual should now show 02-26 with the correct values for ESU OOS (5.5) and ESU Single Operator (15.5). If anything else comes up, ask anytime. ---

**User**

Update all project documentation files so they accurately reflect the latest code and configuration changes in this repo. Then automatically run the necessary git commands to:
1.stage only the updated documentation files,
2.create a single, clear commit for these doc updates with an appropriate versioned message, and
3.push to the current remote branch. Do not ask for confirmation; run the commands directly, and then summarize what you changed and the git commands you executed. ---

**Cursor**


## Summary

### Documentation updates

| File | Changes |
|------|---------|
| **docs/ESU_POWER_BI_LOAD_AND_PUBLISH.md** | Source path `carucci_r`; _Log tables excluded; "1 Man ESU" → "ESU Single Operator" normalization; rolling 13‑month window driven by pReportMonth (includes report month); `type number` for decimals; pReportMonth requirement added |
| **m_code/esu/README.md** | Rolling window driven by pReportMonth; note on 2026‑03‑05 fixes (_Log exclusion, normalization, type number) |
| **CHANGELOG.md** | Added [1.17.28] - 2026‑03‑05: ESU_13Month rolling window, _Log exclusion, TrackedItem normalization, type number, per‑table TrackedCol |
| **docs/MONTHLY_REPORT_TEMPLATE_WORKFLOW.md** | ESU_13Month row updated to note “includes report month; excludes _Log tables” |

### Git commands run

```bash
git add docs/ESU_POWER_BI_LOAD_AND_PUBLISH.md m_code/esu/README.md CHANGELOG.md docs/MONTHLY_REPORT_TEMPLATE_WORKFLOW.md
git commit -m "docs: v1.17.28 — ESU_13Month rolling window, _Log exclusion, TrackedItem normalization"
git push
```

**Commit:** `03aeeeb` on branch `docs/update-20260114-1447`  
**Pushed to:** `origin/docs/update-20260114-1447`

---

**User**

I'm preparing to export this chat. Please generate a descriptive filename that summarizes the main topic or task of this conversation. Requirements:
• 4-8 words
• Title Case (capitalize major words)
• Replace spaces with underscores
• Include .md extension
• No dates or special characters

Output only the filename, with the suffix .md and nothing else. ---

**Cursor**


ESU_13Month_M_Code_Fixes_And_Documentation.md

