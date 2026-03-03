# Power BI Visual Fix Guide

## Issues Found:
1. `TICKET_COUNT` field doesn't exist in `___Summons` table
2. `Officer` and `Summons Count` fields have issues in Top 5 queries
3. Old field references cached in visuals

## Step-by-Step Fix:

### Step 1: Update All M Code Queries
1. Open Power Query Editor (Home → Transform Data)
2. For each query (`___Summons`, `___Top_5_Moving_Violations`, `___Top_5_Parking_Violations`):
   - Click on the query
   - Click "Advanced Editor" 
   - Replace ALL code with the updated M code from the files:
     - `___Summons.m`
     - `top_5_moving.m`
     - `Top_5_parking.m`
   - Click "Done"
   - Click "Close & Apply"

### Step 2: Remove Broken Relationships
1. Go to **Model** view (left sidebar)
2. Look for any relationships involving:
   - `TICKET_COUNT`
   - `ASSIGNMENT_FOUND`
3. **Delete** any relationships that reference these fields
4. If you see a relationship using `TICKET_NUMBER` as a key, consider removing it (duplicate values issue)

### Step 3: Delete Broken Measures/Calculated Columns
1. In **Fields** pane (right side), expand each table
2. Look for any **measures** or **calculated columns** that reference:
   - `TICKET_COUNT`
   - `ASSIGNMENT_FOUND`
3. Right-click → **Delete** each one

### Step 4: Fix Visuals Manually
For each visual showing errors:

1. **Click on the visual** that has the error
2. In the **Visualizations** pane, check the **Fields** section
3. **Remove** any fields that show errors (red X or warning icon):
   - Remove `TICKET_COUNT` if present
   - Remove `ASSIGNMENT_FOUND` if present
4. **Re-add** the correct fields:
   - For Top 5 Moving: Use `Officer`, `Bureau`, `Summons Count` from `___Top_5_Moving_Violations`
   - For Top 5 Parking: Use `Officer`, `Bureau`, `Summons Count` from `___Top_5_Parking_Violations`
   - For other visuals: Use fields from `___Summons` (avoid `TICKET_COUNT` and `ASSIGNMENT_FOUND`)

### Step 5: Refresh All Queries
1. Right-click on each query in the **Fields** pane
2. Select **Refresh**
3. Or use **Home → Refresh All**

### Step 6: Verify Query Outputs
After refreshing, verify each query has the correct columns:

**___Summons** should have:
- `PADDED_BADGE_NUMBER`, `OFFICER_DISPLAY_NAME`, `WG2`, `TYPE`, etc.
- **NO** `TICKET_COUNT` or `ASSIGNMENT_FOUND`

**___Top_5_Moving_Violations** should have:
- `Rank`, `Officer`, `Bureau`, `Summons Count`

**___Top_5_Parking_Violations** should have:
- `Rank`, `Officer`, `Bureau`, `Summons Count`

## Quick Fix Alternative:
If visuals are too broken, you can:
1. Delete the broken visuals
2. Recreate them using the correct fields from the refreshed queries

## Expected Column Names:

### ___Summons Table:
- `PADDED_BADGE_NUMBER` (text)
- `OFFICER_DISPLAY_NAME` (text)
- `WG2` (text) - **Now populated!**
- `TYPE` (text) - "M", "P", "C", etc.
- `TICKET_NUMBER` (text)
- `ISSUE_DATE` (datetime)
- `Year`, `Month`, `YearMonthKey`, `Month_Year`
- **NO** `TICKET_COUNT`
- **NO** `ASSIGNMENT_FOUND`

### ___Top_5_Moving_Violations Table:
- `Rank` (number)
- `Officer` (text)
- `Bureau` (text)
- `Summons Count` (number)

### ___Top_5_Parking_Violations Table:
- `Rank` (number)
- `Officer` (text)
- `Bureau` (text)
- `Summons Count` (number)

