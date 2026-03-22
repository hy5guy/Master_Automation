"""
Summons Quick Fix Script - 2026-02-17
Fixes classification (Statute-based Moving/Parking) and adds YearMonthKey for sorting
"""
import sys
from pathlib import Path

# Add Master_Automation scripts to path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

try:
    import pandas as pd
    import numpy as np
    from datetime import datetime
    
    def classify_violation(row):
        """Prioritize Statute (Title 39) over Case Type Code"""
        raw_type = str(row.get('Case Type Code', '')).strip().upper()
        statute = str(row.get('Statute', '')).strip().upper()
        description = str(row.get('Violation Description', '')).upper()
        
        # 1. STATUTE CHECK (Primary Authority for Moving)
        if statute.startswith("39:"):
            return "M"  # Title 39 = Moving
        
        # 2. PARKING CHECK
        parking_keywords = ["PARK", "METER", "HANDICAP", "NO PARKING", "STATIONARY", "FIRE HYDRANT", "BLOCKING"]
        is_parking = statute.startswith("39:4-138") or statute.startswith("39:4-135")
        
        if is_parking or any(kw in description for kw in parking_keywords):
            return "P"
        
        # 3. FALLBACK: Use Case Type Code if valid
        if raw_type in ['M', 'P', 'C']:
            return raw_type
        
        # Default
        return "P"
    
    # Load current staging file
    file_path = Path(r"C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    print(f"📖 Reading: {file_path.name}")
    df = pd.read_excel(file_path, sheet_name="Summons_Data")
    print(f"   Loaded {len(df):,} records")
    
    # Backup original TYPE column
    if "TYPE" in df.columns:
        df["TYPE_ORIGINAL"] = df["TYPE"].copy()
        print(f"   Original TYPE distribution:")
        print(df["TYPE_ORIGINAL"].value_counts())
    
    # Apply new classification
    print("\n🔧 Applying Statute-based classification...")
    df["TYPE"] = df.apply(classify_violation, axis=1)
    print(f"   New TYPE distribution:")
    print(df["TYPE"].value_counts())
    
    # Count Title 39 violations
    if "Statute" in df.columns:
        title39 = df[df["Statute"].astype(str).str.startswith("39:", na=False)]
        print(f"\n📊 Title 39 Violations:")
        print(f"   Total: {len(title39):,}")
        print(f"   Classified as Moving: {(title39['TYPE'] == 'M').sum():,}")
        print(f"   Classified as Parking: {(title39['TYPE'] == 'P').sum():,}")
    
    # Add YearMonthKey for sorting
    print("\n🔧 Adding YearMonthKey for date sorting...")
    
    # Try different date column names
    date_col = None
    for col in ["Issue Date", "ISSUE_DATE", "Violation Date", "VIOLATION_DATE", "Date"]:
        if col in df.columns:
            date_col = col
            break
    
    if date_col:
        df["ISSUE_DATE"] = pd.to_datetime(df[date_col], errors="coerce")
        df["Month_Year"] = df["ISSUE_DATE"].dt.strftime("%m-%y")
        df["Year"] = df["ISSUE_DATE"].dt.year
        df["Month"] = df["ISSUE_DATE"].dt.month
        df["YearMonthKey"] = (df["Year"] * 100 + df["Month"]).fillna(0).astype(int)
        
        print(f"   ✅ YearMonthKey created from '{date_col}'")
        print(f"   Latest month: {df['YearMonthKey'].max()} ({df['Month_Year'].mode()[0] if len(df['Month_Year'].mode()) > 0 else 'N/A'})")
    else:
        print(f"   ⚠️ No date column found in: {df.columns.tolist()}")
    
    # Save updated file
    print(f"\n💾 Saving updated file...")
    backup_path = file_path.parent / f"{file_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    # Create backup
    import shutil
    shutil.copy2(file_path, backup_path)
    print(f"   Backup: {backup_path.name}")
    
    # Save updated
    df.to_excel(file_path, sheet_name="Summons_Data", index=False)
    print(f"   ✅ Updated: {file_path.name}")
    
    print("\n✅ Fix complete!")
    print(f"\n📋 Summary:")
    print(f"   Moving violations (M): {(df['TYPE'] == 'M').sum():,}")
    print(f"   Parking violations (P): {(df['TYPE'] == 'P').sum():,}")
    print(f"   Court violations (C): {(df['TYPE'] == 'C').sum():,}")
    print(f"   YearMonthKey range: {df['YearMonthKey'].min() if 'YearMonthKey' in df.columns else 'N/A'} to {df['YearMonthKey'].max() if 'YearMonthKey' in df.columns else 'N/A'}")
    
except ImportError as e:
    print(f"❌ Missing required module: {e}")
    print("Please run: pip install pandas openpyxl")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
