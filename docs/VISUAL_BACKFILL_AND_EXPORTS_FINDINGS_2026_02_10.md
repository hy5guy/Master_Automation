# Visual Backfill and Export Findings – 2026-02-10

## Summary

Findings on (1) the **Monthly Accrual and Usage Summary** visual showing null/0 for some months, (2) **multiple export file sizes** in 05_EXPORTS, and (3) whether **CSV structure** issues are causing problems.

---

## 1. Visual not adding backfilled data / null values

### What the recent visual shows

From `data/visual_export/2026_12/2026_02_10_Monthly Accrual and Usage Summary.csv`:

- **01-26** has **0** for: Comp (Hours), Employee Sick Time (Hours), Injured on Duty (Hours), Military Leave (Hours), Used SAT Time (Hours).
- **01-26** has **non-zero** accruals: Accrued Comp/OT Sworn and Non-Sworn (e.g. 68, 150.5, 119, 344).

So the issue is **usage categories** for **January 2026** showing 0, not backfill for prior months.

### Root cause: January 2026 Time Off export is wrong

- **Overtime** `2026_01_otactivity.csv` is correct: real Jan 2026 rows (e.g. 2026-01-01, 2026-01-02).
- **Time Off** `2026_01_timeoffactivity.csv` is **not** January 2026 data:
  - Only 9 rows; dates are **2022-12-01** and **2022-12-23/30** (Dec 2022).
  - File is effectively placeholder or mislabeled.

Usage (Sick, SAT, Comp used, Military, IOD) comes **only from Time Off** in the ETL. So when the 2026_01 Time Off file has no real Jan 2026 data, the pipeline correctly outputs **0** for 01-26 usage. The visual is reflecting the ETL output; the fix is to correct the **source** Time Off export for 2026_01.

### How backfill is supposed to work (and does)

From the repo (SUMMARY.md, scripts, VERIFICATION_SUMMARY.md):

- The **13‑month visual** is built from:
  - **FIXED_monthly_breakdown_*.csv** → usage (Comp, Sick, SAT, Military, IOD)
  - **analytics_output/monthly_breakdown.csv** → accruals (Accrued Comp/OT by Sworn/Non-Sworn)
- To avoid null/0 in **prior** months, `scripts/overtime_timeoff_with_backfill.py`:
  1. Runs v10 for the current 13‑month window.
  2. Restores **historical** months in the FIXED file from `PowerBI_Date\Backfill\YYYY_MM\vcs_time_report\*Monthly Accrual and Usage Summary*.csv`.
  3. Backfills **monthly_breakdown.csv** for prior 12 months from that same backfill (keeps current month from v10).

So backfill is for **past** months. The 01-26 zeros are not a backfill bug; they come from the **current month** (Jan 2026) having no valid Time Off data in the export.

### Verification note (from VERIFICATION_SUMMARY.md)

- “November backfill was exported from a visual that only had October 2025 data populated. Historical usage months were not in that export.”
- So if a **backfill** export was saved when the visual only had partial months, those missing months will show 0 in the backfill. The restore script can only fill what’s in the backfill file. For **December 2025**, `Backfill\2025_12\vcs_time_report\2025_12_Monthly Accrual and Usage Summary.csv` exists and is **WIDE** format (month columns 10-24 … 10-25); the restore script supports both LONG and WIDE.

---

## 2. Export files – “three versions” and different sizes

### What’s in the folders

**Overtime month 2026**

- `2026_01_otactivity.csv`  (34,895 bytes, 02/09/2026)
- `2026_01_OTActivity.xls` (107,443 bytes, 02/09/2026)
- `2026_01_otactivity.xlsx` (20,678 bytes, 02/09/2026)

**Overtime yearly 2025**

- `2025_all_otactivity.csv`  (543,258 bytes)
- `2025_all_otactivity.xlsx` (250,674 bytes)

**Time Off month 2026**

- `2026_01_timeoffactivity.csv`  (1,105 bytes – very small; wrong content)
- `2026_01_timeoffactivity.xlsx` (5,781 bytes)

**Time Off yearly 2025**

- `2025_all_timeoffactivity.csv`  (997,395 bytes)
- `2025_all_timeoffactivity.xlsx` (346,800 bytes)

### Interpretation

- For **month/2026** and **yearly/2025** you may have **.xlsx** (and optionally original **.xls**) per watchdog v2.1.2: conversion is **.xlsx only** (no CSV). Different extensions → different sizes is normal.
- So the “three versions of 01/2026 data” with different sizes are the **three formats** (.csv, .xls, .xlsx) for the same logical export. That is expected and not by itself a structure error.
- The ETL prefers **.xlsx** over .csv over .xls. So as long as the .xlsx (or .csv) has the correct structure and content, pipeline behavior is determined by that file.

---

## 3. Past CSV structure issues – are they in play here?

### Response Time (different pipeline)

- There **was** a CSV structure issue: **Response Time** visual_exports had column names that didn’t match the M code (e.g. `First Response_Time_MMSS` vs `Response_Time_MMSS`), causing 69% empty values. This was fixed in M code v2.5.0 and is documented in `docs/RESPONSE_TIME_FINAL_FIX_v2.5.0.md` and chatlogs (Power_BI_Response_Time_Type_Conversion_Fix). That issue is **not** in the Overtime/TimeOff ETL.

### Overtime/TimeOff – structure is supported

- **FIXED** input: the v10 script and Power BI expect the standard FIXED columns (Period, Accrued_Comp_Time, Employee_Sick_Time_Hours, Used_SAT_Time_Hours, etc.). No mismatch was found.
- **Backfill** input: `restore_fixed_from_backfill.py` and `backfill_monthly_breakdown_from_backfill()` in `overtime_timeoff_with_backfill.py` explicitly support **two** shapes:
  - **LONG**: `Time Category` (or `Time_Category`), `Sum of Value` (or `Value`), `PeriodLabel`
  - **WIDE**: `Time_Category` + one column per month (e.g. `10-24`, `11-24`, …)
- The 2025_12 backfill file is WIDE; the 2026_02_10 visual export is LONG. Both are valid. So the current null/0 for 01-26 is **not** due to an incorrect CSV structure for backfill or FIXED.

### ETL Overtime/TimeOff docs

- **USAGE_HIGH_VALUES_REPORT.md** – December usage ~2x expected (dedup/aggregation), not CSV structure.
- **DECEMBER_HIGH_VALUES_INVESTIGATION_REPORT.md** – Double-counting from processing both “all” and month-specific files; fixed with deduplication.
- **ETL_COMPLETION_REPORT.md** – Deduplication and personnel path fixes.
- **SYNTAX_ERRORS_SUMMARY.md** – M code syntax in `2026_01_12____Overtime_Timeoff_v3.m`, not CSV layout.

So: the **past** structure issue was in **Response Time** CSVs and M code. For **Overtime/TimeOff**, CSV structure (including LONG vs WIDE backfill) is handled; the 01-26 zeros are due to **bad Time Off source data** for 2026_01, not structure.

---

## 4. Recommendations

1. **Fix January 2026 Time Off export**
   - Replace `05_EXPORTS\_Time_Off\export\month\2026\2026_01_timeoffactivity.csv` (and .xlsx if same content) with the **real** January 2026 Time Off export from the source system.
   - Re-run the Overtime/TimeOff pipeline (with backfill) so FIXED and monthly_breakdown include correct 01-26 usage.
   - Re-export or refresh the visual to confirm 01-26 usage is no longer 0.

2. **Keep one format per export if you want to avoid confusion**
   - If you only need one format, keep .xlsx (and optionally .csv) and archive or skip generating .xls so “three versions” is clearly one export in one or two formats.

3. **Backfill workflow**
   - After each month’s run, save the **current** visual export to `PowerBI_Date\Backfill\YYYY_MM\vcs_time_report\` (e.g. `2026_01_Monthly Accrual and Usage Summary.csv`) so next month’s backfill has full history. The VERIFICATION_SUMMARY note (November backfill only having October data) is exactly the “visual not adding backfilled data” case when the **saved** backfill file was incomplete.

4. **Confirm Power BI sources**
   - Ensure Power BI points at the correct FIXED file (e.g. `FIXED_monthly_breakdown_2025-01_2026-01.csv` for the current 13‑month window) and that you refresh after re-running the pipeline.

---

## 5. References (in repo)

- `SUMMARY.md` – Overtime TimeOff backfill + processed month, null/0 prevention.
- `scripts/overtime_timeoff_with_backfill.py` – Backfill root, restore, backfill_monthly_breakdown_from_backfill (LONG/WIDE).
- `scripts/restore_fixed_from_backfill.py` – LONG vs WIDE detection, legacy_map, required FIXED columns.
- `02_ETL_Scripts/Overtime_TimeOff/VERIFICATION_SUMMARY.md` – Accrual verification; usage 0 when backfill export lacked those months.
- `02_ETL_Scripts/Overtime_TimeOff/COMPLETE_AI_VERIFICATION_PACKAGE.md` – Backfill formats (December LONG, November WIDE).
- `docs/RESPONSE_TIME_FINAL_FIX_v2.5.0.md` and Power_BI_Response_Time_Type_Conversion_Fix chatlogs – CSV column/structure fix for Response Time only.

---

## Appendix: Time Off reasons the script uses (v10)

The script classifies rows by the **Reason** column (and fallback text in other columns). Only these usage buckets feed the visual:

| Visual category | Reason(s) from your list that count |
|-----------------|-------------------------------------|
| **Comp (Hours)** | Comp (Hours) |
| **Employee Sick Time (Hours)** | Sick (Days), PEO Sick (Hours), SLEO Ill Sick (Hours) |
| **Used SAT Time (Hours)** | SAT (Hours), Dispatch SAT time |
| **Military Leave (Hours)** | Military Leave |
| **Injured on Duty (Hours)** | Injured on Duty |
| **Vacation (Hours)** | Vacation (Hours), Personal Day* |

\* Vacation bucket: script also matches “annual”, “pto”, “personal time off”, “personal day” (regex). **Personal Day** is counted as vacation. **Floating Holiday (hours)** is not matched and is not in any of the six usage buckets.

**Reasons not used for the six usage totals** (no impact on the Monthly Accrual and Usage Summary):  
Adjustment, Admin Leave, AWOL, Death in Family, FMLA, Holiday, Jury Duty, Marriage Leave, Maternity/Paternity, Pool Day, Regular Day Off, Suspended, Unpaid.

**Technical detail:** Classification is “Reason-first” (regex on the `Reason` column), then fallback search in other text columns. So the export must include a **Reason** column with values exactly as above (e.g. `Comp (Hours)`, `Sick (Days)`, `SAT (Hours)`, `Military Leave`, `Injured on Duty`, `Vacation (Hours)`). See `overtime_timeoff_13month_sworn_breakdown_v10.py` lines 57–70 and 504–527.

---

*Generated 2026-02-10 from Master_Automation repo and 05_EXPORTS/02_ETL_Scripts/Overtime_TimeOff/ PowerBI_Date/Backfill.*
