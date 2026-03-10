"""
run_summons_etl.py
Path-agnostic wrapper for Summons ETL (v2.3.0)
Auto-detects desktop (carucci_r) vs laptop (RobertCarucci).
Produces 3 output tiers: RAW copy, CLEAN Excel, SLIM CSV.
Loads all months in folder (prefers _FIXED.csv from DOpus) for full 13-month coverage.
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Ensure scripts is on path (matches original run_summons_etl pattern)
_scripts = Path(__file__).parent / "scripts"
sys.path.insert(0, str(_scripts))

from path_config import get_onedrive_root
from summons_etl_normalize import (
    normalize_personnel_data,
    write_three_tier_output,
    load_and_concatenate_summons,
)


def _discover_summons_files(month_dir: Path) -> list[Path]:
    """Discover e-ticket exports. Prefer _FIXED.csv (DOpus cleaned) when both exist.
    Fall back to raw when _FIXED has 0 data rows (header-only)."""
    seen = {}
    for f in sorted(month_dir.glob("*_eticket_export*.csv")):
        name = f.name
        if "_FIXED" in name:
            base = name.replace("_eticket_export_FIXED.csv", "")
            seen[base] = f
        elif name.endswith("_eticket_export.csv"):
            base = name.replace("_eticket_export.csv", "")
            if base not in seen:
                seen[base] = f

    # Fallback: if _FIXED has 0 data rows, use raw
    result = []
    for p in sorted(seen.values(), key=lambda x: x.name):
        if "_FIXED" in p.name:
            try:
                with open(p, "r", encoding="utf-8", errors="replace") as f:
                    lines = [ln for ln in f if ln.strip()][1:]  # skip header
                if len(lines) == 0:
                    raw = p.parent / p.name.replace("_FIXED", "")
                    if raw.exists():
                        result.append(raw)
                        continue
            except Exception:
                pass
        result.append(p)
    return result


def main():
    from summons_backfill_merge import merge_missing_summons_months

    prev_month = (datetime.today().replace(day=1) - timedelta(days=1))
    default_month = prev_month.strftime("%Y_%m")

    parser = argparse.ArgumentParser(description="Run Summons ETL with 3-tier output")
    parser.add_argument("--month", default=default_month, help="Latest month YYYY_MM (default: previous complete month)")
    parser.add_argument("--dry-run", action="store_true", help="List files and exit without running")
    args = parser.parse_args()

    base = get_onedrive_root()
    export_root = base / "05_EXPORTS" / "_Summons" / "E_Ticket"
    master_path = base / "09_Reference" / "Personnel" / "Assignment_Master_V2.csv"
    output_xlsx = base / "03_Staging" / "Summons" / "summons_powerbi_latest.xlsx"

    end_year = int(args.month.split("_")[0])
    years_to_scan = sorted({str(end_year - 1), str(end_year)})

    paths = []
    for yr in years_to_scan:
        month_dir = export_root / yr / "month"
        if month_dir.exists():
            found = _discover_summons_files(month_dir)
            paths.extend(found)
            print(f"  Discovered {len(found)} file(s) in {yr}/month/")

    if not paths:
        print(f"  No e-ticket exports found in {export_root}")
        print(f"  Searched: {', '.join(yr + '/month/' for yr in years_to_scan)}")
        print("  Expected: YYYY_MM_eticket_export.csv or YYYY_MM_eticket_export_FIXED.csv")
        sys.exit(1)

    if args.dry_run:
        print("DRY RUN — would process:")
        for p in paths:
            print(f"  {p.name}")
        print(f"\nTotal: {len(paths)} file(s)")
        return

    if not master_path.exists():
        print(f"  Master file not found: {master_path}")
        sys.exit(1)

    output_xlsx.parent.mkdir(parents=True, exist_ok=True)

    print(f"Processing {len(paths)} month(s): {', '.join(p.stem.replace('_eticket_export_FIXED', '').replace('_eticket_export', '') for p in paths)}")
    raw_path_for_tier = None
    if len(paths) == 1:
        summons_path = paths[0]
        raw_path_for_tier = summons_path
        final_data = normalize_personnel_data(str(summons_path), str(master_path), str(output_xlsx))
    else:
        combined_df, temp_path = load_and_concatenate_summons(paths)
        raw_path_for_tier = temp_path
        final_data = normalize_personnel_data(str(temp_path), str(master_path), str(output_xlsx), df=combined_df)

    merged = merge_missing_summons_months(final_data)
    if len(merged) > len(final_data):
        backfill_mask = merged["ETL_VERSION"].isna()
        merged.loc[backfill_mask, "ETL_VERSION"] = "HISTORICAL_SUMMARY"
        merged.loc[backfill_mask, "IS_AGGREGATE"] = True
        print(f"  Backfill merged: {len(merged) - len(final_data)} rows added.")

    write_three_tier_output(merged, str(output_xlsx), str(raw_path_for_tier))

    if len(paths) > 1 and raw_path_for_tier and getattr(raw_path_for_tier, "exists", lambda: False)():
        try:
            raw_path_for_tier.unlink(missing_ok=True)
        except OSError:
            pass  # Windows may hold handle; temp in exports folder is acceptable

    print("\n" + "=" * 60)
    print("ETL COMPLETE!")
    print("=" * 60)
    print(f"\nOutput saved to: {output_xlsx.parent}")
    print("  - RAW:  *_RAW.csv")
    print("  - CLEAN: summons_powerbi_latest.xlsx")
    print("  - SLIM:  summons_slim_for_powerbi.csv (use in Power BI for ~60% faster refresh)")
    print("\nNext: Update M-code queries to source summons_slim_for_powerbi.csv")


if __name__ == "__main__":
    main()
