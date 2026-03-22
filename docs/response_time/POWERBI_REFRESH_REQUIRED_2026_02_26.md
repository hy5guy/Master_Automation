# Power BI Refresh Required — Response Time Queries
# 2026-02-26 | v1.17.17

**Status: ✅ COMPLETE — Template updated via Claude Desktop MCP injection (2026-03-19)**

---

## Summary — What You Need to Do

| Query | M Code Update Needed? | Refresh Needed? |
|-------|-----------------------|----------------|
| `___ResponseTimeCalculator` | **YES — update M code first** | Yes |
| `___ResponseTime_OutVsCall` | No (M code is correct) | Yes |
| `___ResponseTime_DispVsCall` | No (M code is correct) | Yes |

**One M code update + one Refresh All is all that is required.**

---

## Why Both Steps Are Needed

Two critical bugs were corrected in `response_time_batch_all_metrics.py` on 2026-02-26:
- **v1.17.15**: First-arriving-unit sort before dedup
- **v1.17.16 (CRITICAL)**: 92-type administrative incident filter. Over 57% of records
  were officer self-initiated activities (Meal Break, Patrol Check, TAPS, Traffic Detail, etc.)
  included as Routine calls with near-zero dispatch times.
  Routine Jan-25 dispatch processing: 0:50 → **2:27**.
  Routine Jan-25 dispatch to on scene: 0:48 → **2:01**.

All 25 monthly CSVs have been regenerated with both fixes. However:
- **OutVsCall and DispVsCall** already have the correct `Folder.Files()` M code pointing
  to the unified `response_time_all_metrics` folder. They just need a refresh to pick up
  the new CSVs.
- **Calculator** was manually recreated in Power BI from an older M code version. It is
  still reading from the old backfill path and showing pre-fix values (Emergency Jan-26
  still shows 3:11 instead of 2:51). Its M code must be replaced before refreshing.

---

## Step 1 — Update Calculator M Code in Power BI Desktop

1. Open the February 2026 template (`08_Templates\Monthly_Report_Template.pbix`)
2. Home → Transform data (Power Query Editor)
3. Select `___ResponseTimeCalculator` in the left panel
4. Click **Advanced Editor** and replace the entire M code with the contents of:
   `06_Workspace_Management\m_code\response_time\___ResponseTimeCalculator.m`
5. The critical line is:
   `AllFiles = Folder.Files("C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Backfill\response_time_all_metrics"),`
6. Close Advanced Editor → Apply & Close

---

## Step 2 — Refresh All Three Queries

Home → **Refresh All**

The three queries that must load correctly:
- `___ResponseTimeCalculator` — Time Out − Time Dispatched (Dispatch to On Scene)
- `___ResponseTime_OutVsCall` — Time Out − Time of Call (Time Received to On Scene)
- `___ResponseTime_DispVsCall` — Time Dispatched − Time of Call (Dispatch Processing)

**Data folder:** `PowerBI_Data\Backfill\response_time_all_metrics\`
**CSVs last regenerated:** 2026-02-26 23:33 EST (v1.17.16 admin filter applied)

---

## Validation Checklist (complete after refresh)

- [ ] Update `___ResponseTimeCalculator` M code in Power BI Desktop (Step 1)
- [ ] Home → Refresh All — confirm all three load without errors
- [ ] Verify rolling window shows Jan-25 through Jan-26 for all three visuals
- [ ] **Calculator (Dispatch to On Scene)** — Emergency Jan-26: **2:51** (was 3:11)
- [ ] **Calculator (Dispatch to On Scene)** — Routine Jan-25: **2:01** (was 0:48)
- [ ] **OutVsCall (Time Received to Scene)** — Emergency Jan-25: **4:58** ✓ (unchanged)
- [ ] **DispVsCall (Dispatch Processing)** — Routine Jan-25: **2:27** (was 0:50)
- [ ] Confirm Emergency pattern consistent (Emergency ≈ 2:45–3:10 across months)
- [ ] Confirm Routine not showing sub-1-minute values (those were pre-fix artifacts)
- [ ] File → Save

---

## Expected Values After Refresh (v1.17.17 corrected)

| Month | Type | Dispatch to On Scene | Time Received to Scene | Dispatch Processing |
|-------|------|---------------------|----------------------|---------------------|
| 01-26 | Emergency | **2:51** | **4:41** | **2:48** |
| 01-26 | Routine | **2:04** | **2:43** | **2:01** |
| 01-26 | Urgent | **2:35** | **3:05** | **1:39** |
| 01-25 | Emergency | **2:52** | **4:58** | **2:58** |
| 01-25 | Routine | **2:01** | **3:22** | **2:27** |
| 01-25 | Urgent | **2:38** | **3:43** | **2:01** |

**Note on Routine "Dispatch to On Scene":** The mean (~2:01) is pulled down by traffic stops
and field contacts where the officer was already on scene. This is a data characteristic,
not an error. The median for this specific metric is ~0:11 — have this talking point ready
if admin asks why Routine is lower than Emergency for dispatch-to-scene.

---

## After Refresh Is Confirmed

Update this file: change Status at the top to `✅ COMPLETE` and add date/initials.

**Completed by:** Claude Desktop (MCP injection)
**Date/Time:** 2026-03-19
**Notes:** Directory consolidation refactor complete. All 4 Response Time partitions (`___ResponseTime_DispVsCall`, `___ResponseTime_OutVsCall`, `___ResponseTimeCalculator`, `___ResponseTime_AllMetrics`) updated with `PowerBI_Date` → `PowerBI_Data` path corrections. See `CHANGELOG.md` v1.18.13 and `docs/POWERBI_TEMPLATE_MCP_UPDATE_2026_03_19.md`.
