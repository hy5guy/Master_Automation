# Top 5 Parking Violations Query - Fix Summary

**Date:** 2026-01-11  
**Issues Fixed:**
1. Officer name formatting (non-padded badge numbers)
2. Subtitle month (DAX needs update in Power BI)

---

## ✅ Issues Identified

1. **Officer Name Format:**
   - Current: "LIGGIO, PO (0388)" 
   - Should be: "A. LIGGIO #388" (non-padded badge)
   - Other officers: "M. RAMIREZ-DRAKEFORD #2025" (already correct format, just need non-padded badge)

2. **Subtitle:**
   - Current: Shows "November 2025"
   - Should be: "December 2025"
   - **Note:** This is a DAX measure in Power BI, not M code

3. **Top 4 Verification:**
   - ✅ Top 4 are PEO officers in Traffic Bureau (verified)
   - 1. M. RAMIREZ-DRAKEFORD #2025 (PEO, Traffic)
   - 2. K. TORRES #2027 (PEO, Traffic)
   - 3. D. RIZZI #2030 (PEO, Traffic)
   - 4. D. MATTALIAN #0717 (CLASS I, Traffic) - still Traffic Bureau

---

## ✅ M Code Query Created

**File:** `summons_top5_parking.m`

**Features:**
- Dynamically finds most recent month
- Filters to parking violations (TYPE = "P")
- Formats officer names with non-padded badge numbers
- Handles two name patterns:
  - "M. RAMIREZ-DRAKEFORD #2025" → "M. RAMIREZ-DRAKEFORD #2025" (replace badge)
  - "LIGGIO, PO (0388)" → "A. LIGGIO #388" (extract name, add initial)
- Returns top 5 officers by summons count

**Output Columns:**
- `Officer` - Formatted name with non-padded badge (e.g., "A. LIGGIO #388")
- `Sum of Summons Count` - Total parking violations

---

## 📝 Power BI Actions Required

1. **Update M Code Query:**
   - Copy `summons_top5_parking.m` into Power BI Query Editor
   - Refresh the query

2. **Fix Subtitle DAX:**
   - Update the subtitle measure to show the correct month
   - Should reference the most recent month from the data
   - Example: `"Department-wide parking violations (" & FORMAT(MAX(Table[Date]), "MMMM YYYY") & ")"`

---

**Status:** ✅ M Code query created  
**Next:** Update Power BI query and DAX subtitle measure
