#!/usr/bin/env python3
"""
Enhanced date inference for Power BI visual exports.

Strategy:
1. For 13-month rolling visuals: Read CSV, use LAST period column (most recent month)
2. For single-month visuals: Read Period/Month_Year column value
3. Fallback: Infer from filename or use previous month
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import pandas as pd


def _parse_period_to_yyyymm(period: str) -> str | None:
    """
    Parse MM-YY period to YYYY_MM format.
    
    Examples:
        "01-26" -> "2026_01"
        "Sum of 12-25" -> "2025_12"
    """
    if not isinstance(period, str):
        return None
    
    clean = period.strip()
    if clean.lower().startswith("sum of "):
        clean = clean[7:].strip()
    
    m = re.match(r"^(\d{2})-(\d{2})$", clean)
    if not m:
        return None
    
    mm, yy = m.groups()
    month = int(mm)
    year = int(yy)
    
    if not (1 <= month <= 12):
        return None
    
    # Convert 2-digit year to 4-digit
    if year < 100:
        year = 2000 + year
    
    return f"{year:04d}_{month:02d}"


def infer_yyyymm_from_data(
    file_path: Path,
    enforce_13_month: bool = False,
    verbose: bool = False
) -> str | None:
    """
    Infer YYYY_MM by reading CSV data.
    
    Strategy:
    1. For 13-month rolling (enforce_13_month=True):
       - Look for MM-YY format columns (e.g., "01-25", "02-25", ...)
       - Use the LAST column (most recent month)
       - Example: columns end with "01-26" -> return "2026_01"
    
    2. For single-month visuals:
       - Look for Period/Month_Year/Date column
       - Parse the value to get the month
       - Example: Period="01-26" -> return "2026_01"
    
    Returns:
        YYYY_MM string or None (caller should fall back to filename/previous month)
    """
    try:
        # Read first few rows to detect structure
        df = pd.read_csv(file_path, nrows=20, low_memory=False)
        
        if df.empty:
            return None
        
        # Strategy 1: For 13-month rolling, find period columns and use LAST one
        if enforce_13_month:
            period_cols = []
            for col in df.columns:
                if isinstance(col, str):
                    clean_col = col.strip()
                    # Strip "Sum of " prefix
                    if clean_col.lower().startswith("sum of "):
                        clean_col = clean_col[7:].strip()
                    # Check if MM-YY format
                    if re.match(r"^\d{2}-\d{2}$", clean_col):
                        period_cols.append(clean_col)
            
            if period_cols:
                # Use LAST period column (most recent month in rolling window)
                last_period = period_cols[-1]
                yyyymm = _parse_period_to_yyyymm(last_period)
                if yyyymm and verbose:
                    print(f"[DATA] Inferred {yyyymm} from last period column: {last_period}")
                return yyyymm
        
        # Strategy 2: For single-month, look for Period/Month_Year column
        date_columns = ["Period", "Month_Year", "PeriodLabel", "Date", "Month"]
        for col_name in date_columns:
            if col_name in df.columns:
                # Get non-null values
                values = df[col_name].dropna().astype(str).str.strip()
                if values.empty:
                    continue
                
                # Try most common value (in case of multiple rows with same month)
                most_common = values.mode()
                if not most_common.empty:
                    period = most_common.iloc[0]
                    yyyymm = _parse_period_to_yyyymm(period)
                    if yyyymm:
                        if verbose:
                            print(f"[DATA] Inferred {yyyymm} from {col_name} column: {period}")
                        return yyyymm
        
        # No period columns found
        return None
        
    except Exception as e:
        # If reading fails, return None to fall back
        if verbose:
            print(f"[WARN] Could not read data for date inference: {e}")
        return None


def infer_yyyymm_from_path_fallback(file_path: Path) -> str:
    """
    Fallback: Infer YYYY_MM from filename or use previous month.
    
    Tries:
    1. Extract YYYY_MM from filename (e.g., "2026_01_...")
    2. Default to previous complete month
    """
    stem = file_path.stem
    m = re.search(r"(\d{4})_(\d{2})", stem)
    if m:
        y, mo = m.group(1), m.group(2)
        if 1 <= int(mo) <= 12 and int(y) >= 2000:
            return f"{y}_{mo}"
    
    # Default: previous month from now
    now = datetime.now()
    if now.month == 1:
        prev = now.replace(year=now.year - 1, month=12)
    else:
        prev = now.replace(month=now.month - 1)
    
    yyyy_mm = f"{prev.year:04d}_{prev.month:02d}"
    return yyyy_mm


def infer_yyyymm_smart(
    file_path: Path,
    enforce_13_month: bool = False,
    verbose: bool = False
) -> str:
    """
    Smart YYYY_MM inference: Try data first, fall back to filename/previous month.
    
    Priority:
    1. Read CSV data (for 13-month: last column, for others: Period column)
    2. Parse filename for YYYY_MM pattern
    3. Use previous complete month
    
    Always returns a valid YYYY_MM string.
    """
    # Try data-based inference
    yyyymm = infer_yyyymm_from_data(file_path, enforce_13_month, verbose)
    if yyyymm:
        return yyyymm
    
    # Fall back to filename/previous month
    yyyymm = infer_yyyymm_from_path_fallback(file_path)
    if verbose:
        print(f"[FALLBACK] Using {yyyymm} from filename/previous month for {file_path.name}")
    return yyyymm


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python date_inference.py <csv_file> [--13-month] [--verbose]")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    enforce_13_month = "--13-month" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    yyyymm = infer_yyyymm_smart(file_path, enforce_13_month, verbose)
    print(f"Inferred YYYY_MM: {yyyymm}")
