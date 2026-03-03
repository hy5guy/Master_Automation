// 🕒 2026-02-26-23-15-00
// Project: Master_Automation/PEER_REVIEW_Response_Time_Verification
// Author: R. A. Carucci
// Purpose: Independent peer review of v1.17.15 and v1.17.16 response time ETL fixes

# Independent Peer Review — Response Time ETL Pipeline
## Bugs v1.17.15 & v1.17.16 | 2026-02-26

**Reviewer:** Claude Opus 4.6 (independent review)
**Analyst:** R. A. Carucci, Principal Analyst, Hackensack PD
**Scope:** Two critical bugs fixed in `response_time_batch_all_metrics.py`, all supporting documentation, pre/post comparison data, and regenerated output CSVs.

---

## 1. Bug 1: First-Arriving Unit Sort (v1.17.15)

### What Was Wrong

`load_and_clean()` called `drop_duplicates(subset="ReportNumberNew", keep="first")` without first sorting by `Time Out`. For the 28.2% of incidents with multiple responding units, whichever row happened to appear first in the Excel file was kept — not necessarily the officer who arrived first.

### Fix Verification: ✅ CONFIRMED CORRECT

**`response_time_batch_all_metrics.py` line 221–222:**
```python
df = df.sort_values(["ReportNumberNew", "Time Out"])  # v1.17.15 fix
df = df.drop_duplicates(subset="ReportNumberNew", keep="first").reset_index(drop=True)
```

The sort orders all rows for each `ReportNumberNew` by ascending `Time Out`, so `keep="first"` retains the row with the lowest `Time Out` — the first officer to arrive on scene. This is the correct first-arriving-unit methodology and is consistent with NFPA 1710 / CALEA standards.

### Delta Analysis: ✅ CONSISTENT WITH EXPECTATIONS

From the PreFix_vs_PostFix_Comparison doc (Time Out − Time Dispatched):

| Month | Type | Pre-Fix | Post-Fix | Delta |
|-------|------|---------|----------|-------|
| 01-26 | Emergency | 3:11 | 2:51 | **−0:20** |
| 01-26 | Urgent | 2:54 | 2:35 | **−0:19** |
| 01-26 | Routine | 1:26 | 1:23 | −0:03 |
| 01-25 | Emergency | 2:58 | 2:52 | −0:06 |
| 01-25 | Urgent | 2:53 | 2:38 | −0:15 |
| 01-25 | Routine | 0:48 | 0:47 | −0:01 |

**Why this pattern is correct:**

- All deltas are negative — selecting the fastest-arriving officer always produces a lower or equal time.
- Emergency and Urgent show larger reductions (6–20 sec) because they have significantly more multi-unit responses.
- Routine shows near-zero change (1–3 sec) because Routine calls rarely have multiple units, so the sort rarely changes which row is selected.
- The 01-26 deltas are larger than 01-25, which is within normal variation.

### Reference Script Status: ⚠️ FLAG

The uploaded `process_cad_data_13month_rolling.py` is **version 1.0.0 (2025-12-10)** and does **NOT** contain a sort before dedup at line 496:

```python
# Line 496 — no sort_values before this
df = df.drop_duplicates(subset=['ReportNumberNew'], keep='first')
```

The CHANGELOG v1.17.15 states the v1.15.9 sort fix was "confirmed present." This means either the production copy was updated separately, or the uploaded file is an older snapshot. **Recommendation:** Verify the deployed copy at `Master_Automation/scripts/` has the sort. If it doesn't, add it. This script is not the one producing Power BI CSVs (the batch ETL is), but consistency matters.

---

## 2. Bug 2: Administrative Incident Filter (v1.17.16)

### What Was Wrong

The batch ETL was computing response times for **all** CAD records, including officer self-initiated activities like meal breaks, patrol checks, TAPS operations, training, court assignments, vehicle maintenance, etc. These admin activities are not public calls for service — the officer is already on scene or at a fixed location, producing near-zero dispatch-to-arrival times. Including them massively depressed Routine averages because virtually all admin activities are classified as Routine.

### Fix Verification: ✅ CONFIRMED CORRECT

**`response_time_batch_all_metrics.py` lines 87–133:** Defines `ADMIN_INCIDENTS_RAW` — a set of administrative incident type strings.

**Lines 136–139:** Builds `ADMIN_INCIDENTS_NORM` — normalized versions (lowercase, stripped, collapsed whitespace, ASCII-only) for matching.

**Lines 225–240:** Applies the filter in `load_and_clean()`:
```python
df["_inc_norm"] = df["Incident"].fillna("").astype(str).str.strip().str.lower()...
df = df[~df["_inc_norm"].isin(ADMIN_INCIDENTS_NORM)].copy()
```

**Processing order is correct:**
1. Year filter (keep only expected year)
2. Sort by Time Out + dedup (first-arriving unit)
3. **Admin incident filter** ← applied here
4. Response Type resolution (CAD → exact map → normalized map)
5. Timestamp parsing and metric calculation

Filtering before Response Type resolution is the right approach — it prevents admin activities from consuming CallType mapping capacity and avoids any edge cases where an admin incident could get mapped to Emergency or Urgent.

### Admin List Consistency: ✅ IDENTICAL

I extracted the admin incident lists from both scripts programmatically. **The lists are identical** — 92 items in each, with zero differences in either direction.

### Admin List vs CallType_Categories Cross-Check: ⚠️ MINOR DOC DISCREPANCY

The CHANGELOG states "26 of the 101 admin types were confirmed present in CallType_Categories.csv mapped as Routine." My analysis of the actual data shows:

- 91 of 92 extracted admin types appear in CallType_Categories.csv
- **91 are mapped as Routine**, 1 as Urgent, 0 as Emergency

The "26" figure in the CHANGELOG appears to be understated — the actual overlap is much higher. This doesn't affect correctness (the filter works regardless), but the CHANGELOG entry should be corrected for documentation accuracy.

*Note on "101 vs 92": The set literal in the Python code may contain comment lines or formatting that my regex-based extraction didn't capture. The functional count may differ from the claimed 101. Recommend running `len(ADMIN_INCIDENTS_NORM)` at runtime to get the definitive count.*

### Impact Verification: ✅ CONFIRMED — THIS WAS THE LARGER BUG

From the comparison doc (January 2025, Routine):

| Metric | Without Filter (v1.17.15) | With Filter (v1.17.16) | Change |
|--------|--------------------------|----------------------|--------|
| Dispatch to On Scene | 0:47 | **2:01** | +1:14 |
| Time Received to On Scene | 1:14 | **3:22** | +2:08 |
| Dispatch Processing | 0:50 | **2:27** | +1:37 |

Volume removed by the filter:

| Source | Post-Dedup | Post-Filter | Removed | % |
|--------|-----------|-------------|---------|---|
| 2024 | 82,891 | 35,171 | 47,720 | 57.6% |
| 2025 | 87,436 | 33,797 | 53,639 | 61.4% |
| 2026-01 | 7,499 | 3,131 | 4,368 | 58.3% |

**Why this confirms the fix is correct:**
- Administrative activities represent ~58% of all CAD records. This is consistent with police operations — officers spend more time on administrative tasks, directed patrol, and self-initiated activities than responding to citizen calls.
- Pre-filter Routine Dispatch-to-Scene was 0:47 (47 seconds) — implausibly fast for actual dispatched calls. Post-filter it's 2:01, which is operationally reasonable and consistent with the Emergency figure (2:52).
- Emergency and Urgent values changed minimally because admin activities are almost exclusively classified as Routine.

---

## 3. Post-Fix Data Quality Assessment

### 3a. Output CSV Schema: ✅ CORRECT

Both sample CSVs (2025_01, 2026_01) have 9 rows each — the expected 3 Response_Type × 3 Metric_Type combinations. Columns match the documented schema:
`Response_Type, MM-YY, Metric_Type, First_Response_Time_MMSS, Avg_Minutes, Record_Count, Median_Minutes`

### 3b. Cross-Metric Algebraic Consistency

Algebraically, for any individual record: `(Time Out − Time of Call) = (Time Out − Time Dispatched) + (Time Dispatched − Time of Call)`.

However, at the aggregate level (averages across different record subsets), this identity does **not** hold. I computed the discrepancy:

| Month | Type | OutVsCall − Calc | DispVsCall | Gap |
|-------|------|-----------------|------------|-----|
| 01-26 | Emergency | 1.85 min | 2.79 min | −0.95 min |
| 01-26 | Routine | 0.66 min | 2.02 min | −1.36 min |
| 01-26 | Urgent | 0.50 min | 1.66 min | −1.16 min |
| 01-25 | Emergency | 2.10 min | 2.97 min | −0.87 min |
| 01-25 | Routine | 1.35 min | 2.46 min | −1.11 min |
| 01-25 | Urgent | 1.08 min | 2.01 min | −0.93 min |

**Verdict: EXPECTED AND DEFENSIBLE.** Each metric uses only records where both required timestamps are present and produce a value in the 0–10 minute range. The record counts differ significantly (e.g., Jan-26 Emergency: 257 / 212 / 249 across the three metrics). The RECORD_COUNT_MISMATCH_EXPLAINED.md document handles this well. The three metrics should NOT be expected to form a closed algebraic loop at the aggregate level, and administration should NOT attempt to reconcile them by subtraction.

### 3c. Mean vs Median Skew: ⚠️ NEW FINDING — ROUTINE DISPATCH-TO-SCENE

This is a significant data quality observation not addressed in any of the provided documentation:

| Month | Type | Metric | Mean | Median | Ratio |
|-------|------|--------|------|--------|-------|
| 01-26 | **Routine** | **Dispatch to On Scene** | **2:04** | **0:13** | **9.5×** |
| 01-25 | **Routine** | **Dispatch to On Scene** | **2:01** | **0:12** | **10.5×** |
| 01-26 | Emergency | Dispatch to On Scene | 2:51 | 2:18 | 1.2× |
| 01-25 | Emergency | Dispatch to On Scene | 2:52 | 2:32 | 1.1× |

**What this means:** More than half of Routine "Dispatch to On Scene" records have a response time under 13 seconds. This is a **bimodal distribution** — a large cluster of near-zero times (officer self-initiated activities like traffic stops, field contacts, etc. where the officer is already on scene when dispatched) mixed with a smaller cluster of actual dispatched-to-a-location responses (2–5+ minutes).

**Why this survived the admin filter:** The 101-type filter correctly removes administrative/internal activities (meal breaks, training, court, TAPS, etc.). But it does not — and arguably should not — remove legitimate enforcement activities like traffic stops and motor vehicle stops. In these cases, the officer initiates the stop, then requests dispatch to assign a report number. The `Time Dispatched` and `Time Out` are nearly simultaneous because the officer is already on scene.

**Risk:** If admin asks "Why is Routine only 2 minutes when Emergency is almost 3?" — the honest answer is that the Routine average is **pulled down** by self-initiated stops where the officer was already present. The median (13 seconds) better represents the "typical" Routine record but would be misleading in the opposite direction — it reflects officer-initiated activity, not dispatched-call response.

**Recommendations:**
1. **Document this distribution** as a known characteristic. Routine "Dispatch to On Scene" is not apples-to-apples with Emergency — Routine includes both citizen-initiated and officer-initiated calls.
2. **Consider adding a "Dispatched Calls Only" view** in a future enhancement — filter to only records where the dispatch processing time exceeds some threshold (e.g., 30 seconds), which would isolate true citizen-initiated calls.
3. **Keep Median_Minutes in the CSVs** (already present). Consider surfacing it in DAX for analyst-level reporting, even if not shown on the executive dashboard.
4. **Moderate skew also present in:** Routine OutVsCall (2.6×), Routine DispVsCall (2.1×), and Urgent DispVsCall (2.3×). Emergency metrics are healthy (1.0–1.3× range).

---

## 4. Documentation Quality

### Comparison Doc (PreFix_vs_PostFix): ✅ EXCELLENT

- Clear before/after tables with record counts
- Full 13-month series for all three metrics at both v1.17.15 and v1.17.16 stages
- Admin-facing note is plain language and appropriate
- Pattern analysis section correctly explains the operational logic

### Record Count Mismatch Doc: ✅ EXCELLENT

- Restaurant analogy is clear and accessible
- Correctly warns against reconciliation attempts
- Provides a quotable paragraph for admin use

### CHANGELOG: ✅ VERY GOOD (minor corrections needed)

- Well-structured with clear impact metrics
- **Correction needed:** "26 of 101 admin types" should be ~91 of 92 (or whatever the runtime count is)
- **Correction needed:** v1.17.15 states process_cad_data_13month_rolling.py sort fix is "confirmed present," but the uploaded v1.0.0 file does not contain it
- Consider adding the "Also Identified" note about the Calculator M code path to a separate action-item tracker — it's easy to miss buried in the CHANGELOG

### Verification Prompt Doc: ✅ GOOD

- Well-structured for bootstrapping a new conversation
- Artifact list is comprehensive
- The example values in the "Data context" section still reference pre-fix numbers (1:26, 1:53, 3:11, 5:02) — should be updated to v1.17.16 values

---

## 5. Operational Value Patterns (Post-v1.17.16)

The corrected data follows expected operational patterns:

**Dispatch Processing Time (Time of Call → Dispatch):**
- Emergency: 2:36–3:08 — longest because dispatchers gather weapons/injuries/suspect info, coordinate multiple units, and notify supervisors
- Routine: 1:55–2:54 — moderate processing, less urgency
- Urgent: 1:24–2:07 — shortest, which is noteworthy (see below)

**Dispatch to On Scene (Dispatch → Arrival):**
- Emergency: 2:31–2:55 — officers respond with lights/sirens, fastest travel
- Routine: 1:55–3:03 — mixed (see mean/median skew above)
- Urgent: 2:32–2:49 — similar travel times to Emergency

**Total Response (Time of Call → On Scene):**
- Emergency: 4:31–5:03 — highest total, driven by dispatch processing
- Routine: 2:42–4:15 — wide range reflects the bimodal distribution
- Urgent: 2:55–3:44 — lower than Emergency in total, despite similar travel time

**Note on Urgent dispatch processing being shortest:** Urgent calls may have shorter dispatch processing because they often arrive from structured sources (alarm companies, non-emergency transfers) that provide pre-formatted information, reducing dispatcher triage time. Emergency calls require the most real-time information gathering. This is worth exploring further but is defensible as presented.

---

## 6. Overall Assessment

### Is the v1.17.16 data defensible for admin presentation?

**YES** — with the following conditions:

| Condition | Status |
|-----------|--------|
| First-arriving unit methodology | ✅ Correct (v1.17.15 sort) |
| Admin incident exclusion | ✅ Correct (v1.17.16 filter) |
| Response Type classification | ✅ 99.99% coverage via 3-tier resolution |
| Outlier filtering | ✅ 0–10 min range, consistently applied |
| All 25 monthly CSVs regenerated | ✅ Per CHANGELOG |
| Record count mismatch documented | ✅ Separate explanation doc |
| Calculator M code using correct path | ⚠️ **VERIFY** — CHANGELOG says it may still point to old path |
| Power BI refreshed on v1.17.16 data | ⚠️ **VERIFY** before presenting |
| Routine mean/median skew disclosed | ⚠️ **RECOMMENDED** — have talking point ready |

### Remaining Action Items

1. **Verify Calculator M code path in PBIX** — Ensure it reads from `response_time_all_metrics` folder, not old backfill path
2. **Refresh all three Power BI queries** and confirm visual values match v1.17.16 CSVs
3. **Verify production copy of `process_cad_data_13month_rolling.py`** has sort before dedup
4. **Correct CHANGELOG** — "26 of 101" → actual count; reference script sort claim
5. **Update Verification Prompt doc** — example values still show pre-fix numbers
6. **Prepare Routine skew talking point** — in case admin questions why Routine is lower than Emergency

### Confidence Level

**HIGH** — Both bugs are real, both fixes are correct, the delta analysis is consistent with expectations, and the corrected values follow operational logic. The documentation is thorough and admin-ready. The Routine mean/median skew is a data characteristic to be aware of, not a bug.

---

*Review completed: 2026-02-26 | Reviewer: Claude Opus 4.6*
*Files reviewed: response_time_batch_all_metrics.py (v1.17.16), process_cad_data_13month_rolling.py (v1.0.0), 2026_01_response_times.csv, 2025_01_response_times.csv, CallType_Categories.csv (664 entries), CHANGELOG.md, 2026_02_26_PreFix_vs_PostFix_Comparison.md, RECORD_COUNT_MISMATCH_EXPLAINED.md, PROMPT_FOR_CLAUDE_RESPONSE_TIME_VERIFICATION.md*
