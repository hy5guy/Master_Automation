# Summons Backfill – Code Injection Point

**Purpose:** Fill Department-Wide Summons data gaps for months where no e-ticket export exists, by merging aggregate totals from the organized backfill folder.

**Last Updated:** 2026-03-14

---

## Active Pipeline (DEPLOYED)

**Entry point:** `run_summons_etl.py` (repo root)  
**Core ETL:** `scripts/summons_etl_normalize.py` — `normalize_personnel_data()`  
**Backfill merge:** `scripts/summons_backfill_merge.py` — `merge_missing_summons_months()`

**Flow:**
1. `run_summons_etl.py` discovers e-ticket files from both `2025/month/` and `2026/month/`
2. Calls `normalize_personnel_data()` to load, clean, classify (raw Case Type Code M/P/C), and join to Assignment Master
3. Calls `merge_missing_summons_months()` to inject backfill for gap months
4. Writes 3-tier output: RAW CSV, CLEAN Excel (`summons_powerbi_latest.xlsx`), SLIM CSV (`summons_slim_for_powerbi.csv`)

Power BI M code queries source `summons_slim_for_powerbi.csv` directly.

---

## Gap Months (as of 2026-03-11)

| Month | Status | Source |
|-------|--------|--------|
| 07-25 | **True gap** | No e-ticket export exists. 17 straggler M records from other months with July issue dates. **Backfill P (3413) and C** from `Backfill/2026_01/summons/` — type-aware merge adds only missing TYPEs (avoids M double-count). |
| All other 2025 months | E-ticket data available | Files in `05_EXPORTS\_Summons\E_Ticket\2025\month\` |

Previously (pre-2026-03-10), months 03-25, 10-25, 11-25 were listed as gaps, and 01-25/02-25 were set to prefer backfill. File discovery confirmed all those months have e-ticket exports.

---

## Backfill Configuration

In `scripts/summons_backfill_merge.py`:

```python
SUMMONS_GAP_MONTHS = ("07-25",)          # Only July 2025 is a true gap
SUMMONS_BACKFILL_PREFER_MONTHS = ()      # Empty: all months with e-ticket data use individual records
DEFAULT_BACKFILL_SUMMONS_LABEL = "2026_01"
```

---

## Backfill Folder Layout

**Canonical path (single source of truth, from `config/scripts.json` → `powerbi_drop_path`):**

`{OneDrive}/PowerBI_Data/Backfill/{label}/summons/`

Example: `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\Backfill\2026_01\summons\2026_01_department_wide_summons_january_report.csv` (full January report: 01-25 through 01-26)

> **Note:** The legacy `00_dev/projects/PowerBI_Date/Backfill/` location was archived to `99_Archive/PowerBI_Date_00_dev_20260311` on 2026-03-11. All data was merged into the canonical **PowerBI_Data** path before archiving.

CSVs in these folders are expected in "Long" format with columns: `PeriodLabel` (or `Period`), `WG2`, `TICKET_COUNT` (or `Sum of Value`), `TYPE`. Column renaming is handled by `RENAME_MAP` in the merge script.

**Backfill-as-source-of-truth (v1.18.4+):** For ALL months in the consolidated backfill file, e-ticket rows are removed and backfill values are used exclusively. As of v1.18.7, `2026_01_department_wide_summons_january_report.csv` contains the full January report (01-25 through 01-26). Months not in backfill (e.g. 02-26) use e-ticket data.

---

## Dependencies and Caveats

- **Python environment:** Requires `pandas` and `openpyxl`. Install: `pip install -r requirements.txt`
- **OneDrive sync:** May cause `PermissionError` on .xlsx files during sync. Run when sync is idle.
- **Schema drift:** If Power BI visual export changes column names, update `RENAME_MAP` in `summons_backfill_merge.py`.
- **BOM encoding:** The ETL uses `utf-8-sig` to handle Byte Order Mark in CSV files (DOpus FIXED exports).

---

## Related Documentation

- `docs/PROMPT_Claude_MCP_Summons_Bugfix.md` — M code fixes applied via Claude Desktop MCP
- `docs/PROMPT_Claude_MCP_Summons_Round3_Fix.md` — Window, WG2 filter, and Total null fixes
- `docs/Debug summons automation backfill and Power BI issues.md` — Original audit workup
