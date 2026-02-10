# Detective Clearance Rate - 12-25 Not Showing in Visual

**Issue:** 12-25 is checked in the filter but not showing in the visual

**Possible Causes:**
1. Visual is using wrong column for x-axis
2. Visual has additional filters applied
3. Data exists but Month_Abbrev format doesn't match
4. Visual sort order excludes 12-25

---

## ✅ Troubleshooting Steps

1. **Check X-Axis Column:**
   - The visual should use `Month_Abbrev` column (formatted as "12-25")
   - NOT `Month_Year` (formatted as "December 2025")
   - NOT `Month` (original unpivoted column name)

2. **Check Visual Filters:**
   - Verify no visual-level filters are excluding 12-25
   - Check if there's a filter on `Month_Abbrev` or `Date` column

3. **Check Sort Order:**
   - The x-axis should sort by `Sort_Order` or `Date` column
   - Not alphabetically (which would put 12-25 after 11-25)

4. **Verify Data Exists:**
   - Check that 12-25 data exists in the query results
   - Filter the query table to show only "Monthly Bureau Case Clearance %" rows
   - Verify 12-25 appears with a value

---

## 📝 Recommended Visual Configuration

**X-Axis:**
- Field: `Month_Abbrev` (or `Month` if that's the column name)
- Sort by: `Sort_Order` or `Date` (ascending)

**Y-Axis:**
- Field: `Value`
- Filter: `Is_Percent = true` AND `Disposition_Category = "Performance Metric"`

**Data:**
- Filter: `Closed Case Dispositions = "Monthly Bureau Case Clearance %"`

---

If the query is returning 12-25 data (as indicated by the filter showing it's checked), the issue is likely in the visual configuration, not the M code query.
