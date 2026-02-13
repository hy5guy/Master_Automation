import pandas as pd
import os
from pathlib import Path

def setup_test_environment():
    """
    Creates a mock _DropExports folder with samples that test the 
    robust 'Sum of MM-YY' detection and normalization logic.
    """
    # Create the drop directory expected by process_powerbi_exports.py
    drop_dir = Path("_DropExports")
    drop_dir.mkdir(exist_ok=True)
    
    # 1. Summons: Wide Format Test (Tests robust MM-YY detection with prefixes)
    summons_data = {
        "Bureau": ["Traffic", "Patrol", "Traffic", "Patrol"],
        "Moving/Parking": ["Moving", "Moving", "Parking", "Parking"],
        "Sum of 12-25": [10, 20, 30, 40],
        "Sum of 01-26": [15, 25, 35, 45]
    }
    summons_file = drop_dir / "2026_01_Department-Wide Summons.csv"
    pd.DataFrame(summons_data).to_csv(summons_file, index=False)
    
    # 2. Training Cost: Wide Format Test
    training_data = {
        "Delivery Method": ["Online", "In-Person", "Online", "In-Person"],
        "Sum of 12-25": [100.50, 200.75, 150.00, 300.00],
        "Sum of 01-26": [110.00, 210.00, 160.00, 310.00]
    }
    training_file = drop_dir / "2026_01_Training Cost by Delivery Method.csv"
    pd.DataFrame(training_data).to_csv(training_file, index=False)
    
    # 3. Monthly Accrual: Long Format Test (Standard pipeline test)
    accrual_data = {
        "Time Category": ["Sick", "Vacation", "Sick", "Vacation"],
        "Sum of Value": [8.0, 16.0, 4.0, 8.0],
        "PeriodLabel": ["Sum of 12-25", "Sum of 12-25", "Sum of 01-26", "Sum of 01-26"]
    }
    accrual_file = drop_dir / "2026_01_Monthly Accrual and Usage Summary.csv"
    pd.DataFrame(accrual_data).to_csv(accrual_file, index=False)

    print(f"[OK] Test environment setup complete in '{drop_dir}'.")
    print("Sample files created for verification:")
    print(f" - {summons_file.name}")
    print(f" - {training_file.name}")
    print(f" - {accrual_file.name}")

if __name__ == "__main__":
    setup_test_environment()