# Power BI Refresh Required — Response Time Queries
# 2026-02-26 | v1.17.15

**Status: ⏳ PENDING — v1.17.16 CSVs are in place; Calculator M code update + refresh required**

---

## Why a Refresh Is Required

Two critical bugs were corrected in `response_time_batch_all_metrics.py` on 2026-02-26:
- **v1.17.15**: First-arriving-unit sort before dedup
- **v1.17.16 (CRITICAL)**: 101-type administrative incident filter added. Over 57% of records
  were officer self-initiated activities (Meal Break, Patrol Check, TAPS, Traffic Detail, etc.)
  included as Routine calls with near-zero dispatch times. Routine 01-25 dispatch processing:
  0:50 → **2:27**. Routine 01-25 dispatch to on scene: 0:48 → **2:01**.

All 25 monthly CSVs have been regenerated. The `___ResponseTimeCalculator` query in Power BI
Desktop also needs its M code updated manually — it was recreated from an old version and
still reads from the old backfill path, not the unified `response_time_all_metrics` folder.

**Power BI will show incorrect values until both the M code update and refresh are complete.**

## Step 1 — Update Calculator M Code in Power BI Desktop

The `___ResponseTimeCalculator` query must be updated to use the unified folder path:
1. Open the February 2026 template in Power BI Desktop
2. Open Power Query Editor → select `___ResponseTimeCalculator`
3. Replace the entire M code with the contents of:
   `m_code/response_time/___ResponseTimeCalculator.m`
4. The key change: the query must use `Folder.Files("...\response_time_all_metrics")`,
   NOT individual file paths or the old backfill structure
5. Apply and Close

---

## Queries to Refresh

| Query Name | Metric | Data Source |
|-----------|--------|------------|
| `___ResponseTimeCalculator` | Time Out − Time Dispatched (Dispatch to On Scene) | `response_time_all_metrics\` |
| `___ResponseTime_OutVsCall` | Time Out − Time of Call (Time Received to On Scene) | `response_time_all_metrics\` |
| `___ResponseTime_DispVsCall` | Time Dispatched − Time of Call (Dispatch Processing Time) | `response_time_all_metrics\` |

**Data folder:** `PowerBI_Date\Backfill\response_time_all_metrics\`  
**New CSVs written:** 2026-02-26 at 23:12:20 EST  
**All 25 monthly files regenerated:** 2024-01 through 2026-01

---

## Step 2 — Validation Checklist (complete after refresh)

- [ ] Update `___ResponseTimeCalculator` M code in Power BI Desktop (see Step 1)
- [ ] Home → Refresh All
- [ ] Confirm all three response time queries load without errors
- [ ] Verify rolling 13-month window shows Jan-25 through Jan-26 for all three visuals
- [ ] Validate Emergency Jan-26 Dispatch to On Scene: **2:51** (was 3:11 pre-fix)
- [ ] Validate Routine Jan-25 Dispatch to On Scene: **2:01** (was 0:48 pre-admin-filter)
- [ ] Validate Routine Jan-25 Dispatch Processing: **2:27** (was 0:50 pre-admin-filter)
- [ ] Confirm Emergency > Routine pattern holds across all months for all three metrics
- [ ] File → Save to update the template

---

## Expected Value Changes After Refresh

| Month | Type | Metric | Pre-Fix | Post-Fix |
|-------|------|--------|---------|----------|
| 01-26 | Emergency | Dispatch to On Scene | 3:11 | **2:51** |
| 01-26 | Urgent | Dispatch to On Scene | 2:54 | **2:35** |
| 01-26 | Routine | Dispatch to On Scene | 1:26 | **1:23** |
| 01-25 | Emergency | Dispatch to On Scene | 2:58 | **2:52** |
| 01-25 | Urgent | Dispatch to On Scene | 2:53 | **2:38** |

See `docs/response_time/2026_02_26_PreFix_vs_PostFix_Comparison.md` for full delta table.

---

## After Refresh Is Confirmed

Update this file: change Status at the top to `✅ COMPLETE` and add date/initials.

**Completed by:** _______________  
**Date/Time:** _______________  
**Notes:** _______________
