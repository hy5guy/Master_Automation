# ETL Verification Summary Report

**Generated:** 2026-01-13 18:21:09

**Current Month:** 2025_12

**Backfill Month:** 2025_11

**Duration:** 0.1 seconds

## Overall Statistics

| Metric | Value |
|--------|-------|
| Total Verifications | 2 |
| Passed | 0 |
| Failed | 0 |
| Skipped | 0 |
| Errors | 0 |
| Overall Pass Rate | 0.0% |

## Individual Verifications

| Priority | Name | Status | Pass Rate | Issues | Report |
|----------|------|--------|-----------|--------|--------|
| 1 | Overtime & Time Off | [ERROR] ERROR | 100.0% | 0 | [OVERTIME_TIMEOFF_MONTHLY_VERIFICATION_REPORT.md](C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\verification_reports\OVERTIME_TIMEOFF_MONTHLY_VERIFICATION_REPORT.md) |
| 2 | Arrests | [ERROR] ERROR | 100.0% | 3 | [ARRESTS_MONTHLY_VERIFICATION_REPORT.md](C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\verification_reports\ARRESTS_MONTHLY_VERIFICATION_REPORT.md) |

## Detailed Issues

### Arrests

**Status:** PASS

**Issues:**

- {'severity': 'ERROR', 'category': 'File Parsing', 'description': 'Failed to parse C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\Master_Automation\\outputs\\2025_12_Arrest Distribution by Local, State & Out of State.csv: 3 columns passed, passed data had 4 columns'}
- {'severity': 'ERROR', 'category': 'File Parsing', 'description': 'Failed to parse C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\00_dev\\projects\\PowerBI_Date\\Backfill\\2025_11\\arrest\\2025_11_Arrest Distribution by Local, State & Out of State.csv: 3 columns passed, passed data had 4 columns'}
- {'severity': 'ERROR', 'category': 'File Loading', 'description': 'Both current and backfill missing for Arrest Distribution by Local, State & Out of State.csv'}

## Recommendations

