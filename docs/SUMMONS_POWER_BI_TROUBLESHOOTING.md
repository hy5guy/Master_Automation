# Summons Power BI Troubleshooting

**Errors:** "Archive file cannot be size 0" | "File contains corrupted data"

---

## Quick Checks

1. **File path** – All summons queries load from:
   ```
   C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx
   ```
   Must be **City of Hackensack** OneDrive, not Personal.

2. **File size** – Run in PowerShell:
   ```powershell
   (Get-Item "C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx").Length
   ```
   Should be > 20,000,000 (≈24 MB). If 0 or very small, restore from a timestamped copy:
   ```powershell
   $ts = Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_*.xlsx" | Where-Object { $_.Name -match '_\d{8}_\d{6}\.xlsx$' } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
   if ($ts) { Copy-Item $ts.FullName "C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx" -Force }
   ```

3. **OneDrive sync** – Right-click the `03_Staging\Summons` folder → **Always keep on this device**. Avoid placeholder files.

4. **File locks** – Close Excel and any other app that might have the file open before refreshing Power BI.

---

## Refresh Steps (Not Just Close/Reopen)

Closing and reopening Power BI does **not** refresh queries. To reload data:

1. **Home** → **Transform data** → **Power Query Editor**
2. **Home** → **Refresh Preview** (or **Refresh All**)
3. **Close & Apply**
4. **Home** → **Refresh** (model refresh)

Or: Right-click each query (`___Summons`, `summons_13month_trend`, `summons_all_bureaus`) → **Refresh**.

---

## Update M Code in Power BI

If the report still has old queries, paste the latest M code from the repo:

1. **Transform data** → Power Query Editor
2. Right-click `summons_13month_trend` → **Advanced Editor** → replace with `m_code/summons/summons_13month_trend.m`
3. Right-click `summons_all_bureaus` → **Advanced Editor** → replace with `m_code/summons/summons_all_bureaus.m`
4. **Close & Apply**

---

## ETL Save Logic (Reduces Corruption)

The ETL now writes to a timestamped file first, then copies to `summons_powerbi_latest.xlsx`. This avoids a second Excel write that could corrupt the file. Run ETL with Power BI closed.

---

## ⚠️ Verification Note (2026-03-03)

**Review required:** Re-export all summons e-ticket data to verify counts. See `docs/SUMMONS_VERIFICATION_NOTE_2026_03.md`.
