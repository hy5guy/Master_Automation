# Benchmark M Code - Implementation Guide

**Date**: February 9, 2026  
**Status**: M code updated for simplified structure  
**Files Created**: 2 M code versions available

---

## Files Created

### 1. `_benchmark2026_02_09.m` (Full Version)
**Path**: `m_code\_benchmark2026_02_09.m`

**Features**:
- ✅ Error handling (won't break if files missing)
- ✅ Loads latest file from each folder automatically
- ✅ Supports both CSV and Excel files
- ✅ Adds Event Type column
- ✅ Adds Source File column (for tracking)
- ✅ Combines all three event types

**Use this if**: You want robust error handling and automatic latest file selection.

### 2. `_benchmark_simple.m` (Simple Version)
**Path**: `m_code\_benchmark_simple.m`

**Features**:
- ✅ Straightforward code (easier to understand)
- ✅ Loads latest file from each folder
- ✅ CSV files only
- ✅ Adds Event Type column
- ✅ Combines all three event types

**Use this if**: You prefer simpler, more readable code.

---

## How to Use in Power BI

### Step 1: Open Power BI Desktop

Open your Power BI report that uses Benchmark data.

### Step 2: Create New Query

**Option A: From File**
1. Home → Get Data → Blank Query
2. Home → Advanced Editor
3. Delete existing code
4. Copy content from `_benchmark2026_02_09.m` (or `_benchmark_simple.m`)
5. Paste into Advanced Editor
6. Click "Done"
7. Rename query to "Benchmark_Data" or similar

**Option B: Replace Existing Query**
1. Find your existing Benchmark query in Queries pane
2. Right-click → Advanced Editor
3. Replace existing code with new M code
4. Click "Done"

### Step 3: Verify Data Loads

1. Click "Close & Apply"
2. Check that data appears correctly
3. Verify all three event types are present
4. Check date ranges look correct

### Step 4: Update Relationships (if needed)

If this replaces an old query:
1. Go to Model view
2. Verify relationships still exist
3. Recreate if necessary

---

## New Data Source Structure

### What Changed

**Old Structure** (archived):
```
_Benchmark\
├── all_events_combined\
├── by_event_type\
├── by_time_period\
├── show_force\
│   └── complete_report\
│       ├── all_time\
│       └── full_year\2022-2028\
├── use_force\
│   └── complete_report\
│       ├── all_time\
│       └── full_year\2001,2020-2028\
└── vehicle_pursuit\
    └── complete_report\
        ├── all_time\
        └── full_year\2019,2021-2028\
```

**New Structure** (active):
```
Benchmark\
├── show_force\
│   ├── show-of-force-reports-01_01_2001-01_07_2026.csv ✅
│   └── show-of-force-reports-01_01_2025-12_31_2025.csv
├── use_force\
│   └── use-of-force-reports-01_01_2001-01_07_2026.csv ✅
└── vehicle_pursuit\
    └── vehicle-pursuit-reports-01_01_2001-01_07_2026.csv ✅
```

**Benefits**:
- ✅ 90% fewer folders (3 vs 90+)
- ✅ Simple 2-level structure
- ✅ Latest files include all historical data (2001-2026)
- ✅ Easy to navigate and maintain

---

## M Code Features Explained

### Automatic Latest File Selection

Both M code versions automatically select the most recently modified file in each folder:

```m
// Sorts by Date modified (most recent first)
SortedFiles = Table.Sort(Files, {{"Date modified", Order.Descending}}),

// Gets first (most recent) file
LatestFile = SortedFiles{0}[Content]
```

**Why this is useful**:
- When you export new Benchmark data next month, just save it to the same folder
- M code automatically picks up the newest file
- No need to update the query each month

### Event Type Column

The code adds an "Event Type" column to distinguish between:
- "Use of Force"
- "Show of Force"
- "Vehicle Pursuit"

This allows you to:
- Filter by event type in visuals
- Create separate pages for each type
- Analyze all events together or separately

### Error Handling (Full Version Only)

The full version (`_benchmark2026_02_09.m`) includes error handling:

```m
UseOfForce = try LoadLatestFile(...) 
             otherwise #table(type table [Message = text], {{"No data found"}})
```

**Benefits**:
- Query won't break if a folder is empty
- Shows clear error message
- Other event types still load

---

## Testing Checklist

After implementing the new M code:

- [ ] Power BI query refreshes without errors
- [ ] All three event types appear in data
- [ ] "Event Type" column shows correct values
- [ ] Row counts look reasonable (compare to old query)
- [ ] Date ranges are correct (should include January 2026)
- [ ] Existing visuals still work correctly
- [ ] Relationships still function
- [ ] Dashboard refreshes successfully

---

## Troubleshooting

### Issue: "File not found" error

**Solution**: Verify folder paths
```powershell
# Check folders exist
Test-Path "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark\use_force"
Test-Path "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark\show_force"
Test-Path "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark\vehicle_pursuit"
```

### Issue: "No files in folder" error

**Solution**: Check if CSV files exist in folders
```powershell
Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark\use_force" -Filter "*.csv"
```

### Issue: Column names don't match

**Solution**: 
1. Load one file manually to see actual column names
2. Update the TypedColumns section in M code (commented out by default)
3. Match your actual column names

### Issue: Excel files instead of CSV

**Simple version**: Won't work (CSV only)  
**Full version**: Should work automatically (detects .xlsx extension)

If using simple version with Excel files, change:
```m
// From:
Csv.Document(LatestFile, [Delimiter=",", Encoding=65001])

// To:
Excel.Workbook(LatestFile){0}[Data]
```

---

## Monthly Workflow Going Forward

### When New Benchmark Data Arrives

**Step 1**: Export from Benchmark system as usual

**Step 2**: Save files to appropriate folder:
```
Benchmark\use_force\YYYY_MM_DD_use_force.csv
Benchmark\show_force\YYYY_MM_DD_show_force.csv
Benchmark\vehicle_pursuit\YYYY_MM_DD_pursuit.csv
```

**Step 3**: Open Power BI and click "Refresh"

**That's it!** The M code automatically picks up the newest files.

---

## Backup and Rollback

### If You Need to Go Back

The old `_Benchmark` structure is archived:
```
05_EXPORTS\_Benchmark_ARCHIVE_2026_02_09\
```

**To rollback**:
1. Rename `_Benchmark_ARCHIVE_2026_02_09` back to `_Benchmark`
2. Restore old M code from Power BI version history
3. Refresh Power BI

**Archive can be deleted after**:
- New structure working for 1-2 months
- Verified all data is correct
- No issues found

---

## Summary

✅ **Phase 4 Complete**: Old `_Benchmark` archived  
✅ **Phase 5 Complete**: M code updated for new structure  
✅ **Files Created**: 2 M code versions (full & simple)  
✅ **Ready to Use**: Copy M code into Power BI

**Next Steps**:
1. Copy M code into Power BI Desktop
2. Test data refresh
3. Verify visuals work correctly
4. Use new simple structure going forward

---

**Last Updated**: February 9, 2026  
**Status**: Complete and ready for Power BI implementation
