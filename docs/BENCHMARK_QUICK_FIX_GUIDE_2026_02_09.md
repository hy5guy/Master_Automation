# Benchmark Power BI - Quick Implementation Guide

**Date**: February 9, 2026  
**Time Required**: 15-20 minutes  
**Files**: 3 M code queries + DAX measures

---

## What's Wrong

Your Benchmark dashboard is showing errors because:
1. ❌ Table/column names don't match what DAX measures expect
2. ❌ Missing dimension tables (`___DimMonth`, `___DimEventType`)
3. ❌ Missing required columns (`MonthStart`, `Report Key`)

---

## What You Need to Do

### Step 1: Replace Benchmark Data Query (5 minutes)

**Action**: Update your main Benchmark data query

1. Open Power BI Desktop
2. Home → Transform Data
3. Find your Benchmark query (might be named `Benchmark`, `___Benchmark`, or similar)
4. Right-click → Advanced Editor
5. **Delete all existing code**
6. **Copy code from**: `m_code\___Benchmark_FIXED_2026_02_09.m`
7. **Paste into Advanced Editor**
8. Click "Done"
9. **Rename query to**: `___Benchmark` (exactly 3 underscores)

**Important**: Before clicking Done, check the preview:
- Do you see columns like `Incident Date`, `Report Number`, `EventType`?
- If preview shows errors, your CSV column names might be different (see Troubleshooting)

### Step 2: Create Month Dimension Table (3 minutes)

**Action**: Create `___DimMonth` table

1. Home → Get Data → Blank Query
2. Home → Advanced Editor
3. **Copy code from**: `m_code\___DimMonth.m`
4. **Paste into Advanced Editor**
5. Click "Done"
6. **Rename query to**: `___DimMonth` (exactly 3 underscores)
7. Verify preview shows 13 rows (Nov 2024 - Nov 2025)

### Step 3: Create Event Type Dimension Table (2 minutes)

**Action**: Create `___DimEventType` table

1. Home → Get Data → Blank Query
2. Home → Advanced Editor
3. **Copy code from**: `m_code\___DimEventType.m`
4. **Paste into Advanced Editor**
5. Click "Done"
6. **Rename query to**: `___DimEventType` (exactly 3 underscores)
7. Verify preview shows 3 rows (Show of Force, Use of Force, Vehicle Pursuit)

### Step 4: Create Relationships (3 minutes)

**Action**: Link tables together

1. Click "Close & Apply" (bottom left)
2. Go to **Model View** (left sidebar)
3. **Create Relationship 1**:
   - Drag `___Benchmark[MonthStart]` to `___DimMonth[MonthStart]`
   - Cardinality: Many-to-One (*)
   - Cross filter direction: Single
   - Click "OK"
4. **Create Relationship 2**:
   - Drag `___Benchmark[EventType]` to `___DimEventType[EventType]`
   - Cardinality: Many-to-One (*)
   - Cross filter direction: Single
   - Click "OK"

### Step 5: Fix Measures (5 minutes)

**Action**: Update DAX measures

1. Go to **Report View**
2. Find the measure `Total Incidents Rolling 13`
3. Click the measure in Fields pane
4. Check formula bar for errors (red underlines)

**If measure doesn't exist or has errors**:
1. Select `___Benchmark` table
2. Home → New Measure
3. **Copy DAX from**: `scripts\_testing\benchmark_r13.dax`
4. Find `Total Incidents Rolling 13` measure (line 322)
5. Paste into formula bar
6. Press Enter
7. Repeat for `Avg Incidents Per Month` (line 1)

### Step 6: Test (2 minutes)

**Action**: Verify everything works

1. Create a **Card visual**
2. Add measure: `Total Incidents Rolling 13`
3. Should show a number (e.g., 245)
4. Create a **Table visual**
5. Add columns:
   - `___DimMonth[MonthLabel]`
   - `___DimEventType[EventType]`
   - Measure: `Total Incidents Rolling 13`
6. Should show 13 months × 3 event types

**If you see errors**, go to Troubleshooting section below.

---

## Troubleshooting

### Error: "Column 'Incident Date' not found"

**Cause**: Your CSV uses a different column name

**Fix**: 
1. Open one of your Benchmark CSV files
2. Check the actual column names (e.g., `Date`, `IncidentDate`, `Incident_Date`)
3. Edit M code line 68:
   ```m
   // Change this:
   each Date.StartOfMonth([Incident Date]), type date)
   
   // To match your CSV (example):
   each Date.StartOfMonth([Date]), type date)
   ```

### Error: "Column 'Report Number' not found"

**Cause**: Your CSV uses a different unique ID column name

**Fix**:
1. Check your CSV for the unique identifier column (might be `IncidentNumber`, `ReportID`, etc.)
2. Edit M code line 73:
   ```m
   // Change this:
   each [Report Number], type text),
   
   // To match your CSV (example):
   each [IncidentNumber], type text),
   ```

### Error: "No files found in folder"

**Cause**: Folder path is wrong or folder is empty

**Fix**:
1. Open File Explorer
2. Navigate to: `C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark\`
3. Verify folders exist: `use_force\`, `show_force\`, `vehicle_pursuit\`
4. Verify each folder contains at least one CSV file
5. If folders are in a different location, edit M code line 18:
   ```m
   BenchmarkBasePath = "YOUR_ACTUAL_PATH_HERE\",
   ```

### Error: Measure shows "Error" instead of number

**Cause**: Column names in DAX don't match your table

**Fix**:
1. Go to Data View
2. Check column names in `___Benchmark` table
3. Update DAX measure to match (example):
   ```dax
   // If your table has "IncidentNumber" instead of "Report Key"
   DISTINCTCOUNT(___Benchmark[IncidentNumber])
   ```

### Visual Still Shows "Can't display this visual"

**Cause**: Visual filters reference old columns

**Fix**:
1. Click the broken visual
2. Visualizations pane → Filters
3. Remove any filters with yellow warning icons
4. Re-add filters using correct column names
5. OR delete visual and recreate from scratch

---

## Column Name Reference

**M Code adds these columns** (automatically):
- `EventType` - Text: "Use of Force", "Show of Force", "Vehicle Pursuit"
- `MonthStart` - Date: First day of month (e.g., 2024-11-01)
- `Report Key` - Text: Unique identifier (copied from Report Number)
- `Source File` - Text: CSV filename for tracking

**Your CSV must have** (or you need to map them):
- `Incident Date` - Date column (any name is fine, just update M code)
- `Report Number` - Unique ID (any name is fine, just update M code)

**DAX measures expect** (from benchmark_r13.dax):
- `___Benchmark[Report Key]` - For counting incidents
- `___Benchmark[MonthStart]` - For date filtering
- `___Benchmark[EventType]` - For event type filtering
- `___Benchmark[Incident Date]` - For some calculations
- `___Benchmark[# of Officers Involved]` - Optional (some measures use this)
- `___Benchmark[# of Subjects]` - Optional (some measures use this)

---

## Common CSV Column Name Mappings

If your CSV has different column names, update the M code type conversions (line 76-86):

| Your CSV Column | M Code Should Reference |
|----------------|------------------------|
| `Date` | Change `[Incident Date]` to `[Date]` |
| `IncidentDate` | Change `[Incident Date]` to `[IncidentDate]` |
| `ReportNumber` | Change `[Report Number]` to `[ReportNumber]` |
| `IncidentID` | Change `[Report Number]` to `[IncidentID]` |
| `OfficersInvolved` | Change `[# of Officers Involved]` to `[OfficersInvolved]` |
| `SubjectCount` | Change `[# of Subjects]` to `[SubjectCount]` |

---

## What Success Looks Like

After following all steps:
- ✅ No errors in Transform Data window
- ✅ `___Benchmark` table loads data (100+ rows expected)
- ✅ `___DimMonth` table shows 13 rows
- ✅ `___DimEventType` table shows 3 rows
- ✅ Two relationships visible in Model View
- ✅ `Total Incidents Rolling 13` measure shows a number
- ✅ Original Benchmark visual displays correctly
- ✅ No "can't display this visual" errors

---

## Quick Check: Am I Done?

Create this test measure to verify everything:

```dax
_TEST_Benchmark = 
VAR TableExists = NOT(ISBLANK(COUNTROWS(___Benchmark)))
VAR MonthExists = NOT(ISBLANK(COUNTROWS(___DimMonth)))
VAR EventExists = NOT(ISBLANK(COUNTROWS(___DimEventType)))
VAR HasData = COUNTROWS(___Benchmark) > 0
RETURN
    IF(TableExists && MonthExists && EventExists && HasData, 
       "✅ ALL GOOD - " & COUNTROWS(___Benchmark) & " rows loaded", 
       "❌ SETUP INCOMPLETE - Check tables")
```

Add to a card visual. Should show: **✅ ALL GOOD - XXX rows loaded**

---

## Files Reference

**M Code Files** (copy into Power BI Advanced Editor):
- `m_code\___Benchmark_FIXED_2026_02_09.m` - Main data query
- `m_code\___DimMonth.m` - Month dimension
- `m_code\___DimEventType.m` - Event type dimension

**DAX Measures** (copy into Power BI Measure editor):
- `scripts\_testing\benchmark_r13.dax` - All measures (30+ measures)

**Documentation**:
- `docs\BENCHMARK_POWER_BI_FIX_2026_02_09.md` - Detailed diagnostic guide

---

## Still Having Issues?

Check the comprehensive diagnostic guide:
- File: `docs\BENCHMARK_POWER_BI_FIX_2026_02_09.md`
- Includes: Detailed troubleshooting, column mapping, testing scripts

---

**Last Updated**: February 9, 2026  
**Estimated Time**: 15-20 minutes  
**Difficulty**: Moderate (copy/paste + some verification)
