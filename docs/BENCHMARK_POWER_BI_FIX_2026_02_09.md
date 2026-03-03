# Benchmark Power BI Error Fix Guide

**Date**: February 9, 2026  
**Issue**: Benchmark visual shows errors - "can't display this visual" + measure errors  
**Status**: Diagnostic guide created

---

## Error Summary

### Error 1: Visual Display Error
**Message**: "Can't display this visual"  
**Reason**: "This visual contains one or more filters with deleted columns, type mismatches, or other breaking modeling changes."

### Error 2: Measure Error
**Message**: "Fields that need to be fixed"  
**Details**: `(__Benchmark) Avg Incidents Per Month: This expression refers to a Measure object named '__Benchmark[Total Incidents Rolling 13]', which has an error.`

---

## Root Cause

The issue is likely one or more of these:

1. **Table Name Mismatch**
   - DAX measures expect: `___Benchmark` (3 underscores)
   - Your table might be named: `Benchmark` or something else

2. **Missing Dimension Tables**
   - DAX expects: `___DimMonth` table
   - DAX expects: `___DimEventType` table

3. **Column Name Mismatches**
   - DAX expects specific column names that may not exist in your data

---

## Diagnostic Steps

### Step 1: Check Table Names

**Action**: Open Power BI → Model View → Check table names

**Expected Tables**:
- `___Benchmark` (main data table - 3 underscores)
- `___DimMonth` (month dimension table)
- `___DimEventType` (event type dimension table)

**If names are different**, you have two options:
1. **Option A**: Rename tables to match DAX expectations
2. **Option B**: Update all DAX measures to match your table names

### Step 2: Check Column Names in ___Benchmark Table

**Required Columns** (DAX expects these):
- `Report Key` or `Report Number` (unique incident identifier)
- `MonthStart` (date - first day of month)
- `EventType` (text - "Use of Force", "Show of Force", "Vehicle Pursuit")
- `Incident Date` (full date of incident)
- `# of Officers Involved` (number)
- `# of Subjects` (number)

**Action**: Open Power BI → Data View → Check column names in your Benchmark table

### Step 3: Check Dimension Tables

#### ___DimMonth Table

**Required Columns**:
- `MonthStart` (date - first day of month, e.g., 2024-11-01)
- `MonthLabel` (text - "MM-yy" format, e.g., "11-24")
- `MonthSort` (number - YYYYMM format, e.g., 202411)

**M Code** (if table doesn't exist):
```m
let
    StartDate = #date(2024, 11, 1),
    MonthCount = 13,
    
    // Generate list of first day of each month
    MonthStarts = List.Generate(
        () => StartDate,
        each _ <= Date.AddMonths(StartDate, MonthCount - 1),
        each Date.AddMonths(_, 1)
    ),
    
    // Convert to table
    ToTable = Table.FromList(MonthStarts, Splitter.SplitByNothing(), {"MonthStart"}),
    
    // Ensure date type
    TypedDate = Table.TransformColumnTypes(ToTable, {{"MonthStart", type date}}),
    
    // Add helper columns
    AddLabel = Table.AddColumn(TypedDate, "MonthLabel", 
        each Date.ToText([MonthStart], "MM-yy"), type text),
    
    AddSort = Table.AddColumn(AddLabel, "MonthSort", 
        each Date.Year([MonthStart]) * 100 + Date.Month([MonthStart]), Int64.Type)
in
    AddSort
```

#### ___DimEventType Table

**Required Columns**:
- `EventType` (text)

**M Code** (if table doesn't exist):
```m
let
    Source = #table(
        {"EventType"},
        {
            {"Show of Force"},
            {"Use of Force"},
            {"Vehicle Pursuit"}
        }
    ),
    Typed = Table.TransformColumnTypes(Source, {{"EventType", type text}})
in
    Typed
```

---

## Solution 1: Quick Fix (Rename Tables)

**If your tables have different names**, rename them to match DAX expectations:

### Step-by-Step:

1. **Open Power BI Desktop**
2. **Go to Data View**
3. **Find your Benchmark data table**
4. **Right-click table name → Rename**
5. **Rename to**: `___Benchmark` (exactly 3 underscores)
6. **Repeat for dimension tables**:
   - Month table → `___DimMonth`
   - Event Type table → `___DimEventType`

### Create Missing Tables:

**If `___DimMonth` doesn't exist**:
1. Home → Get Data → Blank Query
2. Home → Advanced Editor
3. Paste the `___DimMonth` M code (from Step 3 above)
4. Click "Done"
5. Rename query to `___DimMonth`

**If `___DimEventType` doesn't exist**:
1. Home → Get Data → Blank Query
2. Home → Advanced Editor
3. Paste the `___DimEventType` M code (from Step 3 above)
4. Click "Done"
5. Rename query to `___DimEventType`

---

## Solution 2: Fix Column Names

**If columns have different names**, check what your M code created:

### Check Your M Code Output:

Your M code (from your message) adds these columns:
- `Event Type` (from M code line 48)
- `Source File` (from M code line 51)

**But DAX expects**:
- `EventType` (no space)

### Fix: Update M Code

**Option A: Change M Code** (add column rename step):

Add this step to your M code before the `Result` line:

```m
// Rename columns to match DAX expectations
RenamedColumns = Table.RenameColumns(CombinedBenchmark, {
    {"Event Type", "EventType"}
}),

// Return the renamed data
Result = RenamedColumns
```

**Option B: Add Calculated Column in Power BI**:

1. Go to Data View
2. Select `___Benchmark` table
3. Click "New Column"
4. Enter: `EventType = '___Benchmark'[Event Type]`
5. Press Enter

---

## Solution 3: Fix Measure References

**If measures reference wrong columns**, update them:

### Critical Measures to Check:

#### 1. Total Incidents Rolling 13

**Current (from DAX file)**:
```dax
Total Incidents Rolling 13 = 
VAR LastMonth = EOMONTH(TODAY(), -1)
VAR FirstMonth = EDATE(LastMonth, -12)
RETURN
CALCULATE(
    DISTINCTCOUNT(___Benchmark[Report Key]),
    ___Benchmark[MonthStart] >= FirstMonth,
    ___Benchmark[MonthStart] <= LastMonth
)
```

**Check**:
- Does `___Benchmark[Report Key]` column exist?
- Does `___Benchmark[MonthStart]` column exist?

**If not**, update to use your actual column names.

#### 2. Avg Incidents Per Month

**Current (from DAX file)**:
```dax
Avg Incidents Per Month = 
VAR LastMonth = EOMONTH(TODAY(), -1)
VAR FirstMonth = EDATE(LastMonth, -12)
VAR Total = [Total Incidents Rolling 13]
RETURN
    DIVIDE(Total, 13, 0)
```

**This measure depends on**: `[Total Incidents Rolling 13]`

**Fix order**: Fix `Total Incidents Rolling 13` first!

---

## Solution 4: Create Missing Columns

**If your data doesn't have required columns**, add them:

### Add MonthStart Column (if missing)

**Option 1: In M Code** (recommended):

Add this step after combining Benchmark data:

```m
// Add MonthStart column (first day of incident month)
AddMonthStart = Table.AddColumn(CombinedBenchmark, "MonthStart", 
    each Date.StartOfMonth([Incident Date]), type date),
```

**Option 2: In Power BI as Calculated Column**:

1. Go to Data View
2. Select `___Benchmark` table
3. Click "New Column"
4. Enter: `MonthStart = DATE(YEAR([Incident Date]), MONTH([Incident Date]), 1)`
5. Press Enter

### Add Report Key Column (if missing)

**If your data has `Report Number` but DAX expects `Report Key`**:

**Option A: Rename column** (in M code or Power BI)

**Option B: Add calculated column**:
```dax
Report Key = '___Benchmark'[Report Number]
```

---

## Complete Fix Checklist

Use this checklist to systematically fix the errors:

### Data Model Setup

- [ ] **Table `___Benchmark` exists** (3 underscores)
- [ ] **Table `___DimMonth` exists** with correct columns
- [ ] **Table `___DimEventType` exists** with correct columns

### Column Verification (___Benchmark table)

- [ ] `Report Key` or `Report Number` exists
- [ ] `MonthStart` exists (date type)
- [ ] `EventType` exists (text type, no space)
- [ ] `Incident Date` exists (date type)
- [ ] `# of Officers Involved` exists (number type)
- [ ] `# of Subjects` exists (number type)

### Relationships

- [ ] `___Benchmark[MonthStart]` → `___DimMonth[MonthStart]` (many-to-one)
- [ ] `___Benchmark[EventType]` → `___DimEventType[EventType]` (many-to-one)

### Measure Verification

- [ ] `Total Incidents Rolling 13` measure exists and works
- [ ] `Avg Incidents Per Month` measure exists and works
- [ ] No red underlines in DAX formula bar

### Visual Verification

- [ ] Benchmark visual refreshes without errors
- [ ] No "can't display this visual" errors
- [ ] Numbers appear correctly

---

## Quick Diagnostic Script (Power BI DAX)

**Create a new measure** to test your table structure:

```dax
_DIAGNOSTIC_Test = 
VAR TestTable = "___Benchmark table: " & IF(ISBLANK(COUNTROWS(___Benchmark)), "MISSING", "EXISTS") & 
    UNICHAR(10) & "DimMonth table: " & IF(ISBLANK(COUNTROWS(___DimMonth)), "MISSING", "EXISTS") &
    UNICHAR(10) & "DimEventType table: " & IF(ISBLANK(COUNTROWS(___DimEventType)), "MISSING", "EXISTS")
RETURN
    TestTable
```

**Add to a card visual** to see results.

---

## Most Likely Fix Path

Based on the errors shown, **here's the most likely issue and fix**:

### Issue: Table Named Incorrectly

**Symptom**: Measure error references `'__Benchmark[Total Incidents Rolling 13]'` (2 underscores in screenshot)

**Fix**:
1. Check your table name in Power BI
2. If it's `__Benchmark` (2 underscores), rename to `___Benchmark` (3 underscores)
3. OR update all DAX measures to use 2 underscores: `__Benchmark`

### Issue: Missing MonthStart Column

**Symptom**: Measures reference `___Benchmark[MonthStart]` but column doesn't exist

**Fix**: Add MonthStart column using Solution 4 above

### Issue: EventType Column Has Space

**Symptom**: M code creates `Event Type` but DAX expects `EventType`

**Fix**: Update M code (Solution 2, Option A) or add calculated column

---

## Testing After Fix

### Test 1: Measure Works

1. Create new card visual
2. Add measure: `Total Incidents Rolling 13`
3. Should show a number (not error)

### Test 2: Dimension Tables Work

1. Create table visual
2. Add columns:
   - `___DimMonth[MonthLabel]`
   - `___DimEventType[EventType]`
   - Measure: `[IncidentCount]`
3. Should show 13 months × 3 event types = 39 rows (with data)

### Test 3: Original Visual Works

1. Refresh original Benchmark visual
2. Should display without errors
3. Verify numbers look reasonable

---

## Updated M Code (Complete Fix)

Here's your M code with all fixes applied:

```m
// Benchmark Data Query - Simplified Structure
// Updated: 2026-02-09 (Fixed for DAX compatibility)
// Source: 05_EXPORTS\Benchmark\ (simplified structure)

let
    // Base path to simplified Benchmark directory
    BenchmarkBasePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark\",
    
    // Function to load latest file from a folder
    LoadLatestFile = (folderPath as text, eventType as text) =>
        let
            // Get all CSV files in the folder
            Source = Folder.Files(folderPath),
            
            // Filter to CSV files only
            FilteredFiles = Table.SelectRows(Source, 
                each Text.EndsWith([Name], ".csv") or Text.EndsWith([Name], ".xlsx")
            ),
            
            // Sort by Date modified (most recent first)
            SortedFiles = Table.Sort(FilteredFiles, {{"Date modified", Order.Descending}}),
            
            // Get the first (most recent) file
            LatestFile = if Table.RowCount(SortedFiles) > 0 
                then SortedFiles{0}[Content]
                else error "No files found in " & folderPath,
            
            // Load the file content
            LoadedData = if Text.EndsWith(SortedFiles{0}[Name], ".csv")
                then Csv.Document(LatestFile, [Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None])
                else Excel.Workbook(LatestFile){0}[Data],
            
            // Promote headers
            PromotedHeaders = Table.PromoteHeaders(LoadedData, [PromoteAllScalars=true]),
            
            // Add EventType column (NO SPACE - matches DAX)
            AddedEventType = Table.AddColumn(PromotedHeaders, "EventType", each eventType, type text),
            
            // Add Source File column (for tracking)
            AddedSource = Table.AddColumn(AddedEventType, "Source File", each SortedFiles{0}[Name], type text)
        in
            AddedSource,
    
    // Load each event type
    UseOfForce = try LoadLatestFile(BenchmarkBasePath & "use_force\", "Use of Force") 
                 otherwise #table(type table [Message = text], {{"No Use of Force data found"}}),
    
    ShowOfForce = try LoadLatestFile(BenchmarkBasePath & "show_force\", "Show of Force") 
                  otherwise #table(type table [Message = text], {{"No Show of Force data found"}}),
    
    VehiclePursuit = try LoadLatestFile(BenchmarkBasePath & "vehicle_pursuit\", "Vehicle Pursuit") 
                     otherwise #table(type table [Message = text], {{"No Vehicle Pursuit data found"}}),
    
    // Combine all event types
    CombinedBenchmark = Table.Combine({UseOfForce, ShowOfForce, VehiclePursuit}),
    
    // *** NEW: Add MonthStart column (required by DAX measures) ***
    AddMonthStart = Table.AddColumn(CombinedBenchmark, "MonthStart", 
        each Date.StartOfMonth([Incident Date]), type date),
    
    // *** NEW: Type conversions (adjust column names to match your CSV) ***
    TypedColumns = Table.TransformColumnTypes(AddMonthStart, {
        {"Incident Date", type date},
        {"EventType", type text},
        {"MonthStart", type date},
        {"Source File", type text}
        // Add more columns as needed based on your CSV structure
    }),
    
    // Return the final data
    Result = TypedColumns
in
    Result
```

**Key Changes**:
1. ✅ `EventType` column (no space) - line 50
2. ✅ `MonthStart` column added - line 68
3. ✅ Type conversions - line 72

---

## Summary

**Most Likely Issues**:
1. ❌ Table name mismatch (`__Benchmark` vs `___Benchmark`)
2. ❌ Missing `MonthStart` column
3. ❌ Column name has space (`Event Type` vs `EventType`)
4. ❌ Missing dimension tables (`___DimMonth`, `___DimEventType`)

**Fix Order**:
1. **First**: Create dimension tables (if missing)
2. **Second**: Fix column names in main table
3. **Third**: Verify relationships
4. **Fourth**: Test measures
5. **Fifth**: Refresh visual

**Time Required**: 15-30 minutes

---

**Need Help?**
- Start with the Complete Fix Checklist
- Use the Diagnostic Script to verify table structure
- Test measures one at a time using card visuals

---

**Last Updated**: February 9, 2026  
**Status**: Diagnostic guide complete - ready to implement fix
