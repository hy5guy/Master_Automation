# ESU Power Query: Load and Publish in Power BI

## Recommended: Single query (ESU_13Month)

Use **one query** — `m_code/esu/ESU_13Month.m` — with no helper queries.

1. In Power BI: **Get data → Blank Query**.
2. Open **Advanced Editor** and paste the full contents of `ESU_13Month.m`.
3. Name the query (e.g. `ESU_13Month`).
4. **Refresh.**

**Output columns:** MonthKey, TrackedItem, Total, **Status**, **ItemKey**, **Month_Year** (MM-yy).

**Source:** `C:\Users\RobertCarucci\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\ESU\ESU.xlsx`

**Behavior:**
- Loads only **structured Excel Tables** (`[Kind] = "Table"`) whose names start with `_` and are not `_mom_hacsoc` (e.g. `_26_JAN`, `_25_FEB`). Sheet-based data is not used so that column expansion works correctly.
- Parses table name `_YY_MMM` to **MonthKey** (first of month).
- Looks up **Status** and **ItemKey** from the **\_mom_hacsoc** table (case-insensitive column match: e.g. "status", "Status").
- Adds **Month_Year** as MM-yy (e.g. 01-26).
- Applies a **rolling 13-month** window (last 13 complete months). If that filter returns no rows (e.g. workbook has only older months), the query returns all loaded months so you still get a preview.

**Workbook requirements:**
- Monthly data in **Excel Tables** (Insert → Table / Ctrl+T), not just ranges.
- Table names like **\_26_JAN**, **\_25_FEB** (leading underscore, YY, underscore, MMM).
- Each table: column that trims to **Tracked Items**, and a **Total** column.
- **\_mom_hacsoc** table/sheet with columns that trim to **Tracked Items**, **Status**, and **ItemKey** (status column is required; ItemKey is optional for the lookup).

---

## Optional: Four-query approach (dimension with SortKey)

Only if you need the **TrackedItems dimension with SortKey** (custom sort order in visuals):

1. Add **fnCleanText** (paste `m_code/esu/fnCleanText.m`).
2. Add **fnMonthKeyFromTableName** (paste `m_code/esu/fnMonthKeyFromTableName.m`).
3. Add **TrackedItems** (paste `m_code/esu/TrackedItems.m`).
4. Add **MonthlyActivity** (paste `m_code/esu/MonthlyActivity.m`).

Load the two functions before TrackedItems and MonthlyActivity. For a simple 13-month table with Status and ItemKey, **ESU_13Month alone is enough.**

---

## If you get "Failed to save modifications to the server" with many errors

Power BI **validates the entire model** when you save or publish. Adding ESU can surface every broken reference in the report (missing tables, columns, DAX).

### R43 / field not found (multi-query approach)

- **Error:** `The field 'R43' of the record wasn't found`
- **Cause:** A sheet/table name parsed to a token like "R43". In the four-query setup, `fnMonthKeyFromTableName` and `MonthlyActivity` were updated to handle invalid names (try/otherwise null, filter out null MonthKey).
- **Single-query:** ESU_13Month uses Tables only and inline month parsing; stray names are excluded by the table-name filter.

### Use ESU in a separate .pbix first

To avoid other report errors while fixing them:

1. **File → New** → new Power BI Desktop file.
2. Add **only** the ESU query (paste `ESU_13Month.m` into one Blank Query).
3. Refresh, then Save. Publish this .pbix as a separate ESU report if needed, or merge into the main report later.

### Other errors (Cannot find table, column, DAX)

Those are **report/model issues**, not ESU: add or fix the missing tables, columns, and DAX in the main report.

---

## Summary

| Goal | Action |
|------|--------|
| Simple 13-month ESU table with Status, ItemKey, Month_Year | Use **ESU_13Month.m** only (one query). |
| Dimension table with SortKey for custom sort | Use the four queries (fnCleanText, fnMonthKeyFromTableName, TrackedItems, MonthlyActivity). |
| Empty preview | Ensure monthly data is in **Excel Tables** with names like _26_JAN; ensure _mom_hacsoc has a **status** column (and ItemKey if desired). |
| Save/publish fails with many errors | Fix main report tables/columns/DAX, or use a separate .pbix for ESU. |
