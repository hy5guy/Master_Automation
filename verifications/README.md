# ETL Verification Framework

A reusable verification framework for validating monthly ETL script outputs against baseline backfill data.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [How to Add a New Verifier](#how-to-add-a-new-verifier)
- [Running Verifications](#running-verifications)
- [Interpreting Reports](#interpreting-reports)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

The ETL Verification Framework automates the validation of monthly ETL script outputs by:

1. **Comparing** current month exports with baseline backfill data
2. **Validating** processing rules specific to each ETL script
3. **Detecting** discrepancies in overlapping time periods
4. **Generating** comprehensive verification reports

### Key Features

- **Reusable Base Class**: `ETLVerifier` handles common verification logic
- **Modular Design**: Each ETL script has its own verifier class
- **Multiple CSV Formats**: Supports both wide and long format CSV files
- **Tolerance-Based Comparison**: Handles floating-point precision issues (±0.01)
- **Comprehensive Reports**: Markdown and JSON output with detailed findings
- **Master Runner**: Execute all verifications in sequence

## Quick Start

### Run All Verifications

```bash
cd C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\verifications
python run_all_verifications.py
```

### Run Single Verification

```bash
# Overtime & Time Off
python overtime_timeoff_verifier.py

# Arrests
python arrests_verifier.py
```

### Expected Directory Structure

```
Master_Automation/
├── verifications/
│   ├── reports/                          # Generated verification reports
│   │   ├── ARRESTS_MONTHLY_VERIFICATION_REPORT.md
│   │   └── OVERTIME_TIMEOFF_MONTHLY_VERIFICATION_REPORT.md
│   ├── etl_verification_framework.py    # Base class
│   ├── overtime_timeoff_verifier.py     # Overtime verifier
│   ├── arrests_verifier.py              # Arrests verifier
│   ├── run_all_verifications.py         # Master runner
│   └── README.md                         # This file
├── outputs/                              # Current month exports
│   ├── arrests/
│   ├── visual_exports/
│   ├── summons_validation/
│   └── ...
└── VERIFICATION_SUMMARY_*.md             # Generated master summaries
```

## Architecture

### Base Class: ETLVerifier

The `ETLVerifier` base class in `etl_verification_framework.py` provides:

**Core Methods:**
- `compare_month_overlap()` - Compare current vs backfill for overlapping months
- `check_data_integrity()` - Validate nulls, negatives, empty columns
- `generate_report()` - Create standardized markdown report
- `run_verification()` - Main workflow orchestrator

**CSV Format Support:**
- `parse_long_format()` - Handle CSV with PeriodLabel column
- `parse_wide_format()` - Convert wide format (month columns) to long format

**Configuration:**
- `backfill_root` - Path to backfill data
- `outputs_dir` - Path to current month exports
- `tolerance` - Numeric comparison tolerance (default: 0.01)

### Individual Verifiers

Each verifier inherits from `ETLVerifier` and implements:

1. **`__init__()`** - Define script name, output files, backfill category
2. **`validate_processing_rules()`** - Document ETL-specific processing rules

## How to Add a New Verifier

Follow these steps to create a verifier for a new ETL script.

### Step 1: Create Verifier File

Create `verifications/{script_name}_verifier.py`:

```python
"""
{Script Name} Monthly ETL Verifier

Verifies {script name} monthly processing against November 2025 backfill.

Expected Output Files:
- {output_file_1}.csv
- {output_file_2}.csv

Version: 1.0.0
Created: {date}
"""

import sys
from pathlib import Path

# Add verifications directory to path
sys.path.insert(0, str(Path(__file__).parent))

from etl_verification_framework import ETLVerifier


class {ScriptName}Verifier(ETLVerifier):
    """Verifier for {script name} monthly ETL script."""

    def __init__(self, current_month: str = "2025_12", backfill_month: str = "2025_11"):
        """
        Initialize {script name} verifier.

        Args:
            current_month: Month to verify (default: "2025_12")
            backfill_month: Baseline month for comparison (default: "2025_11")
        """
        super().__init__(
            script_name="{script_name}_monthly",
            output_files=[
                "{output_file_1}.csv",
                "{output_file_2}.csv"
            ],
            backfill_category="{backfill_folder_name}",
            backfill_month=backfill_month,
            current_month=current_month
        )

    def validate_processing_rules(self):
        """
        Validate {script name} specific processing rules.

        Returns:
            List of validation results
        """
        validations = []

        # Rule 1: {Description}
        validations.append({
            "rule": "{Rule Name}",
            "description": "{What this rule validates}",
            "passed": True,
            "notes": "{Implementation details or verification approach}"
        })

        # Add more rules...

        return validations


def main():
    """Run {script name} verification."""
    print("=" * 80)
    print("{SCRIPT NAME} MONTHLY ETL VERIFICATION")
    print("=" * 80)
    print()

    # Initialize verifier
    verifier = {ScriptName}Verifier()

    # Check for output files
    print("[PRE-CHECK] Verifying December 2025 {script name} exports exist...")
    missing_files = []
    for filename in verifier.output_files:
        filepath = verifier.outputs_dir / filename
        if not filepath.exists():
            # Try with month prefix
            prefixed = f"{verifier.current_month}_{filename}"
            filepath_prefixed = verifier.outputs_dir / prefixed
            if not filepath_prefixed.exists():
                missing_files.append(filename)
                print(f"  [MISSING] {filename}")
            else:
                print(f"  [FOUND] {prefixed}")
        else:
            print(f"  [FOUND] {filename}")

    if missing_files:
        print()
        print("=" * 80)
        print("WARNING: DECEMBER 2025 {SCRIPT NAME} EXPORTS NOT FOUND")
        print("=" * 80)
        print()
        print("Expected output files:")
        for f in missing_files:
            print(f"  - {f}")
        print()
        return

    # Run full verification
    print()
    print("[VERIFICATION] Running full {script name} verification...")
    results = verifier.run_verification()

    # Print summary
    print()
    print("=" * 80)
    print(f"FINAL STATUS: {results['status']}")
    print(f"Pass Rate: {results.get('pass_rate', 0):.1f}%")
    print(f"Report: {results.get('report_path', 'N/A')}")
    print("=" * 80)


if __name__ == "__main__":
    main()
```

### Step 2: Identify Required Information

Before writing your verifier, gather:

1. **Script Name**: Python script filename (e.g., `overtime_timeoff_13month_sworn_breakdown_v10.py`)
2. **Output Files**: List of CSV files the script exports
3. **Backfill Category**: Folder name in backfill structure (e.g., `vcs_time_report`, `arrest`)
4. **Processing Rules**: List of 5-10 critical rules the ETL script implements

### Step 3: Document Processing Rules

In `validate_processing_rules()`, document each critical rule:

- **Date Windowing**: How the script filters dates (e.g., 13-month rolling window)
- **Status Filtering**: What status values are included (e.g., only "Approved")
- **Classification Logic**: How records are categorized (e.g., Sworn vs NonSworn)
- **Exclusion Rules**: What data is excluded (e.g., COMP from Time Off files)
- **Normalization**: How data is standardized (e.g., name format conversion)
- **Aggregation**: How data is grouped and summed

### Step 4: Add to Master Runner

Edit `run_all_verifications.py` and add your verifier:

```python
# Import at top
from {script_name}_verifier import {ScriptName}Verifier

# Add to run_all_verifications() method
self._run_verification(
    name="{Script Display Name}",
    verifier_class={ScriptName}Verifier,
    priority={N}
)
```

### Step 5: Test Your Verifier

```bash
# Test standalone
python verifications/{script_name}_verifier.py

# Test in master runner
python verifications/run_all_verifications.py
```

## Running Verifications

### Prerequisites

1. **Backfill Data**: November 2025 backfill must exist at:
   ```
   C:\Users\carucci_r\OneDrive - City of Hackensack\00_dev\projects\PowerBI_Date\Backfill\2025_11\{category}\
   ```

2. **Current Month Exports**: December 2025 exports must exist at:
   ```
   C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\outputs\
   ```

### Run Single Verifier

```bash
cd C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\verifications
python {script_name}_verifier.py
```

**Output:**
- Console output with verification progress
- Report: `reports/{SCRIPT_NAME}_VERIFICATION_REPORT_{timestamp}.md`

### Run All Verifiers

```bash
cd C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\verifications
python run_all_verifications.py
```

**Options:**
```bash
# Verify different months
python run_all_verifications.py --current-month 2026_01 --backfill-month 2025_12
```

**Output:**
- Console output with overall progress
- JSON summary: `../VERIFICATION_SUMMARY_{timestamp}.json`
- Markdown summary: `../VERIFICATION_SUMMARY_{timestamp}.md`

## Interpreting Reports

### Individual Verification Report

Generated by each verifier at `{SCRIPT_NAME}_VERIFICATION_REPORT_{timestamp}.md`.

**Sections:**

1. **Verification Summary**
   - Script name and version
   - Current and backfill months
   - Overall status: PASSED, FAILED, or ERRORS

2. **Data Comparison**
   - Table showing current vs backfill values for overlapping months
   - Match/Diff indicators
   - Pass rate percentage

3. **Data Integrity Checks**
   - Null value detection
   - Negative value detection
   - Empty column detection

4. **Processing Rules Validation**
   - List of critical rules with pass/fail status
   - Implementation notes for each rule

5. **Detailed Findings**
   - Comparison details for each category
   - Specific discrepancies if any

### Master Verification Summary

Generated by `run_all_verifications.py` at `VERIFICATION_SUMMARY_{timestamp}.md`.

**Sections:**

1. **Overall Statistics**
   - Total verifications run
   - Passed, Failed, Skipped, Errors counts
   - Overall pass rate

2. **Individual Verifications Table**
   - Priority, Name, Status, Pass Rate
   - Issue count and report link for each

3. **Detailed Issues**
   - Breakdown of issues by verification

4. **Recommendations**
   - Actions needed for failed verifications
   - Instructions for skipped verifications
   - Error resolution guidance

### Status Codes

- **PASSED**: All comparisons match within tolerance, no integrity issues
- **FAILED**: One or more discrepancies detected, but verification completed
- **SKIPPED**: Required export files not found
- **ERROR**: Unexpected error during verification (e.g., malformed CSV)

## Troubleshooting

### Missing Export Files

**Symptom:** `[MISSING] {filename}.csv`

**Cause:** December 2025 exports haven't been generated or are in wrong location.

**Solution:**
1. Run the ETL script to generate exports
2. Export CSV files from Power BI visuals
3. Ensure files are in `Master_Automation/outputs/` directory
4. Files can be named with or without `{YYYY_MM}_` prefix

### Format Mismatch Errors

**Symptom:** `KeyError: 'PeriodLabel'` or similar column errors

**Cause:** CSV format doesn't match expected structure (wide vs long format).

**Solution:**
1. Check if file uses wide format (month columns) or long format (PeriodLabel column)
2. The framework auto-detects format, but may need adjustment
3. Verify column names match expected conventions
4. Check for BOM encoding issues (framework handles UTF-8-sig)

### All Values Show as Differences

**Symptom:** 0% pass rate despite data looking correct

**Cause:** Column names don't match between current and backfill.

**Solution:**
1. Check column name standardization in `compare_month_overlap()`
2. Verify `category_col`, `value_col`, `month_col` parameters
3. Add column name mapping if needed

### Tolerance Issues

**Symptom:** Small differences flagged (e.g., 123.00 vs 123.01)

**Cause:** Floating-point precision or Excel export rounding.

**Solution:**
- Default tolerance is ±0.01
- Adjust by passing `tolerance` parameter to verifier constructor:
  ```python
  super().__init__(
      ...,
      tolerance=0.1  # Increase to 0.1 if needed
  )
  ```

### Backfill Not Found

**Symptom:** `Backfill directory not found: {path}`

**Cause:** Wrong backfill category or path.

**Solution:**
1. Check backfill structure at:
   ```
   C:\Users\carucci_r\OneDrive - City of Hackensack\00_dev\projects\PowerBI_Date\Backfill\2025_11\
   ```
2. Verify `backfill_category` matches folder name exactly
3. Common categories: `vcs_time_report`, `arrest`, `nibrs`, `summons`

## Best Practices

### When Creating Verifiers

1. **Document Everything**: Write clear docstrings and comments
2. **Test Both Formats**: Handle wide and long CSV formats
3. **Be Specific**: Name files exactly as they appear in exports
4. **Validate Assumptions**: Document what the ETL script SHOULD do
5. **Keep Rules Focused**: 5-10 critical rules is ideal

### When Running Verifications

1. **Run After ETL**: Always run verification immediately after running ETL script
2. **Check Pre-Conditions**: Verify exports exist before running
3. **Review Reports**: Don't just look at pass/fail, review details
4. **Archive Reports**: Keep verification reports with monthly exports
5. **Trend Analysis**: Compare verification results month-over-month

### When Investigating Failures

1. **Check Recent Changes**: Did the ETL script change?
2. **Compare Raw Data**: Look at source data for unexpected patterns
3. **Verify Processing**: Manually check a few records through the pipeline
4. **Review Logs**: Check ETL script logs for warnings or errors
5. **Ask Questions**: Don't assume - investigate root cause

## File Naming Conventions

### Export Files

Exports can use either naming convention:

```
# With month prefix (recommended)
2025_12_Monthly Accrual and Usage Summary.csv
2025_12_Arrest Categories by Type and Gender.csv

# Without month prefix
Monthly Accrual and Usage Summary.csv
Arrest Categories by Type and Gender.csv
```

The framework checks both locations automatically.

### Report Files

Generated reports use timestamps:

```
{SCRIPT_NAME}_VERIFICATION_REPORT_20260113_180309.md
VERIFICATION_SUMMARY_20260113_180309.md
VERIFICATION_SUMMARY_20260113_180309.json
```

## Advanced Usage

### Custom Comparison Logic

Override `compare_month_overlap()` for custom comparison:

```python
class CustomVerifier(ETLVerifier):
    def compare_month_overlap(self, current_df, backfill_df, **kwargs):
        # Custom comparison logic
        results = super().compare_month_overlap(current_df, backfill_df, **kwargs)
        # Add custom checks
        return results
```

### Multiple Output Files

Some ETL scripts generate multiple related files:

```python
def __init__(self, ...):
    super().__init__(
        script_name="complex_script",
        output_files=[
            "Summary Report.csv",
            "Detail Report.csv",
            "Lookup Table.csv"
        ],
        ...
    )
```

The framework will verify each file independently.

### Month-to-Month Verification

To verify a different month pair:

```bash
python run_all_verifications.py --current-month 2026_01 --backfill-month 2025_12
```

## Support

For issues or questions:

1. Review this README thoroughly
2. Check the [Troubleshooting](#troubleshooting) section
3. Review existing verifier implementations for examples
4. Check verification reports for detailed error messages

## Version History

- **1.0.0** (2026-01-13): Initial framework release
  - Base ETLVerifier class
  - Overtime & Time Off verifier
  - Arrests verifier
  - Master runner script
