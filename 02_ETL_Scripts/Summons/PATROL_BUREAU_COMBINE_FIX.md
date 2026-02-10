# PATROL BUREAU → PATROL DIVISION Combine Fix

**Date:** 2026-01-11  
**Issue:** All Bureaus visual shows both "PATROL BUREAU" (M=28, P=2) and "PATROL DIVISION" (M=242, P=608) as separate rows

---

## ✅ Solution Applied

**Updated `summons_all_bureaus.m` query:**
- Added step to replace "PATROL BUREAU" with "PATROL DIVISION" before grouping
- This combines the records so they appear as a single "PATROL DIVISION" row

**Result:**
- PATROL BUREAU records (M=28, P=2) will be combined with PATROL DIVISION (M=242, P=608)
- Final totals: M=270, P=610 for PATROL DIVISION

---

## 📝 Root Cause

The ETL output still contains some records with WG2 = "PATROL BUREAU":
- Likely from an assignment override for badge 0388 (30 records)
- These should be updated in the ETL script override, but the M code fix ensures they're combined in the visual

---

## ✅ Next Steps

1. **Refresh Query:** Refresh `summons_all_bureaus` query in Power BI
2. **Verify:** Visual should now show only "PATROL DIVISION" with combined totals

---

**Status:** ✅ M Code query updated  
**Impact:** PATROL BUREAU and PATROL DIVISION will be combined in the visual
