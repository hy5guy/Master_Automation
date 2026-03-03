#!/usr/bin/env python3
"""
Run SummonsMaster_Simple with local overrides (without editing the upstream project).

Use-case:
- Fix blank Bureau rows driven by missing assignment enrichment for specific badges
  by injecting ASSIGNMENT_OVERRIDES before running the ETL.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--summons-dir",
        default=r"C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Summons",
        help="Path to the Summons project directory (contains SummonsMaster_Simple.py)",
    )
    ap.add_argument(
        "--backfill-converted",
        default=r"C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\_tmp_backfill_for_summonsmaster_simple.csv",
        help="Path to converted backfill CSV with columns TYPE, Month_Year, Count of TICKET_NUMBER",
    )
    ap.add_argument("--month-label", default="11-25", help="Month label for context (not required by ETL)")
    args = ap.parse_args()

    summons_dir = Path(args.summons_dir)
    if not summons_dir.exists():
        raise FileNotFoundError(f"Summons dir not found: {summons_dir}")

    sys.path.insert(0, str(summons_dir))

    import SummonsMaster_Simple as s  # type: ignore

    # Point at the converted backfill file (schema SummonsMaster_Simple expects)
    s.BACKFILL_FILE_OVERRIDE = Path(args.backfill_converted)

    # Inject badge override for 1711 to match the existing 0711 mapping for SQUILLACE PEO J.
    # This prevents blank WG2 (Bureau) which creates a blank Bureau row in Power BI visuals.
    s.ASSIGNMENT_OVERRIDES["1711"] = {
        "OFFICER_DISPLAY_NAME": "J. SQUILLACE #1711",
        "TEAM": "HCOP",
        "WG1": "OPERATIONS DIVISION",
        "WG2": "TRAFFIC BUREAU",
        "WG3": "CLASS I",
        "WG4": "",
        "POSS_CONTRACT_TYPE": "PARKING ENFORCEMENT OFF",
    }

    # Feb 2026: Badge 2025 (Ramirez) - only FIRE LANES violations show as SSOCC; others stay Traffic Bureau.
    s.ASSIGNMENT_OVERRIDES["2025"] = {
        "_condition": {"column": "VIOLATION_DESCRIPTION", "contains": "FIRE LANES"},
        "OFFICER_DISPLAY_NAME": "M. RAMIREZ #2025",
        "TEAM": "Safe Streets Operations",
        "WG1": "OPERATIONS DIVISION",
        "WG2": "SAFE STREETS OPERATIONS CONTROL CENTER",
        "WG3": "PEO",
        "WG4": "",
        "POSS_CONTRACT_TYPE": "PARKING ENFORCEMENT OFF",
    }

    ok = s.main()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())


