# ETL Verification Summary Report

**Generated:** 2026-01-13 18:15:37

**Current Month:** 2025_12

**Backfill Month:** 2025_11

**Duration:** 0.0 seconds

## Overall Statistics

| Metric | Value |
|--------|-------|
| Total Verifications | 2 |
| Passed | 0 |
| Failed | 0 |
| Skipped | 1 |
| Errors | 0 |
| Overall Pass Rate | 0.0% |

## Individual Verifications

| Priority | Name | Status | Pass Rate | Issues | Report |
|----------|------|--------|-----------|--------|--------|
| 1 | Overtime & Time Off | [SKIP] SKIPPED | 0.0% | 1 | N/A |
| 2 | Arrests | [ERROR] ERROR | 0.0% | 5 | [ARRESTS_MONTHLY_VERIFICATION_REPORT.md](C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\verification_reports\ARRESTS_MONTHLY_VERIFICATION_REPORT.md) |

## Detailed Issues

### Overtime & Time Off

**Status:** SKIPPED

**Issues:**

- Missing export files: Monthly Accrual and Usage Summary.csv

### Arrests

**Status:** FAIL

**Issues:**

- {'severity': 'ERROR', 'category': 'File Missing', 'description': 'Current export not found: C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\Master_Automation\\outputs\\Arrest Categories by Type and Gender.csv'}
- {'severity': 'ERROR', 'category': 'File Missing', 'description': 'Current export not found: C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\Master_Automation\\outputs\\Arrest Distribution by Local, State & Out of State.csv'}
- {'severity': 'ERROR', 'category': 'File Parsing', 'description': 'Failed to parse C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\00_dev\\projects\\PowerBI_Date\\Backfill\\2025_11\\arrest\\2025_11_Arrest Distribution by Local, State & Out of State.csv: 3 columns passed, passed data had 4 columns'}
- {'severity': 'ERROR', 'category': 'File Loading', 'description': 'Both current and backfill missing for Arrest Distribution by Local, State & Out of State.csv'}
- {'severity': 'ERROR', 'category': 'File Missing', 'description': 'Current export not found: C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\Master_Automation\\outputs\\TOP 5 ARREST LEADERS.csv'}

## Recommendations

### Skipped Verifications

The following verifications were skipped due to missing export files:

- **Overtime & Time Off**: Missing export files: Monthly Accrual and Usage Summary.csv

To complete these verifications:
1. Export the required CSV files from Power BI visuals
2. Place them in the appropriate outputs directory
3. Re-run the verification

