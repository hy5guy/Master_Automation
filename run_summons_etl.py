"""
Run Summons ETL with correct file paths.
Merges current-month e-ticket data with historical backfill (gap months) and writes one Excel for Power BI.
"""
import sys
from pathlib import Path

sys.path.insert(0, 'scripts')

from summons_etl_normalize import normalize_personnel_data
from summons_backfill_merge import merge_missing_summons_months

# File paths
summons_path = r'C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\2026\month\2026_01_eticket_export.csv'
master_path = r'C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv'
output_path = r'C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx'

# Run ETL (writes Excel once)
final_data = normalize_personnel_data(summons_path, master_path, output_path)

# Merge backfill for 13-month Department-Wide Summons | Moving and Parking only (other visuals use monthly data)
# Gap months 03-25, 07-25, 10-25, 11-25 from PowerBI_Date\Backfill\...\summons\
merged = merge_missing_summons_months(final_data)
if len(merged) > len(final_data):
    # Mark backfill rows for Power BI (13-month trend keeps HISTORICAL_SUMMARY / IS_AGGREGATE)
    backfill_mask = merged['ETL_VERSION'].isna()
    merged.loc[backfill_mask, 'ETL_VERSION'] = 'HISTORICAL_SUMMARY'
    merged.loc[backfill_mask, 'IS_AGGREGATE'] = True
    merged.to_excel(output_path, sheet_name='Summons_Data', index=False)
    print(f"\n  ✓ Backfill merged: {len(merged) - len(final_data)} rows added; Excel overwritten.")

print("\n" + "="*60)
print("ETL COMPLETE!")
print("="*60)
print(f"\nOutput saved to: {output_path}")
print("\nNext step: Run verification script")
print("  python scripts/verify_summons_remediation.py")
