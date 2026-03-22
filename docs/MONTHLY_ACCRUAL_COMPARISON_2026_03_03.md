# Monthly Accrual and Usage Summary — Pre vs Post Refresh Comparison

**Date:** 2026-03-03  
**Files compared:**
- Pre-refresh: `2026_03_03_23_04_37_Monthly Accrual and Usage Summary.csv`
- Post-refresh: `2026_03_03_23_05_17_post_refresh_Monthly Accrual and Usage Summary.csv`
- Backfill: `PowerBI_Data\Backfill\2026_01\vcs_time_report\2026_01_Monthly Accrual and Usage Summary.csv`

---

## Summary

| Metric | Pre-Refresh | Post-Refresh | Backfill (2026_01) |
|--------|-------------|--------------|--------------------|
| **13-month window** | 01-25 → 01-26 | 02-25 → 02-26 | 12-24 → 12-25 |
| **Periods** | 13 months | 13 months | 14 months (includes 12-24) |
| **02-26 data** | ❌ Not present | ✅ Present (9 time categories) | ❌ Not present |
| **Rows** | 117 | 117 | 117+ |

---

## Pre-Refresh (23:04:37)

- **Window:** Feb 2025 (02-25) through Jan 2026 (01-26)
- **Latest month:** 01-26
- **02-26:** Not included (window ended at 01-26)

---

## Post-Refresh (23:05:17)

- **Window:** Feb 2025 (02-25) through Feb 2026 (02-26)
- **Latest month:** 02-26
- **02-26 values (sample):**
  - Accrued Comp. Time - Non-Sworn: 11.0
  - Accrued Comp. Time - Sworn: 194.5
  - Accrued Overtime - Non-Sworn: 151.0
  - Accrued Overtime - Sworn: 336.0
  - Comp (Hours): 216.0
  - Employee Sick Time (Hours): 2049.0
  - Injured on Duty (Hours): 32.0
  - Military Leave (Hours): 72.0
  - Used SAT Time (Hours): 393.0

---

## Backfill (2026_01)

- **Window:** Dec 2024 (12-24) through Dec 2025 (12-25)
- Used for historical months when ETL processes current month
- Does not include 02-26 (backfill predates February 2026)

---

## Conclusion

Post-refresh correctly rolled the 13-month window forward to include February 2026. Pre-refresh showed the prior window (ending 01-26). Backfill provides historical coverage for months not in the current ETL output.
