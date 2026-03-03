#!/usr/bin/env python3
"""
Merge Department-Wide Summons backfill for gap months (03-25, 07-25, 10-25, 11-25).

Backfill is only needed for the **Department-Wide Summons | Moving and Parking** visual,
which shows a rolling 13-month total. Other summons visuals use monthly data only and
do not need backfill rows.

INJECTION POINT (in run_summons_etl.py): after normalize_personnel_data(), merge then
overwrite Excel so the 13-month trend query sees backfill + current month.

Loads from Backfill\\{backfill_month_label}\\summons\\, normalizes visual-export column names
to ETL schema, and concatenates rows. Schema drift: if Power BI export renames columns
(e.g. "Sum of Value" -> "Total"), update RENAME_MAP below.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

try:
    from path_config import get_onedrive_root
except ImportError:
    def get_onedrive_root() -> Path:
        base = os.environ.get("ONEDRIVE_BASE") or os.environ.get("ONEDRIVE_HACKENSACK")
        if base:
            return Path(base)
        return Path(r"C:\Users\carucci_r\OneDrive - City of Hackensack")

if TYPE_CHECKING:
    import pandas as pd

# Gap months (missing in e-ticket exports)
SUMMONS_GAP_MONTHS = ("03-25", "07-25", "10-25", "11-25")
# Months to prefer backfill when e-ticket exists (backfill has validated totals from prior report)
SUMMONS_BACKFILL_PREFER_MONTHS = ("01-25", "02-25")
# All 2025 months in consolidated backfill (for full 13-month coverage when e-ticket discovery fails)
SUMMONS_BACKFILL_ALL_2025 = tuple(f"{m:02d}-25" for m in range(1, 13))
# Prefer most recent backfill (last month's report); fallback to 2025_12
DEFAULT_BACKFILL_SUMMONS_LABEL = "2026_01"
FALLBACK_BACKFILL_LABELS = ("2025_12",)

# Map visual-export / backfill CSV headers to ETL schema (update if Power BI export format changes)
RENAME_MAP = {
    "PeriodLabel": "Month_Year",
    "Period": "Month_Year",  # 2026_01 export uses "Period" not "PeriodLabel"
    "Bureau": "WG2",
    "Sum of Value": "TICKET_COUNT",
    "Value": "TICKET_COUNT",
    "Sum of TICKET_COUNT": "TICKET_COUNT",
    "Moving/Parking": "TYPE",
    "Type": "TYPE",
    "Time Category": "TYPE",
}

# Minimum columns we need for merged rows (main ETL may have more)
TARGET_COLUMNS = ["Month_Year", "WG2", "TICKET_COUNT", "TYPE"]


def _get_backfill_roots() -> list[Path]:
    """Return candidate backfill roots (prefer 00_dev, then PowerBI_Date)."""
    base = get_onedrive_root()
    return [
        base / "00_dev" / "projects" / "PowerBI_Date" / "Backfill",
        base / "PowerBI_Date" / "Backfill",
    ]


def _log() -> logging.Logger:
    return logging.getLogger("summons_backfill_merge")


def merge_missing_summons_months(
    df: "pd.DataFrame",
    backfill_root: Path | None = None,
    backfill_month_label: str = DEFAULT_BACKFILL_SUMMONS_LABEL,
) -> "pd.DataFrame":
    """
    Merge backfill data for gap months into the main summons dataframe.
    Loads CSVs from Backfill\\{backfill_month_label}\\summons\\, normalizes schema,
    and appends rows. Ensures WG2 (Bureau) and TICKET_COUNT are set to avoid blank visuals.
    """
    import pandas as pd

    logger = _log()
    roots = [backfill_root] if backfill_root else _get_backfill_roots()
    labels_to_try = [backfill_month_label] + list(FALLBACK_BACKFILL_LABELS)
    summons_dir = None
    for root in roots:
        if not root or not root.exists():
            continue
        for label in labels_to_try:
            cand = root / label / "summons"
            if cand.exists():
                summons_dir = cand
                logger.info("Using backfill: %s", summons_dir)
                break
        if summons_dir:
            break
    if not summons_dir or not summons_dir.exists():
        logger.warning("No backfill summons directory found; tried roots=%s labels=%s", roots, labels_to_try)
        return df

    backfill_dfs: list[pd.DataFrame] = []

    try:
        all_files = list(summons_dir.glob("*.csv"))
        # Prefer consolidated department_wide_summons (has all gap months in Long format)
        # Match "department_wide_summons" or "Department-Wide Summons" (2026_01 export naming)
        consolidated = [
            f for f in all_files
            if "department_wide_summons" in f.name.lower() or "department-wide summons" in f.name.lower()
        ]
        if consolidated:
            for file_path in consolidated:
                try:
                    bf_data = pd.read_csv(file_path, low_memory=False)
                    if bf_data.empty:
                        continue
                    # Accept PeriodLabel, Period, or Month_Year (2026_01 export uses "Period")
                    if not any(c in bf_data.columns for c in ("PeriodLabel", "Period", "Month_Year")):
                        continue
                    bf_data = bf_data.rename(columns=RENAME_MAP)
                    if "Month_Year" not in bf_data.columns:
                        continue
                    # Add backfill: when main df has few months (e-ticket discovery failed), merge ALL 2025
                    # Otherwise: gap months + prefer months (01-25, 02-25) for consistent values
                    main_month_count = (df["Month_Year"].nunique()) if "Month_Year" in df.columns else 0
                    if main_month_count < 5:
                        gap_to_add = list(SUMMONS_BACKFILL_ALL_2025)
                        logger.info("Main df has %s months; merging full 2025 backfill for 13-month coverage", main_month_count)
                    else:
                        gap_to_add = list(SUMMONS_BACKFILL_PREFER_MONTHS)
                        for m in SUMMONS_GAP_MONTHS:
                            if (df["Month_Year"] == m).sum() > 10:
                                logger.debug("Skipping backfill for %s: main df has e-ticket data", m)
                            else:
                                gap_to_add.append(m)
                    bf_data = bf_data[bf_data["Month_Year"].isin(gap_to_add)].copy()
                    if bf_data.empty:
                        continue
                    if "TICKET_COUNT" not in bf_data.columns:
                        bf_data["TICKET_COUNT"] = 1
                    bf_data["TICKET_COUNT"] = pd.to_numeric(bf_data["TICKET_COUNT"], errors="coerce").fillna(0)
                    if "WG2" not in bf_data.columns:
                        bf_data["WG2"] = "Department-Wide"
                    bf_data["WG2"] = bf_data["WG2"].fillna("Department-Wide").astype(str)
                    if "TYPE" not in bf_data.columns:
                        bf_data["TYPE"] = "Unknown"
                    cols_to_keep = [c for c in TARGET_COLUMNS if c in bf_data.columns]
                    bf_data = bf_data[cols_to_keep].copy()
                    backfill_dfs.append(bf_data)
                    logger.info(
                        "Loaded gap months from consolidated file %s: %s rows",
                        file_path.name,
                        len(bf_data),
                    )
                    break
                except Exception as e:
                    logger.error("Failed to process consolidated backfill file %s: %s", file_path, e)

        # Fallback: per-month files (only if consolidated not used)
        if not backfill_dfs:
            for gap_month in SUMMONS_GAP_MONTHS:
                # Expect MM-YY (e.g. 03-25); reject YYYY-MM or malformed to avoid wrong filenames
                parts = gap_month.split("-")
                if len(parts) != 2 or len(parts[0]) != 2 or len(parts[1]) != 2:
                    logger.warning(
                        "Gap month %r does not match MM-YY; skipping (use e.g. 03-25).",
                        gap_month,
                    )
                    continue
                mm, yy = parts
                if not (mm.isdigit() and yy.isdigit()):
                    logger.warning("Gap month %r has non-digit parts; skipping.", gap_month)
                    continue
                yyyy_mm = f"20{yy}_{mm}"
                # Require filename to start with yyyy_mm to avoid matching timestamps (e.g. 2025_10_09)
                matching_files = [f for f in all_files if f.name.startswith(yyyy_mm + "_")]

                if not matching_files:
                    logger.warning(
                        "No backfill file found for gap month %s (looked for %s at start of name)",
                        gap_month,
                        yyyy_mm,
                    )
                    continue

                for file_path in matching_files:
                    try:
                        bf_data = pd.read_csv(file_path, low_memory=False)
                        if bf_data.empty:
                            continue

                        # Wide format (months as columns) not supported; need Long (PeriodLabel)
                        if "PeriodLabel" not in bf_data.columns and "Month_Year" not in bf_data.columns:
                            month_like = [c for c in bf_data.columns if isinstance(c, str) and len(c) == 5 and c[2] == "-" and c[:2].isdigit() and c[3:5].isdigit()]
                            if month_like:
                                logger.warning(
                                    "Backfill file %s looks like Wide format (month columns: %s). Long format (PeriodLabel) is required for Summons backfill.",
                                    file_path.name,
                                    month_like[:5],
                                )
                                continue

                        # Normalize: visual export columns -> ETL schema
                        bf_data = bf_data.rename(columns=RENAME_MAP)

                        # Log columns to help debug schema drift (e.g. "Bureau Name" vs "Bureau")
                        if "Month_Year" not in bf_data.columns or "TICKET_COUNT" not in bf_data.columns:
                            logger.debug(
                                "Backfill file %s columns after rename: %s",
                                file_path.name,
                                list(bf_data.columns),
                            )

                        if "Month_Year" in bf_data.columns:
                            bf_data = bf_data[bf_data["Month_Year"] == gap_month].copy()
                        if bf_data.empty:
                            continue

                        if "TICKET_COUNT" not in bf_data.columns:
                            bf_data["TICKET_COUNT"] = 1
                        bf_data["TICKET_COUNT"] = pd.to_numeric(bf_data["TICKET_COUNT"], errors="coerce").fillna(0)

                        if "WG2" not in bf_data.columns:
                            bf_data["WG2"] = "Unknown"
                        bf_data["WG2"] = bf_data["WG2"].fillna("Unknown").astype(str)

                        if "TYPE" not in bf_data.columns:
                            bf_data["TYPE"] = "Unknown"

                        cols_to_keep = [c for c in TARGET_COLUMNS if c in bf_data.columns]
                        bf_data = bf_data[cols_to_keep].copy()
                        backfill_dfs.append(bf_data)
                        logger.info("Loaded %s rows for %s from %s", len(bf_data), gap_month, file_path.name)

                    except Exception as e:
                        logger.error("Failed to process backfill file %s: %s", file_path, e)

        if not backfill_dfs:
            return df

        combined_backfill = pd.concat(backfill_dfs, ignore_index=True)

        # Add unique Ticket Number for backfill rows (required for Power BI relationships; blanks cause load errors)
        n = len(combined_backfill)
        if "Month_Year" in combined_backfill.columns and "TYPE" in combined_backfill.columns:
            combined_backfill["Ticket Number"] = [
                f"BACKFILL_{combined_backfill.iloc[i]['Month_Year']}_{combined_backfill.iloc[i]['TYPE']}_{i:06d}"
                for i in range(n)
            ]
        else:
            combined_backfill["Ticket Number"] = [f"BACKFILL_{i:08d}" for i in range(n)]

        # Derive YearMonthKey from Month_Year so M code filter (YearMonthKey between StartYM and EndYM) includes backfill
        if "Month_Year" in combined_backfill.columns:
            def _month_year_to_key(val):
                if pd.isna(val) or not isinstance(val, str):
                    return pd.NA
                parts = val.strip().split("-")
                if len(parts) != 2 or len(parts[0]) != 2 or len(parts[1]) != 2:
                    return pd.NA
                mm, yy = parts[0], parts[1]
                if not (mm.isdigit() and yy.isdigit()):
                    return pd.NA
                return int(f"20{yy}{mm}")

            combined_backfill["YearMonthKey"] = combined_backfill["Month_Year"].map(_month_year_to_key)

        # Ensure target schema columns exist (handles empty main df or minimal backfill)
        for col in TARGET_COLUMNS:
            if col not in combined_backfill.columns:
                combined_backfill[col] = pd.NA

        # Align to main df columns if valid (so concat does not create extra columns)
        if hasattr(df, "columns") and len(df.columns) > 0:
            combined_backfill = combined_backfill.reindex(columns=df.columns, fill_value=pd.NA)

        # Match TICKET_COUNT dtype to main df to avoid DtypeWarning
        if "TICKET_COUNT" in df.columns and "TICKET_COUNT" in combined_backfill.columns:
            combined_backfill["TICKET_COUNT"] = combined_backfill["TICKET_COUNT"].astype(
                df["TICKET_COUNT"].dtype, copy=False
            )

        merged_df = pd.concat([df, combined_backfill], ignore_index=True, sort=False)
        logger.info("Merged %s backfill rows into main dataframe.", len(combined_backfill))
        return merged_df

    except Exception as e:
        logger.error("Error during summons backfill merge: %s", e)
        return df
