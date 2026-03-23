# Handoff: Claude + MCP — Loose ends (2026-03-24)

**Purpose:** Start a **new Claude session** (Cursor with **Power BI Modeling MCP**, or Claude Code with repo + optional MCP) to finish what documentation and prior MCP sessions outlined but did not complete on disk or in Desktop.

**Workspace root (OneDrive):**  
`C:\Users\carucci_r\OneDrive - City of Hackensack\06_Workspace_Management`

**Gold template (typical):**  
`...\08_Templates\Monthly_Report_Template.pbix` or `...\15_Templates\...` (same file; folder varies by machine layout)

---

## 1. What is already done (do not redo blindly)

| Area | Status |
|------|--------|
| **Docs on `origin/main`** | **`CHANGELOG.md` [1.19.3]** — handoffs, `POST_SESSION_ACTION_ITEMS`, `TASKS_A_THROUGH_F_DELIVERABLE`, Desktop MCP prompt, summons/training doc alignment |
| **Pipeline design (repo)** | **`CHANGELOG.md` [1.19.2]** — `apply_fine_amount_and_violation_category`, extended SLIM, training M patterns |
| **Visual build guide** | **`docs/TASKS_A_THROUGH_F_DELIVERABLE.md`** — Tasks A–F checklists (cards, Summons_YTD page, page renames, 6 RT visuals, DFR, contrast) |
| **Post-MCP Desktop steps** | **`docs/POST_SESSION_ACTION_ITEMS.md`** — Save, Close & Apply, ETL, manual PQ for `summons_revenue_by_violation_category` |
| **Power BI MCP primer** | **`docs/handoffs/HANDOFF_PowerBI_MCP_2026_03_23.md`** — connect localhost, **`pReportMonth` is M-only** in DAX |

---

## 2. Loose ends (prioritized)

### A. Code in repo — verify git status and commit if intended

These paths were **not** in the **docs(1.19.3)** commit; confirm diff, test, then commit separately:

| Path | Notes |
|------|--------|
| `run_summons_etl.py` | Calls `apply_fine_amount_and_violation_category` after backfill merge |
| `scripts/summons_etl_normalize.py` | v2.5+ fee schedule + slim columns |
| `m_code/training/___In_Person_Training.m` | Full log from `Policy_Training_Monthly.xlsx`; YTD in DAX |
| `m_code/training/___Cost_of_Training.m` | 13-month ∪ calendar YTD periods |
| `m_code/summons/summons_revenue_by_violation_category.m` | Depends on extended SLIM |

**Orchestrator note:** `config/scripts.json` may still reference `02_ETL_Scripts\Summons\summons_etl_enhanced.py`. Canonical enrichment path for **this** workspace is **`python run_summons_etl.py`** from repo root (see **`docs/SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md`**).

### B. Power BI Desktop (cannot be finished by MCP alone)

1. **Paste repo M** into Advanced Editor for **`___In_Person_Training`** and **`___Cost_of_Training`** if not already applied in pbix.
2. **Close & Apply** after M changes.
3. **`Response_Type_Sort`** calculated column on **`___ResponseTime_AllMetrics`** — see **`docs/TASKS_A_THROUGH_F_DELIVERABLE.md`** Task D (MCP `column_operations` was blocked).
4. **New PQ query** **`summons_revenue_by_violation_category`** from **`m_code/summons/summons_revenue_by_violation_category.m`** — manual PQ only if MCP cannot add tables.
5. **Run** `python run_summons_etl.py` (with fee schedule JSON on disk) so **`FINE_AMOUNT`** populates **`___Summons`** after refresh.
6. **Tasks A–F** visual work — follow **`docs/TASKS_A_THROUGH_F_DELIVERABLE.md`** (cards, **`Summons_YTD`** page, renames, RT ×6, DFR on Drone, contrast).
7. **`Standards/config/powerbi_visuals/visual_export_mapping.json`** — add keys noted in Tasks B/E of deliverable when new visual names exist.

### C. Optional repo hygiene (separate commit)

- Untracked **`docs/chatlogs/**`** subtrees — add if you want transcripts in git; otherwise leave untracked or `.gitignore`.
- **`.cursor/`** — usually not committed.

---

## 3. MCP session startup (Power BI Desktop)

1. Open **`Monthly_Report_Template.pbix`**.
2. MCP: **ListLocalInstances** → **Connect** `Provider=MSOLAP;Data Source=localhost:<port>` (port changes per launch).
3. Read **`docs/handoffs/HANDOFF_PowerBI_MCP_2026_03_23.md`** and **`docs/POWER_BI_YTD_MEASURES_AND_PAGE_INSTRUCTIONS.md`** before editing DAX.

---

## 4. Copy-paste prompt — start Claude (Cursor / Claude Code)

Use after MCP is connected (or for repo-only work if fixing Python/M first).

```text
Workspace: C:\Users\carucci_r\OneDrive - City of Hackensack\06_Workspace_Management

Read first:
- docs/handoffs/HANDOFF_Claude_MCP_Loose_Ends_2026_03_24.md (this handoff)
- docs/handoffs/HANDOFF_PowerBI_MCP_2026_03_23.md
- docs/POST_SESSION_ACTION_ITEMS.md
- docs/TASKS_A_THROUGH_F_DELIVERABLE.md

Goals (pick what applies this session):
1) Repo: git status — if run_summons_etl.py, scripts/summons_etl_normalize.py, and m_code/training/*.m / summons_revenue_by_violation_category.m differ from origin/main, review diffs, run py_compile / a quick ETL smoke test if safe, then propose a single focused commit message (code separate from docs).
2) MCP (if connected to open Monthly_Report_Template.pbix): confirm ___In_Person_Training and ___Cost_of_Training M match repo files; list whether Response_Type_Sort exists; confirm summons_revenue_by_violation_category table/query exists; note any broken queries.
3) Output: numbered checklist of what’s done vs blocked (Desktop-only vs MCP vs repo), with exact file paths for next human steps.

Constraints: Do not invent paths. Do not use bare pReportMonth in new DAX. Match existing naming and CHANGELOG style for any doc edits only if I ask.
```

---

## 5. Quick path index

| Topic | Path |
|--------|------|
| Changelog | `CHANGELOG.md` |
| Project map | `Claude.md`, `README.md`, `SUMMARY.md` |
| Summons import / fees | `docs/SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md` |
| Summons ETL entry | `run_summons_etl.py` |
| Backfill injection order | `docs/SUMMONS_BACKFILL_INJECTION_POINT.md` |
| Training automation | `docs/POLICY_TRAINING_AUTOMATION_AND_COST_VISUAL.md` |
| YTD DAX / DimMonth | `docs/POWER_BI_YTD_MEASURES_AND_PAGE_INSTRUCTIONS.md` |
| Missing visuals spec | `docs/PROMPT_Claude_MCP_Create_Missing_Visuals_For_Monthly_Report.md` |
| Desktop MCP prompts | `docs/PROMPT_Claude_Desktop_Monthly_Report_Template_MCP.md` |
| Export routing | `Standards/config/powerbi_visuals/visual_export_mapping.json` |

---

*Handoff file: `docs/handoffs/HANDOFF_Claude_MCP_Loose_Ends_2026_03_24.md`. Update dates and git facts after you commit remaining code.*
