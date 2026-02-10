# Benchmark Power BI Fix - Complete Solution Package

**Date**: February 9, 2026  
**Issue**: Benchmark visual errors in Power BI ("can't display this visual" + measure errors)  
**Status**: ✅ Complete solution ready

---

## 📋 Executive Summary

Your Benchmark Power BI dashboard is showing errors because:
1. **Table/column names don't match DAX expectations** - DAX measures reference `___Benchmark` with 3 underscores and specific column names
2. **Missing dimension tables** - DAX expects `___DimMonth` and `___DimEventType` tables
3. **Missing required columns** - Need `MonthStart` and `Report Key` columns for measures to work

**Solution**: Replace M code queries and create dimension tables (20-30 minutes)

---

## 🎯 What's Included

### Documentation (3 files)
1. **BENCHMARK_IMPLEMENTATION_CHECKLIST_2026_02_09.md** ⭐ **START HERE**
   - Step-by-step printable checklist
   - Check boxes for each task
   - Estimated time per step
   - Troubleshooting notes section

2. **BENCHMARK_QUICK_FIX_GUIDE_2026_02_09.md**
   - Quick implementation guide
   - Common troubleshooting scenarios
   - Column name mapping reference
   - Success verification tests

3. **BENCHMARK_POWER_BI_FIX_2026_02_09.md**
   - Comprehensive diagnostic guide
   - Detailed explanation of each issue
   - Multiple solution paths
   - Advanced troubleshooting

### M Code Queries (3 files)
4. **___Benchmark_FIXED_2026_02_09.m**
   - Main data query (replaces your current query)
   - Loads all three event types
   - Adds required columns (`EventType`, `MonthStart`, `Report Key`)
   - Includes error handling

5. **___DimMonth.m**
   - Month dimension table (13 months)
   - Rolling window: Nov 2024 - Nov 2025
   - Columns: `MonthStart`, `MonthLabel`, `MonthSort`

6. **___DimEventType.m**
   - Event type dimension table (3 event types)
   - Rows: "Show of Force", "Use of Force", "Vehicle Pursuit"

### DAX Measures (existing file)
7. **scripts\_testing\benchmark_r13.dax**
   - 30+ pre-built measures
   - Key measures: `Total Incidents Rolling 13`, `Avg Incidents Per Month`
   - Support measures for visuals (subtitles, indicators, etc.)

---

## 🚀 Quick Start (20 minutes)

### Option 1: Follow Checklist (Recommended)
1. Open `docs\BENCHMARK_IMPLEMENTATION_CHECKLIST_2026_02_09.md`
2. Print or view side-by-side with Power BI
3. Check off each step as you complete it
4. Document any issues in notes section

### Option 2: Follow Quick Guide
1. Open `docs\BENCHMARK_QUICK_FIX_GUIDE_2026_02_09.md`
2. Follow 6 steps sequentially
3. Use troubleshooting section if errors occur

### Option 3: Deep Dive (if issues)
1. Open `docs\BENCHMARK_POWER_BI_FIX_2026_02_09.md`
2. Read Root Cause section
3. Follow Solution paths
4. Use diagnostic scripts

---

## 📁 File Locations

**All files in workspace**: `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\`

### Documentation
```
docs\
├── BENCHMARK_IMPLEMENTATION_CHECKLIST_2026_02_09.md  ⭐ Start here
├── BENCHMARK_QUICK_FIX_GUIDE_2026_02_09.md
└── BENCHMARK_POWER_BI_FIX_2026_02_09.md
```

### M Code Queries
```
m_code\
├── ___Benchmark_FIXED_2026_02_09.m
├── ___DimMonth.m
└── ___DimEventType.m
```

### DAX Measures
```
scripts\_testing\
└── benchmark_r13.dax
```

---

## ✅ Implementation Steps (Overview)

### Step 1: Replace Benchmark Query (5 min)
- Open Power BI → Transform Data
- Find existing Benchmark query
- Replace with code from `___Benchmark_FIXED_2026_02_09.m`
- Rename to `___Benchmark`

### Step 2: Create DimMonth Table (3 min)
- Get Data → Blank Query
- Paste code from `___DimMonth.m`
- Rename to `___DimMonth`

### Step 3: Create DimEventType Table (2 min)
- Get Data → Blank Query
- Paste code from `___DimEventType.m`
- Rename to `___DimEventType`

### Step 4: Create Relationships (3 min)
- Model View
- `___Benchmark[MonthStart]` → `___DimMonth[MonthStart]`
- `___Benchmark[EventType]` → `___DimEventType[EventType]`

### Step 5: Verify Measures (5 min)
- Check `Total Incidents Rolling 13` exists
- Check `Avg Incidents Per Month` exists
- Create if missing (from benchmark_r13.dax)

### Step 6: Test (2 min)
- Create card visual with measure
- Verify number appears (not error)

---

## 🔧 Key Requirements

### Data Source
**Path**: `C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark\`

**Structure**:
```
Benchmark\
├── show_force\
│   └── *.csv
├── use_force\
│   └── *.csv
└── vehicle_pursuit\
    └── *.csv
```

**M code automatically loads the most recent file in each folder**

### CSV Columns (Required)
Your CSV files must have these columns (names can be adjusted in M code):
- `Incident Date` - Date of incident
- `Report Number` - Unique identifier

Optional but recommended:
- `# of Officers Involved` - Number
- `# of Subjects` - Number
- Other incident details

### Power BI Tables (After Implementation)
- `___Benchmark` - Main data (3 underscores)
- `___DimMonth` - Month dimension (3 underscores)
- `___DimEventType` - Event type dimension (3 underscores)

### Relationships
- `___Benchmark[MonthStart]` → `___DimMonth[MonthStart]` (many-to-one)
- `___Benchmark[EventType]` → `___DimEventType[EventType]` (many-to-one)

---

## 🐛 Common Issues & Solutions

### Issue 1: "Column 'Incident Date' not found"
**Cause**: CSV uses different date column name  
**Fix**: Edit M code line 68 to match your CSV column name

### Issue 2: "No files found in folder"
**Cause**: Folder path incorrect or folders empty  
**Fix**: Verify folder path in M code line 18, check folders contain CSV files

### Issue 3: Measure shows "Error"
**Cause**: Column referenced in DAX doesn't exist  
**Fix**: Check column names in Data View, update DAX or M code to match

### Issue 4: Visual still shows "can't display"
**Cause**: Visual filters reference old deleted columns  
**Fix**: Remove filters with warning icons, or recreate visual

### Issue 5: Wrong number of rows in DimMonth
**Cause**: Date range in M code doesn't match your needs  
**Fix**: Edit `___DimMonth.m` line 12-13 (StartDate and MonthCount)

---

## 📊 Expected Results

### After Implementation
- ✅ `___Benchmark` table: 100-500 rows (depends on your data)
- ✅ `___DimMonth` table: 13 rows
- ✅ `___DimEventType` table: 3 rows
- ✅ Two relationships visible in Model View
- ✅ `Total Incidents Rolling 13` measure: Shows number (e.g., 245)
- ✅ `Avg Incidents Per Month` measure: Shows decimal (e.g., 18.85)
- ✅ Original visual displays without errors
- ✅ All 30+ measures work correctly

### Visual Verification
**Test with table visual** (13 months × 3 event types = 39 potential combinations):
- Should show data for months where incidents occurred
- Months with zero incidents may be blank or show "0" depending on measure

---

## 📚 Additional Resources

### M Code Documentation
- **Folder.Files()** - Lists files in folder
- **Table.SelectRows()** - Filters rows by condition
- **Table.Sort()** - Sorts by column
- **Date.StartOfMonth()** - Returns first day of month

### DAX Documentation
- **CALCULATE()** - Modifies filter context
- **DISTINCTCOUNT()** - Counts unique values
- **EOMONTH()** - Returns end of month date
- **EDATE()** - Adds/subtracts months from date

### Power BI Model Best Practices
- Use dimension tables for better performance
- Create relationships (don't use LOOKUPVALUE in every measure)
- Star schema: fact table (___Benchmark) + dimension tables (___DimMonth, ___DimEventType)

---

## 🎓 Learning Points

### Why This Fix Works

**Problem**: DAX measures couldn't find required columns/tables  
**Solution**: Create the exact table and column structure DAX expects

**Problem**: No way to filter by month or event type properly  
**Solution**: Dimension tables with relationships (star schema)

**Problem**: Measures counted incidents incorrectly  
**Solution**: Use `DISTINCTCOUNT()` on unique identifier (`Report Key`)

**Problem**: Date filtering was inefficient  
**Solution**: Add `MonthStart` column for easy month-based filtering

### Star Schema Benefits
1. **Performance** - Smaller dimension tables, faster queries
2. **Reusability** - Same dimension tables used by multiple measures
3. **Flexibility** - Easy to add new measures without changing data structure
4. **Maintainability** - Clear separation of facts (incidents) and dimensions (time, categories)

---

## 🔄 Monthly Workflow (After Fix)

### When New Benchmark Data Arrives

**Step 1**: Export from Benchmark system  
**Step 2**: Save CSVs to appropriate folders:
```
Benchmark\use_force\2026_03_use_force.csv
Benchmark\show_force\2026_03_show_force.csv
Benchmark\vehicle_pursuit\2026_03_pursuit.csv
```
**Step 3**: Open Power BI, click "Refresh"  
**Step 4**: M code automatically loads newest files  
**Step 5**: Done!

**Update DimMonth** (once at start of new month):
- Only needed if you want to add new months beyond current 13
- Edit `___DimMonth.m` to adjust StartDate or MonthCount
- Refresh query

---

## 🏆 Success Criteria

**You've successfully fixed the Benchmark dashboard when**:
1. ✅ Power BI opens without errors
2. ✅ All visuals display correctly
3. ✅ Numbers look reasonable (compare to historical if available)
4. ✅ Filters work (can slice by month and event type)
5. ✅ Date ranges are correct (shows R13: Nov 2024 - Nov 2025)
6. ✅ All three event types appear in breakdowns
7. ✅ Can refresh data successfully
8. ✅ Can publish to Power BI Service (if applicable)

---

## 📞 Support

**If you get stuck**:
1. Check `BENCHMARK_QUICK_FIX_GUIDE_2026_02_09.md` troubleshooting section
2. Review `BENCHMARK_POWER_BI_FIX_2026_02_09.md` for detailed explanations
3. Verify each step in `BENCHMARK_IMPLEMENTATION_CHECKLIST_2026_02_09.md`
4. Check Master_Automation documentation (`README.md`, `CLAUDE.md`)

**Common mistakes**:
- Forgot to rename table to exactly `___Benchmark` (3 underscores)
- CSV column names don't match M code
- Didn't create relationships in Model View
- Forgot to click "Close & Apply" after editing queries

---

## 📝 Version History

**v1.0 - February 9, 2026**
- Initial release
- Complete fix for Benchmark dashboard errors
- Documentation, M code, and implementation guides created
- Tested against simplified Benchmark directory structure

**Related Updates**:
- `BENCHMARK_CLEANUP_STRATEGY_2026_02_09.md` - Directory consolidation
- `BENCHMARK_M_CODE_IMPLEMENTATION_2026_02_09.md` - Original M code creation
- `BENCHMARK_DIRECTORY_ANALYSIS_2026_02_09.md` - Structure analysis

---

## 🎯 Next Steps

### Immediate (Today)
1. ⭐ **Follow checklist** - Start with `BENCHMARK_IMPLEMENTATION_CHECKLIST_2026_02_09.md`
2. **Implement fix** - Should take 20-30 minutes
3. **Verify** - Test with simple visuals
4. **Save** - Save Power BI file with new version number

### Short Term (This Week)
1. **Test monthly workflow** - Practice refreshing with new data
2. **Add more measures** - Explore other measures in `benchmark_r13.dax`
3. **Enhance visuals** - Add conditional formatting, better titles
4. **Document** - Add notes to Power BI report about data sources

### Long Term (Next Month)
1. **Monitor performance** - Check query refresh times
2. **Optimize** - Consider additional indexes or data reduction
3. **Expand** - Add more event details or officer-level analysis
4. **Automate** - Consider adding Benchmark to Master_Automation ETL

---

## 📄 Files Created (Summary)

**Documentation**: 4 files  
**M Code**: 3 files  
**DAX**: 1 file (existing)  
**Total**: 7 files + 1 summary

**All files ready to use** - No additional configuration needed beyond following implementation guide

---

**Last Updated**: February 9, 2026  
**Package Version**: 1.0  
**Total Estimated Implementation Time**: 20-30 minutes  
**Difficulty Level**: Moderate (copy/paste + verification)  
**Status**: ✅ Ready for implementation

---

**🎉 Good luck with your fix! The checklist has everything you need to succeed.**
