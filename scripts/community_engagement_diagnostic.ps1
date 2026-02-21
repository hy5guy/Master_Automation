# 🕒 2026-02-19-14-32-15

# Project Name: Hackensack PD | Data Ops & ETL Remediation

# File Name: scripts/community_engagement_diagnostic.ps1

# Author: R. A. Carucci

# Purpose: Phase 2 diagnostic to analyze record counts, date ranges, and schema for Community Engagement outputs.

cd “C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation”

Write-Host “`n=== COMMUNITY ENGAGEMENT DIAGNOSTIC (PHASE 2) ===” -ForegroundColor Cyan

$ce_dir = “C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date_DropExports”

# 1. Inventory Files

Write-Host “`n1. Locating Output Files in *DropExports:” -ForegroundColor Yellow
$ce_files = Get-ChildItem $ce_dir -Filter “*engagement*” -File | Sort-Object LastWriteTime -Descending
$ce_files | Select-Object Name, @{N=‘Size_KB’;E={[math]::Round($*.Length/1KB,2)}}, LastWriteTime | Format-Table -AutoSize

# 2. Python Data Integrity Check

Write-Host “`n2. Running Record & Schema Audit…” -ForegroundColor Yellow
python -c @”
import pandas as pd
import os
import glob

ce_dir = r’$ce_dir’
files = glob.glob(os.path.join(ce_dir, ‘*engagement*data*.csv’))

if not files:
print(‘ERROR: No engagement data files found to audit.’)
else:
# Check the most recent file
latest_file = max(files, key=os.path.getmtime)
print(f’Auditing Latest File: {os.path.basename(latest_file)}’)

```
df = pd.read_csv(latest_file)

# Check Record Counts
print(f'\n[STATS]')
print(f'- Total Records: {len(df):,}')
print(f'- Unique Categories: {df.iloc[:, 1].nunique() if len(df.columns) > 1 else "N/A"}')

# Check Date Range
date_cols = [col for col in df.columns if 'date' in col.lower()]
if date_cols:
    df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors='coerce')
    valid_dates = df[date_cols[0]].dropna()
    if len(valid_dates) > 0:
        print(f'- Date Range: {valid_dates.min().date()} to {valid_dates.max().date()}')
        print(f'- Expected Range: Should cover 13 months')
    else:
        print('- Date Range: No valid dates found')
else:
    print('- Date Range: Could not identify date column automatically.')

# Check for Nulls/Empty Values
null_counts = df.isnull().sum().sum()
print(f'- Missing Values (Total): {null_counts:,}')

print(f'\n[SCHEMA PREVIEW]')
print(df.columns.tolist())

# Sample first few rows
print(f'\n[DATA SAMPLE - First 3 Rows]')
print(df.head(3).to_string())
```

“@

Write-Host “`n=== DIAGNOSTIC COMPLETE ===” -ForegroundColor Green
Write-Host “Please paste the results above and describe what’s ‘off’:” -ForegroundColor White
Write-Host “  - Missing events or categories?” -ForegroundColor White
Write-Host “  - Wrong date range (should be 13 months)?” -ForegroundColor White
Write-Host “  - Record count anomalies?” -ForegroundColor White