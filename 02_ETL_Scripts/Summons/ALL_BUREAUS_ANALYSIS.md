# All Bureaus Visual Totals Analysis

**Date:** 2026-01-11  
**Visual Export:** `2025_12_Summons  Moving & Parking  All Bureaus.csv`

---

## 📊 Visual Export Totals

| Bureau | Moving (M) | Parking (P) | Total |
|--------|-----------|-------------|-------|
| CSB | 2 | 3 | 5 |
| DETECTIVE BUREAU | 0 | 4 | 4 |
| HOUSING | 0 | 5 | 5 |
| OFFICE OF SPECIAL OPERATIONS | 3 | 11 | 14 |
| PATROL BUREAU | 247 | 589 | 836 |
| TRAFFIC BUREAU | 160 | 2,308 | 2,468 |
| **TOTAL** | **412** | **2,920** | **3,332** |

---

## ✅ Expected Totals (from ETL Output)

Based on the ETL output for December 2025 e-ticket data:
- **Moving (M):** 440
- **Parking (P):** 2,882
- **Total:** 3,366

---

## 🔍 Discrepancy Analysis

| Metric | Visual Export | ETL Output | Difference | % Difference |
|--------|--------------|------------|------------|--------------|
| Moving (M) | 412 | 440 | **-28** | -6.4% |
| Parking (P) | 2,920 | 2,882 | **+38** | +1.3% |
| **Total** | **3,332** | **3,366** | **-34** | **-1.0%** |

---

## ⚠️ Issues Identified

### 1. Missing Records
- **34 records missing** from the visual (1.0% of total)
- **28 Moving violations missing** (6.4% of M total)
- **38 Parking violations appear extra** (1.3% more than expected)

### 2. Possible Causes

**Missing Moving Violations (28 records):**
- Records without WG2 (bureau) assignments
- Records with WG2 values that don't match visual categories
- Records filtered out by Power BI visual filters

**Extra Parking Violations (38 records):**
- This is unexpected - suggests a grouping or counting issue
- Possibly records counted in visual but not in ETL output
- Or ETL output counts are different from visual aggregation

---

## ✅ Recommendation

**The totals are NOT completely correct** - there are discrepancies:

1. **Missing 34 total records** (1.0% discrepancy)
2. **Missing 28 Moving violations** (6.4% discrepancy - more significant)
3. **38 extra Parking violations** (unexpected)

**Next Steps:**
1. Check for records without WG2 (bureau) assignments in ETL output
2. Verify Power BI visual filters are not excluding records
3. Check if there are WG2 values that don't match the visual categories
4. Verify the visual aggregation logic matches the ETL output structure

---

## 📋 Summary

- **Visual Total:** 3,332 records (M=412, P=2,920)
- **ETL Expected:** 3,366 records (M=440, P=2,882)
- **Discrepancy:** -34 records overall, but with unexpected P count
- **Status:** ⚠️ **Totals do NOT match** - investigation needed
