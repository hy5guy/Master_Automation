# Detective Clearance Rate - 12-25 Not Showing in Visual

**Issue:** 12-25 is checked in the filter but not showing in the visual

---

## ✅ Query Status

If 12-25 appears in the filter pane (checked/selected), the query IS returning the data correctly. The issue is in the visual configuration.

---

## 🔍 Visual Configuration Checklist

### 1. X-Axis Column
**Check which column is used for the x-axis:**
- ✅ Should use: `Month_Abbrev` (formatted as "12-25")
- ❌ NOT: `Month_Year` (formatted as "December 2025")
- ❌ NOT: `Month` (original column name from source)

### 2. Sort Order
**X-axis should be sorted by:**
- ✅ `Sort_Order` (ascending) - numerical sort: 202412, 202501, ..., 202512
- ✅ OR `Date` (ascending)
- ❌ NOT alphabetically (which would put "12-25" after "11-25")

### 3. Visual Filters
**Check for visual-level filters:**
- Verify no filters on `Month_Abbrev`, `Date`, or `Sort_Order` columns
- Check if there's a "Top N" filter or date range filter applied

### 4. Data Type
**Ensure the x-axis column is text type:**
- `Month_Abbrev` should be type text
- If it's being treated as a number, it might cause sorting issues

---

## 📊 Recommended Visual Settings

**X-Axis:**
- Field: `Month_Abbrev`
- Sort by: `Sort_Order` (Ascending) or `Date` (Ascending)

**Y-Axis:**
- Field: `Value`

**Legend/Data:**
- Filter: `Closed Case Dispositions = "Monthly Bureau Case Clearance %"`
- OR: `Is_Percent = true` AND `Disposition_Category = "Performance Metric"`

---

## 🛠️ Quick Fix: Check Visual X-Axis Settings

1. Select the visual
2. Check the X-axis field - should be `Month_Abbrev`
3. Check the X-axis sort - should sort by `Sort_Order` or `Date` (not `Month_Abbrev` alphabetically)
4. Remove any visual-level filters on date/month columns

---

**Note:** Since the filter shows 12-25 is available, the query is working correctly. The issue is in how the visual is configured to display the data.
