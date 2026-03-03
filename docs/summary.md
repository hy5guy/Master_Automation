# Export File Watchdog — Conversion & Paths Summary

**Source**: Export_File_Watchdog (`02_ETL_Scripts/Export_File_Watchdog`) · **Version**: 2.1.2 · **Updated**: 2026-02-10

---

## Conversion (OTActivity / TimeOffActivity only)

- **Only** OTActivity and TimeOffActivity `.xls` files are **converted**; all other exports are **moved** only.
- **Format**: `.xls` → `.xlsx` only (no CSV). Preserves data types and encoding.
- **Where**: Files must be in **Downloads** (OneDrive or local) and have a **required prefix**:
  - **Monthly**: `YYYY_MM_TimeOffActivity.xls` or `YYYY_MM_OTActivity.xls`
  - **Yearly**: `YYYY_all_TimeOffActivity.xls` or `YYYY_all_OTActivity.xls`

---

## Paths (under `05_EXPORTS`)

| Export           | Monthly path                 | Yearly path                  |
|------------------|-----------------------------|------------------------------|
| **Time Off**     | `_Time_Off\export\month\YYYY`  | `_Time_Off\export\yearly\YYYY`  |
| **Overtime**     | `_Overtime\export\month\YYYY` | `_Overtime\export\yearly\YYYY` |

**Examples**

- `2026_01_TimeOffActivity.xls` → `05_EXPORTS\_Time_Off\export\month\2026\` (plus `2026_01_timeoffactivity.xlsx` and original `.xls`).
- `2025_all_OTActivity.xls` → `05_EXPORTS\_Overtime\export\yearly\2025\` (plus `2025_all_otactivity.xlsx` and original `.xls`).

---

For full detail (filename rules, other export types, no-conversion list), see [WATCHDOG_OT_TIMEOFF_CONVERSION_AND_PATHS.md](WATCHDOG_OT_TIMEOFF_CONVERSION_AND_PATHS.md).
