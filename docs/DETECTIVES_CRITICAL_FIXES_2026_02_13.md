# Detective Queries - Critical Fixes Applied (2026-02-13)

## Issues Fixed

### Issue #1: Type Comparison Error ✅
**Error Message**: `Expression.Error: We cannot apply operator < to types Number and Text`

**Root Cause**: Date parsing used `Value.FromText()` which returns text if parsing fails, then tried to compare text to number.

**Fix**: Changed to `Number.From()` which returns null on failure (safe for comparison).

---

### Issue #2: Empty Table Result ✅
**Root Cause**: **Window logic looking for 2025-2026 data, but Excel only has 2026 data!**

**Before**:
```powerquery
StartFilterDate = Date.AddMonths(EndFilterDate, -12)  // Goes back to Jan 2025
```

Excel workbook has: 01-26, 02-26... 12-26 (2026 only)  
Query filtered for: 01-25 through 01-26  
**Result**: All rows excluded → empty table!

**After**:
```powerquery
StartFilterDate = #date(2026, 1, 1)  // Start at Jan 2026
```

Now shows all available 2026 data up to previous complete month.

---

### Issue #3: Circular Reference (Bonus Fix) ✅
**Problem**: MonthsIncluded calculation referenced FilteredMonths inside its own row function.

**Fix**: Pre-calculate unique month count before adding column.

---

## Deploy Now

Both queries are fixed and ready:

1. **`___Detectives`** → Use `m_code/detectives/___Detectives_2026.m`
2. **`___Det_case_dispositions_clearance`** → Use `m_code/detectives/___Det_case_dispositions_clearance_2026.m`

Replace the M code in Power BI Advanced Editor and click **Close & Apply**.

---

## Expected Behavior (2026-Only Data)

**Today = February 13, 2026**

### Current Behavior
- **Start Date**: January 2026 (01-26)
- **End Date**: January 2026 (01-26) - previous complete month
- **Months Shown**: Only January 2026 (1 month)

### March 2026
- **Start Date**: January 2026
- **End Date**: February 2026
- **Months Shown**: Jan, Feb (2 months)

### December 2026
- **Start Date**: January 2026
- **End Date**: November 2026
- **Months Shown**: Jan through Nov (11 months)

### January 2027
- **Start Date**: January 2026
- **End Date**: December 2026
- **Months Shown**: All 12 months of 2026

**Note**: Once you have 2027 data, you'll need to either:
- Add 2027 columns to Excel (preferred for rolling window)
- Update M code to handle multiple years

---

## Testing

Try these queries in Power BI to verify:

```powerquery
// Check filtered date range
Table.SelectRows(AddedSortOrder, each [Date] <> null)
// Should show: 01-26, 02-26... up to current available data
```

---

*Critical Fixes - 2026-02-13*  
*Git Commit: 018722c*  
*Status: READY TO DEPLOY*
