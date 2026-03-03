# Handoff — Response Time Golden Standard & CallType Mapping (2026-02-26)

**Date:** 2026-02-26  
**Scope:** Response Time ETL, Power BI M code, CallType reference, .gitignore, docs  
**Version:** Master_Automation 1.17.14

---

## What Was Done

### 1. Response Time — Golden Standard from Raw CAD

- **Batch ETL:** `02_ETL_Scripts\Response_Times\response_time_batch_all_metrics.py`
  - Processes **2024 full year**, **2025 full year**, and **2026-01 monthly** CAD timereports.
  - Outputs **all three metrics** per month to `PowerBI_Date\Backfill\response_time_all_metrics\`:
    - Time Out − Time Dispatched  
    - Time Out − Time of Call  
    - Time Dispatched − Time of Call  
  - **25 monthly CSVs** (2024-01 through 2026-01); one CSV per month with 9 rows (3 response types × 3 metrics).

- **Response Type backfill:** Missing/invalid CAD `Response Type` is resolved via `09_Reference\Classifications\CallTypes\CallType_Categories.csv`:
  1. Use original CAD value if `Emergency` / `Urgent` / `Routine`.
  2. Exact match on `Incident` column.
  3. Normalized match (lowercase, collapse spaces, strip non-ASCII).
  - **2024:** 894 from CAD + 81,995 from map → 82,889 usable (2 unresolvable).
  - **2025:** 84,162 from CAD + 3,266 from map → 87,428 usable.
  - **2026-01:** 7,498 from CAD + 1 from map → 7,499 usable.

### 2. Power BI M Code — Three Queries, Rolling 13-Month Window

- **___ResponseTimeCalculator.m** — Time Out − Time Dispatched (existing visual).
- **___ResponseTime_OutVsCall.m** — Time Out − Time of Call (new visual).
- **___ResponseTime_DispVsCall.m** — Time Dispatched − Time of Call (new visual).

All three:

- Load from `PowerBI_Date\Backfill\response_time_all_metrics` via `Folder.Files()`.
- Filter by **rolling 13-month window** driven by **`pReportMonth`** (not `TODAY()`), so historical monthly reports show the correct window for their report month.
- Output includes **`Summary_Type`** (literal `"Response_Type"`) so existing DAX measures (`Emergency_Avg_13M`, `Routine_Avg_13M`, `Urgent_Avg_13M`) that filter `Summary_Type = "Response_Type"` continue to work.

**Power BI checklist:**

- Ensure **`pReportMonth`** parameter exists (Date, e.g. `#date(2026,2,1)`).
- Paste updated M code for all three queries from `m_code\response_time\`.
- Refresh; line chart and DAX measures should clear Missing_References once `Summary_Type` is present.

### 3. CallType_Categories — 15 Alias Rows for CAD Variants

- **File:** `09_Reference\Classifications\CallTypes\CallType_Categories.csv` (649 → 664 rows).
- **Patterns addressed:** statute spacing (`2C: 18-2`), Unicode replacement character in place of dash, missing space around dash.
- **Docs added in CallTypes folder:** `README.md`, `CHANGELOG.md`, `SUMMARY.md`; `CallType_Categories_SCHEMA.md` updated with current counts.

### 4. .gitignore — outputs/.gitkeep Negation Fix

- Replaced `outputs/visual_exports/*` etc. with `outputs/.../**` and explicit `!outputs/.../.gitkeep` so `.gitkeep` files are tracked and directories remain ignorable.

### 5. CallTypes Unmapped Audit & Apply Scripts

- **audit_unmapped_incidents.py** — Finds incidents that fail to map; outputs `audit_unmapped_incidents.csv` with fuzzy suggestions.
- **apply_calltype_additions.py** — Applies approved additions to `CallType_Categories.csv` (run after editing PROPOSED list and confirming).

---

## Files Touched (for reference)

| Area | Files |
|------|--------|
| **M code** | `m_code/response_time/___ResponseTimeCalculator.m`, `___ResponseTime_OutVsCall.m`, `___ResponseTime_DispVsCall.m` |
| **ETL** | `02_ETL_Scripts/Response_Times/response_time_batch_all_metrics.py` (CallType mapping + 3 metrics) |
| **Reference** | `09_Reference/Classifications/CallTypes/CallType_Categories.csv`, README, CHANGELOG, SUMMARY, SCHEMA |
| **Scripts** | `02_ETL_Scripts/Response_Times/audit_unmapped_incidents.py`, `apply_calltype_additions.py`, `check_calltype_map.py`, `show_audit.py`, `check_2025_map.py` |
| **Repo** | `.gitignore`, `CHANGELOG.md`, `README.md`, `SUMMARY.md`, `outputs/*/.gitkeep` |
| **Docs** | `docs/HANDOFF_Response_Time_Golden_Standard_And_CallType_2026_02_26.md` (this file) |

---

## Next Steps / Ownership

1. **Power BI template:** Refresh all three response time queries; confirm `pReportMonth` is set; verify line chart and Emergency/Routine/Urgent 13M measures work.
2. **New visuals:** Add two visuals bound to `___ResponseTime_OutVsCall` and `___ResponseTime_DispVsCall` if not already present.
3. **Future months:** Run `response_time_batch_all_metrics.py` when new monthly timereports are available; ensure new CSV is dropped into `PowerBI_Date\Backfill\response_time_all_metrics\` (script writes there directly).
4. **New unmapped incidents:** Run `audit_unmapped_incidents.py` after new CAD exports; review CSV, update `CallType_Categories.csv` (or use `apply_calltype_additions.py`); update CallTypes `CHANGELOG.md` and `SUMMARY.md`.

---

## Version Summary

| Version | Date | Highlights |
|---------|------|------------|
| 1.17.14 | 2026-02-26 | Response time M code: add `Summary_Type` for DAX; handoff doc |
| 1.17.13 | 2026-02-26 | CallType 15 alias rows; 2024 unresolvable 166→2 |
| 1.17.12 | 2026-02-26 | Response time batch ETL + CallType mapping; 25 months, 3 metrics |
| 1.17.11 | 2026-02-26 | Response time Folder.Files + 13-month window + 2 new M queries |

---

**Contact:** R. A. Carucci  
**Repo:** Master_Automation (OneDrive — City of Hackensack)
