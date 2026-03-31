Validate and sync the Assignment Master personnel file used by all ETL pipelines.

The Assignment_Master_V2.csv maps officer badge numbers to organizational units (WG2 bureau/division, WG3 section, WG4 unit, TEAM, Rank). Every ETL pipeline depends on this mapping being accurate and complete.

## Input

The user provides:
- `$ARGUMENTS` — an action keyword:
  - `check` (default) — validate the current Assignment Master
  - `sync` — run the sync script to update from source
  - `compare {badge}` — look up a specific badge across all data sources
  - `find-unmapped {pipeline}` — find badges in a pipeline's exports that aren't in the master

## Process

### For `check` (default):

1. Read `09_Reference/Personnel/Assignment_Master_V2.csv` via pandas
2. Report:
   - Total row count
   - Columns present
   - Rows with blank WG2 (should be 0)
   - Rows with blank WG3, WG4, TEAM (may be acceptable but flag)
   - Duplicate badge numbers
   - Badge format issues (non-numeric, unexpected lengths)
   - Last-modified timestamp of the file
3. Cross-reference against known organizational structure:
   - Valid WG2 values: PATROL DIVISION, DETECTIVE BUREAU, TRAFFIC BUREAU, ADMINSTIVE COMMANDER, OPERATIONS COMMANDER, COMMUNICATIONS, CSB, SSOCC, STACP, RECODS AND EVIDENCE MANAGEMENT, Office of Community and Engagement
   - Flag any WG2 values not in the known set (note: source data contains typos like "ADMINSTIVE" and "RECODS" — these are canonical spellings in the CSV)

### For `sync`:

```bash
python 09_Reference/Personnel/scripts/sync_assignment_master.py
```

Or via batch file:
```bash
09_Reference/Personnel/scripts/run_sync.bat
```

Uses `BASE_DIR = parent of scripts/` — works on both desktop and laptop.

> **WRITE OPERATION** — This will overwrite Assignment_Master_V2.csv.
>
> Before running sync:
> - Verify Assignment_Master_GOLD.xlsx is up to date (this is the source)
> - The sync script reads from: `09_Reference/Personnel/Assignment_Master_GOLD.xlsx`
>   (sheet: `Assignment_Master_V2`)
> - A timestamped backup of GOLD is automatically saved to:
>   `09_Reference/Personnel/Archive/` before any CSV is overwritten
> - A backup of the previous CSV is saved to:
>   `09_Reference/Personnel/backups/` before overwrite
>
> The sync script does NOT read from CAD or POSS directly.
> It only reads GOLD.xlsx and writes V2.csv + schema.

### For `compare {badge}`:

1. Look up the badge in Assignment_Master_V2.csv
2. Search for the same badge in recent exports:
   - Summons e-ticket exports (`05_EXPORTS/_Summons/`)
   - Overtime exports (`05_EXPORTS/_Overtime/`)
   - Arrest exports (`05_EXPORTS/_Arrest/`)
3. Report any discrepancies in name or assignment between sources

### For `find-unmapped {pipeline}`:

1. Collect all unique badges from the specified pipeline's source data
2. Compare against Assignment_Master_V2.csv
3. Report badges that appear in data but not in the master
4. For summons: also run `python scripts/diagnose_summons_blank_bureau.py`

### For `find-unmapped cad`:
Run the CAD assignment parser against the most recent export:
```bash
python 09_Reference/Personnel/scripts/parse_cad_assignment.py
```
Reviews the most recent `*_assignment.csv` in `05_EXPORTS/_Assignment_Resource/`.
Produces: new badges, possible reassignments, possible departures.
After reviewing output, edit Assignment_Master_GOLD.xlsx, then run sync.

## Critical Rules

1. Assignment_Master_V2.csv is the **single source of truth** for badge-to-unit mapping
2. The sync script is path-agnostic (works on desktop via `carucci_r` and laptop via junction)
3. Never modify Assignment_Master_V2.csv directly through this skill — only through the sync script
4. Badge numbers should be treated as strings (preserve leading zeros)
5. When reporting unmapped badges, include the name and any assignment info from the export data to help the user update the master
