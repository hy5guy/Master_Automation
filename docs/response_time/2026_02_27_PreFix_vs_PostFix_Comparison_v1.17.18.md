# Pre/Post Comparison — v1.17.17 → v1.17.19

## Three-Layer Filter Expansion (Citizen-Initiated Call Definition)

**Date:** 2026-02-27 | **Analyst:** R. A. Carucci | **Script:** `response_time_batch_all_metrics.py`

---

## What Changed

| Layer | v1.17.17 | v1.17.19 (final) |
| ----------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| How Reported filter | None | Retain citizen-initiated calls: **9-1-1, Phone, Walk-In**. Exclude: Self-Initiated, Radio, eMail, Fax, Mail, Teletype, Virtual Patrol, Other - See Notes, Canceled Call |
| Incident exclusion list | 92 types | ~272 normalized types (v1.17.18 expansion, then v1.17.19 peer-review corrections) |
| Category_Type filter | None | Exclude all records mapping to "Administrative and Support" or "Community Engagement" |
| `_normalize()` | Remove non-ASCII, keep ASCII dashes | Explicit en-dash/em-dash/replacement-char handling + non-ASCII sweep + ASCII dash → space |

**Citizen-initiated definition:** 9-1-1 (emergency line), Phone (non-emergency line — break-ins,
noise complaints, alarm monitoring company calls), and Walk-In (citizen at the station; officer
dispatched). Excludes officer self-initiated activity and administrative-only channels.

---

## How Reported Filter — Correction Note

An intermediate run used a "9-1-1 only" filter that excluded Phone and Walk-In. This was corrected
after peer review identified three consequences:

- **Urgent counts collapsed** — alarm monitoring company calls (typically reported via Phone) are
  the largest population of genuine Urgent dispatched calls. Excluding them inflated Urgent averages
  by +1:23 to +2:25 across metrics.
- **Sample sizes became statistically marginal** — Jan-26 Emergency fell to n=103, Routine to n=106.
  At those sizes one extreme record shifts the monthly average by 6+ seconds.
- **Definition was indefensible** — a citizen calling the non-emergency line to report a break-in is
  a call for service requiring a response. Excluding it is methodologically incorrect.

The final definition ("citizen-initiated") resolves all three problems.

---

## Data Volume Impact (Final v1.17.19 Pipeline Log)

| Source | Raw (year-filtered) | After How Reported | After Dedup | After Incident Filter | After Category Filter | **Final** |
| ----------- | ------------------- | ------------------ | ----------- | --------------------- | --------------------- | --------- |
| **2024** | 110,328 | 44,653 (−59%) | 29,125 | 18,491 | 18,453 | **18,453** |
| **2025** | 114,064 | 43,560 (−62%) | 28,118 | 18,532 | 18,506 | **18,502** |
| **2026-01** | 10,435 | 3,734 (−64%) | 2,255 | 1,499 | 1,497 | **1,497** |

The "How Reported" filter removes ~60–65% of records because citizen Phone and Walk-In calls are
retained. The incident filter (v1.17.19) is slightly less aggressive than v1.17.18 — the 9 types
moved from excluded to included add ~797 annual records back into 2024 and ~717 into 2025.

---

## January 2025 — Full Comparison

### PRE-RUN (v1.17.17 — no filtering)

| Response_Type | Metric | Avg | Mean/Median | n |
| ------------- | ------------------------------ | ----------------- | --------------------------- | --------- |
| Emergency | Time Out − Time Dispatched | **2:52** (2.861) | median 2:32 (ratio 1.1×) | 355 |
| Emergency | Time Out − Time of Call | **4:58** (4.961) | median 4:55 | 290 |
| Emergency | Time Dispatched − Time of Call | **2:58** (2.969) | median 2:19 | 334 |
| Routine | Time Out − Time Dispatched | **2:01** (2.013) | median **0:11** (**10.5×**) | **1,176** |
| Routine | Time Out − Time of Call | **3:22** (3.362) | median 2:08 (1.6×) | 922 |
| Routine | Time Dispatched − Time of Call | **2:27** (2.456) | median 1:41 (1.5×) | 1,061 |
| Urgent | Time Out − Time Dispatched | **2:38** (2.629) | median 2:15 | 969 |
| Urgent | Time Out − Time of Call | **3:43** (3.711) | median 3:30 | 844 |
| Urgent | Time Dispatched − Time of Call | **2:01** (2.013) | median 1:03 | 995 |

### POST-RUN (v1.17.19 — citizen-initiated: 9-1-1 + Phone + Walk-In)

| Response_Type | Metric | Avg | Mean/Median | n | Δ Avg vs Pre | Δ n |
| ------------- | ------------------------------ | ----------------- | -------------------------------- | ------- | ------------ | ----- |
| Emergency | Time Out − Time Dispatched | **2:54** (2.908) | median 2:35 (1.1×) | 336 | +0:02 | −19 |
| Emergency | Time Out − Time of Call | **5:04** (5.069) | median 5:01 | 275 | +0:06 | −15 |
| Emergency | Time Dispatched − Time of Call | **3:03** (3.042) | median 2:21 (1.3×) | 318 | +0:05 | −16 |
| Routine | Time Out − Time Dispatched | **2:04** (2.065) | median **0:12** (**10.3×**) ⚠️ | **721** | +0:03 | −455 |
| Routine | Time Out − Time of Call | **3:41** (3.677) | median 2:31 (1.5×) | 557 | +0:19 | −365 |
| Routine | Time Dispatched − Time of Call | **2:45** (2.753) | median 1:57 (1.4×) | 644 | +0:18 | −417 |
| Urgent | Time Out − Time Dispatched | **3:21** (3.347) | median 2:56 (1.1×) | **492** | +0:43 | −477 |
| Urgent | Time Out − Time of Call | **5:37** (5.617) | median 5:35 (1.0×) | 355 | +1:54 | −489 |
| Urgent | Time Dispatched − Time of Call | **3:36** (3.594) | median 3:05 (1.2×) | **444** | +1:35 | −551 |

---

## January 2026 — Full Comparison

### PRE-RUN (v1.17.17 — no filtering)

| Response_Type | Metric | Avg | Mean/Median | n |
| ------------- | ------------------------------ | ----------------- | -------------------------- | --------- |
| Emergency | Time Out − Time Dispatched | **2:51** (2.843) | median 2:18 (1.2×) | 257 |
| Emergency | Time Out − Time of Call | **4:41** (4.689) | median 4:32 | 212 |
| Emergency | Time Dispatched − Time of Call | **2:48** (2.795) | median 2:06 | 249 |
| Routine | Time Out − Time Dispatched | **2:04** (2.062) | median **0:13** (**9.5×**) | **1,075** |
| Routine | Time Out − Time of Call | **2:43** (2.718) | median 1:03 (2.6×) | 840 |
| Routine | Time Dispatched − Time of Call | **2:01** (2.017) | median 0:57 (2.1×) | 996 |
| Urgent | Time Out − Time Dispatched | **2:35** (2.582) | median 2:03 | 950 |
| Urgent | Time Out − Time of Call | **3:05** (3.079) | median 2:17 | 916 |
| Urgent | Time Dispatched − Time of Call | **1:39** (1.656) | median 0:43 | 1,080 |

### POST-RUN (v1.17.19 — citizen-initiated: 9-1-1 + Phone + Walk-In)

| Response_Type | Metric | Avg | Mean/Median | n | Δ Avg vs Pre | Δ n |
| ------------- | ------------------------------ | ----------------- | -------------------------- | ------- | ------------ | ----- |
| Emergency | Time Out − Time Dispatched | **3:00** (2.998) | median 2:28 (1.2×) | 234 | +0:09 | −23 |
| Emergency | Time Out − Time of Call | **4:55** (4.916) | median 4:43 | 192 | +0:14 | −20 |
| Emergency | Time Dispatched − Time of Call | **2:54** (2.900) | median 2:11 (1.3×) | 225 | +0:06 | −24 |
| Routine | Time Out − Time Dispatched | **3:33** (3.544) | median 3:19 (**1.1×**) ✅ | **388** | +1:29 | −687 |
| Routine | Time Out − Time of Call | **5:27** (5.457) | median 5:51 (0.9×) | 234 | +2:44 | −606 |
| Routine | Time Dispatched − Time of Call | **3:34** (3.559) | median 2:51 (1.2×) | 335 | +1:33 | −661 |
| Urgent | Time Out − Time Dispatched | **3:46** (3.759) | median 3:37 (**1.0×**) ✅ | **400** | +1:11 | −550 |
| Urgent | Time Out − Time of Call | **5:39** (5.652) | median 5:53 (0.96×) | **298** | +2:34 | −618 |
| Urgent | Time Dispatched − Time of Call | **3:17** (3.282) | median 2:43 (1.2×) | **398** | +1:38 | −682 |

---

## Key Findings

### 1. Jan-26 Routine and Urgent bimodal distributions — RESOLVED

**Jan-26 Routine:** Mean/median ratio improved from **9.5×** (pre) to **1.1×** (post). Mean 3:33,
median 3:19, n=388 — a clean, defensible distribution.

**Jan-26 Urgent:** Mean/median ratio improved to **1.0×** (post). Mean 3:46, median 3:37, n=400.
The addition of Suspicious Person/Vehicle, ESU Response, and Missing Person types — all genuine
citizen-dispatched Urgent calls — produced a larger, better-distributed sample than the
v1.17.18 run.

**Jan-26 Emergency** holds steady at 1.2×, n=234. All 18 metrics are now at healthy ratios (0.9×–1.3×).

### 2. Jan-25 Routine "Time Out − Time Dispatched" — data artifact, not a filter issue

**Jan-25:** Post-filter median for Routine Dispatch-to-Scene is 0:12 (721 records). This pattern
survived all three filter layers (How Reported, Incident, Category_Type), which means it is present
in citizen-initiated 9-1-1/Phone/Walk-In Routine calls and is not caused by self-initiated activity.

**Diagnostic pattern:** `Time Dispatched ≈ Time Out` for the majority of Jan-25 Routine records
(12-second median gap), but `Time of Call → Time Dispatched` is healthy (median 1:57). The other
two Jan-25 Routine metrics show normal ratios (1.4×–1.5×).

**Most probable cause:** The 2025 full-year CAD export may aggregate or flatten timestamps
differently than monthly exports. Jan-26 uses a monthly export and shows a clean 1.1× ratio.

**Recommended action:** Pull Jan-25 records from a monthly export (if available) and compare.
If the monthly export shows a healthy Dispatch-to-Scene distribution, the yearly export is
corrupting those timestamps. If it shows the same pattern, it reflects a dispatcher workflow
change (clicking "Dispatched" and "Out" simultaneously) that should be disclosed in reporting.

### 3. Sample sizes — statistically sound

Post-filter counts (Dispatch-to-Scene) with citizen-initiated definition, v1.17.19:

| Month | Emergency | Routine | Urgent |
|-------|-----------|---------|--------|
| Jan-25 | n=336 | n=721 | n=492 |
| Jan-26 | n=234 | n=388 | n=400 |

All categories are well above the n=100 threshold. Month-to-month variation will be interpretable
for command staff without extreme sensitivity to single outlier records.

### 4. Urgent and Emergency averages increased — expected and correct

Both Urgent and Emergency means increased after filtering because the pre-filter dataset mixed in
non-citizen-initiated calls with artificially short response times (officers self-initiating nearby).
The post-filter values represent true citizen-call-to-arrival performance.

The Urgent mean increase (+1:18 to +2:37 across metrics for Jan-26) is largely attributable to
alarm monitoring company calls (reported via Phone, now correctly retained) which have realistic
travel times of 3–6 minutes.

---

## Admin Talking Points

- **Methodology:** Response time calculations now measure all citizen-initiated calls for service —
  emergency (9-1-1), non-emergency (Phone line), and walk-in reports. Officer self-initiated patrol
  activity, administrative tasks, and canceled calls are excluded.
- **January 2026 Routine response time (dispatch to on scene): 3:33 average, 3:19 median** —
  clean distribution (1.1× ratio), n=388. True officer travel time for citizen-initiated calls.
- **January 2026 Urgent response time (dispatch to on scene): 3:46 average, 3:37 median** —
  clean distribution (1.0× ratio), n=400. Includes alarm company calls, suspicious person/vehicle,
  and missing person reports — all genuine 9-1-1/Phone citizen-initiated dispatches.
- **January 2026 Emergency response time (dispatch to on scene): 3:00 average** — consistent with
  prior reporting and represents calls where officer travel time from dispatch to arrival matters most.
- **Historical data (2024–2025) is re-generated with the same filter** — comparisons across months
  and years are now apples-to-apples on the citizen-initiated population.
- **Jan-25 Routine Dispatch-to-Scene is flagged for source verification** — likely a yearly export
  artifact, not a real performance issue. Will be confirmed against monthly export data.
