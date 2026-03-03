# Benchmark M Code Error Fix - "Report Key Already Exists"

**Date**: February 9, 2026  
**Error**: `Expression.Error: The field 'Report Key' already exists in the record`  
**Status**: ✅ Fixed in v1.1

---

## What Happened

The original M code tried to add a `Report Key` column, but your CSV export **already includes** this column. Power Query doesn't allow duplicate column names, so it threw an error.

---

## Quick Fix (2 minutes)

### Option 1: Use Fixed Version v1.1 (Recommended)

**File**: `m_code\___Benchmark_FIXED_v1.1.m`

**This version**:
- ✅ Checks if `Report Key` exists before adding it
- ✅ Checks if `MonthStart` exists before adding it
- ✅ Works with any CSV structure (existing columns or not)

**Steps**:
1. Open Power BI → Transform Data
2. Find `___Benchmark` query
3. Right-click → Advanced Editor
4. **Delete all existing code**
5. **Copy entire contents** from `m_code\___Benchmark_FIXED_v1.1.m`
6. **Paste** into Advanced Editor
7. Click "Done"
8. Click "Close & Apply"

### Option 2: Quick Edit of Original File

**If you want to keep using the original file**, I've already updated it:

**File**: `m_code\___Benchmark_FIXED_2026_02_09.m` (updated)

The fix is on **lines 72-80**:
```m
// Add Report Key column ONLY if it doesn't already exist
AddReportKey = if List.Contains(Table.ColumnNames(AddMonthStart), "Report Key")
    then AddMonthStart  // Column already exists, skip this step
    else Table.AddColumn(AddMonthStart, "Report Key", each [Report Number], type text),
```

**Steps**: Same as Option 1, but use the updated `___Benchmark_FIXED_2026_02_09.m` file.

---

## Why This Happened

### Your CSV Structure

Your Benchmark CSV exports already include:
- ✅ `Report Key` column (unique identifier)
- ✅ `Incident Date` column
- ✅ Probably other columns like `Report Number`, `EventType`, etc.

### Original M Code Assumption

The original M code assumed:
- ❌ CSV has `Report Number` but NOT `Report Key`
- ❌ Needed to create `Report Key` by copying `Report Number`

### The Conflict

```
CSV has: Report Key (already exists)
M Code tries to add: Report Key (duplicate!)
Result: ERROR ❌
```

---

## What the Fix Does

### Check Before Adding

```m
// Original (caused error):
AddReportKey = Table.AddColumn(AddMonthStart, "Report Key", each [Report Number], type text)

// Fixed (checks first):
AddReportKey = if List.Contains(Table.ColumnNames(AddMonthStart), "Report Key")
    then AddMonthStart  // Already exists, skip
    else Table.AddColumn(AddMonthStart, "Report Key", each [Report Number], type text)
```

### Logic Flow

```
1. Check: Does "Report Key" column exist?
   ├─ YES → Skip adding, use existing column ✅
   └─ NO  → Add new column from Report Number ✅

2. Result: No duplicate columns, no errors!
```

---

## Verification

### After Applying Fix

1. **Preview should show data** (no errors)
2. **Column list should include**:
   - `Report Key` ✅ (from CSV or created)
   - `MonthStart` ✅ (created by M code)
   - `EventType` ✅ (created by M code)
   - `Incident Date` ✅ (from CSV)
   - `Source File` ✅ (created by M code)
   - Plus all other columns from your CSV

3. **No duplicate columns** ✅

### Test Query

Create a test measure in Power BI:
```dax
_TEST_ReportKey = 
VAR RowCount = COUNTROWS(___Benchmark)
VAR UniqueKeys = DISTINCTCOUNT(___Benchmark[Report Key])
RETURN
    "Rows: " & RowCount & " | Unique Keys: " & UniqueKeys
```

Should show something like: **"Rows: 245 | Unique Keys: 245"**

---

## Other Columns That Might Already Exist

Your CSV might also include:
- `MonthStart` - v1.1 checks for this too ✅
- `EventType` - M code adds this regardless (always needed)
- `# of Officers Involved` - No conflict
- `# of Subjects` - No conflict

**v1.1 handles both `Report Key` and `MonthStart`** automatically.

---

## Version Comparison

| Version | File | Report Key Check | MonthStart Check | Recommendation |
|---------|------|-----------------|------------------|----------------|
| v1.0 | `___Benchmark_FIXED_2026_02_09.m` | ✅ Yes (updated) | ❌ No | Use if MonthStart not in CSV |
| v1.1 | `___Benchmark_FIXED_v1.1.m` | ✅ Yes | ✅ Yes | ⭐ **Use this** (most robust) |

---

## Update Documentation References

If following the implementation guides, use **v1.1** instead of the original file:

**Update these references**:
- `BENCHMARK_IMPLEMENTATION_CHECKLIST_2026_02_09.md` → Use v1.1
- `BENCHMARK_QUICK_FIX_GUIDE_2026_02_09.md` → Use v1.1
- Any other guides referencing `___Benchmark_FIXED_2026_02_09.m`

---

## Summary

**Problem**: CSV already has `Report Key` column  
**Error**: Duplicate column name  
**Solution**: Check if column exists before adding  
**Fixed File**: `m_code\___Benchmark_FIXED_v1.1.m` ✅  
**Time to Fix**: 2 minutes  

---

**Next Steps**:
1. ✅ Replace M code with v1.1
2. ✅ Verify preview shows data
3. ✅ Continue with implementation checklist
4. ✅ All other steps remain the same

---

**Last Updated**: February 9, 2026  
**Fix Version**: v1.1  
**Status**: ✅ Resolved
