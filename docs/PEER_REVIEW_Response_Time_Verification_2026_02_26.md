# Peer Review — Response Time Verification (Opus Independent Review)

**Date:** 2026-02-26  
**Reviewer:** Claude Opus 4.6 (independent peer review of Claude Sonnet analysis)  
**Analyst:** R. A. Carucci, Principal Analyst, Hackensack PD  
**Version Reviewed:** Master_Automation v1.17.14

---

## Task 1: Confirm or Correct Each of Sonnet's 5 Findings

### Finding 1 — Formula Correctness: ✅ CONFIRMED

Sonnet's formula mapping is correct and verified against multiple sources:

| Visual | Formula | Measures |
|--------|---------|----------|
| Dispatch to On Scene | Time Out − Time Dispatched | Officer travel time |
| Time Received to On Scene | Time Out − Time of Call | Total citizen experience |
| (Gap / new visual) | Time Dispatched − Time of Call | Dispatch processing time |

**Evidence:**
- The "Response Time Calculation Methods – Executive Comparison" document defines Officer Response Time as `Time Out − Time Dispatched` and Total Response Time as `Time Out − Time of Call`.
- The M code in `___ResponseTimeCalculator.m` filters `Metric_Type = "Time Out - Time Dispatched"`.
- The M code in `___ResponseTime_OutVsCall.m` filters `Metric_Type = "Time Out - Time of Call"`.
- The M code in `___ResponseTime_DispVsCall.m` filters `Metric_Type = "Time Dispatched - Time of Call"`.
- The batch Python script `METRIC_CONFIGS` array confirms all three calculations.

The algebraic relationship holds: (Time Out − Time of Call) = (Time Out − Time Dispatched) + (Time Dispatched − Time of Call). **Confirmed.**

---

### Finding 2 — Record Count Mismatch: ✅ CONFIRMED — Expected Behavior, Minor Nuance Added

Sonnet is correct that record counts differ per metric because each metric independently filters for valid timestamps in both its required columns. A record may have a valid `Time Out` and `Time of Call` but a null `Time Dispatched`, so it would count for the OutVsCall metric but not the Calculator or DispVsCall metrics.

**From the batch ETL `calculate_metric()` function:**
```python
valid = df[
    df["_diff_mins"].notna() &
    (df["_diff_mins"] > MIN_RESPONSE_MINS) &
    (df["_diff_mins"] <= MAX_RESPONSE_MINS)
]
```

This means each metric filters on:
- Its own pair of timestamps being non-null
- The computed difference being > 0 and ≤ 10 minutes

**Assessment:** This is expected and defensible behavior. Forcing all three metrics to use the exact same record set would artificially exclude valid data from one metric because another metric's timestamps were missing. The tradeoff is that the gap (DispVsCall) will not perfectly equal OutVsCall minus Calculator for a given month/type. This is a **minor data footnote**, not a concern worth flagging to admin — though it could be documented internally for anyone who tries to reconcile the three numbers.

---

### Finding 3 — CRITICAL: Missing Sort in Batch ETL: ✅ CONFIRMED — This is a Real Bug

**This is Sonnet's most important finding and I independently confirm it.**

**The code in `response_time_batch_all_metrics.py`, `load_and_clean()` function:**
```python
before_dedup = len(df)
df = df.drop_duplicates(subset="ReportNumberNew", keep="first").reset_index(drop=True)
```

There is **no** `sort_values()` call before `drop_duplicates()`. This means for multi-unit incidents (28.2% of calls per the v1.15.9 changelog), the script keeps whichever row happens to appear first in the Excel file — **not** the first-arriving unit sorted by `Time Out`.

**The correct pattern (established in v1.15.9 for `process_cad_data_13month_rolling.py`):**
```python
df = df.sort_values(["ReportNumberNew", "Time Out"])
df = df.drop_duplicates(subset="ReportNumberNew", keep="first")
```

**Timeline of the bug:**
- **2026-02-18 (v1.15.9):** The first-arriving-unit fix was applied to `process_cad_data_13month_rolling.py`. CHANGELOG explicitly documents: Before = file order, After = sort by Time Out.
- **2026-02-26 (v1.17.11):** The NEW `response_time_batch_all_metrics.py` script was created. It did NOT inherit the sort fix from v1.15.9. The dedup line uses the pre-fix pattern.
- **2026-02-26 (v1.17.12–1.17.14):** Multiple subsequent versions focused on CallType mapping and M code, but the dedup flaw was not caught.

**Impact assessment:**
- All 25 monthly CSVs currently in `PowerBI_Date\Backfill\response_time_all_metrics\` are potentially affected.
- The impact depends on the row ordering of the source Excel files. If Excel rows happen to be sorted by `Time Out` ascending within each `ReportNumberNew`, the current output could be accidentally correct. If rows are in some other order (e.g., unit ID, badge number, insertion order), the response times for 28.2% of incidents may not reflect the first-arriving unit.
- For averages across thousands of records, the effect may be small (random selection vs. minimum selection tends to produce slightly higher averages). But for individual incident accuracy and methodology defensibility, this must be fixed.

**Confidence level: HIGH.** I reviewed the full `load_and_clean()` function in project knowledge. There is no sort by `Time Out` anywhere before the `drop_duplicates` call.

---

### Finding 4 — Fix Scope: ✅ CONFIRMED with One Clarification

Sonnet is correct that:
1. The fix is adding one sort line before the existing `drop_duplicates` in `response_time_batch_all_metrics.py`
2. Then re-running the script to regenerate all 25 CSVs
3. No M code changes are needed (M code reads from the CSVs; it doesn't do dedup)
4. No DAX changes needed

**The fix:**
```python
# In load_and_clean(), BEFORE the drop_duplicates line, add:
df = df.sort_values(["ReportNumberNew", "Time Out"])
df = df.drop_duplicates(subset="ReportNumberNew", keep="first").reset_index(drop=True)
```

**Clarification Sonnet missed:** After re-running the batch ETL, you should:
1. Compare the old vs. new CSVs to quantify the actual magnitude of change
2. Document the delta in the CHANGELOG (e.g., "Emergency avg shifted from X:XX to Y:YY for month Z")
3. Refresh Power BI after the new CSVs are in place

This is a quality assurance step, not a technical requirement.

---

### Finding 5 — Emergency Dispatch Delay Explanation: ⚠️ PARTIALLY CONFIRMED — Additional Factors

Sonnet attributed the larger Emergency DispVsCall (2:54) vs. Routine (1:05) to "dispatcher triage/coordination requirements." This is **one** valid explanation but is **incomplete**.

**Additional factors visible in the code and documentation:**

1. **Multi-unit dispatch overhead:** Emergency calls frequently dispatch multiple units (28.2% multi-unit rate overall, likely higher for Emergency). The dispatcher must coordinate multiple assignments, contributing to longer queue times.

2. **Call verification and information gathering:** Emergency calls often require the dispatcher to obtain critical safety information (weapons, injuries, suspect description) before dispatching, per standard operating procedures.

3. **Possible data artifact from the dedup bug (Finding 3):** Because the batch script doesn't sort by `Time Out` before dedup, the DispVsCall metric may be computed from a non-first-arriving unit's `Time Dispatched` value. If later-dispatched units have a larger gap between `Time of Call` and their individual `Time Dispatched`, this could inflate the Emergency DispVsCall number. This is speculative but worth noting — the fix in Finding 3 may change these numbers.

4. **Routine calls may use self-dispatch or quicker assignment:** Officers may self-initiate on routine calls (e.g., traffic stops, directed patrols) with minimal dispatcher involvement, producing near-zero processing time for those records and pulling the average down.

**Recommendation for admin:** Present the higher Emergency dispatch time as expected, driven by the complexity and safety requirements of emergency call processing. Do not over-explain — command staff understands that emergency calls require more dispatcher work.

---

## Task 2: What Sonnet Missed

### Item A — The `Median_Minutes` Column Is Computed but Not Exposed in M Code

The batch ETL calculates and writes `Median_Minutes` to each CSV, but none of the three M code queries expose it. The DAX measures all use `AVERAGE` on `Average_Response_Time`. Median is a more robust measure for skewed distributions (response times are right-skewed). Consider adding median-based DAX measures or at least documenting that median data is available in the CSVs for future use.

### Item B — The `OutVsCall` and `DispVsCall` M Queries Lack 13-Month Window Filtering

Looking at the M code, `___ResponseTimeCalculator.m` has full rolling 13-month window logic using `pReportMonth`:
```
EndDate = Date.AddMonths(DateTime.Date(pReportMonth), -1)
StartDate = Date.AddMonths(EndDate, -12)
```

But `___ResponseTime_OutVsCall.m` and `___ResponseTime_DispVsCall.m` do NOT have this windowing logic — they load ALL data from the folder without date filtering. This means the OutVsCall and DispVsCall visuals will show all 25 months instead of the rolling 13-month window, creating an inconsistency with the Calculator visual.

**This is a second bug** that should be fixed by copying the windowing logic from `___ResponseTimeCalculator.m` into the other two queries.

### Item C — The 0-10 Minute Filter Range May Warrant Disclosure

The batch ETL filters response times to `> 0 and ≤ 10 minutes`. Any response over 10 minutes is excluded. This is a reasonable outlier filter, but it should be documented in any admin presentation because:
- Some legitimate emergency responses (e.g., remote parts of the jurisdiction, extended scene searches) could exceed 10 minutes
- The filter is applied uniformly to all three metrics, which is appropriate

### Item D — 2024 Data Quality Caveat

Per the CHANGELOG v1.17.12, the 2024 CAD data had `Response Type` populated for less than 1% of records. The CallType mapping resolved 99.99% of these, but the 2024 data relies almost entirely on the incident-to-response-type mapping rather than original CAD classification. The 2025+ data is more directly sourced. This matters for year-over-year comparisons.

---

## Task 3: Data Defensibility Assessment

### Should the department present the current backfill data now?

**Recommendation: HOLD the current data. Fix first, then present.**

Rationale:

1. **The dedup bug (Finding 3) affects methodology credibility.** If administration is told "we use the first-arriving officer" but the code doesn't actually sort for that, and this is later discovered, it undermines trust in all analytics.

2. **The fix is trivial — one line + re-run.** This is not a weeks-long engineering effort. The fix can be implemented and validated in under an hour.

3. **The magnitude of the impact is unknown.** Without comparing pre-fix vs. post-fix CSVs, we cannot say the numbers are "close enough." The 28.2% multi-unit rate means nearly 1 in 3 incidents could be affected.

4. **The M code windowing bug (Item B above) means two of three visuals are showing incorrect date ranges.** This compounds the issue.

**Recommended sequence:**
1. Fix `response_time_batch_all_metrics.py` (add sort line) — 5 minutes
2. Fix OutVsCall and DispVsCall M code (add 13-month window) — 15 minutes
3. Re-run batch ETL to regenerate all 25 CSVs — ~10 minutes
4. Compare old vs. new CSVs to quantify delta — 15 minutes
5. Refresh Power BI and validate visuals — 10 minutes
6. Present to admin with confidence

**Total time to fix: ~1 hour.** Worth it for data integrity.

---

## Task 4: Admin Brief

*(See separate one-page document below)*

---

## Items I Cannot Confirm Without Additional Files

1. **`response_time_fresh_calculator.py` full source code** — I can see references to it in documentation confirming it has the correct sort+dedup pattern, but the full source was not in project knowledge. The VERIFICATION.md doc and CHANGELOG both reference it consistently, so I have high confidence it's correct.

2. **Actual CSV sample data** — I can see the schema and record counts from the CHANGELOG but not a raw CSV row to verify column values match the screenshots.

3. **The `process_cad_data_13month_rolling.py` current source** — I can see the v1.15.9 CHANGELOG confirming the fix was applied, but cannot view the current code to verify it persists.

---

**Review completed: 2026-02-26**  
**Reviewer: Claude Opus 4.6**
