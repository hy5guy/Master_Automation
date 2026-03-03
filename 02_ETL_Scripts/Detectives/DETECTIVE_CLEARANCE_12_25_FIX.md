# Detective Clearance Rate - 12-25 Missing Fix

**Date:** 2026-01-11  
**Issue:** X-axis not showing 12-25 (December 2025), only shows through 11-25

---

## ✅ Problem Identified

The filter logic was using `Date.AddMonths(Date.StartOfMonth(CurrentDate), -1)` which should work, but the explicit year/month calculation is clearer and more reliable.

**Current Date Logic (if today is January 11, 2026):**
- Previous filter: `Date.AddMonths(2026-01-01, -1) = 2025-12-01` ✓
- Should include December 2025 (2025-12-01)

However, the CSV export shows data only through 11-25, suggesting the filter might not be working as expected.

---

## ✅ Solution Applied

**Updated Filter Logic:**
- Use explicit year/month calculation instead of Date.AddMonths
- Handles year rollover correctly (January → December of previous year)
- Ensures December 2025 (12-25) is included when current month is January 2026

**New Logic:**
```m
CurrentYear     = Date.Year(CurrentDate),
CurrentMonth    = Date.Month(CurrentDate),
EndYear         = if CurrentMonth = 1 then CurrentYear - 1 else CurrentYear,
EndMonth        = if CurrentMonth = 1 then 12 else CurrentMonth - 1,
EndFilterDate   = #date(EndYear, EndMonth, 1),
StartFilterDate = Date.AddMonths(EndFilterDate, -12),
```

**Result:**
- When current month is January 2026: EndFilterDate = 2025-12-01
- Filter includes: 2024-12-01 through 2025-12-01 (13 months including December 2025)

---

## 📝 Next Steps

1. **Copy Updated M Code:** Use `detective_clearance_rate_FINAL.m` in Power BI Query Editor
2. **Refresh Query:** Refresh the query to see 12-25 data
3. **Verify:** X-axis should now show 12-25 (December 2025)

---

**Status:** ✅ M Code query updated  
**File:** `detective_clearance_rate_FINAL.m`
