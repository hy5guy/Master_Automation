# Visual Export Normalize and Backfill (Automation)

Why and how we make **default** Power BI visual exports usable for backfill without manual reformatting.

---

## 1. The problem (Long vs Wide, naming)

- **Default export**: Power BI often exports a table visual in **Long** format: one row per (Time Category, Period), with columns like `Time Category`, `Sum of Value`, `PeriodLabel`.
- **Legacy / other tools**: Some logic expects **Wide** format (months as column headers, e.g. `01-25`, `02-25`, …).
- **Naming**: Exports may use `Sum of Value` or `Sum of  Value`; column headers for months might appear as `Sum of 11-25` instead of `11-25`.

If you had to manually pivot or rename every month, the workflow would not scale.

---

## 2. What the pipeline already accepts

The Master_Automation pipeline **already** accepts the default Long export:

- **restore_fixed_from_backfill.py**  
  - Reads both **Long** and **Wide** backfill CSVs.  
  - Accepts `Time Category` or `Time_Category`, and `Value` or `Sum of Value` (and variants).  
  - Normalizes month labels (e.g. `Sum of 11-25` → `11-25`) internally.

- **overtime_timeoff_with_backfill.py** (and its `backfill_monthly_breakdown_from_backfill` step)  
  - Same: Long or Wide, and the same column name variants.

So you **do not** need to change how you export from Power BI for the pipeline to work. The remaining need is to get the file to the **right place** with a **consistent name** and, if needed, normalized labels.

---

## 3. Script: normalize_visual_export_for_backfill.py

To keep the workflow automated and consistent, use the normalizer script:

**Role:**

- Take a **default** visual export (Long or Wide).
- Normalize column names and period labels (e.g. `Sum of 11-25` → `11-25`).
- Write to the standard backfill path with the standard filename so the next pipeline run picks it up.

**Usage:**

```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"

# Normalize and write to Backfill\2025_12\vcs_time_report\2025_12_Monthly Accrual and Usage Summary.csv
# (backfill month inferred from filename 2025_12_... or set explicitly)
python scripts\normalize_visual_export_for_backfill.py --input "path\to\2025_12_Monthly Accrual and Usage Summary.csv"

# Explicit backfill month
python scripts\normalize_visual_export_for_backfill.py --input "path\to\export.csv" --backfill-month 2025_12

# Output Wide format instead of Long (for consumers that only accept Wide)
python scripts\normalize_visual_export_for_backfill.py --input "path\to\export.csv" --backfill-month 2025_12 --wide

# Preview only
python scripts\normalize_visual_export_for_backfill.py --input "path\to\export.csv" --backfill-month 2025_12 --dry-run
```

**Behavior:**

- **Input Long**: Normalizes `Time Category`, `Sum of Value`, `PeriodLabel`; cleans period labels; writes Long by default, or Wide if `--wide`.
- **Input Wide**: Normalizes month column headers (e.g. `Sum of 01-25` → `01-25`); writes to the same backfill path.
- **Output path** (if not using `--output`):  
  `{--backfill-root}\{YYYY_MM}\vcs_time_report\{YYYY_MM}_Monthly Accrual and Usage Summary.csv`  
  So the next run of `overtime_timeoff_with_backfill.py` can use this file as the backfill for that month.

---

## 4. Recommended workflow

1. **Export** from Power BI: “Monthly Accrual and Usage Summary” visual → save as CSV (default Long format is fine).
2. **Normalize and deploy** (one of):
   - Run `normalize_visual_export_for_backfill.py --input <path> [--backfill-month YYYY_MM]` so the file is written to `Backfill\YYYY_MM\vcs_time_report\`.
   - Or manually copy the export to `PowerBI_Data\Backfill\YYYY_MM\vcs_time_report\` and name it `YYYY_MM_Monthly Accrual and Usage Summary.csv`. The pipeline accepts Long as-is; the script is for consistency and label cleaning.
3. **Pipeline**: Run `python scripts\overtime_timeoff_with_backfill.py` when you want to refresh FIXED and monthly_breakdown from that backfill.

---

## 5. Optional: Watchdog / organize script

Gemini’s suggestion to “add a rule to detect Monthly Accrual and Usage Summary and move it to backfill_source” fits here:

- If you use a **watchdog** or an **organize** script (e.g. `organize_backfill_exports.ps1` in PowerBI_Date):
  - Add a rule: when a file matching `*Monthly Accrual and Usage Summary*.csv` appears in a designated folder, either:
    - **Move/copy** it to `Backfill\YYYY_MM\vcs_time_report\` with the standard name, or
    - **Run** `normalize_visual_export_for_backfill.py --input <path> --backfill-month YYYY_MM` and write the result to that path.

That keeps the “export from Power BI → backfill in place” step fully automated.

---

## 6. Summary

| Item | Status |
|------|--------|
| Long vs Wide | Pipeline accepts **both**; normalizer can convert Long → Wide if needed. |
| “Sum of Value” | Accepted by restore and pipeline; normalizer can standardize to `Sum of Value`. |
| Period labels | Restore script normalizes `Sum of 11-25` → `11-25`; normalizer does the same. |
| Naming / location | Normalizer writes to `Backfill\YYYY_MM\vcs_time_report\YYYY_MM_Monthly Accrual and Usage Summary.csv`. |
| Automation | Use the normalizer after export, or wire it (or a simple move/copy) into watchdog/organize. |

*Updated 2026-02-10 – Master_Automation.*
