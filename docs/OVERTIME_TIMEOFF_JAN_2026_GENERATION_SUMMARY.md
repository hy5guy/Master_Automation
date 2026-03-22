# Overtime/TimeOff January 2026 Data Generation - Summary Report

**Date**: 2026-02-14  
**Status**: ✅ **SUCCESS** - Pipeline Complete  
**Window**: 2025-01 through 2026-01 (13 months)

---

## Executive Summary

The Overtime/TimeOff automation successfully processed January 2026 data from the source Excel exports and generated updated output files with proper 13-month rolling window coverage.

**Key Results:**
- ✅ January 2026 data successfully generated
- ✅ All 13 months (01-25 through 01-26) populated
- ✅ FIXED schema validated
- ✅ Backfill integration complete
- ✅ Ready for Power BI refresh

---

## Pipeline Execution Details

### Source Files Processed

| Type | File Path | Status |
|------|-----------|--------|
| **Overtime** | `05_EXPORTS\_Overtime\export\month\2026\2026_01_otactivity.xlsx` | ✅ Found |
| **Time Off** | `05_EXPORTS\_Time_Off\export\month\2026\2026_01_timeoffactivity.xlsx` | ✅ Found |
| **Backfill** | `PowerBI_Data\Backfill\2025_12\vcs_time_report\2025_12_Monthly Accrual and Usage Summary.csv` | ✅ Used |

### Data Processing Stats

```
Rows loaded:
  - Overtime: 25,758
  - Time Off: 31,528
  - Combined: 57,286

After deduplication: 28,821 rows (removed 28,465 duplicates)
After approved filter: 28,552 rows
In 13-month window: 10,060 rows
```

### Output Files Generated

| File | Path | Status |
|------|------|--------|
| **FIXED_monthly_breakdown** | `02_ETL_Scripts\Overtime_TimeOff\output\FIXED_monthly_breakdown_2025-01_2026-01.csv` | ✅ 13 rows |
| **monthly_breakdown** | `02_ETL_Scripts\Overtime_TimeOff\analytics_output\monthly_breakdown.csv` | ✅ 52 rows |

---

## January 2026 Data Comparison

### Backfill Reference Data (12-24 through 12-25)

The backfill file (`overtime_timeoff_backfill.txt`) contains validated data for months 12-24 through 12-25. This data served as the baseline for historical months.

**Key Backfill Metrics (Sample - December 2025):**
- Accrued Comp. Time - Non-Sworn: 55.00 hours
- Accrued Comp. Time - Sworn: 111.00 hours  
- Employee Sick Time: 1,078.00 hours
- Injured on Duty: 32.00 hours
- Military Leave: 24.00 hours

### Generated January 2026 Data

**From FIXED_monthly_breakdown (2026-01 row):**
| Category | Hours |
|----------|-------|
| Employee Sick Time | 1,635.00 |
| Used SAT Time | 497.50 |
| Vacation | 905.50 |
| Comp (Used) | 318.00 |
| Military Leave | 66.00 |
| Injured on Duty | 269.00 |
| **Accrued Comp Time** | **218.50** |
| **Accrued Overtime** | **463.00** |

**From monthly_breakdown (2026-01 by class):**
| Class | Metric | Hours |
|-------|--------|-------|
| NonSworn | Accrued Comp. Time | 68.00 |
| NonSworn | Accrued Overtime | 119.00 |
| Sworn | Accrued Comp. Time | 150.50 |
| Sworn | Accrued Overtime | 344.00 |

**Totals Reconciliation:**
- Accrued Comp. Time: 68.00 + 150.50 = **218.50** ✅ (matches FIXED)
- Accrued Overtime: 119.00 + 344.00 = **463.00** ✅ (matches FIXED)

---

## Data Validation

### ✅ Schema Validation
```
[OK] FIXED schema validated.
```

All columns present and correctly typed:
- Year, Month, Month_Name, Period, Date
- Accrued_Comp_Time, Accrued_Overtime_Paid
- Employee_Sick_Time_Hours, Used_SAT_Time_Hours
- Vacation_Hours, Used_Comp_Time
- Military_Leave_Hours, Injured_on_Duty_Hours

### ✅ Window Coverage
```
Window: 2025-01-01 -> 2026-01-31 (13 months)
```

**All months populated:**
- 2025-01 through 2025-12 (12 months from backfill + current data)
- 2026-01 (newly generated from January exports)

### ✅ Totals Reconciliation
```
Accrued Comp. Time: Total=3612.75
Accrued Overtime:   Total=7691.75
[OK] Comp (window): 3612.75 reconciles
[OK] Overtime (window): 7691.75 reconciles
```

---

## Backfill Integration Details

### Backfill File Used
```
C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Backfill\2025_12\vcs_time_report\2025_12_Monthly Accrual and Usage Summary.csv
```

**Backfill restored historical data (2025-01 through 2025-12) for:**
- Accrued Comp. Time (Sworn/Non-Sworn split)
- Accrued Overtime (Sworn/Non-Sworn split)

**Note:** Vacation (Hours) was removed from the legacy LONG table per requirements.

### FIXED File Updates
```
[OK] Backup created: FIXED_monthly_breakdown_2025-01_2026-01.csv.bak
[OK] FIXED written: FIXED_monthly_breakdown_2025-01_2026-01.csv
[OK] Rows updated: 12/13
[OK] Cells updated: 60
```

The script:
1. Generated new January 2026 data from source Excel files
2. Restored historical months (01-25 through 12-25) from backfill
3. Combined into single 13-month dataset

---

## Monthly Breakdown (analytics_output)

The `monthly_breakdown.csv` file contains the **Sworn/Non-Sworn split** for accrual metrics:

**Structure (52 rows = 13 months × 2 classes × 2 metrics):**
- 13 months: 2025-01 through 2026-01
- 2 classes: Sworn, NonSworn
- 2 metrics: Accrued Comp. Time, Accrued Overtime

**January 2026 Breakdown:**
| Class | Accrued Comp | Accrued OT |
|-------|--------------|------------|
| NonSworn | 68.00 | 119.00 |
| Sworn | 150.50 | 344.00 |
| **Total** | **218.50** | **463.00** |

---

## Power BI Integration

### M Code Query: `___Overtime_Timeoff_v3`

The provided M code is configured to:

1. **Load FIXED_monthly_breakdown** (legacy usage categories)
   - Employee Sick Time, Used SAT Time, Comp (Used)
   - Military Leave, Injured on Duty
   - ~~Vacation~~ (filtered out)

2. **Load monthly_breakdown** (sworn-split accruals)
   - Accrued Comp. Time - Sworn/Non-Sworn
   - Accrued Overtime - Sworn/Non-Sworn

3. **Apply 13-month rolling window**
   - Current logic: Exclude current month, show previous 13
   - As of Feb 2026: Shows 2025-01 through 2026-01

4. **Optional anchoring** (controlled by `UseAnchoring` flag)
   - Anchors periods before 09-25 to published summary
   - Raw values from 09-25 onward

5. **Output format: LONG table**
   - Columns: Time_Category, PeriodLabel, PeriodDate, PeriodKey, DateSortKey, Value
   - All categories × all periods (zero-filled for missing data)

---

## Next Steps for Power BI Refresh

### 1. Refresh the Data Source

In Power BI Desktop:
1. Open the report with `___Overtime_Timeoff_v3` query
2. Go to **Home** → **Refresh**
3. The query will automatically load the updated CSV files

### 2. Verify January 2026 Data Appears

Check the visual to confirm:
- [x] Shows 13 months: 01-25 through 01-26
- [x] January 2026 values match expected:
  - Accrued Comp. Time - Non-Sworn: 68.00
  - Accrued Comp. Time - Sworn: 150.50
  - Employee Sick Time: 1,635.00
  - Used SAT Time: 497.50

### 3. Expected Visual Output

The "Monthly Accrual and Usage Summary" visual should display:

**January 2026 Column (01-26):**
| Category | Value |
|----------|-------|
| Accrued Comp. Time - Non-Sworn | 68 |
| Accrued Comp. Time - Sworn | 151 |
| Accrued Overtime - Non-Sworn | 119 |
| Accrued Overtime - Sworn | 344 |
| Employee Sick Time (Hours) | 1,635 |
| Used SAT Time (Hours) | 498 |
| Comp (Hours) | 318 |
| Military Leave (Hours) | 66 |
| Injured on Duty (Hours) | 269 |

---

## Files Created/Updated

### Output Files
```
C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Overtime_TimeOff\output\
├── FIXED_monthly_breakdown_2025-01_2026-01.csv (13 rows) ✅ UPDATED
└── FIXED_monthly_breakdown_2025-01_2026-01.csv.bak (backup)

C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Overtime_TimeOff\analytics_output\
└── monthly_breakdown.csv (52 rows) ✅ UPDATED
```

### Documentation
```
C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\docs\
└── OVERTIME_TIMEOFF_JAN_2026_GENERATION_SUMMARY.md (this file)
```

---

## Troubleshooting

### If 01-26 doesn't appear in the visual:

1. **Check Power Query refresh status**
   - Open Power Query Editor
   - Click on `___Overtime_Timeoff_v3` query
   - Look at the last step - does it show 01-26 in PeriodLabel column?

2. **Check rolling window calculation**
   - The M code calculates window based on current date
   - As of Feb 2026, should show 01-25 through 01-26
   - Verify `NowDT`, `EndY`, `EndM` values

3. **Check visual filters**
   - Click on the visual
   - Check Filters pane for any date/period filters
   - Remove or adjust if filtering out 01-26

4. **Check source files**
   - Verify source files exist and contain data:
     - `2026_01_otactivity.xlsx`
     - `2026_01_timeoffactivity.xlsx`
   - Re-run automation if needed

---

## Historical Context

### Backfill Baseline (12-24 through 12-25)

The `overtime_timeoff_backfill.txt` file contains the **reference data** exported from a previous visual refresh. This ensures:

1. **Historical accuracy**: Months 12-24 through 12-25 match published reports
2. **Consistency**: The Sworn/Non-Sworn split is preserved
3. **Validation**: New data can be compared against known-good baseline

**Note:** The backfill includes slight precision differences in some months (e.g., May 2025 shows 30.672535... in backfill vs 30.67 in reference). This is expected due to rounding in visual exports.

---

## Summary

✅ **Automation Status**: Complete  
✅ **Data Generation**: Successful  
✅ **Schema Validation**: Passed  
✅ **Backfill Integration**: Complete  
✅ **Reconciliation**: All totals match  
✅ **Ready for Power BI**: Yes

**The Overtime/TimeOff data is ready for Power BI refresh. January 2026 (01-26) data will appear in the visual after refreshing the data source.**

---

**Generated by**: Master_Automation Pipeline  
**Script**: `overtime_timeoff_with_backfill.py`  
**Date**: 2026-02-14  
**Execution Time**: 16.1 seconds
