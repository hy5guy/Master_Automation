# Prompt: Claude in Excel — DFR Directed Patrol Summons M Code

**Context:** Power BI M code for loading the DFR Summons table from `dfr_directed_patrol_enforcement.xlsx`. Use this prompt when updating the M Code Reference sheet in the workbook or when applying changes via Power BI Advanced Editor.

---

## Source

| Item | Value |
|------|-------|
| **Path** | `C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Drone\dfr_directed_patrol_enforcement.xlsx` |
| **Table** | `DFR_Summons` (Excel Table) |
| **Sheet fallback** | `DFR Summons Log` (if Table not found) |

---

## Dual Filter Spec (Summons_Recall + Summons_Status)

Exclude rows where either column indicates Dismiss or Void:

1. **Summons_Recall:** `Text.Contains(Text.Lower(recall), "dismiss")` or `"void"` → exclude
2. **Summons_Status:** `Text.Contains(Text.Trim(Text.Lower(status)), "dismiss")` or `"void"` → exclude (catches Dismissed, Voided, Void)

Use `Text.Contains` (not exact match) so "Voided" and variants are excluded.

---

## 13-Month Rolling Window

```
ReportMonth = Date.From(pReportMonth)
EndDate = Date.EndOfMonth(ReportMonth)
StartDate = Date.StartOfMonth(Date.AddMonths(ReportMonth, -12))
```

Filter: `[Date] >= StartDate and [Date] <= EndDate`

---

## Derived Columns

| Column | Purpose |
|--------|---------|
| **DateSortKey** | YYYYMMDD integer (e.g., 20260316) for row-level sorting |
| **Date_Sort_Key** | `Date.StartOfMonth([Date])` — sort-by column for MM-YY |
| **MM-YY** | Text display (e.g., "03-26") for matrix columns |
| **YearMonthKey** | YYYYMM integer (e.g., 202603) for grouping/trending |

---

## Description Shortening

Strip prefix `"Parking or stopping in designated "` → display only the zone type (e.g., "FIRE LANE/FIRE ZONE"). Source is ALL CAPS from Excel.

---

## Schema (Schema-Resilient)

| Excel Column | M Code Column | Notes |
|--------------|---------------|-------|
| Violation Type | Violation_Type | P/M/C or full category (legacy) |
| Violation Category | Violation_Category | P/M/C (Task 5 wiring) |
| Jurisdiction | Jurisdiction | Hackensack / Other Jurisdiction |

RenameMap, TypeMap, and FinalColumns include both Violation_Type and Violation_Category; schema-resilient `List.Select` applies only to existing columns.

---

## Related Documentation

- [docs/DFR_Summons_Claude_In_Excel_Development_Log.md](DFR_Summons_Claude_In_Excel_Development_Log.md) — 51-turn workbook evolution
- [docs/DFR_Summons_Documentation_Index.md](DFR_Summons_Documentation_Index.md) — Index of DFR docs and chatlogs
- [docs/chatlogs/DFR_Summons_ETL_Enhancement_And_Filter_Fix/](chatlogs/DFR_Summons_ETL_Enhancement_And_Filter_Fix/) — ETL enhancement, dual filter
- [docs/chatlogs/dfr_summons_update_title_39/](chatlogs/dfr_summons_update_title_39/) — Excel/VBA, ViolationData, Title 39
