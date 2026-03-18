# Power BI Visual Build Guide - February 2026 Monthly Report
# Manual Visual Construction Instructions

**Generated:** 2026-03-17 | **Model:** Monthly_Report_Template.pbix (port 57475)
**Design System:** Navy #1a2744, Gold #c8a84b, Green #2e7d32, Red #b71c1c
**Typography:** DIN or Segoe UI | No em dashes or en dashes - hyphens only

---

## MCP Model Work Completed (Both Sessions)

### Response Time Table (___ResponseTime_AllMetrics)
- [x] Table confirmed: 108 rows (12 months x 3 Response_Types x 3 Metrics)
- [x] `RT Trend Total Response` format fixed: "0.0 min"
- [x] `Metric_Label` now sorts by `Metric_Sort` (Dispatch Queue=1, Travel Time=2, Total Response=3)
- [x] `Metric_Sort` hidden
- [x] `MM-YY` sorts by `Date_Sort_Key`
- [x] `MonthName` sorts by `Date_Sort_Key`
- [x] `Response_Type` sorts by `Response_Type_Sort` (Emergency=1, Urgent=2, Routine=3)
- [x] Created `RT Trend Travel Time` (format "0.0 min")
- [x] Created `RT Trend Dispatch Queue` (format "0.0 min")
- [x] Created `RT CF All Metrics Background` - universal CF for all metric/type combos
- [x] Created `RT CF All Metrics Font` - universal font color companion
- [x] All 6 title/subtitle measures moved to "RT Measures" display folder
- [x] Total: 20 measures on ___ResponseTime_AllMetrics

### DFR Summons Table
- [x] `DFR_Summons` table confirmed: full M code, 19 columns, 13-month window
- [x] Created `DFR Summons Count`, `DFR Summons Total Fines`, `DFR Summons Title`, `DFR Summons Subtitle`
- [x] Data is EMPTY - requires Close & Apply to load from Excel source

### Outreach Table (___Combined_Outreach_All)
- [x] Table confirmed: 309 rows, Jan 2024 - Mar 2026
- [x] Fixed `Engagement Subtitle` - removed TODAY(), now uses data range
- [x] Fixed `DateInPrevMonth` - removed TODAY(), now uses max data date
- [x] Total: 8 measures available

### Data Gap
- [x] Feb 2026 response time data MISSING - run `response_time_batch_all_metrics.py`

### Model-Wide Issue Identified
- 50+ measures across other tables still use TODAY() - separate cleanup task

---

## BEFORE BUILDING VISUALS

1. **Run Response Time ETL:**
   ```
   python response_time_batch_all_metrics.py
   ```

2. **Close & Apply** in Power Query Editor (loads DFR_Summons, picks up new RT CSV)

3. **Save** the .pbix

---

## RESPONSE TIME PAGE

### Layout: Option B (3-Zone Design)

```
+--------------------------------------------------+
|  [Emergency KPI]  [Urgent KPI]  [Routine KPI]    |  <- Top 15%
+--------------------------------------------------+
|                                                    |
|    Line Chart with Small Multiples                 |  <- Middle 60%
|    [Emergency]    [Urgent]      [Routine]          |
|                                                    |
+--------------------------------------------------+
|    Matrix: Response_Type > Metric_Label            |  <- Bottom 35%
|    Columns: MM-YY | Values: Response_Time_MMSS     |
+--------------------------------------------------+
```

---

### VISUAL 1: KPI Card Strip (3 cards, top row)

**Create 3 Card (new) visuals, horizontally aligned**

For EACH card:

1. **Insert** > Visualizations > Card (new)
2. **Data wells:**
   - Callout value: `RT Trend Total Response`
   - Trend axis: `Date_Sort_Key`
3. **Visual-level filter** (Filters pane > Filters on this visual):
   - Drag `Response_Type` to the filter area
   - Card 1: select only **Emergency**
   - Card 2: select only **Urgent**
   - Card 3: select only **Routine**
4. **Format (each card):**
   - Callout > Value > Font: 24-28pt, color Navy #1a2744
   - Callout > Label: ON
     - Card 1 label: "Emergency - Total Response"
     - Card 2 label: "Urgent - Total Response"
     - Card 3 label: "Routine - Total Response"
   - Trend > Line color: Steel blue #4682B4
   - Category label: OFF
   - Background: White
   - Border: ON, Navy #1a2744, 1px, rounded 4px
   - Shadow: OFF

5. **Align:** Select all 3 > Format > Align > Distribute Horizontally, Align Top

**Verify:** Emergency ~5.0 min, Urgent ~5.5 min, Routine ~5.3 min (with sparklines)

---

### VISUAL 2: Line Chart with Small Multiples (center)

1. **Insert** > Visualizations > Line Chart
2. **Data wells:**
   - X-Axis: `MM-YY`
   - Y-Axis: `RT Avg Formatted` (or `Average_Response_Time`; use RT Avg Formatted for M:SS display)
   - Legend: `Metric_Label`
   - Small multiples: `Response_Type`
3. **X-Axis type:** Right-click axis label > select **Continuous**
4. **CRITICAL FILTER CHECK:**
   - Open Filters pane for this visual
   - **DELETE any filter on Response_Type** - Small Multiples handles separation
   - All 3 panels (Emergency, Urgent, Routine) MUST appear
5. **Format:**
   - Legend colors (click the colored dot next to each in Legend):
     - Total Response: Dark navy #0C233D
     - Travel Time: Steel blue #4682B4
     - Dispatch Queue: Light blue #87CEEB
   - Data labels > ON > Show: Last only > Apply to Total Response line only
   - Y-Axis:
     - Title: "Minutes"
     - Start value: 0
     - End value: Auto (or lock at 8 for consistency)
   - X-Axis: Title OFF
   - Small multiples:
     - Layout: 1 row x 3 columns
     - Title: ON (shows Emergency | Urgent | Routine)
     - Border: Light gray #E0E0E0
   - Title: "Response Time Trends by Priority"
   - Title font: 11pt, Navy #1a2744
   - Gridlines: Horizontal only, #F0F0F0
   - Background: White/transparent

**Verify:** 3 side-by-side panels, each with 3 lines. Total Response line is highest.

---

### VISUAL 3: Consolidated Detail Matrix (bottom)

1. **Insert** > Visualizations > Matrix
2. **Data wells:**
   - Rows (Level 1): `Response_Type`
   - Rows (Level 2): `Metric_Label`
   - Columns: `MM-YY`
   - Values: `Response_Time_MMSS`
3. **CRITICAL FILTER CHECK:**
   - Open Filters pane for this visual
   - **DELETE any filter on Response_Type** - all 3 types must show
   - Should display 9 data rows (3 types x 3 metrics)
4. **Format:**
   - Row subtotals: **OFF** (Format > Row headers > Subtotals > OFF)
   - Column subtotals: **OFF** (Format > Column headers > Subtotals > OFF)
   - Stepped layout: **ON** (Format > Row headers > Options > Stepped layout)
   - Font size: 9-10pt
   - Column headers: Background Navy #1a2744, Font white #FFFFFF
   - Alternating rows: Light #F8F8F8
   - Grid: Thin, #E0E0E0

5. **Conditional Formatting (traffic light):**
   - In the Values well, click the dropdown arrow on `Response_Time_MMSS`
   - Select **Conditional formatting** > **Background color**
   - Format style: **Field value**
   - What field should we base this on: `RT CF All Metrics Background`
   - Click OK
   - Repeat: dropdown > **Conditional formatting** > **Font color**
   - Field value: `RT CF All Metrics Font`

   NOTE: Use `RT CF All Metrics Background` / `RT CF All Metrics Font` (the NEW universal measures), NOT `RT CF Background Color` / `RT CF Font Color` (which only work for Total Response).

6. **Title:** "Response Time Detail (MM:SS)"
7. **Title font:** 11pt, Navy #1a2744

**Verify:**
- 3 top-level rows: Emergency, Urgent, Routine (sorted in that order)
- Under each: Dispatch Queue, Travel Time, Total Response
- 12 columns: 02-25 through 01-26 (13 after ETL run)
- Values in M:SS format (e.g., "5:02", "3:15")
- Green/Amber/Red backgrounds on all cells

---

## DFR SUMMONS VISUAL - Drone Page

### Prerequisites
- Close & Apply completed (loads data from Excel)
- If still 0 rows, check dates in `dfr_directed_patrol_enforcement.xlsx` fall within Feb 2025 - Feb 2026

### Available Measures
| Measure | Purpose | Format |
|---------|---------|--------|
| DFR Summons Count | Row count | #,0 |
| DFR Summons Total Fines | Sum of fines | $#,0.00 |
| DFR Summons Title | "DFR Directed Patrol Summons" | text |
| DFR Summons Subtitle | Dynamic count + latest month | text |

### Build Steps

1. Navigate to the **Drone** page
2. **Insert** > Table (recommended) or Matrix

**Detail Table layout:**
- Columns (drag in order):
  1. `Date`
  2. `Violation_Type`
  3. `Location`
  4. `Description`
  5. `Statute`
  6. `Fine_Amount`
  7. `Issuing_Officer`
  8. `DFR_Operator`

**Format:**
- Title: Bind to `DFR Summons Title` measure, or type "DFR Directed Patrol Summons"
- Column headers: Navy #1a2744 background, white text
- Alternating rows: #F5F5F5
- Font: 9pt Segoe UI
- Fine_Amount: Currency format
- Border: ON, Navy #1a2744, 1px

**Visual name for export mapping:** Set Alt Text > Title to `dfr_summons`

---

## OUT-REACH PAGE - Engagement Initiatives by Bureau

### What's Available
- Table: `___Combined_Outreach_All` (309 rows)
- Key columns: `Office`, `Event Name`, `Location of Event`, `Date`, `Event Duration (Hours)`, `Number of Police Department Attendees`, `Row_ID`
- Measures: `Engagement Title`, `Engagement Subtitle`, `Outreach Sessions`, `Outreach Total Hours`, `Outreach Total Attendees`

### Verify or Create

1. Navigate to the **Out-Reach** page
2. **If visual exists:** Click on it and verify these fields are bound:
   - Office (for bureau grouping)
   - Event Name, Date, Location
   - Duration, Attendees
   - Title uses `Engagement Title` measure
3. **If visual does NOT exist:** Insert a Table visual with:
   - `Row_ID` (hidden differentiator - set column width to ~0px)
   - `Date`
   - `Event Name`
   - `Location of Event`
   - `Office`
   - `Event Duration (Hours)`
   - `Number of Police Department Attendees`
   - Title: `Engagement Title`
   - Subtitle: `Engagement Subtitle`
   - Format: Navy headers, 9pt, alternating rows

NOTE: Currently all 309 rows show Office = "STA&CP" (single bureau contributing).

---

## SKIPPED ITEMS (Task 3)

- **Chief Michael Antista's Projects and Initiatives** - Blank for now, skip
- **Officer Summons Activity** - Does not exist; the 4 Summons visuals are: Department-Wide Summons, Summons Moving & Parking All Bureaus, Top 5 Parking, Top 5 Moving

---

## POST-BUILD CHECKLIST

### Functional Verification
- [ ] Response Time KPI cards show 3 values (Emergency ~5.0, Urgent ~5.5, Routine ~5.3 min)
- [ ] Response Time Line Chart has 3 Small Multiple panels with 3 lines each
- [ ] Response Time Matrix shows 9 rows (3 types x 3 metrics) with MM-YY columns
- [ ] Matrix conditional formatting shows green/amber/red across ALL rows (not just Total Response)
- [ ] No Response_Type filters on Line Chart or Matrix
- [ ] DFR Summons table populated after Close & Apply
- [ ] Out-Reach engagement visual bound correctly

### Export Mapping
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

### Full Refresh & Save
- [ ] Ctrl+Shift+F5 (full refresh)
- [ ] Ctrl+S (save .pbix)

---

## MEASURE REFERENCE (Complete RT Inventory)

| Measure | Purpose | Use In |
|---------|---------|--------|
| RT Trend Total Response | Decimal avg, Total Response only | KPI Card callout |
| RT Trend Travel Time | Decimal avg, Travel Time only | Optional cards |
| RT Trend Dispatch Queue | Decimal avg, Dispatch Queue only | Optional cards |
| RT KPI Current Month | Latest month Total Response | Card reference |
| RT KPI Prior Month Delta | MoM change (+slower/-faster) | Card delta |
| RT KPI Current Month MMSS | Latest month as M:SS string | Card display |
| RT Avg Total Response | AVERAGE filtered to Total Response | Line chart |
| RT Avg Travel Time | AVERAGE filtered to Travel Time | Line chart |
| RT Avg Dispatch Queue | AVERAGE filtered to Dispatch Queue | Line chart |
| RT CF All Metrics Background | Universal hex BG (all metrics) | Matrix CF |
| RT CF All Metrics Font | Universal hex font (all metrics) | Matrix CF |
| RT CF Background Color | BG for Total Response only | Legacy |
| RT CF Font Color | Font for Total Response only | Legacy |
| RT CF Display Value | M:SS string for Total Response | Legacy |
| RT Average Title | "Average Response Time (Dispatch to On Scene)" | Visual title |
| RT Average Subtitle | Description + rolling 13 months | Visual subtitle |
| RT OutVsCall Title | "Average Response Time (From Time Received to On Scene)" | Visual title |
| RT OutVsCall Subtitle | Description + rolling 13 months | Visual subtitle |
| RT DispVsCall Title | "Dispatch Processing Time (Call Received to Dispatch)" | Visual title |
| RT DispVsCall Subtitle | Description + rolling 13 months | Visual subtitle |

---

*Generated by Claude MCP | Master_Automation v1.18.10 | TODAY() cleanup complete (2026-03-17)*
