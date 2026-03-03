# Why the Three Response Time Visuals Show Different Record Counts

**Audience:** Anyone reviewing the Response Time page in Power BI who notices that
Emergency January 2026 shows 257, 212, and 249 records across the three visuals.

---

## Short Answer

Each of the three metrics requires **two different timestamps** to both be present
and result in a plausible response time. Because not every CAD record has all three
timestamps populated, each metric ends up with a slightly different count of usable
records. This is expected behavior — not a data error.

---

## The Three Metrics and What They Need

| Visual | Metric | Timestamps Required |
|--------|--------|-------------------|
| Dispatch to On Scene | Time Out − Time Dispatched | `Time Out` AND `Time Dispatched` |
| From Time Received to On Scene | Time Out − Time of Call | `Time Out` AND `Time of Call` |
| Dispatch Processing Time | Time Dispatched − Time of Call | `Time Dispatched` AND `Time of Call` |

A record is only included in a metric if:
1. **Both** required timestamps are present (not null or unparseable).
2. The computed difference is **between 0 and 10 minutes** (ETL outlier filter).

---

## Why Counts Differ: A Concrete Example (January 2026, Emergency)

| Metric | Records Used | Reason Some Records Are Excluded |
|--------|-------------|----------------------------------|
| Time Out − Time Dispatched | 257 | Records missing `Time Dispatched` or with outlier result excluded |
| Time Out − Time of Call | 212 | Records missing `Time of Call` or with outlier result excluded |
| Time Dispatched − Time of Call | 249 | Different overlap of valid `Time Dispatched` and `Time of Call` |

CAD records commonly have:
- `Time Out` populated but `Time of Call` missing (if call was self-initiated or transferred)
- `Time Dispatched` populated but `Time of Call` missing or vice versa
- All three timestamps present but one metric's difference falls outside the 0–10 min window

---

## Why These Are NOT a Closed Loop

Administration should NOT attempt to reconcile the three counts by subtraction or
addition. The algebraically correct identity would be:

> **(Time Out − Time of Call)** = **(Time Out − Time Dispatched)** + **(Time Dispatched − Time of Call)**

This holds **at the individual record level**, but only when all three timestamps are
present for that record. The three visuals use different subsets of records, so the
averages and counts do not form a closed loop at the aggregate level.

**Analogy:** Imagine measuring average wait time, average service time, and average total
time in three separate lines at a restaurant — only counting customers where each
measurement was successfully captured. The averages will not necessarily add up because
you measured different (though overlapping) groups of customers each time.

---

## Is This Defensible for Reporting?

**Yes.** This is standard practice in emergency services analytics:
- Each metric is internally consistent and independently accurate.
- The differences in record count are driven by data availability in the CAD system,
  not by methodology errors.
- The first-arriving unit is used for all three metrics (deduplicated by ReportNumberNew
  after sorting by Time Out, as of v1.17.15).
- The 0–10 minute filter removes impossible values (negative times, system errors,
  calls held more than 10 minutes before response).

---

## What to Say to Administration

> "The three response time metrics each require different pairs of timestamps from the
> CAD system. Not every call has all three timestamps populated. Each metric uses only
> the calls where its specific timestamps are available and the result is within a
> reasonable range. The counts differ because the records with valid data for each
> metric are not identical — they are overlapping subsets of the same underlying dataset.
> The numbers are not meant to add up to each other; each metric stands on its own."

---

**Version:** 1.17.15 | **Date:** 2026-02-26 | **Author:** R. A. Carucci
