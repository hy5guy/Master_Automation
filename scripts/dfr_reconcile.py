"""
dfr_reconcile.py
Phase 5 — Fee Schedule Integration & Data Reconciliation

Maps Full Summons Number (DFR workbook) → TICKET_NUMBER (ETL export).
On match: validates field alignment (Date, Statute, Officer).
On mismatch/missing: backfills Description and Fine Amount from fee schedule.
Verifies legal code lookups resolve for all statutes in the DFR workbook.

Usage:
    python dfr_reconcile.py [--dry-run]

Target workbook:
    <OneDrive>/Shared Folder/Compstat/Contributions/Drone/dfr_directed_patrol_enforcement.xlsx
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

try:
    from path_config import get_onedrive_root
except ImportError:
    import os
    def get_onedrive_root() -> Path:
        base = os.environ.get("ONEDRIVE_BASE") or os.environ.get("ONEDRIVE_HACKENSACK")
        if base:
            return Path(base)
        return Path.home() / "OneDrive - City of Hackensack"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ---------------------------------------------------------------------------
# Legal code lookup loaders
# ---------------------------------------------------------------------------

def _load_fee_schedule(base: Path) -> dict[str, dict]:
    """Load municipal-violations-bureau-schedule.json.
    Returns dict keyed by statute code → {description, fine_amount, case_type}."""
    path = base / "09_Reference" / "LegalCodes" / "data" / "Title39" / "municipal-violations-bureau-schedule.json"
    if not path.exists():
        logger.warning("Fee schedule not found: %s", path)
        return {}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    result = {}
    for v in data.get("violations", []):
        statute = v.get("statute", "").strip()
        if statute:
            result[statute] = {
                "description": v.get("description", ""),
                "fine_amount": v.get("fine_amount", 0.0),
                "case_type": v.get("case_type", ""),
            }
    return result


def _load_ordinance_lookup(base: Path) -> dict[str, dict]:
    """Load CityOrdinances_Lookup_Dict.json.
    Returns dict keyed by ordinance code → {description, case_type_code}."""
    path = base / "09_Reference" / "LegalCodes" / "data" / "CityOrdinances" / "CityOrdinances_Lookup_Dict.json"
    if not path.exists():
        logger.warning("Ordinance lookup not found: %s", path)
        return {}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("lookup", {})


def _load_violation_data(wb_path: Path) -> dict[str, dict]:
    """Load ViolationData sheet from the DFR workbook.
    Returns dict keyed by ViolationCode → {description, fine_amount, source_type, violation_type}."""
    try:
        df = pd.read_excel(wb_path, sheet_name="ViolationData", dtype=str)
    except Exception as e:
        logger.warning("Could not read ViolationData sheet: %s", e)
        return {}
    result = {}
    for _, row in df.iterrows():
        code = str(row.get("ViolationCode", "")).strip()
        if code:
            fine_str = str(row.get("FineAmount", "0")).strip()
            try:
                fine = float(fine_str) if fine_str else 0.0
            except ValueError:
                fine = 0.0
            result[code] = {
                "description": str(row.get("Description", "")).strip(),
                "fine_amount": fine,
                "source_type": str(row.get("SourceType", "")).strip(),
                "violation_type": str(row.get("ViolationType", "")).strip(),
            }
    return result


# ---------------------------------------------------------------------------
# Reconciliation logic
# ---------------------------------------------------------------------------

def reconcile(dry_run: bool = False) -> dict:
    """Run the full reconciliation.
    Returns a summary dict with counts and issues."""

    base = get_onedrive_root()
    wb_path = base / "Shared Folder" / "Compstat" / "Contributions" / "Drone" / "dfr_directed_patrol_enforcement.xlsx"
    etl_path = base / "03_Staging" / "Summons" / "summons_slim_for_powerbi.csv"

    if not wb_path.exists():
        logger.error("DFR workbook not found: %s", wb_path)
        return {"error": "DFR workbook not found"}

    # --- Load DFR Summons Log ---
    dfr_df = pd.read_excel(wb_path, sheet_name="DFR Summons Log", dtype=str)
    # Drop rows with no Summons Number (empty formula rows)
    dfr_df = dfr_df[dfr_df["Summons Number"].notna() & (dfr_df["Summons Number"].str.strip() != "")]
    logger.info("DFR workbook: %d records loaded", len(dfr_df))

    # Build Full Summons Number — handle two data entry patterns:
    #   1. Manual entry: Summons Number = "008776" → Full = "E26008776"
    #   2. ETL-injected: Summons Number = "E26005452" (already has prefix) → Full = "E26005452"
    sn = dfr_df["Summons Number"].str.strip()
    already_prefixed = sn.str.upper().str.startswith("E2", na=False)

    if "Full Summons Number" not in dfr_df.columns or dfr_df["Full Summons Number"].isna().all():
        dfr_df["Full Summons Number"] = ""
        dfr_df.loc[already_prefixed, "Full Summons Number"] = sn[already_prefixed]
        dfr_df.loc[~already_prefixed, "Full Summons Number"] = "E26" + sn[~already_prefixed]
    else:
        mask = dfr_df["Full Summons Number"].isna() | (dfr_df["Full Summons Number"].str.strip() == "")
        dfr_df.loc[mask & already_prefixed, "Full Summons Number"] = sn[mask & already_prefixed]
        dfr_df.loc[mask & ~already_prefixed, "Full Summons Number"] = "E26" + sn[mask & ~already_prefixed]

    # --- Load ETL export ---
    if etl_path.exists():
        etl_df = pd.read_csv(etl_path, dtype=str)
        logger.info("ETL export: %d records loaded", len(etl_df))
        etl_lookup = {}
        for _, row in etl_df.iterrows():
            ticket = str(row.get("TICKET_NUMBER", "")).strip()
            if ticket:
                etl_lookup[ticket] = row.to_dict()
    else:
        logger.warning("ETL export not found: %s — skipping ticket matching", etl_path)
        etl_lookup = {}

    # --- Load fee/lookup data ---
    fee_schedule = _load_fee_schedule(base)
    ordinances = _load_ordinance_lookup(base)
    violation_data = _load_violation_data(wb_path)

    logger.info("Fee schedule: %d statutes", len(fee_schedule))
    logger.info("Ordinances: %d codes", len(ordinances))
    logger.info("ViolationData: %d entries", len(violation_data))

    # --- Reconciliation ---
    matched = 0
    unmatched = 0
    field_mismatches = []
    backfill_candidates = []
    statute_resolved = 0
    statute_unresolved = []

    for idx, row in dfr_df.iterrows():
        full_num = str(row.get("Full Summons Number", "")).strip()
        statute = str(row.get("Statute", "")).strip()
        dfr_date = str(row.get("Date", "")).strip()

        # 1. Match against ETL export
        etl_row = etl_lookup.get(full_num)
        if etl_row:
            matched += 1

            # Validate field alignment
            mismatches = []
            etl_statute = str(etl_row.get("STATUTE", "")).strip()
            if statute and etl_statute and statute.upper() != etl_statute.upper():
                mismatches.append(f"Statute: DFR={statute} vs ETL={etl_statute}")

            etl_date = str(etl_row.get("ISSUE_DATE", "")).strip()[:10]
            dfr_date_clean = dfr_date[:10] if dfr_date else ""
            # Date comparison (flexible — DFR may be datetime, ETL may be YYYY-MM-DD)
            if dfr_date_clean and etl_date and dfr_date_clean != etl_date:
                # Try to normalize both
                try:
                    d1 = pd.to_datetime(dfr_date_clean).strftime("%Y-%m-%d")
                    d2 = pd.to_datetime(etl_date).strftime("%Y-%m-%d")
                    if d1 != d2:
                        mismatches.append(f"Date: DFR={d1} vs ETL={d2}")
                except Exception:
                    pass

            if mismatches:
                field_mismatches.append({
                    "full_summons_number": full_num,
                    "mismatches": mismatches,
                })
        else:
            unmatched += 1

        # 2. Check if Description/Fine need backfill
        desc = str(row.get("Description", "")).strip()
        fine = str(row.get("Fine Amount", "")).strip()
        needs_backfill = (not desc or desc.lower() == "nan" or not fine or fine.lower() == "nan" or fine == "0")

        if needs_backfill and statute:
            # Try ViolationData first, with subsection fallback
            import re
            _candidates = [statute]
            _s1 = re.sub(r"\([^)]*\)$", "", statute).strip()
            if _s1 and _s1 != statute:
                _candidates.append(_s1)
            _s2 = re.sub(r"[A-Za-z]+$", "", _s1).rstrip("-")
            if _s2 and _s2 not in _candidates:
                _candidates.append(_s2)

            vd = None
            for _c in _candidates:
                vd = violation_data.get(_c)
                if vd and vd.get("description"):
                    break
                vd = None
            if vd and vd.get("description"):
                backfill_candidates.append({
                    "full_summons_number": full_num,
                    "statute": statute,
                    "source": "ViolationData",
                    "description": vd["description"],
                    "fine_amount": vd["fine_amount"],
                    "violation_type": vd.get("violation_type", ""),
                })
            else:
                # Try fee schedule
                fs = fee_schedule.get(statute)
                if fs and fs.get("description"):
                    backfill_candidates.append({
                        "full_summons_number": full_num,
                        "statute": statute,
                        "source": "FeeSchedule",
                        "description": fs["description"],
                        "fine_amount": fs["fine_amount"],
                    })
                else:
                    # Try ordinances
                    oc = ordinances.get(statute)
                    if oc:
                        backfill_candidates.append({
                            "full_summons_number": full_num,
                            "statute": statute,
                            "source": "CityOrdinances",
                            "description": oc.get("description", ""),
                            "fine_amount": 0.0,
                        })

        # 3. Legal code lookup resolution
        if statute:
            resolved = False
            # Try exact match first, then strip subsection suffixes
            # e.g., "88-6D(2)" -> try "88-6D(2)", "88-6D", "88-6"
            import re
            candidates = [statute]
            # Strip parenthetical suffix: "88-6D(2)" -> "88-6D"
            stripped = re.sub(r"\([^)]*\)$", "", statute).strip()
            if stripped and stripped != statute:
                candidates.append(stripped)
            # Strip trailing letter suffix: "88-6D" -> "88-6"
            stripped2 = re.sub(r"[A-Za-z]+$", "", stripped).rstrip("-")
            if stripped2 and stripped2 not in candidates:
                candidates.append(stripped2)

            for candidate in candidates:
                if candidate in violation_data or candidate in fee_schedule or candidate in ordinances:
                    resolved = True
                    break
            if not resolved:
                # Try partial suffix match in fee_schedule
                for key in fee_schedule:
                    if key.endswith(statute) or statute.endswith(key):
                        resolved = True
                        break
            if resolved:
                statute_resolved += 1
            else:
                if statute not in [s["statute"] for s in statute_unresolved]:
                    statute_unresolved.append({"statute": statute, "full_summons_number": full_num})

    # --- Summary ---
    summary = {
        "dfr_total_records": len(dfr_df),
        "etl_matched": matched,
        "etl_unmatched": unmatched,
        "field_mismatches": field_mismatches,
        "backfill_candidates": len(backfill_candidates),
        "statute_resolved": statute_resolved,
        "statute_unresolved": statute_unresolved,
    }

    # --- Output report ---
    print("\n" + "=" * 70)
    print("  DFR RECONCILIATION REPORT")
    print("=" * 70)
    print(f"\n  DFR Workbook Records:     {len(dfr_df)}")
    print(f"  ETL Export Matches:       {matched}")
    print(f"  ETL Unmatched:            {unmatched}")
    print(f"  Field Mismatches:         {len(field_mismatches)}")
    print(f"  Backfill Candidates:      {len(backfill_candidates)}")
    print(f"  Statutes Resolved:        {statute_resolved}")
    print(f"  Statutes Unresolved:      {len(statute_unresolved)}")

    if field_mismatches:
        print("\n  --- Field Mismatches ---")
        for fm in field_mismatches[:10]:
            print(f"    {fm['full_summons_number']}: {', '.join(fm['mismatches'])}")
        if len(field_mismatches) > 10:
            print(f"    ... and {len(field_mismatches) - 10} more")

    if backfill_candidates:
        print("\n  --- Backfill Candidates (Description/Fine) ---")
        for bc in backfill_candidates[:10]:
            print(f"    {bc['full_summons_number']}: {bc['statute']} -> "
                  f"{bc['source']}: \"{bc['description'][:50]}\" ${bc['fine_amount']:.2f}")
        if len(backfill_candidates) > 10:
            print(f"    ... and {len(backfill_candidates) - 10} more")

    if statute_unresolved:
        print("\n  --- Unresolved Statutes ---")
        for su in statute_unresolved:
            print(f"    {su['statute']} (first seen: {su['full_summons_number']})")

    if not dry_run and backfill_candidates:
        # Write backfill report CSV
        report_path = base / "06_Workspace_Management" / "outputs" / "dfr_reconciliation_report.csv"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(backfill_candidates).to_csv(report_path, index=False)
        print(f"\n  Backfill report saved: {report_path}")

    print("\n" + "=" * 70)
    return summary


def main():
    parser = argparse.ArgumentParser(description="DFR Fee Schedule Reconciliation")
    parser.add_argument("--dry-run", action="store_true", help="Report only, no file writes")
    args = parser.parse_args()
    reconcile(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
