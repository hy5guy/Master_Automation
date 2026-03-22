# Power BI Template MCP Update — 2026-03-19

**Status:** ✅ Complete
**Session:** Claude Desktop MCP injection
**Template:** `08_Templates\Monthly_Report_Template.pbix`
**Context:** Directory consolidation refactor (PowerBI_Date → PowerBI_Data)

---

## Summary

Claude Desktop successfully injected path corrections and DAX fixes into the Monthly Report Template via MCP. This completed the directory consolidation project and resolved several subtitle and data issues.

---

## 1. M-Code Paths Updated (4 Response Time Partitions)

| Partition | Change |
|-----------|--------|
| `___ResponseTime_DispVsCall` | `PowerBI_Date` → `PowerBI_Data` |
| `___ResponseTime_OutVsCall` | `PowerBI_Date` → `PowerBI_Data` |
| `___ResponseTimeCalculator` | `PowerBI_Date` → `PowerBI_Data` |
| `___ResponseTime_AllMetrics` | `PowerBI_Date` → `PowerBI_Data` |

---

## 2. DAX Subtitles Standardized (13 Measures)

13 lagged/broken subtitle measures were rewritten to use a standardized 13-month rolling date format based on `___DimMonth`.

**Fixes:**
- Stale dates when underlying source data had not been updated
- `FIRSTNONBLANK` error in `Subtitle_V3_Accrual`
- Missing column error in `Metrics Qual Subtitle`

---

## 3. New Measure Created

- **Measure:** `Subtitle_DeptWide_Summons`
- **Table:** `summons_13month_trend`

---

## 4. Data Discrepancy Resolved (Use of Force)

- **Issue:** 75 vs 78 count discrepancy for "Use of Force" incidents
- **Cause:** `IncidentCount_13Month` measure — `EDATE` was returning an end-of-month date that excluded February 2025
- **Fix:** Rewritten to normalize to start-of-month date

---

## 5. Cosmetic Deferral

- **Updated:** `STACP_DIAGNOSTIC` comment header → `06_Workspace_Management`
- **Deferred (intentional):** Comment header updates for `___STACP_pt_1_2`, `___Detectives`, and `ESU_13Month` to avoid unnecessary risk to the live AS engine. Local extracted source files are already correct.

---

## Related Documentation

- [CHANGELOG.md](../CHANGELOG.md) — v1.18.13
- [POWERBI_REFRESH_REQUIRED_2026_02_26.md](response_time/POWERBI_REFRESH_REQUIRED_2026_02_26.md) — Status: COMPLETE
- [MONTHLY_REPORT_TEMPLATE_WORKFLOW.md](MONTHLY_REPORT_TEMPLATE_WORKFLOW.md)
- [IMPLEMENTATION_CHECKLIST_Directory_Consolidation.md](../_consolidation_project/IMPLEMENTATION_CHECKLIST_Directory_Consolidation.md) — Phase 4.11 complete; project closed out
