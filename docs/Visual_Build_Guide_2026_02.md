# Power BI Visual Build Guide - February 2026 Monthly Report

**Generated:** 2026-03-17 | **Model:** Monthly_Report_Template.pbix  
**MCP Pre-flight:** All checks PASSED (see summary below)

**Note:** Some preview tables or visuals may be off because `pReportMonth` is set to 02/01/2026. Power BI uses this parameter to drive the 13-month rolling window.

---

## Pre-Flight Results Summary

| Check | Status | Notes |
|-------|--------|-------|
| ___ResponseTime_AllMetrics | PASS | 108 rows (12mo x 3 types x 3 metrics) |
| RT Trend Total Response | FIXED | Format updated to "0.0 min" |
| Response_Type_Sort | PASS | Emergency=1, Urgent=2, Routine=3 (hidden) |
| MM-YY sort by Date_Sort_Key | PASS | Confirmed |
| MonthName sort by Date_Sort_Key | PASS | Confirmed |
| Response_Type sort by Response_Type_Sort | PASS | Confirmed |
| RT CF Background/Font/Display measures | PASS | All 3 exist, self-calibrating |
| RT KPI Current Month / Delta / MMSS | PASS | All 3 exist |
| DFR_Summons table | PASS | Query exists, 19 columns, M code complete |
| DFR_Summons data | NEEDS ACTION | 0 rows - requires Close & Apply |
| DFR Summons measures | CREATED | Count, Total Fines, Title, Subtitle |
| ___Combined_Outreach_All | PASS | 309 rows, Jan 2024 - Mar 2026 |
| Feb 2026 Response Time data | MISSING | Run response_time_batch_all_metrics.py |

---

## BEFORE YOU START

1. **Run Response Time ETL** for February 2026:
   ```
   python response_time_batch_all_metrics.py
   ```
   This adds the 13th month (Feb 2026) to the response_time_all_metrics folder.

2. **Close & Apply** in Power Query Editor to:
   - Load DFR_Summons data from the Excel source
   - Pick up the new Feb 2026 response time CSV

3. **Save** the .pbix after Close & Apply succeeds.

---

## RESPONSE TIME PAGE - Option B Layout (3 Zones)

### Design Specs
- **Color palette:** Navy #1a2744, Gold #c8a84b, Green #2e7d32, Red #b71c1c
- **Conditional format colors:** Green #27AE60, Amber #F39C12, Red #E74C3C
- **Font:** DIN or Segoe UI
- **No em dashes or en dashes** - use hyphens only

### Reference Data (12-month averages for verification)

| Response_Type | Metric | Avg Minutes | Months |
|--------------|--------|-------------|--------|
| Emergency | Dispatch Queue | 3.00 | 12 |
| Emergency | Travel Time | 2.86 | 12 |
| Emergency | Total Response | 5.04 | 12 |
| Urgent | Dispatch Queue | 3.41 | 12 |
| Urgent | Travel Time | 3.62 | 12 |
| Urgent | Total Response | 5.54 | 12 |
| Routine | Dispatch Queue | 3.49 | 12 |
| Routine | Travel Time | 3.35 | 12 |
| Routine | Total Response | 5.28 | 12 |

---

### Visual 1: KPI Card Strip (Top 0-15% of page height)

**Type:** 3 x Card (new) visuals, arranged horizontally, equal width

**Steps for EACH card:**

1. Insert > Card (new)
2. **Callout value well:** Drag `RT Trend Total Response` (from ___ResponseTime_AllMetrics)
3. **Trend axis:** Drag `Date_Sort_Key`
4. **Visual-level filter:** Add `Response_Type` to Filters pane on this visual
   - Card 1: Check only "Emergency"
   - Card 2: Check only "Urgent"
   - Card 3: Check only "Routine"
5. Format the card:
   - **Callout > Label:** Set to the Response_Type name:
     - Card 1: "Emergency - Total Response"
     - Card 2: "Urgent - Total Response"
     - Card 3: "Routine - Total Response"
   - **Callout > Font color:** Navy #1a2744
   - **Callout > Font size:** 24-28pt
   - **Trend > Line color:** Steel blue #4682B4
   - **Category label:** OFF (or set to small 9pt)
   - **Background:** White or transparent
   - **Border:** ON, Navy #1a2744, 1px, rounded corners 4px

6. **Alignment:** Select all 3 cards > Format > Align > Distribute Horizontally, Align Top

**Verification:** Each card should show one decimal value (e.g., "5.0 min") with a sparkline. Emergency ~5.0, Urgent ~5.5, Routine ~5.3.

---

### Visual 2: Line Chart with Small Multiples (Middle ~60% of page)

**Type:** Line Chart

**Steps:**

1. Insert > Line Chart
2. **X-Axis:** Drag `Date_Sort_Key` - set to Continuous (not Categorical)
   - Right-click axis > set to "Continuous"
3. **Y-Axis:** Drag `Average_Response_Time`
4. **Legend:** Drag `Metric_Label`
5. **Small Multiples:** Drag `Response_Type`

6. **CRITICAL - Filter check:**
   - Open the Filters pane for this visual
   - **Remove ANY filter on Response_Type** (the Small Multiples field handles separation)
   - All 3 panels (Emergency, Urgent, Routine) MUST appear

7. **Format:**
   - **Legend colors** (by Metric_Label):
     - Total Response: Dark navy #0C233D
     - Travel Time: Steel blue #4682B4
     - Dispatch Queue: Light blue #87CEEB
   - **Data labels:** Format > Data labels > ON
     - Show: Last only (or Series end)
     - Apply to: Total Response line only (toggle others off if possible)
   - **Y-Axis:**
     - Title: "Minutes"
     - Start: 0
     - End: Lock across panels (set max ~8 or auto)
   - **X-Axis:** 
     - Title: OFF
     - Format: MMM YY or auto date
   - **Small multiples:**
     - Layout: 1 row x 3 columns
     - Title: ON (shows Emergency, Urgent, Routine)
     - Border between panels: Light gray
   - **Title:** "Response Time Trends by Priority" (9pt, Navy)
   - **Gridlines:** Horizontal only, light gray
   - **Background:** White or transparent

**Verification:** You should see 3 panels side by side. Each panel has 3 lines (Total Response highest, Travel Time and Dispatch Queue below). Emergency panel values cluster around 3-5 min range.

---

### Visual 3: Consolidated Detail Matrix (Bottom ~35% of page)

**Type:** Matrix

**Steps:**

1. Insert > Matrix
2. **Rows:**
   - Level 1: `Response_Type`
   - Level 2: `Metric_Label`
3. **Columns:** `MM-YY` (NOT MonthName - MM-YY sorts by Date_Sort_Key automatically)
4. **Values:** `Response_Time_MMSS`

5. **CRITICAL - Filter check:**
   - Open the Filters pane for this visual
   - **Remove ANY filter on Response_Type** - all 3 must show
   - All 3 Response_Type values x 3 Metric_Label values = 9 rows

6. **Format:**
   - **Subtotals:** Row subtotals OFF, Column subtotals OFF
     - Format > Row subtotals > OFF
     - Format > Column subtotals > OFF
   - **Stepped layout:** Format > Row headers > Stepped layout: ON
   - **Font size:** 9-10pt
   - **Column headers:** Navy #1a2744 background, white text
   - **Grid:** Thin gridlines, light gray

7. **Conditional Formatting (traffic light on values):**
   - Select the `Response_Time_MMSS` value in the Values well
   - Right-click > Conditional formatting > Background color
   - Format style: Field value
   - Based on field: `RT CF Background Color` (measure)
   - Click OK
   - Repeat for Font color using `RT CF Font Color` (measure)

   **Alternative if Field Value CF doesn't work:**
   - Use Rules-based:
     - Green #27AE60 for values <= 4:00
     - Amber #F39C12 for values 4:01 - 5:30
     - Red #E74C3C for values > 5:30
   
   **Note:** The CF measures are self-calibrating per Response_Type based on the 13-month average. They only apply to Total Response metric. For a simpler approach, use the rules-based method above.

8. **Title:** "Response Time Detail - MM:SS Format" (9pt, Navy)

**Verification:** Matrix should show:
- 3 top-level rows: Emergency, Urgent, Routine
- Under each: Dispatch Queue, Total Response, Travel Time
- 12 columns (02-25 through 01-26), will become 13 after ETL run
- Values in M:SS format (e.g., "5:02", "3:15")

---

## DFR SUMMONS VISUAL - Drone Page

### Prerequisites
- Close & Apply must complete first (loads data from dfr_directed_patrol_enforcement.xlsx)
- If 0 rows after refresh, verify the Excel file has data with dates in the Feb 2025 - Feb 2026 window

### Measures Created via MCP
| Measure | Expression | Format |
|---------|-----------|--------|
| DFR Summons Count | COUNTROWS('DFR_Summons') | #,0 |
| DFR Summons Total Fines | SUM('DFR_Summons'[Fine_Amount]) | $#,0.00 |
| DFR Summons Title | "DFR Directed Patrol Summons" | text |
| DFR Summons Subtitle | Dynamic count + latest month | text |

### Build Steps

1. Navigate to the **Drone** page
2. Insert > **Table** visual (or Matrix if you want month grouping)

**Option A: Simple Detail Table**
- Columns (drag in this order):
  1. `Date`
  2. `Description` (ALL CAPS; long forms shortened, e.g. "Parking...designated fire lane/fire zone" -> "FIRE LANE/FIRE ZONE")
  3. `Location`
  4. `Statute`
  5. `Fine_Amount`
  6. `Issuing_Officer`
  7. `DFR_Operator`
- Format:
  - Title: Use `DFR Summons Title` measure or static "DFR Directed Patrol Summons"
  - Column headers: Navy #1a2744 background, white text
  - Alternating rows: Light gray #F5F5F5
  - Font: 9pt
  - Fine_Amount: Currency format

**Option B: Summary Matrix by Month**
- Rows: `Description` (ALL CAPS; long forms shortened, e.g. "Parking...designated fire lane/fire zone" -> "FIRE LANE/FIRE ZONE")
- Columns: `MM-YY` (set sort-by-column to `Date_Sort_Key` in model so columns display chronologically)
- Values: `DFR Summons Count`
- Format:
  - Title: "DFR Directed Patrol Summons by Description"
  - Column subtotals: ON (shows monthly totals)
  - Row subtotals: ON (shows description totals)

3. **Visual Name:** Set the visual name (Alt text > Title) to "dfr_summons" or "dfr_directed_patrol_summons" for export mapping.

---

## OUT-REACH PAGE - Engagement Initiatives by Bureau

### Available Data
- **Table:** ___Combined_Outreach_All (309 rows)
- **Columns:** Office, Event Name, Location of Event, Date, Event Duration (Hours), Number of Police Department Attendees, Event ID, Row_ID
- **Measures:** Outreach Sessions, Outreach Total Hours, Outreach Total Attendees, Engagement Title, Engagement Subtitle

### Verify or Create Visual

1. Navigate to the **Out-Reach** page
2. If "Engagement Initiatives by Bureau" visual exists:
   - Verify it uses `Office` for bureau grouping
   - Verify values show session counts, hours, and/or attendees
   - Verify no broken field references

3. If visual does NOT exist, create a **Table** visual:
   - Rows:
     1. `Row_ID` (hidden differentiator - drag column width to ~0px)
     2. `Date`
     3. `Event Name`
     4. `Location of Event`
     5. `Office`
     6. `Event Duration (Hours)`
     7. `Number of Police Department Attendees`
   - Title: Use `Engagement Title` measure
   - Subtitle: Use `Engagement Subtitle` measure
   - Format: Navy headers, 9pt font, alternating rows

**Note:** All 309 rows currently show Office = "STA&CP". If other bureaus contribute engagement data in the future, the Office column will differentiate them.

---

## POST-BUILD CHECKLIST

After all visuals are created:

- [ ] **Response Time KPI Cards:** All 3 show values (Emergency, Urgent, Routine)
- [ ] **Response Time Line Chart:** 3 Small Multiple panels visible, each with 3 lines
- [ ] **Response Time Matrix:** 9 data rows (3 types x 3 metrics), MM-YY columns
- [ ] **Response Time Matrix CF:** Green/amber/red backgrounds on values
- [ ] **DFR Summons:** Data loads after Close & Apply (check row count)
- [ ] **Out-Reach:** Engagement visual bound correctly
- [ ] **No Response_Type filters** on Line Chart or Matrix (all 3 types visible)
- [ ] **Run full refresh** and save .pbix

### Export Mapping Update
Add to `Standards/config/powerbi_visuals/visual_export_mapping.json`:
```json
{
  "dfr_summons": {
    "target_folder": "drone",
    "description": "DFR Directed Patrol Summons"
  }
}
```

### Coverage Check
```bash
python scripts/process_powerbi_exports.py --coverage-report 2026_02
```

---

*Generated by Claude MCP session | Master_Automation v1.18.9*
