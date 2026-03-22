# 🕒 2026-02-19-14-34-20

# Project Name: Hackensack PD | Data Ops & ETL Remediation

# File Name: scripts/community_engagement_data_flow_check.py

# Author: R. A. Carucci

# Purpose: Analyze Community Engagement ETL data flow from source to output, validating 13-month rolling window.

import pandas as pd
import os
import glob
from pathlib import Path
from datetime import datetime, timedelta

# Configuration

import sys, os, json as _json
from pathlib import Path as _Path

def _get_drop_path() -> str:
    _cfg = _Path(__file__).resolve().parent.parent / "config" / "scripts.json"
    try:
        with open(_cfg, encoding="utf-8") as _f:
            return _json.load(_f)["settings"]["powerbi_drop_path"]
    except Exception:
        return r"C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Data\_DropExports"

SOURCE_DIR = r’C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Community_Engagment’
OUTPUT_DIR = _get_drop_path()

print(”=” * 70)
print(“COMMUNITY ENGAGEMENT DATA FLOW DIAGNOSTIC”)
print(”=” * 70)

# 1. Check Source Files

print(”\n[1] SOURCE FILES CHECK”)
print(”-” * 70)
if os.path.exists(SOURCE_DIR):
source_files = list(Path(SOURCE_DIR).rglob(”*.csv”)) + list(Path(SOURCE_DIR).rglob(”*.xlsx”))
print(f”Source Directory: {SOURCE_DIR}”)
print(f”Files Found: {len(source_files)}”)
for f in source_files[:10]:  # Show first 10
print(f”  - {f.name} ({f.stat().st_size / 1024:.1f} KB, Modified: {datetime.fromtimestamp(f.stat().st_mtime).strftime(’%Y-%m-%d %H:%M’)})”)
else:
print(f”❌ SOURCE DIRECTORY NOT FOUND: {SOURCE_DIR}”)

# 2. Check Output Files

print(”\n[2] OUTPUT FILES IN _DROPEXPORTS”)
print(”-” * 70)
engagement_files = glob.glob(os.path.join(OUTPUT_DIR, “*engagement*.csv”))
print(f”Engagement Files Found: {len(engagement_files)}”)

if engagement_files:
for file in sorted(engagement_files, key=os.path.getmtime, reverse=True):
file_size = os.path.getsize(file) / 1024
file_mtime = datetime.fromtimestamp(os.path.getmtime(file))
print(f”  - {os.path.basename(file)}”)
print(f”    Size: {file_size:.1f} KB | Modified: {file_mtime.strftime(’%Y-%m-%d %H:%M:%S’)}”)

```
    # Quick preview of most recent file
    if file == engagement_files[0]:
        try:
            df = pd.read_csv(file, nrows=5)
            print(f"    Columns: {list(df.columns)}")
            print(f"    Sample Records: {len(df)} (showing first 5)")
        except Exception as e:
            print(f"    ❌ Error reading file: {e}")
```

else:
print(“❌ NO ENGAGEMENT OUTPUT FILES FOUND”)

# 3. Date Range Validation (13-Month Rolling Window)

print(”\n[3] 13-MONTH ROLLING WINDOW VALIDATION”)
print(”-” * 70)
if engagement_files:
latest_file = max(engagement_files, key=os.path.getmtime)
print(f”Checking: {os.path.basename(latest_file)}”)

```
try:
    df = pd.read_csv(latest_file)
    date_cols = [col for col in df.columns if 'date' in col.lower() or 'month' in col.lower()]
    
    if date_cols:
        date_col = date_cols[0]
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        valid_dates = df[date_col].dropna()
        
        if len(valid_dates) > 0:
            min_date = valid_dates.min()
            max_date = valid_dates.max()
            month_span = (max_date.year - min_date.year) * 12 + (max_date.month - min_date.month) + 1
            
            print(f"  Date Column: {date_col}")
            print(f"  Date Range: {min_date.date()} to {max_date.date()}")
            print(f"  Month Span: {month_span} months")
            
            if month_span == 13:
                print(f"  ✅ VALID: Exactly 13 months of data")
            elif month_span < 13:
                print(f"  ⚠️  WARNING: Only {month_span} months (expected 13)")
            else:
                print(f"  ⚠️  WARNING: {month_span} months (expected 13)")
                
            # Show monthly breakdown
            print(f"\n  Monthly Record Counts:")
            monthly = df.groupby(df[date_col].dt.to_period('M')).size()
            for period, count in monthly.items():
                print(f"    {period}: {count:,} records")
        else:
            print(f"  ❌ No valid dates in column: {date_col}")
    else:
        print(f"  ❌ No date column found. Columns: {list(df.columns)}")
        
except Exception as e:
    print(f"  ❌ Error analyzing file: {e}")
```

# 4. Schema Comparison

print(”\n[4] SCHEMA CHECK”)
print(”-” * 70)
print(“Expected Columns for Community Engagement:”)
expected_cols = [
“Date/Month Column”,
“Category/Activity Type”,
“Count/Frequency”,
“Location (Optional)”,
“Officer/Unit (Optional)”
]
for col in expected_cols:
print(f”  - {col}”)

print(”\n” + “=” * 70)
print(“DIAGNOSTIC COMPLETE”)
print(”=” * 70)
print(”\nNext Steps:”)
print(”  1. Review date range - should cover exactly 13 months”)
print(”  2. Check for missing categories or anomalous counts”)
print(”  3. Verify ETL script is using correct source data”)
print(”  4. Compare output schema to Power BI visual expectations”)