# Prompt for Claude Desktop MCP: Create Missing Visuals for Monthly Report

**Purpose:** Pass this prompt to Claude Desktop with the Power BI MCP connected and `Monthly_Report_Template.pbix` (or `15_Templates\Monthly_Report_Template.pbix`) open. Claude will create the missing visuals described below.

**Prerequisites:**
1. Power BI Desktop open with `Monthly_Report_Template.pbix` loaded
2. Claude Desktop with Power BI MCP connected
3. Connect to the open model before pasting this prompt

---

## PROMPT START — Copy everything below this line

---

Connect to my open Power BI model (Monthly_Report_Template.pbix). I need you to create several missing visuals for the February 2026 monthly report. Here is the context and tasks.

### Context

- **Report:** Hackensack PD Monthly Report
- **Parameter:** `pReportMonth` controls all rolling windows (e.g. `#date(2026, 2, 1)` for Feb 2026)
- **Design system:** Read `CLAUDE.md` and `docs/templates/HPD_Report_Style_Prompt.md` for colors (navy #1a2744, gold #c8a84b, green #2e7d32, red #b71c1c) and typography. Do not use em dashes (—) or en dashes (–); use hyphens (-) or rephrase.
- **Reference materials:** 
  - `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\docs\chatlogs\Response_Time_AllMetrics_Migration_And_Documentation`
  - `C:\Users\carucci_r\OneDrive - City of Hackensack\KB_Shared\04_output\Claude-Response_time_metric_verification_artifacts`
  - `C:\Users\carucci_r\OneDrive - City of Hackensack\KB_Shared\04_output\Claude-Power_BI_response-time_metrics_implementation`

---

### Task 1: Response Time Visuals (6 visuals — TO BE CREATED)

The Response Time page needs **6 visuals** built from the `___ResponseTime_AllMetrics` table. This table already exists in the model (created 2026-03-06) and consolidates three metrics: Total Response, Travel Time, Dispatch Queue.

**Source table:** `___ResponseTime_AllMetrics`  
**Columns:** `Metric_Label`, `Metric_Sort`, `Response_Type`, `MonthName`, `Date_Sort_Key`, `Average_Response_Time`, `Response_Time_MMSS`, `Record_Count`, etc.

**Implementation reference:** `Master_Automation\docs\response_time\___ResponseTime_AllMetrics_IMPLEMENTATION.md`

**Dedicated Response Time prompt (Option B layout):** `docs\PROMPT_Claude_MCP_Response_Time_Visuals.md` - use for the 3-visual layout (KPI cards, Line chart with small multiples, Matrix).

**Create these 6 visuals:**

| # | Visual Name (for export mapping) | Type | Fields / Layout |
|---|----------------------------------|------|-----------------|
| 1 | Average Response Times  Values are in mmss | Line chart or Matrix | X: MonthName (sort by Date_Sort_Key), Y: Average_Response_Time or Response_Time_MMSS, Legend: Response_Type. Filter by Metric_Label = "Total Response" or show all three metrics with Metric_Label in Legend. |
| 2 | Response Times Detailed | Matrix | Rows: Response_Type, Metric_Label; Columns: MM-YY; Values: Response_Time_MMSS |
| 3 | Response Times by Priority | Line chart | X: MonthName, Y: Average_Response_Time, Legend: Response_Type. Use Metric_Label filter for Total Response. |
| 4 | Average Response Time (Dispatch to On Scene) | Matrix/Line | Filter Metric_Label = "Travel Time". Rows: Response_Type; Columns: MM-YY; Values: Response_Time_MMSS |
| 5 | Dispatch Processing Time (Call Received to Dispatch) | Matrix/Line | Filter Metric_Label = "Dispatch Queue". Same layout as #4. |
| 6 | Average Response Time (From Time Received to On Scene) | Matrix/Line | Filter Metric_Label = "Total Response". Same layout as #4. |

**Option B layout (from transcript):** Line chart + conditional-format matrix. X: Date_Sort_Key, Y: Average_Response_Time, Legend: Metric_Label, Small Multiples: Response_Type.

**Matrix columns:** Use `MM-YY` (not MonthName) for columns to match other tables. MM-YY sorts by Date_Sort_Key in the model.

**Filter rule:** Do not apply a Response_Type filter on the Line Chart or Matrix. All three Response_Type values (Emergency, Urgent, Routine) must be visible.

**DAX:** Confirm `RT Trend Total Response` exists (format "0.0 min"). Add `Response_Type_Sort` calc column if not present: `SWITCH([Response_Type], "Emergency", 1, "Urgent", 2, "Routine", 3, 99)`. Set MonthName and MM-YY to sort by Date_Sort_Key.

---

### Task 2: DFR Summons Visual (NEW — TO BE CREATED)

A new visual for **DFR Directed Patrol Summons** data. The M code query `DFR_Summons` loads from `dfr_directed_patrol_enforcement.xlsx` and applies a 13-month window.

**M code:** `Master_Automation\m_code\drone\DFR_Summons.m`  
**Source:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Drone\dfr_directed_patrol_enforcement.xlsx`  
**Table:** `DFR_Summons` (or `DFR_Summons` query — add to model if not present)

**Steps:**
1. If `DFR_Summons` query does not exist, create it using the M code from `m_code\drone\DFR_Summons.m`
2. Add the query to the model (enable load)
3. Create a new visual on the **Drone** page: table or matrix showing DFR summons by month (MM-YY, sorted by Date_Sort_Key), Description (ALL CAPS, shortened), Violation_Type (P/M/C), Location, etc. Use a 13-month trend or summary suitable for the Drone page layout.

**Reference:** `docs\PROMPT_Claude_In_Excel_DFR_Directed_Patrol_Summons_MCode.md`

---

### Task 3: Visuals to SKIP (do not create)

- **Chief Michael Antista's Projects and Initiatives** — blank for now; skip
- **Officer Summons Activity** — this visual does not exist on the Summons page; the 4 Summons visuals are: Department-Wide Summons, Summons Moving & Parking All Bureaus, Top 5 Parking, Top 5 Moving

---

### Task 4: Out-Reach Page

- **Engagement Initiatives by Bureau** — the only visual for the Out-Reach page. If it exists, ensure it is bound correctly. If not, create it from the `___Combined_Outreach_All` or equivalent community engagement table.

---

### Summary of Actions

1. **Create 6 Response Time visuals** from `___ResponseTime_AllMetrics` (see table above)
2. **Create DFR Summons visual** on Drone page (add query if needed, then visual)
3. **Skip** Chief Projects (blank) and Officer Summons Activity (does not exist)
4. **Verify** Engagement Initiatives by Bureau on Out-Reach page

After creating each visual, ensure it uses `pReportMonth`-driven data (no `TODAY()` or relative dates). Set visual names to match the export mapping so `process_powerbi_exports.py` can route them correctly when exported to CSV.

---

## PROMPT END

---

## Post-Prompt Checklist

After Claude creates the visuals:

1. **Export mapping:** Add `dfr_summons` (or `dfr_directed_patrol_summons`) to `Standards/config/powerbi_visuals/visual_export_mapping.json` with `target_folder: "drone"` so the DFR visual export routes correctly
2. **Refresh:** Run a full refresh to validate all visuals load data
3. **Export test:** Export one visual to `_DropExports` and run `python scripts/process_powerbi_exports.py --diagnose` to confirm matching
4. **Coverage:** Run `python scripts/process_powerbi_exports.py --coverage-report 2026_02` to see updated coverage

---

*Created: 2026-03-16 | Master_Automation*
