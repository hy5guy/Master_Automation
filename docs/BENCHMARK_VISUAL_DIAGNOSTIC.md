# BENCHMARK VISUALS DIAGNOSTIC GUIDE

🕒 2026-02-14
## 🚨 PROBLEM SUMMARY

**What's Working:**
- M code queries load without errors
- Relationships appear correct in model diagram
- January 2025 shows data (405 total incidents)

**What's Broken:**
- Feb 2025 - Jan 2026 all show 0 in matrix visual
- Donut chart empty
- Line chart flat at zero

---

## 🔍 DIAGNOSTIC STEPS (Run in Order)

### **STEP 1: Verify Source Data Coverage**

**Goal:** Confirm the CSV/XLSX files actually contain data beyond January 2025

**Actions:**
1. Open File Explorer → Navigate to:
   ```
   C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark\
   ```

2. Check each subdirectory:
   - `use_force\`
   - `show_force\`
   - `vehicle_pursuit\`

3. Open the latest CSV/XLSX file in each folder

4. **Check the "Incident Date" column range:**
   - Does data exist beyond January 2025?
   - What's the actual date range (earliest → latest)?

**Expected Result:**
- Files should contain incidents from Jan 2025 through recent months
- If files ONLY contain Jan 2025 → **ROOT CAUSE FOUND** (data gap issue)

**If Data Exists Beyond Jan 2025:** → Continue to Step 2

---

### **STEP 2: Validate ___Benchmark Query Date Loading**

**Goal:** Confirm the M code is actually loading all dates from source files

**Actions:**
1. Open Power BI Desktop
2. Go to **Transform Data** (Power Query Editor)
3. Click on **___Benchmark** query
4. Look at the **Incident Date** column
5. Click column header → **Column Tools** → **Column Statistics** (or right-click → **Column Distribution**)

**Check:**
- What's the MIN date shown?
- What's the MAX date shown?
- Does the distribution show dates beyond Jan 2025?

**Expected Result:**
- Should see dates spanning Jan 2025 → Jan 2026 (or current month)
- If you ONLY see Jan 2025 → M code `LoadLatestFile` function may be filtering incorrectly

**If Dates Look Correct:** → Continue to Step 3

---

### **STEP 3: Verify MonthStart Calculation**

**Goal:** Ensure MonthStart field is calculating correctly from Incident Date

**Actions:**
1. In Power Query Editor, still viewing **___Benchmark** query
2. Scroll right to find the **MonthStart** column
3. Check a few rows of data:

**Example Check:**
| Incident Date | MonthStart | Should Be |
|--------------|------------|-----------|
| 2025-01-15 | 2025-01-01 | 2025-01-01 ✅ |
| 2025-02-10 | 2025-02-01 | 2025-02-01 ✅ |
| 2025-03-05 | 2025-03-01 | 2025-03-01 ✅ |

**Check for Issues:**
- Are all MonthStart values showing as `2025-01-01` regardless of Incident Date? → **CALCULATION ERROR**
- Are some MonthStart values `null`? → **TYPE CONVERSION ISSUE**
- Do MonthStart values vary correctly? → ✅ Calculation is working

**If MonthStart Looks Correct:** → Continue to Step 4

---

### **STEP 4: Check ___DimMonth Window**

**Goal:** Verify the month dimension table covers the full 13-month period

**Actions:**
1. In Power Query Editor, click on **___DimMonth** query
2. Check the rows:

**Expected Rows (as of Feb 2026):**
| MonthStart | MonthLabel | MonthSort |
|------------|------------|-----------|
| 2025-01-01 | 01-25 | 202501 |
| 2025-02-01 | 02-25 | 202502 |
| 2025-03-01 | 03-25 | 202503 |
| ... | ... | ... |
| 2026-01-01 | 01-26 | 202601 |

**Check:**
- Should have exactly **13 rows** (last full month was Jan 2026)
- FirstMonthStart should be 2025-01-01
- LastFullMonth should be 2026-01-31

**If Row Count is Wrong:**
- Review the `LastFullMonth` and `FirstMonthStart` calculation in M code
- The `Date.AddMonths(DateTime.LocalNow(), -1)` might be calculating incorrectly

**If Rows Look Correct:** → Continue to Step 5

---

### **STEP 5: Verify Relationship in Model**

**Goal:** Ensure the relationship between tables is active and correct

**Actions:**
1. Close Power Query Editor (Close & Apply if you made changes)
2. Go to **Model View** (left sidebar icon)
3. Find the relationship line between:
   - `___Benchmark[MonthStart]` ↔ `___DimMonth[MonthStart]`

**Check:**
- Is the line solid (active) or dotted (inactive)?
- Does it show `1` on DimMonth side and `*` on Benchmark side?
- Are both fields type **date**?

**Test Relationship:**
- Right-click relationship → **Properties**
- Confirm:
  - Cross filter direction: Single
  - Make this relationship active: ✅ Checked
  - Cardinality: One to Many (1:*)

**If Relationship is Missing/Broken:** → **ROOT CAUSE FOUND**

---

### **STEP 6: Check Visual Field Mappings**

**Goal:** Verify the matrix visual is using the correct fields

**Actions:**
1. Click on the **Use of Force Incident Matrix** visual
2. Look at the **Fields** pane (right side)

**Expected Configuration:**
- **Rows:** `___DimMonth[MonthLabel]` or `___Benchmark[MonthLabel]`
- **Columns:** `___Benchmark[EventType]` or `___DimEventType[EventType]`
- **Values:** Count of rows or a measure counting incidents

**Common Issues:**
- Using wrong MonthLabel field (from wrong table)
- Using a measure that has a hidden filter
- Visual-level filter accidentally applied

---

### **STEP 7: Test with Simple DAX Measure**

**Goal:** Isolate whether the issue is data or DAX

**Actions:**
1. Create a new measure:
   ```dax
   Test Total Incidents = COUNTROWS(___Benchmark)
   ```

2. Create a simple table visual:
   - Rows: `___DimMonth[MonthLabel]`
   - Values: `[Test Total Incidents]`

**Expected Result:**
- Should see counts for multiple months
- If STILL only Jan 2025 shows counts → **DATA/RELATIONSHIP ISSUE**
- If multiple months show counts → **ORIGINAL MEASURE/VISUAL ISSUE**

---

## 🎯 MOST LIKELY ROOT CAUSES (Ranked)

### **1. Source Data Only Contains January 2025** ⭐⭐⭐⭐⭐
**Probability:** 70%

**Symptoms:**
- Step 1 reveals files only have Jan 2025 data
- No data exports happened for Feb-Dec

**Fix:**
- Export data for missing months from source system
- Add CSV/XLSX files to appropriate folders

---

### **2. MonthStart Calculation Error** ⭐⭐⭐
**Probability:** 15%

**Symptoms:**
- Step 3 shows all MonthStart values as `2025-01-01`
- `Date.StartOfMonth()` function failing for non-Jan dates

**Fix:**
```m
// Current code (line in ___Benchmark):
AddMonthStart = Table.AddColumn(IncidentDateTyped, "MonthStart", 
    each Date.StartOfMonth(Date.From([Incident Date])), type date),

// Enhanced with error handling:
AddMonthStart = Table.AddColumn(IncidentDateTyped, "MonthStart", 
    each try Date.StartOfMonth(Date.From([Incident Date])) 
         otherwise null, 
    type date),
```

---

### **3. Date Type Mismatch in Relationship** ⭐⭐
**Probability:** 10%

**Symptoms:**
- Step 5 shows relationship exists but data doesn't flow
- One table has dates, other has datetime or text

**Fix:**
1. Delete existing relationship
2. Ensure both `MonthStart` columns are type **date** (not datetime)
3. Recreate relationship

---

### **4. ___DimMonth Window Incorrect** ⭐
**Probability:** 5%

**Symptoms:**
- Step 4 shows DimMonth only has 1 row or wrong date range

**Fix:**
```m
// Verify these calculations in ___DimMonth:
LastFullMonth = Date.EndOfMonth(Date.AddMonths(DateTime.Date(DateTime.LocalNow()), -1)),
FirstMonthStart = Date.AddMonths(LastFullMonth, -12),

// Debug: Add these as separate steps to see values:
#"Debug Last Month" = LastFullMonth,  // Should be 2026-01-31
#"Debug First Month" = FirstMonthStart,  // Should be 2025-01-31
```

---

## 📋 QUICK DIAGNOSTIC CHECKLIST

Run through this in 5 minutes:

- [ ] **Data Files:** Latest CSV has dates beyond Jan 2025?
- [ ] **Benchmark Query:** Incident Date column shows multiple months?
- [ ] **MonthStart:** Values vary (not all 2025-01-01)?
- [ ] **DimMonth:** Shows 13 rows (Jan 2025 - Jan 2026)?
- [ ] **Relationship:** Solid line between MonthStart fields?
- [ ] **Visual Fields:** Using correct table references?
- [ ] **Simple Measure:** Test measure shows counts for multiple months?

---

## 🛠️ IMMEDIATE NEXT STEPS

**After running diagnostics, report back with:**

1. **Which step revealed the issue?**
   - "Step 1 - files only have Jan 2025 data" 
   - "Step 3 - MonthStart all showing 2025-01-01"
   - "Step 5 - no relationship found"
   - etc.

2. **Screenshots if possible:**
   - Power Query preview showing date columns
   - Model view showing relationships
   - Visual field configuration

3. **We'll create targeted fix** based on root cause identified

---

## 💡 PRO TIPS

**If stuck, try this quick test:**
1. Add `___Benchmark[Incident Date]` to the matrix visual as a row
2. Does it show multiple dates beyond Jan 2025?
   - YES → Data exists, issue is in MonthStart/relationships
   - NO → Data gap issue, check source files

**Power Query Preview Limitation:**
- Power Query only shows top 1000 rows by default
- Your Jan 2025 data might be in first 1000 rows
- Later months might exist but not show in preview
- Solution: Add a filter step to check specific months
