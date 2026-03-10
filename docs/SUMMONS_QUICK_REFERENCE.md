# Summons ETL - Quick Reference Card

**⚡ Fast reference for monthly summons data processing**

---

## 🚀 Quick Start (2 Minutes)

```powershell
# 1. Backup previous month
Copy-Item "03_Staging\Summons\summons_powerbi_latest.xlsx" `
          "03_Staging\Summons\backups\summons_$(Get-Date -Format 'yyyyMMdd').xlsx"

# 2. Run Python ETL (includes backfill merge for 13-month visual)
cd "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
python run_summons_etl.py

# 3. Refresh Power BI (Ctrl+R)
```

---

## 📁 Key File Paths

```
Source:
  00_Raw_Data\Summons\YYYY_MM_eticket_export.csv

Reference:
  09_Reference\Personnel\Assignment_Master_V2.csv

Output:
  03_Staging\Summons\summons_powerbi_latest.xlsx

Backups:
  03_Staging\Summons\backups\summons_YYYYMMDD.xlsx

Scripts:
  scripts\summons_etl_normalize.py

Docs:
  docs\SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md
  docs\SUMMONS_PRODUCTION_CHECKLIST.md
```

---

## ✅ Success Indicators

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| Match Rate | > 95% | 90-95% | < 90% |
| Unknown Badges | < 3% | 3-5% | > 5% |
| Records Processed | > 3,000 | 1,000-3,000 | < 1,000 |
| Bureaus Mapped | 6-8 | 4-6 | < 4 |

---

## 🔍 Quick Diagnostics

**Problem: Script fails to load CSV**
```python
# Check delimiter and encoding
df = pd.read_csv('file.csv', sep=';', encoding='utf-8', nrows=5)
print(df.columns)
```

**Problem: Low match rate**
```python
# Check badge format in both files
print(summons_df['Officer Id'].head())
print(master_df['PADDED_BADGE_NUMBER'].head())
```

**Problem: Power BI visuals empty**
```powerquery
// Verify M code filter
Table.SelectRows(Source, each [IS_AGGREGATE] = false or [ETL_VERSION] = "ETICKET_CURRENT")
```

**All Bureaus visual:** Use **Moving** and **Parking** columns (not M/P). See SUMMONS_DATA_IMPORT_LOGIC_GUIDE Issue 8.

---

## 🎯 Critical Business Rules

1. **Always use `SUM(TICKET_COUNT)` not `COUNTROWS()`**
2. **Bureau consolidation: OSO → PATROL DIVISION**
3. **Filter to ACTIVE personnel only**
4. **Pad badges to 4 digits: 256 → "0256"**
5. **13-month window: Exclude current incomplete month**
6. **All Bureaus:** null/blank/nan/UNKNOWN WG2 → UNASSIGNED (so bureau sum = dept-wide)
7. **Gap months:** Filler rows added for missing (Month_Year, TYPE) so 07-25 shows P=0, C=0 not blank

---

## 🆘 Emergency Contacts

**Script Issues:** Check `SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md`  
**Data Issues:** Update `Assignment_Master_V2.csv`  
**Power BI Issues:** Refresh queries, check M code  

**Rollback:** Restore from `backups\` folder

---

## 📊 Power BI Query Names

- `summons_13month_trend` - Trend visual
- `summons_all_bureaus` - Bureau breakdown
- `summons_top5_parking` - Top 5 parking
- `summons_top5_moving` - Top 5 moving

**All load from:** `03_Staging\Summons\summons_powerbi_latest.xlsx`

---

## 🔧 Common Column Mappings

| E-Ticket Export | Output Schema |
|----------------|---------------|
| `Officer Id` | `PADDED_BADGE_NUMBER` |
| `Statute` | `VIOLATION_NUMBER` |
| `Case Type Code` | `TYPE` |
| `Case Status Code` | `STATUS` |
| `Offense Street Name` | `LOCATION` |
| `Penalty` | `FINE_AMOUNT` |

---

**Version:** 1.1 | **Updated:** 2026-03-10
