# Power BI Visual Export Mapping

Maps Power BI **Page Name** and **Visual Name** to standardized filenames and processing rules.

## File

- **`visual_export_mapping.json`** – Defines for each visual:
  - `page_name`, `visual_name` – Identifiers (visual_name is matched against export filenames)
  - `match_aliases` – Optional list of alternate names (e.g. for "Average Response Times  Values" double-space)
  - `standardized_filename` – Snake_case base name; output is `YYYY_MM_{standardized_filename}.csv`
  - `requires_normalization` – If true, run `normalize_visual_export_for_backfill.py` on the file
  - `normalizer_format` – Optional. When set, passed as `--format` to the normalizer: `summons` or `training_cost`. Omit for Monthly Accrual (default).
  - `is_backfill_required` – If true, copy to `PowerBI_Date/Backfill/YYYY_MM/{target_folder}/`
  - `target_folder` – Subfolder under `09_Reference/Standards/Processed_Exports/`

**Normalized backfill schema (so downstream ETL has no missing values):**

- **summons** → CSV columns: `Month_Year`, `WG2`, `TICKET_COUNT`, `TYPE` (Long; period labels as MM-YY). Consumed by `summons_backfill_merge.py`.
- **training_cost** → CSV columns: `Period`, `Delivery_Type`, `Sum of Cost` (MM-YY period labels). Consumed by Policy Training comparison and any backfill loaders.
- **monthly_accrual** (default) → `Time Category`, `Sum of Value`, `PeriodLabel`. Consumed by Overtime/TimeOff backfill.

`skip_patterns` in the JSON list substrings that cause a file to be skipped (e.g. "Text Box", "Administrative Commander").

## Processing script

From repo root:

```powershell
python scripts/process_powerbi_exports.py
python scripts/process_powerbi_exports.py --dry-run   # Preview
python scripts/process_powerbi_exports.py --verify-only   # Report only
```

Default source: `Master_Automation/_DropExports`. Override with `--source` or set `source_folder_override` in the JSON.

## Backfill-required visuals (current)

- Department-Wide Summons  Moving and Parking  
- DFR Activity Performance Metrics  
- Non-DFR Performance Metrics  
- Training Cost by Delivery Method  
