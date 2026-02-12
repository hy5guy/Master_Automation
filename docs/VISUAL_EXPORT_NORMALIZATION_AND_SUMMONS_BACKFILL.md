# Visual Export Normalization & Summons Backfill

**Status:** Visual Export Normalization integrated into orchestrator (2026-02-12). Summons backfill and M code updates are follow-up work.

---

## 1. Implemented: Visual Export Normalization in Orchestrator

### What was done

- **`scripts/run_all_etl.ps1`** now includes a **Visual Export Normalization** phase that runs **after all ETL scripts** and **before the Execution Summary**.
- **Detection:** The script uses `powerbi_drop_path` from `config/scripts.json` and scans for files matching `*Monthly Accrual and Usage Summary*.csv`.
- **Execution:** For each match it runs:
  ```text
  python scripts/normalize_visual_export_for_backfill.py --input "<FullPath>" --output "<FullPath>"
  ```
  Using the same path for `--input` and `--output` normalizes the file **in place** in `_DropExports`, so it is ready for `organize_backfill_exports.ps1` to move into the Backfill tree.
- **Logging:** Uses existing `Write-Step`, `Write-Success`, `Write-Log`; normalization events are written to `logs/YYYY-MM-DD_HH-mm-ss_ETL_Run.log`.
- **Error handling:** If normalization fails for a file, the error is logged and the orchestrator continues with the next file (no stop on error).
- **Dry run:** With `-DryRun`, the script lists which files would be normalized and does **not** run the Python script.

### Why this helps

- **Automation:** No need to run the normalization script manually after an export.
- **Consistency:** Files that reach `Backfill\` (after you run `organize_backfill_exports.ps1`) have a consistent structure (e.g. normalized `PeriodLabel`, cleaned headers), reducing Power BI refresh issues.
- **Traceability:** Normalization runs and failures appear in the central ETL log.

### References

- `scripts/run_all_etl.ps1` – normalization block before `# Summary`
- `scripts/normalize_visual_export_for_backfill.py` – `--input` / `--output` for in-place use
- `config/scripts.json` – `settings.powerbi_drop_path`
- `docs/VISUAL_BACKFILL_AND_EXPORTS_FINDINGS_2026_02_10.md` – backfill and CSV structure context

---

## 2. Follow-up: Summons Backfill & Data Gaps

The **Department-Wide Summons** report is missing four months (03-25, 07-25, 10-25, 11-25). The 2025_12 visual export can be used to fill those gaps once the rest of the pipeline is updated.

### Already in place

- **Normalization:** Raw visual exports in `_DropExports` are now normalized by the orchestrator; after organizing, backfill CSVs in e.g. `Backfill\2025_12\summons\` (or equivalent) will have a consistent structure (e.g. no raw "Sum of Value" / "Sum of [Month]" where the pipeline expects `Value` / `PeriodLabel`).

### Remaining work (optional prompts)

1. **Summons ETL merging**
   - In the Summons ETL (e.g. `main_orchestrator.py` or related scripts), add logic to **merge** backfill data for the missing months (03-25, 07-25, 10-25, 11-25) from the organized backfill (e.g. `Backfill\2025_12\summons\` or as organized by `organize_backfill_exports.ps1`).
   - Ensure the pipeline prioritizes or merges these backfill months with existing e-ticket exports so the 13-month window is complete.

2. **Power Query M code**
   - Update the **___Summons** query (e.g. `m_code/summons_all_bureaus.m`) to:
     - Dynamically detect and load the missing months from the Backfill folder when they are not present in the primary staging workbook.
     - Ensure the **WG2 (Bureau)** column is correctly populated for backfilled rows to avoid "Blank Bureau" in visuals.

3. **Verification**
   - After changes, run:
     - `scripts/compare_summons_deptwide.py` – validate gap months match 2025_12 visual export totals.
     - `scripts/diagnose_summons_missing_months.py` – confirm all 13 months in the rolling window are present.

### Files to reference for Summons follow-up

- `config/scripts.json`
- `m_code/summons_all_bureaus.m` (or the active ___Summons M query)
- `scripts/normalize_visual_export_for_backfill.py`
- `docs/VISUAL_BACKFILL_AND_EXPORTS_FINDINGS_2026_02_10.md`

### Expected outcome after full implementation

- **Gap closure:** Department-Wide Summons no longer shows gaps for March, July, October, or November 2025.
- **Uniformity:** All Summons data (new and backfilled) use the normalized structure, avoiding "Sum of Value"–style errors in visuals.
- **Automation:** A normal `run_all_etl.ps1` run (plus organizing backfill exports) will include the backfill data on the next refresh.

---

*Created 2026-02-12. Normalization integration complete; Summons backfill and M code updates are documented here for future implementation.*
