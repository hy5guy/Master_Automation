# Context for Claude: Response Time Visuals and M Code Review

**Purpose:** Pass this document (and referenced files) to Claude when asking it to review Hackensack PD Response Time visuals and M code. Based on KB artifacts from:
- `KB_Shared\04_output\Claude-Response_time_metric_verification_artifacts`
- `KB_Shared\04_output\Response_Time_Correction_Report_And_Design_System`
- `KB_Shared\04_output\Response_Time_ETL_Golden_Standard_And_CallType_Mapping`

---

## 1. Response Time Metrics (Power BI)

**Primary table (live model):** `___ResponseTime_AllMetrics` — consolidated query with all three metrics in one long table. Replaces the three separate queries (`___ResponseTimeCalculator`, `___ResponseTime_OutVsCall`, `___ResponseTime_DispVsCall`), which are disabled (load off) as of 2026-03-06.

| Metric_Label | Metric_Type | Formula |
|-------------|-------------|---------|
| **Travel Time** | `"Time Out - Time Dispatched"` | Time Out − Time Dispatched |
| **Total Response** | `"Time Out - Time of Call"` | Time Out − Time of Call |
| **Dispatch Queue** | `"Time Dispatched - Time of Call"` | Time Dispatched − Time of Call |

**M code:** `m_code/response_time/___ResponseTime_AllMetrics.m`

- Source: `PowerBI_Date\response_time_all_metrics\`
- 13-month rolling window driven by `pReportMonth` (not `TODAY()`)
- Columns: `Metric_Label`, `Metric_Sort`, `Date_Sort_Key`, `MonthName`, `Response_Type`, `Average_Response_Time`, `Response_Time_MMSS`, etc.

---

## 2. 13-Month Window Logic

```
pReportMonth = #date(YYYY, M, 1)   — first day of the report's month
EndDate      = month BEFORE pReportMonth  (last complete month)
StartDate    = 12 months before EndDate  (13 months total, inclusive)

Example: pReportMonth = #date(2026,2,1) → window = Jan-25 through Jan-26
```

Using `pReportMonth` (not `TODAY()`) ensures historical monthly report files always display the correct 13-month window for their report period.

---

## 3. Golden Standard ETL (v1.17.18+)

**Batch ETL script:** `response_time_batch_all_metrics.py`  
*(Path may be `02_ETL_Scripts\Response_Times\` in KB/Hackensack structure)*

**Critical logic (must be verified):**
1. **Sort before dedup:** `sort_values(["ReportNumberNew", "Time Out"])` before `drop_duplicates(subset="ReportNumberNew", keep="first")` — ensures **first-arriving unit** per incident.
2. **Admin incident filter:** 92-type administrative incident exclusion (self-initiated, patrols, meal breaks, TAPS, etc.) — otherwise Routine Dispatch-to-Scene is skewed (e.g., 0:48 → 2:01 after fix).
3. **CallType mapping:** `CallType_Categories.csv` used for missing Response Type (2024 had <1% populated; three-tier resolution: CAD value → exact match → normalized match).

**Output:** 25 monthly CSVs in `PowerBI_Data\Backfill\response_time_all_metrics\`  
**Schema:** `Response_Type`, `MM-YY`, `Metric_Type`, `First_Response_Time_MMSS`, `Avg_Minutes`, `Record_Count`, `Median_Minutes`

---

## 4. First-Arriving-Unit Verification

**Standard:** One response time per incident = **first-arriving unit** (earliest Time Out per ReportNumberNew).

**Verification steps for batch ETL:**
1. Open `response_time_batch_all_metrics.py`
2. Find deduplication by `ReportNumberNew`
3. Confirm it **sorts by `ReportNumberNew` and `Time Out`** before `drop_duplicates(..., keep='first')`
4. If not, the kept row may be "first row in file" instead of "first on scene"

---

## 5. Known Issues / Caveats

| Issue | Detail |
|-------|--------|
| **Routine skew** | 10× mean/median ratio (median ~13 sec, mean ~2 min) from self-initiated traffic stops; bimodal distribution |
| **Record count mismatch** | Different metrics have different record counts (expected; different timestamp validity per metric) |
| **2024 data** | Response Type mostly unpopulated; use with caution; CallType mapping resolves ~99.99% |
| **Median_Minutes** | Present in CSVs but not used in M/DAX |
| **How Reported filter** | "9-1-1 only" may be too restrictive; consider "citizen-initiated" (Phone, Walk-In) |
| **Encoding** | CallType_Categories may have `ï¿½` (replacement char); normalization should strip dash-like chars |

---

## 6. DAX Measures

- **response_time_measures.dax:** Avg Response Time (Travel), (Total), (Dispatch Queue)
- **response_time.dax** (or legacy): Rolling_EndDate, Rolling_StartDate, Is_Rolling_Period, Category_Response_Avg, Best_Month_12M
- **Title/subtitle measures:** RT Average Title/Subtitle, RT OutVsCall Title/Subtitle, RT DispVsCall Title/Subtitle — moved to `___ResponseTime_AllMetrics` (2026-03-06)

---

## 7. Design System

- **Footnote:** Exclude admin activities; 0–10 minute range; first-arriving officer
- **HPD report style:** `docs/templates/HPD_Report_Style_Prompt.md`
- **Remove references** to legacy `ResponseTimes` and `CAD_Raw`

---

## 8. Files to Provide Claude

### Required (core logic)
| # | File | Purpose |
|---|------|---------|
| 1 | `m_code/response_time/___ResponseTime_AllMetrics.m` | **Primary** — consolidated query (all 3 metrics) |
| 2 | `m_code/response_time/___ResponseTimeCalculator.m` | Legacy (kept for reference; load disabled in PBI) |
| 3 | `m_code/response_time/___ResponseTime_OutVsCall.m` | Legacy (kept for reference; load disabled in PBI) |
| 4 | `m_code/response_time/___ResponseTime_DispVsCall.m` | Legacy (kept for reference; load disabled in PBI) |
| 5 | `response_time_batch_all_metrics.py` (or `response_time_fresh_calculator.py`) | ETL logic, first-arriving-unit dedup |
| 6 | `response_time_measures.dax` / `response_time.dax` | DAX measures |

### Recommended
| # | File | Purpose |
|---|------|---------|
| 7 | `docs/response_time/RESPONSE_TIME_FIRST_OFFICER_VERIFICATION.md` | First-officer verification doc |
| 8 | `CHANGELOG.md` (response time sections) | Bug fixes v1.17.15, v1.17.16 |
| 9 | Sample CSV from `response_time_all_metrics` | Schema and sample data |

### Optional
| # | File | Purpose |
|---|------|---------|
| 10 | `CallType_Categories.csv` | CallType mapping for admin filter |
| 11 | Visual screenshots | Layout and design review |
| 12 | `docs/response_time/PROMPT_FOR_CLAUDE_ETL_AUDIT_v1_17_16.md` | Prior audit prompt |

---

## 9. Sample Prompt for Claude

```
I need you to review the Hackensack PD Response Time visuals and M code.

**Context:** See the attached PROMPT_FOR_CLAUDE_Response_Time_Visuals_And_M_Code_Review.md and the referenced files.

**Tasks:**
1. Verify the three M code queries correctly implement the 13-month window and Metric_Type filters.
2. Confirm the ETL uses first-arriving-unit deduplication (sort by ReportNumberNew + Time Out before dedup).
3. Check for any logic gaps, inconsistencies, or deviations from the golden standard.
4. Suggest improvements if any.

Please summarize findings and any recommended changes.
```

---

## 10. KB Prompt vs Transcript Session — Scope Clarification

**KB prompt = verification/audit** (confirm logic, first-arriving-unit, golden standard).  
**Transcript session (Response_Time_Correction_Report_And_Design_System) = visual redesign** (line chart fix, DAX, title/subtitle — not ETL audit).

| KB Requirement | Transcript Session | Cursor Audit (2026-03-06) |
|----------------|-------------------|---------------------------|
| 13-month window, Metric_Type filter | ✅ Confirmed | ✅ See `docs/response_time/RESPONSE_TIME_M_CODE_AUDIT_2026_03_06.md` |
| ETL first-arriving-unit sort/dedup | ❌ Not done | ✅ `response_time_fresh_calculator.py` verified |
| Admin filter, CallType, How Reported | ❌ Not done | ETL scope — not in M code |
| ___ResponseTime_AllMetrics consolidated | Proposed | ✅ **Implemented in live PBI 2026-03-06** |

**Live PBI model (2026-03-06):** `___ResponseTime_AllMetrics` is the primary table. Three old tables (`___ResponseTimeCalculator`, `___ResponseTime_OutVsCall`, `___ResponseTime_DispVsCall`) have load disabled. Measures moved to `___ResponseTime_AllMetrics`; date relationships created.

---

*Generated from KB_Shared Response Time artifacts. 2026-03-06.*
