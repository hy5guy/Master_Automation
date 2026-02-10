"""Debug version of verification to see what's happening with classification."""

import pandas as pd
import re

def normalize_status(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").strip().lower())

def classify_overtime_category(pay_type: str):
    """Classify overtime transaction as OT or COMP and extract rate."""
    pay_type = str(pay_type).lower()

    # COMP detection
    if any(term in pay_type for term in ['comp', 'compensatory', 'ct']):
        if '2.5' in pay_type or '250%' in pay_type:
            return 'COMP', '25'
        elif '2.0' in pay_type or '200%' in pay_type or 'double' in pay_type:
            return 'COMP', '20'
        elif '1.5' in pay_type or '150%' in pay_type:
            return 'COMP', '15'
        elif '1.0' in pay_type or '100%' in pay_type:
            return 'COMP', '10'
        return 'COMP', ''

    # OT detection
    ot_terms = ['overtime', 'o.t.', 'o/t', 'dt', 'double time', 'doubletime']
    if any(term in pay_type for term in ot_terms):
        if '2.5' in pay_type or '250%' in pay_type:
            return 'OT', '25'
        elif '2.0' in pay_type or '200%' in pay_type or 'double' in pay_type or 'dt' in pay_type:
            return 'OT', '20'
        elif '1.5' in pay_type or '150%' in pay_type:
            return 'OT', '15'
        return 'OT', '15'

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

# Load overtime file
ot_file = r"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Overtime\export\month\2025\2025_12_otactivity.xlsx"
ot_df = pd.read_excel(ot_file, engine='openpyxl')

print("INITIAL DATA:")
print(f"  Total rows: {len(ot_df)}")
print(f"  Columns: {list(ot_df.columns)}")

# Filter to approved
if 'Status' in ot_df.columns:
    ot_df['Status_norm'] = ot_df['Status'].astype(str).apply(normalize_status)
    approved_statuses = {'approved', 'approvedwstip', 'approvedwithstip',
                        'approvedwithstipend', 'approvedwithstipulation'}
    ot_df = ot_df[ot_df['Status_norm'].isin(approved_statuses)]
    print(f"\nAFTER STATUS FILTER:")
    print(f"  Approved rows: {len(ot_df)}")

# Parse dates and filter to December 2025
ot_df['Date'] = pd.to_datetime(ot_df['Date'], errors='coerce')
ot_df['Hours'] = pd.to_numeric(ot_df['Hours'], errors='coerce').fillna(0)

ot_df_dec = ot_df[(ot_df['Date'].dt.year == 2025) & (ot_df['Date'].dt.month == 12)].copy()
print(f"\nAFTER DATE FILTER (December 2025):")
print(f"  December rows: {len(ot_df_dec)}")
print(f"  Total hours: {ot_df_dec['Hours'].sum():.2f}")

# Apply classification
print("\nCLASSIFYING PAY TYPES...")
ot_df_dec[['Category', 'Rate']] = ot_df_dec['Pay Type'].apply(
    lambda x: pd.Series(classify_overtime_category(x))
)

print(f"\nCATEGORY VALUE COUNTS:")
print(ot_df_dec['Category'].value_counts())

print(f"\nCATEGORY/RATE BREAKDOWN:")
print(ot_df_dec.groupby(['Category', 'Rate'])['Hours'].sum())

# Check for empty categories
if (ot_df_dec['Category'] == '').sum() > 0:
    print(f"\n⚠️ WARNING: {(ot_df_dec['Category'] == '').sum()} rows with no category!")
    unclassified = ot_df_dec[ot_df_dec['Category'] == ''][['Pay Type', 'Hours']].head(10)
    print("Sample unclassified rows:")
    print(unclassified)

# Calculate totals
comp_total = ot_df_dec[ot_df_dec['Category'] == 'COMP']['Hours'].sum()
ot_total = ot_df_dec[ot_df_dec['Category'] == 'OT']['Hours'].sum()

print(f"\nFINAL TOTALS:")
print(f"  COMP Hours: {comp_total:.2f}")
print(f"  OT Hours: {ot_total:.2f}")
print(f"  Total: {comp_total + ot_total:.2f}")
