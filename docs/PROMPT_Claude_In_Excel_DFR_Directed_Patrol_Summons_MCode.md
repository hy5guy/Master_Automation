# Prompt for Claude in Excel: DFR Directed Patrol Enforcement M Code

**Purpose**: Generate Power BI M code to load the `DFR_Summons` table from `dfr_directed_patrol_enforcement.xlsx` for a new Drone Page visual. The query must use a rolling 13-month window driven by `pReportMonth` and filter out summons marked for Dismissal or Void in the Summons Recall column.

---

## Instructions for Claude in Excel

Copy the following prompt into Claude in Excel. Ensure the `dfr_directed_patrol_enforcement.xlsx` workbook is open or its structure is known.

---

### PROMPT START

Generate Power BI M code for a new query named **DFR_Summons** that:

1. **Loads** the `DFR_Summons` table from the Excel workbook:
   - **Path**: `C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Drone\dfr_directed_patrol_enforcement.xlsx`
   - **Source**: Use either a named Excel Table named `DFR_Summons` or a sheet named `DFR Summons Log` (try Table first, fallback to Sheet with PromoteHeaders).
   - Pattern: `Source{[Item="DFR_Summons", Kind="Table"]}[Data]` or `Source{[Name="DFR Summons Log", Kind="Sheet"]}[Data]`

2. **Selects** these columns for the visual (schema-resilient: only transform columns that exist):
   - Summons ID (or equivalent: Ticket Number, Citation ID)
   - Date (issue date or violation date)
   - Time (if present)
   - Location
   - Statute
   - Description
   - Fine Amount
   - Violation Type

3. **Applies** a rolling 13-month window driven by `pReportMonth`:
   - `pReportMonth` is a Date parameter: `#date(YYYY, M, 1)` (first day of report month).
   - **Window**: Include full report month and 12 months prior. Use `EndOfMonth` for end date.
   - `EndDate = Date.EndOfMonth(Date.From(pReportMonth))`
   - `StartDate = Date.StartOfMonth(Date.AddMonths(Date.From(pReportMonth), -12))`
   - Filter rows where the date column falls within `[StartDate, EndDate]`.
   - If the date column is datetime, use `DateTime.Date([DateColumn])` for comparison.

4. **Filters out** summons marked for Dismissal or Void (dual filter):
   - **Summons_Recall:** Exclude rows where Summons Recall contains "Dismiss" or "Void" (case-insensitive).
   - **Summons_Status:** Exclude rows where Summons Status contains "dismiss" or "void" (catches Dismissed, Void, Voided; use Text.Contains on Text.Trim(Text.Lower(status ?? ""))).
   - Keep rows where both columns pass (null/empty or no match).

5. **Adds** a `YearMonthKey` column for grouping/trending: `Date.Year([Date]) * 100 + Date.Month([Date])` (Int64.Type).

6. **Follows** these conventions from our existing M code:
   - Start with `let` and `ReportMonth = pReportMonth`
   - Use `Table.PromoteHeaders(..., [PromoteAllScalars = true])`
   - Use schema-resilient type mapping: only apply `Table.TransformColumnTypes` for columns that exist
   - Use `try ... otherwise` when choosing between Table vs Sheet source
   - Include header comments: `// # drone/DFR_Summons.m`, `// # Author: R. A. Carucci`, `// # Purpose: ...`
   - End with `in <FinalStep>`

7. **Handles** edge cases:
   - If column names differ slightly (e.g., "Summons_ID" vs "Summons ID"), use `Table.RenameColumns` to standardize.
   - Replace null Fine Amount with 0 for DAX compatibility.
   - Ensure Date column is `type date` or `type datetime` before filtering.

**Reference M code patterns** (from our project):

- **Excel load + Table/Sheet fallback** (from `___Social_Media.m`):
```powerquery
Source = Excel.Workbook(File.Contents("...path..."), null, true),
RawData = try Source{[Item="DFR_Summons", Kind="Table"]}[Data]
    otherwise Source{[Name="DFR Summons Log", Kind="Sheet"]}[Data],
Promoted = Table.PromoteHeaders(RawData, [PromoteAllScalars=true]),
```

- **13-month window** (from `DFR_Summons.m`):
```powerquery
EndDate   = Date.EndOfMonth(Date.From(pReportMonth)),
StartDate = Date.StartOfMonth(Date.AddMonths(Date.From(pReportMonth), -12)),
// Filter: [Date] >= StartDate and [Date] <= EndDate
FilteredData = Table.SelectRows(ChangedType, each
    DateTime.Date([DateColumn]) >= StartDate and DateTime.Date([DateColumn]) <= EndDate
),
```

- **Schema-resilient type map** (from `summons_13month_trend.m`):
```powerquery
ExistingCols = Table.ColumnNames(PromotedHeaders),
TypeMap = {
    {"Summons_ID", type text},
    {"Date", type date},
    {"Time", type time},
    {"Location", type text},
    {"Statute", type text},
    {"Description", type text},
    {"Fine_Amount", type number},
    {"Violation_Type", type text}
},
FilteredTypes = List.Select(TypeMap, each List.Contains(ExistingCols, _{0})),
ChangedType = Table.TransformColumnTypes(PromotedHeaders, FilteredTypes),
```

**Output**: Return the complete M code as a single block, ready to paste into Power BI's Power Query Editor as a new query. The query name in Power BI will be `DFR_Summons`.

### PROMPT END

---

## Post-Generation Checklist

After Claude in Excel returns the M code:

1. **Verify path**: Confirm `dfr_directed_patrol_enforcement.xlsx` is saved at the specified path (or update the path in the M code to match your actual location).
2. **Verify sheet/table name**: Ensure the Excel workbook has a table or sheet named `DFR_Summons` with the expected columns.
3. **Add to Power BI**: In Power BI Desktop, create a new blank query, open Advanced Editor, paste the M code, and rename the query to `DFR_Summons`.
4. **Add to Drone Page**: Create a new visual (e.g., table, matrix, or chart) bound to `DFR_Summons`.
5. **Register in model**: Add `DFR_Summons` to the model. Set `MM-YY` to sort by `Date_Sort_Key` so matrix columns display chronologically.
6. **Test pReportMonth**: Change `pReportMonth` and refresh to confirm the 13-month window updates correctly.

---

## Column Name Mapping (Claude in Excel Output)

If Claude in Excel uses different column names in the workbook, map them as follows:

| Expected (M code) | Possible Excel Names |
|------------------|----------------------|
| Summons_ID       | Summons ID, Ticket Number, Citation ID, ID |
| Date             | Date, Issue Date, Violation Date |
| Time             | Time, Issue Time |
| Location         | Location, Address, Place |
| Statute          | Statute, Code, Violation Code |
| Description      | Description, Violation Description |
| Fine_Amount      | Fine Amount, Fine, Amount |
| Violation_Type   | Violation Type, Type, Category |

---

*Last updated: 2026-03-17 | Master_Automation v1.18.9*
