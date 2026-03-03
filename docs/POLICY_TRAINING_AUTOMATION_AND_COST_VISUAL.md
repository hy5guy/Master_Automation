# Policy Training: Automation Location & Cost of Training Visual

## Where the automation runs

Policy Training Monthly is **configured** in Master_Automation but is currently **disabled** in the main orchestrator.

| Item | Detail |
|------|--------|
| **ETL project folder** | `C:\Users\carucci_r\OneDrive - City of Hackensack\02_ETL_Scripts\Policy_Training_Monthly` |
| **Orchestrator config** | `Master_Automation\config\scripts.json` → entry `"Policy Training Monthly"` |
| **Script in config** | `main.py` (path: same as project folder above) |
| **Enabled in run_all_etl** | **No** (`enabled: false`) |
| **Actual ETL code** | `02_ETL_Scripts\Policy_Training_Monthly\src\policy_training_etl.py` (and related modules in `src\`) |

### How to run the Policy Training ETL

1. **From Master_Automation (single script)**  
   - Enable the script in `config\scripts.json` by setting `"enabled": true` for "Policy Training Monthly", then run:
   - `.\scripts\run_etl_script.ps1 -ScriptName "Policy Training Monthly"`
   - Or run the full suite: `.\scripts\run_all_etl.ps1` (will include Policy Training only if enabled).

2. **From the ETL project folder**  
   - Open a terminal, go to the project folder, and run the entry point you normally use (e.g. `python main.py` if present, or `python -m src.policy_training_etl` / whatever the project uses).
   - Output is written to: `...\Policy_Training_Monthly\output\policy_training_outputs.xlsx`.

The Power BI query **___Cost_of_Training.m** reads that same workbook (sheet `Delivery_Cost_By_Month`).

---

## Cost of Training visual: 13-month window fix (01-25 → 01-26)

**Issue:** The visual was showing 12-24 through 12-25 instead of the standard 13-month window 01-25 through 01-26.

**Cause:** The M code did not filter by date; it showed whatever month columns existed in the Excel. The project standard is a **rolling 13-month window**: same month one year earlier through **previous month** (e.g. in Feb 2026 → 01-25 through 01-26).

**Fix (in `m_code\___Cost_of_Training.m`):**

- Added dynamic 13-month window calculation (same logic as STACP and other project visuals):
  - End = previous month (e.g. Jan 2026).
  - Start = same month, one year earlier (e.g. Jan 2025).
- After unpivoting month columns, the query now **filters** to only keep rows whose `Period` (MM-YY) is in that window.

After refreshing the query in Power BI, the Training Cost by Delivery Method visual will show **01-25 through 01-26** (and will roll forward automatically each month).

**Deploy:** Copy the updated `___Cost_of_Training.m` into your Power BI report’s query and refresh.

---

## Why 01-26 can be missing in the export

The M code **only shows months that exist in the source workbook**. It does not create or invent data.

- **Source:** `02_ETL_Scripts\Policy_Training_Monthly\output\policy_training_outputs.xlsx` (sheet `Delivery_Cost_By_Month`).
- If that sheet has columns only for **01-25 through 12-25**, then after unpivot + 13‑month filter you get **01-25 through 12-25** in the visual/export — **no 01-26**.
- **01-26 will appear only when** the Policy Training ETL has been run so that the output workbook includes a **01-26** column (and that file is what Power BI is reading).

**What to do:** Run the Policy Training ETL so it writes the workbook with a January 2026 column (through "previous month" or at least 01-26). After the workbook is updated and Power BI is refreshed, the Training Cost by Delivery Method visual and its export will include 01-26.

---

## In-Person Training visual and source cost columns

- **In-Person Training** Power BI query reads from the ETL output sheet **InPerson_Prior_Month_List** (same workbook `policy_training_outputs.xlsx`). It shows prior-month In-Person courses with Course Name, Course Duration, Total Cost, Attendees Count.
- **Zeros in the visual:** If the source workbook (`Policy_Training_Monthly.xlsx` → sheet **Training_Log**) has **Total Cost** and **Cost Per Attendee** blank or zero for that month, the ETL (and thus the visual) will show 0.00. That is correct behavior.
- **ETL cost imputation:** When Total Cost is missing or zero, the ETL sets `Total Cost = Course per Attendee × Course Attendees`. So filling **Cost Per Attendee** (and having **Count of Attendees**) in the source will produce non-zero cost after re-running the ETL.
- **Source column alias:** The source workbook may use **"Cost Per Attendee"** (capital P). The ETL in `02_ETL_Scripts\Policy_Training_Monthly\src\policy_training_etl.py` was updated to recognize this alias (added to `col_per_attendee` list) so that column is used for imputation when Total Cost is zero.
