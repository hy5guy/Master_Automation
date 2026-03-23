# Handoff: Power BI MCP & Monthly Report Template (Cursor session 2026-03-23)

**Purpose:** Give Claude (Desktop or Cursor) enough context to connect to **Power BI Modeling MCP**, read the **`Monthly_Report_Template.pbix`** model, and continue DAX/visual work without rediscovering constraints.

**Workspace root:** `C:\Users\carucci_r\OneDrive - City of Hackensack\06_Workspace_Management`

---

## 1. MCP connection (Power BI Desktop must be open)

- The MCP talks to the **running Analysis Services workspace** inside Power BI Desktop, **not** the `.pbix` file on disk.
- **Cursor:** User-level MCP config: `%USERPROFILE%\.cursor\mcp.json`. Optional project copy: `06_Workspace_Management\.cursor\mcp.json` (registers `powerbi-modeling-mcp`; path to `powerbi-modeling-mcp.exe` is machine-specific).
- **Connect workflow:** After opening the template in Desktop, use MCP **ListLocalInstances** → note `localhost:<port>` → **Connect** with `Provider=MSOLAP;Data Source=localhost:<port>`. Port changes when Desktop restarts.
- **DAX Studio:** Use **Power BI / SSDT Model** and select the open report (e.g. `Monthly_Report_Template`), not Tabular Server, for local template work.

---

## 2. Critical DAX rule: `pReportMonth` is M-only

- **`pReportMonth`** is a **Power Query (M) parameter**. It is **not** a valid DAX table, variable, or function unless you **load it into the model** as a table/column.
- Symptom: `Failed to resolve name 'pReportMonth'. It is not a valid table, variable, or function name.`
- **Recommended pattern** for YTD bounds, titles, and subtitles aligned with the template’s rolling month axis:

```dax
VAR ReportMonthStart = MAX ( '___DimMonth'[MonthStart] )
VAR YtdStart = DATE ( YEAR ( ReportMonthStart ), 1, 1 )
VAR YtdEnd = EOMONTH ( ReportMonthStart, 0 )
```

- **Canonical write-up:** `docs/POWER_BI_YTD_MEASURES_AND_PAGE_INSTRUCTIONS.md` (updated 2026-03-23 with this errata; changelog **v1.18.18**).

---

## 3. Arrest page (`Arrest_13` / `Arrest_13_Month`)

- **Table:** `___Arrest_13Month` (rolling **13-month** import; row count was **693** in one connected snapshot).
- **Top 5 staging:** `___Top_5_Arrests` (**5** rows; prior-month / pre-aggregated officers).
- **Measure `Arrests YTD`:** Was **missing** from the model at review time; add using **`___DimMonth`** pattern above (see YTD doc Page 15).
- **Matrix (YTD Top 5):** Rows `___Arrest_13Month[Officer of Record]`, values `[Arrests YTD]`, **Top N = 5** on that measure. Title/subtitle measures in same doc (DAX-safe).
- **`Home_Category` on `___Arrest_13Month`:** M currently produces only **`Local`** and **`Out-of-Town`**. `Arrest Local %` is valid; separate In-County / Out-of-State **%** need different M or use **`___Arrest_Distro`**-style logic.

---

## 4. Model inventory notes (from MCP)

- **~293 measures**; **no calculation groups**.
- **Display folders:** `RT Measures`, `DFR Measures`, `Summary` (outreach); many measures ungrouped.
- **`m_code/tmdl_export/`** is a **snapshot**; it can **lag** the live `.pbix` (e.g. measures added only in Desktop may not appear until re-export).

---

## 5. Key repo docs for the next assistant

| Topic | Path |
|--------|------|
| YTD measures + page instructions + DAX errata | `docs/POWER_BI_YTD_MEASURES_AND_PAGE_INSTRUCTIONS.md` |
| Template workflow, `pReportMonth` cycle | `docs/MONTHLY_REPORT_TEMPLATE_WORKFLOW.md` |
| MCP session summary (paths, subtitles, `IncidentCount_13Month`) | `docs/POWERBI_TEMPLATE_MCP_UPDATE_2026_03_19.md` |
| Claude Desktop prompts for template | `docs/PROMPT_Claude_Desktop_Monthly_Report_Template_MCP.md` |
| Missing visuals spec (Response Time, DFR, etc.) | `docs/PROMPT_Claude_MCP_Create_Missing_Visuals_For_Monthly_Report.md` |
| pReportMonth **M** migration (transcripts) | `docs/chatlogs/PROMPT_Claude_MCP_pReportMonth_Migration/` |
| Project map + MCP note | `Claude.md` |
| Changelog doc sync | `CHANGELOG.md` (**[1.19.2]** summons + training pipeline; **[1.18.18]** DAX errata) |
| Summons / training ETL + M code | `CHANGELOG.md` **[1.19.2]**; `docs/SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md`; `docs/POLICY_TRAINING_AUTOMATION_AND_COST_VISUAL.md` |
| Post-MCP manual steps (Close & Apply, ETL, PQ) | `docs/POST_SESSION_ACTION_ITEMS.md` |
| Tasks A–F visual build (YTD cards, Summons_YTD page, RT, DFR, contrast) | `docs/TASKS_A_THROUGH_F_DELIVERABLE.md` |

---

## 6. Suggested first message to Claude Desktop (paste after MCP connected)

```text
Workspace: 06_Workspace_Management. Read docs/handoffs/HANDOFF_PowerBI_MCP_2026_03_23.md and docs/POWER_BI_YTD_MEASURES_AND_PAGE_INSTRUCTIONS.md (YTD + pReportMonth DAX rule).

Connect to my open Monthly_Report_Template.pbix (ListLocalInstances → Connect localhost). Then: (1) confirm whether measure Arrests YTD exists; if not, create it on ___Arrest_13Month using MAX(___DimMonth[MonthStart]) for YTD bounds; (2) list measures on ___Arrest_13Month and ___Top_5_Arrests; (3) suggest any follow-up for Arrest_13 YTD matrix or KPIs.
```

---

*Generated from Cursor session context; adjust paths if OneDrive profile or template folder name differs (`08_Templates` vs `15_Templates`).*
