# Summons ETL: Paths and _DropExports Clarification

**Purpose:** Clarify where Summons data is saved vs. where _DropExports is used, to avoid confusion.

---

## Summons Data Flow (No _DropExports)

The **Summons ETL** (`run_summons_etl.py` in this repo, using `scripts/summons_etl_normalize.py`) does **not** write to `_DropExports`. (A separate **`summons_etl_enhanced.py`** may exist under `02_ETL_Scripts/Summons/` for other workflows.)

| Step | Location | Purpose |
|------|----------|---------|
| **Input** | `05_EXPORTS/_Summons/E_Ticket/2026/` and `2026/month/` | E-ticket CSV exports |
| **Backfill source** | `PowerBI_Data/Backfill/2025_12/summons/` | Gap months (03-25, 07-25, 10-25, 11-25) from `2025_12_department_wide_summons.csv` |
| **Output** | `03_Staging/Summons/summons_powerbi_latest.xlsx` | Full staging workbook (CLEAN tier) |
| **Output** | `03_Staging/Summons/summons_slim_for_powerbi.csv` | Extended SLIM CSV for Power BI (`FINE_AMOUNT`, `VIOLATION_CATEGORY`, financial columns, etc.; see `docs/SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md`) |

Power BI M code queries (all 6 summons queries) load from **summons_slim_for_powerbi.csv**, not from _DropExports.

---

## _DropExports Usage

| Folder | Used By | Purpose |
|--------|---------|---------|
| **PowerBI_Data/_DropExports** | `run_all_etl.ps1`, `process_powerbi_exports.py` | ETL outputs (Arrests, Community Engagement, Response Times, etc.) and raw Power BI visual exports |
| **Master_Automation/_DropExports** | Optional; some docs reference it | Alternative source for visual export processing; not used by Summons ETL |

**Config:** `config/scripts.json` → `powerbi_drop_path`: `PowerBI_Data\_DropExports`

---

## Why Summons Doesn't Use _DropExports

- Summons outputs an **Excel staging workbook** and a **SLIM CSV**; Power BI queries use the CSV
- `scripts.json` Summons `output_patterns` is `["*.csv"]` — no match, so nothing is copied to _DropExports
- Power BI Summons queries point to `03_Staging/Summons/summons_slim_for_powerbi.csv` (v2.5.0+ enrichment; fee schedule JSON on OneDrive for statute-based fines)

---

## Backfill Folder

- **Path:** `PowerBI_Data/Backfill/2025_12/summons/` (lowercase `summons`)
- **Preferred file:** `2025_12_department_wide_summons.csv` (Long format: PeriodLabel, Time Category, Sum of Value)
- **Gap months:** 03-25, 07-25, 10-25, 11-25

*Created 2026-03-03*

---

## ⚠️ Verification Note (2026-03-03)

**Review required:** Re-export all summons e-ticket data to verify counts. See `docs/SUMMONS_VERIFICATION_NOTE_2026_03.md`.
