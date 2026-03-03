"""
Diagnostic script to investigate missing Community Engagement events
Compares source Excel files against ETL output to identify discrepancies
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# Source file paths
CE_FILE = r"C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Community_Engagement\Community_Engagement_Monthly.xlsx"
STACP_FILE = r"C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\STACP\STACP.xlsm"
ETL_OUTPUT = r"C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Community_Engagment\output\community_engagement_data_20251210_024452.csv"

def check_source_data():
    """Check source Excel files for December 2025 events"""

    print("=" * 80)
    print("COMMUNITY ENGAGEMENT SOURCE FILE ANALYSIS")
    print("=" * 80)

    # Read Community Engagement source
    try:
        print(f"\nReading: {CE_FILE}")
        print(f"Sheet: 2025_Master")

        # Get all sheet names first
        xl_file = pd.ExcelFile(CE_FILE)
        print(f"Available sheets: {xl_file.sheet_names}")

        # Read the 2025_Master sheet
        ce_df = pd.read_excel(CE_FILE, sheet_name='2025_Master')
        print(f"\nTotal rows in 2025_Master: {len(ce_df)}")
        print(f"Columns: {list(ce_df.columns)}")

        # Check for Date of Event column
        date_col = 'Date of Event'
        if date_col in ce_df.columns:
            # Convert to datetime
            ce_df[date_col] = pd.to_datetime(ce_df[date_col], errors='coerce')

            # Filter to December 2025
            dec_2025 = ce_df[ce_df[date_col].dt.to_period('M') == '2025-12']
            print(f"\nDecember 2025 events found: {len(dec_2025)}")

            if len(dec_2025) > 0:
                print("\nDecember 2025 Community Engagement Events:")
                for idx, row in dec_2025.iterrows():
                    event_name = row.get('Community Event', 'Unknown')
                    event_date = row[date_col].strftime('%Y-%m-%d') if pd.notna(row[date_col]) else 'No date'
                    print(f"  {event_date}: {event_name}")
        else:
            print(f"\nWARNING: Column '{date_col}' not found!")
            print(f"Available date-like columns: {[col for col in ce_df.columns if 'date' in col.lower()]}")

    except Exception as e:
        print(f"ERROR reading Community Engagement file: {e}")

    print("\n" + "=" * 80)
    print("STA&CP SOURCE FILE ANALYSIS")
    print("=" * 80)

    # Read STA&CP source
    try:
        print(f"\nReading: {STACP_FILE}")
        print(f"Sheet: 25_School_Outreach")

        # Get all sheet names first
        xl_file = pd.ExcelFile(STACP_FILE)
        print(f"Available sheets: {xl_file.sheet_names}")

        # Read the 25_School_Outreach sheet
        stacp_df = pd.read_excel(STACP_FILE, sheet_name='25_School_Outreach')
        print(f"\nTotal rows in 25_School_Outreach: {len(stacp_df)}")
        print(f"Columns: {list(stacp_df.columns)}")

        # Check for Date column
        date_col = 'Date'
        if date_col in stacp_df.columns:
            # Convert to datetime
            stacp_df[date_col] = pd.to_datetime(stacp_df[date_col], errors='coerce')

            # Filter to December 2025
            dec_2025 = stacp_df[stacp_df[date_col].dt.to_period('M') == '2025-12']
            print(f"\nDecember 2025 events found: {len(dec_2025)}")

            if len(dec_2025) > 0:
                print("\nDecember 2025 STA&CP Events:")
                for idx, row in dec_2025.iterrows():
                    event_name = row.get('School Outreach Conducted ', 'Unknown')
                    event_date = row[date_col].strftime('%Y-%m-%d') if pd.notna(row[date_col]) else 'No date'
                    print(f"  {event_date}: {event_name}")
        else:
            print(f"\nWARNING: Column '{date_col}' not found!")
            print(f"Available date-like columns: {[col for col in stacp_df.columns if 'date' in col.lower()]}")

    except Exception as e:
        print(f"ERROR reading STA&CP file: {e}")

    print("\n" + "=" * 80)
    print("ETL OUTPUT FILE ANALYSIS")
    print("=" * 80)

    # Read ETL output
    try:
        print(f"\nReading: {ETL_OUTPUT}")

        etl_df = pd.read_csv(ETL_OUTPUT)
        print(f"Total rows in ETL output: {len(etl_df)}")

        # Convert date to datetime
        etl_df['date'] = pd.to_datetime(etl_df['date'], errors='coerce')

        # Filter to December 2025
        dec_2025_etl = etl_df[etl_df['date'].dt.to_period('M') == '2025-12']
        print(f"\nDecember 2025 events in ETL output: {len(dec_2025_etl)}")

        # Break down by source
        if 'data_source' in etl_df.columns:
            ce_count = len(dec_2025_etl[dec_2025_etl['data_source'] == 'community_engagement'])
            stacp_count = len(dec_2025_etl[dec_2025_etl['data_source'] == 'stacp'])
            print(f"  Community Engagement: {ce_count} events")
            print(f"  STA&CP: {stacp_count} events")

    except Exception as e:
        print(f"ERROR reading ETL output: {e}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("\nThis diagnostic will help identify:")
    print("1. How many December 2025 events are in source files")
    print("2. How many made it to ETL output")
    print("3. Which events are missing from ETL output")

if __name__ == "__main__":
    check_source_data()
