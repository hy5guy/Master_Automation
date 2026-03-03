# BENCHMARK VISUALS - QUICK FIX REFERENCE CARD

🕒 2026-02-14

## 🎯 QUICK DIAGNOSIS (30 Seconds)

**Run this simple test in Power BI:**

1. Open Power BI Desktop
2. Go to **Data View** (left sidebar)
3. Click on `___Benchmark` table
4. Look at **Incident Date** column
5. Scroll through rows - **do you see dates beyond January 2025?**

**Result:**
- ✅ YES, I see Feb/Mar/etc → Issue is in M code or relationships → **USE FIX #2 or #3**
- ❌ NO, only Jan 2025 → Source data issue → **USE FIX #1**

---

## 🔧 FIX #1: Missing Source Data (70% of cases)

**Problem:** CSV/XLSX files only contain January 2025 data

**Quick Fix:**
1. Navigate to: `C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark\`
2. Check each folder: `use_force\`, `show_force\`, `vehicle_pursuit\`
3. Open latest CSV in each folder
4. Verify it has data for Feb 2025 and beyond
5. **If missing:** Export new data from source system and add to folders
6. Refresh Power BI

**Verification:**
- Run the Python diagnostic script: `diagnose_benchmark_data.py`
- Should show data spanning multiple months

---

## 🔧 FIX #2: MonthStart Calculation Error (15% of cases)

**Problem:** All MonthStart values stuck at 2025-01-01

**Symptoms in Power Query:**
- MonthStart column shows same date for all rows
- Visual shows only one month

**Quick Fix:**

1. Open Power BI → **Transform Data**
2. Click `___Benchmark` query
3. Find the step: `AddMonthStart`
4. Replace with this enhanced version:

```m
// OLD (may be failing silently):
AddMonthStart = Table.AddColumn(IncidentDateTyped, "MonthStart", 
    each Date.StartOfMonth(Date.From([Incident Date])), 
    type date),

// NEW (with error handling):
AddMonthStart = Table.AddColumn(IncidentDateTyped, "MonthStart", 
    each 
        let
            IncDate = [Incident Date],
            ConvertedDate = if Value.Is(IncDate, type date) 
                           then IncDate 
                           else if Value.Is(IncDate, type datetime) 
                           then Date.From(IncDate)
                           else try Date.From(IncDate) otherwise null,
            MonthStart = if ConvertedDate = null 
                        then null 
                        else Date.StartOfMonth(ConvertedDate)
        in
            MonthStart, 
    type date),
```

5. **Close & Apply**
6. Check if visuals now show multiple months

---

## 🔧 FIX #3: Broken Relationship (10% of cases)

**Problem:** Relationship between ___Benchmark and ___DimMonth is inactive or wrong

**Quick Fix:**

1. Go to **Model View**
2. Find relationship line between:
   - `___Benchmark[MonthStart]` ↔ `___DimMonth[MonthStart]`

3. **If line is dotted (inactive):**
   - Right-click → Delete relationship
   - Drag from `___Benchmark[MonthStart]` to `___DimMonth[MonthStart]`
   - Ensure: One-to-Many (1:*), Single direction

4. **If no line exists:**
   - Create relationship manually
   - From: `___Benchmark[MonthStart]`
   - To: `___DimMonth[MonthStart]`
   - Cardinality: Many-to-One (*:1)

5. **Verify both columns are type DATE** (not datetime or text)

---

## 🔧 FIX #4: Wrong Month Dimension Window (5% of cases)

**Problem:** ___DimMonth shows wrong date range

**Quick Fix:**

1. **Transform Data** → Click `___DimMonth`
2. Check if you see exactly **13 rows** (Jan 2025 - Jan 2026)

3. **If wrong:** Replace entire ___DimMonth query:

```m
let
    // Calculate dynamic 13-month window
    Today = DateTime.Date(DateTime.LocalNow()),
    LastFullMonth = Date.EndOfMonth(Date.AddMonths(Today, -1)),
    FirstMonthStart = Date.StartOfMonth(Date.AddMonths(LastFullMonth, -12)),
    
    // Generate month list
    MonthStarts = List.Generate(
        () => FirstMonthStart,
        each _ <= LastFullMonth,
        each Date.AddMonths(_, 1)
    ),
    
    // Convert to table
    ToTable = Table.FromList(MonthStarts, Splitter.SplitByNothing(), {"MonthStart"}),
    TypedDate = Table.TransformColumnTypes(ToTable, {{"MonthStart", type date}}),
    AddLabel = Table.AddColumn(TypedDate, "MonthLabel", 
        each Date.ToText([MonthStart], "MM-yy"), type text),
    AddSort = Table.AddColumn(AddLabel, "MonthSort", 
        each Date.Year([MonthStart]) * 100 + Date.Month([MonthStart]), Int64.Type)
in
    AddSort
```

4. **Close & Apply**

---

## 🔧 FIX #5: Visual Field Mapping Error (5% of cases)

**Problem:** Visual using wrong table references

**Quick Fix:**

1. Click the **Use of Force Incident Matrix** visual
2. Look at **Fields** pane (right side)
3. Clear all fields
4. Rebuild with correct fields:

**Correct Configuration:**
- **Rows:** `___DimMonth[MonthLabel]` ← Must use DimMonth!
- **Columns:** `___DimEventType[EventType]`
- **Values:** Create new measure:
  ```dax
  Incident Count = COUNTROWS(___Benchmark)
  ```

5. Format MonthLabel to sort by `___DimMonth[MonthSort]`

---

## 📊 VALIDATION TESTS

After applying any fix, run these quick tests:

### **Test 1: Simple Table**
- Create new table visual
- Rows: `___DimMonth[MonthLabel]`
- Values: `Incident Count` measure
- **Expected:** Should see 13 rows with varying counts

### **Test 2: Data View Check**
- Go to Data View
- Click `___Benchmark` table
- Scroll through rows
- **Expected:** See varying MonthStart dates (not all 2025-01-01)

### **Test 3: Month Count**
- Create card visual
- Add measure:
  ```dax
  Unique Months = DISTINCTCOUNT(___Benchmark[MonthStart])
  ```
- **Expected:** Should show number > 1 (ideally 12-13)

---

## 🚨 EMERGENCY RESET

**If nothing works, try this complete reset:**

1. **Backup current file** (Save As → backup name)

2. **Delete and recreate queries:**
   ```
   a. Delete ___Benchmark query
   b. Delete ___DimMonth query
   c. Delete ___DimEventType query
   d. Recreate from M code provided in project files
   ```

3. **Delete and recreate relationships:**
   ```
   a. Model View → Delete all Benchmark-related relationships
   b. Recreate relationships manually
   ```

4. **Delete and recreate visuals:**
   ```
   a. Delete all Benchmark page visuals
   b. Recreate from scratch using correct fields
   ```

---

## 📞 ESCALATION PATH

**If all fixes fail, provide this info for advanced support:**

1. **Run Python diagnostic script** → Share JSON output
2. **Export ___Benchmark query results** → Save as CSV, check row count
3. **Screenshot Model View** → Show all relationships
4. **Screenshot Data View** → Show Incident Date and MonthStart columns
5. **Share M code** → Copy full text of ___Benchmark query

---

## 💡 PREVENTION TIPS

**To avoid this issue in future:**

1. **Monthly Data Export Checklist:**
   - Export data from source system monthly
   - Verify date range before saving to Benchmark folders
   - Keep consistent file naming: `YYYY_MM_[type].csv`

2. **Power BI Refresh Checklist:**
   - Always **Close & Apply** after M code changes
   - Check Data View after refresh (verify row counts)
   - Test one visual before building others

3. **Documentation:**
   - Keep log of when data was exported
   - Note date ranges in file names or metadata
   - Track Power BI refresh dates

---

**Last Updated:** 2026-02-14
**Created by:** R. A. Carucci
**For:** Hackensack PD Analytics - Benchmark Dashboard
