# Summons ETL v2.3.0 — Deployment Guide

**Historical note (2026-03-23):** The live pipeline is **`run_summons_etl.py`** + **`scripts/summons_etl_normalize.py` v2.5+**. The SLIM CSV is **no longer fixed at 23 columns** — it includes fee/category and related financial columns. See **`CHANGELOG.md` [1.19.2]** and **`docs/SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md`**. This document remains the record of the v2.3.0 drop-in review.

**Date:** 2026-03-04  
**Status:** ✅ Deployed (baseline); superseded for SLIM schema by v2.5+  
**Source:** Claude In Excel Turn 8 + 7-round cross-AI review (Grok, Gemini, Claude)

---

## Summary

Claude's complete v2.3.0 package resolves all 12 audit items and produces a true 23-column SLIM CSV with 100% M-code coverage (v2.5+ extends the SLIM column set; see note above). Deploying this package (not the Grok hybrid) avoids SLIM drift, fragile DQ score logic, and dual codebase maintenance.

---

## What Was Deployed

| File | Location | Purpose |
|------|----------|---------|
| `summons_etl_normalize.py` | `scripts/` | Core ETL: badge-based officer enrichment, statute classification, 3-tier output |
| `run_summons_etl.py` | Project root | Path-agnostic wrapper, `--month` argument, backfill merge |

---

## Three-Tier Output

| Tier | File | Purpose |
|------|------|---------|
| **RAW** | `{YYYY_MM}_eticket_export_RAW.csv` | Exact copy of original e-ticket export |
| **CLEAN** | `summons_powerbi_latest.xlsx` | Full Excel with all enriched columns |
| **SLIM** | `summons_slim_for_powerbi.csv` | 23 columns, ~60% faster Power BI refresh |

---

## SLIM Columns (23)

```
TICKET_NUMBER, STATUS, ISSUE_DATE, STATUTE, VIOLATION_DESCRIPTION,
OFFICER_DISPLAY_NAME, PADDED_BADGE_NUMBER, TYPE, WG1, WG2,
YearMonthKey, Month_Year, Year, Month, TICKET_COUNT, IS_AGGREGATE,
ETL_VERSION, DATA_QUALITY_SCORE, OFFICER_NAME_RAW, SOURCE_FILE,
PROCESSING_TIMESTAMP, TITLE, RANK
```

---

## Usage

```powershell
# Process all months in folder (prefers _FIXED.csv from DOpus)
python run_summons_etl.py

# Dry run: list files without running
python run_summons_etl.py --dry-run

# Legacy: single month
python run_summons_etl.py --month 2026_02
```

---

## DOpus Integration

The ETL discovers all `*_eticket_export*.csv` in `05_EXPORTS/_Summons/E_Ticket/{year}/month/` and **prefers `*_FIXED.csv`** when both raw and FIXED exist (DOpus-cleaned output). If `_FIXED` has 0 data rows (header-only), it falls back to the raw file.

**Workflow:**
1. Export e-ticket data → `YYYY_MM_eticket_export.csv`
2. (Optional) Run DOpus button script → produces `YYYY_MM_eticket_export_FIXED.csv`
3. Run ETL → uses FIXED when present, outputs RAW copy + CLEAN Excel + SLIM CSV

**Fallback when DOpus is skipped:** The ETL applies the same cleanup logic as `pretty_csv.js` internally:
- Strip trailing commas from column names and values (export bug)
- Drop empty `Unnamed` columns
- Auto-detect semicolon vs comma delimiter
- Preserve leading zeros via `dtype=str`

---

## M-Code Updates (6 queries)

All 6 summons queries now source `summons_slim_for_powerbi.csv` via `Csv.Document` with `QuoteStyle=QuoteStyle.Csv` for proper handling of quoted fields:

- `summons_13month_trend.m`
- `summons_all_bureaus.m`
- `summons_top5_moving.m`
- `summons_top5_parking.m`
- `___Summons.m`
- `___Summons_Diagnostic.m`

**Power BI:** Copy updated M code from `m_code/summons/` into Power BI Desktop query editor.

---

## Post-Deployment Checklist

- [x] Replace `scripts/summons_etl_normalize.py` with Claude v2.3.0
- [x] Replace `run_summons_etl.py` (root) with Claude v2.3.0
- [x] Run: `python run_summons_etl.py --month 2026_01`
- [x] Verify 3 output files in `03_Staging/Summons/` (RAW, CLEAN, SLIM)
- [x] Confirm SLIM has exactly 23 columns
- [ ] Verify M/P/C distribution matches expected counts
- [ ] Spot-check officers: Badge 377 (MAZZACCARO), 327 (O'NEILL), 2025 (RAMIREZ-DRAKEFORD)
- [ ] Update 6 M-code queries in Power BI Desktop
- [ ] Refresh Power BI report → confirm zero "column not found" errors
- [x] Update CHANGELOG.md v2.3.0 entry (1.17.26)

---

## References

- `docs/Claude_In_Excel_Officer_Mapping_Analysis.csv` (rows 181–230)
- `KB_Shared/04_output/Grok-Fixed_Large_CSV_Cleaning_Script_(1)`
- `KB_Shared/04_output/Summons_Verification_Note_And_Docs_Update`
- `KB_Shared/04_output/Gemini-Summons_Data_Query_Failures_Explained`
