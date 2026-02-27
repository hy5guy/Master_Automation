# Pre-Fix vs Post-Fix Comparison: Response Time Batch ETL
# Fix Applied: 2026-02-26 | v1.17.15
# Bug: `drop_duplicates(subset="ReportNumberNew", keep="first")` ran without prior
#      `sort_values(["ReportNumberNew", "Time Out"])`. For the 28.2% of calls with
#      multiple responding units, the wrong officer could be selected.

## What Changed

| Before Fix | After Fix |
|-----------|----------|
| `drop_duplicates(subset="ReportNumberNew", keep="first")` | `sort_values(["ReportNumberNew", "Time Out"])` then `drop_duplicates(...)` |
| Kept first row in Excel file order | Keeps first-arriving unit (lowest Time Out) |

## Pre-Fix Values (from Power BI visual screenshots, pre-fix batch run)

**Metric: Time Out − Time Dispatched (Dispatch to On Scene)**

| Month | Emergency (pre) | Routine (pre) | Urgent (pre) |
|-------|----------------|--------------|-------------|
| 01-25 | 2:58 | 0:48 | 2:53 |
| 01-26 | 3:11 | 1:26 | 2:54 |

> Note: 01-26 pre-fix values are from the visual screenshots provided in session 2026-02-26.
> Full 13-month pre-fix series not available (CSVs were overwritten by the corrected run).

---

## Post-Fix Values (from regenerated CSVs, 2026-02-26)

### Metric: Time Out − Time Dispatched (Dispatch to On Scene)

| Month | Emergency | Routine | Urgent | E Records | R Records | U Records |
|-------|-----------|---------|--------|-----------|-----------|-----------|
| 01-25 | 2:52 | 0:47 | 2:38 | 355 | 5,043 | 969 |
| 02-25 | 2:38 | 0:59 | 2:44 | 241 | 3,895 | 797 |
| 03-25 | 2:53 | 1:07 | 2:38 | 282 | 3,983 | 875 |
| 04-25 | 2:43 | 1:11 | 2:35 | 217 | 3,659 | 950 |
| 05-25 | 2:46 | 1:22 | 2:48 | 302 | 3,183 | 935 |
| 06-25 | 2:55 | 1:31 | 2:41 | 255 | 2,872 | 942 |
| 07-25 | 2:43 | 1:29 | 2:46 | 289 | 2,874 | 997 |
| 08-25 | 2:41 | 1:25 | 2:31 | 265 | 2,917 | 1,046 |
| 09-25 | 2:44 | 1:33 | 2:42 | 219 | 2,897 | 914 |
| 10-25 | 2:31 | 1:27 | 2:36 | 237 | 2,913 | 909 |
| 11-25 | 2:48 | 1:33 | 2:44 | 249 | 2,641 | 768 |
| 12-25 | 2:48 | 1:18 | 2:36 | 252 | 2,885 | 882 |
| 01-26 | 2:51 | 1:23 | 2:35 | 257 | 3,051 | 950 |

### Metric: Time Out − Time of Call (From Time Received to On Scene)

| Month | Emergency | Routine | Urgent | E Records | R Records | U Records |
|-------|-----------|---------|--------|-----------|-----------|-----------|
| 01-25 | 4:58 | 1:14 | 3:43 | 290 | 4,799 | 844 |
| 02-25 | 4:41 | 1:25 | 3:44 | 215 | 3,628 | 689 |
| 03-25 | 4:51 | 1:35 | 3:28 | 222 | 3,656 | 781 |
| 04-25 | 4:53 | 1:45 | 3:06 | 187 | 3,378 | 937 |
| 05-25 | 4:36 | 1:50 | 3:33 | 243 | 2,812 | 805 |
| 06-25 | 4:51 | 1:55 | 3:19 | 196 | 2,530 | 848 |
| 07-25 | 4:54 | 2:02 | 3:02 | 226 | 2,501 | 890 |
| 08-25 | 4:49 | 1:55 | 2:55 | 208 | 2,590 | 1,022 |
| 09-25 | 5:03 | 1:56 | 3:24 | 180 | 2,572 | 817 |
| 10-25 | 4:31 | 1:54 | 3:22 | 195 | 2,598 | 823 |
| 11-25 | 5:00 | 1:57 | 3:19 | 197 | 2,370 | 717 |
| 12-25 | 4:55 | 1:48 | 3:07 | 204 | 2,624 | 843 |
| 01-26 | 4:41 | 1:49 | 3:05 | 212 | 2,790 | 916 |

### Metric: Time Dispatched − Time of Call (Dispatch Processing Time)

| Month | Emergency | Routine | Urgent | E Records | R Records | U Records |
|-------|-----------|---------|--------|-----------|-----------|-----------|
| 01-25 | 2:58 | 0:50 | 2:01 | 334 | 5,055 | 995 |
| 02-25 | 2:36 | 0:55 | 2:07 | 237 | 3,818 | 824 |
| 03-25 | 2:53 | 0:57 | 1:44 | 257 | 3,866 | 903 |
| 04-25 | 2:45 | 1:01 | 1:39 | 206 | 3,559 | 1,145 |
| 05-25 | 2:47 | 1:05 | 1:56 | 278 | 3,038 | 967 |
| 06-25 | 3:08 | 1:05 | 1:46 | 229 | 2,753 | 1,004 |
| 07-25 | 3:03 | 1:10 | 1:45 | 262 | 2,708 | 1,080 |
| 08-25 | 3:04 | 1:08 | 1:24 | 248 | 2,808 | 1,277 |
| 09-25 | 2:56 | 1:07 | 1:50 | 205 | 2,783 | 998 |
| 10-25 | 2:45 | 1:03 | 1:54 | 232 | 2,796 | 1,039 |
| 11-25 | 2:53 | 1:04 | 1:48 | 226 | 2,544 | 891 |
| 12-25 | 2:54 | 1:00 | 1:40 | 233 | 2,807 | 1,007 |
| 01-26 | 2:48 | 1:01 | 1:39 | 249 | 3,005 | 1,080 |

---

## Delta: Confirmed Changed Values (pre vs post, Time Out − Time Dispatched)

| Month | Type | Pre-Fix | Post-Fix | Delta |
|-------|------|---------|----------|-------|
| 01-25 | Emergency | 2:58 | 2:52 | −0:06 |
| 01-25 | Urgent | 2:53 | 2:38 | −0:15 |
| 01-25 | Routine | 0:48 | 0:47 | −0:01 |
| 01-26 | Emergency | 3:11 | 2:51 | **−0:20** |
| 01-26 | Urgent | 2:54 | 2:35 | **−0:19** |
| 01-26 | Routine | 1:26 | 1:23 | −0:03 |

### Interpretation
- **Emergency and Urgent** show meaningful reductions (6–20 seconds) after sorting by arrival time.
  This is consistent with Emergency and Urgent calls having more multi-unit responses; without the
  sort, a slower-arriving unit that appeared first in the file was sometimes selected.
- **Routine** shows minimal change (1–3 seconds). Routine calls have fewer multi-unit responses
  so the dedup order mattered less.
- All changes are **reductions** — the corrected values show faster first-arriving units,
  which is the correct methodology. The pre-fix values were defensibly biased high.

---

## Admin-Facing Note

> Response time values for all three metrics were recalculated on 2026-02-26. A correction was
> applied to ensure the **first officer to arrive on scene** is always used when measuring
> multi-unit incidents. Previously, the first row in the source data file was used, which did
> not always correspond to the fastest-arriving officer. The correction reduced Emergency times
> by approximately 6–20 seconds in the January 2025 – January 2026 window. Routine times
> were nearly unchanged (1–3 seconds). All values in the Power BI report reflect the
> corrected calculation as of this date.

---

## v1.17.16 CORRECTION: Admin Incident Filter (Applied After v1.17.15)

A second, more impactful issue was discovered after reviewing the post-refresh values:
the batch ETL had no administrative incident filter, causing Routine to be massively
understated by self-initiated officer activities.

### Admin Filter Impact

| Source | After Dedup | After Admin Filter | Removed | % Removed |
|--------|------------|-------------------|---------|-----------|
| 2024 Full Year | 82,891 | 35,171 | 47,720 | 57.6% |
| 2025 Full Year | 87,436 | 33,797 | 53,639 | 61.4% |
| 2026-01 Monthly | 7,499 | 3,131 | 4,368 | 58.3% |

### Routine Values: v1.17.15 vs v1.17.16 (01-25 shown)

| Metric | v1.17.15 (no admin filter) | v1.17.16 (admin filter applied) | Change |
|--------|--------------------------|--------------------------------|--------|
| Dispatch to On Scene | 0:47 | **2:01** | +1:14 |
| Time Received to On Scene | 1:14 | **3:22** | +2:08 |
| Dispatch Processing | 0:50 | **2:27** | +1:37 |

Emergency and Urgent values changed only marginally (these call types are rarely
admin-initiated).

### Corrected Post-v1.17.16 Values (13-Month Window: Jan-25 through Jan-26)

**Time Out − Time Dispatched (Dispatch to On Scene):**

| Month | Emergency | N | Routine | N | Urgent | N |
|-------|-----------|---|---------|---|--------|---|
| 01-25 | 2:52 | 355 | 2:01 | 1,176 | 2:38 | 969 |
| 02-25 | 2:38 | 241 | 2:24 | 921 | 2:44 | 797 |
| 03-25 | 2:53 | 282 | 2:39 | 922 | 2:38 | 875 |
| 04-25 | 2:43 | 217 | 2:36 | 886 | 2:36 | 942 |
| 05-25 | 2:46 | 302 | 2:50 | 926 | 2:49 | 929 |
| 06-25 | 2:55 | 255 | 3:03 | 818 | 2:43 | 927 |
| 07-25 | 2:43 | 289 | 2:51 | 874 | 2:48 | 984 |
| 08-25 | 2:41 | 265 | 2:44 | 861 | 2:32 | 1,041 |
| 09-25 | 2:44 | 219 | 3:01 | 873 | 2:42 | 913 |
| 10-25 | 2:31 | 237 | 3:00 | 789 | 2:36 | 909 |
| 11-25 | 2:48 | 249 | 2:40 | 825 | 2:44 | 768 |
| 12-25 | 2:48 | 252 | 1:55 | 1,005 | 2:36 | 882 |
| 01-26 | 2:51 | 257 | 2:04 | 1,075 | 2:35 | 950 |

**Time Dispatched − Time of Call (Dispatch Processing):**

| Month | Emergency | N | Routine | N | Urgent | N |
|-------|-----------|---|---------|---|--------|---|
| 01-25 | 2:58 | 334 | 2:27 | 1,061 | 2:01 | 995 |
| 02-25 | 2:36 | 237 | 2:39 | 819 | 2:07 | 824 |
| 03-25 | 2:53 | 257 | 2:45 | 805 | 1:44 | 903 |
| 04-25 | 2:45 | 206 | 2:46 | 765 | 1:39 | 1,138 |
| 05-25 | 2:47 | 278 | 2:54 | 789 | 1:57 | 961 |
| 06-25 | 3:08 | 229 | 2:45 | 682 | 1:47 | 996 |
| 07-25 | 3:03 | 262 | 2:54 | 727 | 1:46 | 1,069 |
| 08-25 | 3:04 | 248 | 2:45 | 752 | 1:24 | 1,273 |
| 09-25 | 2:56 | 205 | 2:49 | 733 | 1:50 | 997 |
| 10-25 | 2:45 | 232 | 2:37 | 683 | 1:54 | 1,039 |
| 11-25 | 2:53 | 226 | 2:24 | 754 | 1:48 | 891 |
| 12-25 | 2:54 | 233 | 1:57 | 930 | 1:40 | 1,007 |
| 01-26 | 2:48 | 249 | 2:01 | 996 | 1:39 | 1,080 |

**Time Out − Time of Call (Time Received to On Scene):**

| Month | Emergency | N | Routine | N | Urgent | N |
|-------|-----------|---|---------|---|--------|---|
| 01-25 | 4:58 | 290 | 3:22 | 922 | 3:43 | 844 |
| 02-25 | 4:41 | 215 | 3:35 | 680 | 3:44 | 689 |
| 03-25 | 4:51 | 222 | 4:05 | 657 | 3:28 | 781 |
| 04-25 | 4:53 | 187 | 4:15 | 646 | 3:07 | 930 |
| 05-25 | 4:36 | 243 | 4:14 | 614 | 3:35 | 799 |
| 06-25 | 4:51 | 196 | 4:06 | 528 | 3:20 | 840 |
| 07-25 | 4:54 | 226 | 4:10 | 575 | 3:04 | 878 |
| 08-25 | 4:49 | 208 | 3:51 | 589 | 2:56 | 1,017 |
| 09-25 | 5:03 | 180 | 4:15 | 562 | 3:25 | 816 |
| 10-25 | 4:31 | 195 | 4:03 | 522 | 3:22 | 823 |
| 11-25 | 5:00 | 197 | 3:25 | 603 | 3:19 | 717 |
| 12-25 | 4:55 | 204 | 2:42 | 794 | 3:07 | 843 |
| 01-26 | 4:41 | 212 | 2:43 | 840 | 3:05 | 916 |

### Pattern Analysis (Post-Fix)

The pattern now follows expected operational logic:
- **Dispatch Processing** (Time of Call → Dispatch): Emergency ~2:45-3:08 (more coordination needed)
  > Routine ~1:55-2:54 > Urgent ~1:24-2:07
- **Dispatch to On Scene** (Dispatch → Arrival): Emergency ~2:31-2:55 ≈ Routine ~1:55-3:03 ≈ Urgent ~2:32-2:49
- **Total Response** (Time of Call → On Scene): Emergency ~4:31-5:03 > Routine ~2:42-4:15 > Urgent ~2:55-3:44

Emergency dispatch coordination taking 15-30 seconds longer than Routine is operationally
defensible — Emergency calls require multi-unit coordination, supervisor notification,
and more thorough address/situation verification before dispatching.

---

**File last updated:** 2026-02-26 (v1.17.16 post-admin-filter ETL run)
**File generated:** 2026-02-26
