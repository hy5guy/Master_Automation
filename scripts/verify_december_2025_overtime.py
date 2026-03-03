"""
December 2025 Overtime & Time Off Verification Script

Verifies that Python ETL scripts correctly processed December 2025 data by:
1. Comparing December export with November backfill for overlapping months
2. Independently processing December 2025 raw exports
3. Validating processing logic
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
from typing import Dict, List, Tuple
from datetime import datetime

# ===== FILE PATHS =====
DEC_EXPORT = r"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\2025_12_Monthly Accrual and Usage Summary.csv"
NOV_BACKFILL = r"C:\Users\carucci_r\OneDrive - City of Hackensack\00_dev\projects\PowerBI_Date\Backfill\2025_11\vcs_time_report\2025_11_Monthly Accrual and Usage Summary.csv"
DEC_OT_RAW = r"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Overtime\export\month\2025\2025_12_otactivity.xlsx"
DEC_TO_RAW = r"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Time_Off\export\month\2025\2025_12_timeoffactivity.xlsx"
PERSONNEL = r"C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\Assignment_Master_V2.csv"

TOLERANCE = 0.01  # Hours tolerance for comparison

# ===== PARSE FILES =====
def parse_december_export(filepath: str) -> pd.DataFrame:
    """Parse December export (long format)."""
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    return df

def parse_november_backfill(filepath: str) -> pd.DataFrame:
    """Parse November backfill (wide format) and convert to long format."""
    # The file has each row as a quoted string with comma-separated values
    # Read as text and parse manually
    rows = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Remove outer quotes and split by comma
            line = line.strip('"')
            values = [v.strip() for v in line.split(',')]
            rows.append(values)

    if not rows:
        return pd.DataFrame(columns=['Time Category', 'Sum of Value', 'PeriodLabel'])

    # First row is header
    header = rows[0]
    data_rows = rows[1:]

    # Convert to DataFrame (wide format)
    df = pd.DataFrame(data_rows, columns=header)

    # Convert wide to long format
    time_category_col = 'Time Category'
    month_cols = [col for col in header if col != time_category_col and col not in ['Sum of 11-25', '']]

    long_rows = []
    for _, row in df.iterrows():
        category = row[time_category_col]
        for month_col in month_cols:
            if month_col in row and row[month_col]:
                try:
                    value = float(row[month_col])
                    long_rows.append({
                        'Time Category': category,
                        'Sum of Value': value,
                        'PeriodLabel': month_col
                    })
                except (ValueError, TypeError):
                    continue

    return pd.DataFrame(long_rows)

# ===== COMPARISON =====
def compare_exports(dec_df: pd.DataFrame, nov_df: pd.DataFrame) -> Dict:
    """Compare December export with November backfill for overlapping months."""

    # Get overlapping months (both should have 11-24 through 11-25)
    dec_months = set(dec_df['PeriodLabel'].unique())
    nov_months = set(nov_df['PeriodLabel'].unique())
    overlap_months = sorted(dec_months & nov_months)

    print(f"\n[INFO] December export has {len(dec_months)} months: {sorted(dec_months)}")
    print(f"[INFO] November backfill has {len(nov_months)} months: {sorted(nov_months)}")
    print(f"[INFO] Overlapping months ({len(overlap_months)}): {overlap_months}")

    results = {
        'comparisons': [],
        'matches': 0,
        'differences': 0,
        'total': 0
    }

    # Compare each category for each overlapping month
    categories = sorted(set(dec_df['Time Category'].unique()) | set(nov_df['Time Category'].unique()))

    for category in categories:
        for month in overlap_months:
            dec_val = dec_df[(dec_df['Time Category'] == category) &
                            (dec_df['PeriodLabel'] == month)]['Sum of Value'].values
            nov_val = nov_df[(nov_df['Time Category'] == category) &
                            (nov_df['PeriodLabel'] == month)]['Sum of Value'].values

            dec_value = float(dec_val[0]) if len(dec_val) > 0 else 0.0
            nov_value = float(nov_val[0]) if len(nov_val) > 0 else 0.0

            diff = abs(dec_value - nov_value)
            match = diff <= TOLERANCE

            results['comparisons'].append({
                'Category': category,
                'Month': month,
                'December_Value': dec_value,
                'November_Value': nov_value,
                'Difference': dec_value - nov_value,
                'Abs_Difference': diff,
                'Match': match
            })

            results['total'] += 1
            if match:
                results['matches'] += 1
            else:
                results['differences'] += 1

    return results

# ===== INDEPENDENT PROCESSING =====
def normalize_status(s: str) -> str:
    """Normalize status string."""
    return re.sub(r"[^a-z0-9]", "", (s or "").strip().lower())

def normalize_name(s: str) -> str:
    """Normalize employee name."""
    s = (str(s) if pd.notna(s) else "").upper().strip()

    # Handle "LastName, FirstName" format
    if "," in s:
        parts = [p.strip() for p in s.split(",")]
        if len(parts) == 2 and parts[0] and parts[1]:
            s = f"{parts[1]} {parts[0]}"

    # Remove titles/ranks
    titles = ["C.O.", "P.O.", "SGT.", "LT.", "CAPT.", "CHIEF", "DET.",
              "SPO II", "SPO III", "HCOP", "DPW", "CLK", "PEO", "TM", "PLA"]
    for title in titles:
        s = s.replace(title, "").strip()

    # Remove badge numbers (3-4 digits at end)
    s = re.sub(r"\s+\d{3,4}$", "", s)

    # Remove extra characters and normalize spaces
    s = re.sub(r"[^A-Z\s]", "", s)
    return re.sub(r"\s+", " ", s).strip()

def classify_overtime_category(pay_type: str) -> Tuple[str, str]:
    """Classify overtime transaction as OT or COMP and extract rate."""
    pay_type = str(pay_type).lower()

    # COMP detection
    if any(term in pay_type for term in ['comp', 'compensatory', 'ct']):
        # Extract rate if present
        if '2.5' in pay_type or '250%' in pay_type:
            return 'COMP', '25'
        elif '2.0' in pay_type or '200%' in pay_type or 'double' in pay_type:
            return 'COMP', '20'
        elif '1.5' in pay_type or '150%' in pay_type:
            return 'COMP', '15'
        elif '1.0' in pay_type or '100%' in pay_type:
            return 'COMP', '10'
        return 'COMP', ''

    # OT detection (including cash with rate >= 1.5)
    ot_terms = ['overtime', 'o.t.', 'o/t', 'dt', 'double time', 'doubletime']
    if any(term in pay_type for term in ot_terms):
        # Extract rate
        if '2.5' in pay_type or '250%' in pay_type:
            return 'OT', '25'
        elif '2.0' in pay_type or '200%' in pay_type or 'double' in pay_type or 'dt' in pay_type:
            return 'OT', '20'
        elif '1.5' in pay_type or '150%' in pay_type:
            return 'OT', '15'
        return 'OT', '15'  # Default OT rate

    # Cash with rate >= 1.5
    if 'cash' in pay_type:
        if any(rate in pay_type for rate in ['1.5', '2.0', '2.5', '150%', '200%', '250%']):
            if '2.5' in pay_type or '250%' in pay_type:
                return 'OT', '25'
            elif '2.0' in pay_type or '200%' in pay_type:
                return 'OT', '20'
            elif '1.5' in pay_type or '150%' in pay_type:
                return 'OT', '15'

    return '', ''

def classify_timeoff_usage(reason: str, comments: str) -> str:
    """Classify time off usage by category (reason-first logic)."""
    reason = str(reason).lower() if pd.notna(reason) else ""
    comments = str(comments).lower() if pd.notna(comments) else ""

    # Reason-first patterns
    if reason.startswith('sick'):
        return 'Sick'
    if reason.startswith('sat'):
        return 'SAT'
    if reason.startswith('comp'):
        return 'Comp Used'
    if 'military' in reason or reason.startswith('mil'):
        return 'Military'
    if any(term in reason for term in ['vac', 'vacation', 'annual', 'pto', 'personal']):
        return 'Vacation'

    # Fallback to comments/text
    text = f"{reason} {comments}".lower()
    if any(term in text for term in ['sick', 'ill', 'illness', 'sck']):
        return 'Sick'
    if 'sat' in text:
        return 'SAT'
    if any(term in text for term in ['comp', 'compensatory', 'comp time used', 'ct used']):
        return 'Comp Used'
    if any(term in text for term in ['military', 'mil']):
        return 'Military'
    if any(term in text for term in ['vacation', 'annual', 'pto', 'personal']):
        return 'Vacation'
    if any(term in text for term in ['iod', 'injured on duty', 'injury on duty']):
        return 'IOD'

    return 'Unknown'

def load_personnel(filepath: str) -> pd.DataFrame:
    """Load personnel file for sworn/nonsworn classification."""
    # Check file extension
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath, engine='openpyxl')

    # Find name and title columns
    name_col = None
    title_col = None
    for col in df.columns:
        col_lower = col.lower()
        if 'full_name' in col_lower or 'fullname' in col_lower or 'name' in col_lower:
            name_col = col
        if 'title' in col_lower or 'rank' in col_lower:
            title_col = col

    if not name_col or not title_col:
        raise ValueError("Cannot find name/title columns in personnel file")

    df = df[[name_col, title_col]].copy()
    df.columns = ['FullName', 'Title']
    df['FullName_norm'] = df['FullName'].apply(normalize_name)

    # Classify as Sworn/NonSworn
    sworn_titles = {"P.O.", "CHIEF", "LT.", "SPO III", "SGT.", "DET.", "CAPT."}
    nonsworn_titles = {"SPO II", "HCOP", "C.O.", "DPW", "CLK", "PEO", "TM", "PLA"}

    def classify_title(title):
        title = str(title).strip().upper()
        if title in sworn_titles:
            return "Sworn"
        elif title in nonsworn_titles:
            return "NonSworn"
        return "Unknown"

    df['MemberClass'] = df['Title'].apply(classify_title)

    return df[['FullName_norm', 'Title', 'MemberClass']]

def process_december_raw(ot_file: str, to_file: str, personnel_file: str) -> Dict:
    """Independently process December 2025 raw exports."""

    print("\n[INFO] Processing December 2025 raw exports...")

    # Load personnel
    personnel = load_personnel(personnel_file)
    print(f"[INFO] Loaded {len(personnel)} personnel records")

    # ===== PROCESS OVERTIME =====
    ot_df = pd.read_excel(ot_file, engine='openpyxl')
    print(f"[INFO] Loaded {len(ot_df)} overtime records")

    # Filter to approved only
    if 'Status' in ot_df.columns:
        ot_df['Status_norm'] = ot_df['Status'].astype(str).apply(normalize_status)
        approved_statuses = {'approved', 'approvedwstip', 'approvedwithstip',
                            'approvedwithstipend', 'approvedwithstipulation'}
        ot_df = ot_df[ot_df['Status_norm'].isin(approved_statuses)]
        print(f"[INFO] {len(ot_df)} approved overtime records")

    # Extract and classify
    ot_df['Employee_norm'] = ot_df['Employee'].apply(normalize_name)
    ot_df['Date'] = pd.to_datetime(ot_df['Date'], errors='coerce')
    ot_df['Hours'] = pd.to_numeric(ot_df['Hours'], errors='coerce').fillna(0)

    # Classify OT vs COMP
    ot_df[['Category', 'Rate']] = ot_df['Pay Type'].apply(
        lambda x: pd.Series(classify_overtime_category(x))
    )

    # Filter to December 2025 only (12-25)
    ot_df_dec = ot_df[(ot_df['Date'].dt.year == 2025) & (ot_df['Date'].dt.month == 12)].copy()
    print(f"[INFO] {len(ot_df_dec)} overtime records in December 2025")

    # Merge with personnel for sworn/nonsworn classification
    ot_df_dec = ot_df_dec.merge(personnel, left_on='Employee_norm', right_on='FullName_norm', how='left')
    ot_df_dec['MemberClass'] = ot_df_dec['MemberClass'].fillna('Unknown')

    # Calculate accruals by category and class
    comp_sworn = ot_df_dec[(ot_df_dec['Category'] == 'COMP') &
                           (ot_df_dec['MemberClass'] == 'Sworn')]['Hours'].sum()
    comp_nonsworn = ot_df_dec[(ot_df_dec['Category'] == 'COMP') &
                              (ot_df_dec['MemberClass'] == 'NonSworn')]['Hours'].sum()
    ot_sworn = ot_df_dec[(ot_df_dec['Category'] == 'OT') &
                         (ot_df_dec['MemberClass'] == 'Sworn')]['Hours'].sum()
    ot_nonsworn = ot_df_dec[(ot_df_dec['Category'] == 'OT') &
                            (ot_df_dec['MemberClass'] == 'NonSworn')]['Hours'].sum()

    # ===== PROCESS TIME OFF =====
    to_df = pd.read_excel(to_file, engine='openpyxl')
    print(f"[INFO] Loaded {len(to_df)} time off records")

    # Filter to approved only
    if 'Status' in to_df.columns:
        to_df['Status_norm'] = to_df['Status'].astype(str).apply(normalize_status)
        to_df = to_df[to_df['Status_norm'].isin(approved_statuses)]
        print(f"[INFO] {len(to_df)} approved time off records")

    # Extract data
    to_df['Date'] = pd.to_datetime(to_df['Date'], errors='coerce')
    to_df['Hours'] = pd.to_numeric(to_df['Hours'], errors='coerce').fillna(0)

    # Filter to December 2025
    to_df_dec = to_df[(to_df['Date'].dt.year == 2025) & (to_df['Date'].dt.month == 12)].copy()
    print(f"[INFO] {len(to_df_dec)} time off records in December 2025")

    # Classify usage
    to_df_dec['Usage_Category'] = to_df_dec.apply(
        lambda row: classify_timeoff_usage(row.get('Reason', ''), row.get('Comments', '')),
        axis=1
    )

    # Calculate usage by category
    sick = to_df_dec[to_df_dec['Usage_Category'] == 'Sick']['Hours'].sum()
    sat = to_df_dec[to_df_dec['Usage_Category'] == 'SAT']['Hours'].sum()
    comp_used = to_df_dec[to_df_dec['Usage_Category'] == 'Comp Used']['Hours'].sum()
    military = to_df_dec[to_df_dec['Usage_Category'] == 'Military']['Hours'].sum()
    vacation = to_df_dec[to_df_dec['Usage_Category'] == 'Vacation']['Hours'].sum()
    iod = to_df_dec[to_df_dec['Usage_Category'] == 'IOD']['Hours'].sum()

    results = {
        'Accrued Comp. Time - Sworn': comp_sworn,
        'Accrued Comp. Time - Non-Sworn': comp_nonsworn,
        'Accrued Overtime - Sworn': ot_sworn,
        'Accrued Overtime - Non-Sworn': ot_nonsworn,
        'Employee Sick Time (Hours)': sick,
        'Used SAT Time (Hours)': sat,
        'Comp (Hours)': comp_used,
        'Military Leave (Hours)': military,
        'Vacation (Hours)': vacation,
        'Injured on Duty (Hours)': iod,
    }

    return results

# ===== MAIN VERIFICATION =====
def run_verification():
    """Run complete verification."""

    print("=" * 80)
    print("DECEMBER 2025 OVERTIME & TIME OFF VERIFICATION")
    print("=" * 80)

    # Load files
    print("\n[TASK 1] Comparing December export with November backfill...")
    dec_df = parse_december_export(DEC_EXPORT)
    nov_df = parse_november_backfill(NOV_BACKFILL)

    comparison = compare_exports(dec_df, nov_df)

    # Print comparison results
    print(f"\n[RESULTS] Comparison Summary:")
    print(f"  Total Comparisons: {comparison['total']}")
    print(f"  Matches: {comparison['matches']}")
    print(f"  Differences: {comparison['differences']}")

    if comparison['differences'] > 0:
        print(f"\n[DIFFERENCES] Found {comparison['differences']} differences:")
        comp_df = pd.DataFrame(comparison['comparisons'])
        diffs = comp_df[~comp_df['Match']]
        for _, row in diffs.iterrows():
            print(f"  {row['Category']:50s} {row['Month']:8s} Dec={row['December_Value']:10.2f} Nov={row['November_Value']:10.2f} Diff={row['Difference']:10.2f}")

    # Check for December 2025 in December export
    dec_12_25 = dec_df[dec_df['PeriodLabel'] == '12-25']
    print(f"\n[CHECK] December 2025 (12-25) present in December export: {len(dec_12_25) > 0}")
    if len(dec_12_25) > 0:
        print(f"  Found {len(dec_12_25)} categories for month 12-25")

    # Task 2: Independent processing
    print("\n[TASK 2] Independently processing December 2025 raw exports...")
    try:
        calculated = process_december_raw(DEC_OT_RAW, DEC_TO_RAW, PERSONNEL)

        print("\n[RESULTS] Calculated December 2025 (12-25) values:")
        for category, value in calculated.items():
            print(f"  {category:50s} {value:10.2f}")

        # Compare with December export
        print("\n[COMPARISON] Calculated vs December Export for 12-25:")
        dec_12_25_dict = {}
        for _, row in dec_12_25.iterrows():
            dec_12_25_dict[row['Time Category']] = row['Sum of Value']

        matches = 0
        diffs = 0
        for category in calculated.keys():
            calc_val = calculated[category]
            export_val = dec_12_25_dict.get(category, 0.0)
            diff = abs(calc_val - export_val)
            match = diff <= TOLERANCE

            if match:
                matches += 1
                status = "MATCH"
            else:
                diffs += 1
                status = f"DIFF {diff:.2f}"

            print(f"  {status:15s} {category:50s} Calc={calc_val:10.2f} Export={export_val:10.2f}")

        print(f"\n  Matches: {matches}, Differences: {diffs}")

    except Exception as e:
        print(f"[ERROR] Failed to process December raw exports: {e}")
        import traceback
        traceback.print_exc()

    # Save detailed results
    output_file = Path(__file__).parent / "december_2025_verification_results.csv"
    comp_df = pd.DataFrame(comparison['comparisons'])
    comp_df.to_csv(output_file, index=False)
    print(f"\n[OUTPUT] Detailed comparison saved to: {output_file}")

    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    run_verification()
