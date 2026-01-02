#!/usr/bin/env python3
"""
Diagnose missing months in summons staging workbook.

Checks:
1. What months are in the staging workbook
2. What months should be there (based on backfill + current month)
3. Identifies missing months
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# Paths
STAGING_WORKBOOK = Path(
    r"C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx"
)
BACKFILL_ROOT = Path(
    r"C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill"
)
E_TICKET_EXPORT = Path(
    r"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket"
)

def get_months_in_staging() -> pd.Series:
    """Get month distribution from staging workbook."""
    print("=" * 80)
    print("CHECKING STAGING WORKBOOK")
    print("=" * 80)
    
    if not STAGING_WORKBOOK.exists():
        print(f"ERROR: Staging workbook not found: {STAGING_WORKBOOK}")
        return pd.Series(dtype=object)
    
    df = pd.read_excel(STAGING_WORKBOOK, sheet_name="Summons_Data")
    months = df["Month_Year"].value_counts().sort_index()
    
    print(f"\nStaging workbook: {STAGING_WORKBOOK.name}")
    print(f"Total rows: {len(df):,}")
    print(f"Unique months: {df['Month_Year'].nunique()}")
    print(f"\nMonth distribution:")
    for month, count in months.items():
        print(f"  {month}: {count:,} rows")
    
    print(f"\nMonth range: {months.index.min()} to {months.index.max()}")
    
    return months

def get_expected_months() -> set:
    """Get expected months from backfill + current month exports."""
    print("\n" + "=" * 80)
    print("CHECKING EXPECTED MONTHS (Backfill + Current Month)")
    print("=" * 80)
    
    expected = set()
    
    # Check backfill directories
    if BACKFILL_ROOT.exists():
        print(f"\nChecking backfill root: {BACKFILL_ROOT}")
        for backfill_dir in BACKFILL_ROOT.glob("*/summons"):
            print(f"\n  Found backfill: {backfill_dir}")
            for csv_file in backfill_dir.glob("*.csv"):
                if "Department-Wide" in csv_file.name:
                    print(f"    Reading: {csv_file.name}")
                    try:
                        df = pd.read_csv(csv_file, encoding="utf-8-sig")
                        # Check for month columns (MM-YY format)
                        month_cols = [c for c in df.columns if c and "-" in str(c) and len(str(c)) == 5]
                        for col in month_cols:
                            if col not in ["TYPE", "Total"]:
                                expected.add(col)
                        print(f"      Found months: {sorted(month_cols)}")
                    except Exception as e:
                        print(f"      ERROR reading {csv_file.name}: {e}")
    
    # Check current month e-ticket exports
    # New structure: YYYY/YYYY_MM_eticket_export.csv (e.g., 2025/2025_12_eticket_export.csv)
    if E_TICKET_EXPORT.exists():
        print(f"\nChecking e-ticket exports: {E_TICKET_EXPORT}")
        # Search in year subdirectories (2025, 2026, etc.)
        for year_dir in E_TICKET_EXPORT.glob("[0-9][0-9][0-9][0-9]"):
            if year_dir.is_dir():
                for csv_file in year_dir.glob("*.csv"):
                    # Extract month from filename (e.g., 2025_12_eticket_export.csv -> 12-25)
                    parts = csv_file.stem.split("_")
                    if len(parts) >= 3 and parts[2] == "eticket" and parts[3] == "export":
                        year_part = parts[0]  # Full year (e.g., "2025")
                        month_part = parts[1]  # Month (e.g., "12")
                        if len(year_part) == 4 and len(month_part) == 2:
                            # Convert to MM-YY format (e.g., 12-25)
                            year_short = year_part[2:]  # Last 2 digits
                            month_year = f"{month_part}-{year_short}"
                            expected.add(month_year)
                            print(f"    Found e-ticket export: {csv_file.name} -> {month_year}")
    
    print(f"\nExpected months (from backfill + exports): {sorted(expected)}")
    return expected

def identify_missing_months(staging_months: pd.Series, expected_months: set) -> dict:
    """Identify missing months."""
    print("\n" + "=" * 80)
    print("MISSING MONTHS ANALYSIS")
    print("=" * 80)
    
    staging_set = set(staging_months.index)
    missing = expected_months - staging_set
    extra = staging_set - expected_months
    
    print(f"\nMonths in staging: {len(staging_set)}")
    print(f"Months expected: {len(expected_months)}")
    print(f"Missing months: {len(missing)}")
    print(f"Extra months (in staging but not expected): {len(extra)}")
    
    if missing:
        print(f"\n⚠️  MISSING MONTHS:")
        for month in sorted(missing):
            print(f"  - {month}")
    
    if extra:
        print(f"\nℹ️  EXTRA MONTHS (in staging but not in expected):")
        for month in sorted(extra):
            print(f"  - {month}")
    
    # Check for gaps in sequence
    print(f"\n" + "=" * 80)
    print("CHECKING FOR GAPS IN MONTH SEQUENCE")
    print("=" * 80)
    
    # Parse months to find gaps
    all_months = sorted(staging_set | expected_months)
    if all_months:
        print(f"\nAll months (staging + expected): {all_months}")
        
        # Check for sequential gaps
        gaps = []
        for i in range(len(all_months) - 1):
            current = all_months[i]
            next_month = all_months[i + 1]
            
            # Parse MM-YY
            try:
                curr_parts = current.split("-")
                next_parts = next_month.split("-")
                curr_m = int(curr_parts[0])
                curr_y = int(curr_parts[1])
                next_m = int(next_parts[0])
                next_y = int(next_parts[1])
                
                # Calculate expected next month
                if curr_m == 12:
                    exp_m = 1
                    exp_y = curr_y + 1
                else:
                    exp_m = curr_m + 1
                    exp_y = curr_y
                
                # Check if there's a gap
                if next_m != exp_m or next_y != exp_y:
                    gap_month = f"{exp_m:02d}-{exp_y:02d}"
                    gaps.append(gap_month)
                    print(f"  ⚠️  Gap detected: {current} -> {next_month} (missing {gap_month})")
            except:
                pass
        
        if gaps:
            print(f"\n⚠️  GAPS FOUND: {gaps}")
        else:
            print(f"\n✓ No gaps in month sequence")
    
    return {
        "missing": sorted(missing),
        "extra": sorted(extra),
        "gaps": gaps if 'gaps' in locals() else []
    }

def main():
    """Main diagnostic function."""
    print("\n" + "=" * 80)
    print("SUMMONS MISSING MONTHS DIAGNOSTIC")
    print("=" * 80)
    print(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get months from staging
    staging_months = get_months_in_staging()
    
    # Get expected months
    expected_months = get_expected_months()
    
    # Identify missing
    if len(staging_months) > 0 and len(expected_months) > 0:
        results = identify_missing_months(staging_months, expected_months)
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Months in staging workbook: {len(staging_months)}")
        print(f"Expected months: {len(expected_months)}")
        print(f"Missing months: {len(results['missing'])}")
        if results['missing']:
            print(f"  → {', '.join(results['missing'])}")
        if results['gaps']:
            print(f"Gaps in sequence: {len(results['gaps'])}")
            print(f"  → {', '.join(results['gaps'])}")
    else:
        print("\n⚠️  Could not complete comparison - missing data")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. If months are missing, check if ETL script needs to be run")
    print("2. Verify backfill data exists for missing months")
    print("3. Check if e-ticket exports exist for 10-25 and 11-25")
    print("4. Run Summons ETL script to merge backfill + current month data")
    print("=" * 80)

if __name__ == "__main__":
    main()


