# Summons Classification and Date Sorting Fix - 2026-02-17

## Resolution / Final Status (2026-02-17)

**Visuals verified:** Top 5 Moving, Top 5 Parking, and All Bureaus are correct. Implemented approach:

- **ETL** (`summons_etl_enhanced.py`): TYPE from export **Case Type Code** only (M/P/C)—no statute logic. Officer identity = badge; display name from Assignment Master **Proposed 4-Digit Format**. TITLE from Assignment Master (used to exclude PEO from Moving). Optional: `run_eticket_export.py` runs ETL on `05_EXPORTS\_Summons\E_Ticket\2026\month\2026_01_eticket_export.csv`.
- **Power BI:** All three queries use **previous complete month** (e.g. January 2026 when run in February). Top 5 Moving excludes TITLE = "PEO". All Bureaus filters UNKNOWN WG2 and consolidates Housing/OSO into Patrol. Copy-paste M code: `docs/SUMMONS_M_CODE_FINAL.md`; source files: `m_code/___Summons_Top5_Moving_STANDALONE.m`, `___Summons_Top5_Parking_STANDALONE.m`, `___Summons_All_Bureaus_STANDALONE.m`.

---

## Context (Original Problem)

We had a data classification bug in our Summons ETL pipeline and a date sorting issue in Power BI visuals.

### The Problem

1. **Classification Issue**: The raw State E-Ticket Export defaults almost all Moving violations to "P" (Parking) in the `Case Type Code` column, causing Moving Summons count to be ~35 instead of the actual ~211.

2. **Power BI Sorting Issue**: "Top 5" and "All Bureaus" visuals are sorting months alphabetically (text "01-26" comes before "12-25"), hiding January 2026 data.

### Current Architecture

- **ETL Entry Point**: `02_ETL_Scripts\Summons\main_orchestrator.py`
- **Output**: `03_Staging\Summons\summons_powerbi_latest.xlsx` (sheet: `Summons_Data`)
- **Source**: `05_EXPORTS\_Summons\E_Ticket\YYYY\YYYY_MM_eticket_export.csv`
- **Personnel**: `09_Reference\Personnel\Assignment_Master_V2.csv`
- **Backfill**: Handled by `scripts/summons_backfill_merge.py` for gap months (03-25, 07-25, 10-25, 11-25)

---

## Part 1: Python ETL Fix - Statute-Based Classification

### Location
File: `02_ETL_Scripts\Summons\main_orchestrator.py` (or wherever classification logic exists)

### Required Changes

#### 1. Update Classification Function

Replace or enhance the existing classification logic with Statute-based priority:

```python
def classify_violation(row):
    """
    Primary logic: Prioritizes Statute (Title 39) to capture Moving violations
    that the State incorrectly labels as 'P'.
    """
    # Normalize inputs
    raw_type = str(row.get('Case Type Code', '')).strip().upper()
    statute = str(row.get('Statute', '')).strip().upper()
    description = str(row.get('Violation Description', '')).upper()
    
    # 1. STATUTE CHECK (Primary Authority for Moving)
    # If it is Title 39, it is Moving, regardless of what Case Type says.
    if statute.startswith("39:"):
        return "M"

    # 2. PARKING CHECK
    parking_keywords = ["PARK", "METER", "HANDICAP", "NO PARKING", "STATIONARY", "FIRE HYDRANT", "BLOCKING"]
    is_parking_statute = statute.startswith("39:4-138") or statute.startswith("39:4-135")
    
    if is_parking_statute or any(keyword in description for keyword in parking_keywords):
        return "P"
    
    # 3. FALLBACK: Use Case Type Code if it is valid
    if raw_type in ['M', 'P', 'C']:
        return raw_type
    
    # Default fallback
    return "P"
```

#### 2. Add Required Schema Columns

Ensure the output includes all columns needed by Power BI:

```python
# Add metadata columns (if not already present)
merged_df['TICKET_COUNT'] = 1
merged_df['PROCESSING_TIMESTAMP'] = datetime.now()
merged_df['ETL_VERSION'] = 'ETICKET_CURRENT'
merged_df['IS_AGGREGATE'] = False

# Add time dimension columns
if 'Issue Date' in merged_df.columns:
    merged_df['ISSUE_DATE'] = pd.to_datetime(merged_df['Issue Date'], errors='coerce')
    merged_df['Month_Year'] = merged_df['ISSUE_DATE'].dt.strftime('%m-%y')
    merged_df['Year'] = merged_df['ISSUE_DATE'].dt.year
    merged_df['Month'] = merged_df['ISSUE_DATE'].dt.month
    # Critical for sorting:
    merged_df['YearMonthKey'] = (merged_df['Year'] * 100 + merged_df['Month']).fillna(0).astype(int)

# Add missing schema columns (if not already present)
merged_df['VIOLATION_TYPE'] = merged_df['TYPE'].map({'M': 'Moving', 'P': 'Parking', 'C': 'Court'})
merged_df['WARNING_FLAG'] = ''
merged_df['DATA_QUALITY_SCORE'] = 0
merged_df['DATA_QUALITY_TIER'] = ''
merged_df['TOTAL_PAID_AMOUNT'] = merged_df.get('Penalty', 0)
merged_df['COST_AMOUNT'] = 0
merged_df['MISC_AMOUNT'] = 0
merged_df['FINE_AMOUNT'] = merged_df.get('Penalty', 0)

# Rename columns to match Power BI expectations
col_map = {
    'Ticket Number': 'TICKET_NUMBER',
    'Statute': 'VIOLATION_NUMBER',
    'Violation Description': 'VIOLATION_DESCRIPTION',
    'Case Status Code': 'STATUS',
    'Offense Street Name': 'LOCATION'
}
merged_df = merged_df.rename(columns={k: v for k, v in col_map.items() if k in merged_df.columns})
```

#### 3. Use Portable Paths

Replace hardcoded paths with `path_config.py`:

```python
from pathlib import Path
import sys

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent.parent / "Master_Automation" / "scripts"
sys.path.insert(0, str(scripts_dir))

from path_config import get_onedrive_root

def get_default_paths():
    """Get portable OneDrive paths"""
    onedrive_root = get_onedrive_root()
    
    return {
        'eticket_path': onedrive_root / "05_EXPORTS" / "_Summons" / "E_Ticket" / "2026" / "2026_01_eticket_export.csv",
        'master_path': onedrive_root / "09_Reference" / "Personnel" / "Assignment_Master_V2.csv",
        'output_path': onedrive_root / "03_Staging" / "Summons" / "summons_powerbi_latest.xlsx"
    }
```

---

## Part 2: Power BI M Code Fixes - Integer-Based Date Sorting

### File Locations
- `m_code/summons_top5_moving.m`
- `m_code/summons_top5_parking.m`
- `m_code/summons_all_bureaus.m`

### Required Changes

Replace text-based month filtering with integer-based `YearMonthKey` logic:

#### 1. Top 5 Moving Violations

```powerquery
let
    // Use path_config for portability
    OneDriveRoot = "C:\Users\carucci_r\OneDrive - City of Hackensack\",
    FilePath = OneDriveRoot & "03_Staging\Summons\summons_powerbi_latest.xlsx",
    
    Source = Excel.Workbook(File.Contents(FilePath), null, true),
    Summons_Data_Sheet = Source{[Item="Summons_Data",Kind="Sheet"]}[Data],
    #"Promoted Headers" = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"YearMonthKey", Int64.Type}, {"TICKET_COUNT", Int64.Type}}),
    
    // FILTER: Only Moving
    #"Filtered Moving" = Table.SelectRows(#"Changed Type", each ([TYPE] = "M")),

    // FIX: Find Latest Month using Integer Key (not text sorting!)
    LatestKey = List.Max(#"Filtered Moving"[YearMonthKey]),
    #"Filtered Latest Month" = Table.SelectRows(#"Filtered Moving", each [YearMonthKey] = LatestKey),

    // GROUP: Top 5
    #"Grouped Rows" = Table.Group(#"Filtered Latest Month", {"VIOLATION_DESCRIPTION"}, {{"Count", each List.Sum([TICKET_COUNT]), type nullable number}}),
    #"Sorted Rows" = Table.Sort(#"Grouped Rows",{{"Count", Order.Descending}}),
    #"Kept First Rows" = Table.FirstN(#"Sorted Rows",5)
in
    #"Kept First Rows"
```

#### 2. Top 5 Parking Violations

```powerquery
let
    OneDriveRoot = "C:\Users\carucci_r\OneDrive - City of Hackensack\",
    FilePath = OneDriveRoot & "03_Staging\Summons\summons_powerbi_latest.xlsx",
    
    Source = Excel.Workbook(File.Contents(FilePath), null, true),
    Summons_Data_Sheet = Source{[Item="Summons_Data",Kind="Sheet"]}[Data],
    #"Promoted Headers" = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"YearMonthKey", Int64.Type}, {"TICKET_COUNT", Int64.Type}}),
    
    // FILTER: Only Parking
    #"Filtered Parking" = Table.SelectRows(#"Changed Type", each ([TYPE] = "P")),

    // FIX: Find Latest Month using Integer Key
    LatestKey = List.Max(#"Filtered Parking"[YearMonthKey]),
    #"Filtered Latest Month" = Table.SelectRows(#"Filtered Parking", each [YearMonthKey] = LatestKey),

    // GROUP: Top 5
    #"Grouped Rows" = Table.Group(#"Filtered Latest Month", {"VIOLATION_DESCRIPTION"}, {{"Count", each List.Sum([TICKET_COUNT]), type nullable number}}),
    #"Sorted Rows" = Table.Sort(#"Grouped Rows",{{"Count", Order.Descending}}),
    #"Kept First Rows" = Table.FirstN(#"Sorted Rows",5)
in
    #"Kept First Rows"
```

#### 3. All Bureaus Summary

```powerquery
let
    OneDriveRoot = "C:\Users\carucci_r\OneDrive - City of Hackensack\",
    FilePath = OneDriveRoot & "03_Staging\Summons\summons_powerbi_latest.xlsx",
    
    Source = Excel.Workbook(File.Contents(FilePath), null, true),
    Summons_Data_Sheet = Source{[Item="Summons_Data",Kind="Sheet"]}[Data],
    #"Promoted Headers" = Table.PromoteHeaders(Summons_Data_Sheet, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"YearMonthKey", Int64.Type}, {"TICKET_COUNT", Int64.Type}}),

    // FIX: Find Latest Month using Integer Key
    LatestKey = List.Max(#"Changed Type"[YearMonthKey]),
    #"Filtered Latest Month" = Table.SelectRows(#"Changed Type", each [YearMonthKey] = LatestKey),

    // GROUP: By Bureau (WG2) and Type
    #"Grouped Rows" = Table.Group(#"Filtered Latest Month", {"WG2", "TYPE"}, {{"Count", each List.Sum([TICKET_COUNT]), type nullable number}}),
    
    // PIVOT & TOTAL
    #"Pivoted Column" = Table.Pivot(#"Grouped Rows", List.Distinct(#"Grouped Rows"[TYPE]), "TYPE", "Count", List.Sum),
    #"Replaced Value" = Table.ReplaceValue(#"Pivoted Column",null,0,Replacer.ReplaceValue,{"M", "P", "C"}),
    #"Added Total" = Table.AddColumn(#"Replaced Value", "Total", each [M] + [P] + (try [C] otherwise 0))
in
    #"Added Total"
```

---

## Part 3: Testing and Verification

### Python ETL Testing

```powershell
# From Master_Automation directory
cd "C:\Users\RobertCarucci\OneDrive - City of Hackensack\Master_Automation"

# Run Summons ETL only
.\scripts\run_etl_script.ps1 -ScriptName "Summons"

# Verify output
# Check: 03_Staging\Summons\summons_powerbi_latest.xlsx
# Confirm: YearMonthKey column exists
# Confirm: Moving violations (TYPE='M') count is ~211 (not ~35)
```

### Power BI Testing

1. Open Power BI Desktop
2. Update M code queries (3 queries)
3. Refresh data
4. Verify:
   - **Top 5 Moving**: Shows January 2026 data (if available)
   - **Top 5 Parking**: Shows January 2026 data (if available)
   - **All Bureaus**: Shows January 2026 data (if available)
   - Months are sorted correctly (202601 > 202512)

### Expected Results

#### Before Fix:
- Moving count: ~35
- Parking count: ~211
- Latest month displayed: December 2025 (12-25)
- Sorting: Alphabetical (12-25 appears last)

#### After Fix:
- Moving count: ~211
- Parking count: ~35
- Latest month displayed: January 2026 (01-26) if data exists
- Sorting: Numerical (202601 appears last)

---

## Part 4: Integration with Backfill

### Gap Month Handling

The Summons ETL should integrate with backfill for gap months (03-25, 07-25, 10-25, 11-25):

```python
# In main_orchestrator.py, after creating merged_df

from pathlib import Path
import sys
scripts_dir = Path(__file__).parent.parent.parent / "Master_Automation" / "scripts"
sys.path.insert(0, str(scripts_dir))

from summons_backfill_merge import merge_missing_summons_months
from path_config import get_onedrive_root

# Merge gap months from backfill
backfill_root = get_onedrive_root() / "PowerBI_Date" / "Backfill"
merged_df = merge_missing_summons_months(merged_df, backfill_root)
```

See `docs/SUMMONS_BACKFILL_INJECTION_POINT.md` for full details.

---

## Part 5: Documentation Updates

After implementing fixes, update:

1. **CHANGELOG.md** - Document version bump and fixes
2. **SUMMARY.md** - Update Summons section with fix status
3. **M_code files** - Add standard headers with fix notes

---

## Implementation Checklist

- [ ] Update classification function in `main_orchestrator.py`
- [ ] Add `YearMonthKey` column to output
- [ ] Verify all required schema columns exist
- [ ] Test Python ETL (verify ~211 Moving violations)
- [ ] Update Top 5 Moving M code
- [ ] Update Top 5 Parking M code
- [ ] Update All Bureaus M code
- [ ] Test Power BI refresh
- [ ] Verify January 2026 data displays (if available)
- [ ] Verify correct month sorting (202601 > 202512)
- [ ] Integrate backfill merge (if needed)
- [ ] Update documentation (CHANGELOG, SUMMARY)

---

**Created**: 2026-02-17  
**Status**: Ready for Implementation  
**Priority**: High (Data Quality Issue)
