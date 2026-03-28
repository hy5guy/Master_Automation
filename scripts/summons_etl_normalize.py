"""
summons_etl_normalize.py
Core normalization module with badge-based officer cleanup + statute lookup
Version 2.5.0 — DFR split (badge 738/Polson always; 2025/Ramirez & 377/Mazzaccaro by date range);
DFR records excluded from main pipeline. Fee enrichment: apply_fine_amount_and_violation_category()
uses municipal-violations-bureau-schedule.json + e-ticket Penalty; extended slim CSV for Power BI.

Resolves all 12 audit items: int badge key, column renames, slim CSV (financial + VIOLATION_CATEGORY),
WG1/WG2/TEAM correct, statute classification, RANK, robust DQ score, graceful degradation.
"""

import csv
import json
import logging
import os
import re
import shutil
from datetime import datetime, date as _date
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Override log for production overrides (PEO, Traffic Bureau)
OVERRIDE_LOG_PATH = "logs/summons_badge_overrides.txt"

# ---------------------------------------------------------------------------
# DFR (Drone / Directed Field Report) badge assignments
# Records matching these badge+date criteria are routed to the DFR workbook
# and excluded from the main summons pipeline counts.
# ---------------------------------------------------------------------------
DFR_ASSIGNMENTS: list[dict] = [
    # Polson — permanent drone operator at SSOCC; always DFR regardless of date
    {"badge": 738, "start_date": None, "end_date": None, "name": "Polson"},
    # Ramirez — temp SSOCC assignment 2026-02-23 through 2026-03-01
    {"badge": 2025, "start_date": _date(2026, 2, 23), "end_date": _date(2026, 3, 1), "name": "Ramirez"},
    # Mazzaccaro — temp SSOCC assignment 2026-03-02 through 2026-03-15
    {"badge": 377, "start_date": _date(2026, 3, 2), "end_date": _date(2026, 3, 15), "name": "Mazzaccaro"},
]


def _build_personnel_lookup(master_path: str) -> dict:
    """Build badge (int) -> officer info lookup. Uses int key for reliable matching."""
    master_df = pd.read_csv(master_path, dtype=str)
    lookup = {}
    for _, row in master_df.iterrows():
        badge_raw = str(row.get("BADGE_NUMBER", row.get("PADDED_BADGE_NUMBER", ""))).strip()
        if not badge_raw or badge_raw.lower() == "nan":
            continue
        try:
            badge = int(float(badge_raw))
        except (ValueError, TypeError):
            continue
        first = str(row.get("FIRST_NAME", "")).strip()
        last = str(row.get("LAST_NAME", "")).strip()
        title = str(row.get("TITLE", "")).strip()
        team = str(row.get("TEAM", "")).strip()
        wg1 = str(row.get("WG1", "")).strip() or str(row.get("TEAM", "")).strip() or "UNKNOWN"
        wg2 = str(row.get("WG2", "")).strip() or "UNKNOWN"
        padded = str(row.get("PADDED_BADGE_NUMBER", str(badge).zfill(4))).strip()
        if not padded or padded == "nan":
            padded = str(badge).zfill(4)
        standard_name = str(row.get("STANDARD_NAME", "")).strip()
        if not standard_name or standard_name.lower() == "nan":
            initial = first[0] if first else ""
            standard_name = f"{initial}. {last} #{padded}".strip()
        wg3 = str(row.get("WG3", "")).strip()
        wg4 = str(row.get("WG4", "")).strip()
        rank = str(row.get("RANK", "")).strip() or title
        lookup[badge] = {
            "FIRST_NAME": first,
            "LAST_NAME": last,
            "TITLE": title,
            "TEAM": team,
            "WG1": wg1,
            "WG2": wg2,
            "WG3": wg3,
            "WG4": wg4,
            "PADDED_BADGE_NUMBER": padded,
            "STANDARD_NAME": standard_name,
            "RANK": rank,
        }
    return lookup


def _load_municipal_fee_schedule(base_dir: Path) -> dict[str, dict]:
    """Load municipal-violations-bureau-schedule.json (statute → fine, case_type, description)."""
    path = (
        base_dir
        / "09_Reference"
        / "LegalCodes"
        / "data"
        / "Title39"
        / "municipal-violations-bureau-schedule.json"
    )
    if not path.exists():
        logger.warning("Municipal fee schedule not found at %s", path)
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.warning("Could not load municipal fee schedule: %s", e)
        return {}
    result: dict[str, dict] = {}
    for v in data.get("violations", []):
        statute = str(v.get("statute", "")).strip()
        if not statute:
            continue
        try:
            fine = float(v.get("fine_amount", 0) or 0)
        except (TypeError, ValueError):
            fine = 0.0
        result[statute] = {
            "description": str(v.get("description", "")).strip(),
            "fine_amount": fine,
            "case_type": str(v.get("case_type", "")).strip().upper(),
        }
    return result


def _load_statute_lookups(base_dir: Path) -> tuple[dict, dict]:
    """Load Title39 and city ordinance statute lookups (optional; empty dicts if missing)."""
    title39_path = base_dir / "09_Reference" / "LegalCodes" / "data" / "Title39" / "Title39_Lookup_Dict.json"
    ordinance_path = base_dir / "09_Reference" / "LegalCodes" / "data" / "CityOrdinances" / "CityOrdinances_Lookup_Dict.json"
    title39_dict: dict = {}
    ordinance_dict: dict = {}
    if title39_path.exists():
        try:
            with open(title39_path, encoding="utf-8") as f:
                title39_dict = json.load(f).get("lookup", {})
        except Exception as e:
            logger.warning("Could not load Title39 lookup: %s", e)
    else:
        logger.warning("Title39 lookup not found at %s", title39_path)
    if ordinance_path.exists():
        try:
            with open(ordinance_path, encoding="utf-8") as f:
                ordinance_dict = json.load(f).get("lookup", {})
        except Exception as e:
            logger.warning("Could not load ordinance lookup: %s", e)
    else:
        logger.warning("Ordinance lookup not found at %s", ordinance_path)
    return title39_dict, ordinance_dict


def _statute_lookup_candidates(raw: str) -> list[str]:
    """Ordered statute keys for fee lookup (exact, strip parens, strip trailing alpha segment)."""
    statute = str(raw).strip() if raw is not None and not (isinstance(raw, float) and np.isnan(raw)) else ""
    if not statute or statute.lower() == "nan":
        return []
    candidates = [statute]
    stripped = re.sub(r"\([^)]*\)$", "", statute).strip()
    if stripped and stripped not in candidates:
        candidates.append(stripped)
    stripped2 = re.sub(r"[A-Za-z]+$", "", stripped).rstrip("-").strip()
    if stripped2 and stripped2 not in candidates:
        candidates.append(stripped2)
    collapsed = re.sub(r"\s+", " ", statute)
    if collapsed not in candidates:
        candidates.append(collapsed)
    return candidates


def _fee_schedule_match(statute: str, fee_schedule: dict[str, dict]) -> tuple[dict | None, str | None]:
    """Return (entry, matched_key) for first matching candidate, else (None, None)."""
    for cand in _statute_lookup_candidates(statute):
        if cand in fee_schedule:
            return fee_schedule[cand], cand
    # Case-insensitive / whitespace-insensitive
    norm_map = {re.sub(r"\s+", "", k.lower()): (k, v) for k, v in fee_schedule.items()}
    for cand in _statute_lookup_candidates(statute):
        nk = re.sub(r"\s+", "", cand.lower())
        if nk in norm_map:
            orig_k, entry = norm_map[nk]
            return entry, orig_k
    # Suffix / prefix tie-break (short keys can false-positive; require min length)
    if len(statute) >= 4:
        for key in sorted(fee_schedule.keys(), key=len, reverse=True):
            if len(key) >= 4 and (statute.endswith(key) or key.endswith(statute)):
                return fee_schedule[key], key
    return None, None


def _violation_category_from_entry(
    case_type: str | None, type_letter: str | None, description: str | None
) -> str:
    """Human-readable category for Power BI (non-blank when TYPE is known)."""
    ct = (case_type or "").strip().upper()
    if ct in ("P", "M", "C"):
        return ct
    t = (type_letter or "").strip().upper()
    if t in ("P", "M", "C"):
        return t
    desc = (description or "").strip()
    if desc:
        return desc[:120]
    return t if t else "Unclassified"


def apply_fine_amount_and_violation_category(df: pd.DataFrame, base_dir: Path) -> pd.DataFrame:
    """
    Populate FINE_AMOUNT (from Penalty when > 0, else municipal fee schedule on STATUTE),
    VIOLATION_CATEGORY, and financial aliases for Power BI slim output.
    Rows with no trustworthy amount stay NaN for FINE_AMOUNT (not forced to 0).
    """
    if df.empty:
        return df
    df = df.copy()
    fee_schedule = _load_municipal_fee_schedule(base_dir)

    if "Penalty" in df.columns:
        penalty_num = pd.to_numeric(df["Penalty"].astype(str).str.replace(",", "", regex=False), errors="coerce")
    else:
        penalty_num = pd.Series(np.nan, index=df.index)

    fines: list[float] = []
    categories: list[str] = []
    unmapped_statutes: set[str] = set()

    for i in df.index:
        p = penalty_num.loc[i] if i in penalty_num.index else np.nan
        statute_val = df.at[i, "STATUTE"] if "STATUTE" in df.columns else ""
        statute_s = str(statute_val).strip() if pd.notna(statute_val) else ""
        type_letter = df.at[i, "TYPE"] if "TYPE" in df.columns else ""

        entry_match = None
        if statute_s and fee_schedule:
            entry_match, _matched_key = _fee_schedule_match(statute_s, fee_schedule)

        if pd.notna(p) and float(p) > 0:
            fine_out = float(p)
        elif entry_match is not None:
            fine_out = float(entry_match.get("fine_amount", 0) or 0)
        else:
            fine_out = np.nan

        if (
            fee_schedule
            and np.isnan(fine_out)
            and statute_s
            and statute_s.lower() != "nan"
            and entry_match is None
        ):
            unmapped_statutes.add(statute_s[:80])

        cat = _violation_category_from_entry(
            entry_match.get("case_type") if entry_match else None,
            str(type_letter) if pd.notna(type_letter) else None,
            entry_match.get("description") if entry_match else None,
        )
        fines.append(fine_out)
        categories.append(cat)

    df["FINE_AMOUNT"] = np.array(fines, dtype=float)
    df["VIOLATION_CATEGORY"] = categories

    # Optional e-ticket financial columns (aliases)
    def _coerce_money(col: str) -> pd.Series:
        if col not in df.columns:
            return pd.Series(np.nan, index=df.index)
        return pd.to_numeric(
            df[col].astype(str).str.replace(r"[$,]", "", regex=True), errors="coerce"
        )

    if "TOTAL_PAID_AMOUNT" not in df.columns:
        paid_col = next((c for c in df.columns if "paid" in str(c).lower() and "total" in str(c).lower()), None)
        if paid_col:
            df["TOTAL_PAID_AMOUNT"] = _coerce_money(paid_col)
        else:
            df["TOTAL_PAID_AMOUNT"] = np.nan
    else:
        df["TOTAL_PAID_AMOUNT"] = _coerce_money("TOTAL_PAID_AMOUNT")

    if "COST_AMOUNT" not in df.columns:
        cost_col = next((c for c in df.columns if str(c).lower() == "cost amount"), None)
        df["COST_AMOUNT"] = _coerce_money(cost_col) if cost_col else np.nan
    else:
        df["COST_AMOUNT"] = _coerce_money("COST_AMOUNT")

    if "MISC_AMOUNT" not in df.columns:
        df["MISC_AMOUNT"] = np.nan
    else:
        df["MISC_AMOUNT"] = _coerce_money("MISC_AMOUNT")

    if "VIOLATION_NUMBER" not in df.columns:
        df["VIOLATION_NUMBER"] = ""
    else:
        df["VIOLATION_NUMBER"] = df["VIOLATION_NUMBER"].astype(str).str.strip().replace({"nan": ""})

    if "VIOLATION_TYPE" not in df.columns:
        vt = next(
            (c for c in df.columns if "violation" in str(c).lower() and "type" in str(c).lower()),
            None,
        )
        if vt:
            df["VIOLATION_TYPE"] = df[vt].astype(str)
        else:
            df["VIOLATION_TYPE"] = df["TYPE"].astype(str) if "TYPE" in df.columns else ""

    if not fee_schedule:
        logger.warning(
            "Fine lookup skipped or incomplete: municipal-violations-bureau-schedule.json not found under "
            "09_Reference/LegalCodes/data/Title39/ — FINE_AMOUNT will only come from Penalty when present."
        )
    elif unmapped_statutes:
        sample = list(unmapped_statutes)[:12]
        logger.info(
            "Fine amount still blank for some rows (no Penalty and no fee-schedule match). "
            "Sample statutes: %s%s",
            sample,
            " ..." if len(unmapped_statutes) > 12 else "",
        )

    if "DATA_QUALITY_TIER" not in df.columns and "DATA_QUALITY_SCORE" in df.columns:
        df["DATA_QUALITY_TIER"] = df["DATA_QUALITY_SCORE"].apply(
            lambda s: "High" if pd.notna(s) and int(s) >= 80 else "Standard"
        )

    if "ASSIGNMENT_FOUND" not in df.columns:
        df["ASSIGNMENT_FOUND"] = True

    return df


def _classify_violation(row, title39_dict, ordinance_dict):
    """Use raw Case Type Code (M/P/C) from the e-ticket export directly.
    Statute-based classification was producing expanded types (License/Registration,
    Moving Violation, etc.) and ordinance substring matching was converting 2,576
    Parking tickets to C. Per SUMMONS_REMEDIATION_2026_02_17: use Case Type Code only."""
    raw_type = str(row.get("Case Type Code", "")).strip().upper()
    if raw_type in ("M", "P", "C"):
        return raw_type
    return "M"


def apply_hard_coded_overrides(df: pd.DataFrame) -> pd.DataFrame:
    """Apply production overrides for PEO/Traffic Bureau (preserved from hybrid)."""
    if "TITLE" not in df.columns:
        return df
    title_str = df["TITLE"].fillna("").astype(str).str.strip().str.upper()
    peo_mask = (title_str == "PARKING ENFORCEMENT OFFICER") | (title_str == "PEO")
    if peo_mask.sum() > 0:
        df = df.copy()
        df.loc[peo_mask, "WG2"] = "TRAFFIC BUREAU"
        df.loc[peo_mask, "TEAM"] = "TRAFFIC"
    if "PADDED_BADGE_NUMBER" in df.columns:
        peo_range = (df["WG2"].isna() | (df["WG2"] == "UNKNOWN")) & (
            df["PADDED_BADGE_NUMBER"].str.match(r"^20[0-9]{2}$", na=False)
        )
        if peo_range.sum() > 0:
            df = df.copy()
            df.loc[peo_range, "WG2"] = "TRAFFIC BUREAU"
            df.loc[peo_range, "TEAM"] = "TRAFFIC"
            df.loc[peo_range, "RANK"] = "PEO"
        known_traffic = {"0256": "GALLORINI"}
        for badge, name in known_traffic.items():
            mask = (df["PADDED_BADGE_NUMBER"] == badge) & (
                (df["WG2"].isna()) | (df["WG2"] != "TRAFFIC BUREAU")
            )
            if mask.sum() > 0:
                df = df.copy()
                df.loc[mask, "WG2"] = "TRAFFIC BUREAU"
                df.loc[mask, "TEAM"] = "TRAFFIC"
    return df


def _apply_pretty_csv_cleanup(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply DOpus pretty_csv.js–style cleanup (fallback when export not processed by DOpus).
    - Strip trailing commas from column names and values (export bug)
    - Drop empty Unnamed columns
    - Preserves leading zeros via dtype=str (handled at read).
    """
    if df.empty:
        return df
    df = df.copy()
    df.columns = [str(c).strip().rstrip(",") for c in df.columns]
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.rstrip(",")
    unnamed = [c for c in df.columns if str(c).strip().startswith("Unnamed")]
    if unnamed:
        df = df.drop(columns=unnamed, errors="ignore")
    return df


def _read_summons_csv(path: Path) -> pd.DataFrame:
    """Load e-ticket CSV; auto-detect delimiter (comma vs semicolon). Applies pretty_csv cleanup."""
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        first_line = f.readline()
    sep = ";" if ";" in first_line and first_line.count(";") > first_line.count(",") else ","
    try:
        df = pd.read_csv(
            path,
            sep=sep,
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
            on_bad_lines="skip",
            engine="python",
            encoding="utf-8-sig",
            dtype=str,
        )
    except (UnicodeDecodeError, ValueError):
        df = pd.read_csv(
            path,
            sep=sep,
            quotechar='"',
            on_bad_lines="skip",
            engine="python",
            encoding="cp1252",
            dtype=str,
        )
    return _apply_pretty_csv_cleanup(df)


def load_and_concatenate_summons(paths: list[Path]) -> tuple[pd.DataFrame, Path]:
    """
    Load multiple e-ticket CSVs, concatenate, preserve SOURCE_FILE per row.
    Returns (combined_df, temp_path_for_raw). Caller should delete temp_path after use.
    """
    import tempfile
    dfs = []
    for p in paths:
        df = _read_summons_csv(p)
        df["SOURCE_FILE"] = p.name
        dfs.append(df)
    combined = pd.concat(dfs, ignore_index=True)
    fd, tmp = tempfile.mkstemp(suffix=".csv")  # system temp to avoid OneDrive handle lock
    os.close(fd)
    combined.to_csv(tmp, index=False, encoding="utf-8-sig")
    return combined, Path(tmp)


def normalize_personnel_data(summons_path: str, master_path: str, output_path: str, df: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Normalize summons data: badge-based officer enrichment, statute classification, derived columns.
    Backward-compatible 3-param signature. Pass df= to use pre-loaded data (e.g. from load_and_concatenate_summons).
    """
    if df is None:
        df = _read_summons_csv(Path(summons_path))

    # Preserve raw officer fields for audit
    for col in ["Officer First Name", "Officer Middle Initial", "Officer Last Name"]:
        if col in df.columns:
            df = df.rename(columns={col: f"RAW_{col.replace(' ', '_').upper()}"})

    base_dir = Path(master_path).resolve().parents[2]
    lookup = _build_personnel_lookup(master_path)
    title39_dict, ordinance_dict = _load_statute_lookups(base_dir)

    unmatched = {}
    df["_MATCHED"] = 0
    for idx, row in df.iterrows():
        badge_str = str(row.get("Officer Id", "")).strip()
        try:
            badge = int(float(badge_str)) if badge_str else None
        except (ValueError, TypeError):
            badge = None
        if badge is not None and badge in lookup:
            info = lookup[badge]
            df.at[idx, "Officer First Name"] = info["FIRST_NAME"]
            df.at[idx, "Officer Last Name"] = info["LAST_NAME"]
            df.at[idx, "Officer Middle Initial"] = ""
            df.at[idx, "OFFICER_DISPLAY_NAME"] = info["STANDARD_NAME"]
            df.at[idx, "TITLE"] = info["TITLE"]
            df.at[idx, "TEAM"] = info["TEAM"]
            df.at[idx, "WG1"] = info["WG1"]
            df.at[idx, "WG2"] = info["WG2"]
            df.at[idx, "WG3"] = info["WG3"]
            df.at[idx, "WG4"] = info["WG4"]
            df.at[idx, "PADDED_BADGE_NUMBER"] = info["PADDED_BADGE_NUMBER"]
            df.at[idx, "RANK"] = info["RANK"]
            df.at[idx, "_MATCHED"] = 1
        else:
            unmatched[badge_str] = unmatched.get(badge_str, 0) + 1
            df.at[idx, "Officer First Name"] = row.get("RAW_OFFICER_FIRST_NAME", "")
            df.at[idx, "Officer Last Name"] = row.get("RAW_OFFICER_LAST_NAME", "")
            df.at[idx, "Officer Middle Initial"] = row.get("RAW_OFFICER_MI", "")
            df.at[idx, "OFFICER_DISPLAY_NAME"] = (
                f"{row.get('RAW_OFFICER_FIRST_NAME', '')} {row.get('RAW_OFFICER_LAST_NAME', '')}".strip()
            )
            df.at[idx, "PADDED_BADGE_NUMBER"] = str(badge).zfill(4) if badge is not None else (badge_str.zfill(4) if badge_str else "")
            df.at[idx, "WG1"] = "UNKNOWN"
            df.at[idx, "WG2"] = "UNKNOWN"
            df.at[idx, "WG3"] = ""
            df.at[idx, "WG4"] = ""
            df.at[idx, "RANK"] = ""

    if unmatched:
        logger.warning("Unmatched badges (kept raw values): %s (e.g., Badge 9110 ANNUNZIATA)", list(unmatched.keys())[:5])

    df = apply_hard_coded_overrides(df)
    df["WG2"] = df["WG2"].fillna("UNKNOWN")

    df["TYPE"] = df.apply(lambda r: _classify_violation(r, title39_dict, ordinance_dict), axis=1)

    date_col = next((c for c in ["Issue Date", "Issue_Date", "Entered Date"] if c in df.columns), None)
    if not date_col:
        raise ValueError(f"No date column found. Available: {list(df.columns)[:20]}...")
    df["Issue_Date_dt"] = pd.to_datetime(df[date_col], errors="coerce")
    df["YearMonthKey"] = df["Issue_Date_dt"].dt.strftime("%Y%m").fillna("0").astype(int)
    df["Month_Year"] = df["Issue_Date_dt"].dt.strftime("%m-%y")
    df["Year"] = df["Issue_Date_dt"].dt.year.fillna(0).astype(int)
    df["Month"] = df["Issue_Date_dt"].dt.month.fillna(0).astype(int)
    df["TICKET_COUNT"] = 1
    df["IS_AGGREGATE"] = False
    df["ETL_VERSION"] = "ETICKET_CURRENT"
    df["OFFICER_NAME_RAW"] = df.apply(
        lambda r: f"{r.get('RAW_OFFICER_FIRST_NAME', '')} {r.get('RAW_OFFICER_LAST_NAME', '')}".strip(), axis=1
    )
    if "SOURCE_FILE" not in df.columns:
        df["SOURCE_FILE"] = Path(summons_path).name if summons_path else "unknown"
    df["PROCESSING_TIMESTAMP"] = datetime.now().isoformat()

    # DATA_QUALITY_SCORE: 100 if personnel matched (enrichment-based, robust)
    df["DATA_QUALITY_SCORE"] = df["_MATCHED"].map({1: 100, 0: 50}).fillna(50).astype(int)
    df = df.drop(columns=["_MATCHED"], errors="ignore")

    if "Issue_Date_dt" in df.columns:
        df = df.drop(columns=["Issue_Date_dt"])

    # UPPER_SNAKE_CASE renames for M-code compatibility
    rename_map = {
        "Ticket Number": "TICKET_NUMBER",
        "Case Status Code": "STATUS",
        "Statute": "STATUTE",
        "Violation Description": "VIOLATION_DESCRIPTION",
        "Violation Number": "VIOLATION_NUMBER",
    }
    if date_col and date_col != "ISSUE_DATE":
        rename_map[date_col] = "ISSUE_DATE"
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    return df


def write_three_tier_output(df: pd.DataFrame, output_xlsx: str, original_summons_path: str) -> None:
    """Write 3 output tiers: RAW (copy), CLEAN (Excel), SLIM CSV for Power BI (incl. FINE_AMOUNT, VIOLATION_CATEGORY)."""
    output_dir = Path(output_xlsx).parent
    base_name = datetime.now().strftime("%Y_%m") + "_eticket_export"

    raw_path = output_dir / f"{base_name}_RAW.csv"
    shutil.copy2(original_summons_path, raw_path)
    logger.info("RAW saved: %s", raw_path.name)

    df.to_excel(output_xlsx, sheet_name="Summons_Data", index=False)
    logger.info("CLEAN full saved: %s (%s rows)", Path(output_xlsx).name, len(df))

    slim_cols = [
        "TICKET_NUMBER",
        "STATUS",
        "ISSUE_DATE",
        "STATUTE",
        "VIOLATION_NUMBER",
        "VIOLATION_DESCRIPTION",
        "VIOLATION_TYPE",
        "VIOLATION_CATEGORY",
        "OFFICER_DISPLAY_NAME",
        "PADDED_BADGE_NUMBER",
        "TYPE",
        "WG1",
        "WG2",
        "WG3",
        "WG4",
        "TEAM",
        "YearMonthKey",
        "Month_Year",
        "Year",
        "Month",
        "TICKET_COUNT",
        "IS_AGGREGATE",
        "ETL_VERSION",
        "DATA_QUALITY_SCORE",
        "DATA_QUALITY_TIER",
        "OFFICER_NAME_RAW",
        "SOURCE_FILE",
        "PROCESSING_TIMESTAMP",
        "TITLE",
        "RANK",
        "TOTAL_PAID_AMOUNT",
        "FINE_AMOUNT",
        "COST_AMOUNT",
        "MISC_AMOUNT",
        "ASSIGNMENT_FOUND",
    ]
    slim_df = df[[c for c in slim_cols if c in df.columns]].copy()
    for col in ("WG1", "WG2", "WG3", "WG4", "TEAM"):
        if col in slim_df.columns:
            slim_df[col] = slim_df[col].fillna("").replace("nan", "")
    slim_path = output_dir / "summons_slim_for_powerbi.csv"
    slim_df.to_csv(slim_path, index=False, encoding="utf-8-sig")
    logger.info("SLIM Power BI version saved: %s (%s rows, %s cols)", slim_path.name, len(slim_df), len(slim_df.columns))


def split_dfr_records(
    df: pd.DataFrame, assignments: list[dict] | None = None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split DataFrame into (dfr_records, main_records).

    DFR records are those issued by drone operators during their SSOCC assignment
    periods. They are excluded from the main summons pipeline and written to the
    DFR directed-patrol workbook instead.

    Args:
        df: Fully normalized summons DataFrame (from normalize_personnel_data).
        assignments: List of DFR assignment dicts. Defaults to DFR_ASSIGNMENTS.

    Returns:
        (dfr_df, main_df) — both are copies; indexes are reset.
    """
    if assignments is None:
        assignments = DFR_ASSIGNMENTS

    # Parse issue dates for date-range checks
    issue_dates = pd.to_datetime(df.get("ISSUE_DATE", pd.Series(dtype=str)), errors="coerce").dt.date

    # Parse badge numbers — PADDED_BADGE_NUMBER is a zero-padded string like "0738"
    badges = pd.to_numeric(df.get("PADDED_BADGE_NUMBER", pd.Series(dtype=str)), errors="coerce")

    dfr_mask = pd.Series(False, index=df.index)
    for assignment in assignments:
        badge_mask = badges == assignment["badge"]
        if assignment["start_date"] is None:
            # Always DFR (no date restriction)
            dfr_mask |= badge_mask
        else:
            date_mask = (
                (issue_dates >= assignment["start_date"])
                & (issue_dates <= assignment["end_date"])
            )
            dfr_mask |= (badge_mask & date_mask)

    dfr_count = dfr_mask.sum()
    if dfr_count > 0:
        logger.info(
            "DFR split: %d record(s) routed to DFR workbook (excluded from main pipeline)",
            dfr_count,
        )
    return df[dfr_mask].reset_index(drop=True), df[~dfr_mask].reset_index(drop=True)
