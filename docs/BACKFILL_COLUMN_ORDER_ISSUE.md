# Backfill CSV Column Order Issue

**Date:** 2025-12-11  
**Issue:** Column order in exported backfill CSV doesn't match expected format

---

## Current CSV Column Order

**File:** `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Backfill\2025_10\vcs_time_report\2025_10_Monthly Accrual and Usage Summary.csv`

**Current Order:**
```
10-24, 11-24, 12-24, 01-25, 02-25, 03-25, 04-25, 05-25, 06-25, 07-25, 08-25, 09-25, Time_Category, 10-25
```

**Problem:** 
- Date columns come first
- `Time_Category` is in the middle (after 09-25, before 10-25)
- Doesn't match the visual display or script expectations

---

## Expected Format

**Based on Script Output (overtime_timeoff_13month_sworn_breakdown_v11.py):**

**Expected Order:**
```
Time Category, 10-24, 11-24, 12-24, 01-25, 02-25, 03-25, 04-25, 05-25, 06-25, 07-25, 08-25, 09-25, 10-25
```

**Why:**
1. Script resets index and makes `Time Category` the first column (line 176-177)
2. Date columns are sorted chronologically (line 172)
3. Power BI visual displays `Time Category` first
4. M code expects `Time Category` as first column

---

## Impact Assessment

### ✅ Script Compatibility

**Pandas can handle it:** The script uses `.set_index("Time_Category")` or column name access, so column position doesn't break functionality.

**However:**
- When script reads backfill for anchoring, it expects `Time Category` column name
- Script output format puts `Time Category` first
- Inconsistency may cause confusion

### ⚠️ Power BI Visual

**Visual Display:** Shows `Time Category` first, then date columns chronologically

**M Code Expectation:** 
- Expects `Time Category` column
- Removes it from date column list: `List.RemoveItems(Table.ColumnNames(T), {"Time Category"})`
- Works regardless of position, but first position is standard

### 📋 Best Practice

**Standard Format:** `Time Category` should be first column for:
1. Consistency with script output
2. Matching visual display
3. Easier manual inspection
4. Standard CSV format (key column first)

---

## Solution Options

### Option 1: Reorder Columns in Excel/Power BI (Recommended)

**Before exporting:**
1. In Power BI, ensure `Time Category` is the first column in the visual
2. Export visual data
3. Verify column order matches expected format

**Or manually reorder in Excel:**
1. Open CSV in Excel
2. Move `Time_Category` column to first position
3. Ensure date columns are in chronological order (10-24 through 10-25)
4. Save

### Option 2: Use Script to Reorder (Automated)

**Create a reorder script:**
```python
import pandas as pd
from pathlib import Path

csv_path = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Backfill\2025_10\vcs_time_report\2025_10_Monthly Accrual and Usage Summary.csv")

# Read CSV
df = pd.read_csv(csv_path)

# Get date columns (all columns except Time_Category)
date_cols = [c for c in df.columns if c != "Time_Category" and c != "Time Category"]

# Sort date columns chronologically
def parse_month(col):
    try:
        mm, yy = col.split('-')
        return (int(yy), int(mm))
    except:
        return (99, 99)  # Put invalid columns at end

date_cols_sorted = sorted(date_cols, key=parse_month)

# Reorder: Time Category first, then date columns
time_col = "Time_Category" if "Time_Category" in df.columns else "Time Category"
new_order = [time_col] + date_cols_sorted
df_reordered = df[new_order]

# Rename Time_Category to Time Category if needed
if "Time_Category" in df_reordered.columns:
    df_reordered = df_reordered.rename(columns={"Time_Category": "Time Category"})

# Save
df_reordered.to_csv(csv_path, index=False)
print(f"✅ Reordered columns: {', '.join(new_order)}")
```

### Option 3: Accept Current Format (If Working)

**If scripts and Power BI work correctly:**
- Current format is functional (pandas uses column names, not positions)
- Only affects readability and consistency
- Can be left as-is if no issues occur

---

## Verification

### Check Current Format
```powershell
$csv = Import-Csv "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Backfill\2025_10\vcs_time_report\2025_10_Monthly Accrual and Usage Summary.csv"
$csv[0].PSObject.Properties.Name
```

### Expected Output
```
Time Category
10-24
11-24
12-24
01-25
02-25
03-25
04-25
05-25
06-25
07-25
08-25
09-25
10-25
```

---

## Recommendation

**Priority: Medium**

**Action:** Reorder columns to match expected format for consistency:
1. ✅ Scripts will work either way (uses column names)
2. ✅ Better readability and consistency
3. ✅ Matches visual display
4. ✅ Matches script output format

**When to Fix:**
- Before next backfill export (if possible)
- Or create a one-time reorder script
- Or manually reorder in Excel if needed

---

**Status:** Functional but inconsistent - recommend fixing for best practices

