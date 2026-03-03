# Detective Clearance Rate - X-Axis Column Issue

**Visual Configuration:**
- X-axis is using: `Month_MM_YY`
- Query creates column: `Month_Abbrev`

**Issue:** 12-25 is checked in filter but not showing in visual

---

## ✅ Solution

The visual is using `Month_MM_YY` but the query creates `Month_Abbrev`. Check:

1. **If `Month_MM_YY` is a calculated column/measure:**
   - Verify it's referencing `Month_Abbrev` from the query
   - Check if it has any filters or logic that excludes 12-25

2. **If `Month_MM_YY` is the actual column name:**
   - The query might need to rename `Month_Abbrev` to `Month_MM_YY`
   - OR the visual should use `Month_Abbrev` instead

3. **Sort Order:**
   - X-axis should sort by `Sort_Order` or `Date` (ascending)
   - NOT alphabetically by `Month_MM_YY` (which would put 12-25 in wrong position)

---

## 🔧 Quick Fix Options

**Option 1: Update Query to Rename Column**
- Add step to rename `Month_Abbrev` to `Month_MM_YY`

**Option 2: Change Visual X-Axis**
- Change X-axis to use `Month_Abbrev` instead of `Month_MM_YY`
- Ensure sort is by `Sort_Order` or `Date` (ascending)

---

**Most Likely Issue:** The X-axis is sorting alphabetically, which would put months in the wrong order. Change the X-axis sort to use `Sort_Order` or `Date` column instead of sorting by `Month_MM_YY` itself.
