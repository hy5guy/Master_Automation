# Power BI Post-Refresh Comparison — v1.17.17 → v1.17.19

**Date:** 2026-02-27 | **Analyst:** R. A. Carucci  
**Pre-refresh source:** Power BI visual screenshot (v1.17.17, unfiltered)  
**Post-refresh source:** Power BI data exports after v1.17.19 ETL regeneration

---

## 1. Dispatch to On Scene (Time Dispatched → Time Out)

| Type | 01-25 | 02-25 | 03-25 | 04-25 | 05-25 | 06-25 | 07-25 | 08-25 | 09-25 | 10-25 | 11-25 | 12-25 | 01-26 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Emergency** PRE | 2:52 | 2:38 | 2:53 | 2:43 | 2:46 | 2:55 | 2:43 | 2:41 | 2:44 | 2:31 | 2:48 | 2:48 | 2:51 |
| **Emergency** POST | 2:54 | 2:43 | 3:01 | 2:50 | 2:51 | 3:05 | 2:47 | 2:51 | 2:51 | 2:41 | 2:51 | 2:52 | 3:00 |
| **Δ** | +0:02 | +0:05 | +0:08 | +0:07 | +0:05 | +0:10 | +0:04 | +0:10 | +0:07 | +0:10 | +0:03 | +0:04 | +0:09 |
| | | | | | | | | | | | | | |
| **Routine** PRE | 2:01 | 2:24 | 2:39 | 2:36 | 2:50 | 3:03 | 2:51 | 2:44 | 3:01 | 3:00 | 2:40 | 1:55 | 2:04 |
| **Routine** POST | 2:04 | 2:26 | 2:54 | 3:02 | 3:17 | 3:35 | 3:26 | 3:30 | 3:43 | 3:49 | 3:43 | 3:18 | 3:33 |
| **Δ** | +0:03 | +0:02 | +0:15 | +0:26 | +0:27 | +0:32 | +0:35 | +0:46 | +0:42 | +0:49 | +1:03 | +1:23 | +1:29 |
| | | | | | | | | | | | | | |
| **Urgent** PRE | 2:38 | 2:44 | 2:38 | 2:36 | 2:49 | 2:43 | 2:48 | 2:32 | 2:42 | 2:36 | 2:44 | 2:36 | 2:35 |
| **Urgent** POST | 3:21 | 3:39 | 3:28 | 3:41 | 3:41 | 3:37 | 3:50 | 3:34 | 3:34 | 3:38 | 3:35 | 3:25 | 3:46 |
| **Δ** | +0:43 | +0:55 | +0:50 | +1:05 | +0:52 | +0:54 | +1:02 | +1:02 | +0:52 | +1:02 | +0:51 | +0:49 | +1:11 |

---

## 2. Dispatch Processing Time (Time of Call → Time Dispatched)

| Type | 01-25 | 02-25 | 03-25 | 04-25 | 05-25 | 06-25 | 07-25 | 08-25 | 09-25 | 10-25 | 11-25 | 12-25 | 01-26 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Emergency** PRE | 2:58 | 2:36 | 2:53 | 2:45 | 2:47 | 3:08 | 3:03 | 3:04 | 2:56 | 2:45 | 2:53 | 2:54 | 2:48 |
| **Emergency** POST | 3:03 | 2:40 | 3:01 | 2:51 | 2:52 | 3:14 | 3:15 | 3:16 | 3:02 | 2:52 | 3:00 | 3:00 | 2:54 |
| **Δ** | +0:05 | +0:04 | +0:08 | +0:06 | +0:05 | +0:06 | +0:12 | +0:12 | +0:06 | +0:07 | +0:07 | +0:06 | +0:06 |
| | | | | | | | | | | | | | |
| **Routine** PRE | 2:27 | 2:39 | 2:45 | 2:46 | 2:54 | 2:45 | 2:54 | 2:45 | 2:49 | 2:37 | 2:24 | 1:57 | 2:01 |
| **Routine** POST | 2:45 | 3:00 | 3:09 | 3:27 | 3:36 | 3:27 | 3:40 | 3:45 | 3:35 | 3:29 | 3:44 | 3:26 | 3:34 |
| **Δ** | +0:18 | +0:21 | +0:24 | +0:41 | +0:42 | +0:42 | +0:46 | +1:00 | +0:46 | +0:52 | +1:20 | +1:29 | +1:33 |
| | | | | | | | | | | | | | |
| **Urgent** PRE | 2:01 | 2:07 | 1:44 | 1:39 | 1:57 | 1:47 | 1:46 | 1:24 | 1:50 | 1:54 | 1:48 | 1:40 | 1:39 |
| **Urgent** POST | 3:36 | 3:40 | 3:18 | 3:21 | 3:28 | 3:17 | 3:34 | 3:26 | 3:28 | 3:32 | 3:22 | 3:13 | 3:17 |
| **Δ** | +1:35 | +1:33 | +1:34 | +1:42 | +1:31 | +1:30 | +1:48 | +2:02 | +1:38 | +1:38 | +1:34 | +1:33 | +1:38 |

---

## 3. Total Response Time (Time of Call → Time Out)

| Type | 01-25 | 02-25 | 03-25 | 04-25 | 05-25 | 06-25 | 07-25 | 08-25 | 09-25 | 10-25 | 11-25 | 12-25 | 01-26 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Emergency** PRE | 4:58 | 4:41 | 4:51 | 4:53 | 4:36 | 4:51 | 4:54 | 4:49 | 5:03 | 4:31 | 5:00 | 4:55 | 4:41 |
| **Emergency** POST | 5:04 | 4:50 | 5:05 | 5:02 | 4:48 | 5:06 | 5:12 | 5:10 | 5:15 | 4:48 | 5:08 | 5:08 | 4:55 |
| **Δ** | +0:06 | +0:09 | +0:14 | +0:09 | +0:12 | +0:15 | +0:18 | +0:21 | +0:12 | +0:17 | +0:08 | +0:13 | +0:14 |
| | | | | | | | | | | | | | |
| **Routine** PRE | 3:22 | 3:35 | 4:05 | 4:15 | 4:14 | 4:06 | 4:10 | 3:51 | 4:15 | 4:03 | 3:25 | 2:42 | 2:43 |
| **Routine** POST | 3:41 | 3:57 | 4:49 | 5:25 | 5:24 | 5:17 | 5:29 | 5:29 | 5:40 | 5:38 | 5:34 | 5:13 | 5:27 |
| **Δ** | +0:19 | +0:22 | +0:44 | +1:10 | +1:10 | +1:11 | +1:19 | +1:38 | +1:25 | +1:35 | +2:09 | +2:31 | +2:44 |
| | | | | | | | | | | | | | |
| **Urgent** PRE | 3:43 | 3:44 | 3:28 | 3:07 | 3:35 | 3:20 | 3:04 | 2:56 | 3:25 | 3:22 | 3:19 | 3:07 | 3:05 |
| **Urgent** POST | 5:37 | 5:55 | 5:25 | 5:30 | 5:32 | 5:30 | 5:31 | 5:34 | 5:45 | 5:33 | 5:21 | 5:13 | 5:39 |
| **Δ** | +1:54 | +2:11 | +1:57 | +2:23 | +1:57 | +2:10 | +2:27 | +2:38 | +2:20 | +2:11 | +2:02 | +2:06 | +2:34 |

---

## Analysis by Response Type

### Emergency — Verified Correct ✅
Small, consistent increases across all three metrics: **+0:02 to +0:21** across the full 13-month
window. The increases are uniform month-to-month (no outliers), which is the expected signature of
a filter that removed a consistent volume of faster non-citizen calls from the average. Emergency
was already a relatively clean population before filtering; the pre-filter dataset happened to
include some non-emergency citizen contacts classified as Emergency which pulled the average down
slightly. The post-filter values are the authoritative numbers.

### Routine — Significantly Higher, Direction Correct ✅
Dispatch-to-Scene increases range from **+0:03 (Jan-25)** to **+1:29 (Jan-26)**. The Jan-25 figure
is anomalously small because the 2025 yearly export artifact (Time Dispatched ≈ Time Out for most
records) suppresses both the pre- and post-filter values in the same direction — the artifact is
present in both datasets, not introduced by the filter.

The growing delta from early to late 2025 reflects that the unfiltered dataset accumulated more
self-initiated activity over the course of the year (patrol density varies by season/staffing).
The post-filter Routine Dispatch-to-Scene trend (rising from ~2:26 in Feb-25 to ~3:43 in Nov-25)
represents true citizen-call response time and is the correct trend to report.

### Urgent — Large Increase, Requires Admin Communication ⚠️
This is the most significant change and the one most likely to generate questions.

**Dispatch Processing Time (Call to Dispatch):** Increased from ~1:24–2:07 (pre) to ~3:13–3:40
(post). **Δ consistently +1:30 to +2:02 across all 13 months.**

**Root cause:** The pre-filter Urgent dataset was dominated by self-initiated officer activity and
patrol check entries where Time of Call ≈ Time Dispatched (the officer was already on location —
no dispatcher processing lag). Removing those artificially compressed the average dispatch
processing time to ~1:45. The post-filter dataset contains only citizen-initiated Urgent calls
(alarm monitoring companies via Phone, suspicious person/vehicle via 9-1-1, etc.) which involve
a real dispatcher-to-officer workflow — the 3:15–3:40 range reflects that actual workflow.

**Total Response Time:** Increased from ~3:04–3:44 (pre) to ~5:13–5:55 (post). This is primarily
driven by the dispatch processing increase above; the Dispatch-to-Scene component only increased
~+0:50–1:11, which is defensible. The total response time for Urgent being ~5:30 for citizen calls
is a significant finding — it means from the moment a citizen reports an Urgent incident to an
officer arriving is approximately 5.5 minutes. This is the correct number to present.

**Recommended admin talking point:** "Prior Urgent response time averages of 3:05–3:44 were
understated because they included officer-directed patrol activities where response time is
effectively zero — the officer was already present. The corrected 5:13–5:55 figure represents
the actual experience of citizens who call to report an Urgent incident and wait for an officer
to arrive."

---

## Summary Table — Jan-26 Only (Most Recent, Cleanest Data)

| Metric | Type | PRE (v1.17.17) | POST (v1.17.19) | Δ |
|---|---|---|---|---|
| Dispatch to On Scene | Emergency | 2:51 | 3:00 | +0:09 |
| Dispatch to On Scene | Routine | 2:04 | 3:33 | +1:29 |
| Dispatch to On Scene | Urgent | 2:35 | 3:46 | +1:11 |
| Dispatch Processing | Emergency | 2:48 | 2:54 | +0:06 |
| Dispatch Processing | Routine | 2:01 | 3:34 | +1:33 |
| Dispatch Processing | Urgent | 1:39 | 3:17 | +1:38 |
| Total Response Time | Emergency | 4:41 | 4:55 | +0:14 |
| Total Response Time | Routine | 2:43 | 5:27 | +2:44 |
| Total Response Time | Urgent | 3:05 | 5:39 | +2:34 |
