# Response Time v2.8.2 - Single Source Fix

**Date**: 2026-02-09  
**Issue**: Visual 1 showing incorrect values (mixed old backfill + new fresh calculator data)  
**Solution**: Update M code to load ONLY from Fresh Calculator output  

---

## Problem Identified

After implementing Fresh Calculator v3.0.0, the Power BI visuals were still showing incorrect values:

### October 2025 Comparison:
| Type | Fresh Calculator | Visual 1 Export | Issue |
|------|-----------------|-----------------|-------|
| Emergency | **02:07** | 02:59 | ❌ Wrong (+0:52) |
| Urgent | **01:12** | 02:52 | ❌ Wrong (+1:40) |
| Routine | **00:24** | 01:18 | ❌ Wrong (+0:54) |

### Root Cause:
The M code was loading files from **multiple locations simultaneously**:
1. ✅ `_DropExports` - Fresh Calculator (correct data)
2. ❌ `data\visual_export` - Old manual exports (wrong data)
3. ❌ `outputs\visual_exports` - Old manual exports (wrong data)
4. ❌ `Backfill` - Legacy backfill (wrong data)

When combined, Power BI mixed fresh + old data, resulting in incorrect averages.

---

## Solution: v2.8.2 Changes

### 1. Removed Multi-Path Fallback
**Before (v2.8.1):**
```powerquery
PossiblePaths = {
    "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\_DropExports",
    "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\data\visual_export",
    "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\outputs\visual_exports",
    "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Backfill"
},
FindValidPath = List.First(...),
BackfillBasePath = FindValidPath,
```

**After (v2.8.2):**
```powerquery
// Use ONLY Fresh Calculator output from _DropExports
BackfillBasePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\_DropExports",
```

### 2. Updated File Filter
**Before:**
```powerquery
// Loaded from response_time subdirs OR _DropExports OR visual_export
each (Text.Contains([Folder Path], "response_time") or 
      Text.Contains([Folder Path], "_DropExports") or
      Text.Contains([Folder Path], "visual_export")) and
     (Text.Contains([Name], "Average") or 
      Text.Contains([Name], "Response Time"))
```

**After:**
```powerquery
// Load ONLY files matching Fresh Calculator naming pattern
each Text.EndsWith(Text.Lower([Name]), ".csv") and
     Text.Contains([Name], "Average_Response_Times")
```

---

## Implementation Steps

### Step 1: Update Power BI M Code

1. Open Power BI Desktop
2. Go to **Home** → **Transform data**
3. Find the `___ResponseTimeCalculator` query
4. Click **Advanced Editor**
5. Replace the entire query with the updated M code from:
   ```
   M:\Master_Automation\m_code\___ResponseTimeCalculator.m
   ```
6. Click **Done**
7. Click **Close & Apply**

### Step 2: Refresh Data

1. Click **Refresh** in Power BI
2. Wait for data to load (should load 13 files: 2025-01 through 2026-01)
3. Check that all visuals update

### Step 3: Verify Results

Check **Visual 1** (Average Response Times) for October 2025:
- ✅ Emergency: Should be ~**02:07** (raw) or ~**02:49** (with 13M rolling avg)
- ✅ Urgent: Should be ~**01:12** (raw) or ~**02:52** (with 13M rolling avg)
- ✅ Routine: Should be ~**00:24** (raw) or ~**02:11** (with 13M rolling avg)

Check **Visual 2** (Response Times by Priority):
- Should show 13-month rolling averages calculated by DAX measures
- Emergency_Avg_13M, Urgent_Avg_13M, Routine_Avg_13M should work correctly

---

## Expected Behavior After Fix

### Data Source:
- **Single Source**: Only `_DropExports` folder
- **13 Files**: One per month (2025-01 through 2026-01)
- **Each File**: 3 rows (Emergency, Urgent, Routine)
- **Format**: `YYYY_MM_Average_Response_Times__Values_are_in_mmss.csv`

### Visual 1 Values:
The raw monthly values from Fresh Calculator, displayed as MM:SS format.

### Visual 2 Values:
The 13-month rolling average calculated by DAX measures:
- `Emergency_Avg_13M`
- `Urgent_Avg_13M`
- `Routine_Avg_13M`

These measures use:
- `Summary_Type` = "Response_Type"
- `Category` = Emergency/Urgent/Routine
- `Average_Response_Time` (decimal minutes)
- `Date` (first of month)

---

## Verification Checklist

- [ ] M code updated to v2.8.2
- [ ] Power BI refreshed successfully
- [ ] Visual 1 shows correct October 2025 values
- [ ] Visual 2 shows correct 13-month rolling averages
- [ ] No error messages in Power Query
- [ ] All 13 months (Jan 2025 - Jan 2026) have data
- [ ] DAX measures calculate correctly

---

## Troubleshooting

### Issue: "DataSource.NotFound" error
**Solution**: Verify the `_DropExports` folder exists and contains CSV files:
```
C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\_DropExports\
  2025_01_Average_Response_Times__Values_are_in_mmss.csv
  2025_02_Average_Response_Times__Values_are_in_mmss.csv
  ...
  2026_01_Average_Response_Times__Values_are_in_mmss.csv
```

### Issue: Still seeing old values
**Solution**: 
1. Clear Power BI cache: **File** → **Options** → **Data Load** → **Clear Cache**
2. Close and reopen Power BI Desktop
3. Refresh data again

### Issue: Visual 1 shows wrong format
**Solution**: Ensure visual is using `First Response_Time_MMSS` field (not `Average_Response_Time`)

---

## Files Modified

- `m_code\___ResponseTimeCalculator.m` - Updated to v2.8.2 (single source)

## Files Created

- `docs\RESPONSE_TIME_v2.8.2_SINGLE_SOURCE_FIX.md` - This implementation guide

---

## Next Steps

1. Implement v2.8.2 M code in Power BI
2. Refresh and verify visuals
3. If values are correct, export new visuals for February 2026 report
4. Consider archiving old backfill/visual_export data to avoid confusion

---

**Status**: Ready for implementation  
**Expected Time**: 5 minutes (M code update + refresh)  
**Risk**: Low (can rollback by restoring v2.8.1 M code)
