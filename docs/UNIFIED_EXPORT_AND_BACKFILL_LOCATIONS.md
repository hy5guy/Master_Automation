# Unified Export and Backfill Locations — Recommendation

**Date:** 2026-03-04  
**Status:** Proposal for standardization

---

## Current State (Fragmented)

| Data Type | Export Location | Backfill Location |
|-----------|-----------------|-------------------|
| Overtime/TimeOff (VCS) | `_DropExports` → `organize_backfill_exports.ps1` | `PowerBI_Data\Backfill\YYYY_MM\vcs_time_report\` |
| Summons | `03_Staging\Summons\` | `PowerBI_Data\Backfill\YYYY_MM\summons\` or `00_dev\projects\PowerBI_Data\Backfill\` |
| Arrests | `01_DataSources\ARREST_DATA\Power_BI\` | Various |
| Response Times | `02_ETL_Scripts\Response_Times\output\` | `PowerBI_Data\Backfill\YYYY_MM\response_time\` |
| Chief/Contributions | `Shared Folder\Compstat\Contributions\` | — |
| STACP/Social Media | `Shared Folder\Compstat\Contributions\STACP\` | — |

---

## Proposed Unified Structure

### 1. Visual Export Drop (Raw)

**Purpose:** Single folder where Power BI exports land before processing.

```
{OneDrive}\PowerBI_Data\_DropExports\
├── *.csv                    # All visual exports (unnamed or timestamped)
├── _manifest.json           # Catalog of files
└── _manifest.csv
```

**Workflow:** Power BI → Export to _DropExports → `organize_backfill_exports.ps1` categorizes and moves to Backfill.

---

### 2. Backfill (Processed, Cleaned, Standardized)

**Purpose:** One root for all backfill data, organized by report month and category.

```
{OneDrive}\PowerBI_Data\Backfill\
├── 2026_01\
│   ├── vcs_time_report\           # Overtime/TimeOff
│   │   └── 2026_01_Monthly Accrual and Usage Summary.csv
│   ├── summons\
│   │   └── 2026_01_Department-Wide Summons  Moving and Parking.csv
│   ├── response_time\
│   │   └── 2026_01_*_Average_Response_Times*.csv
│   └── ...
├── 2026_02\
│   └── ...
└── _TEMPLATE_YYYY_MM\             # Template for new months
```

**Naming convention:** `{YYYY_MM}_{original_name}.csv` (e.g., `2026_01_Monthly Accrual and Usage Summary.csv`)

---

### 3. ETL Output (Staging)

**Purpose:** Processed data ready for Power BI to consume.

```
{OneDrive}\03_Staging\
├── Summons\
│   ├── summons_slim_for_powerbi.csv
│   ├── summons_powerbi_latest.xlsx
│   └── *_RAW.csv
├── Arrests\                      # If consolidated
└── ...
```

---

## Implementation Checklist

- [ ] Update `organize_backfill_exports.ps1` to use only `PowerBI_Data\Backfill\YYYY_MM\`
- [ ] Deprecate `00_dev\projects\PowerBI_Data\Backfill` in favor of `PowerBI_Data\Backfill`
- [ ] Standardize backfill filenames: `YYYY_MM_{descriptive_name}.csv`
- [ ] Document category folders per visual type (vcs_time_report, summons, response_time, etc.)
- [ ] Update `summons_derived_outputs.py` and other scripts to read from unified Backfill path
- [ ] Add `PowerBI_Data\_DropExports` as the single export target in Power BI bookmark/instructions

---

## References

- `scripts/organize_backfill_exports.ps1`
- `scripts/normalize_visual_export_for_backfill.py`
- `docs/VISUAL_EXPORT_NORMALIZATION_AND_SUMMONS_BACKFILL.md`
