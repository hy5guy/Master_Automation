# Summons M Code Fix - Template Update

**Date:** 2026-02-13  
**Issue:** January 2026 used temporary one-off CSV queries instead of proper ETL queries  
**Solution:** Restore December's proper M code to template

---

## Problem Summary

### What Happened in January
You rushed the January report and created quick CSV-based queries instead of using the proper ETL output from `summons_powerbi_latest.xlsx`. These temporary queries:
1. Used static file paths (`00_dev\PowerBI_Date\`)
2. Had hardcoded month references (e.g., `nov2025`, `1125`)
3. Required manual CSV file creation each month
4. Bypassed the entire Summons ETL pipeline

### Impact
- Template now contains incorrect queries
- Future monthly reports will fail (looking for hardcoded November 2025 files)
- Loses all the ETL benefits (validation, formatting, backfill integration)

---

## Correct M Code (December 2025)

### Query Mapping

| Visual | Correct Query Name | Source File |
|--------|-------------------|-------------|
| 13-Month Trend | `summons_13month_trend` | `summons_powerbi_latest.xlsx` |
| All Bureaus | `summons_all_bureaus` | `summons_powerbi_latest.xlsx` |
| Top 5 Parking | `summons_top5_parking` | `summons_powerbi_latest.xlsx` |
| Top 5 Moving | `summons_top5_moving` | `summons_powerbi_latest.xlsx` |

### Temporary Queries to Remove

| Temporary Name | Should Be Replaced With |
|----------------|-------------------------|
| `___Backfill` | `summons_13month_trend` |
| `___wg3` | `summons_all_bureaus` |
| `___TopParking` | `summons_top5_parking` |
| `___TopMoving` | `summons_top5_moving` |

---

## M Code Files Created

I've created 4 M code files in `m_code/summons/` with the correct December versions:

1. **`summons_13month_trend.m`** - 13-Month Trend visual
   - Loads all columns from `summons_powerbi_latest.xlsx`
   - Filters for 13-month data window
   - Includes backfill and current month
   - Filters out UNKNOWN WG2 records

2. **`summons_all_bureaus.m`** - All Bureaus visual
   - Groups by WG2 (Bureau)
   - Gets most recent month dynamically
   - Combines OFFICE OF SPECIAL OPERATIONS → PATROL DIVISION
   - Sums Moving (M) and Parking (P) by bureau

3. **`summons_top5_parking.m`** - Top 5 Parking Leaders
   - Formats officer names (e.g., "A. LIGGIO #388")
   - Uses non-padded badge numbers
   - Dynamically gets most recent month
   - Takes top 5 by count

4. **`summons_top5_moving.m`** - Top 5 Moving Leaders
   - Same formatting as parking
   - Excludes "MULTIPLE OFFICERS" records
   - Dynamically gets most recent month
   - Takes top 5 by count

---

## How to Fix the Template

### Step 1: Backup Current Template
```powershell
Copy-Item "C:\Users\carucci_r\OneDrive - City of Hackensack\15_Templates\Monthly_Report_Template.pbix" `
          "C:\Users\carucci_r\OneDrive - City of Hackensack\15_Templates\backup\Monthly_Report_Template_2026_02_13_BEFORE_FIX.pbix"
```

### Step 2: Open Template in Power BI Desktop
1. Open `15_Templates\Monthly_Report_Template.pbix`
2. Go to **Transform Data** (Power Query Editor)

### Step 3: Delete Temporary Queries
Delete these queries:
- ❌ `___Backfill`
- ❌ `___wg3`
- ❌ `___TopParking`
- ❌ `___TopMoving`

### Step 4: Update/Create Proper Queries

For each of the 4 summons queries:

#### A. If Query Exists (e.g., `summons_13month_trend`)
1. Right-click query → Advanced Editor
2. Copy M code from `m_code\summons\summons_13month_trend.m`
3. Paste, click Done
4. Refresh preview to verify

#### B. If Query Missing
1. Click **New Source** → **Blank Query**
2. Right-click "Query1" → Advanced Editor
3. Paste M code from corresponding `.m` file
4. Rename query to correct name

### Step 5: Update Visuals
If any visuals reference the old temporary queries:
1. Select visual
2. In **Fields** pane, change data source:
   - `___Backfill` → `summons_13month_trend`
   - `___wg3` → `summons_all_bureaus`
   - `___TopParking` → `summons_top5_parking`
   - `___TopMoving` → `summons_top5_moving`

### Step 6: Verify and Save
1. Click **Close & Apply**
2. Refresh all data (Ctrl+R or Refresh button)
3. Verify all 4 summons visuals show correct data
4. Save template

---

## Verification Checklist

After updating template, verify:

- [ ] `summons_13month_trend` query exists and loads from `summons_powerbi_latest.xlsx`
- [ ] `summons_all_bureaus` query exists and loads from `summons_powerbi_latest.xlsx`
- [ ] `summons_top5_parking` query exists and loads from `summons_powerbi_latest.xlsx`
- [ ] `summons_top5_moving` query exists and loads from `summons_powerbi_latest.xlsx`
- [ ] All temporary queries (`___Backfill`, `___wg3`, etc.) are deleted
- [ ] All visuals reference correct query names
- [ ] Data refreshes without errors
- [ ] Visual outputs match expected values

---

## Benefits of Fix

### Before (January - Temporary)
- ❌ Hardcoded file paths (`wg2_movers_parkers_nov2025.csv`)
- ❌ Manual CSV creation required
- ❌ No ETL validation
- ❌ Static month references
- ❌ Bypasses entire Summons pipeline

### After (Fixed - Using ETL)
- ✅ Dynamic data from ETL output
- ✅ Automatic monthly updates
- ✅ Full ETL validation and formatting
- ✅ Backfill integration
- ✅ Officer name formatting
- ✅ Bureau consolidation (OSO → Patrol)
- ✅ Proper 13-month window
- ✅ Works with entire Master Automation pipeline

---

## Testing After Fix

### 1. Test Current Month (January 2026)
```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
.\scripts\run_all_etl.ps1
```

Then open template and refresh - should show January 2026 data

### 2. Test February 2026 (Next Month)
When February data is ready:
1. Run ETL
2. Open template from `15_Templates\`
3. Refresh → Should automatically show February data
4. No manual CSV creation needed!

---

## Files Created

1. `m_code\summons\summons_13month_trend.m` - 13-month trend query
2. `m_code\summons\summons_all_bureaus.m` - All bureaus query
3. `m_code\summons\summons_top5_parking.m` - Top 5 parking query
4. `m_code\summons\summons_top5_moving.m` - Top 5 moving query

---

## Next Steps

1. ✅ M code files created in `m_code\summons\`
2. ⏳ **YOU:** Backup current template
3. ⏳ **YOU:** Open template in Power BI Desktop
4. ⏳ **YOU:** Delete temporary queries (`___Backfill`, `___wg3`, etc.)
5. ⏳ **YOU:** Update queries with correct M code
6. ⏳ **YOU:** Update visual references
7. ⏳ **YOU:** Test refresh
8. ⏳ **YOU:** Save template

---

*Documentation created: 2026-02-13*
