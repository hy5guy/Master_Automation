# 🕒 2026-02-18-23-28-16
# # Response_Times/process_cad_data_13month_rolling.py
# # Author: R. A. Carucci
# # Purpose: Implement explicit sort by Time Out to ensure first-arriving unit is selected during deduplication.

import pandas as pd
# Community Engagement Deep-Dive Diagnostic
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"

Write-Host "`n=== COMMUNITY ENGAGEMENT DIAGNOSTIC (PHASE 2) ===" -ForegroundColor Cyan

# Define standard paths
$ce_dir = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports"

# 1. Inventory Files
Write-Host "`n1. Locating Output Files in _DropExports:" -ForegroundColor Yellow
$ce_files = Get-ChildItem $ce_dir -Filter "*engagement*" -File | Sort-Object LastWriteTime -Descending
$ce_files | Select-Object Name, @{N='Size_KB';E={[math]::Round($_.Length/1KB,2)}}, LastWriteTime | Format-Table -AutoSize

# 2. Python Data Integrity Check
Write-Host "2. Running Record & Schema Audit..." -ForegroundColor Yellow
python -c @"
import pandas as pd
import os
import glob

ce_dir = r'$ce_dir'
files = glob.glob(os.path.join(ce_dir, '*engagement*data*.csv'))

if not files:
    print('ERROR: No engagement data files found to audit.')
else:
    # Check the most recent file
    latest_file = max(files, key=os.path.getmtime)
    print(f'Auditing Latest File: {os.path.basename(latest_file)}')
    
    df = pd.read_csv(latest_file)
    
    # Check Record Counts
    print(f'\n[STATS]')
    print(f'- Total Records: {len(df)}')
    print(f'- Unique Categories: {df.iloc[:, 1].nunique() if len(df.columns) > 1 else "N/A"}')
    
    # Check Date Range
    # Attempting to find date column automatically
    date_cols = [col for col in df.columns if 'date' in col.lower()]
    if date_cols:
        df[date_cols[0]] = pd.to_datetime(df[date_cols[0]])
        print(f'- Date Range: {df[date_cols[0]].min().date()} to {df[date_cols[0]].max().date()}')
    else:
        print('- Date Range: Could not identify date column automatically.')

    # Check for Nulls/Empty Values
    null_counts = df.isnull().sum().sum()
    print(f'- Missing Values (Total): {null_counts}')

    print(f'\n[SCHEMA PREVIEW]')
    print(df.columns.tolist())

"@

Write-Host "`n=== DIAGNOSTIC COMPLETE ===" -ForegroundColor Green
Write-Host "Please paste the results above and describe what looks 'off' (e.g., missing events, wrong dates)." -ForegroundColor White