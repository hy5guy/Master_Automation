// 🕒 2026-03-23-18-15-00 (Task D DAX cleanup + MCP summary 2026-03-24)
// # Monthly_Report_Template/TASKS_A_THROUGH_F_DELIVERABLE.md
// # Author: R. A. Carucci
// # Purpose: Complete deliverable for Tasks A-F — YTD card placement, Summons_YTD page, page normalization, Response Time visuals, DFR Summons visual, and contrast evaluation.

---

# Tasks A–F: Visual Creation & Page Normalization Deliverable

**Model:** `Monthly_Report_Template.pbix` (localhost port varies per Desktop session)
**Session:** 2026-03-23
**MCP Limitation:** Cannot create/position visuals or rename pages. All items below are **manual build checklists**.

### Verified via MCP (same session)

| Item | Result |
|------|--------|
| YTD measures | **101** across **13** display folders |
| `___ResponseTime_AllMetrics` | Present (**15** columns); `MonthName`, `MM-YY`, `Metric_Label` sort columns OK |
| `DFR_Summons` | Present (**20** columns); includes `FINE_AMOUNT`, `DateSortKey`, `YearMonthKey`; **4** DFR measures |
| `Response_Type_Sort` | **Missing** — `column_operations` blocked; add manually (canonical DAX under Task D) |
| Summons revenue | Stays **$0** until **`run_summons_etl.py`** v2.5+ + refresh populates **`FINE_AMOUNT`** on `___Summons` |
| Training YTD blanks | After **Close & Apply** with repo **___In_Person_Training** / **___Cost_of_Training** M (full rows + YTD period union) |

---

## Executive Summary

| Task | Status | Detail |
|------|--------|--------|
| A — YTD Card visuals | ✅ Measures confirmed (101) | Checklist below for manual card placement |
| B — Summons_YTD page | ✅ Measures confirmed (5) | Page creation + card/matrix spec below |
| C — Page rename | ✅ Table produced | 25+ pages → Title_Case_Underscores |
| D — Response Time visuals | ✅ Table + 22 RT measures exist | 6-visual spec below; `Response_Type_Sort` needs manual add |
| E — DFR Summons visual | ✅ Table (20 cols) + 4 measures exist | Visual spec for Drone page below |
| F — Canvas contrast | ⚠️ Cannot evaluate visually via MCP | Recommendations from theme doc below |

---

## Task A — YTD Card Visuals (Page-by-Page Checklist)

**Visual type:** Card (new) — callout value = YTD measure, no trend sparkline unless noted.
**Style:** Navy border `#1a2744`, DIN font, gold accent `#c8a84b` for Warrant/currency only. Card title = short label. Format: counts `#,0`, currency `$#,0`.
**Layout:** Horizontal strip at top or bottom of page (3–5 cards per row).

### Page: Out_Reach (Outreach / Community Engagement)

| Card Title | Measure Name | Format | Position |
|-----------|-------------|--------|----------|
| Events YTD | `Outreach Events YTD` | #,0 | Top row, left |
| Hours YTD | `Outreach Hours YTD` | #,0.0 | Top row, center |
| Attendees YTD | `Outreach Attendees YTD` | #,0 | Top row, right |

### Page: REMU (Records & Evidence)

| Card Title | Measure Name | Format |
|-----------|-------------|--------|
| Records Requests | `REMU Records Requests YTD` | #,0 |
| OPRA Requests | `REMU OPRA Requests YTD` | #,0 |
| Discovery Requests | `REMU Discovery Requests YTD` | #,0 |
| NIBRS Entries | `REMU NIBRS Entries YTD` | #,0 |
| Applications/Permits | `REMU Applications Permits YTD` | #,0 |
| Background Checks | `REMU Background Checks YTD` | #,0 |
| Evidence Received | `REMU Evidence Received YTD` | #,0 |

**Layout:** Row of 4 + row of 3, or single row of 7 if space permits.

### Page: Crime Suppression Bureau (CSB)

| Card Title | Measure Name | Format |
|-----------|-------------|--------|
| Arrests | `CSB Arrests YTD` | #,0 |
| Currency Seized | `CSB Currency Seized YTD` | $#,0 |
| Drug-Related Arrests | `CSB Drug-Related Arrests YTD` | #,0 |
| Generated Complaints | `CSB Generated Complaints YTD` | #,0 |
| High Value Items | `CSB High Value Items Seized YTD` | $#,0 |
| MV Thefts | `CSB Motor Vehicle Thefts YTD` | #,0 |
| Weapons Seized | `CSB Weapons Seized YTD` | #,0 |

### Page: Detective Case Disposition

| Card Title | Measure Name | Format |
|-----------|-------------|--------|
| Active/Admin Closed | `Det Active Admin Closed YTD` | #,0 |
| Arrest | `Det Arrest Disp YTD` | #,0 |
| Complaint Signed | `Det Complaint Signed YTD` | #,0 |
| Ex Cleared/Closed | `Det Ex Cleared Closed YTD` | #,0 |
| Unfounded/Closed | `Det Unfounded Closed YTD` | #,0 |

### Page: Detective_1 (Part A — top strip)

| Card Title | Measure Name |
|-----------|-------------|
| Agg. Assault | `Det Aggravated Assault YTD` |
| Arson | `Det Arson YTD` |
| Bias | `Det Bias YTD` |
| Burglary-Auto | `Det Burglary Auto YTD` |
| Burglary-Commercial | `Det Burglary Commercial YTD` |
| Burglary-Residence | `Det Burglary Residence YTD` |
| Crim. Sexual Contact | `Det Criminal Sexual Contact YTD` |

### Page: Detective_1 (Part B — bottom strip or second row)

| Card Title | Measure Name |
|-----------|-------------|
| Firearm Bg Checks | `Det Firearm Background Checks YTD` |
| Firearm Investigations | `Det Firearm Investigations YTD` |
| Generated Complaints | `Det Generated Complaints YTD` |
| Lewdness | `Det Lewdness YTD` |
| MV Theft | `Det Motor Vehicle Theft YTD` |
| Robbery | `Det Robbery YTD` |
| Sexual Assault | `Det Sexual Assault YTD` |
| Terroristic Threats | `Det Terroristic Threats YTD` |
| Theft | `Det Theft YTD` |

**Note:** 16 total Det YTD cards across 2 groups — split across the two Detective pages or use two rows on one page.

### Page: STACP_Pt1

| Card Title | Measure Name |
|-----------|-------------|
| Arrests | `STACP Arrests YTD` |
| Assaults | `STACP Assaults YTD` |
| Burglary | `STACP Burglary YTD` |
| CDS | `STACP CDS YTD` |
| Child Abuse | `STACP Child Abuse YTD` |
| Child Endangerment | `STACP Child Endangerment YTD` |
| Criminal Mischief | `STACP Criminal Mischief YTD` |
| Curbside Warning | `STACP Curbside Warning YTD` |
| Cyber Harassment | `STACP Cyber Harassment YTD` |
| DCP&P Notification | `STACP DCPP Notification YTD` |
| DCP&P Referrals | `STACP DCPP Referrals YTD` |
| Juvenile Complaints | `STACP Juvenile Complaints YTD` |
| Juvenile Incident | `STACP Juvenile Incident YTD` |
| Juv. Short-Term Custody | `STACP Juvenile Short-Term Custody YTD` |

### Page: STACP_Pt2

| Card Title | Measure Name |
|-----------|-------------|
| Luring | `STACP Luring YTD` |
| Missing Person | `STACP Missing Person YTD` |
| Station House Adj. | `STACP Station House Adj YTD` |
| Terroristic Threats | `STACP Terroristic Threats YTD` |
| Theft | `STACP Theft YTD` |
| Threat Assessments | `STACP Threat Assessments YTD` |
| Trespassing | `STACP Trespassing YTD` |
| Underage Alcohol | `STACP Underage Alcohol YTD` |
| Underage CDs | `STACP Underage CDs YTD` |
| Weapons | `STACP Weapons YTD` |
| Welfare Checks | `STACP Welfare Checks YTD` |

### Page: Traffic_MVA (Motor Vehicle Accidents)

| Card Title | Measure Name | Format |
|-----------|-------------|--------|
| All MVA | `Traffic All MVA YTD` | #,0 |
| Bicyclist Struck | `Traffic Bicyclist Struck YTD` | #,0 |
| Hit & Run | `Traffic Hit And Run YTD` | #,0 |
| Pedestrian Struck | `Traffic Pedestrian Struck YTD` | #,0 |
| Police Vehicle | `Traffic Police Vehicle YTD` | #,0 |
| With Injury | `Traffic With Injury YTD` | #,0 |

### Page: Traffic (Bureau Activity)

| Card Title | Measure Name | Format |
|-----------|-------------|--------|
| DUI Incidents | `Traffic DUI Incidents YTD` | #,0 |
| Fatal Incidents | `Traffic Fatal Incidents YTD` | #,0 |
| Assigned H&R Inv. | `Traffic Assigned MVA HitRun YTD` | #,0 |
| Closed H&R Inv. | `Traffic Closed MVA HitRun YTD` | #,0 |
| Officer Accident Reviews | `Traffic Officer Accident Reviews YTD` | #,0 |
| MV Stops | `Traffic MV Stops YTD` | #,0 |
| City Ord. Violations | `Traffic City Ord Violations YTD` | #,0 |
| City Ord. Warnings | `Traffic City Ord Warnings YTD` | #,0 |
| Parking Fees Collected | `Traffic Parking Fees YTD` | $#,0 |

### Page: ESU (Emergency Service Unit)

| Card Title | Measure Name |
|-----------|-------------|
| Arrests | `ESU Arrests YTD` |
| Assist Other Bureau | `ESU Assist Other Bureau YTD` |
| ESU OOS | `ESU OOS YTD` |
| Single Operator | `ESU Single Operator YTD` |
| Forcible Entries | `ESU Forcible Entries YTD` |
| ICS Functions | `ESU ICS Functions YTD` |
| MV Lock Outs | `ESU MV Lock Outs YTD` |
| Targeted Area Patrols | `ESU Targeted Area Patrols YTD` |

### Page: Patrol

| Card Title | Measure Name |
|-----------|-------------|
| Arrive Program | `Patrol Arrive Program YTD` |
| Calls for Service | `Patrol Calls for Service YTD` |
| CDS Arrests | `Patrol CDS Arrests YTD` |
| DUI Arrests | `Patrol DUI Arrests YTD` |
| DV Arrests | `Patrol DV Arrests YTD` |
| DV Incidents | `Patrol DV Incidents YTD` |
| Mental Health Calls | `Patrol Mental Health Calls YTD` |
| MV Stops | `Patrol MV Stops YTD` |
| NARCAN Deployment | `Patrol NARCAN Deployment YTD` |
| Self-Initiated Arrests | `Patrol Self-Initiated Arrests YTD` |

### Page: Policy & Training

| Card Title | Measure Name | Format |
|-----------|-------------|--------|
| Classes Attended | `Training Classes Attended YTD` | #,0 |
| Course Duration | `Training Course Duration YTD` | #,0.0 |
| Training Cost | `Training Cost YTD` | $#,0 |
| In-Person Cost | `Training In-Person YTD` | $#,0 |
| Online Cost | `Training Online YTD` | $#,0 |

### Page: Arrest_13

Already has: `Arrests YTD`, `Arrests YTD Rank`, `Title Top 5 Arrests YTD`, `Subtitle Top 5 Arrests YTD`, `Arrest Out-of-Town %`

| Card Title | Measure Name | Format |
|-----------|-------------|--------|
| Arrests YTD | `Arrests YTD` | #,0 |
| Non-Local % | `Arrest Out-of-Town %` | 0.0% |

---

## Task B — Summons_YTD Page (New)

### Step 1: Create page named `Summons_YTD`

### Step 2: KPI Cards (top strip)

| Card Title | Measure Name | Format |
|-----------|-------------|--------|
| Moving Summons YTD | `Moving Summons YTD` | #,0 |
| Parking Summons YTD | `Parking Summons YTD` | #,0 |
| Revenue - All Bureaus | `Summons Revenue All Bureaus YTD` | $#,0 |
| Revenue - Moving | `Summons Revenue Moving YTD` | $#,0 |
| Revenue - Parking | `Summons Revenue Parking YTD` | $#,0 |

**Note:** Revenue measures will show $0 until Summons ETL v2.5+ runs and Close & Apply refreshes `FINE_AMOUNT`.

### Step 3: Matrix tables (middle section)

| Matrix | Rows | Values | Filter | Notes |
|--------|------|--------|--------|-------|
| All Bureaus YTD | `___Summons[WG2]` | `Moving Summons YTD`, `Parking Summons YTD` | None | Grand total row |
| Top 5 Parking YTD | `___Summons[OFFICER_DISPLAY_NAME]` | `Parking Summons YTD` | Visual TopN = 5 | Sort desc |
| Top 5 Moving YTD | `___Summons[OFFICER_DISPLAY_NAME]` | `Moving Summons YTD` | Visual TopN = 5 | Sort desc |

**⚠️ Deferred:** Revenue-by-employee Top 5 matrices require a RANKX measure that doesn't exist yet. Create:
```dax
Summons Revenue Parking Rank YTD =
RANKX(
    ALLSELECTED('___Summons'[OFFICER_DISPLAY_NAME]),
    [Summons Revenue Parking YTD],,DESC,DENSE
)
```
Same pattern for Moving.

### Step 4: Export mapping follow-up
Add to `visual_export_mapping.json`:
```json
"summons_ytd_moving": { "target_folder": "summons", "backfill_folder": "summons" },
"summons_ytd_parking": { "target_folder": "summons", "backfill_folder": "summons" },
"summons_ytd_all_bureaus": { "target_folder": "summons", "backfill_folder": "summons" }
```

---

## Task C — Page Name Normalization

| Current Name (approximate) | New Name | Notes |
|---------------------------|----------|-------|
| Arrest 13 | `Arrest_13` | |
| Response Time | `Response_Time` | |
| Benchmark | `Benchmark` | No change needed |
| Out-Reach | `Out_Reach` | Hyphen → underscore |
| Summons | `Summons` | No change |
| (new) | `Summons_YTD` | Task B |
| Policy & Training Qual | `Policy_And_Training_Qual` | Ampersand → And |
| REMU | `REMU` | No change |
| Crime Suppression Bureau | `Crime_Suppression_Bureau` | |
| Detective Case Disposition | `Detective_Case_Disposition` | |
| Detective 1 | `Detective_1` | If two pages, `Detective_1_A` / `Detective_1_B` |
| STACP Pt1 | `STACP_Pt1` | |
| STACP Pt2 | `STACP_Pt2` | |
| Traffic MVA | `Traffic_MVA` | |
| Traffic | `Traffic` | No change |
| ESU | `ESU` | No change |
| Patrol | `Patrol` | No change |
| Drone / DFR | `Drone_DFR` | Consolidate slash name |
| Social Media | `Social_Media` | |
| SSOCC | `SSOCC` | No change |
| Chief LED | `Chief_LED` | |
| NIBRS | `NIBRS` | No change |
| Overtime / Time Off | `Overtime_TimeOff` | |
| High Activity | `High_Activity` | |
| TAS | `TAS` | No change |

**⚠️ Bookmark/tooltip check:** If any page is a tooltip target or has bookmarks, update those references after rename.

---

## Task D — Response Time: 6 Visuals Spec

### Prerequisites in Model (verified ✅)
- Table `___ResponseTime_AllMetrics` — 15 columns, exists ✅
- `MonthName` sorts by `Date_Sort_Key` ✅
- `MM-YY` sorts by `Date_Sort_Key` ✅
- `Metric_Label` sorts by `Metric_Sort` ✅
- 22 RT measures exist in `RT Measures` folder ✅

### Manual step required: `Response_Type_Sort` calculated column

MCP **`column_operations`** is blocked (AS engine state). Add in Power BI Desktop:

1. Table **`___ResponseTime_AllMetrics`** → **New column**
2. Paste **only** this definition (order **Routine → Urgent → Emergency** when sorted ascending on this column):

```dax
Response_Type_Sort =
SWITCH (
    '___ResponseTime_AllMetrics'[Response_Type],
    "Routine", 1,
    "Urgent", 2,
    "Emergency", 3,
    99
)
```

3. Select column **`Response_Type`** → **Sort by column** → **`Response_Type_Sort`**
4. Use for **Small Multiples** / axis ordering on Response Time line visuals as needed

### Visual 1: Line Chart — Response Times by Priority (Total Response)

| Setting | Value |
|---------|-------|
| **Type** | Line Chart |
| **X-axis** | `Date_Sort_Key` (continuous date) |
| **Y-axis** | `RT Avg Formatted` (format `#":"00`) |
| **Legend** | None — use **Small Multiples** |
| **Small Multiples** | `Response_Type` (sorted by `Response_Type_Sort`) |
| **Filter** | `Metric_Label` = "Total Response" |
| **Data labels** | `RT Avg Label` (M:SS text) |
| **Title** | Use measure `RT Average Title` |
| **Subtitle** | Use measure `RT Line Chart Subtitle` |

### Visual 2: Matrix — Response Times Detailed (All Metrics × All Types)

| Setting | Value |
|---------|-------|
| **Type** | Matrix |
| **Rows** | `Response_Type`, `Metric_Label` |
| **Columns** | `MM-YY` (sorted by `Date_Sort_Key`) |
| **Values** | `RT CF Display Value` (M:SS text) |
| **Conditional Format — Background** | `RT CF All Metrics Background` (rules-based, field value) |
| **Conditional Format — Font Color** | `RT CF All Metrics Font` (rules-based, field value) |
| **Title** | "Response Time Matrix - All Metrics" |

### Visual 3: KPI Cards (3 cards — one per metric)

| Card | Callout | Trend | Reference Label |
|------|---------|-------|-----------------|
| Total Response | `RT KPI Current Month MMSS` | `RT Trend Total Response` | "13-mo avg" |
| Travel Time | `RT Avg Travel Time` | `RT Trend Travel Time` | — |
| Dispatch Queue | `RT Avg Dispatch Queue` | `RT Trend Dispatch Queue` | — |

### Visual 4: Matrix — Travel Time (Dispatch to On Scene)

Same as Visual 2 but with page-level filter: `Metric_Label = "Travel Time"`
- **Values:** `RT CF Display Value`
- **CF Background/Font:** Same measures (they're universal)
- **Title:** Use `RT Average Title`

### Visual 5: Matrix — Dispatch Queue (Call Received to Dispatch)

Same layout, filter: `Metric_Label = "Dispatch Queue"`
- **Title:** Use `RT DispVsCall Title`

### Visual 6: Matrix — Total Response (Time Received to On Scene)

Same layout, filter: `Metric_Label = "Total Response"`
- **Title:** Use `RT OutVsCall Title`

**Option B Layout (Recommended — Council):** Visuals 1 + 2 + 3 on a single page. Visuals 4/5/6 are filtered views of Visual 2 and can be omitted if the full matrix is sufficient.

---

## Task E — DFR Summons Visual on Drone Page

### Prerequisites (verified ✅)
- Table `DFR_Summons` — 20 columns including `Date`, `Description`, `FINE_AMOUNT`, `Violation_Type`, `DateSortKey`, `YearMonthKey`
- 4 measures in `DFR Measures`: `DFR Summons Count`, `DFR Summons Total Fines`, `DFR Summons Title`, `DFR Summons Subtitle`

### Visual Spec: Table/Matrix on Drone Page

| Setting | Value |
|---------|-------|
| **Type** | Table (tabular, scrollable) or Matrix |
| **Columns** | `Date`, `Summons_Number`, `Description`, `Violation_Type`, `Location`, `FINE_AMOUNT`, `Summons_Status` |
| **Sort** | `Date` descending |
| **Title** | `DFR Summons Title` (measure) |
| **Subtitle** | `DFR Summons Subtitle` (measure) |
| **Position** | Below existing DFR Activity matrix on Drone page |

### Alternative: Summary Matrix (trending)

| Setting | Value |
|---------|-------|
| **Type** | Matrix |
| **Rows** | `Violation_Type` |
| **Columns** | Derived MM-YY from `YearMonthKey` (or add computed column) |
| **Values** | `DFR Summons Count`, `DFR Summons Total Fines` |

### Export Mapping Follow-Up
Add to `visual_export_mapping.json`:
```json
"dfr_directed_patrol_summons": { "target_folder": "drone", "backfill_folder": "drone" },
"dfr_total_fines_ytd": { "target_folder": "drone", "backfill_folder": "drone" }
```

---

## Task F — Canvas Contrast Evaluation

**Cannot evaluate visually via MCP.** Recommendations based on HPD theme doc:

### Known Risks from Theme
| Issue | Where | Fix |
|-------|-------|-----|
| Gold (#c8a84b) on white card background | KPI card labels, Warrant category | Add navy (#1a2744) background to card, or use dark text for gold labels |
| Thin gray text on light background | Matrix column headers, axis labels | Ensure font weight ≥ 400, font size ≥ 10px |
| Conditional format amber (#F39C12) with dark font | RT matrix cells | Already uses `#1A1A1A` — verify readability |
| Small Multiples panel titles | RT line chart Response_Type labels | Verify font is ≥ 10px, navy color |

### Recommended Pass (Manual)
After placing all visuals:
1. Toggle between light and dark monitor settings
2. Check every card: title text vs card background
3. Check every matrix: header row contrast, conditional format cells (green text on green bg?)
4. Check line charts: legend colors distinguishable?
5. Print preview: do navy backgrounds print solid or washed out?

---

## Next Manual Steps (Ordered)

1. **Save .pbix** (Ctrl+S) — persists 101 measures + 2 M code updates
2. **Add `Response_Type_Sort` calc column** (Task D prerequisite)
3. **Close & Apply** in Power Query Editor — triggers M code refreshes
4. **Run Summons ETL** if not done: `python run_summons_etl.py` (populates FINE_AMOUNT)
5. **Add `summons_revenue_by_violation_category` query** via Power Query Editor
6. **Create Summons_YTD page** + all card/matrix visuals (Task B)
7. **Build Card visuals** on each page per Task A checklist
8. **Build 6 Response Time visuals** per Task D spec
9. **Build DFR Summons visual** on Drone page per Task E spec
10. **Rename pages** per Task C table
11. **Canvas contrast pass** per Task F
12. **Update `visual_export_mapping.json`** with new visual names
13. **Export test:** `python scripts/process_powerbi_exports.py --diagnose`

---

*End of deliverable. All measure names are exact model names — copy/paste into Power BI field wells.*
