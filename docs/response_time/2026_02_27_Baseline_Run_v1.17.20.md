# Response Time Baseline Run — v1.17.20

**Date:** 2026-02-27 | **Analyst:** R. A. Carucci

---

## Summary

First run of the v1.17.19 filter logic from **raw exports only** — no backfill. Establishes a true 13‑month baseline for future runs.

### Changes from v1.17.19

| Item | Before | After |
|------|--------|-------|
| **Sources** | 2024 yearly + 2025 yearly + 2026-01 monthly (25 months) | 2025 yearly + 2026-01 monthly (13 months) |
| **Output path** | `PowerBI_Date\Backfill\response_time_all_metrics` | `PowerBI_Date\response_time_all_metrics` |
| **Output files** | 25 CSVs (2024-01 through 2026-01) | 13 CSVs (2025-01 through 2026-01) |

### Raw Export Paths Used

- `05_EXPORTS\_CAD\timereport\yearly\2025_full_timereport.xlsx`
- `05_EXPORTS\_CAD\timereport\monthly\2026_01_timereport.xlsx`

---

## Archive

Previous 25-month backfill archived to:

`Master_Automation\archive\response_time_backfill_pre_baseline_20260227\`

---

## Power BI Path Update

The three response time M code queries now read from:

```
C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\response_time_all_metrics
```

**If the PBIX file still references the old path:**

1. Open Power BI Desktop
2. Edit each of: `___ResponseTimeCalculator`, `___ResponseTime_OutVsCall`, `___ResponseTime_DispVsCall`
3. In the `Folder.Files` step, change:

   ```
   ...\PowerBI_Date\Backfill\response_time_all_metrics
   ```

   to:

   ```
   ...\PowerBI_Date\response_time_all_metrics
   ```

4. Apply & Close

The M code files in `m_code\response_time\` have been updated for this path.

---

## Run Output

13 monthly CSVs written to `PowerBI_Date\response_time_all_metrics\`:

- 2025_01 through 2025_12, 2026_01
- Each file: 9 rows (3 Response Types × 3 Metric Types)

---

## Visual Export Workflow (v1.17.21)

The three response time visuals are mapped in `Standards/config/powerbi_visuals/visual_export_mapping.json`:

| Power BI export name | Output file |
|----------------------|-------------|
| Average Response Time (Dispatch to On Scene) | `YYYY_MM_response_time_dispatch_to_onscene.csv` |
| Dispatch Processing Time (Call Received to Dispatch) | `YYYY_MM_dispatch_processing_time.csv` |
| Average Response Time (From Time Received to On Scene) | `YYYY_MM_response_time_received_to_onscene.csv` |

Exports go to `_DropExports`, then `python scripts/process_powerbi_exports.py` routes them to `Processed_Exports/response_time/`. No normalization required.

---

## Future Runs

When new monthly timereports are available:

1. Add the new monthly export to `05_EXPORTS\_CAD\timereport\monthly\`
2. Add the new source to `SOURCES` in `response_time_batch_all_metrics.py`
3. Run the ETL — it will append new CSVs to the folder
4. Export visuals to `_DropExports`, run `process_powerbi_exports.py`
5. Refresh Power BI
