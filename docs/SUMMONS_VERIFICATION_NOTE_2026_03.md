# Summons Data Verification – March 2026

**Status:** ⚠️ REVIEW REQUIRED  
**Date:** 2026-03-03

---

## Action Required

**Re-export all summons e-ticket data to verify counts.**

A comparison of `2026_01_eticket_export.csv` against expected Department-Wide values showed:

- **Parking (P): 3,577** — ✅ Matches raw file and ETL output
- **Moving (M): 406 expected vs 462 from ETL** — ⚠️ 56-ticket discrepancy

The source e-ticket export may have changed, or prior reports used different methodology. To establish a clean baseline:

1. **Re-export all summons** from the e-ticket system for the 13-month window (e.g. 2025_02 through 2026_02).
2. **Place exports** in `05_EXPORTS\_Summons\E_Ticket\{year}\month\` as `YYYY_MM_eticket_export.csv`.
3. **Run Summons ETL** and compare Department-Wide Moving/Parking totals against the prior report.
4. **Document** any methodology differences (date range, filters, backfill vs e-ticket).

---

## Reference

- E-ticket path: `05_EXPORTS\_Summons\E_Ticket\2026\month\`
- Staging output: `03_Staging\Summons\summons_powerbi_latest.xlsx`
- Last month's report (archive): `archive/_DropExports_pre_2026_02_27/Summons__Department-Wide Summons  Moving and Parking.csv`
