# Claude Code — Skill Hardening Fixup + CAD Parser
# Hackensack PD ETL Workspace | Follow-up to 2026-03-30 hardening session | v3.0
# Combines: skill fixup pass + new parse_cad_assignment.py capability

==================================================
CONTEXT — READ BEFORE STARTING
==================================================

Read these files in full before touching anything:
  09_Reference/Personnel/claude.md         — Personnel pipeline rules
  09_Reference/Personnel/README.md         — Architecture and workflow
  09_Reference/Personnel/scripts/README.md — Existing script inventory
  09_Reference/Personnel/docs/POSS_RECONCILIATION_WORKFLOW.md
  scripts/path_config.py                   — Path resolution (use get_onedrive_root())
  .claude/commands/preflight.md            — Current skill file
  .claude/commands/sync-personnel.md       — Current skill file
  docs/SKILL_HARDENING_MASTER.md           — Global tracker
  docs/skill_memory/preflight_MEMORY.md
  docs/skill_memory/sync-personnel_MEMORY.md

GLOB every path before using it in code. Never assume a path exists.
Badge numbers MUST be treated as strings — preserve leading zeros.
Never modify Assignment_Master_V2.csv, Assignment_Master_GOLD.xlsx, or config/scripts.json.

==================================================
ITEM 1 (MINOR): Fix stale example in preflight.md
==================================================

File: .claude/commands/preflight.md

The example output block (Step 6) shows:
  [PASS] Assignment_Master_V2.csv (247 rows)

Change to:
  [PASS] Assignment_Master_V2.csv (171 rows, columns: BADGE_NUMBER LAST_NAME FIRST_NAME WG2 RANK)

Note: 171 is the actual count confirmed during hardening. The number is dynamic
(script reports whatever it finds); this is cosmetic only — the script is already correct.

Update docs/skill_memory/preflight_MEMORY.md: mark this item resolved.

==================================================
ITEM 2A: Fix export paths in preflight.md
==================================================

File: .claude/commands/preflight.md

The Step 2 path table contains WRONG paths. Replace with CONFIRMED paths from disk:

| Pipeline | Correct Path |
|---|---|
| Overtime | 05_EXPORTS/_Overtime/export/month/{YYYY}/{YYYY}_{MM}_otactivity.xlsx |
| TimeOff | 05_EXPORTS/_Time_Off/export/month/{YYYY}/{YYYY}_{MM}_timeoffactivity.xlsx |
| Arrests | GLOB actual path — confirm before writing |
| Response Times | GLOB actual path — confirm before writing |
| Summons | GLOB actual path — confirm before writing |
| Community Eng | GLOB actual path — confirm before writing |

IMPORTANT: Before writing any path into the skill file, GLOB it to confirm it exists.
Do not change Overtime/TimeOff — those are confirmed correct above.
For all others, glob and verify, then update if wrong.

==================================================
ITEM 2B: Add Overtime + TimeOff check to Pre_Flight_Validation.py
==================================================

File: scripts/Pre_Flight_Validation.py

The script currently does NOT check for Overtime or TimeOff exports.

Add checks using these confirmed path patterns:
  05_EXPORTS/_Overtime/export/month/{YEAR}/{YEAR}_{MM:02d}_otactivity.xlsx
  05_EXPORTS/_Time_Off/export/month/{YEAR}/{YEAR}_{MM:02d}_timeoffactivity.xlsx

Where {YEAR} and {MM} are extracted from the --report-month argument (e.g., 2026-02).

Rules:
1. Resolve 05_EXPORTS via get_onedrive_root() (already used in the script)
2. Match using glob pattern: {YEAR}_{MM:02d}*otactivity* and *timeoffactivity*
3. Report [PASS] if file found, [WARN] if directory exists but no monthly file found,
   [FAIL] only if the parent year directory doesn't exist at all
4. A missing monthly file = WARN, not FAIL (overtime may not be ready on day 1)
5. Do NOT break any currently passing checks

After editing, test with:
  python scripts/Pre_Flight_Validation.py --report-month 2026-02

Capture: exact command, exit code, and relevant output lines for the memory file.
Note: Both 2026-02 and 2026-03 export files exist on disk (March is partial/testing).
Expect [PASS] for both months.

Update docs/skill_memory/preflight_MEMORY.md with:
  - Iteration history entry for this fixup
  - Evidence: command, exit code, output snippet

==================================================
ITEM 3: Add sync mode safety note to sync-personnel.md
==================================================

File: .claude/commands/sync-personnel.md

Add a WARNING block under the ## For `sync`: section:

  > ⚠️ WRITE OPERATION — This will overwrite Assignment_Master_V2.csv.
  > 
  > Before running sync:
  > - Verify Assignment_Master_GOLD.xlsx is up to date (this is the source)
  > - The sync script reads from: 09_Reference/Personnel/Assignment_Master_GOLD.xlsx
  >   (sheet: Assignment_Master_V2)
  > - A timestamped backup of GOLD is automatically saved to:
  >   09_Reference/Personnel/Archive/ before any CSV is overwritten
  > - A backup of the previous CSV is saved to:
  >   09_Reference/Personnel/backups/ before overwrite
  >
  > The sync script does NOT read from CAD or POSS directly.
  > It only reads GOLD.xlsx and writes V2.csv + schema.

Update docs/skill_memory/sync-personnel_MEMORY.md:
  - Mark remaining gap "sync mode not live-tested" as "documented; deferred by design"
  - Add reusable lesson: sync reads GOLD.xlsx → not CAD, not POSS directly

==================================================
ITEM 4 (NEW): Build parse_cad_assignment.py
==================================================

Create: 09_Reference/Personnel/scripts/parse_cad_assignment.py

PURPOSE:
  Compare a CAD "Assign Shift" CSV export against Assignment_Master_V2.csv.
  Produces a Personnel Change Report: new badges, possible reassignments, possible departures.
  This is a READ-ONLY diagnostic — it never modifies GOLD, CSV, or any source file.

SOURCE DATA CONTEXT:
  The CAD export is saved to:
    C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Assignment_Resource\
  File naming convention: {YYYY}_{MM}_{DD}_{HH}_{mm}_{ss}_assignment.csv
  Example: 2026_03_30_18_49_30_assignment.csv

  The CSV has NO HEADER ROW. Column order (11 columns, always fixed):
    Col 0  → Car              (patrol car/radio car number; often blank)
    Col 1  → Date             (assignment start or hire date; often blank)
    Col 2  → Date1DayNew      (snapshot date — all rows same date YYYY-MM-DD)
    Col 3  → Officer          (e.g. "P.O. Frank Cavallo 253" — rank + name + badge at end)
    Col 4  → OfficerRank      (e.g. "P.O", "Sgt", "Det", "HCOP", "CLK", "PEO")
    Col 5  → SecondaryOfficer (usually blank)
    Col 6  → ShiftStatus      ("On Duty" / "Off Duty")
    Col 7  → Squad            (CAD squad code — see mapping below)
    Col 8  → Unit             (police radio number; 99.9% of the time = badge number)
    Col 9  → Weapon           (usually blank)
    Col 10 → Zone             (patrol zone assignment)

  Badge extraction logic (in priority order):
    1. Parse last whitespace-separated token from Officer field
       e.g. "P.O. Frank Cavallo 253" → badge = "253"
    2. If Officer is blank, use Unit field value
    3. If both Officer and Unit are blank → skip row (equipment/filler row, not a person)
    4. Cross-check: if Officer-badge ≠ Unit (when both populated), log as DATA_NOTE,
       trust Officer-badge as primary (Unit is radio number, Officer field is authoritative
       for identity)

  Rows to SKIP entirely:
    - OfficerRank is blank AND Officer is blank or whitespace-only
    - These are equipment/zone placeholder rows, not people

CAD SQUAD → WG2 MAPPING:
  Use this lookup when comparing CAD Squad to Assignment Master WG2:

  CAD_TO_WG2 = {
    "A1": "PATROL DIVISION",  "A2": "PATROL DIVISION",
    "A3": "PATROL DIVISION",  "A4": "PATROL DIVISION",
    "B1": "PATROL DIVISION",  "B2": "PATROL DIVISION",
    "B3": "PATROL DIVISION",  "B4": "PATROL DIVISION",
    "DET":      "DETECTIVE BUREAU",
    "TRF":      "TRAFFIC BUREAU",
    "SSOCC":    "SSOCC",
    "STA":      "STACP",
    "CSB":      "CSB",
    "REMU":     "RECODS AND EVIDENCE MANAGEMENT",
    "COMM ENG": "Office of Community and Engagement",
    "ESU":      "PATROL DIVISION",
    "ADMIN":    None,   # command staff — WG2 varies, do not flag as mismatch
    "TRN":      None,   # training unit — no fixed WG2
    "HCOP":     "TRAFFIC BUREAU",
  }
  # If Squad not in mapping → flag as UNKNOWN_SQUAD in report, do not assume WG2

SCRIPT BEHAVIOR:

  Usage:
    python scripts/parse_cad_assignment.py [--cad PATH_TO_CSV] [--master PATH_TO_CSV]

  Defaults:
    --cad:    auto-discover the MOST RECENT *_assignment.csv in
              {onedrive_root}/05_EXPORTS/_Assignment_Resource/
              (NOT in _processed/ subfolder)
    --master: {personnel_root}/Assignment_Master_V2.csv

  Path resolution:
    Use get_onedrive_root() from scripts/path_config.py (already in PYTHONPATH for
    scripts in 09_Reference/Personnel/scripts/).
    Personnel root = parent of scripts/ directory (BASE_DIR pattern — see sync_assignment_master.py).
    Import path_config by appending the 06_Workspace_Management/scripts/ dir to sys.path,
    OR copy the get_onedrive_root() approach from the existing Personnel scripts.

    IMPORTANT: Check how existing scripts in 09_Reference/Personnel/scripts/ resolve
    the OneDrive root before writing new code. Follow the same pattern exactly.

  Output — print to stdout, structured as:

    =====================================
    CAD Assignment Personnel Change Report
    Snapshot date: {Date1DayNew from CSV}
    CAD file: {filename}
    Master: Assignment_Master_V2.csv ({N} active records)
    =====================================

    SECTION 1 — NEW BADGES (in CAD, not in Master)
    These officers appear in CAD but have no matching badge in the Assignment Master.
    Action: Review and add to Assignment_Master_GOLD.xlsx if confirmed active.
    ------------------------------------------------------------------
    Badge  | Name (from CAD)            | Rank  | Squad | Mapped WG2
    -------|----------------------------|-------|-------|------------
    ...

    SECTION 2 — POSSIBLE REASSIGNMENTS (badge in both; Squad→WG2 differs from Master WG2)
    These officers are in both CAD and Master, but their CAD squad maps to a different WG2.
    Action: Confirm if transfer is permanent, then update GOLD.xlsx.
    Note: Skip if Squad maps to None (ADMIN, TRN) — command staff WG2 is not squad-driven.
    ------------------------------------------------------------------
    Badge  | Name (Master)              | CAD Squad | CAD→WG2        | Master WG2
    -------|----------------------------|-----------|----------------|------------
    ...

    SECTION 3 — POSSIBLE DEPARTURES (Active in Master, absent from CAD)
    These ACTIVE officers are in the Assignment Master but do not appear in the CAD snapshot.
    Action: Verify — may be on leave, furlough, or resigned. If resigned, set STATUS=INACTIVE
    in GOLD.xlsx. Do NOT delete rows.
    Note: HCOPs, PEOs, CLKs, and DPW often have no CAD entry — filter them per TITLE.
    Filter out TITLE in: HCOP, CLK, PEO, DPW, TM, PLA, CIV, C.O. (dispatch/civilian roles
    don't appear in CAD shift assignments regularly)
    ------------------------------------------------------------------
    Badge  | Name (Master)              | Title | Team          | WG2
    -------|----------------------------|-------|---------------|-----
    ...

    SECTION 4 — DATA NOTES
    Badge mismatches (Officer-badge ≠ Unit), unknown squad codes, blank-officer rows skipped.
    ------------------------------------------------------------------
    ...

    =====================================
    SUMMARY
    New badges:            {N}
    Possible reassignments:{N}
    Possible departures:   {N}  (sworn officers only)
    Data notes:            {N}
    =====================================
    NEXT STEP: Review above, edit Assignment_Master_GOLD.xlsx, then run:
      python scripts/sync_assignment_master.py

  After producing the report, move the processed CAD file to:
    {onedrive_root}/05_EXPORTS/_Assignment_Resource/_processed/
  Create _processed/ if it doesn't exist.

SAFETY RULES for this script:
  - Read-only with respect to Assignment Master and GOLD
  - The only file it writes/moves: the input CAD CSV → _processed/ (after report)
  - Never modify Assignment_Master_V2.csv, Assignment_Master_GOLD.xlsx
  - Never delete any rows — departures are INACTIVE changes, not deletes

INTEGRATION:
  After writing the script, update .claude/commands/sync-personnel.md:
  Add "cad" as a valid pipeline name for the find-unmapped action:

    ### For `find-unmapped cad`:
    Run the CAD assignment parser against the most recent export:
    ```bash
    python 09_Reference/Personnel/scripts/parse_cad_assignment.py
    ```
    Reviews the most recent *_assignment.csv in 05_EXPORTS/_Assignment_Resource/.
    Produces: new badges, possible reassignments, possible departures.
    After reviewing output, edit Assignment_Master_GOLD.xlsx, then run sync.

  Update docs/skill_memory/sync-personnel_MEMORY.md to note this mode was added.

TEST THE SCRIPT:
  Run against the existing file:
    python 09_Reference/Personnel/scripts/parse_cad_assignment.py \
      --cad "05_EXPORTS/_Assignment_Resource/2026_03_30_18_49_30_assignment.csv"

  Capture: command, exit code, Section 1/2/3 row counts as evidence.
  The file should be moved to _processed/ after running.

==================================================
SAFETY RULES (NON-NEGOTIABLE)
==================================================

1. Never mark anything PASS without captured evidence.
2. Never modify config/scripts.json.
3. Never modify production ETL scripts in 02_ETL_Scripts/.
4. Never modify Assignment_Master_V2.csv or Assignment_Master_GOLD.xlsx directly.
5. Pre_Flight_Validation.py: test after every change; confirm no regressions.
6. Surgical fixes only — do NOT re-run the full hardening loop.
7. Do NOT touch .claude/commands/fix-excel.md.
8. GLOB every path before using it in code — never assume a path exists.
9. Follow 09_Reference/Personnel/claude.md rules for all Personnel work.

==================================================
OUTPUTS REQUIRED
==================================================

1. Exact diff or replacement for each file changed (.md skill files, Pre_Flight_Validation.py).
2. Test output for Item 2B (Pre_Flight_Validation.py --report-month 2026-02).
3. parse_cad_assignment.py written and tested (command + exit code + row counts from report).
4. Updated memory files:
   - docs/skill_memory/preflight_MEMORY.md
   - docs/skill_memory/sync-personnel_MEMORY.md
5. Append "Fixup Pass v3 — 2026-03-30" to docs/SKILL_HARDENING_MASTER.md.
6. scripts/README.md in 09_Reference/Personnel/scripts/ updated with parse_cad_assignment.py entry.

==================================================
STOP CONDITION
==================================================

Stop when all items are addressed with evidence. Final report must include:

  Item 1  (preflight.md example):       resolved / skipped / blocked
  Item 2A (path table fix):              resolved / skipped / blocked
  Item 2B (overtime check in script):    resolved / skipped / blocked + test evidence
  Item 3  (sync safety note):           resolved / skipped / blocked
  Item 4  (parse_cad_assignment.py):     resolved / skipped / blocked + test evidence
