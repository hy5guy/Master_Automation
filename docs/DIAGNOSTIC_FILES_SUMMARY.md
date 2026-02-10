# Diagnostic M Code Files - Summary

**Date:** January 5, 2026  
**Purpose:** Diagnostic queries to troubleshoot empty results in arrest queries

---

## 📁 File Locations

### M Code Files
All diagnostic M code files are located in: `m_code/`

### Documentation
Diagnostic instructions: `docs/DIAGNOSTIC_INSTRUCTIONS.md`

---

## 🔍 Diagnostic Queries (Run in Order)

### 1. `___Top_5_Arrests_DIAGNOSTIC.m`
**Purpose:** Shows diagnostic information about file loading and filtering

**What it displays:**
- Latest PowerBI_Ready file name
- File modification date
- Total files found
- Total rows in source (before filtering)
- Column names in the data
- Target year and month being searched
- **Rows after date filter** ← KEY METRIC

**Use this to:**
- Verify source file is loading
- See if data exists before date filtering
- Check what month the query is targeting

---

### 2. `___Arrest_Date_Distribution.m`
**Purpose:** Shows what arrest dates are actually in the source data

**What it displays:**
- Count of arrests by Month/Year
- Sorted with most recent first
- Shows "Invalid Date" entries if any

**Use this to:**
- See what months have arrest data
- Identify the most recent month with data
- Check for date parsing issues

---

### 3. `___Arrest_Raw_Data_Preview.m`
**Purpose:** Shows first 100 rows of raw data

**What it displays:**
- First 100 rows from source file
- All columns as they appear in Excel
- Source file name

**Use this to:**
- Verify data is actually loading
- Check date format in "Arrest Date" column
- Check officer names format
- Verify column names match expectations

---

### 4. `___Top_5_Arrests_ALL_TIME.m`
**Purpose:** Top 5 officers for ALL TIME (no date filter)

**What it displays:**
- Top 5 officers by arrest count
- All time data (no month filter)

**Use this to:**
- Test if query logic works without date filter
- If this shows data → Date filter is the issue
- If this is empty too → Problem is in file loading or officer column

---

## 🎯 How to Use

1. **Load all 4 diagnostic queries** into Power BI
2. **Run them in order** (1-4)
3. **Take screenshots** of the results
4. **Share results** to identify the root cause

---

## 📊 Expected Findings

### Scenario 1: No December 2024 Data
- **Finding:** Date Distribution shows no Dec 2024 arrests
- **Solution:** Change target month to most recent month with data

### Scenario 2: Source File is Empty
- **Finding:** "Total Rows in Source" = 0
- **Solution:** Check if PowerBI_Ready Excel file has data

### Scenario 3: Column Name Mismatch
- **Finding:** Columns don't match expected names
- **Solution:** Update column name handling in query

### Scenario 4: Date Format Issue
- **Finding:** Date Distribution shows "Invalid Date" entries
- **Solution:** Update ToDate function to handle additional formats

---

## ✅ Files Status

All diagnostic files have been:
- ✅ Reviewed for syntax errors
- ✅ Fixed (nullable date type in diagnostic query)
- ✅ Copied to `m_code/` directory
- ✅ Ready for use in Power BI

---

## 📝 Next Steps

1. Load diagnostic queries into Power BI
2. Run them and review results
3. Share findings to get targeted fix
4. Update main queries based on diagnostic results

---

**See also:** `docs/DIAGNOSTIC_INSTRUCTIONS.md` for detailed step-by-step instructions
