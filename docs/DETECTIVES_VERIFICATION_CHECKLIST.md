# Detective Queries - Pre-Deployment Verification Checklist

**Date**: 2026-02-13  
**Status**: Ready for testing

---

## Fixes Applied

### Both Queries ✅
1. **Date Parsing Fixed** - Changed from `Value.FromText()` to `Number.From()`
   - Prevents type comparison errors (Number vs Text)
   - Returns null instead of text on parse failure
   - Safe for `>= 50` comparison

2. **Window Logic Updated** - Changed for 2026-only data
   - **Old**: Start = Jan 2025, End = Jan 2026 (looking for 2025 data)
   - **New**: Start = Jan 2026, End = previous month (shows available 2026 data)

### ___Detectives Query ✅
3. **Circular Reference Fixed** - MonthsIncluded pre-calculated
   - Was: Calculated inside Table.AddColumn (caused empty table)
   - Now: Calculated once before column addition

---

## Test in Power BI

### Test 1: ___Detectives Query

1. Open Power BI → **Transform Data**
2. Find query: `___Detectives` (or create new one)
3. **Advanced Editor** → Paste from:
   ```
   C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\m_code\detectives\___Detectives_2026.m
   ```
4. Click **Done**

**Expected Results**:
- ✅ No errors in preview
- ✅ Shows data rows (not empty!)
- ✅ Date column shows 2026 dates (e.g., 1/1/2026, 2/1/2026)
- ✅ MonthsIncluded shows a number (1-12 depending on available data)
- ✅ ReportingPeriod shows "01/26 - 01/26" (or current range)

**Check these columns**:
- `Tracked Items` (or first column name)
- `Month_MM_YY` (e.g., "01-26", "02-26")
- `Value` (numbers)
- `Date` (dates, not null)
- `Month_Sort_Order` (202601, 202602, etc.)
- `Case_Type` (High Impact or Administrative)
- `MonthsIncluded` (should be 1 for January 2026 data only)

---

### Test 2: ___Det_case_dispositions_clearance Query

1. Find query: `___Det_case_dispositions_clearance`
2. **Advanced Editor** → Paste from:
   ```
   C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\m_code\detectives\___Det_case_dispositions_clearance_2026.m
   ```
3. Click **Done**

**Expected Results**:
- ✅ No type comparison errors
- ✅ Shows 9-10 disposition rows (depending on YTD % presence)
- ✅ Date column shows 2026 dates
- ✅ Percentage rows show decimal values (0.00 to 1.00)

**Check these columns**:
- First column (disposition types)
- `Month` (e.g., "01-26")
- `Value` (numbers, decimals for % rows)
- `Date` (dates, not null)
- `Is_Percent` (true for % rows, false for others)
- `Disposition_Category` (Open Cases, Prosecuted, Cleared, Performance Metric)

**Verify percentage normalization**:
- If Excel has "50%" → Value should be 0.50
- If Excel has 50 → Value should be 0.50
- If Excel has 0.50 → Value should be 0.50

---

## Common Issues to Check

### If ___Detectives Still Returns Empty:

**Check Applied Steps** in Power Query:
1. Click on `FilteredToActiveCases` step
   - Should show rows with activity > 0
   - If empty here, Excel data might have no non-zero values
   
2. Click on `UnpivotedData` step
   - Should show unpivoted data with Month_MM_YY column
   - If empty, previous step had no data
   
3. Click on `AddedDateInfo` step
   - Check Date column - should NOT be all nulls
   - If all null, date parsing is failing
   
4. Click on `FilteredMonths` step
   - Should show filtered data
   - If empty here, date filter is excluding everything

**Debug**: Remove the date filter temporarily to see if data appears:
- Comment out the FilteredMonths step
- Use AddedSortOrder as the next input instead

---

### If Type Error Still Occurs:

**Check** which step is failing:
1. Click through Applied Steps one by one
2. Find where error appears
3. Look at the error message details

**Common causes**:
- Column name mismatch (FirstColumnName not matching)
- Date parsing on non-date columns
- Type conversion on mixed data types

---

## Quick Verification Script

Run this in Power Query to check your data:

```powerquery
// Quick test - paste in blank query
let
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Detectives\detectives_monthly.xlsx"),
        null, true
    ),
    
    // Check what tables are available
    TableList = Source,
    
    // Try to load _mom_det
    MoM_Test = try Source{[Item="_mom_det", Kind="Table"]}[Data] otherwise "Table not found",
    
    // Try to load _CCD_MOM
    CCD_Test = try Source{[Item="_CCD_MOM", Kind="Table"]}[Data] otherwise "Table not found"
in
    #table(
        {"Test", "Result"},
        {
            {"Tables Available", Text.Combine(Table.Column(TableList, "Name"), ", ")},
            {"_mom_det Load", if MoM_Test is table then "OK" else MoM_Test},
            {"_CCD_MOM Load", if CCD_Test is table then "OK" else CCD_Test}
        }
    )
```

**Expected**:
- Tables Available: Should list "_mom_det", "_CCD_MOM" and sheet names
- _mom_det Load: "OK"
- _CCD_MOM Load: "OK"

---

## Please Test and Report

After pasting the updated M code in Power BI, please check:

1. **___Detectives Query**:
   - [ ] Shows data in preview (not empty)?
   - [ ] How many rows appear?
   - [ ] What value does MonthsIncluded show?
   - [ ] Any errors?

2. **___Det_case_dispositions_clearance Query**:
   - [ ] Shows data in preview?
   - [ ] How many disposition types appear?
   - [ ] Are percentage values showing as decimals (0.xx)?
   - [ ] Any errors?

Let me know the results and we'll proceed from there!

---

*Verification Checklist - 2026-02-13*
