# Summons Automation System - Documentation Index

**Complete documentation suite for the Hackensack PD Summons ETL pipeline**  
**Version:** 2.0  
**Last Updated:** 2026-03-10  
**Status:** ✅ Production Ready (v1.18.0 — full pipeline overhaul)

---

## 📚 Documentation Suite

### 🎯 **For First-Time Users → Start Here**

**[SUMMONS_QUICK_REFERENCE.md](SUMMONS_QUICK_REFERENCE.md)**  
⏱️ **2-minute read**  
**Purpose:** Fast reference card for monthly processing  
**Contains:**
- Quick start commands
- Key file paths
- Success indicators
- Common diagnostics
- Emergency contacts

**Best for:** Monthly routine execution, troubleshooting

---

### 📖 **For Complete Understanding → Read This**

**[SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md](SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md)**  
⏱️ **30-minute read** | 720+ lines  
**Purpose:** Master reference for all ETL logic and business rules  
**Contains:**
- Complete ETL pipeline architecture
- All 4 Power Query M code explanations
- Full schema (35+ columns)
- Business rules & transformations
- Common issues & solutions
- E-ticket export column mapping
- Data quality notes

**Best for:** Understanding the system, training new users, troubleshooting complex issues, sharing with AI assistants

---

### ✅ **For Production Deployment → Follow This**

**[SUMMONS_PRODUCTION_CHECKLIST.md](SUMMONS_PRODUCTION_CHECKLIST.md)**  
⏱️ **15-minute read** | Detailed checklist  
**Purpose:** Step-by-step guide for first production run  
**Contains:**
- Pre-deployment verification (3 steps)
- First run execution (7 steps)
- Quality assurance checks
- Unknown badge investigation
- Monthly maintenance schedule
- Emergency rollback procedure
- Success criteria

**Best for:** First-time deployment, monthly processing, quality assurance

---

### 📊 **For Project Overview → Review This**

**[SUMMONS_AUTOMATION_SUMMARY.md](SUMMONS_AUTOMATION_SUMMARY.md)**  
⏱️ **10-minute read**  
**Purpose:** High-level summary of what was built and why  
**Contains:**
- What was created (3 documents + 1 script)
- Key corrections applied (based on Gemini testing)
- Validation results
- Integration with existing system
- Files modified/created
- Usage instructions
- Testing checklist

**Best for:** Project handoff, executive summary, stakeholder communication

---

## 🐍 Python Scripts

### **Primary ETL Script**

**[scripts/summons_etl_normalize.py](../scripts/summons_etl_normalize.py)**  
**Purpose:** Main production ETL script  
**Features:**
- Loads e-ticket export (handles semicolon delimiter, bad lines)
- Cleans officer names (removes tabs, extra spaces)
- Pads badge numbers to 4 digits
- Parses ISO 8601 dates
- Joins to Assignment Master (ACTIVE only)
- Applies bureau consolidation
- Adds ETL metadata
- Exports to Excel

**Usage:**
```python
from scripts.summons_etl_normalize import normalize_personnel_data

final_data = normalize_personnel_data(
    summons_path='2026_01_eticket_export.csv',
    master_path='Assignment_Master_V2.csv',
    output_path='summons_powerbi_latest.xlsx'
)
```

---

### **Supporting Scripts**

**[scripts/summons_backfill_merge.py](../scripts/summons_backfill_merge.py)**  
**Purpose:** Merge historical backfill data for gap months  
**Use when:** Gap months need historical data (currently only 07-25)

**[run_summons_etl.py](../run_summons_etl.py)**  
**Purpose:** Entry point — discovers e-ticket files from 2025+2026, orchestrates ETL + backfill + 3-tier output  
**Usage:** `python run_summons_etl.py --month 2026_02`

---

### 🤖 Claude MCP Prompts (for Power BI Desktop updates)

**[PROMPT_Claude_MCP_Summons_Bugfix.md](PROMPT_Claude_MCP_Summons_Bugfix.md)**  
**Purpose:** Initial M code fixes (List.Sum, IS_AGGREGATE, BackfillMonths)

**[PROMPT_Claude_MCP_Summons_Validation_Post_ETL.md](PROMPT_Claude_MCP_Summons_Validation_Post_ETL.md)**  
**Purpose:** Post-ETL refresh validation with DAX checks

**[PROMPT_Claude_MCP_Summons_Round3_Fix.md](PROMPT_Claude_MCP_Summons_Round3_Fix.md)**  
**Purpose:** Window alignment, WG2 filter removal, Total null coalesce

**[PROMPT_Claude_MCP_Summons_AllBureaus_Fix.md](PROMPT_Claude_MCP_Summons_AllBureaus_Fix.md)**  
**Purpose:** UNASSIGNED mapping so bureau totals match department-wide

**[PROMPT_Claude_MCP_Summons_DeptWide_Backfill_Fix.md](PROMPT_Claude_MCP_Summons_DeptWide_Backfill_Fix.md)**  
**Purpose:** 07-25 filler rows for gap months (M=17, P=0, C=0 instead of blank)

### 📋 Lessons Learned (for AI assistants)

**[SUMMONS_M_CODE_NOTES.md](SUMMONS_M_CODE_NOTES.md)**  
**Purpose:** Reference for future Claude MCP sessions — table schema constraint, List.TransformMany syntax, Show Errors crash workaround, filler row pattern, WG2 filter rules, BackfillMonths, subtitle measures, ___Traffic dynamic typing, DAX validation queries

---

## 📊 Power Query M Code

### **Query 1: 13-Month Trend**
**[m_code/summons/summons_13month_trend.m](../m_code/summons/summons_13month_trend.m)**  
**Purpose:** Load all summons data for trend analysis  
**Includes:** Historical backfill + current month detail  
**Used by:** 13-Month Trend visual

### **Query 2: All Bureaus**
**[m_code/summons/summons_all_bureaus.m](../m_code/summons/summons_all_bureaus.m)**  
**Purpose:** Bureau-level summary for current month  
**Includes:** Bureau consolidation, current month filter  
**Used by:** All Bureaus visual

### **Query 3: Top 5 Parking**
**[m_code/summons/summons_top5_parking.m](../m_code/summons/summons_top5_parking.m)**  
**Purpose:** Top 5 parking violation officers  
**Used by:** Top 5 Parking visual

### **Query 4: Top 5 Moving**
**[m_code/summons/summons_top5_moving.m](../m_code/summons/summons_top5_moving.m)**  
**Purpose:** Top 5 moving violation officers  
**Used by:** Top 5 Moving visual

---

## 🎓 Learning Path

### **Level 1: Monthly User (Time: 30 min)**
1. Read **SUMMONS_QUICK_REFERENCE.md** (2 min)
2. Review **SUMMONS_PRODUCTION_CHECKLIST.md** (15 min)
3. Run test execution (10 min)
4. Verify output in Power BI (3 min)

**You can now:** Run monthly summons ETL process

---

### **Level 2: Power User (Time: 2 hours)**
1. Complete Level 1
2. Read **SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md** (30 min)
3. Review Python script `summons_etl_normalize.py` (30 min)
4. Study M code queries (30 min)
5. Practice troubleshooting scenarios (30 min)

**You can now:** Troubleshoot issues, modify scripts, train others

---

### **Level 3: System Administrator (Time: 4 hours)**
1. Complete Level 1 & 2
2. Review **SUMMONS_AUTOMATION_SUMMARY.md** (10 min)
3. Study Assignment_Master_SCHEMA.md (20 min)
4. Review all supporting scripts (1 hour)
5. Create test environment and validate (2 hours)
6. Document custom modifications (30 min)

**You can now:** Maintain the entire system, extend functionality, integrate with other systems

---

## 🔍 How to Find Information

### **I need to...**

**Run the monthly process**  
→ Start with **SUMMONS_QUICK_REFERENCE.md**

**Understand why something works a certain way**  
→ Check **SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md**

**Deploy for the first time**  
→ Follow **SUMMONS_PRODUCTION_CHECKLIST.md**

**Explain the system to someone**  
→ Share **SUMMONS_AUTOMATION_SUMMARY.md**

**Fix a specific error**  
→ Search **SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md** Section 8 (Common Issues)

**Modify the Python script**  
→ Read script comments + **SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md** Section 5 (Data Cleaning)

**Update Power Query M code**  
→ Check **SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md** Section 4 (Power Query M Code Logic)

**Share with AI assistant**  
→ Provide **SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md** + **summons_etl_normalize.py**

---

## 📂 File Structure

```
Master_Automation/
├── docs/
│   ├── 📄 SUMMONS_DOC_INDEX.md                  ← YOU ARE HERE
│   ├── 📘 SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md    ← Master reference
│   ├── 📗 SUMMONS_PRODUCTION_CHECKLIST.md       ← Deployment guide
│   ├── 📙 SUMMONS_AUTOMATION_SUMMARY.md         ← Project summary
│   ├── 📕 SUMMONS_QUICK_REFERENCE.md            ← Quick ref card
│   └── 📋 SUMMONS_M_CODE_NOTES.md               ← Lessons learned (AI assistant ref)
│
├── scripts/
│   ├── 🐍 summons_etl_normalize.py              ← Main ETL script
│   └── 🐍 summons_backfill_merge.py             ← Backfill helper
│
├── m_code/summons/
│   ├── 📊 summons_13month_trend.m               ← Trend query
│   ├── 📊 summons_all_bureaus.m                 ← Bureau query
│   ├── 📊 summons_top5_parking.m                ← Top 5 parking
│   └── 📊 summons_top5_moving.m                 ← Top 5 moving
│
├── 00_Raw_Data/Summons/
│   └── YYYY_MM_eticket_export.csv               ← Monthly input
│
├── 03_Staging/Summons/
│   ├── summons_powerbi_latest.xlsx              ← Output for Power BI
│   └── backups/                                 ← Monthly backups
│
└── 09_Reference/Personnel/
    ├── Assignment_Master_V2.csv                 ← Personnel master
    └── Assignment_Master_SCHEMA.md              ← Schema docs
```

---

## 🤖 For AI Assistants

**If you're an AI assistant helping with this system:**

1. **Always read first:** `SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md` (has all context)
2. **Reference implementation:** `scripts/summons_etl_normalize.py` (production-tested)
3. **Critical rules to follow:**
   - Always use `List.Sum([TICKET_COUNT])` in M code, not `Table.RowCount()`
   - TYPE classification: use raw Case Type Code (M/P/C) — do NOT use statute lookup
   - 13-month trend: NO WG2 filter (dept-wide includes all officers); window = `pReportMonth - 1` as end date
   - Bureau consolidation: HOUSING, OSO, PATROL BUREAU → PATROL DIVISION
   - Badge padding: 256 → "0256"
   - Filter to ACTIVE personnel only
   - **Read `SUMMONS_M_CODE_NOTES.md`** before modifying M code — table schema, List.TransformMany, filler pattern, Show Errors workaround

4. **When troubleshooting:**
   - Check Section 8 of the guide first (Common Issues)
   - Verify column names match actual e-ticket export
   - Check Assignment_Master_V2.csv for STATUS values

5. **When modifying code:**
   - Follow existing patterns in `summons_etl_normalize.py`
   - Update documentation if you change business rules
   - Test with real data before recommending

---

## 📞 Support

**System Owner:** R. A. Carucci  
**Department:** Hackensack Police Department  
**System Name:** Master_Automation/Summons Pipeline

**Documentation Location:**  
`C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\docs\`

**For Questions:**
- Technical: Review `SUMMONS_DATA_IMPORT_LOGIC_GUIDE.md`
- Process: Review `SUMMONS_PRODUCTION_CHECKLIST.md`
- Quick answer: Check `SUMMONS_QUICK_REFERENCE.md`

---

## 📈 Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 2.1 | 2026-03-10 | v1.18.1: Ramirez SSOCC overrides, UNASSIGNED mapping, 07-25 filler rows, SUMMONS_M_CODE_NOTES, AllBureaus/DeptWide prompts | R. A. Carucci + Claude |
| 2.0 | 2026-03-10 | v1.18.0 overhaul: updated for run_summons_etl.py entry point, raw Case Type Code classification, Claude MCP prompts, corrected gap months | R. A. Carucci + Claude |
| 1.0 | 2026-02-16 | Initial documentation suite created | R. A. Carucci + Claude + Gemini |
| | | - Master guide (699 lines) | |
| | | - Production checklist | |
| | | - Quick reference | |
| | | - Automation summary | |
| | | - Python ETL script | |
| | | - This index | |

---

## 🎯 Success Metrics

**Documentation Quality:**
- ✅ Complete end-to-end coverage
- ✅ Multiple entry points for different user levels
- ✅ Real-world tested (Gemini validation)
- ✅ AI-assistant friendly
- ✅ Includes troubleshooting guides

**System Quality:**
- ✅ Production-ready Python script
- ✅ Handles real-world data issues
- ✅ 95%+ match rate achieved
- ✅ Comprehensive logging
- ✅ Error handling

**Usability:**
- ✅ Quick start in 2 minutes
- ✅ First-time deployment guide
- ✅ Monthly maintenance checklist
- ✅ Emergency rollback procedure

---

**🎉 You now have a gold-standard data automation system with complete documentation!**

**Next Steps:**
1. Run first production deployment (follow SUMMONS_PRODUCTION_CHECKLIST.md)
2. Schedule monthly maintenance (Week 1 after month end)
3. Train backup person on Level 2 (Power User)
4. Set up automated backups (PowerShell scheduled task)

---

**Document Version:** 2.1  
**Last Updated:** 2026-03-10  
**Status:** ✅ Complete and Production-Ready (v1.18.1)
