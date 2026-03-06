# Response Time M Code Audit — 2026-03-06

**Purpose:** Verification audit per KB prompt requirements. Covers M code in Master_Automation; ETL audit covers `response_time_fresh_calculator.py` (batch script `response_time_batch_all_metrics.py` is in KB/Hackensack structure).

---

## Live PBI Model — Migration Complete (2026-03-06)

| Table | Status |
|-------|--------|
| `___ResponseTime_AllMetrics` | ✅ **Primary** — consolidated query, all 3 metrics, 13-month window, full schema |
| `___ResponseTimeCalculator` | Load disabled (private) |
| `___ResponseTime_OutVsCall` | Load disabled (private) |
| `___ResponseTime_DispVsCall` | Load disabled (private) |

**Migration (via Claude MCP):** Created `___ResponseTime_AllMetrics`; disabled load on three old tables; moved 6 title/subtitle measures; created date relationships. Row count validated 117 = 39+39+39.

---

## 1. M Code Verification

### 1.1 13-Month Window Logic (pReportMonth vs TODAY)

**Status: ✅ PASS**

All three queries use `pReportMonth` correctly:

```powerquery
EndDate   = Date.AddMonths(DateTime.Date(pReportMonth), -1),  // last complete month
StartDate = Date.AddMonths(EndDate, -12),                      // 13 months total
EndYM     = Date.Year(EndDate)   * 100 + Date.Month(EndDate),
StartYM   = Date.Year(StartDate) * 100 + Date.Month(StartDate),
```

- Window: `StartYM <= ym <= EndYM` (inclusive)
- No `TODAY()` references — historical reports retain correct window

**Files:** `___ResponseTimeCalculator.m`, `___ResponseTime_OutVsCall.m`, `___ResponseTime_DispVsCall.m`

---

### 1.2 Metric_Type Filter Correctness

**Status: ✅ PASS**

| Query | Metric_Type Filter | Expected |
|-------|-------------------|----------|
| ___ResponseTimeCalculator | `"Time Out - Time Dispatched"` | ✅ |
| ___ResponseTime_OutVsCall | `"Time Out - Time of Call"` | ✅ |
| ___ResponseTime_DispVsCall | `"Time Dispatched - Time of Call"` | ✅ |

Each query filters `AllData` by the correct `Metric_Type` before windowing.

---

### 1.3 Data Source

**Status: ✅ PASS**

All three use:
```
C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\response_time_all_metrics
```

- File pattern: `*_response_times.csv`
- Encoding: 65001 (UTF-8)
- Single unified folder — no legacy `ResponseTimes` or `CAD_Raw` references in M code

---

### 1.4 Schema Consistency

**Status: ✅ PASS**

All three produce identical column sets:
- `YearMonth`, `Date_Sort_Key`, `Date`, `Response_Type`, `Category`, `Summary_Type`
- `Average_Response_Time`, `Response_Time_MMSS`, `MM-YY`, `Record_Count`, `Metric_Type`
- `Count`, `MonthName`

---

### 1.5 Median_Minutes

**Status: ⚠️ NOT USED**

- CSV schema includes `Median_Minutes` (per KB)
- M code does not load or use it — only `Avg_Minutes` → `Average_Response_Time`
- **Recommendation:** Document as intentional (mean used for visuals); or add if median-based visuals are needed

---

## 2. ETL First-Arriving-Unit Verification

### 2.1 response_time_fresh_calculator.py (Master_Automation)

**Status: ✅ PASS**

```python
df_combined.sort_values(['ReportNumberNew', 'Time Out'], inplace=True)
df_combined = df_combined.drop_duplicates(subset=['ReportNumberNew'], keep='first')
```

- Sort by `ReportNumberNew` and `Time Out` before dedup
- `keep='first'` → first-arriving unit (earliest Time Out) per incident
- Docstring confirms: "First-arriving unit deduplication (sort by Time Out before drop_duplicates)"

**Path:** `scripts/response_time_fresh_calculator.py` (lines 222–223)

---

### 2.2 response_time_batch_all_metrics.py (KB/Hackensack)

**Status: ⚠️ NOT AUDITED HERE**

- Path: `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Response_Times\response_time_batch_all_metrics.py`
- Not in Master_Automation workspace
- CHANGELOG and peer review docs confirm v1.17.16+ fixes (sort + admin filter)
- **Action:** If this script feeds the CSVs used by Power BI, verify separately or attach for Claude audit

---

## 3. Items Not Covered (Per KB Gaps)

| Item | Status | Notes |
|------|--------|------|
| Admin incident exclusion (92-type filter) | ❌ | ETL-level; not in M code |
| CallType mapping 3-tier resolution | ❌ | ETL-level |
| How Reported filter (9-1-1 vs citizen-initiated) | ❌ | ETL-level |
| CallType_Categories encoding (ï¿½) | ❌ | ETL-level |
| Legacy ResponseTimes / CAD_Raw in DAX | ⚠️ | `response_time.dax` has legacy note; ensure no active use |
| ___ResponseTime_AllMetrics consolidated query | ✅ | Implemented in live PBI 2026-03-06 |

---

## 4. Summary

| Check | Result |
|-------|--------|
| 13-month window (pReportMonth) | ✅ |
| Metric_Type filter per query | ✅ |
| Single source folder | ✅ |
| Schema consistency | ✅ |
| First-arriving-unit (fresh calculator) | ✅ |
| Median_Minutes usage | ⚠️ Not used (document or add) |
| Batch ETL (if used) | ⚠️ Verify separately |
| Admin/How Reported/CallType | ETL scope — not in M code |

---

*Audit performed on Master_Automation workspace. 2026-03-06.*
