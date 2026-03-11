// 🕒 2026-03-10-17-45-00
// # docs/SUMMONS_M_CODE_NOTES.md
// # Author: R. A. Carucci
// # Purpose: Lessons learned from summons Power Query M code fixes — reference for future Claude MCP sessions.

# Summons M Code Notes

Reference for future Claude MCP sessions working on `summons_13month_trend`, `summons_all_bureaus`, `summons_top5_moving`, `summons_top5_parking` in the Monthly Report Power BI model.

---

## 1. Power BI Table Schema Requires All Defined Columns

**Finding:** `summons_13month_trend` has **24 columns** defined in its table schema (confirmed via `INFO.COLUMNS()` where `TableID = 70049`):

```
TYPE, ETL_VERSION, Month_Year, YearMonthKey, Year, Month, DATA_QUALITY_SCORE,
PADDED_BADGE_NUMBER, OFFICER_DISPLAY_NAME, WG2, ISSUE_DATE, OFFICER_NAME_RAW,
Bureau_Consolidated, TITLE, statute, TICKET_COUNT, TICKET_NUMBER, STATUS,
VIOLATION_DESCRIPTION, WG1, IS_AGGREGATE, source_file, PROCESSING_TIMESTAMP, RANK
```

**Why it matters:** The partition M code must return **every column in the table schema** or the refresh commit fails. During the 2026-03-10 session, a `Slimmed` step using `Table.SelectColumns` was added to drop unused columns (PADDED_BADGE_NUMBER, OFFICER_NAME_RAW, etc.). The refresh itself succeeded, but the **commit failed** with:

```
The 'ETL_VERSION' column does not exist in the rowset.
```

**Rule:** Do NOT slim the partition output unless you also remove the corresponding column definitions from the table schema (via `column_operations -> Delete`). This is a two-step operation and risks breaking visuals or measures that reference those columns.

**Resolution:** The `Slimmed` step was reverted. The final step is `Combined` (full column set). The preview slowness in Power Query Editor is caused by the cross-join filler logic, not column count — once refreshed into the model, queries are fast.

---

## 2. List.TransformMany Syntax

**Finding:** `List.TransformMany` expects the projection function to return a **record**, not a list-wrapped record.

**Correct:**
```m
FullCross = List.TransformMany(
    MonthYearLabels,
    each AllTypes,
    (my, t) => [Month_Year = my, TYPE = t]
),
CrossTable = Table.FromRecords(FullCross),
```

**Wrong (causes type errors):**
```m
// DON'T wrap in { } — that creates a list of records, not a flat record list
(my, t) => {[Month_Year = my, TYPE = t]}
```

**Why it matters:** The wrong syntax can produce nested lists instead of a flat record list, causing `Table.FromRecords` to fail or produce unexpected results.

---

## 3. Power BI "Show Errors" NullReferenceException

**Finding:** Clicking "Show Errors" on a partition with errors can trigger a `NullReferenceException` crash in Power BI Desktop. This is a **Power BI Desktop UI bug**, not an M code problem.

**Workaround:** Instead of clicking "Show Errors" in the UI, use the MCP tool to inspect the error:

```
partition_operations -> Get -> references: [{ "tableName": "<table>" }]
```

Check the `errorMessage` field in the response.

---

## 4. Filler Row Pattern for Gap Months

**Context:** July 2025 has only 17 straggler M records — no P or C data exists. Without filler rows, the Department-Wide visual shows `07-25 | M=17 | P=(blank)` which looks broken.

**Pattern:** After `AddConsolidatedBureau`, the M code:
1. Groups existing data by `{Month_Year, TYPE}` to get actual ticket counts
2. Generates a full cross-join of all 13 months × 3 types (M, P, C) using `List.Generate` + `List.TransformMany`
3. Left-outer joins the cross table to the grouped data
4. Filters to only the missing combos (TICKET_COUNT = 0)
5. Adds required columns (ISSUE_DATE, YearMonthKey) to the filler rows
6. Appends filler rows to the original data via `Table.Combine`

This ensures every month shows explicit 0 values instead of blanks in visuals.

**Important:** Filler rows have null values for all columns not explicitly added (WG2, OFFICER_DISPLAY_NAME, etc.). This is fine because the trend visual only aggregates by Month_Year and TYPE.

---

## 5. WG2 Filter Rules

| Query | WG2 Filter | Reason |
|-------|-----------|--------|
| `summons_13month_trend` | **None** — all officers included | Department-wide counts; K. Peralta (no WG2) must be counted |
| `summons_all_bureaus` | Maps null/blank/"nan"/"UNKNOWN" → "UNASSIGNED" | Bureau breakdown needs a catch-all row so bureau totals = dept-wide |
| `summons_top5_moving` | None (uses OFFICER_DISPLAY_NAME grouping) | Officers with no WG2 can still appear in top 5 |
| `summons_top5_parking` | None | Same reasoning |

**K. Peralta #0311** (Community Outreach) has WG2 = `"nan"` in the CSV (pandas NaN export). Her 30 Feb 2026 tickets (2 M + 28 P) appear in dept-wide trend and in the UNASSIGNED row of all_bureaus.

---

## 6. BackfillMonths = {} (Empty)

The `BackfillMonths` list in `summons_13month_trend` is intentionally empty. July 2025 has 17 straggler records with `IS_AGGREGATE = False`. Setting `BackfillMonths = {"07-25"}` would filter those out (expecting `IS_AGGREGATE = TRUE` rows from a backfill file that doesn't exist), hiding July entirely. Leave it empty unless a backfill CSV is actually created.

---

## 7. Subtitle Measures — Avoid UI Table Dependency

Multiple subtitle measures were broken because they referenced `'UI'[UI MonthRange 13m]` — a table that was removed from the model. The fix replaces them with self-contained DAX using `EOMONTH(TODAY(), -1)`:

```dax
VAR EndDate   = EOMONTH(TODAY(), -1)
VAR StartDate = EDATE(EndDate, -12)
RETURN
"Description text. " &
"Rolling 13-Month Overview (" &
    FORMAT(StartDate, "MMMM yyyy") & " - " & FORMAT(EndDate, "MMMM yyyy") & ")"
```

This pattern (matching `Subtitle_V3_Accrual`) auto-advances monthly and has no external dependencies. Applied to: `Traffic Subtitle`, `Traffic Crashes Subtitle`.

---

## 8. ___Traffic Dynamic Changed Type

The `___Traffic` query's `#"Changed Type"` step was hardcoded with month columns through `"01-26"`. When new months (02-26 through 12-26) were added to `Traffic_Monthly.xlsx`, they were silently dropped.

**Fix:** Replaced with dynamic typing that auto-types every non-"Tracked Items" column:

```m
#"Changed Type" = Table.TransformColumnTypes(
    _mom_traffic_Table,
    List.Transform(
        List.RemoveItems(Table.ColumnNames(_mom_traffic_Table), {"Tracked Items"}),
        each {_, Int64.Type}
    )
    & {{"Tracked Items", type text}}
)
```

This never needs updating when new month columns are added to the Excel source.

---

## Quick Reference: MCP Validation Queries

```dax
-- 13-month trend by type
EVALUATE SUMMARIZECOLUMNS(
    'summons_13month_trend'[Month_Year],
    'summons_13month_trend'[TYPE],
    "Tickets", SUM('summons_13month_trend'[TICKET_COUNT])
)

-- All bureaus
EVALUATE 'summons_all_bureaus'

-- Top 5 moving / parking
EVALUATE 'summons_top5_moving'
EVALUATE 'summons_top5_parking'

-- Check table schema columns
EVALUATE SELECTCOLUMNS(
    FILTER(INFO.COLUMNS(), [TableID] = 70049 && [Type] = 1),
    "Col", [ExplicitName],
    "DataType", [ExplicitDataType]
)
```
