# ESU Power Query

## Use one query: ESU_13Month

Use **ESU_13Month.m** only. You do **not** need MonthlyActivity, TrackedItems, fnCleanText, or fnMonthKeyFromTableName.

1. In Power BI: **Get data → Blank Query**.
2. Open **Advanced Editor** and paste the full contents of `ESU_13Month.m`.
3. Name the query (e.g. `ESU_13Month`).
4. **Refresh.**

**Result:** One table with:

| Column     | Description                          |
|-----------|--------------------------------------|
| MonthKey  | First day of month (date)            |
| TrackedItem | Tracked item name (text)           |
| Total     | Count/value (number)                 |
| Status    | From _mom_hacsoc (e.g. Active)       |
| ItemKey   | From _mom_hacsoc (identifier)        |
| Month_Year| MM-yy (e.g. 01-26)                   |

**Rolling 13 months:** Last 13 complete months. If the workbook has only older months, the query returns all loaded months so you still get data; filter by MonthKey in the report if needed.

**Workbook requirements:**
- **Source:** `Shared Folder\Compstat\Contributions\ESU\ESU.xlsx`
- Monthly data in **Excel Tables** (Ctrl+T), names like **\_26_JAN**, **\_25_FEB** (leading underscore, YY_MMM).
- Each monthly table: column that trims to **Tracked Items**, and **Total**.
- **\_mom_hacsoc** table/sheet with columns that trim to **Tracked Items**, **Status**, and **ItemKey** (Status is required; column name is matched case-insensitively, e.g. "status" or "Status").

---

## Optional: MonthlyActivity + helpers

Only if you need the **dimension table with SortKey** (custom sort order in visuals), use the four queries:

- `fnCleanText.m`, `fnMonthKeyFromTableName.m`, `TrackedItems.m`, `MonthlyActivity.m`

Load the two functions first, then TrackedItems, then MonthlyActivity. For a simple 13-month table with Status and ItemKey, **ESU_13Month alone is enough.**
