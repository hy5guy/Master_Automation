Process Power BI visual exports from the _DropExports inbox folder.

Matches exported CSV files to the visual export mapping, renames them to standardized filenames, normalizes data formats, routes to Processed_Exports categories, and copies to Backfill when required.

## Input

The user provides:
- `$ARGUMENTS` — the report month, optionally followed by flags

Accepted month formats (all equivalent):
- `2026_02` (YYYY_MM with underscore)
- `2026-02` (YYYY-MM with hyphen)
- `202602` (YYYYMM compact)

The skill normalizes any of these to `YYYY-MM` (hyphen) before passing to `--report-month`.

Supported flags:
- `--dry-run` — preview what would happen without moving files
- `--verify-only` — report current state of Processed_Exports
- `--scan-processed-exports-inbox` — also process stray CSVs at Processed_Exports root

If no argument is provided, default to the previous complete month.

## Process

### Step 0: Normalize the month input

Parse the user-provided month string into `YYYY-MM` (hyphen) format, which is what the script expects:
- `2026_02` -> `2026-02`
- `202602` -> `2026-02`
- `2026-02` -> `2026-02` (already correct)

Store the normalized value as `{YYYY-MM}`.

### Step 1: Preview with dry-run

Always start with a dry-run to show the user what will happen:

```bash
python scripts/process_powerbi_exports.py --report-month {YYYY-MM} --dry-run
```

Show the output, which lists:
- Each CSV found in _DropExports
- Its matched visual mapping entry (or "[WARN] No mapping for:" = UNMATCHED)
- The target destination path
- Whether normalization will be applied
- Whether backfill copy will occur

Explicitly call out any UNMATCHED files (tagged `[WARN]`) so the user can decide whether to add a mapping entry or ignore them.

### Step 2: Confirm with user

Ask the user to confirm before proceeding. List any UNMATCHED files that will be skipped.

### Step 3: Execute processing

```bash
python scripts/process_powerbi_exports.py --report-month {YYYY-MM}
```

### Step 4: Post-processing validation

After processing completes, run a quick inventory of what landed:

```bash
python scripts/process_powerbi_exports.py --verify-only
```

Report the results organized by target folder (summons, response_time, patrol, etc.).

### Step 5: Optional — scan Processed_Exports inbox

If user mentions stray files in the Processed_Exports root:

```bash
python scripts/process_powerbi_exports.py --scan-processed-exports-inbox
```

## Key Paths (resolved via path_config.py)

- **Source**: `PowerBI_Data/_DropExports/` (raw CSV exports from Power BI Ctrl+Shift+E)
- **Mapping**: `Standards/config/powerbi_visuals/visual_export_mapping.json`
- **Destination**: `09_Reference/Standards/Processed_Exports/{category}/`
- **Backfill**: `PowerBI_Data/Backfill/{YYYY_MM}/{category}/`
- **Archive**: Previous files archived under `archive/YYYY_MM/` within each category folder before overwrite

## Normalization Formats

| Format | Description | Columns |
|--------|-------------|---------|
| `summons` | Summons trend/bureau data | Month_Year, WG2, TICKET_COUNT, TYPE |
| `training_cost` | Training cost by delivery | Period, Delivery_Type, Sum of Cost |
| *(default)* | Monthly accrual/usage | Time Category, Sum of Value, PeriodLabel |

## Critical Rules

1. Never process without showing dry-run first
2. Archive previous files before overwriting (handled by `processed_exports_routing.py`)
3. Identical files are skipped (idempotent)
4. Files matching `skip_patterns` (Text Box, Administrative Commander) are silently skipped
5. The `--report-month` value drives the 13-month window end date calculation
