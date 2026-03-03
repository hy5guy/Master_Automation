# Summons Visuals Fix – March 3, 2026

**Issues addressed:** Department-Wide off, All Bureaus wrong bureau name/totals, Top 5 not updating, blank Month_Year rows.

---

## Root Causes

1. **ETL only loaded 2026 data** – Hardcoded to 2026_01 and 2026_02; no 2025 data for 13‑month visuals.
2. **WG2 display** – Override used "SAFE STREETS OPERATIONS CONTROL CENTER"; Assignment Master uses "SSOCC".
3. **Badge 0738** – Drone operator not in Assignment Master; WG2 was UNKNOWN.
4. **Blank Month_Year** – Rows with null/empty Month_Year caused bad aggregations.
5. **Backfill double-count** – When e-ticket had data for gap months, backfill was still merged.

---

## Fixes Applied

### 1. Full 13‑Month E-Ticket Load (`summons_etl_enhanced.py`)

- **Before:** Loaded only 2026_01 and 2026_02.
- **After:** Loads all months in the 13‑month window (e.g., 2025_02 through 2026_02 for Feb 2026 report).
- File discovery: `YYYY/month/`, `YYYY/`, root.

### 2. WG2 Override and Normalization

- Override for badge 2025 (FIRE LANES): `WG2 = "SSOCC"` (was "SAFE STREETS OPERATIONS CONTROL CENTER").
- Added override for badge 0738 (drone): `WG2 = "SSOCC"`.
- Post-processing: replace "SAFE STREETS OPERATIONS CONTROL CENTER" → "SSOCC" in WG2.

### 3. Backfill Avoids Double-Count (`summons_backfill_merge.py`)

- Skips gap months when main df already has >10 rows for that Month_Year.
- Backfill only used when e-ticket data is missing.

### 4. Filter Blank Month_Year (`summons_13month_trend.m`)

- Added `FilteredMonthYear` step to drop rows with null/empty Month_Year.
- Removes the M,,2 and P,,2 rows that were distorting totals.

---

## Deployment Checklist

1. **Run Summons ETL** – `.\scripts\run_all_etl.ps1 -ScriptNames Summons` or run `summons_etl_enhanced.py` directly.
2. **Update Power BI** – Apply `summons_13month_trend.m` changes in Power Query Editor.
3. **Refresh report** – Refresh the Summons page and verify visuals.

---

## Expected Results

- **Department-Wide Summons:** 13 months (02-25 through 02-26), no blank Month_Year.
- **All Bureaus:** SSOCC instead of "Safe Streets Operations Control Center"; correct totals.
- **Top 5 Moving/Parking:** Current month data from full 13‑month load.

---

## ⚠️ Verification Note (2026-03-03)

**Review required:** Re-export all summons e-ticket data to verify counts. A comparison showed Moving (M) discrepancy for 01-26 (406 expected vs 462 from ETL). See `docs/SUMMONS_VERIFICATION_NOTE_2026_03.md`.
