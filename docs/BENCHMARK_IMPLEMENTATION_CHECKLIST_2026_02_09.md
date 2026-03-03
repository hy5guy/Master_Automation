# Benchmark Power BI Fix - Implementation Checklist

**Date**: February 9, 2026  
**Print this page and check off each step as you complete it**

---

## ✅ Pre-Implementation

- [ ] Power BI Desktop is open
- [ ] Benchmark report is loaded
- [ ] Files are ready:
  - [ ] `m_code\___Benchmark_FIXED_2026_02_09.m`
  - [ ] `m_code\___DimMonth.m`
  - [ ] `m_code\___DimEventType.m`
  - [ ] `scripts\_testing\benchmark_r13.dax`

---

## ✅ Step 1: Replace Main Benchmark Query (5 min)

- [ ] Home → Transform Data
- [ ] Found existing Benchmark query
- [ ] Right-click → Advanced Editor
- [ ] **Deleted all existing code**
- [ ] Opened `m_code\___Benchmark_FIXED_2026_02_09.m`
- [ ] **Copied entire file contents**
- [ ] **Pasted into Advanced Editor**
- [ ] Clicked "Done"
- [ ] Preview shows data (no errors)
- [ ] Right-click query name → Rename
- [ ] Renamed to: `___Benchmark` (3 underscores)

**Troubleshooting** (if preview shows errors):
- [ ] Error says "Column not found"? → Note column name error
- [ ] Error says "File not found"? → Verify folder path
- [ ] Fixed column name in M code (line 68 or 73)
- [ ] Fixed folder path in M code (line 18)
- [ ] Preview now shows data ✅

---

## ✅ Step 2: Create Month Dimension (3 min)

- [ ] Home → Get Data → Blank Query
- [ ] Home → Advanced Editor
- [ ] Opened `m_code\___DimMonth.m`
- [ ] **Copied entire file contents**
- [ ] **Pasted into Advanced Editor**
- [ ] Clicked "Done"
- [ ] Preview shows 13 rows ✅
- [ ] Right-click query name → Rename
- [ ] Renamed to: `___DimMonth` (3 underscores)

**Verify columns**:
- [ ] `MonthStart` column exists (date type)
- [ ] `MonthLabel` column exists (text: "11-24", "12-24", etc.)
- [ ] `MonthSort` column exists (number: 202411, 202412, etc.)

---

## ✅ Step 3: Create Event Type Dimension (2 min)

- [ ] Home → Get Data → Blank Query
- [ ] Home → Advanced Editor
- [ ] Opened `m_code\___DimEventType.m`
- [ ] **Copied entire file contents**
- [ ] **Pasted into Advanced Editor**
- [ ] Clicked "Done"
- [ ] Preview shows 3 rows ✅
- [ ] Right-click query name → Rename
- [ ] Renamed to: `___DimEventType` (3 underscores)

**Verify rows**:
- [ ] Row 1: "Show of Force"
- [ ] Row 2: "Use of Force"
- [ ] Row 3: "Vehicle Pursuit"

---

## ✅ Step 4: Apply Changes (1 min)

- [ ] Clicked "Close & Apply" (bottom left)
- [ ] Waited for data to refresh (may take 30-60 seconds)
- [ ] Refresh completed without errors ✅

---

## ✅ Step 5: Create Relationships (3 min)

- [ ] Clicked **Model View** (left sidebar icon)
- [ ] Can see three tables: `___Benchmark`, `___DimMonth`, `___DimEventType`

**Relationship 1**: Benchmark → DimMonth
- [ ] Dragged `___Benchmark[MonthStart]` to `___DimMonth[MonthStart]`
- [ ] Relationship dialog appeared
- [ ] Cardinality: **Many to One (*)** ✅
- [ ] Cross filter direction: **Single** ✅
- [ ] Clicked "OK"
- [ ] Line appeared connecting the two tables ✅

**Relationship 2**: Benchmark → DimEventType
- [ ] Dragged `___Benchmark[EventType]` to `___DimEventType[EventType]`
- [ ] Relationship dialog appeared
- [ ] Cardinality: **Many to One (*)** ✅
- [ ] Cross filter direction: **Single** ✅
- [ ] Clicked "OK"
- [ ] Line appeared connecting the two tables ✅

---

## ✅ Step 6: Verify/Fix Measures (5 min)

- [ ] Clicked **Report View** (left sidebar)
- [ ] Opened Fields pane (right side)
- [ ] Expanded `___Benchmark` table

**Check Measure 1**: Total Incidents Rolling 13
- [ ] Measure exists in Fields pane
- [ ] OR measure needs to be created:
  - [ ] Selected `___Benchmark` table
  - [ ] Home → New Measure
  - [ ] Opened `scripts\_testing\benchmark_r13.dax`
  - [ ] Found `Total Incidents Rolling 13 =` (line 322)
  - [ ] Copied lines 322-330
  - [ ] Pasted into formula bar
  - [ ] Pressed Enter
  - [ ] No errors in formula bar ✅

**Check Measure 2**: Avg Incidents Per Month
- [ ] Measure exists in Fields pane
- [ ] OR measure needs to be created:
  - [ ] Selected `___Benchmark` table
  - [ ] Home → New Measure
  - [ ] Opened `scripts\_testing\benchmark_r13.dax`
  - [ ] Found `Avg Incidents Per Month =` (line 1)
  - [ ] Copied lines 1-6
  - [ ] Pasted into formula bar
  - [ ] Pressed Enter
  - [ ] No errors in formula bar ✅

---

## ✅ Step 7: Test with Simple Visual (2 min)

- [ ] Created new page (+ at bottom)
- [ ] Inserted **Card** visual
- [ ] Added field: `Total Incidents Rolling 13` measure
- [ ] Card shows a NUMBER (not error) ✅
- [ ] **Record the number**: _______________

- [ ] Inserted **Table** visual
- [ ] Added row: `___DimMonth[MonthLabel]`
- [ ] Added row: `___DimEventType[EventType]`
- [ ] Added values: `Total Incidents Rolling 13` measure
- [ ] Table shows 13-39 rows ✅
- [ ] All numbers look reasonable ✅

---

## ✅ Step 8: Fix Original Visual (3 min)

- [ ] Navigated back to original Benchmark page
- [ ] Found the visual that was showing error
- [ ] Visual now displays correctly ✅
  - [ ] OR still shows error → Continue below

**If still showing error**:
- [ ] Clicked on visual
- [ ] Visualizations pane → Filters
- [ ] Found filters with ⚠️ warning icon
- [ ] Removed all warning filters
- [ ] Visual now works ✅
  - [ ] OR deleted visual and recreated

---

## ✅ Step 9: Verify All Measures Work (Optional - 5 min)

Go through each measure in `benchmark_r13.dax` and verify:

**Core Counting Measures**:
- [ ] `IncidentCount` - shows number
- [ ] `IncidentCount_13Month` - shows number
- [ ] `Total Incidents Rolling 13` - shows number
- [ ] `Avg Incidents Per Month` - shows decimal

**Month-over-Month Measures**:
- [ ] `BM MoM Change` - shows number (can be negative)
- [ ] `BM MoM Change %` - shows percentage

**Year-over-Year Measures**:
- [ ] `BM YoY Change` - shows percentage

**Visual Support Measures**:
- [ ] `Donut Subtitle` - shows text with date range
- [ ] `Line Chart Subtitle` - shows text with date range
- [ ] `Matrix Subtitle` - shows text with date range

---

## ✅ Step 10: Save & Publish (2 min)

- [ ] File → Save
- [ ] Saved as: `Benchmark_Dashboard_v2026_02_09.pbix` (or similar)
- [ ] File → Publish (if publishing to Power BI Service)
- [ ] Verified published report shows no errors

---

## ✅ Final Verification

- [ ] **ALL visuals display correctly** (no "can't display" errors)
- [ ] **Numbers look reasonable** (compare to old dashboard if available)
- [ ] **Date ranges are correct** (Nov 2024 - Nov 2025 for R13)
- [ ] **All three event types appear** in breakdowns
- [ ] **Filters work correctly** (can slice by month, event type)
- [ ] **Saved successfully**

---

## 🎉 Success Criteria

**You're done when ALL these are true**:
- ✅ Three tables exist: `___Benchmark`, `___DimMonth`, `___DimEventType`
- ✅ Two relationships created (visible in Model View)
- ✅ Key measures work: `Total Incidents Rolling 13`, `Avg Incidents Per Month`
- ✅ Original visual displays without errors
- ✅ Test visuals show reasonable numbers
- ✅ File saved

---

## 📝 Notes / Issues Encountered

**Column name mappings needed**:
- `Incident Date` → `_______________________`
- `Report Number` → `_______________________`

**Other issues**:
```
_______________________________________________________________

_______________________________________________________________

_______________________________________________________________

_______________________________________________________________
```

---

## 📞 If Still Having Issues

**Check these files**:
1. `docs\BENCHMARK_POWER_BI_FIX_2026_02_09.md` - Detailed troubleshooting
2. `docs\BENCHMARK_QUICK_FIX_GUIDE_2026_02_09.md` - Implementation guide

**Common problems**:
- Column names in CSV don't match M code → Update M code lines 68, 73
- Folder path wrong → Update M code line 18
- Relationships not created → Delete and recreate in Model View
- Measure errors → Check column names match your table

---

**Completion Date**: ____________  
**Time Taken**: ____________  
**Final Status**: ⬜ Success ⬜ Partial ⬜ Failed (notes above)

---

**Last Updated**: February 9, 2026  
**Total Estimated Time**: 20-30 minutes
