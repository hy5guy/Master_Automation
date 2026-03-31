# sync-personnel Memory

## Current Status
- Overall status: Wave A complete (read-only modes tested)
- Confidence level: High (check/compare/find-unmapped); sync mode deferred to Wave B
- Last updated: 2026-03-30
- Current iteration: 1
- Skill type: HYBRID (check/compare/find-unmapped = READ-ONLY; sync = WRITE-CAPABLE)

## Skill Contract
- Expected inputs: action keyword (check | sync | compare BADGE | find-unmapped PIPELINE)
- Expected outputs: Personnel validation results, sync status, badge lookup, unmapped badges
- Critical rules: Badge numbers as strings; never modify CSV directly; sync only via approved script
- Safety constraints: sync mode is Wave B (write-capable, isolated)

## Binary Scorecard
| Test | Result | Evidence | Gap | Next Action |
|------|--------|----------|-----|-------------|
| T1 | PASS | Skill file check/compare/find-unmapped modes match implementation. Paths to 09_Reference canonical CSV and sync script confirmed on disk. find-unmapped references diagnose_summons_blank_bureau.py (confirmed). | WG2 known-value list uses mixed-case names that don't match actual data (e.g., "Patrol Division" vs "PATROL DIVISION", "Detective Division" vs "DETECTIVE BUREAU"). Skill says "etc." which partially covers this. | Update WG2 list in skill to match actual values (edit was denied this pass; document as known gap) |
| T2 | PASS | Skill uses relative path `09_Reference/Personnel/Assignment_Master_V2.csv` (line 18), not hardcoded OneDrive. Sync script path `09_Reference/Personnel/scripts/sync_assignment_master.py` is relative. Only `carucci_r` mention (line 63) is documentation about path-agnosticism, not a hardcoded path. | None | |
| T3 | PASS | check mode: reads CSV + reports stats. compare mode: reads CSV + exports. find-unmapped: reads pipeline data + CSV + runs diagnose_summons_blank_bureau.py (confirmed read-only: only pd.read_excel + print). No write operations in any read-only mode. | None | |
| T4 | PASS | Ran check simulation against real CSV. Results: 171 rows, 25 columns, 4 blank WG2 (badges: 265/Chief Antista, NaN/DPW Caero, NaN/DPW Licata, NaN/CLK Prezioso), 16 duplicate badge rows (12 NaN badges + 4 badge 9999), 12 non-numeric badges. File last modified 2026-03-11 12:44:37. | None | |
| T5 | PASS | Output includes specific badge numbers (265, 9999, NaN), counts (171 rows, 4 blank WG2, 16 duplicates, 12 non-numeric), column names (all 25 listed), unique WG2 values (11 distinct). | None | |
| T6 | PASS | Badge loaded as dtype str via pd.read_csv(..., dtype={'BADGE_NUMBER': str}). Skill line 64: "Badge numbers should be treated as strings (preserve leading zeros)". Canonical path is 09_Reference; local copy at 06_Workspace_Management/Assignment_Master_V2.csv exists but skill correctly references 09_Reference as source of truth. | None | |
| T7 | PASS | WG2 discrepancy documented as regression item below. NaN badge entries (12 records) and badge 9999 (4 records) are data quality findings, not skill bugs. | None | |
| T8 | PASS | This file updated with full evidence. | None | |

## Iteration History
### Iteration 1 (2026-03-30) — Wave A read-only modes
- Tested: check, compare (interface review), find-unmapped (interface review + diagnose script audit)
- check mode: full pandas simulation against real data
- All read-only paths verified on disk
- No file modifications made (read-only pass)
- Edit denied for WG2 list update in skill file — documented as known gap

## Evidence Log
### T4 check mode output (2026-03-30)
```
Row count: 171
Columns (25): REF_NUMBER, FULL_NAME, TITLE, FIRST_NAME, LAST_NAME, BADGE_NUMBER,
  PADDED_BADGE_NUMBER, TEAM, WG1, WG2, WG3, WG4, CONTRACT_TYPE, STANDARD_NAME,
  CONFLICT_RESOLUTION, CODE, WORKING_GROUP, DOB, JOINED_SERVICE, SGT, LT, CAPT,
  CHIEF, STATUS, RANK

Blank WG2 (4): Badge 265 (Chief Antista), NaN (DPW Caero), NaN (DPW Licata), NaN (CLK Prezioso)
Blank WG3: 67 | Blank WG4: 118 | Blank TEAM: 0
Duplicate BADGE_NUMBER: 16 (12 NaN + 4 badge 9999)
Non-numeric badges: 12 (all NaN — civilian/non-sworn personnel without badge numbers)

Actual WG2 values in data: ADMINSTIVE COMMANDER, COMMUNICATIONS, CSB, DETECTIVE BUREAU,
  OPERATIONS COMMANDER, Office of Community and Engagement, PATROL DIVISION,
  RECODS AND EVIDENCE MANAGEMENT, SSOCC, STACP, TRAFFIC BUREAU
  (Note: "RECODS" and "ADMINSTIVE" are source-data spellings)

File last modified: 2026-03-11 12:44:37
```

### Referenced files confirmed on disk
- `09_Reference/Personnel/Assignment_Master_V2.csv` — 171 rows, 25 columns
- `09_Reference/Personnel/scripts/sync_assignment_master.py` — exists
- `06_Workspace_Management/scripts/diagnose_summons_blank_bureau.py` — exists, read-only
- `06_Workspace_Management/Assignment_Master_V2.csv` — local copy exists (not canonical)

## Regression Tests
1. **WG2 known-value mismatch**: Skill file lists "Patrol Division, Detective Division, Administrative Division, Traffic Bureau" but actual data uses ALL-CAPS and different names (PATROL DIVISION, DETECTIVE BUREAU, TRAFFIC BUREAU). No "Administrative Division" exists; closest is "ADMINSTIVE COMMANDER". Fix: update skill WG2 list to match actual values. (Edit denied this pass.)
2. **NaN badge handling**: 12 records have NaN badge numbers (civilian/non-sworn). Skill should note this is expected for non-badge personnel and not flag as errors.

## Remaining Gaps
1. ~~**WG2 list in skill file needs update**~~ — RESOLVED: updated with actual ALL-CAPS values from data
2. **sync mode** — documented with safety warning; deferred to user-initiated run by design (writes V2.csv)
3. **compare mode live test** — interface reviewed but no live badge lookup performed (would need specific badge + export files)
4. ~~**find-unmapped live test**~~ — RESOLVED: `find-unmapped cad` mode added and tested (see below)

### `find-unmapped cad` mode added (2026-03-30)
- Script: `09_Reference/Personnel/scripts/parse_cad_assignment.py`
- Test command: `python 09_Reference/Personnel/scripts/parse_cad_assignment.py --cad "05_EXPORTS/_Assignment_Resource/2026_03_30_18_49_30_assignment.csv"`
- Exit code: 0
- Results: Section 1 (new badges): 12 | Section 2 (reassignments): 5 | Section 3 (departures): 1 | Section 4 (data notes): 5
- Snapshot date: 3/29/2026 | Master: 170 active records
- CAD file moved to `_processed/` after report
- Notable findings: 7 CLK/HCOP/CIV/PEO new badges (non-sworn, no badge number — name parsed as badge); 5 badge vs Unit mismatches logged as DATA_NOTE; 1 sworn departure (badge 381 P.O. Swaby); 5 reassignments flagged (squad->WG2 differs from master WG2)

### Sync mode safety warning added (2026-03-30 fixup)
- Added write-operation warning block to skill file under `For sync:` section
- Documents: GOLD.xlsx is the source, Archive/ backup is automatic, backups/ for CSV, sync does NOT read CAD/POSS

## Reusable Lessons
1. Always load BADGE_NUMBER as str dtype to preserve leading zeros and handle NaN correctly
2. Assignment_Master has civilian records with no badge (NaN) — these appear as duplicates and non-numeric; skill should distinguish these from actual data errors
3. Source-data typos (RECODS, ADMINSTIVE) exist in the canonical CSV; do not auto-correct in validation — flag for human review
4. Sync reads GOLD.xlsx only — not CAD, not POSS directly. Those are separate reconciliation workflows.
