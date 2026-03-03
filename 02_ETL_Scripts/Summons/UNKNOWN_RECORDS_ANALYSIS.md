# UNKNOWN Records Analysis

**Date:** 2026-01-11  
**Issue:** 12 records showing WG2="UNKNOWN" in the All Bureaus visual

---

## 🔍 Analysis

**UNKNOWN Records Found:**
- **Count:** 12 records (M=4, P=8)
- **Badge Numbers:** 0390, 0391, 0392 (probationary officers)

---

## 📋 Root Cause

These records have badge numbers that are NOT in the Assignment Master file:
- **0390** - P.O. ROBERT OROPEZA (Probationary PO)
- **0391** - P.O. TEUDY LUNA (Probationary PO)
- **0392** - P.O. JASON CAMPOVERDE (Probationary PO)

When the ETL joins e-ticket data with Assignment Master and no match is found, it assigns WG2="UNKNOWN" as a placeholder.

---

## ✅ Solution Applied

**M Code Update:**
- Added filter to exclude records where `WG2 = "UNKNOWN"`
- Updated filter: `each [WG2] <> null and [WG2] <> "" and [WG2] <> "UNKNOWN"`

**Result:**
- UNKNOWN records will no longer appear in the All Bureaus visual
- These 12 records will be excluded from the visual

---

## 📝 Long-term Solution (Optional)

**Option 1: Add Missing Officers to Assignment Master**
- Add probationary officers (0390, 0391, 0392) to Assignment_Master_V2.csv
- Assign them to appropriate bureaus (likely PATROL BUREAU)

**Option 2: Keep Filter in M Code** (Current Solution)
- Continue filtering out UNKNOWN records in the M code
- This is acceptable if these officers are temporary or don't need to be tracked

---

## ✅ Status

**M Code Updated:** ✅ UNKNOWN records will be filtered out  
**Visual Impact:** UNKNOWN row will no longer appear in All Bureaus visual

---

**Next Steps:**
- M code updated - refresh Power BI to see changes
- Optional: Add missing officers to Assignment Master if needed for tracking
