# DFR Summons Documentation Index

Index of documentation for the DFR (Directed Focused Response) Summons workbook and Power BI integration.

---

## Workspace Docs

| Doc | Purpose |
|-----|---------|
| [PROMPT_Claude_In_Excel_DFR_Directed_Patrol_Summons_MCode.md](PROMPT_Claude_In_Excel_DFR_Directed_Patrol_Summons_MCode.md) | M code spec: dual filter, 13-month window, schema, derived columns |
| [DFR_Summons_Claude_In_Excel_Development_Log.md](DFR_Summons_Claude_In_Excel_Development_Log.md) | 51-turn Claude in Excel development history (03/13–03/20/2026) |

---

## M Code

| Path | Purpose |
|------|---------|
| `m_code/drone/DFR_Summons.m` | Power BI query; loads DFR_Summons table; dual filter; schema-resilient Violation_Category, Jurisdiction |

---

## Chatlogs (Workspace)

| Folder | Topic |
|--------|-------|
| [docs/chatlogs/DFR_Summons_ETL_Enhancement_And_Filter_Fix/](chatlogs/DFR_Summons_ETL_Enhancement_And_Filter_Fix/) | ETL enhancement, DFR_CONFIG, dual filter, M code |
| [docs/chatlogs/dfr_summons_update_title_39/](chatlogs/dfr_summons_update_title_39/) | Excel/VBA, DFR Summons Log, ViolationData, Title 39 |
| [docs/chatlogs/Summons_ETL_Fee_Schedule_Integration_Documentation/](chatlogs/Summons_ETL_Fee_Schedule_Integration_Documentation/) | Fee schedule, ViolationData, VBA macro, reconciliation |

---

## KB_Shared (Mirror)

| Path | Content |
|------|---------|
| `KB_Shared/04_output/DFR_Summons_ETL_Enhancement_And_Filter_Fix` | Same as workspace DFR_Summons_ETL chatlog |
| `KB_Shared/04_output/dfr_summons_update_title_39` | Same as workspace dfr_summons_update_title_39 |
| `KB_Shared/04_output/Summons_ETL_Fee_Schedule_Integration_Documentation` | Same as workspace Summons_ETL_Fee_Schedule chatlog |

---

## Workbook

| Item | Path |
|------|------|
| **Target** | `Shared Folder\Compstat\Contributions\Drone\dfr_directed_patrol_enforcement.xlsx` |
| **Table** | DFR_Summons (A1:S501) |
| **Sheets** | DFR Summons Log, ViolationData, Master Fee Schedule, Instructions, M Code Reference, Dashboard, etc. |
