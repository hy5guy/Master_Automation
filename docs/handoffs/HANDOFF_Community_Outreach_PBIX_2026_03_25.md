# Handoff: Community Outreach page & `___Combined_Outreach_All` (2026-03-25 → 2026-03-26)

**Purpose:** Context for Claude working **inside `Monthly_Report_Template.pbix`** (via Power BI Modeling MCP or Desktop) on the **Community / Out_Reach** page, titles, subtitles, YTD cards, matrix, and related model objects.

**Workspace root:** `C:\Users\carucci_r\OneDrive - City of Hackensack\06_Workspace_Management`

**MCP session log (chunked):** [docs/chatlogs/community_outreach_claude_mcp/](../chatlogs/community_outreach_claude_mcp/) — `2026_03_26_20_18_22_community_outreach_claude_mcp_transcript.md`

---

## 1. Data & Power Query

- **Table:** `___Combined_Outreach_All`
- **Repo M (source of truth for text):** `m_code/community/___Combined_Outreach_All.m`
- **Behavior:** Loads the **newest** file by **Date modified** in  
  `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Community_Engagement\output\`  
  matching `community_engagement_data_*.csv` **or** `*.xlsx`. Excel path uses sheet **`Combined_Data`**.
- **ETL:** `02_ETL_Scripts\Community_Engagement\` — run `python src/main_processor.py` after source updates; then **Refresh** the PBIX.
- **CSB contamination (fixed in Python):** The CSB workbook is a COMPSTAT **activity** tracker (monthly sheets), not an outreach event log. The ETL must **not** flatten those rows into the combined outreach file, or must **strip** rows where `event_name` contains **`(Monthly Total)`** / known non-outreach labels. Prefer excluding the CSB file from discovery **and** a safety filter after `concat`. See [Community_Outreach_YTD_And_Combined_Outreach_Import_2026_03.md](../Community_Outreach_YTD_And_Combined_Outreach_Import_2026_03.md) §6.
- **Duration bug (fixed in Python):** `timedelta` values were serialized to CSV as strings like `1:00:00`; Power Query `Number.From` failed and hours defaulted to **0.5**. Processors must emit **decimal hours** before export. Implementation notes: [cursor_prompt_fix_duration_and_attendees.md](../cursor_prompt_fix_duration_and_attendees.md).

---

## 2. Model relationships (critical)

- **`___Combined_Outreach_All[Date]`** relates to an **auto-generated local date table**, **not** to **`___DimMonth`**.
- Therefore, **slicers or filters on `___DimMonth` do not filter** the outreach fact table via relationships.
- **Period and YTD measures** must use **explicit** `CALCULATE` filters on **`'___Combined_Outreach_All'[Date]`** with bounds derived from **`MAX ( '___DimMonth'[MonthStart] )`** (same pattern as YTD doc). That works **without** a relationship because the filter is applied directly to the fact column.

---

## 3. DAX rules

### `pReportMonth` is M-only

Do **not** reference `pReportMonth` in DAX unless it is loaded as a model column. Use **`___DimMonth`**:

```dax
VAR ReportMonthStart = MAX ( '___DimMonth'[MonthStart] )
VAR MonthEnd = EOMONTH ( ReportMonthStart, 0 )
-- period (report month):
RETURN CALCULATE ( <agg>, '___Combined_Outreach_All'[Date] >= ReportMonthStart, '___Combined_Outreach_All'[Date] <= MonthEnd )
```

YTD uses `YtdStart = DATE ( YEAR ( ReportMonthStart ), 1, 1 )` and `YtdEnd = EOMONTH ( ReportMonthStart, 0 )`.

**Canonical doc:** `docs/POWER_BI_YTD_MEASURES_AND_PAGE_INSTRUCTIONS.md`

### Period card measures (top cards)

`Outreach Sessions`, `Outreach Total Hours`, `Outreach Total Attendees` should scope to the **report month** using the pattern above — **not** bare `COUNTROWS` / `SUM` with only `IsPrevMonth` page filters.

### Remove legacy page filters

After migrating measures, **remove** page/visual filters on **`IsPrevMonth`**, **`Prev Month Flag`**, **`DateInPrevMonth`** (those objects were removed from the model in the 2026-03-26 session). If any remain in an old `.pbix` copy, strip them in the Filters pane.

### Matrix / “previous month” trap

If a matrix uses a **visual filter** on **`___Combined_Outreach_All[Date]`** (e.g. February only) **but** the measures still use **`MAX('___DimMonth'[MonthStart])`**, the measures evaluate in **report month** context (e.g. March) while the subtitle may show February from `MIN([Date])` in the visual filter — **numbers and subtitle disagree**.

**Fix (pick one):**

- **A.** Add **`___DimMonth[MonthLabel]`** (e.g. `02-26`) to **Filters on this visual** for that matrix, **or**
- **B.** Add **Previous month** measures (`EDATE(ReportMonthStart,-1)` … `EOMONTH`) so the matrix auto-aligns to the month before the report month without manual label changes.

### `measure SubtitlePrevMonth`

Still in model as of session end — **confirm no visual uses it**; prefer **`Engagement Subtitle`** for rolling copy if that is the product intent.

---

## 4. TMDL snapshot vs live PBIX

- **`m_code/tmdl_export/`** under **this** workspace:  
  `C:\Users\carucci_r\OneDrive - City of Hackensack\06_Workspace_Management\m_code\tmdl_export`  
  Re-export after material model changes (MCP **ExportToTmdlFolder** or Tabular Editor). **Canvas** (page filters, visual bindings) is **not** in TMDL — only the semantic model.

---

## 5. Outstanding tasks (from MCP session)

| # | Task | Owner |
|---|------|--------|
| 1 | Confirm **`measure SubtitlePrevMonth`** unused → delete or repoint visuals | Desktop |
| 2 | **Matrix** for “previous month”: add **`___DimMonth`** visual filter **or** implement **Previous Month** DAX measures | Desktop / MCP |
| 3 | Wire **`config.json` `output_settings.output_directory`** (e.g. `_DropExports`) in **`main_processor.py`** if you want ETL output path to match config (M already points at `Community_Engagement\output\`) | Python |
| 4 | After ETL + measure changes: **Save .pbix**, **Refresh**, re-export TMDL if repo parity matters | Ops |

---

## 6. Related docs (read order)

| Topic | Path |
|--------|------|
| YTD DAX patterns & outreach errata | `docs/POWER_BI_YTD_MEASURES_AND_PAGE_INSTRUCTIONS.md` |
| Combined import, CSB, matrix trap, ETL | `docs/Community_Outreach_YTD_And_Combined_Outreach_Import_2026_03.md` |
| Duration / attendee ETL fix log | `docs/cursor_prompt_fix_duration_and_attendees.md` |
| Power BI MCP connection | `docs/handoffs/HANDOFF_PowerBI_MCP_2026_03_23.md` |
| Community ETL layout | `02_ETL_Scripts/Community_Engagement/Claude.md` |

---

*Last updated: 2026-03-26 (MCP community_outreach_claude_mcp transcript merged in)*
