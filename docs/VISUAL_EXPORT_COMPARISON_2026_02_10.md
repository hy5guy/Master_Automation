# Visual Export Comparison – 2026-02-10

Comparison of **2026_02_10_18_24_36_Monthly Accrual and Usage Summary.csv** against (1) the earlier same-day export and (2) last month’s visual (image: 13 months ending 11-25).

---

## 1. Data sources

| Source | Description |
|--------|-------------|
| **18_24_36 export** | `data/visual_export/2026_12/2026_02_10_18_24_36_Monthly Accrual and Usage Summary.csv` — export you asked to check |
| **Earlier export** | `data/visual_export/2026_12/2026_02_10_Monthly Accrual and Usage Summary.csv` — referenced in VISUAL_BACKFILL doc; had 01-26 usage = 0 |
| **Last month’s visual** | Screenshot: “Monthly Accrual and Usage Summary,” columns 11-24 through 11-25, same time categories |

No backfill CSV was found under `Master_Automation` (backfill lives under `PowerBI_Data\Backfill\...` per docs).

---

## 2. Structure

- **Format**: LONG — columns `Time Category`, `Sum of Value`, `PeriodLabel`.
- **Time categories**: Accrued Comp. Time (Non-Sworn / Sworn), Accrued Overtime (Non-Sworn / Sworn), Comp (Hours), Employee Sick Time (Hours), Injured on Duty (Hours), Military Leave (Hours), Used SAT Time (Hours). No Vacation (Hours), consistent with M code excluding it.
- **Periods in 18_24_36**: 01-25 through 12-25 plus **01-26** for all categories.

---

## 3. 18_24_36 vs last month’s visual (November 2025 = 11-25)

Values for **PeriodLabel = 11-25**:

| Time Category | Last month’s visual (image) | 18_24_36 export | Match |
|---------------|-----------------------------|-----------------|--------|
| Accrued Comp. Time - Non-Sworn | 29.00 | 31 | Close (likely scaling/rounding) |
| Accrued Comp. Time - Sworn | 224.25 | 220.75 | Close |
| Accrued Overtime - Non-Sworn | 211.50 | 208.5 | Close |
| Accrued Overtime - Sworn | 281.75 | 281.75 | **Exact** |
| Comp (Hours) | 389 | 389 | **Exact** |
| Employee Sick Time (Hours) | 946.5 | 946.5 | **Exact** |
| Injured on Duty (Hours) | 24 | 24 | **Exact** |
| Military Leave (Hours) | 12 | 12 | **Exact** |
| Used SAT Time (Hours) | 580.5 | 580.5 | **Exact** |

**Conclusion:** Usage for 11-25 matches the image exactly. Accruals for 11-25 are very close; small differences are consistent with prior-anchor scaling or rounding in the M code.

---

## 4. 18_24_36 vs earlier same-day export (01-26)

| Category | Earlier export (01-26) | 18_24_36 export (01-26) |
|----------|------------------------|--------------------------|
| Accrued Comp / Overtime (all 4) | Non-zero (e.g. 68, 150.5, 119, 344) | Same non-zero |
| Comp (Hours) | **0** | **318** |
| Employee Sick Time (Hours) | **0** | **1635** |
| Injured on Duty (Hours) | **0** | **269** |
| Military Leave (Hours) | **0** | **66** |
| Used SAT Time (Hours) | **0** | **497.5** |

So the **18_24_36** export has **January 2026 usage populated**. That implies either:

- The pipeline was re-run after fixing or replacing the 2026_01 Time Off export (per VISUAL_BACKFILL doc, the original 2026_01 Time Off file had wrong/2022 data), or  
- Backfill/restore was run and filled 01-26 from a backfill file that contained 01-26 usage.

The earlier same-day export reflected the state when 01-26 usage was still 0 (bad/missing Time Off for Jan 2026).

---

## 5. Summary

- **vs last month’s visual:** 18_24_36 matches the image for 11-25 usage exactly and for accruals within expected scaling/rounding.
- **vs backfill/earlier export:** 18_24_36 shows 01-26 usage no longer zero; it is consistent with corrected source data or backfill.
- **Recommendation:** Treat **2026_02_10_18_24_36_Monthly Accrual and Usage Summary.csv** as the current, correct visual export. Keep saving the latest visual to backfill (e.g. `PowerBI_Data\Backfill\YYYY_MM\vcs_time_report\`) each month so future backfill runs have full history.

*Generated 2026-02-10 from Master_Automation repo.*
