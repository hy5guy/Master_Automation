#!/usr/bin/env python3
"""
Diagnose why WG2 is not being populated from Assignment_Master_V2.csv in summons data.

Checks:
1. If Assignment_Master_V2.csv is being loaded correctly
2. If badge matching is working
3. If WG2 is being populated from the assignment master
4. Why WG2_ASSIGN has values but WG2 is null
"""

import pandas as pd
from pathlib import Path
import sys

def main():
    # Paths
    staging_file = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx")
    assignment_master = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv")
    
    print("=" * 80)
    print("SUMMONS ASSIGNMENT MAPPING DIAGNOSTIC")
    print("=" * 80)
    
    # Load staging workbook
    if not staging_file.exists():
        print(f"❌ Staging file not found: {staging_file}")
        return 1
    
    print(f"\n✓ Loading staging workbook: {staging_file.name}")
    df = pd.read_excel(staging_file, sheet_name="Summons_Data")
    print(f"  Total rows: {len(df):,}")
    
    # Check WG2 status
    print(f"\n📊 WG2 Column Status:")
    wg2_null = df["WG2"].isna().sum()
    wg2_empty = (df["WG2"].astype(str).str.strip() == "").sum()
    wg2_has_value = len(df) - wg2_null - wg2_empty
    
    print(f"  Null: {wg2_null:,}")
    print(f"  Empty string: {wg2_empty:,}")
    print(f"  Has value: {wg2_has_value:,}")
    
    # Check WG2_ASSIGN status
    if "WG2_ASSIGN" in df.columns:
        print(f"\n📊 WG2_ASSIGN Column Status:")
        wg2_assign_null = df["WG2_ASSIGN"].isna().sum()
        wg2_assign_empty = (df["WG2_ASSIGN"].astype(str).str.strip() == "").sum()
        wg2_assign_has_value = len(df) - wg2_assign_null - wg2_assign_empty
        
        print(f"  Null: {wg2_assign_null:,}")
        print(f"  Empty string: {wg2_assign_empty:,}")
        print(f"  Has value: {wg2_assign_has_value:,}")
        
        # Check if WG2_ASSIGN has values where WG2 is null
        if wg2_assign_has_value > 0:
            mask = df["WG2"].isna() & df["WG2_ASSIGN"].notna()
            rows_with_wg2_assign_but_no_wg2 = mask.sum()
            print(f"\n⚠️  Rows where WG2_ASSIGN has value but WG2 is null: {rows_with_wg2_assign_but_no_wg2:,}")
            
            if rows_with_wg2_assign_but_no_wg2 > 0:
                print("\n  Sample rows:")
                sample = df[mask][["PADDED_BADGE_NUMBER", "OFFICER_DISPLAY_NAME", "WG2", "WG2_ASSIGN"]].head(10)
                print(sample.to_string())
    else:
        print("\n⚠️  WG2_ASSIGN column not found in staging data")
    
    # Load Assignment Master
    if not assignment_master.exists():
        print(f"\n❌ Assignment Master not found: {assignment_master}")
        return 1
    
    print(f"\n✓ Loading Assignment Master: {assignment_master.name}")
    am = pd.read_csv(assignment_master)
    print(f"  Total rows: {len(am):,}")
    print(f"  Columns: {', '.join(am.columns[:10])}...")
    
    # Check badge matching
    print(f"\n🔍 Badge Matching Analysis:")
    
    # Get unique badges from summons data
    summons_badges = set(df["PADDED_BADGE_NUMBER"].dropna().astype(str).str.strip())
    am_badges = set(am["PADDED_BADGE_NUMBER"].dropna().astype(str).str.strip())
    
    print(f"  Unique badges in summons data: {len(summons_badges):,}")
    print(f"  Unique badges in Assignment Master: {len(am_badges):,}")
    
    # Find badges in summons but not in assignment master
    missing_badges = summons_badges - am_badges
    print(f"  Badges in summons but NOT in Assignment Master: {len(missing_badges):,}")
    
    if len(missing_badges) > 0:
        print(f"\n  Top 20 missing badges:")
        for badge in sorted(list(missing_badges))[:20]:
            count = len(df[df["PADDED_BADGE_NUMBER"].astype(str).str.strip() == badge])
            print(f"    {badge}: {count:,} rows")
    
    # Check if badges that have WG2_ASSIGN but not WG2 are in Assignment Master
    if "WG2_ASSIGN" in df.columns:
        mask = df["WG2"].isna() & df["WG2_ASSIGN"].notna()
        problem_rows = df[mask].copy()
        
        if len(problem_rows) > 0:
            print(f"\n🔍 Analyzing {len(problem_rows):,} rows with WG2_ASSIGN but no WG2:")
            problem_badges = set(problem_rows["PADDED_BADGE_NUMBER"].dropna().astype(str).str.strip())
            in_am = problem_badges & am_badges
            not_in_am = problem_badges - am_badges
            
            print(f"  Badges in Assignment Master: {len(in_am):,}")
            print(f"  Badges NOT in Assignment Master: {len(not_in_am):,}")
            
            if len(in_am) > 0:
                print(f"\n  ⚠️  These badges ARE in Assignment Master but WG2 is still null:")
                for badge in sorted(list(in_am))[:10]:
                    am_row = am[am["PADDED_BADGE_NUMBER"].astype(str).str.strip() == badge]
                    if len(am_row) > 0:
                        wg2_value = am_row.iloc[0].get("WG2", "N/A")
                        print(f"    Badge {badge}: WG2 in AM = '{wg2_value}'")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATION:")
    print("=" * 80)
    print("The ETL script should:")
    print("1. Load Assignment_Master_V2.csv")
    print("2. Join on PADDED_BADGE_NUMBER (normalized to 4-digit string)")
    print("3. Populate WG2, WG1, WG3, etc. from Assignment Master")
    print("4. If WG2_ASSIGN exists but WG2 is null, copy WG2_ASSIGN to WG2")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

