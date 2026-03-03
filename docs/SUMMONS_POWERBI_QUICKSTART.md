# Power BI Update - Quick Instructions
## Summons Queries (2026-02-17) | VISUALS VERIFIED

## ⏱ Time: 2-3 minutes

**Status:** Top 5 Moving, Top 5 Parking, and All Bureaus are correct. Use the M code from **`docs/SUMMONS_M_CODE_FINAL.md`** (copy-paste ready). Queries use **previous complete month** and load from `summons_powerbi_latest.xlsx`.

### Step-by-Step

1. **Open Power BI Desktop** and your monthly report.

2. **Open Power Query Editor** → `Home → Transform Data`

3. **Create/Update 3 Queries** — use the full M code from **`SUMMONS_M_CODE_FINAL.md`**:
   - **Query 1: ___Summons_Top5_Moving** — Previous month; exclude PEO (TITLE = "PEO"); group by badge; Top 5 by Moving count.
   - **Query 2: ___Summons_Top5_Parking** — Previous month; group by badge; Top 5 by Parking count.
   - **Query 3: ___Summons_All_Bureaus** — Previous month; filter out UNKNOWN WG2; Housing & OSO → Patrol Division; M/P/Total by bureau.

4. **How to Create/Update Each Query**
   - Open **`docs/SUMMONS_M_CODE_FINAL.md`** and copy the M code block for the query (Query 1, 2, or 3).
   - **Option A – Update existing:** In Power Query Editor, select the query → Right-click → Advanced Editor → Replace all with pasted code → Done.
   - **Option B – New query:** Home → New Source → Blank Query → Advanced Editor → Paste code → Done → Rename query.

5. **Close & Apply**
   - Click: `Home → Close & Apply`
   - Wait for refresh to complete

6. **Verify Results**
   - **Month_Year:** Previous complete month (e.g. 01-26 when run in February).
   - **Top 5 Moving:** Five officers by Moving count; PEOs excluded; names from Assignment Master.
   - **Top 5 Parking:** Five officers by Parking count.
   - **All Bureaus:** PATROL DIVISION, TRAFFIC BUREAU, DETECTIVE BUREAU, CSB, etc. with M and P counts for that month.

### Current Behavior (2026-02-17)
- **ETL:** TYPE from export **Case Type Code** only (M/P/C); officer identity and display name from Assignment Master (badge); TITLE in staging for PEO filter.
- **Power BI:** All three queries use **previous complete month**; Top 5 Moving excludes TITLE = "PEO"; counts are row counts from staging file.

### Troubleshooting

**Error: "Column YearMonthKey doesn't exist"**
- Ensure the query loads from `summons_powerbi_latest.xlsx` (Summons_Data sheet) and that the ETL has been run so the file has YearMonthKey, TYPE, WG2, TITLE, etc.

**Error: "Can't find file"**
- Check the path in the query matches your actual path
- Path should be: `C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx`

**Values still look wrong:**
- Close Power BI completely and reopen
- Click Refresh again

---

**Files:** M code in `m_code\___Summons_Top5_Moving_STANDALONE.m`, `___Summons_Top5_Parking_STANDALONE.m`, `___Summons_All_Bureaus_STANDALONE.m`; full copy-paste in `docs/SUMMONS_M_CODE_FINAL.md`.
**Data:** `03_Staging\Summons\summons_powerbi_latest.xlsx` (run Summons ETL to refresh).
