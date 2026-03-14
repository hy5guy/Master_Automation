# Claude in Excel: Traffic Visual Not Showing Parking Fees

**Use when:** Parking fees were added to the MoM sheet in Traffic_Monthly.xlsx but the Power BI visual does not show them.

**File:** `Traffic_Monthly.xlsx`  
**Table:** `_mom_traffic`

---

## Copy-Paste Prompt for Claude in Excel

```
The Power BI visual for Traffic Bureau is not showing the Parking Fees Collected value ($115,283.87) for February 2026, even though we fixed the formulas on the MoM sheet. The Power BI query loads from the Excel table named _mom_traffic.

Please diagnose and fix:

1. **Locate the _mom_traffic table**
   - Find the Excel Table named _mom_traffic (Table Design → Table Name, or Formulas → Name Manager).
   - Note which sheet it's on (likely "MoM").

2. **Check if the table includes the 02-26 column**
   - The Power BI M code unpivots all columns except "Tracked Items" and expects column headers in MM-YY format (e.g. 01-25, 02-25, 02-26).
   - List the column headers of _mom_traffic. Is there a column for 02-26 (February 2026)?
   - If 02-26 is missing: The table range may not include the new column. Expand the table (Table Design → Resize Table) to include the 02-26 column.

3. **Verify the Parking Fees value**
   - Find the "Parking Fees Collected" row in _mom_traffic.
   - Check the cell in the 02-26 column. Does it show $115,283.87 (or 115283.87)?
   - Ensure the cell is a number, not text (no leading apostrophe; format Number or Currency).

4. **Check column header format**
   - Power BI parses Period as: first 2 chars = month, last 2 chars = year. So "02-26" works.
   - If the column is named "2-26" or "Feb-26" or "2026-02", the parsing may fail. Rename to "02-26" if needed.

5. **Ensure table range is correct**
   - The table must include: Tracked Items column + all month columns (01-25 through 02-26) + optionally Total.
   - If there's a "Total" column, Power BI will try to parse it as a date and filter it out (that's OK).
   - The critical columns are the month columns in MM-YY format.

6. **Save and close**
   - Save the workbook. Close it if Power BI has it locked (Power BI holds a connection).
   - Then refresh the ___Traffic query in Power BI.
```

---

## After Excel Fix: Power BI Steps

1. **Close** Traffic_Monthly.xlsx if it's open (Power BI may have it locked).
2. **Refresh** the ___Traffic query in Power BI (Right-click ___Traffic → Refresh, or Refresh All).
3. **Verify** the visual shows Parking Fees Collected for 02-26.

---

## If Still Not Showing: M Code Check

The ___Traffic M code types all month columns as `Int64.Type`, which truncates decimals. Parking Fees needs `type number`. If the MCP already fixed this in the .pbix, you're good. If not, update the partition expression in Power BI:

Change:
```powerquery
List.Transform(TrafficMonthCols, each {_, Int64.Type})
```
To:
```powerquery
List.Transform(TrafficMonthCols, each {_, type number})
```

This preserves $115,283.87 with full decimal precision.
