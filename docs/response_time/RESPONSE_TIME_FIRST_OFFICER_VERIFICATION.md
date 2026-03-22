# Response Time: Time Out − Time of Call & First-Responding-Officer Verification

**Date:** 2026-02-26  
**Purpose:** Confirm that (1) **Time Out − Time of Call** is the correct formula for total response time, and (2) all three response time queries use **only the first responding officer** (first-arriving unit) per incident.

---

## 1. Is “Time Out − Time of Call” correct?

**Yes.** Per **Response Time Calculation Methods – Executive Comparison** (Jan 15, 2026):

| Method | Formula | Measures | Use |
|--------|---------|----------|-----|
| **Officer Response Time** | Time Out − Time Dispatched | Dispatch → arrival | Patrol efficiency |
| **Total Response Time** | **Time Out − Time of Call** | **Call → arrival** | **Citizen experience** |

So:

- **___ResponseTimeCalculator** (Time Out − Time Dispatched) = officer travel time (dispatch to on scene).
- **___ResponseTime_OutVsCall** (Time Out − Time of Call) = **total response time** from when the call is received until an officer is on scene. That is the correct definition for “from time received to on scene.”

The formula itself is correct for the OutVsCall visual.

---

## 2. Are we using only the first responding officer?

**By design, yes.** The documented standard is **one response time per incident**, using the **first-arriving unit**.

### Executive / ETL documentation

- **Response Time ETL – Executive Packet:**  
  “Deduplicate by ReportNumberNew. **Keep the first officer response per call.**”
- **Response Time ETL – Comparison Table:**  
  “Same call counted multiple times (once per responding officer)” was the problem; the fix is “Each call counted once (deduplicated)” and “**Keep the first officer response per call**.”
- **Response Time Calculation Correction – Executive Summary:**  
  “One response counted per incident” and “Duplicate officer responses removed.”

So the intended logic is: **one row per incident = one response time**, and that row is the **first officer response** (first-arriving unit).

### How “first” is defined in code

For **first-arriving unit** (not just “first row in file”):

1. **Sort** by `ReportNumberNew` and **Time Out** (arrival on scene).
2. **Deduplicate** by `ReportNumberNew` with **keep='first'**.

Then the kept row is the unit that arrived on scene **earliest** for that incident.

- **process_cad_data_13month_rolling.py** (13‑month rolling ETL): The Feb 2026 fix added this sort before `drop_duplicates`: sort by `['ReportNumberNew', 'Time Out']`, then `drop_duplicates(subset=['ReportNumberNew'], keep='first')`. So that script uses **first-arriving unit**.
- **response_time_fresh_calculator.py** (Master_Automation): Same pattern — `sort_values(['ReportNumberNew', 'Time Out'])` then `drop_duplicates(subset=['ReportNumberNew'], keep='first')`. Docstring: “first-arriving unit via Time Out sort” and “First-arriving unit deduplication (sort by Time Out before drop_duplicates).”

So wherever this pattern is used, **Time Out**, **Time Dispatched**, and **Time of Call** for that incident all come from the **same** row: the first-arriving unit. That gives:

- Time Out − Time Dispatched (Calculator)
- Time Out − Time of Call (OutVsCall)
- Time Dispatched − Time of Call (DispVsCall)

all from the **first responding officer** for that call.

---

## 3. Source of the Power BI data (response_time_all_metrics)

The three Power BI queries (**___ResponseTimeCalculator**, **___ResponseTime_OutVsCall**, **___ResponseTime_DispVsCall**) read from:

`PowerBI_Data\Backfill\response_time_all_metrics\`

Those CSVs are produced by:

**`02_ETL_Scripts\Response_Times\response_time_batch_all_metrics.py`**

That script is **outside** the Master_Automation repo. To be sure that **Time Out − Time of Call** (and the other two metrics) also use only the first responding officer:

### Verify the batch script

1. Open **`02_ETL_Scripts\Response_Times\response_time_batch_all_metrics.py`**.
2. Find the deduplication step (e.g. step that reduces to one row per incident).
3. Confirm it does **both**:
   - Sort by **ReportNumberNew** and **Time Out** (so the first-arriving unit is first within each incident).
   - Then **drop_duplicates(subset=['ReportNumberNew'], keep='first')** (or equivalent).

If the batch script uses that pattern **before** computing the three metrics (Time Out − Time Dispatched, Time Out − Time of Call, Time Dispatched − Time of Call), then:

- **Time Out − Time of Call** is correct as “total response time” and  
- All three metrics are based on **only the first responding officer** (first-arriving unit) per incident.

If the batch script does **not** sort by `Time Out` before deduplication, then it may be keeping “first row in file” instead of “first-arriving unit.” In that case, update the batch script to match the logic in `process_cad_data_13month_rolling.py` and `response_time_fresh_calculator.py` (sort by `ReportNumberNew`, `Time Out`; then keep first per `ReportNumberNew`).

---

## 4. Summary

| Question | Answer |
|----------|--------|
| Is **Time Out − Time of Call** the right formula for total response (call to on scene)? | **Yes.** It matches “Total Response Time” in the Executive Comparison doc. |
| Are we using only the **first responding officer**? | **By design, yes.** ETL docs and the two scripts above use first-arriving unit (sort by Time Out, keep first per ReportNumberNew). |
| What should I check? | Confirm **response_time_batch_all_metrics.py** uses the same first-arriving-unit deduplication before writing the CSVs that feed the three Power BI queries. |

---

**References**

- `docs/response_time/Response Time Calculation Methods – Executive Comparison.pdf`
- `docs/response_time/Response Time ETL - Executive Packet.pdf`
- `docs/response_time/Response Time ETL Filtering Implementation.pdf`
- `docs/response_time/2026_01_14_18_39_05_Response Time ETL - Comparison Table.pdf`
- `scripts/response_time_fresh_calculator.py` (lines 220–225: sort + drop_duplicates)
- Chatlog: Claude-February_2026_ETL_Cycle_Response_Times_Fix (first-arriving unit fix in process_cad_data_13month_rolling.py)
