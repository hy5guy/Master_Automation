# Claude MCP Prompt: Fix Response Time Line Chart - Display Values as M:SS

**Purpose:** Pass this prompt to Claude Desktop with the Power BI MCP connected and the Response Time line chart visual selected. The goal is to change the Y-axis and data label values from decimal minutes (10.8, 12.8) to time format (10:48, 12:48) so they are readable at a glance.

**Prerequisites:**
1. Power BI Desktop open with the monthly report .pbix loaded
2. Claude Desktop with Power BI MCP connected
3. Connect to the open model
4. Response Time line chart exists (small multiples: Emergency, Routine, Urgent; Legend: Metric_Label; Y-axis currently shows decimal values)

---

## PROMPT START - Copy everything below this line

---

**Task:** Fix the Response Time line chart so the Y-axis and data labels display values in **minutes:seconds format** (e.g., "10:48" for 10.8 minutes, "12:48" for 12.8 minutes) instead of decimal base-10 (10.8, 12.8). The decimal format does not make sense at a glance for response time.

**Context:** The visual uses `___ResponseTime_AllMetrics`. The Y-axis/Values well currently has `Average_Response_Time` (decimal minutes) or `RT Avg Minutes` (0.0 "min" format). Both show values like 10.8, 12.8. We need M:SS format (10:48, 12:48).

**Approach:** Create or replace a measure that returns a value Power BI can format as time. Two options:

**Option 1 - Fraction of day (recommended):**  
Convert decimal minutes to fraction of day so Power BI time format applies:
```dax
RT Avg Formatted = 
VAR AvgMinutes = AVERAGE('___ResponseTime_AllMetrics'[Average_Response_Time])
RETURN AvgMinutes / 1440
```
- Set measure format string to **`m:ss`** or **`mm:ss`** (minutes:seconds)
- Replace the current Y-axis field with this measure
- The chart will plot correctly; axis and data labels will display as "5:18", "10:48", etc.

**Option 2 - TIME() function:**  
If Option 1 does not format correctly:
```dax
RT Avg Formatted = 
VAR AvgMinutes = AVERAGE('___ResponseTime_AllMetrics'[Average_Response_Time])
RETURN TIME(0, INT(AvgMinutes), ROUND((AvgMinutes - INT(AvgMinutes)) * 60, 0))
```
- Set measure format string to **`m:ss`** or **`mm:ss`**
- Use this measure in the Y-axis/Values well

**Steps (via MCP or manual):**
1. Create or edit the measure `RT Avg Formatted` on table `___ResponseTime_AllMetrics` with one of the DAX options above
2. Set the measure format string to `m:ss` (or `mm:ss` if needed for leading zero on minutes)
3. In the Response Time line chart: remove the current Y-axis/Values field (Average_Response_Time or RT Avg Minutes)
4. Add `RT Avg Formatted` to the Y-axis/Values well
5. Verify: data labels and Y-axis should show "5:18", "10:48", "12:48" instead of 5.3, 10.8, 12.8

**If the measure cannot be dragged to the Y-axis well:**
- Ensure the measure is created on `___ResponseTime_AllMetrics` (Table tools > New measure)
- The measure must return a numeric or datetime value (not text) for the line chart to accept it
- Try Option 1 (fraction of day) first - it returns a decimal that Power BI can format as time

**Verification:** Emergency Total Response ~5:18 to 6:31; Routine ~9:18 to 13:30; Urgent ~8:24 to 9:24. All values should display as M:SS.

---

## PROMPT END

---

*Created: 2026-03-17 | Master_Automation*
