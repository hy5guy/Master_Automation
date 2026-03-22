#!/usr/bin/env python3
"""
Normalize Power BI visual exports for backfill consumption with 13-month rolling window enforcement.

Handles Long (default) and Wide formats, normalizes column names and period labels,
and optionally enforces a 13-month rolling data window (ending with previous complete month).

Usage:
  python normalize_visual_export_for_backfill.py --input <path> --output <path> [--format summons|training_cost] [--enforce-13-month] [--dry-run]
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

try:
    from path_config import get_onedrive_root
except ImportError:
    import os
    def get_onedrive_root() -> Path:
        base = os.environ.get("ONEDRIVE_BASE") or os.environ.get("ONEDRIVE_HACKENSACK")
        if base:
            return Path(base)
        return Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack")


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def calculate_13_month_window(as_of_date: datetime | None = None) -> tuple[str, str, list[str]]:
    """
    Calculate 13-month rolling window ending with previous complete month.
    
    Operational Rule:
    - End Date: Previous month from today (never include current month)
    - Start Date: 12 months before end date
    - Window: 13 full months (start + 12 = 13 total)
    
    Args:
        as_of_date: Reference date (defaults to today)
    
    Returns:
        Tuple of (start_period, end_period, all_periods)
        Periods in MM-YY format (e.g. "01-25")
    
    Example:
        Today: February 12, 2026
        End: January 2026 (01-26)
        Start: January 2025 (01-25)
        Window: 01-25, 02-25, ..., 12-25, 01-26 (13 months)
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
    # Adjust to first of month 12 months prior
    if start_date.month == end_month:
        # If we landed on same month, go back one more month
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
        
        # Next month
        if current_month == 12:
            current_month = 1
            current_year += 1
        else:
            current_month += 1
    
    start_period = f"{start_month:02d}-{str(start_year)[-2:]}"
    end_period = f"{end_month:02d}-{str(end_year)[-2:]}"
    
    return start_period, end_period, periods


def _period_label_to_year_month(label: str) -> tuple[int, int] | None:
    """
    Parse period label to (year, month) if it matches MM-YY format.
    Returns None if not a valid month label.
    
    Examples:
      "01-25" -> (2025, 1)
      "Sum of 11-25" -> (2025, 11)
      "Random Text" -> None
    """
    if not isinstance(label, str):
        return None
    
    # Strip "Sum of " prefix if present
    clean = label.strip()
    if clean.lower().startswith("sum of "):
        clean = clean[7:].strip()
    
    # Match MM-YY pattern
    m = re.match(r"^(\d{2})-(\d{2})$", clean)
    if not m:
        return None
    
    mm, yy = m.groups()
    month = int(mm)
    year = int(yy)
    
    if not (1 <= month <= 12):
        return None
    
    # Convert 2-digit year to 4-digit (assume 20xx)
    if year < 100:
        year = 2000 + year
    
    return (year, month)


def enforce_13_month_window(df: pd.DataFrame, period_column: str = "Period") -> pd.DataFrame:
    """
    Filter dataframe to only include records from the 13-month rolling window.
    
    Args:
        df: DataFrame with period column
        period_column: Name of column containing MM-YY period labels
    
    Returns:
        Filtered DataFrame with validation warnings
    """
    if period_column not in df.columns:
        logger.warning(
            "Cannot enforce 13-month window: column '%s' not found. Available columns: %s",
            period_column,
            list(df.columns)
        )
        return df
    
    start_period, end_period, valid_periods = calculate_13_month_window()
    
    logger.info(
        "Enforcing 13-month window: %s through %s (%d periods)",
        start_period,
        end_period,
        len(valid_periods)
    )
    
    # Normalize period labels in dataframe
    df[period_column] = df[period_column].astype(str).str.strip()
    df[period_column] = df[period_column].str.replace(r"^Sum of ", "", regex=True).str.strip()
    
    # Filter to valid periods
    original_count = len(df)
    df_filtered = df[df[period_column].isin(valid_periods)].copy()
    filtered_count = len(df_filtered)
    
    if filtered_count < original_count:
        removed_periods = set(df[period_column].unique()) - set(valid_periods)
        logger.info(
            "Filtered out %d rows from %d periods outside 13-month window: %s",
            original_count - filtered_count,
            len(removed_periods),
            sorted(removed_periods)[:5]
        )
    
    # Validate coverage
    actual_periods = set(df_filtered[period_column].unique())
    missing_periods = set(valid_periods) - actual_periods
    
    if missing_periods:
        logger.warning(
            "13-month window incomplete: %d missing periods: %s",
            len(missing_periods),
            sorted(missing_periods)
        )
    
    if not df_filtered.empty:
        logger.info(
            "13-month window validated: %d periods present, %d rows",
            len(actual_periods),
            len(df_filtered)
        )
    
    return df_filtered


def normalize_monthly_accrual(df: pd.DataFrame, enforce_window: bool = False) -> pd.DataFrame:
    """
    Normalize Monthly Accrual and Usage Summary (default format).
    Handles Long format with Time Category, PeriodLabel, Sum of Value.
    Keeps PeriodLabel (overtime_timeoff_with_backfill expects it).
    """
    logger.info("Normalizing Monthly Accrual format (default)")
    
    # Normalize column names (keep PeriodLabel for OT backfill parser)
    rename_map = {
        "Time Category": "Time_Category",
        "Sum of Value": "Value",
        "Sum of  Value": "Value",  # double space variant
    }
    df = df.rename(columns=rename_map)

    if "PeriodLabel" in df.columns:
        df["PeriodLabel"] = df["PeriodLabel"].astype(str).str.strip()
        df["PeriodLabel"] = df["PeriodLabel"].str.replace(r"^Sum of ", "", regex=True).str.strip()
        if enforce_window:
            df = enforce_13_month_window(df, period_column="PeriodLabel")
    if "Value" in df.columns:
        df["Value"] = pd.to_numeric(df["Value"], errors="coerce").fillna(0)

    return df


def normalize_summons(df: pd.DataFrame, enforce_window: bool = False) -> pd.DataFrame:
    """
    Normalize Summons visual exports (Long format).
    Expected columns: PeriodLabel or Month_Year, Bureau or WG2, Moving/Parking or TYPE, Sum of Value or TICKET_COUNT.
    """
    logger.info("Normalizing Summons format")
    
    # Detect format: Long vs Wide
    cols = df.columns.tolist()
    month_like = [c for c in cols if isinstance(c, str) and _period_label_to_year_month(c) is not None]
    
    if month_like:
        logger.warning(
            "Summons export appears to be Wide format (month columns: %s). "
            "Long format (PeriodLabel) is required for backfill. Attempting to unpivot.",
            month_like[:5]
        )
        # Attempt to unpivot
        id_cols = [c for c in cols if c not in month_like]
        df = df.melt(id_vars=id_cols, value_vars=month_like, var_name="PeriodLabel", value_name="TICKET_COUNT")
    
    # Normalize column names
    rename_map = {
        "PeriodLabel": "Month_Year",
        "Bureau": "WG2",
        "Sum of Value": "TICKET_COUNT",
        "Value": "TICKET_COUNT",
        "Sum of TICKET_COUNT": "TICKET_COUNT",
        "Moving/Parking": "TYPE",
        "Type": "TYPE",
    }
    
    df = df.rename(columns=rename_map)
    
    # Clean period labels
    if "Month_Year" in df.columns:
        df["Month_Year"] = df["Month_Year"].astype(str).str.strip()
        df["Month_Year"] = df["Month_Year"].str.replace(r"^Sum of ", "", regex=True).str.strip()
        
        # Enforce 13-month window if requested
        if enforce_window:
            df = enforce_13_month_window(df, period_column="Month_Year")
    
    # Ensure TICKET_COUNT is numeric
    if "TICKET_COUNT" in df.columns:
        df["TICKET_COUNT"] = pd.to_numeric(df["TICKET_COUNT"], errors="coerce").fillna(0)
    
    # Ensure WG2 and TYPE exist
    if "WG2" not in df.columns:
        df["WG2"] = "Unknown"
    if "TYPE" not in df.columns:
        df["TYPE"] = "Unknown"
    
    df["WG2"] = df["WG2"].fillna("Unknown").astype(str)
    df["TYPE"] = df["TYPE"].fillna("Unknown").astype(str)
    
    return df


def normalize_training_cost(df: pd.DataFrame, enforce_window: bool = False) -> pd.DataFrame:
    """
    Normalize Training Cost by Delivery Method (Long format).
    Expected columns: Delivery_Type, PeriodLabel or period columns, Sum of Value or Cost.
    """
    logger.info("Normalizing Training Cost format")
    
    # Detect format: Long vs Wide
    cols = df.columns.tolist()
    month_like = [c for c in cols if isinstance(c, str) and _period_label_to_year_month(c) is not None]
    
    if month_like:
        logger.info("Training Cost export is Wide format (month columns: %s). Unpivoting to Long.", month_like[:5])
        # Unpivot
        id_cols = [c for c in cols if c not in month_like]
        df = df.melt(id_vars=id_cols, value_vars=month_like, var_name="PeriodLabel", value_name="Cost")
    
    # Normalize column names
    rename_map = {
        "PeriodLabel": "Period",
        "Delivery_Type": "Delivery_Type",
        "Sum of Value": "Cost",
        "Value": "Cost",
        "Sum of Cost": "Cost",
    }
    
    df = df.rename(columns=rename_map)
    
    # Clean period labels
    if "Period" in df.columns:
        df["Period"] = df["Period"].astype(str).str.strip()
        df["Period"] = df["Period"].str.replace(r"^Sum of ", "", regex=True).str.strip()
        
        # Enforce 13-month window if requested
        if enforce_window:
            df = enforce_13_month_window(df, period_column="Period")
    
    # Ensure Cost is numeric
    if "Cost" in df.columns:
        df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce").fillna(0)
    
    # Ensure Delivery_Type exists
    if "Delivery_Type" not in df.columns:
        df["Delivery_Type"] = "Unknown"
    
    return df


def normalize_response_time_series(df: pd.DataFrame, enforce_window: bool = False) -> pd.DataFrame:
    """
    Normalize response time series exports (Emergency/Routine/Urgent Total Response).
    Input has Date_Sort_Key (datetime) and a value column with "X.X min" format.
    """
    logger.info("Normalizing Response Time Series format")

    # Standardize date column
    date_col = "Date_Sort_Key"
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        # Derive MM-YY period label for window enforcement
        df["Period"] = df[date_col].dt.strftime("%m-%y")
        if enforce_window:
            df = enforce_13_month_window(df, period_column="Period")

    # Standardize value column: find the response time column
    value_cols = [c for c in df.columns if c != date_col and c != "Period"]
    for col in value_cols:
        if df[col].dtype == object:
            # Strip " min" suffix for numeric parsing
            df[col] = df[col].astype(str).str.replace(r"\s*min$", "", regex=True)

    return df


def normalize_response_time_priority_matrix(df: pd.DataFrame, enforce_window: bool = False) -> pd.DataFrame:
    """
    Normalize Response Time Trends by Priority exports.
    Input: MM-YY, RT Avg Formatted, Response_Type, Metric_Label.
    """
    logger.info("Normalizing Response Time Priority Matrix format")

    period_col = "MM-YY"
    if period_col in df.columns:
        df[period_col] = df[period_col].astype(str).str.strip()
        df[period_col] = df[period_col].str.replace(r"^Sum of ", "", regex=True).str.strip()
        if enforce_window:
            df = enforce_13_month_window(df, period_column=period_col)

    return df


def normalize_export(
    input_path: Path,
    output_path: Path,
    normalizer_format: str = "monthly_accrual",
    enforce_13_month: bool = False,
    dry_run: bool = False,
) -> bool:
    """
    Normalize a Power BI visual export and write to output_path.
    
    Args:
        input_path: Source CSV file
        output_path: Destination CSV file
        normalizer_format: Format type (monthly_accrual, summons, training_cost)
        enforce_13_month: If True, filter to 13-month rolling window
        dry_run: If True, preview only (no file write)
    
    Returns:
        True on success, False on failure
    """
    if not input_path.exists():
        logger.error("Input file not found: %s", input_path)
        return False
    
    try:
        # Read CSV
        df = pd.read_csv(input_path, low_memory=False)
        
        if df.empty:
            logger.warning("Input file is empty: %s", input_path)
            return False
        
        logger.info("Loaded %d rows from %s", len(df), input_path.name)
        
        # Apply normalization based on format
        if normalizer_format == "summons":
            df = normalize_summons(df, enforce_window=enforce_13_month)
        elif normalizer_format == "training_cost":
            df = normalize_training_cost(df, enforce_window=enforce_13_month)
        elif normalizer_format == "response_time_series":
            df = normalize_response_time_series(df, enforce_window=enforce_13_month)
        elif normalizer_format == "response_time_priority_matrix":
            df = normalize_response_time_priority_matrix(df, enforce_window=enforce_13_month)
        else:  # monthly_accrual (default)
            df = normalize_monthly_accrual(df, enforce_window=enforce_13_month)
        
        if df.empty:
            logger.error("After normalization, dataframe is empty. Check 13-month window filters.")
            return False
        
        if dry_run:
            logger.info("[DRY RUN] Would write %d rows to %s", len(df), output_path)
            logger.info("[DRY RUN] Preview (first 5 rows):\n%s", df.head())
            if enforce_13_month:
                period_col = next(
                    (c for c in ("PeriodLabel", "Period", "Month_Year") if c in df.columns),
                    None,
                )
                if period_col:
                    unique_periods = sorted(df[period_col].unique())
                    logger.info("[DRY RUN] Periods in output: %s", unique_periods)
            return True
        
        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False, encoding="utf-8")
        logger.info("Wrote %d rows to %s", len(df), output_path)
        return True
        
    except Exception as e:
        logger.error("Normalization failed: %s", e, exc_info=True)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize Power BI visual exports for backfill")
    parser.add_argument("--input", type=Path, required=True, help="Input CSV file")
    parser.add_argument("--output", type=Path, required=True, help="Output CSV file")
    parser.add_argument(
        "--format",
        choices=["monthly_accrual", "summons", "training_cost", "response_time_series", "response_time_priority_matrix"],
        default="monthly_accrual",
        help="Normalization format (default: monthly_accrual)"
    )
    parser.add_argument(
        "--enforce-13-month",
        action="store_true",
        help="Enforce 13-month rolling window (ending with previous complete month)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview only, do not write output")
    
    args = parser.parse_args()
    
    # Log 13-month window for reference
    if args.enforce_13_month:
        start, end, periods = calculate_13_month_window()
        logger.info("13-month window: %s to %s (%d periods)", start, end, len(periods))
    
    success = normalize_export(
        input_path=args.input,
        output_path=args.output,
        normalizer_format=args.format,
        enforce_13_month=args.enforce_13_month,
        dry_run=args.dry_run,
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
