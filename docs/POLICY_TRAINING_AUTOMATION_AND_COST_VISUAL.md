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

The Power BI query **`___Cost_of_Training.m`** reads that workbook (sheet **`Delivery_Cost_By_Month`**).

---

## Cost of Training M query (13-month rolling + calendar YTD)

**Source:** `02_ETL_Scripts\Policy_Training_Monthly\output\policy_training_outputs.xlsx` — sheet **`Delivery_Cost_By_Month`**.

**Behavior (as of 2026-03-23, `m_code/training/___Cost_of_Training.m`):**

1. **Rolling 13-month window** (project standard for the wide “Training Cost by Delivery Method” visual): computed from **`pReportMonth`** with **end = calendar month before the report month** and **start = same month one year earlier** (see comments in the M file).
2. **Calendar YTD through report month:** month labels from **January of the report year** through **`pReportMonth`** are **unioned** with the rolling list so rows exist for **`Period_Sort`** values used by **Training Cost YTD** DAX (see `docs/POWER_BI_YTD_MEASURES_AND_PAGE_INSTRUCTIONS.md`). This also fixes the edge case where a **January** report month left no overlap with the old rolling-only filter.

After unpivoting month columns, the query **keeps** any row whose **`Period`** (MM-YY) is in **`List.Distinct(List.Combine({ PeriodLabelsMMYY, YTDLabels }))`**.

**Deploy:** Paste the repo **`___Cost_of_Training.m`** into Power BI Advanced Editor and refresh.

---

## Why a month column can be missing in the visual

The M code **only shows months that exist as columns** in the source workbook. It does not invent periods.

- If **`Delivery_Cost_By_Month`** has no **03-26** column, March 2026 will not appear until the Policy Training ETL (or manual workbook edit) adds that column.
- After the workbook is updated and Power BI is refreshed, unpivoted rows for that period appear (if the period is inside the **union** of rolling + YTD lists).

---

## In-Person Training visual and source (2026-03-23)

**Power BI query:** `m_code\training\___In_Person_Training.m`

| Item | Detail |
|------|--------|
| **Workbook** | `Shared Folder\Compstat\Contributions\Policy_Training\Policy_Training_Monthly.xlsx` (source of truth; always current) |
| **Sheets** | **`Training_Log`**, with fallback **`Training_Log_Clean`** |
| **Filter** | In-Person only: **`Delivery Method`** or **`Delivery_Type`**, normalized (trim, lower case) |
| **Columns** | **`Start date`**, **`End date`**, **`Course Name`**, **`Course Duration`**, **`Total Cost`**, **`Attendees Count`** (aliases: CourseDuration, TotalCost, Count of Attendees → Attendees Count) |
| **YTD in Power BI** | The M query loads **all** qualifying in-person rows. **Training Classes YTD**, **Training Duration YTD**, etc., apply **calendar YTD** filters in **DAX** on **`Start date`** (see YTD measures doc). |

**Zeros or blanks:** If **Total Cost** is blank or zero for events in range, cards/measures show 0 or blank as appropriate. The Python ETL can impute cost from **Cost Per Attendee × attendees** when configured.

**Source column alias:** The workbook may use **"Cost Per Attendee"** (capital P). The ETL in `02_ETL_Scripts\Policy_Training_Monthly\src\policy_training_etl.py` recognizes this alias for imputation when Total Cost is zero.

---

## Historical note (superseded paths)

Earlier versions of **`___In_Person_Training.m`** read **`policy_training_outputs.xlsx`** / **`InPerson_Prior_Month_List`** (prior month only). That pattern **does not** support calendar **YTD** DAX on **`Start date`** when the sheet holds only one month. **Repo gold copy = source workbook + full log**, as above.
