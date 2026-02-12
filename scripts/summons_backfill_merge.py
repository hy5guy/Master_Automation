#!/usr/bin/env python3
"""
Merge Department-Wide Summons backfill for gap months (03-25, 07-25, 10-25, 11-25).

INJECTION POINT (in 02_ETL_Scripts/Summons/main_orchestrator.py):
  After the main summons dataframe is loaded (the one that feeds Department-Wide Summons):
    df = merge_missing_summons_months(df)

Loads from Backfill\\{backfill_month_label}\\summons\\, normalizes visual-export column names
to ETL schema, and concatenates rows. Uses low_memory=False and explicit dtypes to avoid
Pandas DtypeWarnings. Schema drift: if Power BI export renames columns (e.g. "Sum of Value"
-> "Total"), update RENAME_MAP below.
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

# Gap months identified for Department-Wide Summons (missing in e-ticket exports)
SUMMONS_GAP_MONTHS = ("03-25", "07-25", "10-25", "11-25")
DEFAULT_BACKFILL_SUMMONS_LABEL = "2025_12"

# Map visual-export / backfill CSV headers to ETL schema (update if Power BI export format changes)
RENAME_MAP = {
    "PeriodLabel": "Month_Year",
    "Bureau": "WG2",
    "Sum of Value": "TICKET_COUNT",
    "Value": "TICKET_COUNT",
    "Sum of TICKET_COUNT": "TICKET_COUNT",
    "Moving/Parking": "TYPE",
    "Type": "TYPE",
}

# Minimum columns we need for merged rows (main ETL may have more)
TARGET_COLUMNS = ["Month_Year", "WG2", "TICKET_COUNT", "TYPE"]


def _get_backfill_root() -> Path:
    return get_onedrive_root() / "PowerBI_Date" / "Backfill"


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
    root = backfill_root or _get_backfill_root()
    summons_dir = root / backfill_month_label / "summons"

    if not summons_dir.exists():
        logger.warning("Backfill summons directory not found: %s; skipping merge.", summons_dir)
        return df

    backfill_dfs: list[pd.DataFrame] = []

    try:
        all_files = list(summons_dir.glob("*.csv"))
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
            matching_files = [f for f in all_files if yyyy_mm in f.name]

            if not matching_files:
                logger.warning(
                    "No backfill file found for gap month %s (looked for %s in name)",
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

        # Ensure target schema columns exist (handles empty main df or minimal backfill)
        for col in TARGET_COLUMNS:
            if col not in combined_backfill.columns:
                combined_backfill[col] = pd.NA

        # Align to main df columns if valid (so concat does not create extra columns)
        if hasattr(df, "columns") and len(df.columns) > 0:
            for col in df.columns:
                if col not in combined_backfill.columns:
                    combined_backfill[col] = pd.NA
            combined_backfill = combined_backfill.reindex(columns=df.columns, copy=False)

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
