# 🕒 2026-02-14-15-35-00
# Project: Hackensack PD Analytics/Benchmark Diagnostics
# Author: R. A. Carucci
# Purpose: Analyze Benchmark source files to identify data coverage issues

import pandas as pd
import os
from pathlib import Path
from datetime import datetime

def analyze_benchmark_files(base_path):
    """
    Analyze all CSV/XLSX files in Benchmark subdirectories
    to identify date coverage and data distribution.
    """
    
    print("="*80)
    print("BENCHMARK SOURCE FILE DIAGNOSTIC")
    print("="*80)
    print(f"Analyzing files in: {base_path}\n")
    
    subdirs = ['use_force', 'show_force', 'vehicle_pursuit']
    results = {}
    
    for subdir in subdirs:
        folder_path = os.path.join(base_path, subdir)
        print(f"\n{'='*80}")
        print(f"ANALYZING: {subdir.upper()}")
        print(f"{'='*80}")
        
        if not os.path.exists(folder_path):
            print(f"❌ Folder not found: {folder_path}")
            results[subdir] = {"error": "Folder not found"}
            continue
        
        # Find all CSV and XLSX files
        files = []
        for ext in ['*.csv', '*.xlsx']:
            files.extend(Path(folder_path).glob(ext))
        
        if not files:
            print(f"❌ No CSV or XLSX files found in: {folder_path}")
            results[subdir] = {"error": "No files found"}
            continue
        
        # Sort by modification date (newest first)
        files_sorted = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
        latest_file = files_sorted[0]
        
        print(f"\n📁 Latest File: {latest_file.name}")
        print(f"   Modified: {datetime.fromtimestamp(latest_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Size: {latest_file.stat().st_size:,} bytes\n")
        
        # Try to load the file
        try:
            if latest_file.suffix == '.csv':
                df = pd.read_csv(latest_file)
            else:
                df = pd.read_excel(latest_file)
            
            print(f"✅ File loaded successfully")
            print(f"   Total Rows: {len(df):,}")
            print(f"   Total Columns: {len(df.columns)}\n")
            
            # Find date column (try common names)
            date_col = None
            for col_name in ['Incident Date', 'Date', 'INCIDENT_DATE', 'incident_date']:
                if col_name in df.columns:
                    date_col = col_name
                    break
            
            if date_col is None:
                print(f"⚠️  Could not find date column. Available columns:")
                for col in df.columns:
                    print(f"     - {col}")
                results[subdir] = {
                    "file": latest_file.name,
                    "rows": len(df),
                    "error": "No date column found"
                }
                continue
            
            print(f"📅 Date Column Found: '{date_col}'")
            
            # Convert to datetime
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            # Remove nulls
            valid_dates = df[date_col].dropna()
            
            if len(valid_dates) == 0:
                print(f"❌ No valid dates found in column '{date_col}'")
                results[subdir] = {
                    "file": latest_file.name,
                    "rows": len(df),
                    "error": "No valid dates"
                }
                continue
            
            # Analyze date range
            min_date = valid_dates.min()
            max_date = valid_dates.max()
            
            print(f"\n📊 DATE RANGE ANALYSIS:")
            print(f"   Earliest Date: {min_date.strftime('%Y-%m-%d')}")
            print(f"   Latest Date:   {max_date.strftime('%Y-%m-%d')}")
            print(f"   Date Span:     {(max_date - min_date).days} days")
            print(f"   Valid Dates:   {len(valid_dates):,} / {len(df):,} rows\n")
            
            # Month-by-month breakdown
            df['YearMonth'] = valid_dates.dt.to_period('M')
            month_counts = df.groupby('YearMonth').size().sort_index()
            
            print(f"📈 MONTHLY DISTRIBUTION:")
            print(f"   {'Month':<15} {'Count':>10}")
            print(f"   {'-'*15} {'-'*10}")
            
            for month, count in month_counts.items():
                marker = "⭐" if str(month).startswith('2025-01') else "  "
                print(f"   {marker} {str(month):<15} {count:>10,}")
            
            # Check for January 2025 concentration
            jan_2025_count = month_counts.get(pd.Period('2025-01'), 0)
            total_count = month_counts.sum()
            jan_pct = (jan_2025_count / total_count * 100) if total_count > 0 else 0
            
            print(f"\n🎯 JANUARY 2025 CONCENTRATION:")
            print(f"   Jan 2025 Records: {jan_2025_count:,}")
            print(f"   Total Records:    {total_count:,}")
            print(f"   Percentage:       {jan_pct:.1f}%")
            
            if jan_pct > 90:
                print(f"\n   ⚠️  WARNING: {jan_pct:.1f}% of data is from January 2025!")
                print(f"   This explains why visuals only show Jan 2025 data.")
            elif jan_pct < 50:
                print(f"\n   ✅ Good distribution - data spans multiple months")
            
            # Store results
            results[subdir] = {
                "file": latest_file.name,
                "rows": len(df),
                "valid_dates": len(valid_dates),
                "min_date": min_date.strftime('%Y-%m-%d'),
                "max_date": max_date.strftime('%Y-%m-%d'),
                "months_covered": len(month_counts),
                "jan_2025_pct": jan_pct,
                "monthly_distribution": month_counts.to_dict()
            }
            
        except Exception as e:
            print(f"❌ Error loading file: {str(e)}")
            results[subdir] = {
                "file": latest_file.name,
                "error": str(e)
            }
    
    # Summary Report
    print(f"\n{'='*80}")
    print("SUMMARY REPORT")
    print(f"{'='*80}\n")
    
    total_issues = 0
    for subdir, data in results.items():
        if "error" in data:
            print(f"❌ {subdir.upper()}: {data['error']}")
            total_issues += 1
        elif data.get('jan_2025_pct', 0) > 90:
            print(f"⚠️  {subdir.upper()}: Data heavily concentrated in Jan 2025 ({data['jan_2025_pct']:.1f}%)")
            total_issues += 1
        else:
            print(f"✅ {subdir.upper()}: Good data distribution ({data['months_covered']} months)")
    
    print(f"\n{'='*80}")
    if total_issues > 0:
        print(f"🚨 ROOT CAUSE IDENTIFIED: {total_issues} of 3 data sources have issues")
        print(f"\nRECOMMENDED ACTION:")
        print(f"  1. Export data for missing months from source system")
        print(f"  2. Add new CSV/XLSX files to respective Benchmark folders")
        print(f"  3. Refresh Power BI queries")
    else:
        print(f"✅ All data sources look good - issue may be in Power BI queries/relationships")
    print(f"{'='*80}\n")
    
    return results


if __name__ == "__main__":
    # Default path - update if needed
    benchmark_path = r"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark"
    
    print("\nBENCHMARK DATA DIAGNOSTIC TOOL")
    print("This script analyzes source CSV/XLSX files to identify data coverage issues.\n")
    
    # Allow user to specify custom path
    user_path = input(f"Enter Benchmark folder path (or press Enter for default):\n{benchmark_path}\n\n> ").strip()
    
    if user_path:
        benchmark_path = user_path
    
    if not os.path.exists(benchmark_path):
        print(f"\n❌ ERROR: Path not found: {benchmark_path}")
        print("Please verify the path and try again.")
    else:
        results = analyze_benchmark_files(benchmark_path)
        
        # Export results to JSON for reference
        import json
        output_file = f"benchmark_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📄 Detailed results saved to: {output_file}")
    
    input("\nPress Enter to exit...")
