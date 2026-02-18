import pandas as pd
import os
from datetime import datetime

def generate_integrity_report(processed_file, report_month="01-26"):
    """
    Generates a Data Integrity Report based on the TRIMMED ETL output.
    Aligns with the standardized column schema.
    """
    print(f"Generating Integrity Report for {report_month}...")
    
    if not os.path.exists(processed_file):
        print(f"❌ Error: Processed file {processed_file} not found.")
        return

    # Load the trimmed dataset
    df = pd.read_excel(processed_file, sheet_name='Summons_Data')
    
    # Filter to the specific report month (using the new MM-YY format)
    month_data = df[df['Month_Year'] == report_month].copy()
    
    if month_data.empty:
        print(f"⚠ Warning: No data found for month {report_month}.")
        return

    # 1. Match Rate Calculation
    total_records = len(month_data)
    # Records where WG2 is NOT UNKNOWN are considered matched
    matched_records = len(month_data[month_data['WG2'] != 'UNKNOWN'])
    match_rate = (matched_records / total_records) * 100 if total_records > 0 else 0

    # 2. Data Quality Tier Summary (Using new ETL columns)
    dq_summary = month_data['DATA_QUALITY_TIER'].value_counts().to_dict()

    # 3. Bureau Distribution Summary
    bureau_dist = month_data.groupby(['WG2', 'VIOLATION_TYPE'])['TICKET_COUNT'].sum().unstack(fill_value=0)

    # 4. Unknown Badge Investigation
    unknown_badges = month_data[month_data['WG2'] == 'UNKNOWN']['PADDED_BADGE_NUMBER'].unique().tolist()

    # --- Generate Markdown Report ---
    report_content = f"""
# Summons Data Integrity Report: {report_month}
**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 High-Level Metrics
* **Total Records processed:** {total_records}
* **Match Rate (to Assignment Master):** {match_rate:.2f}%
* **Target Match Rate:** ≥ 95.00%
* **Status:** {"✅ PASS" if match_rate >= 95 else "❌ FAIL"}

## 🛡️ Data Quality Tiers
{pd.Series(dq_summary).to_markdown()}

## 👮 Bureau Assignment Summary (Ticket Counts)
{bureau_dist.to_markdown()}

## 🔍 Investigation: Unknown Badges
The following badge numbers were found in the e-ticket export but are missing from the Assignment Master:
* {', '.join(unknown_badges) if unknown_badges else "None - 100% Personnel Coverage"}

---
*End of Report*
"""
    
    # Save the report
    report_path = f"reports/summons_integrity_{report_month.replace('-', '')}.md"
    os.makedirs('reports', exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ Integrity report saved to: {report_path}")

# Run for January 2026
if __name__ == "__main__":
    PROCESSED_PATH = r'C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx'
    generate_integrity_report(PROCESSED_PATH, report_month="01-26")