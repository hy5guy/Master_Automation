# 🔍 Arrest Queries Diagnostic Guide
**Date:** 2025-01-05
**Issue:** Both queries load successfully but show no data in preview

---

## 📊 Problem Summary

Your queries compile without errors but return **ZERO rows**. This means:
- ✅ Syntax is correct
- ✅ File paths are accessible
- ❌ **Data is being filtered out somewhere**

Most likely cause: **No arrests for December 2024** (the previous month filter)

---

## 🛠️ Diagnostic Steps - Run These Queries in Order

### **Step 1: Check Source File & Columns**
**Query:** `___Top_5_Arrests_DIAGNOSTIC.m`

**What it shows:**
- Latest PowerBI_Ready file name
- File modification date
- Total files found
- **Total rows BEFORE filtering**
- Column names in the data
- Target month being searched (Dec 2024)
- **Rows AFTER date filter** ← KEY METRIC

**What to look for:**
- If "Total Rows in Source" = 0 → Source file is empty
- If "Rows After Date Filter" = 0 → No December 2024 arrests
- Check if column names match expected format

---

### **Step 2: See What Dates Are Actually Available**
**Query:** `___Arrest_Date_Distribution.m`

**What it shows:**
- Count of arrests by Month/Year
- Sorted with most recent first

**What to look for:**
- Do you have December 2024 arrests?
- What's the most recent month with data?
- Are there any Invalid Date entries?

---

### **Step 3: View Raw Data**
**Query:** `___Arrest_Raw_Data_Preview.m`

**What it shows:**
- First 100 rows of actual source data
- All columns as they appear in Excel

**What to look for:**
- Verify data is actually loading
- Check date format in "Arrest Date" column
- Check officer names format

---

### **Step 4: Test Without Date Filter**
**Query:** `___Top_5_Arrests_ALL_TIME.m`

**What it shows:**
- Top 5 officers for ALL TIME (no month filter)

**What to look for:**
- If this shows data → Date filter is the issue
- If this is empty too → Problem is in file loading or officer column

---

## 🎯 Expected Findings & Solutions

### **Scenario 1: No December 2024 Data**
**Finding:** Date Distribution shows no Dec 2024 arrests

**Solutions:**
1. **Wait for December data to be added** to PowerBI_Ready file
2. **Change target month** in queries to use the most recent month that HAS data
3. **Manually specify a month** instead of using "previous month" logic

**Quick Fix - Change to Specific Month:**
```m
// Instead of:
PreviousMonth = Date.AddMonths(Current, -1),

// Use specific month:
TargetYear = 2024,
TargetMonth = 11,  // November 2024
MonthYearDisplay = "November 2024",
```

---

### **Scenario 2: Source File is Empty**
**Finding:** "Total Rows in Source" = 0

**Solutions:**
1. Check if PowerBI_Ready Excel file has data
2. Verify Python preprocessing script ran successfully
3. Check if source folder path is correct

---

### **Scenario 3: Column Name Mismatch**
**Finding:** Columns in Data shows different names than expected

**Solutions:**
1. Update column name handling in query
2. Add additional fallback column names
3. Verify Python script is creating correct column headers

---

### **Scenario 4: Date Format Issue**
**Finding:** Date Distribution shows "Invalid Date" entries

**Solutions:**
1. Check date format in Excel source
2. Update ToDate function to handle additional formats
3. Verify dates are recognized by Excel as dates (not text)

---

## 📝 Next Steps After Diagnostics

**When you run these queries, send me:**

1. Screenshot of `___Top_5_Arrests_DIAGNOSTIC` results
2. Screenshot of `___Arrest_Date_Distribution` results
3. Latest month that shows arrests in the distribution

**I'll then provide:**
- Exact fix based on your data
- Updated queries targeting the correct month
- Any necessary date parsing adjustments

---

## 🔧 Quick Temporary Fix

**If you need data NOW and can't wait for December:**

Replace this section in both original queries:
```m
// CURRENT (looks for previous month):
Current = Date.From(DateTime.LocalNow()),
PreviousMonth = Date.AddMonths(Current, -1),
TargetYear = Date.Year(PreviousMonth),
TargetMonth = Date.Month(PreviousMonth),
```

**With this (looks for November 2024):**
```m
// TEMPORARY FIX - Hardcode to November 2024:
TargetYear = 2024,
TargetMonth = 11,
MonthYearDisplay = "November 2024",
```

This will show November 2024 data if it exists.

---

## 📞 Support

After running diagnostics, share the results and I'll:
- Identify exact root cause
- Provide targeted fix
- Update queries to work with your data

**Remember:** Empty preview ≠ broken query. It means no data matches your filter criteria!
