# Summons SLIM CSV Migration — Archived Files

**Date:** 2026-03-04  
**Reason:** Superseded by v2.3.0 SLIM CSV deployment

## Contents

Superseded versions archived when deploying Claude's v2.3.0 package and switching all 6 Power BI M-code queries from Excel to `summons_slim_for_powerbi.csv`.

### M-code .txt exports (Excel source, pre-SLIM)
- `summons_13month_trend.txt`
- `summons_all_bureaus.txt`
- `summons_top5_moving.txt`
- `summons_top5_parking.txt`
- `___Summons.txt`
- `___Summons_Diagnostic.txt`
- `2026_03_03_00_47_00_all_mcode_summons_queries.txt` — consolidated export of all 6

### Script backups (pre-v2.3.0)
- `run_summons_etl.txt` — old hardcoded-path wrapper
- `summons_etl_normalize.txt` — v2.2.0 Grok hybrid (28-col SLIM, Excel output)

## Active versions

- **M code:** `m_code/summons/*.m` — Csv.Document with QuoteStyle=QuoteStyle.Csv
- **ETL:** `scripts/summons_etl_normalize.py` (v2.3.0), `run_summons_etl.py` (v2.3.0)
