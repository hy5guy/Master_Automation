"""Analyze December 2025 e-ticket export data"""
import pandas as pd
from pathlib import Path

# Read the December 2025 e-ticket export
eticket_file = Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\2025\raw\month\2025_12_eticket_export.csv")

print("=" * 70)
print("ANALYZING DECEMBER 2025 E-TICKET EXPORT")
print("=" * 70)

# Detect delimiter
with open(eticket_file, 'r', encoding='utf-8') as f:
    first_line = f.readline()
    delimiter = ";" if first_line.count(";") > first_line.count(",") else ","
    print(f"\nDetected delimiter: '{delimiter}'")

# Load data
df = pd.read_csv(eticket_file, sep=delimiter, encoding='utf-8', low_memory=False, dtype=str)
print(f"\nTotal rows in export: {len(df):,}")

# Show column names
print(f"\nColumns ({len(df.columns)} total):")
for i, col in enumerate(df.columns[:15], 1):
    print(f"  {i}. {col}")
if len(df.columns) > 15:
    print(f"  ... and {len(df.columns) - 15} more")

# Check for Case Type Code or similar column
type_cols = [col for col in df.columns if 'type' in col.lower() or 'code' in col.lower() or 'violation' in col.lower()]
print(f"\nPotential type/code columns: {type_cols}")

# If Case Type Code exists, count by type
if 'Case Type Code' in df.columns:
    print("\n" + "=" * 70)
    print("COUNTS BY CASE TYPE CODE:")
    print("=" * 70)
    counts = df['Case Type Code'].value_counts()
    for typ, count in counts.items():
        print(f"  {typ}: {count:,}")
    
    # Calculate M and P totals
    m_count = counts.get('M', 0) if 'M' in counts.index else 0
    p_count = counts.get('P', 0) if 'P' in counts.index else 0
    print(f"\n  Moving (M): {m_count:,}")
    print(f"  Parking (P): {p_count:,}")
    print(f"  Total: {m_count + p_count:,}")

# Check Issue Date column
date_cols = [col for col in df.columns if 'date' in col.lower() or 'issue' in col.lower()]
print(f"\nPotential date columns: {date_cols}")

if 'Issue Date' in df.columns:
    print("\n" + "=" * 70)
    print("SAMPLE ISSUE DATES:")
    print("=" * 70)
    sample_dates = df['Issue Date'].dropna().head(10).tolist()
    for date in sample_dates:
        print(f"  {date}")

print("\n" + "=" * 70)
print("COMPARISON WITH CHATGPT CLAIMS:")
print("=" * 70)
print("ChatGPT claimed:")
print("  Moving (M): 443")
print("  Parking (P): 2,896")
print("  Total: 3,339")
if 'Case Type Code' in df.columns:
    counts = df['Case Type Code'].value_counts()
    m_actual = counts.get('M', 0) if 'M' in counts.index else 0
    p_actual = counts.get('P', 0) if 'P' in counts.index else 0
    print(f"\nActual from export:")
    print(f"  Moving (M): {m_actual:,}")
    print(f"  Parking (P): {p_actual:,}")
    print(f"  Total: {m_actual + p_actual:,}")
    
    if m_actual != 443 or p_actual != 2896:
        print("\n⚠️  DISCREPANCY DETECTED!")
        print(f"  M difference: {m_actual - 443} ({'+' if m_actual > 443 else ''}{m_actual - 443})")
        print(f"  P difference: {p_actual - 2896} ({'+' if p_actual > 2896 else ''}{p_actual - 2896})")
