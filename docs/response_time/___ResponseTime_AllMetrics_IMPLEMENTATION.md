# ___ResponseTime_AllMetrics — Implementation Guide

**Source:** `KB_Shared\04_output\Claude-Power_BI_response-time_metrics_implementation\2026_03_06_14_01_12_Claude-Power_BI_response-time_metrics_implementation_transcript.md`

**M code:** `m_code/response_time/___ResponseTime_AllMetrics.m`

**Status:** ✅ Implemented in live PBI model 2026-03-06 (via Claude MCP). Three old tables disabled; measures moved; date relationships created.

---

## Overview

Consolidates the three response-time queries into one long table. Replaces the three separate matrix visuals with:
- **Option A:** Single stacked bar + line combo with small multiples by Response_Type
- **Option B:** Line chart + conditional-format matrix (recommended for council/admin)

---

## Power BI Setup (Completed 2026-03-06)

1. **Create query** — ✅ Done via Claude MCP
2. **Set pReportMonth** — ✅ Parameter exists
3. **Sort columns:**
   - `Metric_Label` → Sort by Column → `Metric_Sort` ✅
   - `MonthName` → Sort by Column → `Date_Sort_Key` ✅
   - `Response_Type` → Add calc column `Response_Type_Sort` (Emergency=1, Urgent=2, Routine=3), then Sort by Column
4. **Disable load** on the three old queries — ✅ Done (`___ResponseTimeCalculator`, `___ResponseTime_OutVsCall`, `___ResponseTime_DispVsCall`)
5. **Validate row count** — ✅ 117 = 39+39+39
6. **Measures moved** — RT Average/OutVsCall/DispVsCall Title & Subtitle → `___ResponseTime_AllMetrics`
7. **Date relationships** — `Date_Sort_Key` and `Date` → LocalDateTables

---

## DAX — Table Name

The transcript uses `'ResponseTime_AllMetrics'` in DAX. In Power BI, the table name is **`___ResponseTime_AllMetrics`** (from the query name). Update DAX accordingly:

```dax
Current_Month_Total_Response = 
CALCULATE(
    AVERAGE('___ResponseTime_AllMetrics'[Average_Response_Time]),
    '___ResponseTime_AllMetrics'[Metric_Label] = "Total Response",
    '___ResponseTime_AllMetrics'[Date_Sort_Key] = MAX('___ResponseTime_AllMetrics'[Date_Sort_Key])
)
```

---

## Response_Type_Sort (Calc Column)

```dax
Response_Type_Sort = 
SWITCH(
    '___ResponseTime_AllMetrics'[Response_Type],
    "Emergency", 1,
    "Urgent", 2,
    "Routine", 3,
    99
)
```

---

## Visual Mappings (Option B — Council Layout)

| Visual | Fields |
|--------|--------|
| **Line chart** | X: Date_Sort_Key, Y: Average_Response_Time, Legend: Metric_Label, Small Multiples: Response_Type |
| **Matrix** | Rows: Response_Type, Metric_Label; Columns: MonthName; Values: Response_Time_MMSS |

---

## Quality Checks

1. Row count = 3 × single-metric table
2. Dispatch Queue + Travel Time ≈ Total Response (additivity)
3. Panel order: Emergency → Urgent → Routine
4. Y-axis scale consistent across small multiples
5. Spot-check 3 cells vs. old matrices
