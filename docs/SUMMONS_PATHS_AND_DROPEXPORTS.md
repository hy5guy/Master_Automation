# Summons ETL: Paths and _DropExports Clarification

**Purpose:** Clarify where Summons data is saved vs. where _DropExports is used, to avoid confusion.

---

## Summons Data Flow (No _DropExports)

The **Summons ETL** (`summons_etl_enhanced.py`) does **not** write to `_DropExports`.

| Step | Location | Purpose |
|------|----------|---------|
| **Input** | `05_EXPORTS/_Summons/E_Ticket/2026/` and `2026/month/` | E-ticket CSV exports |
| **Backfill source** | `PowerBI_Date/Backfill/2025_12/summons/` | Gap months (03-25, 07-25, 10-25, 11-25) from `2025_12_department_wide_summons.csv` |
| **Output** | `03_Staging/Summons/summons_powerbi_latest.xlsx` | Staging workbook for Power BI |

Power BI M code queries load directly from the **staging workbook**, not from _DropExports.

---

## _DropExports Usage

| Folder | Used By | Purpose |
|--------|---------|---------|
| **PowerBI_Date/_DropExports** | `run_all_etl.ps1`, `process_powerbi_exports.py` | ETL outputs (Arrests, Community Engagement, Response Times, etc.) and raw Power BI visual exports |
| **Master_Automation/_DropExports** | Optional; some docs reference it | Alternative source for visual export processing; not used by Summons ETL |

**Config:** `config/scripts.json` → `powerbi_drop_path`: `PowerBI_Date\_DropExports`

---

## Why Summons Doesn't Use _DropExports

- Summons outputs an **Excel staging workbook** (not CSV)
- `scripts.json` Summons `output_patterns` is `["*.csv"]` — no match, so nothing is copied to _DropExports
- Power BI Summons queries point to `03_Staging/Summons/summons_powerbi_latest.xlsx` directly

---

## Backfill Folder

- **Path:** `PowerBI_Date/Backfill/2025_12/summons/` (lowercase `summons`)
- **Preferred file:** `2025_12_department_wide_summons.csv` (Long format: PeriodLabel, Time Category, Sum of Value)
- **Gap months:** 03-25, 07-25, 10-25, 11-25

*Created 2026-03-03*

---

## ⚠️ Verification Note (2026-03-03)

**Review required:** Re-export all summons e-ticket data to verify counts. See `docs/SUMMONS_VERIFICATION_NOTE_2026_03.md`.
