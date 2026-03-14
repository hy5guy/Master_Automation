# Claude MCP Prompt: Fix Traffic Visual Not Showing Parking Fees (02-26)

**Use when:** Excel is correct (AH34 = $115,283.87) but the Power BI visual does not show Parking Fees for February 2026.

**Prerequisite:** Connect to Power BI Desktop (e.g. `2026_02_Monthly_Report.pbix`). Ensure `pReportMonth = #date(2026, 2, 1)`.

---

## Copy-Paste Prompt for Claude (Power BI MCP)

```
The Traffic Bureau visual is not showing Parking Fees Collected for 02-26 ($115,283.87). Excel is confirmed correct — _mom_traffic table has the value in AH34. The issue is on the Power BI side.

Please:

1. **Get** the `___Traffic` table partition expression using partition_operations (operation Get) or table_operations (operation Get).

2. **Verify** the M code:
   - Uses `List.Skip(TrafficColNames, 1)` for TrafficMonthCols (dynamic — picks up all columns including 02-26). No static column list.
   - Uses `type number` (not Int64.Type) for month columns in the Changed Type step — Parking Fees has decimals.
   - If it uses Int64.Type, update to type number.

3. **Update** the partition if needed. The correct Changed Type step is:
   ```powerquery
   #"Changed Type" = Table.TransformColumnTypes(
       _mom_traffic_Table, {{"Tracked Items", type text}} & List.Transform(TrafficMonthCols, each {_, type number})
   ),
   ```

4. **Check** the Value column in the tabular model — it should be Double, not String. If String, update to Double.

5. **Refresh** the `___Traffic` table (Full refresh).

6. **Verify** with a DAX query: Parking Fees Collected for Period 02-26 should return 115283.87.
```

---

## Quick Checklist

| Step | Action |
|------|--------|
| 1 | Connect to .pbix |
| 2 | Get ___Traffic partition |
| 3 | Ensure `type number` (not Int64) for month columns |
| 4 | Ensure Value column is Double in model |
| 5 | Refresh ___Traffic |
| 6 | Verify DAX: Parking Fees Collected, 02-26 = 115283.87 |

---

## If Still Not Showing After Fix

- Refresh All (not just ___Traffic)
- Close and reopen the .pbix
- Confirm no page/visual filters on the Traffic report page
- Confirm pReportMonth = #date(2026, 2, 1)
