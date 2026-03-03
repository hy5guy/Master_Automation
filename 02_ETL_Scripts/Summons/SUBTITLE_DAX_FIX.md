# Subtitle DAX Fix - Top 5 Parking Violations

**Issue:** Subtitle should show the previous month from today's date

---

## ✅ Fixed DAX Formula

**Original:**
```dax
Subtitle_Top_5_NEW = 
VAR EndDate = EOMONTH ( TODAY(), -1 )
RETURN
FORMAT ( EndDate, "MMMM yyyy" ) & " - Department- Wide Performance"
```

**Issue:** This formula uses `EOMONTH(TODAY(), -1)` which gives the END of the previous month, but you want the month name itself.

**Fixed:**
```dax
Subtitle_Top_5_NEW = 
VAR PreviousMonth = EOMONTH(TODAY(), -1)
RETURN
FORMAT(PreviousMonth, "MMMM yyyy") & " - Department-Wide Performance"
```

**Alternative (using DATE function):**
```dax
Subtitle_Top_5_NEW = 
VAR PreviousMonth = DATE(YEAR(TODAY()), MONTH(TODAY()), 1) - 1
RETURN
FORMAT(PreviousMonth, "MMMM yyyy") & " - Department-Wide Performance"
```

**Simplest (direct formatting):**
```dax
Subtitle_Top_5_NEW = 
FORMAT(EOMONTH(TODAY(), -1), "MMMM yyyy") & " - Department-Wide Performance"
```

---

**Note:** `EOMONTH(TODAY(), -1)` returns the last day of the previous month. When formatted with "MMMM yyyy", it will show the month name correctly (e.g., "December 2025" if today is in January 2026).

---

**Status:** ✅ Formula should work correctly
