# Claude-Optimized Prompt: Response Time M Code Fix

**Domain Classification**: `powerbi_m_dax` + `response_time_kpi`  
**Created**: February 9, 2026  
**Based On**: Actual resolved issue - Response Time Calculator M Code

---

## Section A: Optimized Prompt

### Optimized Prompt for Claude

```xml
<role>
Senior Power BI M code specialist with expertise in CAD/RMS response time KPI analysis. 
Deep knowledge of: Power Query type system, CSV auto-typing behavior, mixed format data handling, 
locale-safe conversions, municipal police response time SLA tracking.
</role>

<context>
Municipal police department Power BI dashboard showing response time KPIs for command staff.
Data pipeline: CAD timereport exports → Python ETL (monthly aggregation) → Power BI M query → Dashboard visuals.
Current blocker: M code query failing with type conversion errors preventing dashboard refresh.
System: Windows 10, Power BI Desktop, OneDrive-synced workspace.
Timezone: EST (all timestamps).
</context>

<inputs>
**Source Files**:
- Location: `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\outputs\visual_exports\`
- Files: `YYYY_MM_DD_HH_MM_SS_Average Response Times  Values are in mmss.csv`
- Structure discovered:
  ```csv
  Response Type,MM-YY,First Response_Time_MMSS
  Emergency,12-24,2:39
  Emergency,01-25,2:58
  Routine,01-25,1.3
  Urgent,01-25,2.5
  ```

**CSV Characteristics**:
- Power Query loads with `PromoteAllScalars = true`
- Auto-typing causes mixed types in Response_Time_MMSS column:
  * "2:39" → typed as Time or Text
  * 1.3 → typed as Number
  * "1.3" → typed as Text
- Column names: "Response Type" (space), "First Response_Time_MMSS", "MM-YY"

**Current M Query Issues**:
1. DataSource.NotFound: Hardcoded paths to `C:\Dev\PowerBI_Date\...` (old location)
2. Type conversion errors: "Cannot convert value '1.3' to type Number"
3. Duplicate column errors: "Field 'Response_Type' already exists"
4. Missing field errors: "Field 'MM-YY' not found"
5. Response_Time_MMSS: 31% errors
6. Average_Response_Time: 69% empty values
7. YearMonth: 60% errors

**Expected M Query Structure** (was using):
- Hardcoded file paths (broken)
- Assumed Text type in all cells
- No type checking before conversion
- Attempted to load from old Backfill structure
</context>

<deliverables>
1. **Production M code query** (`___ResponseTimeCalculator`) with:
   - Dynamic file discovery from visual_exports folder
   - Type-agnostic handling (Value.Is checks before conversion)
   - Mixed format support (MM:SS, M:SS, HH:MM:SS, decimal minutes)
   - Locale-safe conversion (en-US for all Text.From and Number.From)
   - Forced Average_Response_Time recalculation for accuracy
   - Complete inline documentation

2. **Data transformations** that produce:
   - Response_Time_MMSS: Standardized MM:SS format (e.g., "02:39")
   - Average_Response_Time: Decimal minutes (e.g., 2.65)
   - YearMonth: YYYY-MM format (e.g., "2025-01")
   - Date_Sort_Key: Date type for chronological sorting
   - Summary_Type, Category, Date: DAX-compatible columns

3. **Format conversion table** showing:
   - Input → Type detected → Processing logic → Output (MM:SS and decimal)
   - Cover: "2:39", "02:39", "1.3", 1.3, "02:40:00", null, invalid

4. **Implementation guide** with:
   - Step-by-step Power Query Editor instructions
   - Verification checklist (column quality checks)
   - Expected row count (~30-50 rows)
   - Rollback procedure

5. **Code header** (at top of M query):
   ```m
   // 🕒 2026-02-09 (EST)
   // Master_Automation/m_code/___ResponseTimeCalculator.m
   // Author: R. A. Carucci (AI-assisted: Claude + Gemini)
   // Purpose: Dynamic response time aggregation loader with type-agnostic mixed format handling
   // Version: 2.7.1 (Production Final)
   ```
</deliverables>

<constraints>
**Technical**:
- Must work with Power Query's auto-typing (PromoteAllScalars = true)
- Zero type conversion errors required
- Handle Number, Time, and Text types in same column
- Support HH:MM:SS time format (take first two segments as MM:SS)
- Locale-independent (en-US for all conversions)
- File size filter: <50KB (exclude raw incident data, keep aggregated summaries)

**Data Quality**:
- 100% valid data required (0% errors in all columns)
- Response times: 0-15 minutes typical range
- Response types: Emergency, Routine, Urgent (standardized)
- Date range: Rolling 13-month window (or available months)

**Performance**:
- Query refresh: <10 seconds for 30-50 rows
- Memory usage: <50 MB
- No query folding issues

**Naming Conventions**:
- Columns: Use underscores (Response_Type, not "Response Type")
- Files: Match pattern `YYYY_MM_*_Average Response Times*.csv`
- Output columns: YearMonth, Date_Sort_Key, Date, Response_Type, Summary_Type, Category, 
  Average_Response_Time, Response_Time_MMSS, MM-YY

**Compatibility**:
- Must work with both aggregated formats:
  * Long format: One row per month per priority (Response_Type column)
  * Wide format: One row per month (Emergency Avg, Routine Avg, Urgent Avg columns)
- Skip raw incident data files (have ReportNumberNew, Time of Call columns)
</constraints>

<quality_checks>
**Pre-Implementation**:
- [ ] Backup existing query (duplicate)
- [ ] Verify source CSV files exist in visual_exports
- [ ] Check sample CSV structure matches expected format
- [ ] Note current error percentages for comparison

**Post-Implementation**:
- [ ] Power Query preview loads without errors
- [ ] Column quality indicators:
  * Response_Time_MMSS: 100% Valid (green), 0% Error
  * Average_Response_Time: 100% Valid (green), 0% Empty
  * YearMonth: 100% Valid (green), 0% Error
- [ ] Row count: 30-50 rows (not thousands - indicates aggregated data loading)
- [ ] Sample data verification:
  * Response_Time_MMSS: All in MM:SS format ("02:39" not "2:39" or "1.3")
  * Average_Response_Time: All decimals (2.65, 1.30, 2.50)
  * YearMonth: All YYYY-MM format ("2025-01" not "01-25")
- [ ] Report visuals display correctly
- [ ] No performance degradation (<10 second refresh)
- [ ] Distinct values check:
  * List.Distinct(___ResponseTimeCalculator[Response_Type]) = ["Emergency", "Routine", "Urgent"]
  * List.Count(List.Distinct(___ResponseTimeCalculator[YearMonth])) = 10-17 months

**Exception Handling Verification**:
- [ ] Test with null values (should default to "00:00", 0.00)
- [ ] Test with invalid values (should fallback to "00:00", 0.00)
- [ ] Test with decimal numbers typed as Number (should convert correctly)
- [ ] Test with time strings (should pad and parse correctly)
</quality_checks>

<assumptions>
- Power Query auto-types CSV columns during load (PromoteAllScalars = true)
- Mixed types exist in Response_Time_MMSS column (Number, Time, Text)
- Files in visual_exports are aggregated monthly summaries (not raw incidents)
- Source files are <50KB each (aggregated, not raw data)
- Rolling window: 10-17 months of data available
- Response priorities: Emergency, Routine, Urgent (standard CAD priorities)
- Timezone: All dates/times in EST
- OneDrive sync: Files locally available (not cloud-only)
- No Backfill structure files exist yet (ETL hasn't generated monthly folders)
</assumptions>

<questions>
None - all blockers resolved through iterative testing. CSV structure confirmed via sample data.
</questions>

<output_format>
**M Code File**:
- Filename: `___ResponseTimeCalculator.m`
- Header format:
  ```m
  // 🕒 2026-02-09 (EST)
  // Master_Automation/m_code/___ResponseTimeCalculator.m
  // Author: R. A. Carucci (AI-assisted: Claude + Gemini)
  // Purpose: Dynamic response time aggregation loader with type-agnostic mixed format handling
  // Version: 2.7.1 (Production Final)
  ```
- Structure: Complete let...in statement ready for Advanced Editor
- Inline comments: Every major transformation step explained
- Total lines: ~330 lines

**Documentation**:
- Implementation guide (markdown)
- Test cases table (markdown table)
- Before/after comparison (markdown table)
- Version history summary

**Artifacts**:
- Primary: Working M code query
- Secondary: Implementation checklist
- Tertiary: Troubleshooting guide
</output_format>
```

---

## Section B: Change Log

### Transformations Applied

**Added**:
- Explicit CSV structure with sample data (Response Type, MM-YY, First Response_Time_MMSS)
- Type auto-detection context (PromoteAllScalars behavior)
- Mixed type specification (Number, Time, Text in same column)
- All 7 discovered error conditions with percentages
- File size constraint (<50KB to exclude raw data)
- Rolling window specification (10-17 months)
- Locale requirement (en-US mandatory)
- Complete quality check list (pre and post implementation)
- Exception handling verification steps
- Row count expectation (30-50 rows for aggregated data)

**Clarified**:
- Data source: visual_exports folder (not Backfill structure)
- Column naming: "First Response_Time_MMSS" → needs rename to "Response_Time_MMSS"
- Format variations: Three types (MM:SS, decimal Number, decimal Text)
- Auto-typing issue: Root cause of type conversion errors
- Aggregated vs raw: Must load aggregated only (size filter)
- Priority types: Emergency, Routine, Urgent (CAD standard)
- Response time range: 0-15 minutes typical (SLA context)

**Assumed**:
- Windows environment with Power BI Desktop
- OneDrive sync operational (files locally available)
- EST timezone for all temporal data
- No Backfill monthly folders exist yet (explained why visual_exports used)
- CAD export structure follows municipal standard
- Rolling 13-month window requirement (actual: 10-17 months available)
- Power Query PromoteAllScalars = true (standard CSV import)

**Removed**:
- Vague "fix the error" language
- Generic Power BI references
- Assumed prior knowledge of issue history

**Structured**:
- Separated technical constraints, data quality, performance, naming, compatibility
- Organized quality checks into pre/post with specific verification steps
- Created clear deliverables list (5 concrete outputs)
- Added exception handling verification (null, invalid, mixed types)

**Compliance Notes**:
- No PII in response time aggregated data (monthly averages only)
- No redaction required for this data type
- Command staff audience (internal use)

---

## Usage Instructions

**To Use This Prompt**:
1. Copy entire `<optimized_prompt>` section
2. Provide to Claude in new conversation
3. Claude will generate production-ready M code solution
4. Follow implementation guide provided in deliverables

**Expected Claude Output**:
- Complete M code with type-agnostic handling
- Value.Is() pattern for mixed types
- Locale-safe conversions (en-US)
- Format conversion logic (MM:SS, decimal, HH:MM:SS)
- Implementation checklist
- Test cases table
- Verification steps

**Success Metrics**:
- 100% data quality (0% errors)
- All format variations handled
- Type-safe conversions
- Production-ready code

---

*Prompt Engineering Template Demonstration*  
*Framework: Law Enforcement Data Systems*  
*Domain: powerbi_m_dax + response_time_kpi*
