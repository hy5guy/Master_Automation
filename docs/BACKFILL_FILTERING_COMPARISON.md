# Backfill Filtering Comparison & Issues Found

**Date:** 2025-12-10  
**Issue:** November 2025 response times don't match backfill data structure

---

## 🔴 Critical Discrepancies Found

### Issue 1: Response Time Threshold Mismatch

**Backfill Generation Scripts Use:**
- `calc_response_time_test.py`: Filters `<= 10` minutes (line 102)
- `generate_backfilled_monthly_summary.py`: Filters `<= 10` minutes (line 136)

**Current Script (`process_cad_data_for_powerbi_FINAL.py`):**
- **Before fix:** Filtered `<= 60` minutes
- **After fix:** Filters `< 25` minutes (per PROJECT_SUMMARY)
- **Should be:** Filters `<= 10` minutes (to match backfill generation)

**Impact:** November 2025 data includes response times 10-25 minutes that backfill excludes, causing higher averages.

---

### Issue 2: Missing Administrative Incident Filtering

**Backfill Scripts Exclude:**
- List of ADMIN_INCIDENTS including:
  - Task Assignment
  - Meal Break
  - Relief / Personal
  - Administrative Assignment
  - Traffic Detail
  - Patrol Check
  - TAPS variants
  - And more (see `calc_response_time_test.py` lines 20-40)

**Current Script:**
- ❌ Does NOT exclude ADMIN_INCIDENTS
- ✅ Only excludes "Self-Initiated" (if column exists)
- ✅ Only excludes "Motor Vehicle Stop"

**Impact:** Administrative incidents are included in November 2025 calculations but excluded from backfill, causing discrepancy.

---

### Issue 3: Calculation Method Difference

**Backfill Scripts:**
- Use: `(Time Out - Time Dispatched)` calculation (line 100 in calc_response_time_test.py)
- Fallback to `Time Response` if missing (line 127 in generate_backfilled_monthly_summary.py)

**Current Script:**
- Uses: `Time Response` column directly (timedelta objects)

**Impact:** May produce slightly different values if timing differs.

---

## ✅ Required Fixes

### Fix 1: Update Response Time Threshold to 10 Minutes

```python
# Change from:
(df['Response_Time_Minutes'] < 25)  # Current

# To:
(df['Response_Time_Minutes'] <= 10)  # Match backfill
```

### Fix 2: Add Administrative Incident Filtering

```python
ADMIN_INCIDENTS = {
    "Task Assignment",
    "Meal Break",
    "Relief / Personal",
    "Administrative Assignment",
    "Traffic Detail",
    "Patrol Check",
    "TAPS - Park",
    "TAPS - Housing",
    "TAPS - Parking Garage",
    "TAPS - Other",
    "TAPS - ESU - Medical Facility",
    "TAPS - ESU - Business",
    "Overnight Parking",
    "Car Wash",
    "OPRA Request",
    "Records Request - DCPP (DYFS)",
    "Applicant ABC License",
    "Canceled Call",
    "UAS Operation"
}

# In apply_filters():
df = df[~df['Incident'].isin(ADMIN_INCIDENTS)].copy()
```

### Fix 3: Verify Backfill Values Match Exactly

Compare backfill file values:
- Emergency 10-25: 2:49 (2.81 minutes)
- Routine 10-25: 2:11 (2.18 minutes)
- Urgent 10-25: 2:52 (2.87 minutes)

These should match what the script produces for October 2025.

---

## Verification Checklist

- [ ] Update script to filter `<= 10` minutes (not 25)
- [ ] Add ADMIN_INCIDENTS exclusion
- [ ] Keep "Self-Initiated" exclusion (if column exists)
- [ ] Keep "Motor Vehicle Stop" exclusion
- [ ] Re-run script for November 2025
- [ ] Compare November 2025 output with backfill pattern
- [ ] Verify values are in expected range (similar to October 2025)

---

## Expected Results

After fixes, November 2025 should show:
- **Emergency:** ~2-4 minutes (similar to backfill months)
- **Routine:** ~1-2 minutes (similar to backfill months)
- **Urgent:** ~2-3 minutes (similar to backfill months)

Current November 2025 output (before fixes):
- Emergency: 9:25 (9.42 minutes) - **TOO HIGH**
- Routine: 4:02 (4.04 minutes) - **TOO HIGH**
- Urgent: 8:56 (8.94 minutes) - **TOO HIGH**

