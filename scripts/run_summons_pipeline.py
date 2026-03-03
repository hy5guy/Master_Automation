import os
import sys
from datetime import datetime

# Import the core functions from your existing scripts
from scripts.summons_etl_normalize import normalize_personnel_data
from scripts.generate_summons_integrity_report import generate_integrity_report

# Configuration Paths
RAW_EXPORT = r'C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\2026\month\2026_01_eticket_export.csv'
MASTER_FILE = r'C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv'
OUTPUT_EXCEL = r'C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx'

def run_pipeline(target_month="01-26"):
    """
    Executes the full Summons Data Pipeline:
    1. Runs Trimmed ETL (Normalization + Personnel Mapping)
    2. Runs Data Integrity Report (Match Rates + Unknown Badge Audit)
    """
    start_time = datetime.now()
    print("=" * 70)
    print(f"SUMMONS PIPELINE EXECUTION: {target_month}")
    print("=" * 70)

    # --- STEP 1: RUN ETL ---
    print(f"\n[STEP 1/2] Executing Trimmed ETL...")
    try:
        # Calls the function with the new Trim/HTML/Badge logic
        etl_result = normalize_personnel_data(RAW_EXPORT, MASTER_FILE, OUTPUT_EXCEL)
        
        if etl_result is not None:
            print(f"✓ ETL Complete. Processed {len(etl_result)} records into staging.")
        else:
            print("❌ Pipeline halted: ETL failed to produce output.")
            return
    except Exception as e:
        print(f"❌ Critical Error during ETL: {e}")
        return

    # --- STEP 2: RUN INTEGRITY REPORT ---
    print(f"\n[STEP 2/2] Generating Data Integrity Report...")
    try:
        # Calls the updated report generator aligned with trimmed columns
        generate_integrity_report(OUTPUT_EXCEL, report_month=target_month)
    except Exception as e:
        print(f"❌ Critical Error during Integrity Reporting: {e}")
        return

    duration = datetime.now() - start_time
    print("\n" + "=" * 70)
    print(f"PIPELINE SUCCESSFUL | TOTAL TIME: {duration.total_seconds():.2f}s")
    print(f"EXCEL READY: {OUTPUT_EXCEL}")
    print("=" * 70)

if __name__ == "__main__":
    # You can pass a specific month as an argument, e.g., python run_pipeline.py 02-26
    current_target = sys.argv[1] if len(sys.argv) > 1 else "01-26"
    run_pipeline(current_target)