# What to do after updating the backfill (2025_12 export)

## 1. Re-run the Overtime/TimeOff pipeline

From the **Master_Automation** folder (PowerShell or Command Prompt):

```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
python scripts\overtime_timeoff_with_backfill.py
```

- The pipeline uses **end month = last month** (e.g. Jan 2026 if today is Feb 2026). It looks for backfill for that month first; if missing, it uses **2025_12**, which is where we deployed the new export.
- It will:
  1. Ensure month exports are .xlsx if needed.
  2. Run v10 to produce the 13‑month FIXED and monthly_breakdown.
  3. **Restore FIXED** from the backfill CSV (your 2025_12 export).
  4. **Backfill monthly_breakdown** from the same CSV for history months.

Optional: preview without writing files:

```powershell
python scripts\overtime_timeoff_with_backfill.py --dry-run
```

## 2. Refresh Power BI

After the pipeline finishes:

- Open the report and **Refresh** the **___Overtime_Timeoff_v3** query (or Refresh All).
- The Monthly Accrual and Usage Summary visual will then use the updated FIXED + monthly_breakdown (12-24 through 12-25 from the 2025_12 export).

## Summary

| Step | Action |
|------|--------|
| 1 | Run `python scripts\overtime_timeoff_with_backfill.py` from Master_Automation |
| 2 | Refresh Power BI (___Overtime_Timeoff_v3 or Refresh All) |

No other steps are required; the backfill file is already in `PowerBI_Data\Backfill\2025_12\vcs_time_report\`.
