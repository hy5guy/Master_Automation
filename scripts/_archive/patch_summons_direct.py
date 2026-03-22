"""
Direct patch to summons_powerbi_latest.xlsx - Add TYPE and YearMonthKey columns
Run with any Python that has pandas + openpyxl
"""
import sys

# Try different import approaches
try:
    # First try direct
    import pandas as pd
    print("OK Pandas loaded")
except:
    try:
        # Try with explicit path to site-packages
        import os
        possible_paths = [
            r"C:\Users\RobertCarucci\AppData\Local\Programs\Python\Python313\Lib\site-packages",
            r"C:\Python313\Lib\site-packages",
            r"C:\Python312\Lib\site-packages",
            r"C:\Python311\Lib\site-packages",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                sys.path.insert(0, path)
                import pandas as pd
                print(f"OK Pandas loaded from {path}")
                break
    except Exception as e:
        print(f"ERROR Cannot load pandas: {e}")
        print("\nPlease install pandas:")
        print("  pip install pandas openpyxl")
        sys.exit(1)

from pathlib import Path
from datetime import datetime

file_path = Path(r"C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx")

print(f"\nReading: {file_path}")
df = pd.read_excel(file_path, sheet_name="Summons_Data")
print(f"   Rows: {len(df):,}")

# Show current columns
print(f"\nColumns ({len(df.columns)}):")
for i, col in enumerate(list(df.columns)[:30], 1):
    print(f"  {i}. {col}")
if len(df.columns) > 30:
    print(f"  ... and {len(df.columns) - 30} more")

# Find TYPE column
if "TYPE" in df.columns:
    print(f"\nCurrent TYPE distribution:")
    print(df["TYPE"].value_counts())
else:
    print("\nNo TYPE column - will create it")

# Classification function
def classify_violation(row):
    # Try different column name variations
    case_type = ""
    statute = ""
    description = ""
    
    for col in ["Case Type Code", "CASE_TYPE_CODE", "CaseTypeCode"]:
        if col in row.index:
            case_type = str(row.get(col, "")).strip().upper()
            break
    
    for col in ["Statute", "STATUTE", "VIOLATION_NUMBER"]:
        if col in row.index:
            statute = str(row.get(col, "")).strip().upper()
            break
    
    for col in ["Violation Description", "VIOLATION_DESCRIPTION", "Description"]:
        if col in row.index:
            description = str(row.get(col, "")).upper()
            break
    
    # 1. STATUTE CHECK - Title 39 = Moving
    if statute.startswith("39:"):
        return "M"
    
    # 2. PARKING CHECK
    parking_keywords = ["PARK", "METER", "HANDICAP", "NO PARKING", "FIRE HYDRANT"]
    is_parking = statute.startswith("39:4-138") or statute.startswith("39:4-135")
    if is_parking or any(kw in description for kw in parking_keywords):
        return "P"
    
    # 3. FALLBACK
    if case_type in ['M', 'P', 'C']:
        return case_type
    
    return "P"

print("\nApplying Statute-based TYPE classification...")
df["TYPE"] = df.apply(classify_violation, axis=1)
print(f"\nNew TYPE distribution:")
print(df["TYPE"].value_counts())

# Check Title 39
statute_col = None
for col in ["Statute", "STATUTE", "VIOLATION_NUMBER"]:
    if col in df.columns:
        statute_col = col
        break

if statute_col:
    title39 = df[df[statute_col].astype(str).str.startswith("39:", na=False)]
    print(f"\nTitle 39 Violations Check:")
    print(f"   Total Title 39: {len(title39):,}")
    print(f"   Classified as M: {(title39['TYPE'] == 'M').sum():,}")
    print(f"   Classified as P: {(title39['TYPE'] == 'P').sum():,}")

# Add YearMonthKey
print("\nAdding YearMonthKey for sorting...")
date_col = None
for col in ["Issue Date", "ISSUE_DATE", "Violation Date", "VIOLATION_DATE", "Date"]:
    if col in df.columns:
        date_col = col
        break

if date_col:
    df["ISSUE_DATE_TEMP"] = pd.to_datetime(df[date_col], errors="coerce")
    df["Month_Year"] = df["ISSUE_DATE_TEMP"].dt.strftime("%m-%y")
    df["Year"] = df["ISSUE_DATE_TEMP"].dt.year
    df["Month"] = df["ISSUE_DATE_TEMP"].dt.month
    df["YearMonthKey"] = (df["Year"] * 100 + df["Month"]).fillna(0).astype(int)
    df.drop("ISSUE_DATE_TEMP", axis=1, inplace=True)
    print(f"   OK YearMonthKey created")
    print(f"   Range: {df['YearMonthKey'].min()} to {df['YearMonthKey'].max()}")
else:
    print(f"   Warning: No date column found")

# Backup and save
backup = file_path.parent / f"{file_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
print(f"\nCreating backup: {backup.name}")

import shutil
shutil.copy2(file_path, backup)

print(f"Saving updated file: {file_path.name}")
df.to_excel(file_path, sheet_name="Summons_Data", index=False)

print("\nCOMPLETE!")
print(f"\nFinal Summary:")
print(f"   Moving (M): {(df['TYPE'] == 'M').sum():,}")
print(f"   Parking (P): {(df['TYPE'] == 'P').sum():,}")
print(f"   Court (C): {(df['TYPE'] == 'C').sum():,}")
if "YearMonthKey" in df.columns:
    print(f"   Latest month: {df['YearMonthKey'].max()}")
