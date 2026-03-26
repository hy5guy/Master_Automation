// 🕒 2026-03-25 (EST)
// # docs/SSOCC_Service_Log_Excel_And_Power_BI_Rework_2026_03.md
// # Author: R. A. Carucci (sourced from Claude-in-Excel session)
// # Purpose: Canonical notes for SSOCC Service Log workbook + Power BI Option B migration

# SSOCC Service Log — Excel rework & Power BI (Option B)

## Source chat log (chunked export)

Full transcript and chunks live here (not in this repo):

`C:\Users\carucci_r\OneDrive - City of Hackensack\KB_Shared\04_output\ssocc_claude_in_excel_rework\`

| File | Contents |
|------|----------|
| `2026_03_25_21_45_53_ssocc_claude_in_excel_rework_transcript.md` | Readable merge of the session |
| `2026_03_25_21_45_53_ssocc_claude_in_excel_rework_sidecar.json` | Metadata, chunk index |
| `chunk_00000.txt`, `chunk_00001.txt` | Raw chunks |

## Excel workbook

- **Path (canonical in M code):** `C:\Users\carucci_r\OneDrive - City of Hackensack\SSOCC\Archive\_SSOCC - Service Log.xlsx`
- **2026 monthly sheets:** `2026_01` … `2026_12` (JAN26 was renamed to `2026_01`).
- **Table names (2026+):** `T_2026_01` … `T_2026_12` (format `T_YYYY_MM`).
- **Per-sheet log columns:** Control #, Date, Time, CCBP, Service/Product, Description, LIS, LIC, OCA/CAD#
- **Data validation:** CCBP (staff list), Service/Product (`ServiceList_Current`). **Patrol Support** removed from the service dropdown per session.
- **New dimension table (in workbook):** **`DimServiceGroup`** — columns: `Service/Product`, `Service_Group`, `Service_Category`, `Is_Tracked` (~91 service rows; `Is_Tracked = FALSE` excludes Patrol Support and other non-tracked rows).

## Architecture: legacy vs Option B

| Layer | Legacy (still in `___SSOCC_Data.m`) | Option B (target) |
|-------|--------------------------------------|-------------------|
| Excel | MoMTotals: six wide tables `_ADMIN`, `_ANALYSIS`, `_SUR`, `_MAIN`, `_MEET`, `_TRAIN` + manual month columns + COUNTIF into `YEARLY_TOTALS` | **Raw monthly log tables only** + **`DimServiceGroup`**; new months = new sheet/table `T_YYYY_MM` — no new MoM columns |
| Power Query | `Service_Analysis_MoM_Tables_Fixed_v2` pattern: read 6 tables, unpivot month headers (`24-Oct`, etc.), priority flags | **`FactServiceLog`**: discover all monthly **log** tables dynamically, expand rows; **`DimServiceGroup`**: load mapping table |
| DAX | Many cards filter `___SSOCC_Data[Value]` with hard-coded `Service/Product` text | **`COUNTROWS(FactServiceLog)`** with filters on **`DimServiceGroup[Service_Group]`** / **`Service_Category]`** / **`Is_Tracked]`** (relationship on `Service/Product`) |

## Monthly log table naming (Power Query discovery)

**Include** tables whose names match:

- **New:** `T_20*` (e.g. `T_2026_01`, `T_2027_03`)
- **Legacy 2025–2026:** `_25_JAN` … `_25_DEC`, `_26_*` month tables (underscore + YY + month)
- **Legacy 2024:** `_Oct_24`, `_Nov_24`, `_Dec_24` style (`_*_*_24`)

**Exclude** (not row-level logs): `_ADMIN`, `_ANALYSIS`, `_SUR`, `_MAIN`, `_MEET`, `_TRAIN`, `DimServiceGroup`, `DimService`, `YEARLY_TOTALS`, `ServiceList_Current`, and any other non-log table.

## Repo M code layout

| File | Role |
|------|------|
| `m_code/ssocc/FactServiceLog.m` | **New** fact query (Option B) — paste into Power BI as query `FactServiceLog` |
| `m_code/ssocc/DimServiceGroup.m` | **New** dimension query — paste as `DimServiceGroup` |
| `m_code/ssocc/___SSOCC_Data.m` | **Legacy** MoM/unpivot query; keep until the `.pbix` is migrated and visuals/measures are repointed |

## Model relationships (Option B)

- `DimServiceGroup[Service/Product]` → `FactServiceLog[Service/Product]`
- Cardinality: **one-to-many**
- Cross-filter: **single** (dim filters fact)

## DAX measures (summary)

Implement on `FactServiceLog` (or a measures table). Names match the Cursor orchestration prompt in the transcript (Turn 5).

- **Total Services** — `COUNTROWS(FactServiceLog)` where `DimServiceGroup[Is_Tracked] = TRUE`
- **Priority Services Total** — `Service_Category = "Priority Services"`
- **Analysis Total** — `Service_Group = "Analysis"`
- **Investigative Assistance Total** — `Service_Group = "Investigative Assistance"`
- **Analysis & Investigation Total** — `Service_Group` in `{"Analysis","Investigative Assistance"}`
- **Surveillance & Monitoring Total** — `Service_Category = "Surveillance & Monitoring"`
- **Avigilon Flag Review Total**, **CCTV Site Analysis Total**, **TAS Alerts Total**, **Virtual Patrol Total**, **SSOCC Tour Total** — filter `Service_Group` as named

**Important:** Option B measures count **rows (log entries)**, not `SUM(Value)`. Retire old `___SSOCC_Data`-based measures that used `SUM(...[Value])` after migration.

## Cursor / implementation checklist

Use the block under **“SSOCC Power BI Restructure — Option B Implementation”** in the transcript (Turn 5) as the step-by-step prompt: create queries, relationship, DAX, replace card measures, disable `___SSOCC_Data`, validate refresh when adding `T_2026_MM`.

## Validation (from session)

1. `FactServiceLog` loads without errors; rows span legacy months through current entry months.
2. `DimServiceGroup` loads (~91 rows; exact count follows Excel).
3. Active relationship dim → fact on `Service/Product`.
4. `Total Services` > 0; Analysis / Investigative Assistance reflect grouped services.
5. Patrol Support excluded from `Total Services` when `Is_Tracked` is FALSE.
6. Add a new monthly table in Excel (e.g. `T_2026_02`) → refresh → rows appear **without** editing M.

## Related repo files

- `m_code/ssocc/TAS_Dispatcher_Incident.m` — separate SSOCC workbook query (unchanged by this rework)
- `m_code/tmdl_export/tables/___SSOCC_Data.tmdl` — TMDL snapshot; re-export from Power BI after migrating the model
