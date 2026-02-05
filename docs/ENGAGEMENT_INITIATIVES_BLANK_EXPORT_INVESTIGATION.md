# Engagement Initiatives by Bureau - Blank Export Investigation

**Issue ID:** DEC2025-001  
**Priority:** HIGH  
**Status:** 🔴 OPEN - Requires Fix  
**Discovered:** 2026-02-05  
**Affected Reports:** All 3 copies of December 2025 Power BI report

---

## Issue Summary

The "Engagement Initiatives by Bureau" visual shows **complete data** in the PDF report but exports as a **blank CSV file** (only headers, no data rows). This affects all monthly reporting and historical data tracking.

---

## Affected Files

### Power BI Reports (All 3 show same issue):
```
C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Monthly Reports\2025\12_december\
  ├─ 2026_01_10_12_Monthly_FINAL_LAP.pbix ❌
  ├─ 2026_01_10_12_Monthly_FINAL_LAP-PD_BCI_LTP.pbix ❌
  └─ 2025_12_Monthly_FINAL_LAP.pbix ❌
```

### Exported CSV File:
```
C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\2025_12\community_engagement\
  └─ 2025_12_Engagement Initiatives by Bureau.csv (83 bytes - BLANK)
```

### PDF Report (Shows Data):
```
C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Monthly Reports\2025\12_december\
  └─ 2026_01_10_12_Monthly_FINAL_LAP.pdf (Page 6 - Complete Data)
```

---

## Evidence

### CSV Export Result (BLANK):
```csv
Office,Event Name,Location of Event,Event Duration (Hours),Number of Attendees

```
**Size:** 83 bytes  
**Data Rows:** 0  
**Status:** ❌ BLANK

### PDF Report Result (COMPLETE):
**Page 6 shows:**
- **22 events** for December 2025
- **71 total attendees**
- **15.5 total hours** of engagement

| Office | Event Name | Location | Hours | Attendees |
|--------|-----------|----------|-------|-----------|
| Community Engagement | chiefs luncheon | Civic Center | 0.50 | 2 |
| Community Engagement | City Christmas Tree Lighting | At The Green | 0.50 | 8 |
| Community Engagement | Distributing gifts Santa and the Grinch | 4 different locations | 0.50 | 4 |
| Community Engagement | Eiffel Tower Toy pick up | 181 Prospect Ave | 0.50 | 3 |
| Community Engagement | Hope One Van | Stop & Shop | 0.50 | 1 |
| Community Engagement | Hope One Van Flu Shot | Johnson Library | 0.50 | 1 |
| Community Engagement | Meeting Home Depot Handing out flyers | Home Depot, Noches, Baires, Salad | 0.50 | 2 |
| Community Engagement | Meeting Homeless shelter | 120 S. River st | 0.50 | 3 |
| Community Engagement | MLK Senior Center Giveaway | 375 First st | 0.50 | 2 |
| Community Engagement | Orange & Brew (Coffee w a Cop) | Lodi High School | 0.50 | 1 |
| Community Engagement | Photo with Santa | Columbus Park | 0.50 | 4 |
| Community Engagement | Shop with a cop | Target | 0.50 | 5 |
| Community Engagement | Toy Drive Closter | Closter NJ | 0.50 | 4 |
| Community Engagement | Toy giveaway | Mount Zion | 0.50 | 3 |
| Community Engagement | Toy pick up | around town | 0.50 | 3 |
| Community Engagement | Toy pick up | Edgewater | 0.50 | 3 |
| Community Engagement | Youth Night | 116 Holt st | 0.50 | 5 |
| STA&CP | LEAD | Fairmount School | 0.50 | 1 |
| STA&CP | LEAD | Hillers School | 0.50 | 1 |
| STA&CP | LEAD | Jackson Ave School | 3.50 | 7 |
| STA&CP | LEAD | Nellie K. Parker School | 1.50 | 3 |
| STA&CP | LEAD Graduation | Jackson Ave School | 0.50 | 4 |

**Total:** 22 events, 71 attendees, 15.5 hours

---

## Root Cause Analysis

### Hypothesis #1: Relative Date Filter Using TODAY() ⭐ MOST LIKELY

**Problem:** Visual filter uses `TODAY()` or `NOW()` function to show "previous month" data, which causes the filter to exclude December 2025 when current date is in February 2026.

**Evidence:**
- PDF generated on January 10, 2026 shows December 2025 data ✅
- CSV exported on January 10, 2026 is blank ❌
- When date was closer to December, data was visible
- Now in February 2026, December 2025 is 2 months ago

**Example DAX that would cause this:**
```dax
// This would fail when current date moves past January
Engagement This Month = 
CALCULATE(
    COUNT(Engagement[EventID]),
    FILTER(
        Engagement,
        Engagement[Date] >= EOMONTH(TODAY(), -2) + 1 &&
        Engagement[Date] <= EOMONTH(TODAY(), -1)
    )
)
```

**Why PDF works but CSV doesn't:**
- PDF rendering might cache the visual state from when it was created
- CSV export re-evaluates the DAX/filters in real-time with current date
- This causes a mismatch between what's shown and what's exported

### Hypothesis #2: Page-Level or Visual-Level Date Filter

**Problem:** A date slicer or filter on the page is set to "Previous Month" or similar relative date, which changes as time passes.

**Check for:**
- Date slicers on the page
- Visual-level filters in the Filters pane
- Page-level filters
- Report-level filters

### Hypothesis #3: M Code Date Filter in Power Query

**Problem:** The Power Query source might have a date filter that excludes December when current month is February.

**Example M Code that would cause this:**
```m
// This would exclude December 2025 when current date is in February 2026
let
    Source = ...,
    FilteredRows = Table.SelectRows(
        Source, 
        each [Date] >= Date.AddMonths(DateTime.LocalNow(), -1) and 
             [Date] < DateTime.LocalNow()
    )
in
    FilteredRows
```

### Hypothesis #4: Visual Export Limitation

**Problem:** Some Power BI visuals have limitations on what can be exported, especially tables with complex calculations.

**Less Likely** because:
- Headers export correctly
- Other similar visuals export fine
- This is a simple table visual

---

## Troubleshooting Steps

### Step 1: Open Power BI Desktop

1. Open one of the affected .pbix files:
   ```
   2026_01_10_12_Monthly_FINAL_LAP.pbix
   ```

2. Navigate to the page containing "Engagement Initiatives by Bureau"

### Step 2: Check Visual Filters

1. **Click on the visual** to select it
2. **Open the Filters pane** (right side of Power BI)
3. **Check all filter levels:**
   - Visual-level filters
   - Page-level filters
   - Report-level filters
   - Drill-through filters

4. **Look for date filters** containing:
   - `TODAY()`
   - `NOW()`
   - "Relative date"
   - "Last month"
   - "Previous month"

5. **Screenshot the filters** for documentation

### Step 3: Check DAX Measures

1. **Open the Fields pane** (right side)
2. **Find the measure** used in the visual
3. **Right-click the measure** → "Edit formula"
4. **Look for date logic** using:
   - `TODAY()`
   - `NOW()`
   - `EOMONTH(TODAY()...)`
   - `DATEADD(..., -1, MONTH)`

5. **Copy the DAX formula** to the investigation notes below

### Step 4: Check Table/Visual Properties

1. **Select the visual**
2. **Go to Format pane** (paintbrush icon)
3. **Check under "Title"** - note the exact title text
4. **Check under "General"** - any date-related properties

### Step 5: Check Data Source (Power Query)

1. **Go to Home tab** → **Transform data** (opens Power Query Editor)
2. **Find the Engagement table** in the Queries pane
3. **Look at the Applied Steps** on the right
4. **Check each step** for date filtering:
   - Click each step
   - Look at the formula bar at the top
   - Look for `DateTime.LocalNow()` or `Date.AddMonths()`

5. **Copy any date-related M code** to investigation notes

### Step 6: Check Source Data

1. In Power Query Editor, **right-click the Engagement query** → "Advanced Editor"
2. **Review the complete M code**
3. **Check the source location**:
   - Is it a file?
   - Is it a database?
   - Where is the data coming from?

### Step 7: Test Data Visibility

1. **Back in Report View**, create a **new simple table visual**
2. **Add fields:**
   - Office
   - Event Name
   - Date
3. **Try to export this new visual** as CSV
4. **Compare results:**
   - Does the new visual export with data?
   - If yes, the issue is specific to the original visual design
   - If no, the issue is in the data source/query

---

## Investigation Notes Template

Use this template to document findings:

### Date: _______

#### Visual Filters Found:
```
Filters Pane:
  - Visual Level: _________________________
  - Page Level: ___________________________
  - Report Level: _________________________
  
Slicers on Page: _________________________
```

#### DAX Measure(s) Used:
```dax
// Copy the exact DAX formula here


```

#### Power Query Source:
```m
// Copy the M code from Advanced Editor


```

#### Data Source Details:
```
Source Type: _________________ (File/Database/API)
Location: ____________________
Last Refresh: ________________
Rows in Table: _______________
Date Range: __________________
```

#### Test Results:
```
New Visual Created: Yes / No
New Visual Export Result: ____________
Date Filter Found: Yes / No
Date Filter Type: ____________________
```

---

## Proposed Fixes

### Fix Option 1: Replace Relative Date with Parameter (RECOMMENDED)

**Create a Month/Year Parameter:**

1. **Home tab** → **Manage Parameters** → **New Parameter**
   - Name: `ExportMonth`
   - Type: Text
   - Current Value: `2025-12`

2. **Update DAX measure:**
```dax
Engagement Data = 
VAR SelectedYear = VALUE(LEFT([ExportMonth], 4))
VAR SelectedMonth = VALUE(RIGHT([ExportMonth], 2))
RETURN
CALCULATE(
    EngagementTable,
    FILTER(
        EngagementTable,
        YEAR(EngagementTable[Date]) = SelectedYear &&
        MONTH(EngagementTable[Date]) = SelectedMonth
    )
)
```

3. **Before each export:**
   - Set `ExportMonth` parameter to the target month (e.g., "2025-12")
   - Export data
   - Generates correct data regardless of current date

### Fix Option 2: Remove Relative Date Logic

**Replace with explicit date range:**

```dax
// BEFORE (PROBLEMATIC):
Engagement Last Month = 
CALCULATE(
    EngagementTable,
    Engagement[Date] >= EOMONTH(TODAY(), -2) + 1,
    Engagement[Date] <= EOMONTH(TODAY(), -1)
)

// AFTER (FIXED):
Engagement December 2025 = 
CALCULATE(
    EngagementTable,
    Engagement[Date] >= DATE(2025, 12, 1),
    Engagement[Date] < DATE(2026, 1, 1)
)
```

**Pros:**
- Simple and reliable
- No dependency on current date

**Cons:**
- Must manually update for each month
- Need separate report file for each month

### Fix Option 3: Use Report-Level Date Slicer

**Add a Month Slicer:**

1. **Create a Date table** if not already exists:
```dax
DateTable = 
ADDCOLUMNS(
    CALENDAR(DATE(2024, 1, 1), DATE(2026, 12, 31)),
    "Year", YEAR([Date]),
    "Month", MONTH([Date]),
    "MonthYear", FORMAT([Date], "YYYY-MM")
)
```

2. **Add a slicer to the page:**
   - Field: `MonthYear`
   - Style: Dropdown
   - Position: Top of page

3. **Remove all date filters from visual**

4. **Before exporting:**
   - Set slicer to "2025-12"
   - Export all visuals
   - Data will reflect selected month

### Fix Option 4: Power Query Date Filter Removal

If the issue is in Power Query:

```m
// BEFORE (PROBLEMATIC):
FilteredRows = Table.SelectRows(
    Source, 
    each [Date] >= Date.AddMonths(DateTime.LocalNow(), -1)
)

// AFTER (FIXED):
// Remove date filter from Power Query
// Handle filtering in DAX instead for better control
Source
```

**Note:** Power Query filters are applied during data refresh and can't be changed at report level.

---

## Testing Plan

### Test 1: Verify Fix Works
1. Apply chosen fix
2. Refresh data (if Power Query was changed)
3. Export "Engagement Initiatives by Bureau" to CSV
4. Verify CSV contains 22 events for December 2025
5. File size should be ~2-3 KB (not 83 bytes)

### Test 2: Verify Other Months
1. Change parameter/slicer to November 2025
2. Export CSV
3. Verify correct month data appears

### Test 3: Verify PDF Generation Still Works
1. Generate new PDF after fix
2. Verify page 6 still shows engagement data
3. Compare to original PDF

### Test 4: Verify All 3 .pbix Files
1. Apply fix to all 3 copies
2. Test each independently
3. Ensure consistency across all versions

---

## Prevention Measures

### For Future Reports:

1. **Avoid `TODAY()` and `NOW()` in visuals meant for export**
   - Use parameters or slicers instead
   - Document any date dependencies

2. **Create Export Validation Checklist:**
   - [ ] All visuals have data (not just headers)
   - [ ] File sizes are reasonable (> 1 KB for data visuals)
   - [ ] Month/year matches expected report period
   - [ ] Compare row counts to PDF

3. **Test Export Immediately After PDF Generation:**
   - Don't wait weeks/months to export
   - Export while date context is still fresh

4. **Document Date Filter Logic:**
   - Add comments in DAX measures
   - Note any relative date dependencies
   - Create troubleshooting guide (this document)

5. **Use Version Control for .pbix Files:**
   - Track changes to measures and filters
   - Can rollback if issues arise

---

## Related Issues

### Similar Issue: Chief's Projects & Initiatives
- Same symptoms (blank export, data in PDF)
- Same likely cause (date filter)
- Same fixes apply
- File: `2025_12_Chief Michael Antista's Projects and Initiatives.csv`

### Potentially Related: Summons Missing Months
- Different symptom (data gaps, not blank)
- Different cause (source data missing)
- Separate investigation needed
- File: `2025_12_Department-Wide Summons  Moving and Parking.csv`

---

## Status Tracking

| Date | Action | Result | Next Step |
|------|--------|--------|-----------|
| 2026-02-05 | Issue identified | 3 blank exports found | Open .pbix and investigate |
| | | | |
| | | | |

---

## Resources

### Power BI Date Functions Documentation:
- `TODAY()`: https://learn.microsoft.com/en-us/dax/today-function-dax
- `EOMONTH()`: https://learn.microsoft.com/en-us/dax/eomonth-function-dax
- Parameters: https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-what-if

### Related Documentation:
- `DECEMBER_2025_VISUAL_EXPORT_DIAGNOSTIC_REPORT.md`
- `VISUAL_EXPORT_CHECKLIST.md` (to be created)
- `POWER_BI_REPORT_INFO.md`

---

## Contact

**Issue Owner:** Officer Robert Carucci  
**Report Date:** 2026-02-05  
**Priority:** HIGH  
**Target Resolution:** Before January 2026 export

---

**Next Action:** Open Power BI Desktop and complete Step 1-7 of Troubleshooting Steps
