# 2026-02-20-00-00-00 (EST)
# Project Name: Hackensack PD | Data Ops & ETL Remediation
# File Name: docs/M_CODE_DATETIME_FIX_GUIDE.md
# Author: R. A. Carucci
# Purpose: Complete audit and implementation guide for replacing DateTime.LocalNow() with a locked ReportMonth parameter across all M code queries.

---

# M CODE DATETIME.LOCALNOW() FIX GUIDE

## The Problem

Every M code query that uses `DateTime.LocalNow()` to compute a rolling 13-month window or a previous-month filter is **time-sensitive**. When Power BI refreshes the report in a later month, the window shifts forward — silently dropping older months and including future months that have no data.

**Example — January 2026 report refreshed in March 2026:**

| | Refreshed Jan 2026 | Refreshed Mar 2026 |
|---|---|---|
| Window start | Jan 2025 | Mar 2025 |
| Window end | Jan 2026 | Feb 2026 |
| Jan 2025 data | ✅ Present | ❌ Dropped |
| Feb 2026 data | ❌ Not present | ✅ Appears (empty) |

**This violates the core requirement:** historical monthly reports must show identical data regardless of when they are refreshed.

---

## The Fix

Replace `DateTime.LocalNow()` with a `ReportMonth` parameter that is set once per reporting cycle.

### Standard Fix Pattern

```m
// ── BEFORE (time-sensitive) ──────────────────────────────────────────────
NowDT   = DateTime.LocalNow(),
CurrY   = Date.Year(NowDT),
CurrM   = Date.Month(NowDT),
EndY    = if CurrM = 1 then CurrY - 1 else CurrY,
EndM    = if CurrM = 1 then 12 else CurrM - 1,
StartY  = EndY - 1,
StartM  = EndM,

// ── AFTER (locked to reporting period) ───────────────────────────────────
ReportMonth = #date(2026, 1, 1),        // ← ONLY LINE CHANGED EACH CYCLE
NowDT   = DateTime.From(ReportMonth),   // was: DateTime.LocalNow()
CurrY   = Date.Year(NowDT),            // UNCHANGED
CurrM   = Date.Month(NowDT),           // UNCHANGED
EndY    = if CurrM = 1 then CurrY - 1 else CurrY,   // UNCHANGED
EndM    = if CurrM = 1 then 12 else CurrM - 1,       // UNCHANGED
StartY  = EndY - 1,                    // UNCHANGED
StartM  = EndM,                        // UNCHANGED
```

### For Previous-Month Filters (Arrests, Summons Standalone)

```m
// ── BEFORE ──────────────────────────────────────────────────────────────
Prev  = Date.AddMonths(Date.From(DateTime.LocalNow()), -1),
PrevY = Date.Year(Prev),
PrevM = Date.Month(Prev),

// ── AFTER ────────────────────────────────────────────────────────────────
ReportMonth = #date(2026, 1, 1),        // ← ONLY LINE CHANGED EACH CYCLE
Prev  = Date.AddMonths(ReportMonth, -1),  // was: Date.From(DateTime.LocalNow())
PrevY = Date.Year(Prev),               // UNCHANGED
PrevM = Date.Month(Prev),              // UNCHANGED
```

### Monthly Cycle Update Procedure

Each reporting cycle, update **only one line** in each affected query:

| Cycle | Value to set |
|-------|-------------|
| January 2026 | `ReportMonth = #date(2026, 1, 1)` |
| February 2026 | `ReportMonth = #date(2026, 2, 1)` |
| March 2026 | `ReportMonth = #date(2026, 3, 1)` |
| … | … |

---

## Full Audit Table — All Affected Files

| # | File | Line(s) | Pattern | Fix Type |
|---|------|---------|---------|----------|
| 1 | `m_code/___Overtime_Timeoff_v3.m` | 28 | `NowDT = DateTime.LocalNow()` | Rolling window |
| 2 | `m_code/___Arrest_Categories_FIXED.m` | 44 | `Date.From(DateTime.LocalNow())` | Previous-month filter |
| 3 | `m_code/___Top_5_Arrests_FIXED.m` | 53 | `Date.From(DateTime.LocalNow())` | Previous-month filter |
| 4 | `m_code/___Top_5_Arrests_DIAGNOSTIC.m` | 59 | `Date.From(DateTime.LocalNow())` | Diagnostic — fix for consistency |
| 5 | `m_code/___Cost_of_Training.m` | 27 | `DateTime.LocalNow()` | Rolling window |
| 6 | `m_code/esu/ESU_13Month.m` | 76 | `DateTime.LocalNow()` | Rolling window |
| 7 | `m_code/esu/MonthlyActivity.m` | 66 | `DateTime.LocalNow()` | Rolling window |
| 8 | `m_code/stacp/STACP_pt_1_2_FIXED.m` | 16 | `DateTime.LocalNow()` | Rolling window |
| 9 | `m_code/stacp/STACP_DIAGNOSTIC.m` | 16 | `DateTime.LocalNow()` | Diagnostic — fix for consistency |
| 10 | `m_code/detectives/___Detectives_2026.m` | 105, 186, 187, 195 | `DateTime.LocalNow()` | Rolling window + refresh timestamp |
| 11 | `m_code/detectives/___Det_case_dispositions_clearance_2026.m` | 238 | `DateTime.LocalNow()` | Rolling window |
| 12 | `m_code/___Summons_All_Bureaus_STANDALONE.m` | 8 | `Date.From(DateTime.LocalNow())` | Previous-month calc |
| 13 | `m_code/___Summons_Top5_Moving_STANDALONE.m` | 8 | `Date.From(DateTime.LocalNow())` | Previous-month calc |
| 14 | `m_code/2026_02_16_detectives.m` | 98, 171, 173, 181 | `DateTime.LocalNow()` | Rolling window |
| 15 | `m_code/2026_02_19_jan_m_codes.m` | 238, 744, 872, 984, 1189, 1262–1272, 1502, 1551, 1800, 1849, 2511, 2622, 3159, 3424, 3541, 3612, 3881, 4079 | Multiple patterns | Consolidated multi-query file |

**Total: 20 files, 35+ occurrences**

---

## Deployment Checklist

### Per-File Steps
- [ ] Open the Power BI Desktop file containing the query
- [ ] Open Power Query Editor → select the query
- [ ] Add `ReportMonth = #date(2026, 1, 1),` as the **first line** of the `let` block
- [ ] Replace `DateTime.LocalNow()` with `DateTime.From(ReportMonth)` (rolling window files)
- [ ] Replace `Date.From(DateTime.LocalNow())` with `ReportMonth` (previous-month filter files)
- [ ] Update the file header timestamp
- [ ] Click **Close & Apply**
- [ ] Verify the 13-month window shows Jan 2025 – Jan 2026

### Post-Fix Validation
- [ ] All affected visuals show 13-month window: Jan 2025 – Jan 2026
- [ ] Refresh again — window does NOT shift (same data on second refresh)
- [ ] Arrest Categories visual shows January 2026 data (not February)
- [ ] Overtime/TimeOff shows 13 periods starting Jan 2025
- [ ] Summons standalone files show correct previous month (January 2026)
- [ ] Detectives show Jan 2025 – Jan 2026 window

---

## Secondary Fixes (Same Pass)

### A — Hardcoded Paths (8 instances)

Replace `C:\Users\RobertCarucci\` or `C:\Dev\` with `C:\Users\carucci_r\OneDrive - City of Hackensack\` in:

| File | Lines | Old Path Fragment |
|------|-------|-------------------|
| `m_code/summons/summons_13month_trend.m` | ~3325 | `RobertCarucci` |
| `m_code/summons/summons_top5_parking.m` | ~3374 | `RobertCarucci` |
| `m_code/summons/summons_all_bureaus.m` | ~3429 | `RobertCarucci` |
| `m_code/summons/summons_top5_moving.m` | ~3549 | `RobertCarucci` |
| `m_code/esu/ESU_13Month.m` | ~4010 | `RobertCarucci` |
| `m_code/___ResponseTimeCalculator.m` | 2211, 2303 | `C:\Dev\` |

### B — Missing Column in Hardcoded Lists (2 instances)

Add `"01-26"` to the hardcoded column lists in:
- `___Patrol` query — column list currently stops at `12-25`
- `___Traffic` query — same

---

## Claude AI Fix Prompt

Use this prompt in the **Hackensack PD | Data Ops & ETL Performance** Claude project to generate the corrected M code for all files:

```
You are the Lead Data Operations Engineer for the Hackensack PD Master Automation suite.

TASK: Fix all M code queries that use DateTime.LocalNow() for rolling 13-month window
calculations or previous-month filters. Replace each occurrence with a ReportMonth parameter
so that historical monthly reports remain frozen to their specific reporting period.

ARCHITECTURAL PROBLEM:
DateTime.LocalNow() recalculates on every refresh. A January 2026 report refreshed in March
2026 shifts its 13-month window to Feb 2025–Feb 2026, dropping January 2025 data and adding
February 2026 data. Historical reports must show identical data regardless of refresh date.

STANDARD FIX PATTERN:
// Step 1 — Add at the top of the let block
ReportMonth = #date(2026, 1, 1),           // ← UPDATE THIS ONE LINE each new cycle

// Step 2 — Rolling window files
NowDT = DateTime.From(ReportMonth),        // was: DateTime.LocalNow()

// Step 2 — Previous-month filter files
Prev = Date.AddMonths(ReportMonth, -1),    // was: Date.AddMonths(Date.From(DateTime.LocalNow()), -1)

// Step 3 — ALL downstream calculations remain UNCHANGED

AFFECTED FILES (fix all):
1.  m_code/___Overtime_Timeoff_v3.m              — Line 28
2.  m_code/___Arrest_Categories_FIXED.m          — Line 44
3.  m_code/___Top_5_Arrests_FIXED.m              — Line 53
4.  m_code/___Top_5_Arrests_DIAGNOSTIC.m         — Line 59
5.  m_code/___Cost_of_Training.m                 — Line 27
6.  m_code/esu/ESU_13Month.m                     — Line 76
7.  m_code/esu/MonthlyActivity.m                 — Line 66
8.  m_code/stacp/STACP_pt_1_2_FIXED.m           — Line 16
9.  m_code/stacp/STACP_DIAGNOSTIC.m              — Line 16
10. m_code/detectives/___Detectives_2026.m        — Lines 105, 186, 187, 195
11. m_code/detectives/___Det_case_dispositions_clearance_2026.m — Line 238
12. m_code/___Summons_All_Bureaus_STANDALONE.m   — Line 8
13. m_code/___Summons_Top5_Moving_STANDALONE.m   — Line 8
14. m_code/2026_02_16_detectives.m               — Lines 98, 171, 173, 181
15. m_code/2026_02_19_jan_m_codes.m              — 15+ occurrences

HEADER REQUIREMENT — update timestamp on every modified file:
// 2026-02-20-HH-MM-SS (EST)
// Project Name: Hackensack PD | Data Ops & ETL Remediation
// File Name: m_code/[filename].m
// Author: R. A. Carucci
// Purpose: [existing purpose line — do not change]

SECONDARY FIXES (same pass):
A. Hardcoded paths — replace RobertCarucci / C:\Dev\ with carucci_r OneDrive path in:
   summons/summons_13month_trend.m, summons_top5_parking.m, summons_all_bureaus.m,
   summons_top5_moving.m, esu/ESU_13Month.m, ___ResponseTimeCalculator.m

B. Missing column — add "01-26" to hardcoded column lists in ___Patrol and ___Traffic queries

DELIVERABLE: Complete updated M code for each file + one-line change summary.
CURRENT REPORTING PERIOD: January 2026 → ReportMonth = #date(2026, 1, 1)
```

---

**Reference:** `docs/Phase_2_Remediation_Roadmap.md` — Priority 0 task  
**Last Updated:** 2026-02-20  
**Author:** R. A. Carucci
