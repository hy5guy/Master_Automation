# Claude MCP Prompt: Fix Department-Wide 07-25 Backfill Blank P Cell

**Copy-paste this into a new Claude Desktop conversation (with Power BI MCP enabled) to apply the summons_13month_trend M code fix.**

---

## Task

Connect to Power BI Desktop and update the `summons_13month_trend` partition with the M code below. Then refresh the table.

**Context:** The Department-Wide Summons visual shows 07-25 with M=17 but P=blank. July 2025 has only 17 straggler e-ticket records (all Moving); no Parking data exists. The fix appends filler rows for missing (Month_Year, TYPE) combinations so P and C show 0 instead of blank.

---

## Steps

1. **Connect** to Power BI Desktop (use `mcp_powerbi-modeling-mcp_connection_operations` with operation `Connect` if not already connected).

2. **Update** the `summons_13month_trend` partition with the M expression below. Use `mcp_powerbi-modeling-mcp_partition_operations` or `mcp_powerbi-modeling-mcp_table_operations` as appropriate.

3. **Refresh** the `summons_13month_trend` table.

4. **Verify** that the Department-Wide visual now shows 07-25 with M=17, P=0, Total=17 (no blank P cell).

---

## M Code to Apply

Copy the full contents of `m_code/summons/summons_13month_trend.m` into the partition. The key addition (after `AddConsolidatedBureau`) appends filler rows for missing (Month_Year, TYPE) so 07-25 P shows 0 not blank.

---

## Notes

- Ensure Power BI Desktop has the report open.
- The filler rows are appended to the original data; relationships and measures that use ISSUE_DATE, WG2, etc. continue to work.
