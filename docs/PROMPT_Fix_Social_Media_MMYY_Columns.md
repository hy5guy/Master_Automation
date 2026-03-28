# Claude MCP Prompt: Fix Power BI Visuals in TEST_2026_02_Monthly_Report_TEST.pbix

---

## Quick Copy-Paste Prompt for Claude

```
Use the Power BI MCP (user-powerbi-modeling-mcp) to fix multiple visuals in the open TEST_2026_02_Monthly_Report_TEST.pbix file. pReportMonth = 2026-03-01.

Follow docs/PROMPT_Fix_Social_Media_MMYY_Columns.md for full instructions. Tasks:

1. ___Social_Media: Fix Missing_References; ensure M code produces Platform + MM-YY columns (02-25 … 02-26). Fallback to MoMTotals sheet if _stacp_mom_sm table missing.

2. ___Arrest_Categories: Fix blank "Arrest Categories by Type and Gender" visual. Query filters to previous month from pReportMonth; verify source file path and that latest PowerBI_Ready file contains Feb 2026 data. Path: C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\ARREST_DATA\Power_BI

3. ___Combined_Outreach_All: Investigate why the visual on Out-Reach page is blank. Check source path (Community_Engagement\output\), ETL output files, and query logic.

4. Detectives Case Dispositions: Investigate why visuals are missing 02-25 and have extra 03-26. Query: ___Det_case_dispositions_clearance. Source: detectives_monthly.xlsx, table _CCD_MOM. Fix 13-month window logic.

5. Training Cost by Delivery: Investigate why visual is missing 02-25 and 02-26. Query: ___Cost_of_Training. Source: policy_training_outputs.xlsx, sheet Delivery_Cost_By_Month. Fix 13-month window logic.

Connect via connection_operations (ListLocalInstances, then Connect). Use partition_operations to Get/Update each query. Sync fixes to m_code/ in Master_Automation repo.
```

---

## Full Instructions

**Context:** The `___Social_Media` query in `TEST_2026_02_Monthly_Report_TEST.pbix` has:
- **Underlying Error:** Missing_References
- **Issue:** The M code does not produce the MM-YY columns (02-25, 03-25, … 02-26) that the visual expects. The Fields pane shows these columns with yellow warning icons.

**Goal:** Use the Power BI MCP to connect to the open .pbix file, inspect the ___Social_Media query, and fix the M code so it returns a table with:
- **Platform** (text)
- **MM-YY columns** for the rolling 13-month window (e.g. 02-25, 03-25, …, 02-26 for pReportMonth = 2026-03-01)
- **Total** (if present in source)

---

## Step 1: Connect to Power BI Desktop

1. Ensure **Power BI Desktop** has `C:\_Sandbox\TEST_2026_02_Monthly_Report_TEST.pbix` **open**.
2. Call `connection_operations` with `operation: "ListLocalInstances"` to find the Power BI instance.
3. Call `connection_operations` with `operation: "Connect"` and `connectionString` from the ListLocalInstances result (e.g. `"Data Source=localhost:63310;Application Name=MCP-PBIModeling"`).

---

## Step 2: Inspect Current ___Social_Media Query

1. Call `partition_operations` with `operation: "Get"` and `references: [{"tableName": "___Social_Media"}]`.
2. Review the current M expression. Identify:
   - Whether it loads from `_stacp_mom_sm` (Kind="Table") or `MoMTotals` (Kind="Sheet")
   - What column names the source actually has (the STACP.xlsm workbook may use "3-25" vs "03-25", or different naming)
   - Why the MM-YY columns are missing (e.g. `MissingField.Ignore` dropping non-matching columns, or source has different names)

---

## Step 3: Fix the M Code

The fix must:

1. **Load the source** – Try `_stacp_mom_sm` (Kind="Table") first; if that fails (Missing_References), fall back to `MoMTotals` (Kind="Sheet") with `Table.PromoteHeaders`.

2. **Handle column name variations** – The source may use:
   - `"3-25"` or `"03-25"` (single vs double-digit month)
   - Different formats – normalize to `"MM-yy"` (e.g. `"03-25"`)

3. **Build the 13-month window** – For `pReportMonth = 2026-03-01`:
   - End of window = last complete month = Feb 2026 (02-26)
   - Start of window = 12 months before = Feb 2025 (02-25)
   - Target columns: `02-25`, `03-25`, …, `01-26`, `02-26`

4. **Map source columns to MM-yy** – If the source has `"3-25"`, map it to `"03-25"`. Use logic like:
   ```
   NormalizeMMYY = (col) => 
     let Parts = Text.Split(col, "-"),
         M = Text.PadStart(Parts{0}, 2, "0"),
         Y = Parts{1}
     in M & "-" & Y
   ```
   Then select/rename columns so the output has exactly: Platform, 02-25, 03-25, …, 02-26, Total.

5. **Ensure output schema** – The final table must have:
   - First column: **Platform** (text)
   - Next 13 columns: **02-25** through **02-26** (or the correct window for pReportMonth)
   - Optional: **Total** column

---

## Step 4: Update the Partition

1. Call `partition_operations` with `operation: "Update"` and `definitions` containing the corrected M expression for `___Social_Media`.
2. Optionally call `partition_operations` with `operation: "Refresh"` and `refreshDefinitions: [{"tableName": "___Social_Media"}]` to test (note: model commit may fail if other tables are broken; the partition update itself may still succeed).

---

## Reference: Source File Path

```
C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\STACP\STACP.xlsm
```

- **___STACP_pt_1_2** uses: `Source{[Item="MoMTotals", Kind="Sheet"]}[Data]` – this works.
- **___Social_Media** previously used: `Source{[Item="_stacp_mom_sm", Kind="Table"]}[Data]` – this causes Missing_References (table may not exist).

---

## Suggested M Code Structure (Template)

```powerquery
let
    ReportMonth = pReportMonth,
    Source = Excel.Workbook(
        File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\STACP\STACP.xlsm"),
        null,
        true
    ),
    RawData = try Source{[Item="_stacp_mom_sm", Kind="Table"]}[Data]
        otherwise Source{[Item="MoMTotals", Kind="Sheet"]}[Data],
    Promoted = Table.PromoteHeaders(RawData, [PromoteAllScalars=true]),
    // Normalize month column names: "3-25" -> "03-25", "03-25" -> "03-25"
    Cols = Table.ColumnNames(Promoted),
    RenameMap = List.Transform(Cols, each 
        let Parts = Text.Split(_, "-")
        in {_, Text.PadStart(Parts{0}, 2, "0") & "-" & (if List.Count(Parts) >= 2 then Parts{1} else "25")}
    ),
    Normalized = Table.RenameColumns(Promoted, List.Select(RenameMap, each _{0} <> _{1})),
    // ... rest: filter to Platform + 13 month columns, apply types, select final columns
in
    FinalTable
```

---

## Additional Fixes

### ___Arrest_Categories (Arrest Categories by Type and Gender – blank)

**Query:** `___Arrest_Categories`  
**Visual:** Arrest Categories by Type and Gender  
**Source:** `C:\Users\carucci_r\OneDrive - City of Hackensack\01_DataSources\ARREST_DATA\Power_BI` (latest `*PowerBI_Ready*.xlsx`)

**Logic:** Filters to **previous month** from pReportMonth. For pReportMonth = 2026-03-01, it looks for **February 2026** arrests.

**Investigate:**
- Does the latest PowerBI_Ready file contain February 2026 data?
- Is the file named `2026_02_Arrests_PowerBI_Ready.xlsx`?
- Does the query load the correct file (sorted by Date modified, descending)?
- If December 2025 or another month is missing, the Arrests ETL may need to be run for that month.

**Fix:** Ensure pReportMonth aligns with available data, or run Arrests ETL to generate the missing month’s PowerBI_Ready file.

---

### ___Combined_Outreach_All (Out-Reach page – blank)

**Query:** `___Combined_Outreach_All`  
**Visual:** On Out-Reach page; "Engagement Initiatives by Bureau"  
**Source:** `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Community_Engagement\output\`  
**Pattern:** `community_engagement_data_*.csv`

**ETL config (2026-03-11):** STACP sheet = `School_Outreach` (not `_25_outreach`). Config paths use `carucci_r` base (desktop); laptop uses `RobertCarucci`.

**M code:** Includes Event ID and Row_ID so each event displays as an individual row. Add Row_ID to visual's Rows well to prevent aggregation.

**Investigate:**
- Do any `community_engagement_data_*.csv` files exist in that folder?
- Is the path correct? (Note: folder is `Community_Engagement` – typo in name)
- Has the Community Engagement ETL been run recently?
- Does the query’s dynamic file discovery find a file, or does it error/return empty?
- Check column names: `date`, `duration_hours`, `event_name`, `location`, `attendee_count`, `office`, `Event ID`, `Row_ID`

**Fix:** Run Community Engagement ETL if needed; verify output path in `config/scripts.json`; ensure query handles empty/missing files gracefully.

---

### Detectives Case Dispositions (missing 02-25, has extra 03-26)

**Query:** `___Det_case_dispositions_clearance`  
**Visual:** Detectives Case Dispositions  
**Source:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Detectives\detectives_monthly.xlsx`  
**Table:** `_CCD_MOM`

**Expected window (pReportMonth = 2026-03-01):** 02-25 through 02-26 (13 months: Feb 2025 – Feb 2026)

**Investigate:**
- What month columns does the _CCD_MOM table actually have? (Comment in M code says "01-26 through 12-26 only" – may lack 2025 columns)
- Is the 13-month window logic excluding 02-25 or including 03-26 incorrectly?
- Compare window calculation: EndMonth = previous month vs. report month. For "Feb 2025 – Feb 2026", window should **include** report month (Feb 2026).

**Fix:** Adjust window logic so it produces 02-25 through 02-26. If source lacks 02-25, the Excel workbook may need to be updated to include that column.

---

### Training Cost by Delivery (missing 02-25 and 02-26)

**Query:** `___Cost_of_Training`  
**Visual:** Training Cost by Delivery Method  
**Source:** `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Policy_Training_Monthly\output\policy_training_outputs.xlsx`  
**Sheet:** `Delivery_Cost_By_Month`

**Expected window (pReportMonth = 2026-03-01):** 02-25 through 02-26 (13 months)

**Current logic:** EndMonth = previous month (Feb 2026), StartYear = EndYear - 1 → Feb 2025 – Feb 2026. That should include 02-25 and 02-26.

**Investigate:**
- What month columns does the Delivery_Cost_By_Month sheet actually have?
- Does the source use "2-25" vs "02-25" (single vs double-digit month)?
- Is the PeriodLabelsMMYY filter dropping 02-25/02-26 due to format mismatch?
- Is the Policy Training ETL output missing those months?

**Fix:** Normalize column names (e.g. "2-25" → "02-25"); ensure source workbook has 02-25 and 02-26 columns; verify window filter uses correct format.

---

## Deliverables

1. **___Social_Media:** Fixed M expression with Platform + MM-YY columns; updated [m_code/social_media/___Social_Media.m](m_code/social_media/___Social_Media.m).
2. **___Arrest_Categories:** Diagnosis and fix (or ETL run instructions) for blank visual; update [m_code/arrests/___Arrest_Categories.m](m_code/arrests/___Arrest_Categories.m) if needed.
3. **___Combined_Outreach_All:** Diagnosis and fix for blank Out-Reach visual; update [m_code/community/___Combined_Outreach_All.m](m_code/community/___Combined_Outreach_All.m) if needed.
4. **___Det_case_dispositions_clearance:** Fixed window logic; updated [m_code/detectives/___Det_case_dispositions_clearance.m](m_code/detectives/___Det_case_dispositions_clearance.m).
5. **___Cost_of_Training:** Fixed window/column logic; updated [m_code/training/___Cost_of_Training.m](m_code/training/___Cost_of_Training.m).
6. **Summary:** Brief report of root causes and changes for each visual.
