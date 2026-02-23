---
name: Docs Update & M Code Fix
overview: Update all stale project documentation to reflect the current Feb 20, 2026 state, add a new M Code audit guide, and deliver a structured Claude AI prompt to implement the ReportMonth parameter fix across all 20+ affected M code files.
todos:
  - id: update-summary-md
    content: "Update SUMMARY.md: bump to v1.16.0, 2026-02-20, fix Next Steps, integrate v1.15.9 section, add Phase 2 table"
    status: pending
  - id: update-claude-md
    content: "Update Claude.md: add v1.16.0 Recent Updates entry, update system status block, add M_CODE_DATETIME_FIX_GUIDE reference, clean up appended entries"
    status: pending
  - id: update-phase2-roadmap
    content: "Update Phase_2_Remediation_Roadmap.md: insert Priority 0 M Code ReportMonth fix above current priorities"
    status: pending
  - id: create-mcode-fix-guide
    content: "Create docs/M_CODE_DATETIME_FIX_GUIDE.md: full audit table, reference implementation, deployment steps, monthly workflow"
    status: pending
  - id: fix-overrides-script
    content: "Fix scripts/run_summons_with_overrides.py: rename POSS_CONTRACT_TYPE → CONTRACT_TYPE, remove WG5 key from override dict"
    status: pending
  - id: archive-add-traffic
    content: Move scripts/add_traffic_officers.py to scripts/_archive/ (deprecated — officers already added, references deleted columns WG5/POSS_CONTRACT_TYPE)
    status: pending
  - id: update-summons-name-doc
    content: "Update docs/CLAUDE_AI_SUMMONS_NAME_NORMALIZATION_PROMPT.md: replace 'Proposed 4-Digit Format' with 'STANDARD_NAME' (column was renamed)"
    status: pending
isProject: false
---

# Docs Update, Fix Summary & Claude Prompt

## Current State Gaps Found

### Docs that are stale / incomplete

- `**SUMMARY.md**` — Header says v1.15.7 / 2026-02-13; bottom appends v1.15.9 from 2026-02-18 but "Next Steps" section still lists basic setup tasks from Dec 2025. Phase 2 status and M-code DateTime issue are absent.
- `**Claude.md**` — Missing the v1.16.x entry for the `DateTime.LocalNow()` architectural flaw. "Current System Status" block still references v1.15.7. The 2026-02-17 & 2026-02-18 entries are appended raw at the bottom rather than integrated.
- `**docs/Phase_2_Remediation_Roadmap.md**` — Created 2026-02-19 and largely current, but **missing the M Code ReportMonth parameter fix entirely** — the single highest-impact architectural issue in the project.

### New doc needed

- `**docs/M_CODE_DATETIME_FIX_GUIDE.md`** — Full audit table + implementation blueprint for the ReportMonth parameter replacement.

---

## What Needs to Be Fixed (Priority-Ordered)

### Priority 0 — M Code `DateTime.LocalNow()` → `ReportMonth` Parameter (CRITICAL)

**Why it's #1:** Every query using `DateTime.LocalNow()` produces a different rolling window each month it is refreshed. January 2026 reports will show different data if opened in March. This breaks historical data integrity — the core requirement.

**Scope:** 20 files, 35+ occurrences


| File                                                          | Occurrences | Type                       |
| ------------------------------------------------------------- | ----------- | -------------------------- |
| `m_code/2026_02_19_jan_m_codes.m`                             | 15+         | Consolidated multi-query   |
| `m_code/___Overtime_Timeoff_v3.m`                             | 1           | Rolling window             |
| `m_code/___Arrest_Categories_FIXED.m`                         | 1           | Previous-month filter      |
| `m_code/___Top_5_Arrests_FIXED.m`                             | 1           | Previous-month filter      |
| `m_code/___Cost_of_Training.m`                                | 1           | Rolling window             |
| `m_code/esu/ESU_13Month.m`                                    | 1           | Rolling window             |
| `m_code/esu/MonthlyActivity.m`                                | 1           | Rolling window             |
| `m_code/stacp/STACP_pt_1_2_FIXED.m`                           | 1           | Rolling window             |
| `m_code/detectives/___Detectives_2026.m`                      | 3           | Rolling window + timestamp |
| `m_code/detectives/___Det_case_dispositions_clearance_2026.m` | 1           | Rolling window             |
| `m_code/___Summons_All_Bureaus_STANDALONE.m`                  | 1           | Previous-month calc        |
| `m_code/___Summons_Top5_Moving_STANDALONE.m`                  | 1           | Previous-month calc        |
| `m_code/2026_02_16_detectives.m`                              | 3           | Rolling window             |


**Fix pattern:**

```m
// OLD — time-sensitive, breaks historical integrity
NowDT = DateTime.LocalNow(),

// NEW — locked to reporting period; set once per cycle
ReportMonth = #date(2026, 1, 1),  // ← Only line changed each month
NowDT       = DateTime.From(ReportMonth),
```

### Priority 1 — Community Engagement Validation (PENDING)

- 2 files created but unvalidated; 13-month window unconfirmed
- Run `community_engagement_diagnostic.ps1` + `community_engagement_data_flow_check.py`

### Priority 2 — Summons Derived Outputs Schema Fix (BLOCKED)

- Script expects `IS_AGGREGATE`, `TICKET_COUNT` columns — currently absent
- Blocking 4 Power BI visuals (`wg2_movers_parkers_nov2025.csv`, top5 files, backfill summary)

### Priority 3 — Hardcoded Paths in M Code (8 instances)

- `RobertCarucci` and `C:\Dev\` paths in summons, ESU, ResponseTime M files
- Must use `path_config.py`-equivalent variable or OneDrive-relative path

### Priority 4 — Hardcoded Column Lists (2 instances)

- `___Patrol` and `___Traffic` missing `01-26` column
- Columns are currently hardcoded; need dynamic unpivot

### Priority 5 — Response Times Historical Backfill (PENDING)

- Nov 2024 – Dec 2025 months need first-arriving-unit recalculation

---

## Doc Update Plan

### 1. `SUMMARY.md`

- Bump version to **v1.16.0**, update `Last Updated` to 2026-02-20
- Replace stale "Next Steps" with Phase 2 task list (M Code fix as #1)
- Integrate the raw-appended v1.15.9 section into proper `## Recent Updates` format
- Add Phase 2 status table (5/6 workflows, M code DateTime issue identified)

### 2. `Claude.md`

- Add `## Recent Updates (2026-02-20) / v1.16.0` section documenting the DateTime.LocalNow() architectural flaw and ReportMonth fix scope
- Update "Current System Status" version block to v1.16.0
- Add `docs/M_CODE_DATETIME_FIX_GUIDE.md` to the "Detailed guides" reference list
- Clean up the raw-appended 2026-02-17/18 entries (integrate into proper section)

### 3. `docs/Phase_2_Remediation_Roadmap.md`

- Insert new **Priority 0: M Code ReportMonth Parameter Fix** block above current Priority 1
- Status: IDENTIFIED — 20 files, 35+ occurrences
- Estimated time: 4–6 hours
- Mark as blocking all historical data integrity

### 4. NEW: `docs/M_CODE_DATETIME_FIX_GUIDE.md`

- Full audit table of all 20 affected files with line numbers and fix type
- Reference implementation (ReportMonth parameter pattern)
- Step-by-step deployment instructions
- Monthly workflow update procedure (change `ReportMonth` date each cycle)

---

## Assignment_Master_V2.csv — Script Compatibility Verification (2026-02-20)

### CSV structure after Claude-in-Excel cleanup (25 columns):

`REF_NUMBER, FULL_NAME, TITLE, FIRST_NAME, LAST_NAME, BADGE_NUMBER, PADDED_BADGE_NUMBER, TEAM, WG1, WG2, WG3, WG4, CONTRACT_TYPE, STANDARD_NAME, CONFLICT_RESOLUTION, CODE, WORKING_GROUP, DOB, JOINED_SERVICE, SGT, LT, CAPT, CHIEF, STATUS, RANK`

### Key column changes from old schema:

- `WG5` — DELETED (was empty for all patrol officers)
- `POSS_CONTRACT_TYPE` — RENAMED to `CONTRACT_TYPE`
- `Proposed 4-Digit Format` — RENAMED to `STANDARD_NAME`
- `FullName`, `Badge`, `Status` (old lowercase), `DEP_CHIEF`, `Notes` — DELETED (replaced by FULL_NAME, BADGE_NUMBER, STATUS)
- 10 `_seniority` columns — DELETED

### Script compatibility matrix:


| Script                                   | Columns Used                                                      | Result                                                |
| ---------------------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------- |
| `summons_etl_normalize.py`               | `PADDED_BADGE_NUMBER`, `WG1–3`, `TEAM`, `RANK`, `TITLE`, `STATUS` | All present ✅                                         |
| `diagnose_summons_assignment_mapping.py` | `PADDED_BADGE_NUMBER`, `WG2`                                      | All present ✅                                         |
| `fix_summons_wg2_from_assignment.py`     | `PADDED_BADGE_NUMBER`, `WG2`                                      | All present ✅                                         |
| `remerge_wg2.py`                         | `PADDED_BADGE_NUMBER`, `WG2`, `TEAM`, `STATUS`                    | Columns OK ✅ (path is `RobertCarucci` — pre-existing) |
| `check_traffic_badges_in_master.py`      | `PADDED_BADGE_NUMBER`, `WG2`                                      | All present ✅                                         |
| `verify_traffic_updates.py`              | `PADDED_BADGE_NUMBER`, `WG2`                                      | All present ✅                                         |
| `Pre_Flight_Validation.py`               | File path only                                                    | ✅                                                     |
| `**run_summons_with_overrides.py`**      | Injects `WG5`, `POSS_CONTRACT_TYPE` into override dict            | **Needs 2-line fix** ⚠️                               |
| `**add_traffic_officers.py`**            | Writes `WG5`, `POSS_CONTRACT_TYPE` as new row fields              | **Deprecated — archive** ⚠️                           |


### Scripts to fix:

`**scripts/run_summons_with_overrides.py` lines 52–53:**

```python
# BEFORE
"WG5": "",
"POSS_CONTRACT_TYPE": "PARKING ENFORCEMENT OFF",

# AFTER
"CONTRACT_TYPE": "PARKING ENFORCEMENT OFF",   # WG5 line removed
```

`**docs/CLAUDE_AI_SUMMONS_NAME_NORMALIZATION_PROMPT.md` lines 5 and 152:**

- Replace `Proposed 4-Digit Format` → `STANDARD_NAME` (column was renamed by Claude-in-Excel)

`**scripts/add_traffic_officers.py`:**

- Move to `scripts/_archive/` — the 4 officers it adds (0387, 0839, 0844, 9110) are already in the CSV; running it again would try to write columns `WG5` and `POSS_CONTRACT_TYPE` which no longer exist, causing a crash.

---

## Claude AI Prompt for M Code Fix

After confirming the plan, I will deliver this as a ready-to-paste prompt for the Hackensack PD | Data Ops Claude project.

```
You are the Lead Data Operations Engineer for the Hackensack PD Master Automation suite.

TASK: Fix all M code queries in the project that use DateTime.LocalNow() for rolling 13-month window
calculations or previous-month filters. Replace each occurrence with a ReportMonth parameter so that
historical monthly reports remain frozen to their specific reporting period.

ARCHITECTURAL PROBLEM:
DateTime.LocalNow() recalculates on every refresh. A January 2026 report refreshed in March 2026
will shift its 13-month window to Feb 2025 – Feb 2026, dropping January 2025 data and adding
February 2026 data. This breaks the core requirement: historical reports must show the same data
regardless of when they are refreshed.

STANDARD FIX PATTERN (apply to every affected query):
// Step 1 — Add this at the top of the let block (or as a shared Power BI parameter)
ReportMonth = #date(2026, 1, 1),   // ← UPDATE THIS ONE LINE each new reporting cycle

// Step 2 — Replace DateTime.LocalNow() with DateTime.From(ReportMonth)
NowDT  = DateTime.From(ReportMonth),  // was: DateTime.LocalNow()

// Step 3 — All downstream calculations (CurrY, CurrM, EndY, EndM, StartY, StartM,
//           StartDate, EndDate, MonthList, etc.) remain UNCHANGED — they derive from NowDT

AFFECTED FILES (fix all of these):
1.  m_code/___Overtime_Timeoff_v3.m              — Line 28:  NowDT = DateTime.LocalNow()
2.  m_code/___Arrest_Categories_FIXED.m          — Line 44:  Prev = Date.AddMonths(Date.From(DateTime.LocalNow()), -1)
3.  m_code/___Top_5_Arrests_FIXED.m              — Line 53:  (same pattern as above)
4.  m_code/___Top_5_Arrests_DIAGNOSTIC.m         — Line 59:  (diagnostic; fix for consistency)
5.  m_code/___Cost_of_Training.m                 — Line 27:  rolling window
6.  m_code/esu/ESU_13Month.m                     — Line 76:  rolling window
7.  m_code/esu/MonthlyActivity.m                 — Line 66:  rolling window
8.  m_code/stacp/STACP_pt_1_2_FIXED.m           — Line 16:  rolling window
9.  m_code/stacp/STACP_DIAGNOSTIC.m              — Line 16:  rolling window (diagnostic)
10. m_code/detectives/___Detectives_2026.m        — Lines 105, 186, 187, 195
11. m_code/detectives/___Det_case_dispositions_clearance_2026.m — Line 238
12. m_code/___Summons_All_Bureaus_STANDALONE.m   — Line 8:   Prev = Date.AddMonths(Date.From(DateTime.LocalNow()), -1)
13. m_code/___Summons_Top5_Moving_STANDALONE.m   — Line 8:   (same)
14. m_code/2026_02_16_detectives.m               — Lines 98, 171, 173, 181
15. m_code/2026_02_19_jan_m_codes.m              — 15+ occurrences across multiple embedded queries

HEADER REQUIREMENT:
Every modified file must update its header timestamp. Use this format at the top:
// 2026-02-20-HH-MM-SS (EST)
// Project Name: Hackensack PD | Data Ops & ETL Remediation
// File Name: m_code/[filename].m
// Author: R. A. Carucci
// Purpose: [existing purpose line — do not change]

SECONDARY FIXES (do in same pass if time permits):
A. Hardcoded paths — replace C:\Users\RobertCarucci\ or C:\Dev\ paths with
   C:\Users\carucci_r\OneDrive - City of Hackensack\ equivalent in:
   - m_code/summons/*.m (4 files)
   - m_code/esu/ESU_13Month.m
   - m_code/___ResponseTimeCalculator.m (2 occurrences)

B. Missing column — add "01-26" to hardcoded column lists in:
   - ___Patrol query (wherever column list stops at 12-25)
   - ___Traffic query (same)

DELIVERABLE FORMAT:
For each file, provide:
1. The complete updated M code (not just the diff) with correct header
2. A one-line summary of what changed
3. After all files, a deployment checklist:
   - [ ] Copy each .m file content into the matching Power BI query editor
   - [ ] Set ReportMonth = #date(2026, 1, 1) for January 2026 cycle
   - [ ] Refresh each query and verify 13-month window: Jan 2025 – Jan 2026
   - [ ] Save Power BI Desktop file
   - [ ] Update ReportMonth to #date(2026, 2, 1) when running the February 2026 cycle

CURRENT REPORTING PERIOD: January 2026 → ReportMonth = #date(2026, 1, 1)
```

