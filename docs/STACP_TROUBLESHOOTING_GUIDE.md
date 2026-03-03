# STACP Visual - Comprehensive Troubleshooting Guide
## Issue: Visuals Only Show 12-25 and 01-26 After M Code Update

**Date**: 2026-02-13  
**Status**: INVESTIGATING

---

## Excel File Analysis ✅ CONFIRMED OK

**File**: `STACP.xlsm`  
**Sheet**: `MoMTotals`

**Column Structure** (Python Analysis Results):
- ✅ Total columns: 54
- ✅ Date columns found: **32** (all properly formatted as MM-YY)
- ✅ Column headers: `06-23, 07-23, 08-23... 12-25, 01-26`
- ✅ Data exists in individual month sheets (`25_JAN`, `25_FEB`, etc.)
- ✅ **ALL columns are formatted correctly** (no unpadded months like "3-25")

**Conclusion**: The Excel source file is **correct** and has all 32 months of data.

---

## Problem Diagnosis

Since the Excel file has all months but Power BI only shows 2 months (12-25, 01-26), the issue is likely:

### Hypothesis 1: Power BI Cache Not Refreshed
**Most Likely Cause**

Power BI may be using cached column metadata from before you updated the M code.

**Symptoms**:
- M code is updated
- Excel file has all columns
- But Power BI still shows old behavior

**Solution**: Force Power BI to reload the query

### Hypothesis 2: Wrong Query Being Used
The visual might be pointing to a different query (not `___STACP_pt_1_2`).

**Solution**: Verify which query the visual is actually using

### Hypothesis 3: Filter Applied to Visual
There might be a page-level or visual-level filter limiting the months shown.

**Solution**: Check visual filters

---

## Troubleshooting Steps

### Step 1: Verify You're Updating the Correct Query

1. Open Power BI Desktop
2. Go to **Home** → **Transform Data** (Power Query Editor)
3. In the left pane (Queries list), look for:
   - `___STACP_pt_1_2` ← Should be this one
   - `STACP_pt_1_2` ← Or maybe without underscores?
   - Other STACP-related queries?

**Question**: What's the **exact name** of the query in the Queries pane?

---

### Step 2: Run Diagnostic Query

Create a NEW query to see what Power BI is actually detecting:

1. In Power Query Editor, click **New Source** → **Blank Query**
2. Click **Advanced Editor**
3. Paste the contents from:
   ```
   C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\m_code\stacp\STACP_DIAGNOSTIC.m
   ```
4. Click **Done**
5. Rename query to `STACP_Diagnostic`

**Expected Result**:
```
Metric                          | Count | Details
--------------------------------|-------|--------------------------------
Total Columns in MoMTotals      | 54    | (all column names)
Detected Month Columns          | 32    | 06-23, 07-23... 01-26
Columns in 13-Month Window      | 13    | 01-25, 02-25... 12-25, 01-26
First Column Name               | 1     | Tracked Items
```

**If you see**:
- ✅ **32 detected month columns** → M code is working, continue to Step 3
- ❌ **2 detected month columns** → M code not loaded correctly, go to Step 4

---

### Step 3: Force Refresh Without Cache

1. Close Power BI Desktop completely (don't just save)
2. Navigate to file location in File Explorer
3. Right-click the `.pbix` file → **Properties**
4. Note the file size and modified date
5. Open Power BI Desktop again
6. Open the file
7. **DO NOT** click "Apply Changes" immediately
8. Go to **Home** → **Transform Data**
9. Find the `___STACP_pt_1_2` query
10. Right-click → **Delete** (yes, delete it!)
11. Create a **NEW** query:
    - **New Source** → **Blank Query**
    - **Advanced Editor**
    - Paste from `STACP_pt_1_2_FIXED.m`
    - Rename to `___STACP_pt_1_2`
12. Click **Close & Apply**

This forces Power BI to completely rebuild the query metadata.

---

### Step 4: Verify Query Applied Steps

If the diagnostic shows only 2 columns detected:

1. In Power Query Editor, click on `___STACP_pt_1_2` query
2. Look at **Applied Steps** pane (right side)
3. Click on the `AllMonthColumns` step (if it exists)
4. In the formula bar (top), you should see the enhanced detection logic

**Check for**:
```powerquery
IsMonthValid = Text.Length(MonthPart) >= 1 and Text.Length(MonthPart) <= 2 and 
               (try Number.From(MonthPart) >= 1 and Number.From(MonthPart) <= 12 otherwise false),
```

**If you see old code** (like `HasYear = Text.Contains...`):
- The M code didn't update properly
- Delete the query and recreate it (Step 3)

---

### Step 5: Check Visual Configuration

If Power Query shows 13 months but visual still shows 2:

1. Click on the STACP visual
2. Open **Filters** pane (right side)
3. Check:
   - **Filters on this visual**
   - **Filters on this page**
   - **Filters on all pages**
4. Look for `Month_MM_YY` or `Date_Sort_Key` filters

**If filtered**:
- Clear the filter
- Or expand it to include all 13 months

---

### Step 6: Check Visual Data Source

1. Click on the STACP visual
2. Look at **Fields** pane (right side)
3. Under **Rows**, what does it show?
   - Should be from `___STACP_pt_1_2` table
4. Under **Columns**, what does it show?
   - Should be `Month_MM_YY` from `___STACP_pt_1_2`

**If it's pointing to a different query**:
- The visual is using the wrong data source
- You need to update the visual to point to the correct query

---

## Common Issues and Solutions

### Issue: "Column 'Month_MM_YY' not found"

**Cause**: Visual is using old cached column list

**Solution**:
1. Remove the visual completely
2. Create a new matrix visual
3. Add fields from the updated query
4. Configure the new visual

### Issue: "Applied changes show 13 months in Power Query but visual shows 2"

**Cause**: Visual configuration issue or filter

**Solution**:
1. Check Step 5 (Visual filters)
2. Try creating a NEW visual from scratch
3. Verify the visual is using `___STACP_pt_1_2` as data source

### Issue: "Power Query shows old M code even after pasting new code"

**Cause**: Power BI didn't accept the changes or wrong query was updated

**Solution**:
1. Delete the query completely
2. Create new blank query
3. Paste fresh M code
4. Rename to match original
5. Update visual to use new query

---

## Diagnostic Checklist

Use this checklist to identify where the issue is:

- [ ] Excel file has all 32 month columns ✅ **CONFIRMED**
- [ ] M code updated in Power BI (`STACP_pt_1_2_FIXED.m` contents)
- [ ] Correct query name: `___STACP_pt_1_2` (note the 3 underscores)
- [ ] Power Query Applied Steps show enhanced detection logic
- [ ] Diagnostic query shows 32 detected month columns
- [ ] Diagnostic query shows 13 columns in window
- [ ] Visual is using `___STACP_pt_1_2` as data source
- [ ] No filters limiting months on visual
- [ ] No filters limiting months on page
- [ ] Power BI file closed and reopened after changes
- [ ] **Close & Apply** clicked after M code update

---

## Request for Information

To continue troubleshooting, please provide:

1. **Diagnostic Query Results**: After running `STACP_DIAGNOSTIC.m`, what are the counts?
   - Total Columns in MoMTotals: ?
   - Detected Month Columns: ?
   - Columns in 13-Month Window: ?

2. **Query Name**: What's the exact name in the Queries pane?

3. **Applied Steps**: In Power Query Editor, what Applied Steps do you see for the query?

4. **Filter Status**: Are there any filters showing in the Filters pane when you click the visual?

5. **Visual Data Source**: In the Fields pane, which table/query is the visual pulling from?

---

## Next Actions

**If Diagnostic shows 32 columns detected**:
- Issue is with visual configuration or filters
- Follow Steps 5-6

**If Diagnostic shows 2 columns detected**:
- M code not applied correctly
- Follow Steps 3-4

**If unsure**:
- Provide the diagnostic results above
- We'll identify the exact issue and fix it

---

*Troubleshooting Guide - 2026-02-13*
