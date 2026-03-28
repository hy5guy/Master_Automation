// 🕒 2026-03-23-17-30-00
// # Monthly_Report_Template/POST_SESSION_ACTION_ITEMS.md
// # Author: R. A. Carucci
// # Purpose: Action items after MCP session — M code updates committed, manual steps required before measures populate.

---

# Post-Session Action Items — 2026-03-23

## Claude verification snapshot (live model vs repo docs)

Cross-check after MCP connected to **Monthly_Report_Template.pbix**:

| Finding | Root cause | Fix |
|--------|------------|-----|
| **Training Classes / Duration / Cost YTD blank** | `___In_Person_Training` M was **report-month-only** (e.g. v2026-03-13) | Use repo **`m_code/training/___In_Person_Training.m`** — load full log; **YTD in DAX** |
| **Training In-Person / Online YTD = $0** | `___Cost_of_Training` lacked **calendar YTD ∪ 13-month** periods | Use repo **`m_code/training/___Cost_of_Training.m`** (`YTDLabels` / `AllPeriodLabels` union) |
| **`___Summons` `FINE_AMOUNT` all zero** | Staging CSV not rebuilt with **v2.5+** enrichment, and/or **`municipal-violations-bureau-schedule.json`** missing on disk | Run **`run_summons_etl.py`** from **this repo**; confirm JSON under OneDrive `09_Reference/LegalCodes/data/Title39/`; then **Close & Apply** |
| **`summons_revenue_by_violation_category` missing** | Query/table not in model; MCP may be blocked if engine has broken objects | **Power Query → New query →** paste **`m_code/summons/summons_revenue_by_violation_category.m`** |

---

## What Was Done This Session (MCP)

### Measures Created: 101 total
- 1 bug fix (`Arrest Out-of-Town %` → non-Local filter)
- 3 Out_Reach YTD (Events, Hours, Attendees)
- 7 REMU YTD
- 7 CSB YTD (Currency/High Value use `$#,0` format)
- 5 Detective Case Disposition YTD
- 16 Detective_1 Part A+B YTD
- 14 STACP Pt1 YTD
- 11 STACP Pt2 YTD
- 6 Traffic MVA YTD
- 9 Traffic YTD (Parking Fees uses `$#,0`)
- 8 ESU YTD
- 10 Patrol YTD
- 5 Training YTD (Classes, Duration, Cost, In-Person, Online)
- 5 Summons YTD (Moving, Parking, Revenue All/Moving/Parking)

### M Code Partitions Updated (2)
| Table | Old Version | New Version | Change |
|-------|------------|-------------|--------|
| `___In_Person_Training` | 2026-03-13 (report month only) | 2026-03-23 (all rows) | Removes `[Start date] >= ReportStart` filter. YTD handled in DAX. |
| `___Cost_of_Training` | 2026-03-12 (rolling 13-mo only) | 2026-03-23 (rolling + Calendar YTD union) | Adds `YTDLabels` union so `Period_Sort` covers Jan→report month for YTD DAX. |

---

## REQUIRED: Manual Steps in Power BI Desktop

### Step 1 — Save the .pbix (Ctrl+S)
Persists all 101 measures + 2 M code updates to disk.

### Step 2 — Close & Apply in Power Query Editor
**Critical.** MCP commits M expressions to the AS engine but Power BI Desktop does NOT re-execute queries until Close & Apply.

After Close & Apply:
- `___In_Person_Training` will reload ALL in-person rows (not just report month)
- `___Cost_of_Training` will include Calendar YTD periods in addition to rolling 13-mo
- `___Summons` will reload from `summons_slim_for_powerbi.csv` (picks up `FINE_AMOUNT` if ETL v2.5+ has run)
- All 101 YTD measures will then have data to evaluate

### Step 3 — Run Summons ETL (if not already done for this report month)

**Canonical script (this workspace):** `06_Workspace_Management\run_summons_etl.py` (calls `merge_missing_summons_months` then `apply_fine_amount_and_violation_category`). If your daily orchestrator still points at `02_ETL_Scripts\Summons\summons_etl_enhanced.py`, that path may **not** include v2.5+ fee enrichment — align with **`CHANGELOG.md` [1.19.2]** and **`docs/SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md`**.

```powershell
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\06_Workspace_Management"
python run_summons_etl.py
```

Optional: `python run_summons_etl.py --month YYYY_MM` if the wrapper supports it (see script `--help`).

This populates **`FINE_AMOUNT`** and **`VIOLATION_CATEGORY`** in `03_Staging\Summons\summons_slim_for_powerbi.csv`. If **`Penalty`** is empty and the **municipal fee schedule JSON** is missing, fines can remain **0** — check ETL log warnings.

### Step 4 — Add `summons_revenue_by_violation_category` Query (Manual)
MCP cannot create new tables due to the broken-AS-engine constraint. Add via Power Query Editor:

1. Open Power Query Editor
2. New Query → Blank Query → Advanced Editor
3. Paste the M code from `m_code/summons/summons_revenue_by_violation_category.m`
4. Name it `summons_revenue_by_violation_category`
5. Close & Apply

This creates a table with columns: `VIOLATION_CATEGORY`, `Revenue` — aggregated YTD from the SLIM CSV.

### Step 5 — Verify Training Source Data
The `Training Classes Attended YTD` measure depends on `___In_Person_Training[Start date]`. After Close & Apply, check:
- If rows exist with `Start date` in Jan–Mar 2026
- If `Total Cost` is populated (not all zeros)
- If `Policy_Training_Monthly.xlsx` has been updated for the current reporting period

The `Training In-Person YTD` and `Training Online YTD` measures use `___Cost_of_Training[Period_Sort]`. After Close & Apply, check:
- That `policy_training_outputs.xlsx` sheet `Delivery_Cost_By_Month` has columns for 01-26, 02-26, 03-26
- If the Policy Training ETL hasn't run yet, enable it: `config\scripts.json` → `"Policy Training Monthly"` → `enabled: true`

---

## Measures Still Returning $0 / Blank — Expected Until Data Refreshes

| Measure Group | Returns | Will Fix After |
|---------------|---------|----------------|
| Training Classes/Duration/Cost YTD | Blank | Close & Apply (M code now loads all rows) |
| Training In-Person/Online YTD | $0 | Close & Apply + verify ETL output has current months |
| Summons Revenue (All/Moving/Parking) YTD | $0 | Summons ETL v2.5+ run + Close & Apply |
| ESU Arrests YTD | 0 | Likely legitimate zero for Q1 2026 |

---

## Display Folder Organization (New Measures)

| Folder | Measures |
|--------|----------|
| `Summary` | Outreach Events/Hours/Attendees YTD |
| `REMU YTD` | 7 REMU measures |
| `CSB YTD` | 7 CSB measures |
| `Det Case Disp YTD` | 5 Detective Case Disposition measures |
| `Det YTD` | 16 Detective measures (Part A + B) |
| `STACP YTD` | 25 STACP measures (Pt1 + Pt2) |
| `Traffic YTD` | 15 Traffic measures (MVA + Bureau) |
| `ESU YTD` | 8 ESU measures |
| `Patrol YTD` | 10 Patrol measures |
| `Training YTD` | 5 Training measures |
| `Summons YTD` | 5 Summons measures |

---

## Visual Creation — Next Session

All measures are created. Next session should focus on:

1. **Create Card (new) visuals** on each page using the YTD measures
2. **Create Summons_YTD page** (new page + cards + matrices)
3. **Normalize page names** to Title_Case_With_Underscores
4. **Response Time visuals** per PROMPT_Claude_MCP_Create_Missing_Visuals doc (6 visuals)
5. **DFR Summons visual** on Drone page
6. **Canvas contrast** evaluation

---

## Community Outreach — follow-ups (2026-03-26, MCP transcript)

See [handoffs/HANDOFF_Community_Outreach_PBIX_2026_03_25.md](handoffs/HANDOFF_Community_Outreach_PBIX_2026_03_25.md) and [chatlogs/community_outreach_claude_mcp/](chatlogs/community_outreach_claude_mcp/).

| Task | Notes |
|------|--------|
| **Matrix vs report month** | If “previous month” matrix shows wrong totals vs subtitle, add **`___DimMonth[MonthLabel]`** on that visual **or** add **Previous month** DAX measures (`EDATE` / `EOMONTH`). |
| **`measure SubtitlePrevMonth`** | Confirm no visual uses it; delete if orphaned. |
| **ETL output path** | Optional: wire **`output_settings.output_directory`** in **`main_processor.py`** to match **`config.json`** (M already reads `Community_Engagement\output\`). |
| **Save + refresh** | After ETL fixes: **Ctrl+S** PBIX, **Refresh**; re-export **`m_code/tmdl_export`** if repo parity required. |

---

*Session complete. Save .pbix → Close & Apply → verify.*
