# Prompt: Claude MCP — Arrest Query Path & Top 5 Fixes

**Context:** After the `_Arrest` folder refactor (v1.18.16), arrest M code queries fail. Use this prompt with Claude Desktop connected to the Power BI MCP to fix the `.pbix` queries.

---

## Instruction for Next Claude Session

**Update M codes in BOTH Power BI and the local directory.** Claude has access to `C:\Users\carucci_r\OneDrive - City of Hackensack\06_Workspace_Management`. After applying changes to the Power BI `.pbix`, also update the corresponding `.m` files in the repo so they stay in sync:

- `m_code/arrests/___Arrest_13Month.m`
- `m_code/arrests/___Top_5_Arrests.m`

This keeps the repo as the source of truth for M code and avoids drift between the `.pbix` and version control.

---

## Issue 1: ___Arrest_13Month — Folder Not Found

**Error:** `We couldn't find the folder '...\05_EXPORTS\_Arrest\monthly\*'`

**Cause:** The path `05_EXPORTS\_Arrest\monthly` no longer exists. The new structure is `05_EXPORTS\_Arrest\YYYY\month\` (e.g. `2026\month\`).

**Fix:** Replace the single-folder logic with multi-year discovery:

1. Open query **___Arrest_13Month** in Power Query Editor.
2. Replace the `BasePath` and `AllFiles` logic (around lines 13–14) with:

```powerquery
BasePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Arrest",
Years = List.Numbers(Date.Year(StartOfWindow), Date.Year(EndOfWindow) - Date.Year(StartOfWindow) + 1),
FolderPaths = List.Transform(Years, each BasePath & "\" & Number.ToText(_) & "\month"),
AllFiles = Table.Combine(
    List.Transform(FolderPaths, each
        try Folder.Files(_) otherwise #table({"Content", "Name", "Extension", "Date accessed", "Date modified", "Date created", "Attributes", "Folder Path"}, {})
    )
),
```

3. Ensure `EndOfWindow` and `StartOfWindow` are defined above this block (they should already be).
4. Apply changes and refresh.

---

## Issue 2: ___Top_5_Arrests — "No arrest data found for February 2026"

**Error:** `Expression.Error: No arrest data found for February 2026. Check date filters and data availability.`

**Cause:** The query loads the **latest file by modified date** and then filters to the **previous month**. If the latest file is `2026_03_Arrests_PowerBI_Ready.xlsx` (March only), filtering to February returns 0 rows.

**Fix:** Load the file that matches the **target month** (previous month), not the latest file:

1. Open query **___Top_5_Arrests** in Power Query Editor.
2. Move `PreviousMonth`, `TargetYear`, `TargetMonth`, and `MonthYearDisplay` to the top of the `let` block (right after `ReportMonth = pReportMonth`).
3. Replace the file-loading section (FolderFiles → Source) with:

```powerquery
PreviousMonth = Date.AddMonths(ReportMonth, -1),
TargetYear = Date.Year(PreviousMonth),
TargetMonth = Date.Month(PreviousMonth),
MonthYearDisplay = Date.MonthName(PreviousMonth) & " " & Text.From(TargetYear),

FolderFiles = Folder.Files(
    "C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\ARREST_DATA\Power_BI"
),
PowerBIFiles = Table.SelectRows(
    FolderFiles,
    each [Extension] = ".xlsx" and Text.Contains([Name], "PowerBI_Ready")
),
TargetPattern = Text.From(TargetYear) & "_" & Text.PadStart(Text.From(TargetMonth), 2, "0"),
TargetFile = Table.SelectRows(PowerBIFiles, each Text.Contains([Name], TargetPattern)),

Source = if Table.RowCount(TargetFile) > 0 then
    let
        FileContent = TargetFile{0}[Content],
        ExcelData = Excel.Workbook(FileContent, null, true),
        FirstSheet = ExcelData{0}[Data]
    in
        FirstSheet
else
    error "No Power BI ready file for " & MonthYearDisplay & ". Run Arrest ETL with --report-month " & Text.From(TargetYear) & "-" & Text.PadStart(Text.From(TargetMonth), 2, "0"),
```

4. Remove the duplicate `PreviousMonth`, `TargetYear`, `TargetMonth`, `MonthYearDisplay` from the later section (they are now at the top).
5. Update `WithSourceInfo` to use `TargetFile{0}[Name]` instead of `Sorted{0}[Name]` (and change the condition to `Table.RowCount(TargetFile) > 0`).
6. Apply changes and refresh.

---

## Script vs M Code

| Component | Responsibility |
|-----------|----------------|
| **Arrest ETL script** | Produces `YYYY_MM_Arrests_PowerBI_Ready.xlsx` in `01_DataSources\ARREST_DATA\Power_BI\` for the report month. Run with `--report-month YYYY-MM` for a specific month. |
| **M code** | Reads from the correct paths. `___Arrest_13Month` reads raw LawSoft exports from `05_EXPORTS\_Arrest\YYYY\month\`. `___Top_5_Arrests` and `___Arrest_Categories` read Power BI–ready files from `01_DataSources\ARREST_DATA\Power_BI\`. |

**To get February 2026 Top 5 data:** Run Arrest ETL with `--report-month 2026-02` so `2026_02_Arrests_PowerBI_Ready.xlsx` exists. With `pReportMonth = March 2026`, Top 5 shows the previous month (February).

---

## Verification

1. Ensure `05_EXPORTS\_Arrest\2025\month\` and `05_EXPORTS\_Arrest\2026\month\` contain LawSoft arrest `.xlsx` files.
2. Ensure `01_DataSources\ARREST_DATA\Power_BI\` contains `YYYY_MM_Arrests_PowerBI_Ready.xlsx` for the months you need (e.g. `2026_02` for February, `2026_03` for March).
3. Refresh the report; `___Arrest_13Month` and `___Top_5_Arrests` should load without errors.
