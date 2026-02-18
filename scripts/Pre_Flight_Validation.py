import os
import sys
from pathlib import Path

# 1. Path Portability (Leverages path_config logic)
def get_onedrive_root():
    # Priority: Env Var > Default Path
    root = os.environ.get('ONEDRIVE_HACKENSACK') or os.environ.get('ONEDRIVE_BASE')
    if not root:
        root = r"C:\Users\carucci_r\OneDrive - City of Hackensack"
    return Path(root)

def validate_system():
    root = get_onedrive_root()
    master_path = root / "Master_Automation"
    drop_folder = root / "PowerBI_Date" / "_DropExports"
    
    print(f"--- PRE-FLIGHT AUDIT: Master Automation ---")
    print(f"Target Root: {root}\n")

    # Required Checks List
    checks = [
        # Essential Infrastructure
        (master_path / "Assignment_Master_V2.csv", "Critical Personnel File"),
        (master_path / "config" / "scripts.json", "ETL Orchestrator Config"),
        
        # Monthly Source Data (Feb 2026 Cycle / Jan Data)
        (root / "05_EXPORTS" / "_Summons" / "E_Ticket" / "2026" / "2026_01_eticket_export.csv", "Jan 2026 Summons Source"),
        (root / "05_EXPORTS" / "_CAD" / "timereport" / "monthly" / "2026_01_timereport.xlsx", "Jan 2026 Response Time Source"),
        
        # Integration Points
        (drop_folder, "Power BI Drop Folder Access")
    ]

    failed_checks = 0
    for path, description in checks:
        if path.exists():
            print(f"[PASS] {description}")
        else:
            print(f"[FAIL] {description} MISSING at: {path}")
            failed_checks += 1

    print(f"\n--- Audit Summary ---")
    if failed_checks == 0:
        print("✅ READY: All dependencies found. Proceeding to run_all_etl.ps1.")
        return True
    else:
        print(f"❌ STOP: {failed_checks} critical issues found. Fix these before running ETL.")
        return False

if __name__ == "__main__":
    if not validate_system():
        sys.exit(1)