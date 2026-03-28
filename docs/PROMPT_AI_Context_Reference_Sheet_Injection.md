# Prompt: AI_Context_Reference Sheet Injection for HPD Shared Workbooks

## Role and Objective

You are an Expert Data Architect and Senior Python Automation Engineer working on the **Hackensack Police Department (HPD) Compstat Power BI & ETL Infrastructure**. Your task is to programmatically analyze and enhance the shared Excel workbooks (`.xlsx` and `.xlsm`) that serve as data entry points and ETL sources for the department's Power BI reporting pipeline.

For **every workbook in the target directory**, analyze its structure, business logic, and ETL relationships, then programmatically append a new, formatted worksheet named **`AI_Context_Reference`**. This sheet serves two purposes:
1. A machine-readable context layer for **Claude in Excel** sessions (AI-assisted data entry, formula building, and validation).
2. A human-readable reference dashboard for analysts maintaining the ETL pipeline.

---

## Target Directory & Workbook Inventory

**Base Path (OneDrive):**
```
C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\
```

### Primary Shared Workbooks (Tier 1 — Staff Data Entry)

| # | Workbook | Format | Subfolder | Purpose |
|---|----------|--------|-----------|---------|
| 1 | `csb_monthly.xlsm` | .xlsm | `CSB\` | Crime Suppression Bureau monthly metrics |
| 2 | `STACP.xlsm` | .xlsm | `STACP\` | Strategic Tackling Armed Crime Plan data |
| 3 | `patrol_monthly.xlsm` | .xlsm | `Patrol\` | Patrol Division monthly activity metrics |
| 4 | `Policy_Training_Monthly.xlsx` | .xlsx | `Policy_Training\` | Training course attendance and cost tracking |
| 5 | `detectives_monthly.xlsx` | .xlsx | `Detectives\` | Detective case dispositions and clearance rates |
| 6 | `ESU.xlsx` | .xlsx | `ESU\` | Emergency Services Unit monthly activity |
| 7 | `Traffic_Monthly.xlsx` | .xlsx | `Traffic\` | Traffic Bureau enforcement and citations |
| 8 | `chief_monthly.xlsx` | .xlsx | `Chief\` | Chief's Projects and Initiatives tracking |
| 9 | `Drone_Monthly.xlsx` | .xlsx | `Contributions\` (root) | Drone operations metrics (DFR vs Non-DFR) |
| 10 | `dfr_directed_patrol_enforcement.xlsx` | .xlsx | `Drone\` | DFR Summons Log (Claude in Excel workbook; ETL-fed via `dfr_export.py`) |

### Secondary Workbooks (Tier 2 — ETL Output / Reference)

Also inject `AI_Context_Reference` into these if accessible:

| # | Workbook | Location | Purpose |
|---|----------|----------|---------|
| 11 | `policy_training_outputs.xlsx` | `02_ETL_Scripts\Policy_Training_Monthly\output\` | Aggregated training delivery costs (ETL output) |
| 12 | `Assignment_Master_V3_FINAL.xlsx` | `09_Reference\Personnel\` | Personnel roster — 25 columns, 166 records |
| 13 | `NIBRS_Monthly_Report.xlsx` | `01_DataSources\NIBRS\` | NIBRS monthly incident classification |
| 14 | `_SSOCC - Service Log.xlsx` | `KB_Shared\04_output\ssocc_claude_in_excel_rework\` | SSOCC dispatch and alert data |

---

## Scope of Analysis per Workbook

Before writing to a workbook, extract and synthesize the following metadata:

### 1. Workbook Structure & Navigation
- List **all sheets** — differentiate between visible, hidden, and very hidden.
- Identify all **structured Excel Tables** (`ListObjects`) with their names, the sheets they reside on, and their row/column counts.
- Note any **named ranges** (especially those used by Data Validation or formulas).
- Flag any **password-protected** sheets (document but do not attempt to unlock).

### 2. Data Dictionary & Types
For all primary data tables, extract:
- **Column names** (preserve exact casing and spacing, including non-breaking spaces `\xa0`).
- **Inferred data type** per column: Date, Time, Text, Integer, Decimal, Currency, Formula/Calculated, Boolean.
- **Auto-generated ID patterns** (e.g., `CE20250101-0002` in Community Engagement, Summons Numbers like `H-2025-000001`).
- **Month-column naming conventions** used in this specific workbook:
  - `MM-YY` format (e.g., `01-24`, `02-24`) — used by CSB, Traffic, Patrol, STACP
  - `_YY_MMM` format (e.g., `_25_JAN`, `_25_FEB`) — used by ESU tables
  - Standard date columns (e.g., `Start date`, `Date`) — used by Training, DFR, Chief

### 3. Data Validation, Lists & Lookups
- Identify cells/columns governed by **Data Validation** (dropdown lists, date constraints, number ranges).
- **Map each dropdown** to its source: in-sheet list, named range, another sheet (e.g., `List` sheet, `ViolationData` sheet), or external reference.
- Identify key **lookup formulas** (`XLOOKUP`, `VLOOKUP`, `INDEX/MATCH`) and document:
  - The lookup column (key).
  - The return column(s).
  - The reference table/range.
- Note **conditional formatting** rules that encode business logic (e.g., red if overdue, green if complete).

### 4. ETL & Power Query Context

Cross-reference with the repository's configuration files to populate this section:

**Config files to read programmatically:**
- `Master_Automation/config/scripts.json` — ETL script registry (names, paths, enabled status, output patterns)
- `Master_Automation/Standards/config/powerbi_visuals/visual_export_mapping.json` — Visual export routing (40+ mappings with 13-month enforcement flags)
- `Master_Automation/config.json` — PowerBI data root folder

**For each workbook, document:**

| Field | Description |
|-------|-------------|
| **Consuming M Code Query** | Which Power Query (M) file loads this workbook (e.g., `m_code/csb/___CSB_Monthly.m`) |
| **M Code Source Pattern** | How the M code references this workbook (`Excel.Workbook(File.Contents(...))` with exact path) |
| **Sheet/Table Target in M** | Which sheet or table name the M code extracts (e.g., `MoM` sheet, `DFR_Summons` table) |
| **Python ETL Script** | Which Python script processes this workbook (e.g., `scripts/dfr_export.py`) |
| **Downstream CSV Outputs** | What CSV files are generated from this workbook's data |
| **Power BI Page(s)** | Which Power BI report page(s) display data from this workbook |
| **13-Month Window** | Whether this data uses a rolling 13-month window (yes/no, with `pReportMonth` reference) |
| **pReportMonth Pattern** | The standard window calculation: `EndOfWindow = Date.EndOfMonth(pReportMonth)`, `StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12))` |

**Known M Code → Workbook Mappings (use as lookup):**

| M Code File | Source Workbook | Sheet/Table Target |
|-------------|----------------|--------------------|
| `m_code/csb/___CSB_Monthly.m` | `csb_monthly.xlsm` | `MoM` sheet |
| `m_code/stacp/___STACP_pt_1_2.m` | `STACP.xlsm` | Multiple sheets (month columns MM-YY) |
| `m_code/patrol/___Patrol.m` | `patrol_monthly.xlsm` | `_mom_patrol` table |
| `m_code/training/___In_Person_Training.m` | `policy_training_outputs.xlsx` | `InPerson_Prior_Month_List` sheet |
| `m_code/training/___Cost_of_Training.m` | `policy_training_outputs.xlsx` | `Delivery_Cost_By_Month` sheet |
| `m_code/detectives/___Detectives.m` | `detectives_monthly.xlsx` | Case data tables |
| `m_code/detectives/___Det_case_dispositions_clearance.m` | `detectives_monthly.xlsx` | Disposition tables |
| `m_code/esu/ESU_13Month.m` | `ESU.xlsx` | `_YY_MMM` named tables + `_mom_hacsoc` dimension |
| `m_code/traffic/___Traffic.m` | `Traffic_Monthly.xlsx` | `_mom_traffic` table |
| `m_code/chief/___Chief2.m` | `chief_monthly.xlsx` | `Table8` (events) |
| `m_code/chief/___chief_projects.m` | `chief_monthly.xlsx` | Projects table |
| `m_code/drone/___Drone.m` | `Drone_Monthly.xlsx` | `DFR Activity` sheet, Non-DFR sheet |
| `m_code/drone/DFR_Summons.m` | `dfr_directed_patrol_enforcement.xlsx` | `DFR_Summons` table (fallback: `DFR Summons Log` sheet) |
| `m_code/nibrs/___NIBRS_Monthly_Report.m` | `NIBRS_Monthly_Report.xlsx` | NIBRS data tables |
| `m_code/ssocc/___SSOCC_Data.m` | `_SSOCC - Service Log.xlsx` | Service log tables |

### 5. VBA & Automation (Critical for .xlsm files)
For macro-enabled workbooks (`csb_monthly.xlsm`, `STACP.xlsm`, `patrol_monthly.xlsm`):
- **List all VBA modules** (Standard, Class, UserForm) and their names.
- **Summarize macro functionality** (e.g., automated data import, formatting, PDF generation, sheet protection toggle).
- **Document sheet-level event code** (e.g., `Worksheet_Change`, `Worksheet_Activate` triggers).
- **Note any `ThisWorkbook` events** (e.g., `Workbook_Open`, `Workbook_BeforeSave`).
- **Flag VBA references** to external libraries or data connections.

### 6. Claude in Excel Context
For workbooks that are actively developed or maintained via Claude in Excel:
- Note any existing **Claude-generated formulas** or **Claude Log** sheets.
- Document **formula patterns** Claude should follow when extending this workbook (e.g., `XLOOKUP` for fee schedules, `TEXT(date,"MM-YY")` for month keys).
- Include a **"Quick Start for Claude"** block: what to know before editing this workbook, common pitfalls, protected ranges.

---

## Execution Instructions

### Technology Stack
- Use **`openpyxl`** for `.xlsx` files.
- For `.xlsm` files, use **`openpyxl` with `keep_vba=True`** to safely preserve VBA projects.
- Use **`json`** module to read `config/scripts.json` and `visual_export_mapping.json` for cross-referencing.
- If running on Windows with Excel available, optionally use **`xlwings`** for richer VBA inspection.

### Path Resolution
```python
import os

# Primary: OneDrive base path
ONEDRIVE_ROOT = os.path.expanduser(
    r"~\OneDrive - City of Hackensack"
)
# Contributions directory (Tier 1 workbooks)
CONTRIBUTIONS_DIR = os.path.join(
    ONEDRIVE_ROOT, "Shared Folder", "Compstat", "Contributions"
)
# Master_Automation repo root (for config files)
REPO_ROOT = os.path.join(ONEDRIVE_ROOT, "Master_Automation")
```

### Error Handling
- **Password-protected workbooks**: Log and skip; note in terminal summary.
- **Missing workbooks**: Log path not found; continue to next.
- **Corrupt or unreadable files**: Catch `openpyxl` exceptions; log and skip.
- **Existing `AI_Context_Reference` sheet**: Delete and recreate (this is the one sheet we own).
- **VBA inspection failures** on `.xlsm`: Fall back to noting "VBA present but inspection requires xlwings/COM".

---

## Output Format: AI_Context_Reference Sheet Layout

Create a worksheet named **`AI_Context_Reference`** with the following structured sections. Use a **two-column layout** (Label | Value) for metadata, and **tabular layouts** for directories and dictionaries.

### Sheet Structure

```
Row 1:  [TITLE]  "{Workbook Name} — AI & ETL Context Architecture"
Row 2:  [Subtitle] "Generated: {timestamp} | Hackensack PD Compstat Pipeline"
Row 3:  (blank separator)

=== SECTION 1: OVERVIEW ===
Row 4:  Section Header: "1. OVERVIEW"
Row 5:  "Purpose" | "{auto-detected or mapped purpose from inventory}"
Row 6:  "File Format" | ".xlsx / .xlsm (macro-enabled)"
Row 7:  "Pipeline Role" | "Tier 1 — Staff Data Entry → Power BI via M Code"
Row 8:  "OneDrive Path" | "{full path}"
Row 9:  "Consuming M Code" | "{m_code file path(s)}"
Row 10: "Python ETL" | "{script name(s) or 'None — direct Power Query load'}"
Row 11: "Power BI Page(s)" | "{page name(s)}"
Row 12: "13-Month Window" | "Yes — pReportMonth driven | Standard pattern"
Row 13: (blank separator)

=== SECTION 2: SHEET & TABLE DIRECTORY ===
Row 14: Section Header: "2. SHEET & TABLE DIRECTORY"
Row 15: Column Headers: "Sheet Name" | "Visibility" | "Table Name(s)" | "Row Count" | "Column Count" | "Notes"
Row 16+: One row per sheet

=== SECTION 3: DATA DICTIONARY ===
Row N:  Section Header: "3. DATA DICTIONARY & VALIDATION"
Row N+1: Column Headers: "Column Name" | "Data Type" | "Sample Value" | "Validation/Dropdown" | "Dropdown Source" | "Formula Dependencies" | "Notes"
Row N+2+: One row per column (for each primary table)

=== SECTION 4: ETL & INTEGRATION MAP ===
Row M:  Section Header: "4. ETL & INTEGRATION MAP"
Row M+1: "M Code Query" | "{query name and file path}"
Row M+2: "M Code Source Pattern" | "Excel.Workbook(File.Contents(\"{path}\"), null, true)"
Row M+3: "Target Sheet/Table" | "{what M code extracts}"
Row M+4: "Month Column Format" | "MM-YY / _YY_MMM / Date column"
Row M+5: "Rolling Window" | "pReportMonth → EndOfMonth(pReportMonth) back 12 months"
Row M+6: "Python ETL Script" | "{script path and version}"
Row M+7: "Output CSV Pattern" | "{output file patterns}"
Row M+8: "Downstream Power BI Visuals" | "{visual names from visual_export_mapping.json}"
Row M+9: "ETL Rules" | "{specific rules: 13-month enforcement, zero-padded badges, court ID constants, etc.}"

=== SECTION 5: VBA & MACROS (if .xlsm) ===
Row P:  Section Header: "5. VBA & MACROS"
Row P+1: Column Headers: "Module Name" | "Type" | "Purpose" | "Triggers"
Row P+2+: One row per VBA module

=== SECTION 6: CLAUDE IN EXCEL QUICK START ===
Row Q:  Section Header: "6. CLAUDE IN EXCEL — QUICK START"
Row Q+1: "Workbook Purpose" | "{one-line summary}"
Row Q+2: "Key Tables" | "{table names and what they contain}"
Row Q+3: "Month Key Format" | "{how months are encoded in this workbook}"
Row Q+4: "Common Formulas" | "{patterns to follow: XLOOKUP, TEXT, etc.}"
Row Q+5: "Protected Ranges" | "{any ranges that should not be modified}"
Row Q+6: "Validation Rules" | "{dropdown sources, constraints}"
Row Q+7: "Gotchas" | "{non-breaking spaces in headers, merged cells, hidden sheets, etc.}"
Row Q+8: "Related Docs" | "{links to relevant docs in Master_Automation/docs/}"
```

### Formatting Rules

| Element | Style |
|---------|-------|
| **Title row (Row 1)** | Font: Calibri 16pt Bold, Color: Navy (#1A2744), Fill: Light Gold (#F5F0E0) |
| **Subtitle row (Row 2)** | Font: Calibri 10pt Italic, Color: Gray (#666666) |
| **Section headers** | Font: Calibri 12pt Bold, Color: White (#FFFFFF), Fill: Navy (#1A2744), Full row merge |
| **Column headers** | Font: Calibri 10pt Bold, Color: Navy (#1A2744), Fill: Light Blue (#D6E4F0), Border: thin bottom |
| **Data cells** | Font: Calibri 10pt, Color: Black, Alternating row fill: White / #F2F2F2 |
| **Hyperlinks** | Font: Calibri 10pt, Color: Blue (#0563C1), Underline |
| **Freeze panes** | Freeze at Row 3 (title + subtitle always visible) |
| **Gridlines** | Hidden on this sheet only |
| **Column widths** | Auto-fit with minimum 15 characters, maximum 80 characters |
| **Tab color** | Gold (#C8A84B) — matches HPD report style |

> **Color Palette Source:** HPD Report Design System (`docs/templates/HPD_Report_Style_Prompt.md`):
> Navy `#1A2744`, Gold `#C8A84B`, Dark Green `#2E7D32`, Dark Red `#B71C1C`

---

## Acceptance Criteria

1. **Do NOT modify, delete, or overwrite** any existing data, formulas, sheets, VBA code, or logs. The only mutation is adding/replacing the `AI_Context_Reference` sheet.
2. **Preserve VBA projects** in `.xlsm` files — use `keep_vba=True` with `openpyxl` and verify macro functionality is intact after save.
3. **Gracefully handle errors** — password-protected files, missing workbooks, corrupt files, and permission issues should be logged and skipped.
4. **Cross-reference config files** — read `config/scripts.json` and `visual_export_mapping.json` to populate ETL integration data. Do not hardcode what can be looked up.
5. **Terminal summary** — after processing, print a formatted table showing:
   - Workbook name
   - Status (✅ Injected / ⚠️ Skipped / ❌ Error)
   - Sheets found
   - Tables found
   - VBA modules found (if .xlsm)
   - M Code query mapped
   - Reason for skip/error (if applicable)
6. **Idempotent** — running the script multiple times produces the same result. If `AI_Context_Reference` already exists, delete and recreate it.
7. **Non-breaking space handling** — detect and document `\xa0` characters in column headers (common in ESU and CSB workbooks).

---

## Additional Context from Repository

### Key Repository Paths (for cross-referencing)
```
Master_Automation/
├── config/scripts.json                    # ETL script registry
├── config/response_time_filters.json      # Response time exclusion filters
├── Standards/config/powerbi_visuals/
│   └── visual_export_mapping.json         # 40+ visual export routing rules
├── m_code/                                # 133 Power Query M files across 26 folders
│   ├── parameters/                        # pReportMonth, EtlRootPath, etc.
│   ├── shared/                            # ___DimMonth, ___ComprehensiveDateTable
│   ├── functions/                         # fnLoadRaw, fnEnsureColumns, etc.
│   └── {domain}/                          # arrests, csb, drone, esu, etc.
├── scripts/                               # Python ETL and utility scripts
├── docs/                                  # 262+ documentation files
│   ├── SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md
│   ├── DFR_Summons_Claude_Excel_Development_Log.md
│   ├── SSOCC_Service_Log_Excel_And_Power_BI_Rework_2026_03.md
│   ├── POLICY_TRAINING_AUTOMATION_AND_COST_VISUAL.md
│   └── ESU_POWER_BI_LOAD_AND_PUBLISH.md
└── 09_Reference/
    ├── Personnel/Assignment_Master_V3_FINAL.xlsx
    └── Standards/ResponseTime_AllMetrics_DataDictionary.md
```

### pReportMonth Standard (Project-Wide)
All M code queries use `pReportMonth` (migrated 2026-03-09). The parameter is set per `.pbix` file:
```
pReportMonth = #date(2026, 3, 1)  // March 2026 report
```
Standard 13-month window:
```
EndOfWindow   = Date.EndOfMonth(pReportMonth)
StartOfWindow = Date.StartOfMonth(Date.AddMonths(pReportMonth, -12))
```

### Author & Organization
- **Author**: R. A. Carucci #261 | Principal Analyst
- **Unit**: Safe Streets Operations Control Center (SSOCC)
- **Department**: Hackensack Police Department
- **Project Version**: v1.19.8+

---

## Execution Command

```bash
# From Master_Automation repo root (or adjust path):
python scripts/inject_ai_context_reference.py

# With options:
python scripts/inject_ai_context_reference.py --dry-run          # Preview without writing
python scripts/inject_ai_context_reference.py --workbook "ESU"   # Single workbook
python scripts/inject_ai_context_reference.py --verbose           # Detailed logging
python scripts/inject_ai_context_reference.py --tier2             # Include Tier 2 workbooks
```

Please begin by writing and executing the Python script to map the local directory and generate these reference sheets.
