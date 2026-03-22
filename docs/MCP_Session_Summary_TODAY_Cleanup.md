# MCP Session Summary - TODAY() DAX Measure Cleanup
# Monthly_Report_Template.pbix - Complete Model Audit

**Date:** 2026-03-17
**Model:** Monthly_Report_Template.pbix (port 57475)
**TMDL Export:** 87 files to `m_code/tmdl_export/`

---

## Achievement: Zero TODAY()/NOW() References in DAX

Starting count: **50+ measures** using `TODAY()` or `NOW()`
Ending count: **0 measures** using `TODAY()` or `NOW()`

The entire model is now parameter-driven:
- M code queries: `pReportMonth` (completed 2026-03-09)
- DAX measures: Data-driven via `MAX(date_column)` (completed 2026-03-17)

---

## Measures Fixed by Table

### Response Time (___ResponseTime_AllMetrics) - 5 new items
| Action | Measure | Details |
|--------|---------|---------|
| Fixed | `RT Trend Total Response` | Format "0.0" -> "0.0 min" |
| Fixed | `Metric_Label` | Added sortByColumn = Metric_Sort |
| Created | `RT Trend Travel Time` | Format "0.0 min", for Card sparklines |
| Created | `RT Trend Dispatch Queue` | Format "0.0 min", for Card sparklines |
| Created | `RT CF All Metrics Background` | Universal CF for all metric/type combos |
| Created | `RT CF All Metrics Font` | Universal font color companion |

### DFR Summons - 4 new measures
| Action | Measure | Details |
|--------|---------|---------|
| Created | `DFR Summons Count` | COUNTROWS, #,0 format |
| Created | `DFR Summons Total Fines` | SUM(Fine_Amount), $#,0.00 |
| Created | `DFR Summons Title` | Static title |
| Created | `DFR Summons Subtitle` | Dynamic count + month |

### Outreach (___Combined_Outreach_All) - 3 fixes
| Measure | Change |
|---------|--------|
| `Engagement Subtitle` | TODAY() -> MAX/MIN(Date) data range |
| `DateInPrevMonth` | TODAY() -> MAX(Date) from ALL data |
| `Prev Month Flag` | TODAY() -> MAX(Date) from ALL data |

### Summons (summons_13month_trend + sub-tables) - 7 fixes
| Measure | Change |
|---------|--------|
| `Summons Subtitle` | TODAY() -> MAX(ISSUE_DATE) |
| `SubtitleAllDep` | TODAY() -> MAX(ISSUE_DATE) |
| `Patrol_Bureau_Parking_Previous_Month_Date` | TODAY() -> MAX(ISSUE_DATE) |
| `Patrol_Bureau_Moving_Previous_Month_Date` | TODAY() -> MAX(ISSUE_DATE) |
| `Top5_Parking_Subtitle` | TODAY() -> MAX(Month_Year) |
| `Top5_Moving_Subtitle` | TODAY() -> MAX(Month_Year) |
| `AllBureaus_Subtitle` | TODAY() -> cross-table MAX |

### Arrests (___Arrest_Distro, ___Top_5_Arrests) - 2 fixes
| Measure | Change |
|---------|--------|
| `Subtitle_Arrest_Distro` | TODAY() -> MAX(Arrest Date) |
| `Subtitle_Top_5` | TODAY() -> MAX(Month_Year) |

### NIBRS (___NIBRS_Monthly_Report) - 5 fixes
| Measure | Change |
|---------|--------|
| `NIBRS Subtitle` | TODAY() -> MAX(MonthDate) |
| `Current Month Clearance Rate` | TODAY() -> MAX(MonthDate) |
| `LineChartSubtitle` | TODAY() -> MAX(MonthDate) |
| `NIBRS Matrix 2 Subtitle` | TODAY() -> MAX(MonthDate) |
| `NIBRS Clearance Matrix Subtitle` | TODAY() -> MAX(MonthDate) |

### Detectives (___Det_case_dispositions_clearance, ___Detectives) - 4 fixes
| Measure | Change |
|---------|--------|
| `Case Dispositions Subtitle` | TODAY() -> MAX(Date) |
| `Performance Icon` | TODAY() -> MAX(Date), removed emoji |
| `YoY Clearance Change` | TODAY() -> MAX(Date) |
| `Det1 Rolling13 EndDate` | TODAY() -> MAX(Date) |

### Traffic, Patrol, CSB, Social Media - 6 fixes
| Measure | Table | Change |
|---------|-------|--------|
| `Traffic Subtitle` | ___Traffic | TODAY() -> MAX(Period Label) |
| `Traffic Crashes Subtitle` | ___Traffic | TODAY() -> MAX(Period Label) |
| `Patrol Subtitle` | ___Patrol | TODAY() -> MAX(PeriodDate) |
| `Law Enforcement Duties Subtitle` | ___Patrol | TODAY() -> MAX(PeriodDate) |
| `CSB Activity Subtitle` | ___CSB_Monthly | TODAY() -> MAX(Date) |
| `Social Media Subtitle` | ___Social_Media | TODAY() -> MAX(PeriodDate) |

### Overtime, ESU, REMU, Chief - 4 fixes
| Measure | Table | Change |
|---------|-------|--------|
| `Subtitle_V3_Accrual` | ___Overtime_Timeoff_v3 | Static (String date cols) |
| `Time Report Subtitle` | ___Overtime_Timeoff_v3 | Static |
| `esu Table Subtitle` | ESU_13Month | MIN/MAX(Month_Year) |
| `Records & Evidence Subtitle` | ___REMU | MAX(PeriodDate) |
| `Chief LED Subtitle` | ___Chief2 | Static |

### SSOCC (___SSOCC_Data) - 6 fixes
| Measure | Change |
|---------|--------|
| `SSOCC Subtitle` | TODAY() -> MAX(Date), launch-aware |
| `CSB Card Title` | TODAY() -> MAX(Date) |
| `CSB Months` | TODAY() -> MAX(Date) |
| `CSB Rows in Window` | TODAY() -> MAX(Date) |
| `Detective CompStat YTD` | TODAY() -> MAX(Date) |
| `Analysis for CSB Total` | TODAY() -> MAX(Date) |

### Benchmark (___Benchmark, BM_Calendar) - 12 fixes
| Measure | Change |
|---------|--------|
| `BM_Calendar_Rolling13_Flag` | TODAY() -> MAX(Incident Date) |
| `BM_Rolling13_Count` | TODAY() -> MAX(Incident Date) |
| `BM_YoY_Change` | TODAY() -> MAX(Incident Date) |
| `BM_Rolling13_Count_Zero` | TODAY() -> MAX(Incident Date) |
| `Matrix Subtitle` | TODAY() -> MAX(Incident Date) |
| `Total Incidents Rolling 13` | TODAY() -> MAX(Incident Date) |
| `Most Frequent Event Type` | TODAY() -> MAX(Incident Date) |
| `Avg Incidents Per Month` | Inherits from Total Incidents |
| `Donut Subtitle` | TODAY() -> MAX(Incident Date) |
| `Donut Subtitle Short` | TODAY() -> MAX(Incident Date) |
| `Donut Subtitle with Count` | TODAY() -> MAX(Incident Date) |
| `Line Chart Subtitle` | TODAY() -> MAX(Incident Date) |
| `Line Chart Subtitle Short` | TODAY() -> MAX(Incident Date) |
| `IncidentCount_13Month` | TODAY() -> MAX(Incident Date) |

### STACP, TAS, Training, Misc - 5 fixes
| Measure | Table | Change |
|---------|-------|--------|
| `STACP P1 Subtitle` | ___STACP_pt_1_2 | TODAY() -> MAX(Date_Sort_Key) |
| `STACP P2 Subtitle` | ___STACP_pt_1_2 | TODAY() -> MAX(Date_Sort_Key) |
| `High Activity Subtitle` | ___STACP_pt_1_2 | TODAY() -> MAX(Date_Sort_Key) |
| `TAS Subtitle` | TAS_Dispatcher_Incident | TODAY() -> MIN/MAX(Month) |
| `Metrics Qual Subtitle` | ___In_Person_Training | TODAY() -> MIN/MAX(Date) |
| `Report Generated` | STACP_Measures | TODAY() -> MAX(Date_Sort_Key) |

---

## Verification

```dax
-- Run this DAX query to confirm zero TODAY()/NOW() references:
EVALUATE
SELECTCOLUMNS(
    FILTER(
        INFO.MEASURES(),
        CONTAINSSTRING([Expression], "TODAY") || CONTAINSSTRING([Expression], "NOW()")
    ),
    "Table", [TableID],
    "Measure", [Name]
)
-- Expected result: empty (0 rows)
```

**Result: 0 rows returned. Model is clean.**

---

## TMDL Export

- **Path:** `C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation\m_code\tmdl_export\`
- **Files:** 87 (up from 85 in previous export - added DFR_Summons.tmdl + LocalDateTable)
- **Timestamp:** 2026-03-17T22:09:13Z

---

## Remaining Manual Work

1. Run `response_time_batch_all_metrics.py` for February 2026
2. Close & Apply in Power BI Desktop
3. Build 3 Response Time visuals (see Visual_Build_Guide_2026_02_v2.md)
4. Build DFR Summons visual on Drone page
5. Verify Out-Reach engagement visual
6. Update visual_export_mapping.json
7. Save .pbix

---

*Session completed: 2026-03-17 | Master_Automation v1.18.9*
