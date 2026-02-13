# Power BI Visual Export Pipeline – FAQ

## Prefix logic (YYYY_MM_)

The script **does not** use the original filename to build the prefix. It derives **YYYY_MM** as follows:

1. **From the filename:** It looks for a pattern **`YYYY_MM`** (e.g. `2025_12`, `2026_01`) anywhere in the file **stem** (filename without `.csv`).  
   - Example: `2025_12_Monthly Accrual and Usage Summary.csv` → prefix **2025_12**.
2. **If none found:** It uses **the previous calendar month from today’s date**.  
   - Example: run on Feb 12, 2026 with file `Monthly Accrual and Usage Summary.csv` → prefix **2026_01**.

The output filename is always: **`YYYY_MM_{standardized_filename}.csv`**  
(e.g. `2026_01_monthly_accrual_and_usage_summary.csv`).

---

## Where files are moved

| Step | Location |
|------|----------|
| **1. Processed (archive)** | `C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Standards\Processed_Exports\{target_folder}\` |
| **2. Backfill (if `is_backfill_required`)** | `C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\Backfill\YYYY_MM\{target_folder}\` |

- **Summons** → `Processed_Exports\Summons\` and `Backfill\YYYY_MM\Summons\`
- **Training** → `Processed_Exports\Training\` and `Backfill\YYYY_MM\Training\`
- **Time_Off (Monthly Accrual)** → `Processed_Exports\Time_Off\` only (no backfill copy in current mapping)

Source files are **removed** from `Master_Automation\_DropExports` after a successful move/copy.

---

## Were the three files in `data\backfill\2026_12_compair\` processed?

**No.** Those three files live in a **comparison folder** (`2026_12_compair`), not in the pipeline’s source folder.

- **`process_powerbi_exports.py`** only reads from:
  - **Default source:** `Master_Automation\_DropExports`
  - Or the path you pass with `--source`
- It does **not** scan `data\backfill\2026_12_compair\`, so those CSVs were **not** processed, renamed, moved, or normalized by the script.

So:

- **Department-Wide Summons  Moving and Parking.csv** – not processed by the pipeline  
- **Training Cost by Delivery Method.csv** – not processed by the pipeline  
- **Monthly Accrual and Usage Summary.csv** – not processed by the pipeline  

---

## Did they replace previous versions in the folders?

**No.** Because they were never used as input to the pipeline, nothing was written to:

- `09_Reference\Standards\Processed_Exports\`
- `PowerBI_Date\Backfill\`

So no previous versions in those folders were replaced by these three files.

---

## Were the Summons, Policy/Training, and Overtime/TimeOff scripts run to process them?

- **Summons** and **Overtime/TimeOff** are run by **`run_all_etl.ps1`** (when you run the full ETL).
- They read **backfill** from:
  - **Overtime/TimeOff:** `PowerBI_Date\Backfill\YYYY_MM\vcs_time_report\` (expects “Monthly Accrual and Usage Summary” CSV there).
  - **Summons:** `PowerBI_Date\Backfill\YYYY_MM\summons\` (expects Department-Wide Summons CSVs there).
- **Policy Training Monthly** is **disabled** in `config/scripts.json` (`enabled: false`).

Because the three files in `2026_12_compair` were never copied into those Backfill paths, the ETL scripts did **not** process these specific exports. They only process what’s already in Backfill (and other configured sources).

---

## How to process the `2026_12_compair` files and use them in the pipeline

If you want these three files to be **processed, named, moved, normalized, and used as backfill**:

1. **Run the visual export processor** with that folder as source (from repo root):

   ```powershell
   python scripts/process_powerbi_exports.py --source "data\backfill\2026_12_compair"
   ```

   That will:

   - Match and rename to `YYYY_MM_{standardized_filename}.csv`
   - Normalize (where `requires_normalization` is true)
   - Move to `09_Reference\Standards\Processed_Exports\{target_folder}`
   - Copy to `PowerBI_Date\Backfill\YYYY_MM\{target_folder}` for Summons and Training (because `is_backfill_required` is true)

   **Note:** In the current mapping, **Monthly Accrual** has `is_backfill_required: false` and `target_folder: "Time_Off"`. The **Overtime/TimeOff** script, however, looks for Monthly Accrual in **`Backfill\YYYY_MM\vcs_time_report\`**. So for Overtime/TimeOff to use a processed Monthly Accrual file, you would either:

   - Manually copy the normalized file from `Processed_Exports\Time_Off\` into `Backfill\YYYY_MM\vcs_time_report\`, or  
   - Change the mapping to use `target_folder: "vcs_time_report"` and `is_backfill_required: true` for Monthly Accrual, then re-run the processor.

2. **Run the ETL** so downstream scripts use the new backfill:

   ```powershell
   .\scripts\run_all_etl.ps1
   ```

   This runs Summons (which will merge from Backfill) and Overtime/TimeOff (which will use backfill from `vcs_time_report` if present).

3. **Refresh Power BI** after ETL outputs are updated.

---

## Can you update the January 2026 Power BI project to refresh the visuals?

**Yes.** After:

1. Putting the visual exports where the pipeline expects them (e.g. by running `process_powerbi_exports.py` as above and, if needed, copying Monthly Accrual into `vcs_time_report`), and  
2. Running the ETL (`run_all_etl.ps1`) so Summons and Overtime/TimeOff (and any other scripts) have updated data,

you can refresh the **January 2026** Power BI project and the visuals will use the updated data.

---

## Where the pipeline expects files

| Purpose              | Source (input)                    | Destinations (output)                                                                 |
|----------------------|-----------------------------------|----------------------------------------------------------------------------------------|
| Visual export processor | `Master_Automation\_DropExports` or `--source` | `09_Reference\Standards\Processed_Exports\{target_folder}` and `PowerBI_Date\Backfill\YYYY_MM\{target_folder}` (when backfill required) |
| run_all_etl “Visual Export Normalization” | `PowerBI_Date\_DropExports`       | In-place normalization only (no move/copy to Backfill)                                |
| Overtime/TimeOff backfill | Reads from                          | `PowerBI_Date\Backfill\YYYY_MM\vcs_time_report\`                                       |
| Summons backfill     | Reads from                        | `PowerBI_Date\Backfill\YYYY_MM\summons\`                                               |
