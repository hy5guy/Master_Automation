# Claude Code Prompt: Power BI Data Consolidation – Execute Plan

**Role:** You are the Lead Data Operations Engineer for the Hackensack PD Master Automation suite. Execute the Power BI Data Consolidation plan step by step. Use full absolute paths. Do not skip steps.

**Workspace root:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation`

**Canonical Power BI location:** `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date`

---

## Phase 1: Pre-Migration

### Step 1.1 – Verify canonical location

Confirm these paths exist and are writable:

- `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports`
- `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill`

If either is missing, create it. Report status.

### Step 1.2 – Create merge script

Create the file:

`C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\merge_powerbi_backfill.py`

Use the reference implementation from the plan (Appendix A). Ensure:

- `ONEDRIVE_ROOT = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack")`
- `DEV_BACKFILL_DIR = ONEDRIVE_ROOT / "00_dev" / "projects" / "PowerBI_Date" / "Backfill"`
- `CANONICAL_BACKFILL_DIR = ONEDRIVE_ROOT / "PowerBI_Date" / "Backfill"`
- `LOG_DIR = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\logs")`
- `DRY_RUN = True` initially

Include `safe_copy()`, `is_valid_data_file()`, `should_overwrite()`, and full error handling for PermissionError and directory creation failures.

### Step 1.3 – Run merge script (dry run)

```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
python scripts\merge_powerbi_backfill.py
```

Verify the log at `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\logs\powerbi_backfill_merge_*.log`. Confirm MOVED, OVERWROTE, SKIPPED entries look correct.

### Step 1.4 – Run merge script (live)

Set `DRY_RUN = False` in `merge_powerbi_backfill.py`, then run again:

```powershell
python scripts\merge_powerbi_backfill.py
```

Review the log for any PermissionError or failed copies. Resolve before proceeding.

### Step 1.5 – Archive 00_dev PowerBI_Date

Create archive directory and move:

```powershell
$date = Get-Date -Format "yyyyMMdd"
$archive = "C:\Users\carucci_r\OneDrive - City of Hackensack\99_Archive\PowerBI_Date_00_dev_$date"
New-Item -ItemType Directory -Path $archive -Force
Move-Item "C:\Users\carucci_r\OneDrive - City of Hackensack\00_dev\projects\PowerBI_Date" $archive
```

### Step 1.6 – Archive C:\Dev\Power_BI_Data

```powershell
$date = Get-Date -Format "yyyyMMdd"
$archive = "C:\Users\carucci_r\OneDrive - City of Hackensack\99_Archive\Power_BI_Data_C_Dev_$date"
New-Item -ItemType Directory -Path $archive -Force
Move-Item "C:\Dev\Power_BI_Data\*" $archive -Force
```

---

## Phase 2: Add config helper and update references

### Step 2.1 – Add get_powerbi_paths() helper

Add to `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\path_config.py`:

```python
def get_powerbi_paths() -> tuple[Path, Path]:
    """Return (drop_path, backfill_root) from config/scripts.json."""
    import json
    config_path = Path(__file__).resolve().parent.parent / "config" / "scripts.json"
    with open(config_path, encoding="utf-8") as f:
        data = json.load(f)
    drop = Path(data["settings"]["powerbi_drop_path"])
    backfill = drop.parent / "Backfill"
    return drop, backfill
```

Or create `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\powerbi_paths.py` with this logic and import from there.

### Step 2.2 – Update process_powerbi_exports.py

File: `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\process_powerbi_exports.py`

Change the default `source_dir` in `process_exports()` from `AUTOMATION_ROOT / "_DropExports"` to the `powerbi_drop_path` from config. Load config and use `settings.powerbi_drop_path` as the default source.

### Step 2.3 – Update summons_backfill_merge.py

File: `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\summons_backfill_merge.py`

Change `_get_backfill_roots()` to return only the config-derived path. Remove `00_dev/projects/PowerBI_Date/Backfill` from the candidate list. Use `get_powerbi_paths()` or equivalent to get `backfill_root`.

### Step 2.4 – Update summons_derived_outputs.py

File: `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\summons_derived_outputs.py`

- Set `output_dir` from config (`powerbi_drop_path`).
- Remove `backfill = root / "00_dev" / "projects" / "PowerBI_Date" / "Backfill"` and `backfill_alt = root / "PowerBI_Date" / "Backfill"`. Use only the config-derived backfill path for candidate file lookups.

### Step 2.5 – Update remaining scripts

Apply config-derived paths to:

- `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\verify_december_2025_overtime.py`
- `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\compare_response_time_results.py`
- `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\restore_fixed_from_backfill.py` (example in docstring)
- `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\community_engagement_data_flow_check.py` (fix typo `PowerBI_Date_DropExports` → `PowerBI_Date\_DropExports`; use config)
- `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\community_engagement_diagnostic.ps1` (fix typo; read from config)
- `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\scripts\diagnose_summons_missing_months.py`

### Step 2.6 – Update documentation

- `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\docs\SUMMONS_BACKFILL_INJECTION_POINT.md` – Remove `00_dev` as preferred path.
- `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\docs\POWERBI_VISUAL_EXPORT_PIPELINE_FAQ.md` – Clarify source paths (canonical `PowerBI_Date\_DropExports`).
- `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\docs\M_CODE_IMPLEMENTATION_STEPS.md` – Replace `C:\Dev\PowerBI_Date` with canonical path.

### Step 2.7 – Git commit (single commit for rollback)

```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
git status
git add -A
git commit -m "chore: consolidate Power BI paths"
```

---

## Phase 3: Verification

### Step 3.1 – Dry run ETL

```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
.\scripts\run_all_etl.ps1 -DryRun -ValidateInputs
```

Confirm no path-related failures.

### Step 3.2 – Path checks

- Config: `Get-Content "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\config\scripts.json" | Select-String powerbi_drop` → should show `PowerBI_Date\_DropExports`
- Drop folder: `Test-Path "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports"` → True
- Backfill: `Test-Path "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill"` → True

### Step 3.3 – Power BI Desktop (manual)

Before refreshing the report:

1. Open Power BI Desktop.
2. Options > Data Load > Clear Cache.
3. Refresh the report.
4. Confirm no broken data sources.

### Step 3.4 – Power BI parameterization (optional, manual)

In Power BI Desktop, create a native parameter for the root path:

`C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date`

Update M queries to reference this parameter instead of hardcoding the path.

---

## Phase 4: Fix Power BI visuals (post-consolidation)

After consolidation, if the TEST report shows blank or incorrect visuals, use:

**`docs/PROMPT_Fix_Social_Media_MMYY_Columns.md`**

That prompt covers:

- **___Arrest_Categories** – Arrest Categories by Type and Gender (blank)
- **___Social_Media** – Missing_References; MM-YY columns
- **___Combined_Outreach_All** – Out-Reach page blank
- **Detectives Case Dispositions** – Missing 02-25, extra 03-26
- **Training Cost by Delivery** – Missing 02-25 and 02-26

Use Power BI MCP (`user-powerbi-modeling-mcp`) with the open `TEST_2026_02_Monthly_Report_TEST.pbix` file. Sync fixes to `m_code/` in Master_Automation.

---

## Rollback (if needed)

If the Power BI refresh fails:

```powershell
# Restore 00_dev from archive (replace YYYYMMDD with actual date)
Move-Item "C:\Users\carucci_r\OneDrive - City of Hackensack\99_Archive\PowerBI_Date_00_dev_YYYYMMDD" "C:\Users\carucci_r\OneDrive - City of Hackensack\00_dev\projects\PowerBI_Date"

# Revert script changes
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
git revert HEAD --no-edit
```

---

## Full path reference

| Purpose | Path |
|---------|------|
| Workspace root | `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation` |
| Config | `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\config\scripts.json` |
| Canonical Power BI | `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date` |
| Drop exports | `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports` |
| Backfill | `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill` |
| 00_dev source (pre-archive) | `C:\Users\carucci_r\OneDrive - City of Hackensack\00_dev\projects\PowerBI_Date\Backfill` |
| Logs | `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\logs` |
| Archive base | `C:\Users\carucci_r\OneDrive - City of Hackensack\99_Archive` |
