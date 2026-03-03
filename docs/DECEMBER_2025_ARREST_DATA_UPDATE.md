# December 2025 Arrest Data Update - January 5, 2026

## ✅ Status Update

### December 2025 Data Available
- **Source File:** `C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Arrest\monthly_export\2025\2025_12_LAWSOFT_ARREST.xlsx`
- **Status:** ✅ File exists and is ready for processing

### Power BI Ready Files
- **Directory:** `C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\ARREST_DATA\Power_BI`
- **Latest File:** `2025_11_Arrests_PowerBI_Ready.xlsx` (November 2025)
- **December File:** ⏳ **Not yet created** - ETL script needs to process December source file

---

## 🔄 Changes Made

### 1. Updated M Code Queries

Both queries now use **previous month logic** to automatically target December 2025:

#### `___Top_5_Arrests_FIXED.m`
```m
// Calculate previous month (December 2025 from January 2026)
Current = Date.From(DateTime.LocalNow()),
PreviousMonth = Date.AddMonths(Current, -1),
TargetYear = Date.Year(PreviousMonth),
TargetMonth = Date.Month(PreviousMonth),
MonthYearDisplay = Date.MonthName(PreviousMonth) & " " & Text.From(TargetYear),
```

#### `___Arrest_Categories_FIXED.m`
```m
// Calculate previous month (December 2025 from January 2026)
Prev = Date.AddMonths(Date.From(DateTime.LocalNow()), -1),
PrevY = Date.Year(Prev),
PrevM = Date.Month(Prev),
```

### 2. Enhanced Date Parsing

Both queries now handle Excel serial dates correctly:
- ✅ Excel serial numbers (45962, 45963, etc.)
- ✅ Actual date values
- ✅ Text date strings

---

## 📋 Next Steps

### Step 1: Run ETL Script to Process December Data

**Action Required:** Run the arrest ETL script to process the December 2025 file:

```powershell
# Run the main ETL orchestrator (processes all scripts including Arrests)
.\scripts\run_all_etl.ps1
```

**OR** run the arrest script directly:
```powershell
# Navigate to arrest script directory
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Arrests"

# Run the processor
python arrest_python_processor.py
```

**Expected Output:**
- File created: `C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\ARREST_DATA\Power_BI\2025_12_Arrests_PowerBI_Ready.xlsx`

### Step 2: Update Power BI Queries

1. **Copy updated M code** from:
   - `m_code/___Top_5_Arrests_FIXED.m`
   - `m_code/___Arrest_Categories_FIXED.m`

2. **Paste into Power BI:**
   - Open Power BI Desktop
   - Go to Power Query Editor
   - Update the `___Top_5_Arrests` query
   - Update the `___Arrest_Categories` query

3. **Refresh queries:**
   - Click "Refresh" in Power Query Editor
   - Verify queries load December 2025 data

### Step 3: Verify Results

After refreshing:
- ✅ `___Top_5_Arrests` should show top 5 officers from **December 2025**
- ✅ `___Arrest_Categories` should show all December 2025 arrests with categories
- ✅ Date filtering should work correctly
- ✅ No empty tables

---

## 🔍 File Locations Summary

### Source Files (Raw Data)
```
C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Arrest\monthly_export\2025\
├── 2025_12_LAWSOFT_ARREST.xlsx  ✅ EXISTS
└── 2025_11_LAWSOFT_ARREST.xlsx  (previous month)
```

### Processed Files (Power BI Ready)
```
C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\ARREST_DATA\Power_BI\
├── 2025_12_Arrests_PowerBI_Ready.xlsx  ⏳ TO BE CREATED
└── 2025_11_Arrests_PowerBI_Ready.xlsx  ✅ EXISTS
```

### M Code Queries
```
m_code\
├── ___Top_5_Arrests_FIXED.m      ✅ UPDATED (uses previous month logic)
└── ___Arrest_Categories_FIXED.m  ✅ UPDATED (uses previous month logic)
```

---

## 🎯 Expected Behavior

### Automatic Month Detection
The queries now automatically:
1. Calculate previous month from current date (January 2026 → December 2025)
2. Load the latest PowerBI_Ready file from the directory
3. Filter to the target month (December 2025)
4. Display results

### Future Months
When January 2026 data becomes available:
- Queries will automatically target January 2026 (previous month from February 2026)
- No manual updates needed!

---

## ✅ Verification Checklist

After running ETL and updating Power BI:

- [ ] December 2025 PowerBI_Ready file exists
- [ ] Power BI queries updated with new M code
- [ ] Queries refresh without errors
- [ ] `___Top_5_Arrests` shows December 2025 data
- [ ] `___Arrest_Categories` shows December 2025 data
- [ ] Date filtering works correctly
- [ ] No empty tables

---

**Status:** ✅ **Queries Updated - Ready for ETL Processing**
