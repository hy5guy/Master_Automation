# Backfill data (Monthly Accrual and Usage Summary)

**Primary source:** `data/visual_export/2026_12/2025_12_Monthly Accrual and Usage Summary.csv` — the up-to-date visual export (13 months: 12-24 through 12-25).

## Files in this folder

| File | Description |
|------|-------------|
| **2025_12_Monthly_Accrual_and_Usage_Summary.csv** | Copy of the 2025_12 visual export. LONG format (Time Category, Sum of Value, PeriodLabel). Use as the December backfill. |
| **backfill_from_image_11-25_only.csv** | November 2025 (11-25) only — 9 rows. Use to patch just 11-25 if needed. |
| **Monthly_Accrual_and_Usage_Summary_backfill_from_image.csv** | Earlier full backfill (01-25–12-25 + 01-26) with 11-25 overwritten from image. Superseded by the 2025_12 export above. |

## Deployed (PowerBI_Date)

- **2025_12:** `PowerBI_Date\Backfill\2025_12\vcs_time_report\2025_12_Monthly Accrual and Usage Summary.csv` — updated from the 2025_12 visual export. Pipeline/restore for December will use this.
- **2025_11:** `PowerBI_Date\Backfill\2025_11\vcs_time_report\2025_11_Monthly Accrual and Usage Summary.csv` — previously deployed (image-corrected).

## How to replace or update backfill

1. **Backfill location** (used by `overtime_timeoff_with_backfill.py` and `restore_fixed_from_backfill.py`):
   ```
   C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\YYYY_MM\vcs_time_report\
   ```

2. To use the **2025_12 export** for another month folder: copy  
   `data/visual_export/2026_12/2025_12_Monthly Accrual and Usage Summary.csv`  
   to `PowerBI_Date\Backfill\YYYY_MM\vcs_time_report\YYYY_MM_Monthly Accrual and Usage Summary.csv`.

3. **Run restore:**
   ```powershell
   python scripts\restore_fixed_from_backfill.py --fixed "C:\...\02_ETL_Scripts\Overtime_TimeOff\output\FIXED_monthly_breakdown_....csv" --backfill "C:\...\PowerBI_Date\Backfill\2025_12\vcs_time_report\2025_12_Monthly Accrual and Usage Summary.csv" --inplace
   ```
   Add `--include-accruals` to restore Accrued_Comp_Time and Accrued_Overtime_Paid from the backfill.

## Automating default exports (Long → backfill)

Power BI’s default export is often **Long** (Time Category, Sum of Value, PeriodLabel). The pipeline already accepts that. To normalize labels and write to the correct Backfill path in one step, use:

```powershell
python scripts\normalize_visual_export_for_backfill.py --input "path\to\export.csv" [--backfill-month 2025_12]
```

See **docs/VISUAL_EXPORT_NORMALIZE_AND_BACKFILL.md** for full workflow and optional watchdog/organize integration.

*Updated 2026-02-10 – Master_Automation. Primary backfill is now the 2025_12 visual export.*
