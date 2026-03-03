---
name: PBIX Export Automation
overview: Export all M code queries and visual data from the January 2026 PBIX file using PBIX ZIP extraction for M code and ADOMD.NET (via DAX Studio DLL) for visual data against the local AS instance on port 49673.
todos:
  - id: write-export-script
    content: "Write Export-PbixData.ps1: M code extraction + AS data export + manifests"
    status: pending
  - id: run-export
    content: Execute the script and verify outputs against acceptance checks
    status: pending
  - id: verify-counts
    content: Confirm M code count matches PBIX queries and visual export count matches discovered visuals
    status: pending
isProject: false
---

# PBIX Export Automation

## Environment (confirmed)

- **PBIX**: `C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Monthly Reports\2026\01_january\2026_01_Monthly_Report.pbix`
- **PBI Desktop**: Store version, PID 46176
- **AS instance**: `localhost:49673`, PID 13688, database `9c28d788-a168-44d9-bc2d-61caebf2bd8b`
- **ADOMD.NET**: `C:\Program Files\DAX Studio\bin\Microsoft.AnalysisServices.AdomdClient.dll` (v19.98.0.3)
- **dotnet**: 10.0.103 (can install `pbi-tools`)
- **Python**: 3.14.2
- **Output root**: `C:\Users\carucci_r\Downloads\PBIX_Exports\2026_02_21\`

## Approach

### A. M Code Export

**Primary method**: Parse the PBIX as a ZIP archive, extract the `DataMashup` blob, locate the inner ZIP within it, then extract individual query `.m` files from the `Formulas` section.

**Fallback**: Install `pbi-tools` via `dotnet tool install --global pbi-tools` and run `pbi-tools extract`.

**Output**:

- `01_M_Code\<QueryName>.m` -- one file per query
- `01_M_Code\ALL_QUERIES_CONSOLIDATED.m` -- all queries concatenated
- `01_M_Code\m_export_manifest.csv` -- query_name, file_name, bytes, modified_time

### B. Visual Data Export

**Method**: Single PowerShell script using ADOMD.NET from DAX Studio:

1. Connect to `localhost:49673`
2. Query `$SYSTEM.MDSCHEMA_MEASURES` to list all measures
3. Query `$SYSTEM.DBSCHEMA_TABLES` to list all tables
4. For each table, run `EVALUATE 'TableName'` and export to CSV
5. Extract `Report/Layout` from the PBIX ZIP to enumerate pages and visuals
6. Cross-reference visuals to tables for the mapping

**Output**:

- `02_Visual_Data_Exports\<PageName>__<VisualTitle>.csv` -- one per visual/table
- `02_Visual_Data_Exports\visual_export_manifest.csv` -- page, visual, file_name, rows, cols, bytes, modified_time
- `02_Visual_Data_Exports\visual_export_mapping.json` -- generated from report layout

## Script delivery

One PowerShell script (`Export-PbixData.ps1`) that:

1. Creates the output directory structure
2. Extracts M code from the PBIX ZIP
3. Connects to AS instance and exports all table data
4. Parses report layout for visual inventory
5. Generates both manifests
6. Fails fast with clear error messages at each step

## Risks

- **PBIX ZIP parsing**: The DataMashup blob has a binary header before the inner ZIP. Script will scan for the PK magic bytes to find the ZIP start offset.
- **Visual-to-table mapping**: Report layout JSON maps visuals to model objects, but complex visuals (measures, calculated columns) may not map 1:1 to a single table export. Script will export all model tables and note the mapping.
- **Store version permissions**: WindowsApps folder is locked; ADOMD.NET from DAX Studio works as confirmed.

