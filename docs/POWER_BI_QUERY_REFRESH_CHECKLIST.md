# Power BI Query Refresh Checklist

**Date:** 2025-12-10  
**Query:** `___ResponseTimeCalculator`  
**Report:** `25_11_Monthly_FINAL.pbix`

---

## ✅ Yes, the Query Needs to be Refreshed

### Why?
1. **New data generated** with corrected filtering (1,698 calls vs previous 58)
2. **File format updated** to match backfill structure exactly
3. **New values** may differ from previous calculations

---

## 📋 Steps Required Before Refresh

### Step 1: Run ETL Script (if not already done)
The script has been updated and tested. Output files:
- **Location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Response_Times\output\`
- **File:** `Average_Response_Times__Values_are_in_mmss.csv`
- **Format:** Matches backfill file structure (Response Type, MM-YY, First Response_Time_MMSS)

### Step 2: Copy File to Backfill Location
The M code expects the November 2025 file at:
```
C:\Dev\PowerBI_Date\Backfill\2025_12\response_time\2025_12_Average_Response_Times__Values_are_in_mmss.csv
```

**Action Required:**
```powershell
# Copy the newly generated file to the backfill location
Copy-Item `
  "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Response_Times\output\Average_Response_Times__Values_are_in_mmss.csv" `
  "C:\Dev\PowerBI_Date\Backfill\2025_12\response_time\2025_12_Average_Response_Times__Values_are_in_mmss.csv" `
  -Force
```

**OR** run the organize script (which should handle this):
```powershell
cd C:\Dev\PowerBI_Date
.\tools\organize_backfill_exports.ps1
```

### Step 3: Verify File Format Matches Backfill
The new file should have:
- ✅ Column: `Response Type` (not `Response_Type`)
- ✅ Column: `MM-YY` (with hyphen, not `MM_YY`)
- ✅ Column: `First Response_Time_MMSS` (not `Response_Time_MMSS`)
- ✅ Values: `Emergency,11-25,5:01` (matches backfill format)

### Step 4: Refresh Power BI Query
In Power BI Desktop:
1. Open `25_11_Monthly_FINAL.pbix`
2. Go to **Home** → **Refresh** (or press `F5`)
3. **OR** Right-click on `___ResponseTimeCalculator` query → **Refresh**
4. Wait for refresh to complete

---

## 📊 Expected Results After Refresh

### November 2025 Data (from new ETL output):
- **Emergency:** 5:01 (244 calls)
- **Routine:** 2:52 (950 calls)
- **Urgent:** 4:59 (504 calls)

### Comparison with Backfill:
These values should now be combined with backfill data (Nov 2024 - Oct 2025) to show:
- Complete 13-month rolling period
- Proper chronological sorting with Date_Sort_Key
- All DAX measures working correctly

---

## ⚠️ Important Notes

1. **File Location:** The M code loads from `C:\Dev\PowerBI_Date\Backfill\2025_12\response_time\`
   - Make sure the file is there BEFORE refreshing

2. **File Naming:** The file must be named exactly:
   - `2025_12_Average_Response_Times__Values_are_in_mmss.csv`
   - (Note the double underscore before `Values`)

3. **File Format:** Must match backfill structure:
   - Header: `Response Type,MM-YY,First Response_Time_MMSS`
   - Values: `Emergency,11-25,5:01` (format matches backfill)

4. **M Code Status:** The M code in `RESPONSE_TIMES_M_CODE_COMPLETE_FIX.txt` is already updated
   - It handles column renaming automatically
   - It combines backfill (Nov 2024 - Oct 2025) with November 2025 data
   - It calculates `Average_Response_Time` and `Date_Sort_Key`

---

## ✅ Verification After Refresh

After refreshing, verify:
- [ ] Query loads without errors
- [ ] All 13 months visible (Nov 2024 - Nov 2025)
- [ ] November 2025 shows new values (5:01, 2:52, 4:59)
- [ ] DAX measures (`Emergency_Avg_13M`, etc.) calculate correctly
- [ ] Date sorting works properly
- [ ] Visuals display correctly

---

## 🔄 Current File Status

**Generated File:**
- Location: `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Response_Times\output\Average_Response_Times__Values_are_in_mmss.csv`
- Format: ✅ Matches backfill structure
- Content: ✅ November 2025 data (3 rows)

**Target Location (where M code expects it):**
- `C:\Dev\PowerBI_Date\Backfill\2025_12\response_time\2025_12_Average_Response_Times__Values_are_in_mmss.csv`
- **Status:** ⚠️ Needs to be copied/updated

---

**Answer:** ✅ **YES, refresh the query AFTER copying the file to the backfill location.**

