# Summons Backfill – Code Injection Point

**Purpose:** Fill Department-Wide Summons data gaps for months **03-25, 07-25, 10-25, 11-25** by merging from the organized backfill folder.

---

## Where to inject (DEPLOYED)

**Script:** `02_ETL_Scripts/Summons/summons_etl_enhanced.py` (active script per config)  
**Path:** `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Summons\summons_etl_enhanced.py`

**Injection point:** After `create_unified_summons_dataset()` and before `save_to_staging()`:

1. Add `TICKET_COUNT=1` to main df (ticket-level rows)
2. Call `merge_missing_summons_months(unified_data)` from `Master_Automation/scripts/summons_backfill_merge.py`
3. The script adds `Master_Automation/scripts` to `sys.path` so the import resolves

**Note:** `main_orchestrator.py` is not used; config uses `summons_etl_enhanced.py`.

---

## Skeleton location

- **File:** `Master_Automation/scripts/summons_backfill_merge.py`
- **Function:** `merge_missing_summons_months(df, backfill_root=None, backfill_month_label="2025_12")`
- **Behavior:** Currently a no-op (returns `df` unchanged). TODO: load from `Backfill\2025_12\summons\` (or `backfill_month_label`) for the four gap months; normalize schema to match main df; ensure WG2 (Bureau) is set for backfilled rows; concatenate and return.

---

## Backfill folder layout

After `organize_backfill_exports.ps1` and any normalization:

- `PowerBI_Date\Backfill\2025_12\summons\` (or similar) should contain CSVs that can be merged for 03-25, 07-25, 10-25, 11-25.

Use the same logging style as the rest of the Summons ETL (e.g. `logging.getLogger(__name__)` or existing logger). Paths should use `ONEDRIVE_BASE` or `ONEDRIVE_HACKENSACK` env when available; see `summons_backfill_merge._get_backfill_root()`.

---

---

## Dependencies and caveats

- **Python environment:** The orchestrator uses the executable from `config/scripts.json` (`python_executable`). That environment must have `pandas` and `openpyxl` installed, or `validate_exports.py` and `summons_backfill_merge.py` will fail. Install from the repo root: `pip install -r requirements.txt`.
- **OneDrive sync:** If OneDrive is syncing `.xlsx` files while a script reads them, you may see `PermissionError`. `validate_exports.py` retries up to 3 times with a 2s delay; for other scripts, run when sync is idle or add a similar retry in production.
- **Schema drift:** If the Power BI visual export changes column names (e.g. "Sum of Value" → "Total"), update `RENAME_MAP` in `scripts/summons_backfill_merge.py`.
- **Visual export date format:** The backfill merge expects `MM-YY` (e.g. `03-25`) in gap months and in `PeriodLabel`. If Power BI is set to a different format (e.g. "March 2025"), the script logs a warning and skips the file; check logs if backfill data appears missing.
- **Memory:** Backfill CSVs are read with `low_memory=False` to reduce DtypeWarnings; for very large files, memory use may increase. Monthly exports are typically small.

*Created 2026-02-12; updated with Gemini review (centralized paths, full merge implementation).*

---

## ⚠️ Verification Note (2026-03-03)

**Review required:** Re-export all summons e-ticket data to verify counts. See `docs/SUMMONS_VERIFICATION_NOTE_2026_03.md`.
