# Summons Revenue DAX Measures

**Created:** 2026-03-21  
**Author:** R. A. Carucci  
**Resolves:** Issue #6  
**Depends on:** `summons_revenue_by_bureau.m` and `summons_revenue_by_violation_category.m` loaded as Power BI queries

## Instructions

Add these measures to the Power BI model after loading both M code queries into Power BI Desktop.
Each measure should be added to the appropriate table in the model view.

---

## Measure 1: Summons YTD Revenue (Total)

```dax
Summons YTD Revenue =
SUMX(summons_revenue_by_bureau, [Revenue])
```

**Purpose:** Total YTD summons fine revenue across all bureaus.  
**Table:** `summons_revenue_by_bureau`  
**Format:** Currency ($)

---

## Measure 2: Top Violation Category by Revenue

```dax
Top Violation Category =
FIRSTNONBLANK(
    TOPN(1, summons_revenue_by_violation_category, [Revenue], DESC),
    TRUE()
)
```

**Purpose:** Returns the violation category generating the most YTD revenue.  
**Table:** `summons_revenue_by_violation_category`  
**Format:** Text (for KPI card label)

---

## Validation

After loading both queries:
1. Spot-check a known summons row in `summons_slim_for_powerbi.csv` against `Summons YTD Revenue` total
2. Confirm `FINE_AMOUNT` is being summed (not counted) — row count should differ from revenue total
3. Confirm `Top Violation Category` returns a non-blank value for the current reporting period
4. Cross-check Jan 2026 revenue totals against backfill baseline data if available
