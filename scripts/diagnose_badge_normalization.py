#!/usr/bin/env python3
"""
Diagnose badge number normalization issues between e-ticket exports and Assignment Master.

Checks:
1. E-ticket export "Officer Id" column format (should be 4 digits with leading zeros)
2. Assignment_Master_V2.csv PADDED_BADGE_NUMBER format (should be 4 digits, no floats)
3. Assignment_Master_V2.xlsx PADDED_BADGE_NUMBER format (for comparison)
4. Matching issues between e-ticket Officer Id and Assignment Master PADDED_BADGE_NUMBER
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# Paths
ETICKET_EXPORT = Path(
    r"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\2025\2025_12_eticket_export.csv"
)
ASSIGNMENT_CSV = Path(
    r"C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv"
)
ASSIGNMENT_XLSX = Path(
    r"C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.xlsx"
)

def analyze_eticket_officer_ids(df: pd.DataFrame) -> dict:
    """Analyze Officer Id column in e-ticket export."""
    print("=" * 80)
    print("E-TICKET EXPORT: Officer Id Analysis")
    print("=" * 80)
    
    if "Officer Id" not in df.columns:
        print("ERROR: 'Officer Id' column not found in e-ticket export")
        return {}
    
    officer_ids = df["Officer Id"].astype(str).str.strip()
    
    # Remove empty/null values
    officer_ids = officer_ids[officer_ids != ""]
    officer_ids = officer_ids[officer_ids != "nan"]
    officer_ids = officer_ids[officer_ids.notna()]
    
    total_count = len(officer_ids)
    unique_count = officer_ids.nunique()
    
    print(f"\nTotal Officer Id values: {total_count:,}")
    print(f"Unique Officer Id values: {unique_count:,}")
    
    # Check for floating point numbers
    has_floats = officer_ids.str.contains(r"\.0+$", regex=True, na=False).any()
    if has_floats:
        float_count = officer_ids.str.contains(r"\.0+$", regex=True, na=False).sum()
        print(f"\n⚠️  WARNING: Found {float_count:,} values with floating point format (e.g., '386.0')")
        float_examples = officer_ids[officer_ids.str.contains(r"\.0+$", regex=True, na=False)].head(10)
        print("   Examples:")
        for val in float_examples:
            print(f"     - {val}")
    
    # Check length distribution
    lengths = officer_ids.str.len()
    length_dist = lengths.value_counts().sort_index()
    print(f"\nLength distribution:")
    for length, count in length_dist.items():
        print(f"  {length} characters: {count:,} values")
    
    # Check for leading zeros
    not_padded = officer_ids[~officer_ids.str.match(r"^\d{4}$", na=False)]
    not_padded_count = len(not_padded)
    
    if not_padded_count > 0:
        print(f"\n⚠️  WARNING: {not_padded_count:,} values are NOT 4-digit padded format")
        print("   Examples of non-padded values:")
        examples = not_padded.unique()[:20]
        for val in examples:
            print(f"     - '{val}' (length: {len(str(val))})")
    else:
        print(f"\n[OK] All Officer Id values are 4-digit padded format")
    
    # Check for non-numeric values
    non_numeric = officer_ids[~officer_ids.str.match(r"^\d+\.?\d*$", na=False)]
    if len(non_numeric) > 0:
        print(f"\n⚠️  WARNING: Found {len(non_numeric):,} non-numeric values")
        examples = non_numeric.unique()[:10]
        print("   Examples:")
        for val in examples:
            print(f"     - '{val}'")
    
    return {
        "total": total_count,
        "unique": unique_count,
        "has_floats": has_floats,
        "not_padded_count": not_padded_count,
        "length_distribution": length_dist.to_dict()
    }

def analyze_assignment_csv(df: pd.DataFrame) -> dict:
    """Analyze PADDED_BADGE_NUMBER in Assignment_Master_V2.csv."""
    print("\n" + "=" * 80)
    print("ASSIGNMENT_MASTER_V2.CSV: PADDED_BADGE_NUMBER Analysis")
    print("=" * 80)
    
    if "PADDED_BADGE_NUMBER" not in df.columns:
        print("ERROR: 'PADDED_BADGE_NUMBER' column not found")
        return {}
    
    if "BADGE_NUMBER" not in df.columns:
        print("WARNING: 'BADGE_NUMBER' column not found (cannot compare)")
    
    padded_badges = df["PADDED_BADGE_NUMBER"].astype(str).str.strip()
    
    # Remove empty/null values
    padded_badges = padded_badges[padded_badges != ""]
    padded_badges = padded_badges[padded_badges != "nan"]
    padded_badges = padded_badges[padded_badges.notna()]
    
    total_count = len(padded_badges)
    unique_count = padded_badges.nunique()
    
    print(f"\nTotal PADDED_BADGE_NUMBER values: {total_count:,}")
    print(f"Unique PADDED_BADGE_NUMBER values: {unique_count:,}")
    
    # Check for floating point numbers
    has_floats = padded_badges.str.contains(r"\.0+$", regex=True, na=False).any()
    if has_floats:
        float_count = padded_badges.str.contains(r"\.0+$", regex=True, na=False).sum()
        print(f"\n❌ ERROR: Found {float_count:,} values with floating point format (e.g., '386.0')")
        print("   PADDED_BADGE_NUMBER should be strings like '0386', not '386.0'")
        float_examples = padded_badges[padded_badges.str.contains(r"\.0+$", regex=True, na=False)].head(10)
        print("   Examples:")
        for val in float_examples:
            print(f"     - {val}")
    else:
        print(f"\n[OK] No floating point numbers found")
    
    # Check length distribution
    lengths = padded_badges.str.len()
    length_dist = lengths.value_counts().sort_index()
    print(f"\nLength distribution:")
    for length, count in length_dist.items():
        print(f"  {length} characters: {count:,} values")
    
    # Check for 4-digit format
    not_4digit = padded_badges[~padded_badges.str.match(r"^\d{4}$", na=False)]
    not_4digit_count = len(not_4digit)
    
    if not_4digit_count > 0:
        print(f"\n❌ ERROR: {not_4digit_count:,} values are NOT 4-digit format")
        print("   Examples of non-4-digit values:")
        examples = not_4digit.unique()[:20]
        for val in examples:
            print(f"     - '{val}' (length: {len(str(val))})")
    else:
        print(f"\n[OK] All PADDED_BADGE_NUMBER values are 4-digit format")
    
    # Compare with BADGE_NUMBER if available
    if "BADGE_NUMBER" in df.columns:
        badge_numbers = df["BADGE_NUMBER"].astype(str).str.strip()
        badge_numbers = badge_numbers[badge_numbers != ""]
        badge_numbers = badge_numbers[badge_numbers != "nan"]
        badge_numbers = badge_numbers[badge_numbers.notna()]
        
        # Check if padding is correct
        print(f"\nComparing BADGE_NUMBER vs PADDED_BADGE_NUMBER:")
        mismatches = []
        for idx, row in df.iterrows():
            badge = str(row.get("BADGE_NUMBER", "")).strip()
            padded = str(row.get("PADDED_BADGE_NUMBER", "")).strip()
            
            if badge and padded and badge != "nan" and padded != "nan":
                # Remove .0 if present
                badge_clean = badge.replace(".0", "")
                padded_clean = padded.replace(".0", "")
                
                # Check if padded is correct
                expected_padded = badge_clean.zfill(4)
                if padded_clean != expected_padded:
                    mismatches.append({
                        "badge": badge,
                        "padded": padded,
                        "expected": expected_padded
                    })
        
        if mismatches:
            print(f"  ❌ Found {len(mismatches)} mismatches:")
            for mm in mismatches[:10]:
                print(f"     Badge {mm['badge']} -> PADDED should be '{mm['expected']}' but is '{mm['padded']}'")
        else:
                    print(f"  [OK] All PADDED_BADGE_NUMBER values correctly pad BADGE_NUMBER")
    
    return {
        "total": total_count,
        "unique": unique_count,
        "has_floats": has_floats,
        "not_4digit_count": not_4digit_count
    }

def analyze_assignment_xlsx(df: pd.DataFrame) -> dict:
    """Analyze PADDED_BADGE_NUMBER in Assignment_Master_V2.xlsx (older version)."""
    print("\n" + "=" * 80)
    print("ASSIGNMENT_MASTER_V2.XLSX: PADDED_BADGE_NUMBER Analysis (Older Version)")
    print("=" * 80)
    
    if "PADDED_BADGE_NUMBER" not in df.columns:
        print("ERROR: 'PADDED_BADGE_NUMBER' column not found")
        return {}
    
    padded_badges = df["PADDED_BADGE_NUMBER"].astype(str).str.strip()
    
    # Remove empty/null values
    padded_badges = padded_badges[padded_badges != ""]
    padded_badges = padded_badges[padded_badges != "nan"]
    padded_badges = padded_badges[padded_badges.notna()]
    
    total_count = len(padded_badges)
    unique_count = padded_badges.nunique()
    
    print(f"\nTotal PADDED_BADGE_NUMBER values: {total_count:,}")
    print(f"Unique PADDED_BADGE_NUMBER values: {unique_count:,}")
    
    # Check for floating point numbers
    has_floats = padded_badges.str.contains(r"\.0+$", regex=True, na=False).any()
    if has_floats:
        float_count = padded_badges.str.contains(r"\.0+$", regex=True, na=False).sum()
        print(f"\n⚠️  Found {float_count:,} values with floating point format")
    else:
        print(f"\n[OK] No floating point numbers found")
    
    # Check for 4-digit format
    not_4digit = padded_badges[~padded_badges.str.match(r"^\d{4}$", na=False)]
    not_4digit_count = len(not_4digit)
    
    if not_4digit_count > 0:
        print(f"\n⚠️  {not_4digit_count:,} values are NOT 4-digit format")
    else:
        print(f"\n[OK] All PADDED_BADGE_NUMBER values are 4-digit format")
    
    return {
        "total": total_count,
        "unique": unique_count,
        "has_floats": has_floats,
        "not_4digit_count": not_4digit_count
    }

def compare_matching(eticket_df: pd.DataFrame, assignment_df: pd.DataFrame):
    """Compare matching between e-ticket Officer Id and Assignment Master."""
    print("\n" + "=" * 80)
    print("MATCHING ANALYSIS: E-ticket Officer Id vs Assignment Master")
    print("=" * 80)
    
    if "Officer Id" not in eticket_df.columns:
        print("ERROR: Cannot compare - 'Officer Id' not found in e-ticket")
        return
    
    if "PADDED_BADGE_NUMBER" not in assignment_df.columns:
        print("ERROR: Cannot compare - 'PADDED_BADGE_NUMBER' not found in Assignment Master")
        return
    
    # Normalize e-ticket Officer Id
    eticket_officer_ids = eticket_df["Officer Id"].astype(str).str.strip()
    eticket_officer_ids = eticket_officer_ids.str.replace(".0", "", regex=False)
    eticket_officer_ids = eticket_officer_ids.str.zfill(4)
    eticket_unique = set(eticket_officer_ids.unique())
    
    # Normalize Assignment Master
    assignment_padded = assignment_df["PADDED_BADGE_NUMBER"].astype(str).str.strip()
    assignment_padded = assignment_padded.str.replace(".0", "", regex=False)
    assignment_padded = assignment_padded.str.zfill(4)
    assignment_unique = set(assignment_padded.unique())
    
    # Find matches and mismatches
    matches = eticket_unique & assignment_unique
    eticket_only = eticket_unique - assignment_unique
    assignment_only = assignment_unique - eticket_unique
    
    print(f"\nE-ticket unique Officer Ids: {len(eticket_unique):,}")
    print(f"Assignment Master unique PADDED_BADGE_NUMBER: {len(assignment_unique):,}")
    print(f"\nMatches: {len(matches):,}")
    print(f"E-ticket only (not in Assignment Master): {len(eticket_only):,}")
    print(f"Assignment Master only (not in e-ticket): {len(assignment_only):,}")
    
    if eticket_only:
        print(f"\n⚠️  Officer Ids in e-ticket but NOT in Assignment Master (first 20):")
        for badge in sorted(list(eticket_only))[:20]:
            print(f"     - {badge}")
    
    match_percentage = (len(matches) / len(eticket_unique) * 100) if eticket_unique else 0
    print(f"\nMatch rate: {match_percentage:.1f}%")

def main():
    """Main diagnostic function."""
    print("\n" + "=" * 80)
    print("BADGE NORMALIZATION DIAGNOSTIC")
    print("=" * 80)
    print(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load e-ticket export
    print(f"\nLoading e-ticket export: {ETICKET_EXPORT}")
    if not ETICKET_EXPORT.exists():
        print(f"ERROR: E-ticket export not found: {ETICKET_EXPORT}")
        return
    
    try:
        # Parse e-ticket (semicolon-delimited)
        with ETICKET_EXPORT.open("r", encoding="utf-8", errors="ignore") as f:
            header_line = f.readline().rstrip("\n")
            header = header_line.split(";")
            rows = []
            for line in f:
                line = line.rstrip("\n")
                if not line:
                    continue
                if line.startswith('"'):
                    try:
                        inner = line.split('"', 2)[1]
                    except Exception:
                        inner = line.strip('"')
                    parts = inner.split(";")
                else:
                    parts = line.split(";")
                if len(parts) < 10:
                    continue
                row = dict(zip(header, parts + [""] * max(0, len(header) - len(parts))))
                rows.append(row)
        eticket_df = pd.DataFrame(rows)
        print(f"Loaded {len(eticket_df):,} rows from e-ticket export")
    except Exception as e:
        print(f"ERROR loading e-ticket export: {e}")
        return
    
    # Analyze e-ticket
    eticket_analysis = analyze_eticket_officer_ids(eticket_df)
    
    # Load Assignment Master CSV
    print(f"\nLoading Assignment Master CSV: {ASSIGNMENT_CSV}")
    if not ASSIGNMENT_CSV.exists():
        print(f"ERROR: Assignment Master CSV not found: {ASSIGNMENT_CSV}")
    else:
        try:
            assignment_csv_df = pd.read_csv(ASSIGNMENT_CSV, dtype=str)
            print(f"Loaded {len(assignment_csv_df):,} rows from Assignment Master CSV")
            csv_analysis = analyze_assignment_csv(assignment_csv_df)
            
            # Compare matching
            compare_matching(eticket_df, assignment_csv_df)
        except Exception as e:
            print(f"ERROR loading Assignment Master CSV: {e}")
    
    # Load Assignment Master XLSX (older version)
    print(f"\nLoading Assignment Master XLSX: {ASSIGNMENT_XLSX}")
    if not ASSIGNMENT_XLSX.exists():
        print(f"WARNING: Assignment Master XLSX not found: {ASSIGNMENT_XLSX}")
    else:
        try:
            assignment_xlsx_df = pd.read_excel(ASSIGNMENT_XLSX, dtype=str)
            print(f"Loaded {len(assignment_xlsx_df):,} rows from Assignment Master XLSX")
            xlsx_analysis = analyze_assignment_xlsx(assignment_xlsx_df)
            
            # Compare CSV vs XLSX
            print("\n" + "=" * 80)
            print("COMPARISON: CSV vs XLSX")
            print("=" * 80)
            if 'csv_analysis' in locals() and 'xlsx_analysis' in locals():
                csv_has_issues = csv_analysis.get("has_floats", False) or csv_analysis.get("not_4digit_count", 0) > 0
                xlsx_has_issues = xlsx_analysis.get("has_floats", False) or xlsx_analysis.get("not_4digit_count", 0) > 0
                
                if csv_has_issues and not xlsx_has_issues:
                    print("\n[OK] XLSX version appears to be CORRECT (no issues)")
                    print("  [ERROR] CSV version has issues - should be fixed to match XLSX")
                elif not csv_has_issues and xlsx_has_issues:
                    print("\n[OK] CSV version appears to be CORRECT (no issues)")
                    print("  ⚠️  XLSX version has issues")
                elif csv_has_issues and xlsx_has_issues:
                    print("\n⚠️  Both versions have issues")
                else:
                    print("\n[OK] Both versions appear correct")
        except Exception as e:
            print(f"ERROR loading Assignment Master XLSX: {e}")
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
