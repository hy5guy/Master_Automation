# Summons Post-ETL Validation -- Claude MCP Investigation Prompt

> **Purpose:** Refresh the 4 summons tables after a full ETL re-run that added Feb 2026, fixed TYPE classification, and fixed a BOM parsing bug. Then investigate specific discrepancies.
>
> **Model:** `2026_02_Monthly_Report` (currently open in Power BI Desktop)
>
> **Parameter:** `pReportMonth = #date(2026, 3, 1)` (report month is March; visuals target previous complete month = Feb 2026)
>
> **Date:** 2026-03-10

---

## Context: What Changed in the ETL

The underlying data file `summons_slim_for_powerbi.csv` was regenerated with these fixes:

1. **Feb 2026 data added** — 2,849 new records (P=2,354, M=421, C=74)
2. **TYPE classification fixed** — previously, a statute-lookup function was reclassifying ~2,576 Parking (P) tickets as Criminal/Complaint (C) and splitting Moving (M) into subcategories. Now uses the raw `Case Type Code` from the e-ticket export directly (M/P/C only).
3. **Feb 2025 BOM fix** — recovered 2,743 rows that were being lost due to a corrupt FIXED CSV header.
4. **All 13 months present**: 01-25 through 02-26 (July 2025 has only 17 straggler records — true gap month, no e-ticket export).

---

## Step 1: Update pReportMonth Parameter

The report month needs to advance to March 2026 so the "previous complete month" visuals target February 2026.

```
named_expression_operations -> Get -> references: [{ "name": "pReportMonth" }]
```

Check the current value. If it's `#date(2026, 2, 1)`, update it:

```
named_expression_operations -> Update
definitions: [{
  "name": "pReportMonth",
  "expression": "#date(2026, 3, 1) meta [IsParameterQuery=true, Type=\"Date\", IsParameterQueryRequired=true]"
}]
```

---

## Step 2: Refresh All 4 Summons Tables

```
table_operations -> Refresh -> references: [{ "name": "summons_13month_trend" }]
table_operations -> Refresh -> references: [{ "name": "summons_all_bureaus" }]
table_operations -> Refresh -> references: [{ "name": "summons_top5_moving" }]
table_operations -> Refresh -> references: [{ "name": "summons_top5_parking" }]
```

After each refresh, verify no errors:

```
table_operations -> Get -> references: [{ "name": "summons_13month_trend" }, { "name": "summons_all_bureaus" }, { "name": "summons_top5_moving" }, { "name": "summons_top5_parking" }]
```

All should show "Ready" state.

---

## Step 3: Validate 13-Month Trend (Department-Wide)

```
dax_query_operations -> Execute
query:
  EVALUATE
  SUMMARIZECOLUMNS(
    'summons_13month_trend'[Month_Year],
    'summons_13month_trend'[TYPE],
    "Tickets", SUM('summons_13month_trend'[TICKET_COUNT])
  )
```

**Show me the full result table.** Expected:

| Month_Year | What I Expect |
|-----------|--------------|
| 02-25 | M ~324, P ~2,368 |
| 03-25 | M ~445, P ~3,095 |
| 04-25 | M ~517, P ~3,101 |
| 05-25 | M ~340, P ~3,071 |
| 06-25 | M ~337, P ~2,955 |
| 08-25 | M ~842, P ~3,437 |
| 09-25 | M ~503, P ~4,041 |
| 10-25 | M ~416, P ~3,490 |
| 11-25 | M ~416, P ~2,947 |
| 12-25 | M ~442, P ~2,893 |
| 01-26 | M ~418, P ~3,444 |
| **02-26** | **M ~421, P ~2,354** |

- If 02-26 is missing, the pReportMonth parameter wasn't updated or the refresh failed.
- If any month shows ticket counts of 1 or 2, the `List.Sum([TICKET_COUNT])` fix is not applied.
- July 2025 may or may not appear (only 17 straggler records).
- January 2025 should appear (~3,323 total).

---

## Step 4: Validate All Bureaus (Feb 2026)

```
dax_query_operations -> Execute
query: EVALUATE 'summons_all_bureaus'
```

**Show me the full result table.** For Feb 2026 I expect:

| Bureau | M | P | Notes |
|--------|---|---|-------|
| CSB | ~5 | 0 | Small bureau |
| PATROL DIVISION | ~188 | ~300 | Includes HOUSING, OSO, PATROL BUREAU via consolidation |
| TRAFFIC BUREAU | ~230 | ~2,022 | |
| **SSOCC** | **0** | **4** | **R. POLSON #0738 — temp adjusted duty assignment. This is the key check.** |
| DETECTIVE BUREAU | ~1 | 0 | Small |

**Critical checks:**
- **Does SSOCC appear as its own row?** Polson (badge 0738) has 4 Parking summons (city ordinance 88-6D(2) Fire Lanes and 117-3(F)) classified as TYPE=P. She's assigned to SSOCC in the Assignment Master.
- **M total across bureaus**: Should be ~419. Dept-wide M is 421. The gap of 2 is **K. PERALTA #0311** (Community Outreach team, no WG2 mapped) — these are filtered out by the `[WG2] <> null` filter. This is expected.
- **P total across bureaus**: Should be ~2,326. Dept-wide P is 2,354. The gap of 28 is also Peralta (28 P tickets with no WG2).

---

## Step 5: Validate Top 5 Moving & Parking

```
dax_query_operations -> Execute
query: EVALUATE 'summons_top5_moving'
```

```
dax_query_operations -> Execute
query: EVALUATE 'summons_top5_parking'
```

**Show me both result tables.** Expected for Feb 2026:

**Top 5 Moving:** 5 officers, counts > 10, no PEO badges (2000-series). Likely includes JACOBSEN, ONEILL, LOPEZ, FRANCAVILLA.

**Top 5 Parking:** 5 officers, counts > 50. Likely includes ONEILL, TORRES, MATTALIAN, SQUILLACE, RIZZI. R. POLSON should NOT appear here (only 4 P tickets — not enough for top 5).

---

## Step 6: Investigate Historical Month Discrepancies

**IMPORTANT CONTEXT:** The numbers for months 02-25 through 05-25 will NOT match the January 2026 backfill report values. This is expected and correct. Here's why:

The **old** ETL pipeline used statute-based classification that:
- Reclassified ~2,576 Parking tickets as "C" (Complaint) via ordinance substring matching
- Split Moving violations into subcategories (License/Registration, Moving Violation, Equipment, DWI/DUI, Other)

The **new** ETL uses the raw `Case Type Code` (M/P/C) from the e-ticket export, which is more accurate.

Run this to see the current TYPE=C distribution (should be small — real criminal/complaint cases only):

```
dax_query_operations -> Execute
query:
  EVALUATE
  SUMMARIZECOLUMNS(
    'summons_13month_trend'[Month_Year],
    'summons_13month_trend'[TYPE],
    "Tickets", SUM('summons_13month_trend'[TICKET_COUNT])
  )
```

For each month, C should be a small fraction (50-90 per month). If C is in the thousands for any month, the old classification is still active (should not happen after refresh).

---

## Step 7: Spot-Check Feb 2026 M/P/C Split

```
dax_query_operations -> Execute
query:
  EVALUATE
  SUMMARIZECOLUMNS(
    'summons_13month_trend'[Month_Year],
    'summons_13month_trend'[TYPE],
    "Tickets", SUM('summons_13month_trend'[TICKET_COUNT])
  )
```

For 02-26 specifically:
- **M = 421** (Moving)
- **P = 2,354** (Parking) — was inflated to C in old pipeline, now correct
- **C = 74** (Criminal/Complaint)
- **Total = 2,849**

If P is much lower (e.g., ~500) and C is much higher (e.g., ~2,600), the `_classify_violation` fix was not applied in the CSV — re-run the ETL.

---

## Summary Report

After running all steps, give me a summary table:

| Check | Status | Detail |
|-------|--------|--------|
| pReportMonth updated | PASS/FAIL | New value? |
| Tables refreshed | PASS/FAIL | Any errors? |
| 13-month trend | PASS/FAIL | How many months? 02-26 present? Any showing 1 or 2? |
| SSOCC in all_bureaus | PASS/FAIL | Does SSOCC row appear? P=4? |
| All bureaus M/P totals | PASS/FAIL | M total? P total? Gap from dept-wide? |
| Top 5 moving | PASS/FAIL | 5 officers? No PEOs? |
| Top 5 parking | PASS/FAIL | 5 officers? Counts reasonable? |
| Feb 2026 M/P/C split | PASS/FAIL | M=? P=? C=? |
| C distribution | PASS/FAIL | C < 100 per month for all months? |

---

## Known Issues (Not Bugs)

1. **K. PERALTA #0311** (Community Outreach) has no WG2 in `Assignment_Master_V2.csv`. Her 30 Feb 2026 tickets (2 M + 28 P) are in the dept-wide trend but not in all_bureaus. Decision pending on whether to assign her a WG2.

2. **July 2025** has only 17 rows (no e-ticket export exists). These are straggler records from other monthly files with July issue dates.

3. **Historical months (02-25 through 05-25)** will show HIGHER M and P counts than the January 2026 report backfill. This is because the TYPE classification was fixed — the old pipeline undercounted M and P by misclassifying tickets. The new values are more accurate.

4. **Consolidation logic** in `summons_all_bureaus` merges HOUSING, OFFICE OF SPECIAL OPERATIONS, and PATROL BUREAU into "PATROL DIVISION". SSOCC, DETECTIVE BUREAU, and CSB are NOT consolidated — they appear as their own rows (if they have data for the month).
