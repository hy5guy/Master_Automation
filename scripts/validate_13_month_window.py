#!/usr/bin/env python3
"""
Validate that Power BI visual exports contain the correct 13-month rolling window.

Usage:
  python validate_13_month_window.py --input export.csv [--period-column Period]
  python validate_13_month_window.py --scan-folder Processed_Exports/Summons
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from typing import Literal


def calculate_13_month_window(as_of_date: datetime | None = None) -> tuple[str, str, list[str]]:
    """
    Calculate 13-month rolling window ending with previous complete month.
    Returns (start_period, end_period, all_periods) in MM-YY format.
    """
    if as_of_date is None:
        as_of_date = datetime.now()
    
    # End date: previous month
    if as_of_date.month == 1:
        end_year = as_of_date.year - 1
        end_month = 12
    else:
        end_year = as_of_date.year
        end_month = as_of_date.month - 1
    
    # Start date: 12 months before end
    start_date = datetime(end_year, end_month, 1) - timedelta(days=365)
    if start_date.month == end_month:
        if start_date.month == 1:
            start_year = start_date.year - 1
            start_month = 12
        else:
            start_year = start_date.year
            start_month = start_date.month - 1
    else:
        start_year = start_date.year
        start_month = start_date.month
    
    # Generate all 13 periods
    periods = []
    current_year = start_year
    current_month = start_month
    
    for _ in range(13):
        period = f"{current_month:02d}-{str(current_year)[-2:]}"
        periods.append(period)
        
        if current_month == 12:
            current_month = 1
            current_year += 1
        else:
            current_month += 1
    
    start_period = f"{start_month:02d}-{str(start_year)[-2:]}"
    end_period = f"{end_month:02d}-{str(end_year)[-2:]}"
    
    return start_period, end_period, periods


def normalize_period_label(label: str) -> str:
    """Strip 'Sum of ' prefix and trim whitespace."""
    if not isinstance(label, str):
        return str(label).strip()
    clean = label.strip()
    if clean.lower().startswith("sum of "):
        clean = clean[7:].strip()
    return clean


def validate_file(
    file_path: Path,
    period_column: str | None = None,
    verbose: bool = False
) -> tuple[Literal["PASS", "FAIL", "WARN"], str]:
    """
    Validate a single CSV file for 13-month window compliance.
    
    Returns:
        (status, message)
        status: "PASS" (13 months), "WARN" (12 months with missing), "FAIL" (<12 months or issues)
    """
    if not file_path.exists():
        return ("FAIL", f"File not found: {file_path}")
    
    try:
        df = pd.read_csv(file_path, low_memory=False)
        
        if df.empty:
            return ("FAIL", "File is empty")
        
        # Auto-detect period column if not specified
        if period_column is None:
            candidates = ["Period", "Month_Year", "PeriodLabel", "Month", "Date"]
            for col in candidates:
                if col in df.columns:
                    period_column = col
                    break
            
            if period_column is None:
                return ("FAIL", f"No period column found. Available columns: {list(df.columns)}")
        
        if period_column not in df.columns:
            return ("FAIL", f"Column '{period_column}' not found. Available: {list(df.columns)}")
        
        # Normalize period labels
        df[period_column] = df[period_column].apply(normalize_period_label)
        
        # Get expected window
        start_expected, end_expected, periods_expected = calculate_13_month_window()
        
        # Get actual periods
        actual_periods = sorted(df[period_column].unique())
        
        # Validate
        missing_periods = set(periods_expected) - set(actual_periods)
        extra_periods = set(actual_periods) - set(periods_expected)
        
        # Determine status
        if len(actual_periods) == 13 and not missing_periods and not extra_periods:
            status = "PASS"
            msg = f"✓ 13 months: {start_expected} to {end_expected}"
        elif len(actual_periods) >= 12 and len(missing_periods) <= 1:
            status = "WARN"
            msg = f"⚠ {len(actual_periods)} months (missing: {sorted(missing_periods)})"
        else:
            status = "FAIL"
            msg = f"✗ {len(actual_periods)} months (expected 13)"
        
        if verbose:
            details = []
            if missing_periods:
                details.append(f"  Missing: {sorted(missing_periods)}")
            if extra_periods:
                details.append(f"  Extra: {sorted(extra_periods)}")
            if details:
                msg += "\n" + "\n".join(details)
        
        return (status, msg)
        
    except Exception as e:
        return ("FAIL", f"Error reading file: {e}")


def scan_folder(
    folder_path: Path,
    period_column: str | None = None,
    verbose: bool = False
) -> dict[str, tuple[str, str]]:
    """
    Scan folder for CSV files and validate each.
    Returns dict of {filename: (status, message)}.
    """
    if not folder_path.exists():
        return {}
    
    results = {}
    csv_files = sorted(folder_path.glob("*.csv"))
    
    for file_path in csv_files:
        status, msg = validate_file(file_path, period_column, verbose)
        results[file_path.name] = (status, msg)
    
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate 13-month rolling window in CSV exports")
    parser.add_argument("--input", type=Path, help="Single CSV file to validate")
    parser.add_argument("--scan-folder", type=Path, help="Folder containing CSV files to scan")
    parser.add_argument("--period-column", type=str, help="Name of period column (auto-detect if not specified)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed validation info")
    
    args = parser.parse_args()
    
    # Show expected window
    start, end, periods = calculate_13_month_window()
    print(f"Expected 13-month window (as of {datetime.now().strftime('%Y-%m-%d')}): {start} to {end}")
    print(f"Periods: {', '.join(periods)}")
    print()
    
    # Validate single file or scan folder
    if args.input:
        status, msg = validate_file(args.input, args.period_column, args.verbose)
        print(f"[{status}] {args.input.name}")
        print(f"  {msg}")
        return 0 if status == "PASS" else 1
    
    elif args.scan_folder:
        results = scan_folder(args.scan_folder, args.period_column, args.verbose)
        
        if not results:
            print(f"No CSV files found in {args.scan_folder}")
            return 1
        
        # Summary
        pass_count = sum(1 for s, _ in results.values() if s == "PASS")
        warn_count = sum(1 for s, _ in results.values() if s == "WARN")
        fail_count = sum(1 for s, _ in results.values() if s == "FAIL")
        
        print(f"Scanned {len(results)} files in {args.scan_folder}:")
        print()
        
        # Results
        for filename, (status, msg) in results.items():
            print(f"[{status}] {filename}")
            if args.verbose or status != "PASS":
                print(f"  {msg}")
        
        print()
        print(f"Summary: {pass_count} PASS, {warn_count} WARN, {fail_count} FAIL")
        
        return 0 if fail_count == 0 else 1
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
