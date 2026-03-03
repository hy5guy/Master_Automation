# Detective Queries - 2026 Workbook Update Guide

**Date**: 2026-02-13  
**Author**: R. A. Carucci  
**Purpose**: Update Power BI M code queries for restructured Detectives workbook (2026-only data)

---

## Excel Workbook Changes (by Claude Excel Add-on)

### What Changed

**File**: `detectives_monthly.xlsx`  
**Location**: `C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Detectives\`

### Restructure Summary

1. **New MoM Table (_mom_det)**
   - **Old**: Multi-year columns spanning several years
   - **New**: 12 columns only: `01-26` through `12-26` (2026 only)
   - **Rows**: 40 tracked items
   - **Format**: Text headers (@) to prevent auto-date formatting

2. **New CCD Table (_CCD_MOM)**
   - **Old**: Multi-year columns
   - **New**: 12 columns: `01-26` through `12-26` (2026 only)
   - **Rows**: 11 disposition types (10 counts + 1 percentage row)
   - **Format**: Percentage rows (10-11) formatted as decimals (0.0%)

3. **Monthly Sheets Created**
   - **Sheets**: `26_JAN`, `26_FEB`, `26_MAR`... `26_DEC` (12 total)
   - **Tables**: Each sheet has 2 tables:
     - `_26_JAN` (Tracked Items with Total column)
     - `_26_JAN_CCD` (Case dispositions with Total column)
   - **Linking**: MoM and CCD tables use XLOOKUP to pull from monthly sheets

4. **Known Issues Fixed**
   - Row label spacing (trailing/double spaces) handled
   - MM-YY headers stored as text (not dates)
   - Percentage values stored as decimals

---

## M Code Query Updates

### Query 1: ___Detectives

**File**: `m_code/detectives/___Detectives_2026.m`

#### Key Changes

1. **Simplified Rolling Window**
   - Still calculates 13-month window dynamically
   - Works with 2026-only data (will filter to available months)
   - As 2026 progresses, will include 13 months (up to 12 in 2026 + spillover)

2. **Date Parsing Enhanced**
   - Default year changed from "25" to "26" for current year
   - Handles MM-YY format: `01-26` → January 2026

3. **Added Standard Header**
   - Following project conventions
   - Includes timestamp, project, author, purpose

#### What Stayed the Same

- Table name: `_mom_det` (unchanged)
- File path: Same location
- Column structure: Still unpivots month columns
- Row filtering: Still removes empty rows and filters to active cases
- Metadata: Same reporting period and case type classification

---

### Query 2: ___Det_case_dispositions_clearance

**File**: `m_code/detectives/___Det_case_dispositions_clearance_2026.m`

#### Key Changes

1. **Enhanced Row Label Matching**
   - Uses `Text.Trim()` to handle trailing/double spaces
   - More robust matching against `RequiredOrder` list

2. **Added YTD Bureau Case Clearance %**
   - Added to `RequiredOrder` list per Claude recommendation
   - Row will be included if present in Excel

3. **Percentage Normalization Enhanced**
   - Handles decimals stored in Excel (0.50)
   - Still handles legacy formats ("50%", 50)
   - Simplified logic since Excel now stores as decimals

4. **Added Standard Header**
   - Following project conventions
   - Includes timestamp, project, author, purpose

#### What Stayed the Same

- Table name: `_CCD_MOM` (unchanged)
- File path: Same location
- Rolling 13-month window logic
- Disposition category grouping
- All helper columns (Date, Month_Year, Sort_Order, etc.)

---

## Deployment Instructions

### Step 1: Backup Current Queries

1. Open Power BI Desktop
2. Go to **Home** → **Transform Data**
3. Find queries:
   - `___Detectives`
   - `___Det_case_dispositions_clearance`
4. For each query:
   - Right-click → **Duplicate**
   - Rename duplicate to `___Detectives_BACKUP_20260213`
   - Leave backups disabled (don't load to report)

### Step 2: Update ___Detectives Query

1. Click on `___Detectives` query
2. Click **View** → **Advanced Editor**
3. **Select All** (Ctrl+A) and delete
4. Open file: `m_code\detectives\___Detectives_2026.m`
5. **Copy** entire contents
6. **Paste** into Advanced Editor
7. Click **Done**
8. Verify no errors appear

### Step 3: Update ___Det_case_dispositions_clearance Query

1. Click on `___Det_case_dispositions_clearance` query
2. Click **View** → **Advanced Editor**
3. **Select All** (Ctrl+A) and delete
4. Open file: `m_code\detectives\___Det_case_dispositions_clearance_2026.m`
5. **Copy** entire contents
6. **Paste** into Advanced Editor
7. Click **Done**
8. Verify no errors appear

### Step 4: Verify Data Load

1. Check `___Detectives` query preview:
   - Should show tracked items with 2026 dates
   - MonthsIncluded column should show actual count (1-12 depending on current month)
   - ReportingPeriod should show current 13-month window

2. Check `___Det_case_dispositions_clearance` query preview:
   - Should show disposition types with 2026 dates
   - Percentage rows should show decimal values (0.xx)
   - Should include "YTD Bureau Case Clearance %" if present in Excel

### Step 5: Close & Apply

1. Click **Close & Apply** (top left)
2. Wait for data refresh to complete
3. Check visuals for correct data display

### Step 6: Test Visuals

Verify these elements in your report:

- [ ] Detective case counts by month show 2026 data
- [ ] Case disposition types display correctly
- [ ] Percentage values display correctly (xx.x%)
- [ ] Rolling window includes correct months
- [ ] No error messages in visuals
- [ ] Filters work correctly

---

## Troubleshooting

### Issue: "Table '_mom_det' not found"

**Cause**: Excel table name mismatch

**Solution**:
1. Open `detectives_monthly.xlsx`
2. Go to MoMTotals sheet
3. Click in table → **Table Design** tab
4. Verify table name is exactly `_mom_det`
5. If different, update M code or rename Excel table

### Issue: "No data showing in visuals"

**Cause**: Date filtering or empty data

**Solution**:
1. Check Power Query Editor
2. Look at `FilteredMonths` step
3. Verify dates are within the 13-month window
4. Check if Excel sheets have data in monthly tables

### Issue: "Percentage values showing as whole numbers"

**Cause**: Percentage normalization not working

**Solution**:
1. Check `Normalized` step in Power Query
2. Verify `Is_Percent` flag is true for percentage rows
3. Check if Excel percentage rows are formatted correctly

### Issue: "Missing rows in CCD query"

**Cause**: Row label spacing mismatch

**Solution**:
1. Check `RequiredOrder` list in M code
2. Compare with actual row labels in Excel `_CCD_MOM` table
3. Adjust for trailing spaces: `"Label "` vs `"Label"`
4. Use `Text.Trim()` to normalize (already in updated code)

---

## Data Validation Checklist

After deployment, verify:

- [ ] **___Detectives query**
  - Shows data for 2026 months only
  - MonthsIncluded = actual available months (not 13 until Dec 2026)
  - All tracked items present
  - Case_Type classification working (High Impact vs Administrative)
  
- [ ] **___Det_case_dispositions_clearance query**
  - All 9-10 disposition types present
  - Percentage row(s) showing decimal values
  - Disposition_Category grouping correct
  - Month_Abbrev showing MM-YY format
  
- [ ] **Power BI Visuals**
  - All visuals showing 2026 data
  - No error messages
  - Filters working
  - Percentages displaying correctly (as %)

---

## Monthly Data Entry Process (for reference)

As each month progresses in 2026:

1. **Update Monthly Sheet** (e.g., `26_FEB`)
   - Enter tracked items data in main table
   - Enter case dispositions in CCD table
   - Update Total Follow-Ups if applicable

2. **Automatic Updates**
   - MoM table auto-updates via XLOOKUP
   - CCD table auto-updates via XLOOKUP
   - Power BI refreshes on next scheduled refresh

3. **Rolling Window Adjustment**
   - Power BI queries automatically adjust window
   - Example (as of Feb 13, 2026):
     - Window: Jan 2025 - Jan 2026
     - But only Jan 2026 data available from Excel
     - Query will show only available months

---

## Future Considerations

### When to Update for 2027

**Around December 2026**, the workbook will need another restructure to include 2027 months. At that time:

1. Excel will need new columns: `01-27` through `12-27`
2. M code may need updates for multi-year handling
3. Consider keeping 2026 data for historical comparison

### Alternative: Multi-Year Structure

If frequent restructuring is undesirable, consider changing Excel to:
- Keep all historical columns (01-25, 02-25... 01-27, 02-27, etc.)
- M code already handles multi-year via dynamic date parsing
- Only downside: Excel file grows wider over time

---

## Files Created

1. `m_code/detectives/___Detectives_2026.m` - Updated Detectives query
2. `m_code/detectives/___Det_case_dispositions_clearance_2026.m` - Updated CCD query
3. `docs/DETECTIVES_2026_UPDATE_GUIDE.md` - This file

---

## Summary of Changes

| Component | Old Behavior | New Behavior |
|-----------|-------------|--------------|
| **Data Range** | Multi-year columns | 2026 only (01-26 to 12-26) |
| **Rolling Window** | Complex multi-year filtering | Simplified for single year |
| **Date Parsing** | Default year "25" | Default year "26" |
| **Row Matching** | Direct comparison | Text.Trim() for spacing |
| **Percent Normalization** | Complex multi-format | Simplified (Excel stores decimals) |
| **YTD Clearance %** | Not included | Added to RequiredOrder |
| **Headers** | No standard header | Standard project header added |

---

## Testing Completed

- [x] M code syntax validated (no errors)
- [x] Standard headers added per project conventions
- [x] Documentation complete
- [ ] **User to test**: Deploy to Power BI and verify data loads correctly

---

*Guide Created: 2026-02-13*  
*Author: R. A. Carucci*  
*Version: 1.0*
