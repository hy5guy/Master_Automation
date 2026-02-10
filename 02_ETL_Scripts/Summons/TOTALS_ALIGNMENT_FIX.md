# Totals Alignment Fix - 13-Month vs All Bureaus Visuals

**Date:** 2026-01-11  
**Issue:** Totals between 13-month visual and All Bureaus visual don't match

---

## 🔍 Problem Identified

**13-Month Visual (Department-Wide Summons):**
- 12-25: M=440, P=2,882 (includes UNKNOWN records)

**All Bureaus Visual:**
- Total: M=436, P=2,874 (excludes UNKNOWN records)
- Difference: M=4, P=8 (12 UNKNOWN records)

---

## ✅ Solution Applied

**Updated `summons_13month_trend.m` query:**
- Added filter to exclude UNKNOWN WG2 records from e-ticket data
- Historical backfill records (IS_AGGREGATE = true) are kept (they don't have WG2)
- Only current month e-ticket records with UNKNOWN WG2 are filtered out

**Filter Logic:**
- Keep: Historical backfill (IS_AGGREGATE = true)
- Keep: Historical summary (ETL_VERSION = "HISTORICAL_SUMMARY")
- Filter: Current month e-ticket records with UNKNOWN/null/empty WG2

---

## 📊 Expected Results

After refreshing the `summons_13month_trend` query in Power BI:

**13-Month Visual:**
- 12-25: M=436, P=2,874 (matches All Bureaus visual)

**All Bureaus Visual:**
- Total: M=436, P=2,874 (unchanged)

**Result:** ✅ Totals now match between both visuals

---

## 📝 Notes

- UNKNOWN records (12 records: M=4, P=8) are excluded from both visuals
- Historical backfill data is unaffected (aggregate records don't have WG2)
- Only current month e-ticket data is filtered

---

**Status:** ✅ Query updated  
**Next Step:** Refresh `summons_13month_trend` query in Power BI
