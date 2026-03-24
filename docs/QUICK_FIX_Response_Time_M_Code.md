# Quick Fix Guide - Response Time M Code Update

**Fix Time**: 5 minutes  
**Difficulty**: Easy  
**Impact**: Fixes DataSource.NotFound error + duplicate column error  
**Version**: v2.1.1

---

## 🎯 Problems Fixed
1. Power BI error: `Could not find a part of the path 'C:\Dev\PowerBI_Data\Backfill\...'`
2. Power BI error: `The field 'YearMonth' already exists in the record`

## ✅ Solution
Update M code to dynamically load files from correct Backfill location with smart column handling.

---

## 🚀 Implementation (5 Steps)

### 1. Open Power BI Report
- Open your Response Times Power BI report
- Click "Transform Data" (Power Query Editor)

### 2. Find the Query
- In the Queries pane (left side)
- Find: `___ResponseTimeCalculator`
- Click on it

### 3. Backup Current Query
- Right-click `___ResponseTimeCalculator`
- Select "Duplicate"
- Rename duplicate to: `___ResponseTimeCalculator_BACKUP`

### 4. Update M Code
- Click on original `___ResponseTimeCalculator` query
- Click "Advanced Editor" button (top ribbon)
- **Delete all existing code**
- **Copy the updated code from**:
  ```
  C:\Users\carucci_r\OneDrive - City of Hackensack\06_Workspace_Management\m_code\response_time\___ResponseTimeCalculator.m
  ```
- **Paste** into Advanced Editor
- Click "Done"

### 5. Test & Apply
- Click "Refresh Preview" - should load without errors
- Click "Close & Apply" (top left)
- Wait for refresh to complete
- **Verify visuals display correctly**

---

## ✅ Verification

After implementation, check:

1. **No Errors**: Query loads without error messages
2. **Data Present**: Response time visuals show data
3. **Date Range**: All expected months are visible
4. **Values Correct**: Response times look reasonable (2-8 minutes typical)

---

## 🔧 Key Changes

**Issue 1 - Old Code** (hardcoded paths):
```m
File.Contents("C:\Dev\PowerBI_Data\Backfill\2025_10\response_time\...")
File.Contents("C:\Dev\PowerBI_Data\Backfill\2025_12\response_time\...")
```

**Issue 2 - Old Code** (always adds columns):
```m
WithYearMonth = Table.AddColumn(WithAvg, "YearMonth", ...)
// Error if column already exists!
```

**Fixed Code v2.1.1** (dynamic loading + conditional columns):
```m
BackfillBasePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Backfill"
AllFilesRaw = Folder.Files(BackfillBasePath)
// Automatically finds all monthly CSV files

WithYearMonth = if Table.HasColumns(WithAvg, "YearMonth")
                then WithAvg
                else Table.AddColumn(...)
// Only adds column if it doesn't exist
```

---

## 🎯 Benefits

✅ **Automatic**: Picks up new monthly files automatically  
✅ **Flexible**: Works with any number of months  
✅ **Correct Path**: Uses actual OneDrive location  
✅ **Future-Proof**: No manual updates needed  
✅ **Smart**: Handles CSVs with or without pre-calculated columns  
✅ **No Duplicates**: Checks before adding columns

---

## 🆘 If Something Goes Wrong

### Quick Rollback
1. Delete `___ResponseTimeCalculator` query
2. Rename `___ResponseTimeCalculator_BACKUP` → `___ResponseTimeCalculator`
3. Click "Close & Apply"

### Get Help
- Full documentation: `docs\RESPONSE_TIME_M_CODE_FIX_2026_02_09.md`
- Troubleshooting guide included in full documentation

---

## 📋 File Location

**Updated M Code**:
```
C:\Users\carucci_r\OneDrive - City of Hackensack\06_Workspace_Management\m_code\response_time\___ResponseTimeCalculator.m
```

**Full Documentation**:
```
C:\Users\carucci_r\OneDrive - City of Hackensack\06_Workspace_Management\docs\RESPONSE_TIME_M_CODE_FIX_2026_02_09.md
```

---

**Status**: ✅ Ready to implement  
**Tested**: Code verified (v2.1.1 fixes duplicate column error)  
**Time Required**: 5 minutes

---

*Last Updated: February 9, 2026 - v2.1.1*
