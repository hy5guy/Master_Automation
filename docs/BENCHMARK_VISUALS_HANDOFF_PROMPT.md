# Benchmark Power BI Visuals – AI Handoff Prompt

**Date:** 2026-02-14  
**Status:** Visuals broken; multiple fixes attempted  
**Goal:** Restore Use of Force Incident Matrix, Incident Distribution Donut, and Incident Count Line Chart to display correct data across a 13-month rolling window.

---

## 1. Project Context

**Workspace:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation`

**Benchmark ETL location:** `02_ETL_Scripts\Benchmark\`  
**Data export location:** `05_EXPORTS\Benchmark\` (flat structure: use_force, show_force, vehicle_pursuit)

**Purpose:** Power BI report showing Use of Force, Show of Force, and Vehicle Pursuit incident counts over a rolling 13-month window (Jan 2025–Jan 2026 as of Feb 2026).

---

## 2. Current Problem

### Symptoms
- **Use of Force Incident Matrix:** Only January 2025 (01-25) shows data (39, 345, 21, 405); all other months (02-25 through 01-26) show 0.
- **Incident Distribution by Event Type (donut):** Empty.
- **Incident Count by Date and Event Type (line chart):** Flat line at zero.

### Visual Configuration
- **Matrix:** Rows = EventType, Columns = MonthLabel, Values = IncidentCount
- **Donut:** Uses event-type breakdown (expected: IncidentCount_13Month or similar)
- **Line chart:** X = MonthLabel, Y = IncidentCount, Legend = EventType

---

## 3. Data Model Structure

### Tables
| Table | Source | Purpose |
|-------|--------|---------|
| ___Benchmark | Power Query: loads from 05_EXPORTS\Benchmark\{use_force, show_force, vehicle_pursuit} | Fact table (incident-level rows) |
| ___DimMonth | Power Query: dynamic 13-month list | Dimension (MonthStart, MonthLabel, MonthSort) |
| ___DimEventType | Power Query: static 3 rows | Dimension (Show of Force, Use of Force, Vehicle Pursuit) |

### Required Columns in ___Benchmark
- Incident Date, Report Key, Report Number
- EventType (matches ___DimEventType)
- MonthStart (first day of month, for relationship to ___DimMonth)
- MonthLabel, MonthSort
- # of Officers Involved, # of Subjects, etc.

### Relationships (Required)
- ___Benchmark[MonthStart] → ___DimMonth[MonthStart] (many-to-one, single cross-filter)
- ___Benchmark[EventType] → ___DimEventType[EventType] (many-to-one, single cross-filter)

---

## 4. Data Source Files

**Path:** `C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark\`

| Folder | File | Notes |
|--------|------|-------|
| use_force | use-of-force-reports-01_01_2001-02_06_2026.csv | Incident-level, has Incident Date, Report Key |
| show_force | show-of-force-reports-01_01_2001-02_06_2026.csv | Same schema |
| vehicle_pursuit | vehicle-pursuit-reports-01_01_2001-02_06_2026.csv | Same schema |

**Raw schema:** Officer Name, Badge Number, Rank, Organization, Incident Number, Report Number, Incident Date, Location, Initial Contact, # of Officers Involved, # of Subjects, Subject type, Report Key

**Note:** Raw CSVs do NOT have EventType or MonthStart; the M query must add them when combining the three folders.

---

## 5. Fixes Already Attempted

| Fix | Status |
|-----|--------|
| Changed ___Benchmark to add EventType (not Event Type), MonthStart, SourceFile | User has corrected M code available in ___Benchmark_FIXED.m |
| Changed ___DimMonth to dynamic 13-month window | User has ___DimMonth_dynamic.m |
| Created relationship ___Benchmark[MonthStart] → ___DimMonth[MonthStart] | User saved it |
| Relationship ___Benchmark[EventType] → ___DimEventType[EventType] | Already existed (Power BI reported "relationship already exists") |
| Fixed BM_YoY_Change DAX (DATEADD → EDATE) | Fixed |
| IncidentCount_Matrix measure (explicit SUMX iteration) | Did not resolve matrix showing same/zeros |
| IncidentCount_NEW measure | Did not resolve |
| Refresh visuals | User performed; visuals still broken |

---

## 6. Files to Review

| File | Path | Purpose |
|------|------|---------|
| ___Benchmark_FIXED.m | 02_ETL_Scripts\Benchmark\ | Corrected ___Benchmark Power Query |
| ___DimMonth_dynamic.m | 02_ETL_Scripts\Benchmark\ | Dynamic ___DimMonth Power Query |
| Benchmark_DAX_Measures.dax | 02_ETL_Scripts\Benchmark\ | All DAX measures |
| data dictionary | 02_ETL_Scripts\Benchmark\schemas\data_dictionary.md | Expected column schema |
| **diagnose_benchmark_data.py** | scripts\ | Python script – analyzes source CSVs for date coverage, monthly distribution |
| **BENCHMARK_VISUAL_DIAGNOSTIC.md** | docs\ | Step-by-step troubleshooting (7 steps) |
| **BENCHMARK_QUICK_FIX_REFERENCE.md** | docs\ | Quick fixes for common root causes |
| benchmark test data.csv | data\backfill\2026_12_compair\ben chmark test data.csv | Pre-aggregated monthly totals; NOT the source for ___Benchmark; use for validation only |

---

## 7. Root Cause Hypothesis

The matrix showing data only for January 2025 suggests one of:

1. **MonthStart in ___Benchmark is wrong** – Most or all rows may have MonthStart = 2025-01-01 due to parsing/calculation error.
2. **Date type mismatch** – ___Benchmark[MonthStart] vs ___DimMonth[MonthStart] (Date vs DateTime) preventing join.
3. **Relationship inactive or wrong** – Multiple relationships between tables; wrong one active.
4. **___Benchmark not loading latest data** – Query cached or pointing to wrong path; only partial data loaded.
5. **Incident Date parsing** – Locale or format causing incorrect Date.From([Incident Date]).

---

## 8. Diagnostic Steps Requested

**Start here:** Run `python scripts/diagnose_benchmark_data.py` to analyze source CSVs. If data spans multiple months, proceed with Power BI checks.

**Power BI steps (see docs/BENCHMARK_VISUAL_DIAGNOSTIC.md):**
1. **Verify ___Benchmark data:** Table visual with ___Benchmark[MonthStart] and COUNTROWS(___Benchmark). Confirm multiple distinct MonthStart values.
2. **Verify ___DimMonth:** Confirm 13 rows (Jan 2025–Jan 2026).
3. **Verify relationship:** Model view – active, correct cardinality, filter direction.
4. **Trace M query:** Incident Date type datetime, MonthStart calculation, EventType matches ___DimEventType.
5. **Check for filters:** Report/page/visual filters restricting to one month.

**Quick fixes:** See docs/BENCHMARK_QUICK_FIX_REFERENCE.md for Fix #1–#5.

---

## 9. Expected Behavior

- **Matrix:** Each cell (EventType × MonthLabel) shows distinct count of Report Key for that month and event type.
- **Donut:** Shows distribution of incidents by EventType for the 13-month period.
- **Line chart:** Shows trend of IncidentCount by month, with separate lines per EventType.

---

## 10. Prompt for AI Assistant

```
You are assisting with a Power BI Benchmark report. The Use of Force Incident Matrix, Incident Distribution donut, and Incident Count line chart are broken:

- Matrix: Only Jan 2025 has data; Feb 2025–Jan 2026 show 0.
- Donut: Empty.
- Line chart: Flat at zero.

Context is in: C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\docs\BENCHMARK_VISUALS_HANDOFF_PROMPT.md

Please:
1. Review the handoff document and relevant files (___Benchmark_FIXED.m, ___DimMonth_dynamic.m, Benchmark_DAX_Measures.dax, raw CSV structure).
2. Diagnose why only January 2025 shows data in the matrix.
3. Provide specific, actionable fixes (M code changes, DAX changes, relationship checks, or diagnostic queries).
4. Format responses clearly with headers and tables.
5. If proposing M code, provide the complete corrected query for copy-paste.
```

---

## 11. Key Paths Summary

```
Master_Automation\
├── scripts\
│   └── diagnose_benchmark_data.py       ← Run first: analyzes source CSV date coverage
├── docs\
│   ├── BENCHMARK_VISUALS_HANDOFF_PROMPT.md  (this file)
│   ├── BENCHMARK_VISUAL_DIAGNOSTIC.md       ← 7-step troubleshooting guide
│   └── BENCHMARK_QUICK_FIX_REFERENCE.md     ← Fix #1–#5 quick reference
├── 02_ETL_Scripts\Benchmark\
│   ├── ___Benchmark_FIXED.m
│   ├── ___DimMonth_dynamic.m
│   ├── Benchmark_DAX_Measures.dax
│   ├── schemas\data_dictionary.md
│   └── README.md
└── data\backfill\2026_12_compair\
    └── ben chmark test data.csv  (pre-aggregated; validation only)

05_EXPORTS\Benchmark\
├── use_force\use-of-force-reports-01_01_2001-02_06_2026.csv
├── show_force\show-of-force-reports-01_01_2001-02_06_2026.csv
└── vehicle_pursuit\vehicle-pursuit-reports-01_01_2001-02_06_2026.csv
```

---

**End of handoff document**
