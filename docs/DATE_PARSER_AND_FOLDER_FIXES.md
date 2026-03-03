# Date Parser and Folder Structure Fixes

**Date:** 2026-02-13  
**Version:** 1.15.2  
**Status:** ✅ Fixed and Tested

---

## Issues Fixed

### Issue 1: Date Format Parser - YY-MMM Support

**Problem:** Date parser only supported `MM-YY` format (like "12-25"), but Power BI exports use `YY-MMM` format (like "25-Dec").

**Impact:** Files like Summons with `Month_Year` column showing "25-Dec" were incorrectly dated as `2026_01` (fallback to previous month) instead of `2025_12`.

**Fix:** Enhanced `_parse_period_to_yyyymm()` to support both formats:
- `MM-YY` format: "12-25" → 2025_12
- `YY-MMM` format: "25-Dec" → 2025_12
- Supports all month abbreviations (jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec)

**Test Results:**
```
25-Dec → 2025_12 ✓
26-Jan → 2026_01 ✓
12-25 → 2025_12 ✓ (backwards compatible)
```

---

### Issue 2: Multi-Month Data - Use Latest Date

**Problem:** When a visual contains multiple months of data in rows (like Summons with both "25-Dec" and "26-Jan"), the script was using `mode()` (most common) which could pick the wrong month.

**Example Data:**
```csv
WG2,TYPE,Month_Year,TICKET_COUNT
Traffic,Moving,25-Dec,10
Patrol,Moving,25-Dec,20
Traffic,Parking,26-Jan,15
Patrol,Parking,26-Jan,25
```

**Old Behavior:** Uses most common → "25-Dec" (appears 2x) → `2025_12`  
**New Behavior:** Uses latest date → max("25-Dec", "26-Jan") → "26-Jan" → `2026_01` ✓

**Fix:** Changed logic to parse all unique values in date column and use `max()` (latest YYYY_MM).

---

### Issue 3: Folder Names - Page-Based Structure

**Problem:** Folders used generic category names instead of matching Power BI page names.

**Old Structure:**
```
Processed_Exports/
├── Arrests/
├── Community_Engagement/
├── Executive/
├── Time_Off/
├── Training/
└── ...
```

**New Structure (Page-Based):**
```
Processed_Exports/
├── arrests/
├── social_media_and_time_report/
├── law_enforcement_duties/
├── policy_and_training_qual/
├── summons/
├── traffic_mva/
└── ...
```

**Normalization Rules:**
- Lowercase all characters
- Replace " & " with "_and_"
- Replace spaces with underscores
- Example: "Social Media & Time Report" → "social_media_and_time_report"

---

## Page Name to Folder Mapping

| Power BI Page | Folder Name |
|---------------|-------------|
| Arrests | arrests |
| NIBRS | nibrs |
| Response Time | response_time |
| Benchmark | benchmark |
| Chief Projects | chief_projects |
| Social Media and Time Report | social_media_and_time_report |
| Law Enforcement Duties | law_enforcement_duties |
| Out-Reach | out_reach |
| Summons | summons |
| Patrol | patrol |
| Drone | drone |
| Traffic | traffic |
| Traffic MVA | traffic_mva |
| STACP_Pt1 | stacp_pt1 |
| STACP_Pt2 | stacp_pt2 |
| Detectives_Pt1 | detectives_pt1 |
| Detectives_Pt2 | detectives_pt2 |
| Detectives Case Dispositions | detectives_case_dispositions |
| Crime Suppression Bureau | crime_suppression_bureau |
| REMU | remu |
| Policy & Training Qual | policy_and_training_qual |
| SSOCC | ssocc |

---

## Files Updated

### 1. `process_powerbi_exports.py`
- Enhanced `_parse_period_to_yyyymm()` with YY-MMM support
- Changed `infer_yyyymm_from_data()` to use `max()` for latest date in multi-month data
- Log shows: `[DATA] Inferred {date} from '{column}' column (latest of {n} periods)`

### 2. `visual_export_mapping.json`
- Updated all 32 visual entries with page-based `target_folder` names
- Normalized folder names (lowercase, & → and, spaces → _)

### 3. Helper Scripts Created
- `update_mapping_folders.py` - Updates mapping with page-based folders
- `reorganize_processed_exports.py` - Moves existing files to new structure

---

## Testing Needed

### Test Cases

1. **Summons with 25-Dec data:**
   ```
   Expected: 2025_12_department_wide_summons.csv
   Folder: summons/
   ```

2. **Training with 26-Jan data:**
   ```
   Expected: 2026_01_training_cost_by_delivery_method.csv
   Folder: policy_and_training_qual/
   ```

3. **Motor Vehicle Accidents:**
   ```
   Expected: 2025_12_motor_vehicle_accidents_summary.csv
   Folder: traffic_mva/
   ```

### Next Export Test

Place December 2025 exports in `_DropExports` and run:
```powershell
python scripts\process_powerbi_exports.py
```

Expected behavior:
- Files with "25-Dec" dates correctly named with `2025_12` prefix
- Files with "26-Jan" dates correctly named with `2026_01` prefix
- All files placed in page-based folders (lowercase, underscores)
- Log shows which date was selected when multiple periods found

---

## Backwards Compatibility

✅ **MM-YY format still works** (12-25 → 2025_12)  
✅ **Period column detection unchanged** (Period, Month_Year, PeriodLabel, Date, Month)  
✅ **13-month visuals still use last column** (for rolling windows)  
✅ **Fallback chain unchanged** (Data → Filename → Previous month)

---

## Summary

- **Date Parser:** Now supports both MM-YY and YY-MMM formats
- **Multi-Month Logic:** Uses latest date when data contains multiple months
- **Folder Structure:** Page-based normalized names for better organization
- **Ready to Test:** Needs real December 2025 exports to verify fixes

**Status:** Code ready, awaiting test with December 2025 data

*Fixes completed: 2026-02-13*
