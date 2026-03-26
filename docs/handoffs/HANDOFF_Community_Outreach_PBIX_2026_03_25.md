# Handoff: Community Outreach page & `___Combined_Outreach_All` (2026-03-25)

**Purpose:** Context for Claude working **inside `Monthly_Report_Template.pbix`** (via Power BI Modeling MCP or Desktop) on the **Community / Out_Reach** page, titles, subtitles, YTD cards, and related model objects.

**Workspace root:** `C:\Users\carucci_r\OneDrive - City of Hackensack\06_Workspace_Management`

---

## 1. Data & Power Query

- **Table:** `___Combined_Outreach_All`
- **Repo M (source of truth for text):** `m_code/community/___Combined_Outreach_All.m`
- **Behavior:** Loads the **newest** file by **Date modified** in  
  `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Community_Engagment\output\`  
  matching `community_engagement_data_*.csv` **or** `*.xlsx`. Excel path uses sheet **`Combined_Data`**.
- **ETL:** `02_ETL_Scripts\Community_Engagment\` — `config.json` must match live workbook sheets (e.g. **`2025_Master`** for CE division file, CSB **`YY_MM`** tabs). Run `python src/main_processor.py` after source updates; then **Refresh** the PBIX.

---

## 2. DAX rules

### `pReportMonth` is M-only

Do **not** reference `pReportMonth` in DAX unless it is loaded as a model column. For YTD aligned with the template month axis use **`___DimMonth`**:

```dax
VAR ReportMonthStart = MAX ( '___DimMonth'[MonthStart] )
VAR YtdStart = DATE ( YEAR ( ReportMonthStart ), 1, 1 )
VAR YtdEnd = EOMONTH ( ReportMonthStart, 0 )
```

**Canonical doc:** `docs/POWER_BI_YTD_MEASURES_AND_PAGE_INSTRUCTIONS.md`

### Page filters vs cards (important)

If a measure or flag such as **`IsPrevMonth`** (or **`DateInPrevMonth`**) is applied as a **page-level** filter, it affects **all** visuals on the page—including **YTD cards**. Scope month filters to the **matrix/table visual only** unless cards should share that context.

### Table / matrix subtitle measure

**`SubtitlePrevMonth`** (on `___Combined_Outreach_All` in TMDL snapshot):

```dax
SubtitlePrevMonth =
VAR MinD = MIN ( '___Combined_Outreach_All'[Date] )
RETURN
    IF (
        NOT ISBLANK ( MinD ),
        "Tracking community outreach and engagement initiatives by bureau | "
            & FORMAT ( MinD, "MMMM yyyy" ),
        "Tracking community outreach and engagement initiatives by bureau"
    )
```

Use **`MAX ( '___Combined_Outreach_All'[Date] )`** instead of **`MIN`** if the subtitle should show the **latest** date in filter context.

**Related:** `Engagement Title` = `"Engagement Initiatives by Bureau"`. **`Engagement Subtitle`** may reference **`'UI'[UI PrevMonth Label]`** — do not mix with `SubtitlePrevMonth` unless product intent is aligned.

---

## 3. TMDL snapshot vs live PBIX

- **`m_code/tmdl_export/`** is an **export snapshot** and can **lag** the open `.pbix`. After editing in Desktop, re-export if the repo must stay in sync.

---

## 4. Related docs (read order for broad template work)

| Topic | Path |
|--------|------|
| YTD DAX patterns & outreach errata | `docs/POWER_BI_YTD_MEASURES_AND_PAGE_INSTRUCTIONS.md` |
| Power BI MCP connection & `pReportMonth` | `docs/handoffs/HANDOFF_PowerBI_MCP_2026_03_23.md` |
| Community ETL layout & sheets | `02_ETL_Scripts/Community_Engagment/Claude.md` |

---

*Last updated: 2026-03-25*
