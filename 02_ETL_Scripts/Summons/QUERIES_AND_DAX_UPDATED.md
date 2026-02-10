# Updated Queries and DAX - Top 5 Parking and Moving

**Date:** 2026-01-11

---

## ✅ Fixed M Code Queries

### 1. summons_top5_parking.m
- Fixed null handling for IS_AGGREGATE
- Formats officer names with non-padded badge numbers
- Handles "LIGGIO, PO (0388)" → "A. LIGGIO #388"

### 2. summons_top5_moving.m  
- Updated to match parking query formatting
- Formats officer names with non-padded badge numbers
- Same name formatting logic as parking query

---

## ✅ DAX Subtitle Fix

**Issue:** Subtitle shows "November 2025" but should show "December 2025"

**Solution Options:**

### Option 1: Use Previous Month from Today (Current Formula)
```dax
Subtitle_Top_5_NEW = 
FORMAT(EOMONTH(TODAY(), -1), "MMMM yyyy") & " - Department-Wide Performance"
```
- If TODAY() is January 2026, this shows "December 2025"
- If it's showing November, check if TODAY() is evaluating correctly in your Power BI environment

### Option 2: Reference Month from Data (Recommended)
Create a measure that gets the month from your query data:

```dax
Subtitle_Top_5_NEW = 
VAR LatestMonth = MAX('summons_13month_trend'[Month_Year])
VAR MonthNum = VALUE(LEFT(LatestMonth, 2))
VAR YearNum = VALUE(RIGHT(LatestMonth, 2)) + 2000
VAR MonthDate = DATE(YearNum, MonthNum, 1)
RETURN
FORMAT(MonthDate, "MMMM yyyy") & " - Department-Wide Performance"
```

### Option 3: Simple Previous Month (Alternative)
```dax
Subtitle_Top_5_NEW = 
VAR PrevMonth = DATE(YEAR(TODAY()), MONTH(TODAY()) - 1, 1)
RETURN
FORMAT(PrevMonth, "MMMM yyyy") & " - Department-Wide Performance"
```

---

**Recommendation:** Use Option 2 to ensure the subtitle always matches the data month.
