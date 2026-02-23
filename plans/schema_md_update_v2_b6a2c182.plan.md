---
name: Schema MD Update V2
overview: Rewrite Assignment_Master_SCHEMA.md to reflect the V3_FINAL.xlsx state — 25 columns (down from 42), standardized rank/title/team enumerations, updated validation code, 10-entry version history, and corrected maintenance procedures.
todos:
  - id: rewrite-schema-md
    content: "Rewrite 09_Reference/Personnel/Assignment_Master_SCHEMA.md: all 16 sections updated per V3_FINAL.xlsx state"
    status: completed
  - id: create-personnel-subdir-md
    content: Create 09_Reference/Standards/Personnel/ subdirectory and copy updated Assignment_Master_SCHEMA.md into it (human/AI-readable mirror)
    status: completed
  - id: create-json-schema
    content: "Create 09_Reference/Standards/Personnel/assignment_master.schema.json: formal JSON Schema with type/enum/pattern for all 25 columns, following cad_export.schema.json convention"
    status: completed
isProject: false
---

# Assignment_Master_SCHEMA.md — V2 Update Plan

## Files being created / updated

- **UPDATE** `[09_Reference/Personnel/Assignment_Master_SCHEMA.md](C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_SCHEMA.md)` — canonical human-readable schema (V2 rewrite)
- **NEW** `09_Reference/Standards/Personnel/` — subdirectory (does not yet exist)
- **NEW** `09_Reference/Standards/Personnel/Assignment_Master_SCHEMA.md` — mirror copy of the updated .md (matches `cad_data_dictionary_ai.md` role)
- **NEW** `09_Reference/Standards/Personnel/assignment_master.schema.json` — formal JSON Schema for all 25 columns (matches `cad_export.schema.json` role)

## Standards directory convention (existing pattern)


| File                            | Role                         | Audience           |
| ------------------------------- | ---------------------------- | ------------------ |
| `cad_export.schema.json`        | Machine-readable JSON Schema | Validation scripts |
| `cad_data_dictionary_ai.md`     | Flat human/AI reference      | Claude / humans    |
| `timereport_export.schema.json` | Machine-readable JSON Schema | Validation scripts |


Personnel will follow the same pattern inside a `Personnel\` subdirectory, since it may grow (future schema revisions, patrol roster schema, etc.).

## What changes (section by section)

**Header / file metadata**

- Title: `Assignment_Master_V2.csv Schema Documentation` → `Assignment_Master_V3_FINAL.xlsx Schema Documentation (V2)`
- File: `Assignment_Master_V2.csv` → `Assignment_Master_V3_FINAL.xlsx`
- Last Updated: `2026-02-05` (add)
- Record count: `168` → `166` with explanation (6 dupes removed, 4 probationary added via POSS)
- Add: Sheet Name = `Assignment_Master_V2`, Table Name = `Assignment_Master_V2`

**Column structure — complete overhaul**

- Old: ~10 "essential" + handful of "additional" columns, mentions WG1–WG5, POSS_CONTRACT_TYPE, seniority cols
- New: Full 25-column numbered table with type, null count, and description
- Add column-change summary: removed 17 cols, renamed 3, added 2 (CODE, WORKING_GROUP)

**Valid RANK values**

- Old: 13 values, inconsistent format (`Sgt.`  with trailing space, `Captain`, `Chief` )
- New: 14 standardized values with "from" notes; adds `C.O.` and `HCOP`; removes trailing-space variants
- Add TITLE vs RANK distinction note (Detectives have TITLE=DET., RANK=P.O.)

**New section — Valid TITLE values**

- 15 values: `P.O., SGT., LT., CAPT., CHIEF, DET., SPO II, SPO III, C.O., CLK, PEO, DPW, TM, PLA, HCOP`

**Valid TEAM values**

- Old: sample list of ~10 values
- New: full 37-value categorized list (Patrol 14, Investigative 5, Ops & Support 12, Admin 4, Civilian 2)

**New section — Valid CONTRACT_TYPE values**

- Replaces old `POSS_CONTRACT_TYPE` reference
- 9 values with descriptions

**New section — Valid WG4 values**

- A1–A4, B1–B4 with note: patrol only, null for all others

**FULL_NAME format update**

- Old: `Last, First MI` format (Smith, John P)
- New: `TITLE FIRST LAST BADGE` format (P.O. JANN ABERDE 386), with unbadged example

**Validation code**

- Old: `pd.read_csv('Assignment_Master_V2.csv')`, basic badge/team sets
- New: `pd.read_excel('Assignment_Master_V3_FINAL.xlsx', sheet_name='Assignment_Master_V2')`, updated sets including VALID_RANKS, sworn_officers filter

**Data quality notes**

- Old: 3 vague notes about trailing spaces, badge format, nulls
- New: 8 specific notes including RANK 100% populated, 20 STANDARD_NAME gaps, WG2 typo (RECODS), TITLE vs RANK distinction for Wanda Rivera, date storage as Excel serial numbers

**Trim candidates**

- Old: references deleted columns (seniority, workgroup, WG4/WG5, old renamed cols)
- New: current candidates only (WG4 ~100 nulls, CONFLICT_RESOLUTION ~50, CODE ~15, WORKING_GROUP redundancy, 20 STANDARD_NAME gaps)

**Related files**

- Old: `Assignment_Master_V2.csv` listed as canonical
- New: `Assignment_Master_V3_FINAL.xlsx` as canonical; V2.csv and V2.xlsx moved to "previous (archived)"; add `POSS_EMPLOYEE.xlsx` as Turn 9 source

**Version history**

- Old: 1 entry (v1.0.0 only)
- New: 10 entries from v1.0.0 → v3.2.0 covering all 11 turns

**Drift detection**

- Old: 3 general bullet points, reference to external script file
- New: 5 specific items including STANDARD_NAME gaps, with live detection code (cad_badges / master_badges set diff)

**Maintenance procedures**

- Old: 2 basic procedures (Add, Mark Inactive)
- New: 3 procedures (Add with 6 steps, Mark Inactive, Update Squads with 3 steps) + contact line

