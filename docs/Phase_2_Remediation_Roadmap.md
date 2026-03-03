# 🕒 2026-02-19-14-36-45

# Project Name: Hackensack PD | Data Ops & ETL Remediation

# File Name: Phase_2_Remediation_Roadmap.md

# Author: R. A. Carucci

# Purpose: Comprehensive roadmap for Phase 2 ETL remediation tasks (Target: March 10, 2026)

-----

# PHASE 2 REMEDIATION ROADMAP

## Target Completion: March 10, 2026

-----

## 📊 CURRENT STATUS (As of Feb 20, 2026)

### February 2026 Cycle Results: 5/6 Success (83%)

|Workflow            |Status|Achievement                            |
|--------------------|------|---------------------------------------|
|Arrests             |✅     |42 records processed                   |
|Community Engagement|⚠️     |2 files created, **needs validation**  |
|Overtime/TimeOff    |✅     |13 files, 13-month rolling working     |
|Summons             |✅     |262,765 records processed              |
|Response Times      |✅     |**FIXED with first-arriving unit sort**|
|Summons Derived     |⏸️     |Schema mismatch deferred               |

-----

## 🎯 PHASE 2 PRIORITY TASKS

### **Priority 0: M Code ReportMonth Parameter Fix**

**Status:** IDENTIFIED — Ready for Implementation
**Estimated Time:** 4–6 hours
**Blocking:** Historical data integrity for ALL Power BI monthly reports

**Problem:**

Every M code query using `DateTime.LocalNow()` re-calculates its rolling 13-month window on every Power BI refresh. A January 2026 report refreshed in March 2026 silently shifts its window to Feb 2025 – Feb 2026, dropping Jan 2025 data. This breaks the core requirement: monthly reports must show identical data regardless of when they are refreshed.

**Scope:**

| File | Occurrences | Usage |
|------|-------------|-------|
| `m_code/2026_02_19_jan_m_codes.m` | 15+ | Consolidated multi-query file |
| `m_code/___Overtime_Timeoff_v3.m` | 1 | Rolling window |
| `m_code/___Arrest_Categories_FIXED.m` | 1 | Previous-month filter |
| `m_code/___Top_5_Arrests_FIXED.m` | 1 | Previous-month filter |
| `m_code/___Cost_of_Training.m` | 1 | Rolling window |
| `m_code/esu/ESU_13Month.m` | 1 | Rolling window |
| `m_code/esu/MonthlyActivity.m` | 1 | Rolling window |
| `m_code/stacp/STACP_pt_1_2_FIXED.m` | 1 | Rolling window |
| `m_code/detectives/___Detectives_2026.m` | 3 | Rolling window + timestamp |
| `m_code/detectives/___Det_case_dispositions_clearance_2026.m` | 1 | Rolling window |
| `m_code/___Summons_All_Bureaus_STANDALONE.m` | 1 | Previous-month calc |
| `m_code/___Summons_Top5_Moving_STANDALONE.m` | 1 | Previous-month calc |
| `m_code/2026_02_16_detectives.m` | 3 | Rolling window |

**Fix Pattern:**

```m
// OLD — breaks historical integrity
NowDT = DateTime.LocalNow(),

// NEW — locked to reporting period; change only this line each cycle
ReportMonth = #date(2026, 1, 1),   // ← UPDATE EACH REPORTING CYCLE
NowDT       = DateTime.From(ReportMonth),
// All downstream calculations (CurrY, CurrM, EndY, EndM, etc.) unchanged
```

**Actions:**

1. Use `docs/M_CODE_DATETIME_FIX_GUIDE.md` as the implementation reference
2. Apply fix to all 13 files listed above (the consolidated file counts as one)
3. Set `ReportMonth = #date(2026, 1, 1)` for the January 2026 cycle
4. Paste updated M code into each Power BI query editor
5. Refresh and verify 13-month window: Jan 2025 – Jan 2026 for each visual
6. Update `ReportMonth` to `#date(2026, 2, 1)` when running February 2026 cycle

**Success Criteria:**

- [ ] All 13 files updated — no `DateTime.LocalNow()` in production queries
- [ ] 13-month window: Jan 2025 – Jan 2026 confirmed in each visual
- [ ] January 2026 report refreshed in March 2026 shows identical data
- [ ] `ReportMonth` update procedure documented in monthly run checklist

**Reference:** `docs/M_CODE_DATETIME_FIX_GUIDE.md`

-----

### **Priority 1: Community Engagement Validation**

**Status:** PENDING  
**Estimated Time:** 2-3 hours  
**Blocking:** Power BI visual accuracy

**Actions:**

1. Run `community_engagement_diagnostic.ps1` to check outputs
1. Run `community_engagement_data_flow_check.py` for schema validation
1. Verify 13-month rolling window coverage
1. Compare record counts to expected baselines
1. Fix any date range or categorization issues

**Success Criteria:**

- [ ] 13-month date range confirmed
- [ ] All activity categories present
- [ ] Record counts match expected patterns
- [ ] Schema matches Power BI visual requirements

-----

### **Priority 2: Summons Derived Outputs Schema Fix**

**Status:** BLOCKED  
**Estimated Time:** 3-4 hours  
**Blocking:** 4 Power BI visuals

**Problem:**

- Script expects: `IS_AGGREGATE`, `TICKET_COUNT`
- Current schema: Missing these columns

**Actions:**

1. Review `summons_derived_outputs.py` line ~45-60 (schema definition)
1. Update schema to include:
- `IS_AGGREGATE` (boolean flag for summary rows)
- `TICKET_COUNT` (integer count field)
1. Modify aggregation logic in SummonsMaster.py if needed
1. Re-run full pipeline: Summons → Derived Outputs
1. Validate against Power BI visuals:
- `wg2_movers_parkers_nov2025.csv`
- `top5_moving_1125.csv`
- `top5_parking_1125.csv`
- `backfill_summons_summary.csv`

**Success Criteria:**

- [ ] Schema updated with required columns
- [ ] All 4 derived output files generated
- [ ] Files load successfully into Power BI
- [ ] No errors in `run_all_etl.ps1` execution

-----

### **Priority 3: Response Times Historical Backfill**

**Status:** PENDING  
**Estimated Time:** 4-6 hours  
**Blocking:** Historical trend analysis

**Actions:**

1. Identify months needing backfill (likely Nov 2024 - Dec 2025)
1. Locate historical CAD exports in `05_EXPORTS\_CAD\timereport\monthly\`
1. Create backfill script using validated logic from `process_cad_data_13month_rolling.py`
1. Apply first-arriving unit sort to ALL historical runs
1. Generate outputs for each missing month
1. Copy to `PowerBI_Date\_DropExports` with proper naming convention

**Success Criteria:**

- [ ] All months from Nov 2024 - Jan 2026 have Response Times data
- [ ] First-arriving unit logic applied consistently
- [ ] Files follow naming pattern: `YYYY_MM_Average_Response_Times__Values_are_in_mmss.csv`
- [ ] Verified against known benchmarks (Emergency ~3:00, Urgent ~2:45, Routine ~2:45)

-----

### **Priority 4: Secondary Response Time Metrics**

**Status:** DEFERRED (Optional Enhancement)  
**Estimated Time:** 6-8 hours  
**Blocking:** None (enhancement only)

**Potential Additions:**

- **Travel Time:** Time Out → On Scene
- **Processing Time:** On Scene → Cleared/Closed
- **Dispatch Delay:** Call Received → Time Out

**Note:** These are lower priority and can be implemented post-March 10 if time permits.

-----

## 📅 RECOMMENDED SCHEDULE

### Week 1 (Feb 20-23)

- **Day 1-2:** M Code ReportMonth parameter fix (Priority 0 — all 13 files)
- **Day 3:** Community Engagement diagnostic & fix
- **Day 4-5:** Summons Derived schema remediation

### Week 2 (Feb 24-Mar 2)

- **Day 1-3:** Response Times historical backfill
- **Day 4-5:** End-to-end pipeline testing

### Week 3 (Mar 3-9)

- **Day 1-2:** Final validation & documentation
- **Day 3-4:** Buffer for unexpected issues
- **Day 5:** Pre-delivery QA check

### Week 4 (Mar 10)

- **March Cycle Execution:** Full run with all fixes applied
- **Delivery:** Reports to Chief by COB

-----

## 🔧 TECHNICAL NOTES

### Path Configuration

Always use `scripts/path_config.py` for directory references:

```python
from path_config import get_onedrive_root, get_powerbi_drop

onedrive_root = get_onedrive_root()
drop_path = get_powerbi_drop()
```

### Header Standards

All code artifacts must include:

```python
# 🕒 YYYY-MM-DD-HH-MM-SS (EST)
# Project Name: Hackensack PD | Data Ops & ETL Remediation
# File Name: [path]/[filename]
# Author: R. A. Carucci
# Purpose: [Concise description]
```

### 13-Month Rolling Window Enforcement

Verify in `visual_export_mapping.json` that all 25 visuals are configured for 13-month windows.

-----

## ✅ PHASE 2 SUCCESS CRITERIA

### Definition of Done:

- [ ] **6/6 workflows executing successfully**
- [ ] **All Power BI visuals loading without errors**
- [ ] **13-month rolling windows validated across all datasets**
- [ ] **March 2026 cycle completes end-to-end**
- [ ] **Documentation updated with fix details**
- [ ] **Response Times backfill available for trend analysis**

-----

## 🚨 RISK MITIGATION

### Known Risks:

1. **Community Engagement:** Unknown root cause of “off” data
1. **Summons Derived:** Schema changes may require Power BI visual updates
1. **Historical Data:** CAD exports may have inconsistent formats over time

### Mitigation Strategies:

- Start with diagnostics to understand exact issues
- Make incremental changes with version control
- Test each fix in isolation before full pipeline run
- Keep backups of working configurations

-----

## 📞 ESCALATION PATH

If blocked or behind schedule:

1. Run diagnostic scripts immediately
1. Document specific error messages
1. Re-engage Claude for targeted troubleshooting
1. Consider scope reduction (e.g., defer backfill to April)

-----

**Last Updated:** February 20, 2026  
**Next Review:** February 23, 2026 (after M Code ReportMonth fix and Community Engagement validation)