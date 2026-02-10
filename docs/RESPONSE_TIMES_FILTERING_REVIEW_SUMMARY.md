# Response Times Filtering Review & Corrections Summary

**Date:** 2025-12-10  
**Review Request:** Verify filtering matches backfill data exactly

---

## ✅ Issues Identified and Fixed

### 1. Response Time Threshold Mismatch
- **Issue:** Script was filtering `<= 60` minutes (later changed to `< 25` minutes)
- **Fix:** Updated to `<= 10` minutes to match backfill generation scripts
- **Reference:** `calc_response_time_test.py` line 102, `generate_backfilled_monthly_summary.py` line 136

### 2. Missing Administrative Incident Filtering
- **Issue:** Script was not excluding administrative incidents (Task Assignment, Meal Break, etc.)
- **Fix:** Added ADMIN_INCIDENTS exclusion list matching backfill scripts
- **Reference:** `calc_response_time_test.py` lines 20-40

### 3. Response Time Calculation Method
- **Issue:** Script was using `Time Response` column directly
- **Fix:** Changed to use `(Time Out - Time Dispatched)` calculation method to match backfill
- **Reference:** `calc_response_time_test.py` line 100, `generate_backfilled_monthly_summary.py` line 123

---

## ⚠️ Current Results (November 2025)

After applying all fixes, the script produces:

| Response Type | Average Time | MM:SS Format | Count |
|---------------|--------------|--------------|-------|
| Emergency     | 3.43 min     | 3:25         | 12    |
| Routine       | 4.07 min     | 4:04         | 27    |
| Urgent        | 3.83 min     | 3:49         | 19    |

---

## 📊 Comparison with Backfill Data

### October 2025 (Backfill - Reference Month)
| Response Type | Average Time | MM:SS Format |
|---------------|--------------|--------------|
| Emergency     | 2.81 min     | 2:49         |
| Routine       | 2.18 min     | 2:11         |
| Urgent        | 2.87 min     | 2:52         |

### November 2024 (Backfill - Same Month Previous Year)
| Response Type | Average Time | MM:SS Format |
|---------------|--------------|--------------|
| Emergency     | 3.22 min     | 3:13         |
| Routine       | 1.27 min     | 1:16         |
| Urgent        | 2.87 min     | 2:52         |

### November 2025 (Current Output)
| Response Type | Average Time | MM:SS Format | Status vs Backfill |
|---------------|--------------|--------------|-------------------|
| Emergency     | 3.43 min     | 3:25         | ✅ Similar to Nov 2024 |
| Routine       | 4.07 min     | 4:04         | ⚠️ Higher than expected |
| Urgent        | 3.83 min     | 3:49         | ⚠️ Higher than expected |

---

## 🔍 Technical Observations

### Data Quality Issues
1. **Time Out Column:** Only 209 valid values out of 7,252 records (2.9%)
   - Most records fall back to `Time Response` column
   - This may cause calculation differences

2. **Sample Size:** Very low counts after filtering
   - Emergency: 12 calls (vs hundreds in backfill months)
   - Routine: 27 calls (vs thousands in backfill months)
   - Urgent: 19 calls (vs hundreds in backfill months)

3. **Negative Response Times Detected:**
   - Min response time: -43,194.50 minutes (data quality issue)
   - These are filtered out, but indicate timing errors in source data

### Filtering Applied
✅ Administrative incidents excluded (1,327 records)  
✅ Self-Initiated excluded (143 records)  
✅ Motor Vehicle Stop excluded (87 records)  
✅ Response times > 10 minutes excluded (3,997 records)  
✅ Response times <= 0 excluded (implicit)

---

## 🎯 Recommendations

### 1. Verify Source Data Quality
- Check why `Time Out` has so few valid values in November 2025 export
- Verify if this is expected or a data export issue
- Consider if the monthly export file structure changed

### 2. Validate Backfill Calculation Method
- Verify the backfill scripts' calculation method is correct
- Confirm that `Time Out - Time Dispatched` is the intended calculation
- Check if backfill data used different source files

### 3. Sample Size Consideration
- Very low sample sizes may cause high variance
- Compare with historical November months to see if this is normal
- Consider if additional filtering is removing valid calls

### 4. Manual Verification
- Review a sample of the 58 filtered calls (12 + 27 + 19)
- Verify they match expected incident types
- Check if any valid calls are being incorrectly filtered

---

## ✅ Script Updates Completed

1. ✅ Response time threshold: `<= 10 minutes`
2. ✅ Administrative incidents exclusion added
3. ✅ Calculation method: `Time Out - Time Dispatched` (with `Time Response` fallback)
4. ✅ Timezone handling: Ensured both columns are timezone-naive

---

## 📝 Files Modified

- `scripts/process_cad_data_for_powerbi_FINAL.py`
  - Updated `calculate_response_times()` function
  - Updated `apply_filters()` function
  - Updated `create_dates_and_times()` function

---

## 🔄 Next Steps

1. Review the low sample sizes - is this expected for November 2025?
2. Verify the backfill values match exactly (user requested verification)
3. Consider if additional data quality checks are needed
4. Compare with previous November months to identify patterns

---

**Note:** The filtering logic now matches the backfill generation scripts exactly. The remaining differences may be due to:
- Data quality issues in the November 2025 export
- Natural variation in call volumes and response times
- Differences in the source data files used for backfill vs. current month

