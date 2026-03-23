# Power BI YTD Measures & Page Enhancement Instructions

**Version:** 1.19.0 (DAX errata 2026-03-23) | **Date:** 2026-03-21 | **Author:** R. A. Carucci + Claude
**Target:** `15_Templates\Monthly_Report_Template.pbix`

---

## Page Rename Mapping

Apply in Power BI Desktop: right-click each page tab > Rename.

| Current Name | New Name |
|---|---|
| Arrest_13 | Arrest_13_Month |
| Response_Time | Response_Time |
| Benchmark | Benchmark |
| Out_Reach | Community_Outreach |
| (NEW) | Summons_YTD |
| Policy_And_Training_Qual | Training_And_Qualifications |
| REMU | Records_Evidence |
| Crime_Suppression_Bureau | Crime_Suppression |
| Detective_Case_Disposition | Detective_Dispositions |
| Detective_1 | Detectives_Part_A |
| Detective_1 (Part B) | Detectives_Part_B |
| STACP_Pt2 | STACP_Part_2 |
| STACP_Pt1 | STACP_Part_1 |
| Traffic_MVA | Traffic_Crashes |
| Traffic | Traffic_Enforcement |
| ESU | ESU_Operations |
| Patrol | Patrol_Division |

---

## YTD Date Window (Standard Pattern)

**Conceptual window** (aligned with the Power Query parameter `pReportMonth`):

```
YTD Start = first day of calendar year for the report year
YTD End   = end of the report month (same month as pReportMonth)
```

Example: if `pReportMonth` = 1 March 2026, YTD runs 1 Jan 2026 through 31 Mar 2026.

### CRITICAL: `pReportMonth` is not valid DAX by default

The **`pReportMonth`** query is an **M (Power Query) parameter**. It drives query folding and refresh, but **`pReportMonth` is not a DAX table, variable, or function**. Measures that contain `YEAR(pReportMonth)` or `EOMONTH(pReportMonth, 0)` will fail with:

`Failed to resolve name 'pReportMonth'. It is not a valid table, variable, or function name.`

**Use one of these in DAX instead:**

1. **`___DimMonth` bridge (recommended for this template)** — same report-month axis as rolling 13-month visuals:

```dax
VAR ReportMonthStart = MAX ( '___DimMonth'[MonthStart] )
VAR YtdStart = DATE ( YEAR ( ReportMonthStart ), 1, 1 )
VAR YtdEnd = EOMONTH ( ReportMonthStart, 0 )
```

2. **Load report month into the model** — e.g. a one-row table `ReportParameters[ReportMonth]` from M, then `VAR RM = MAX ( ReportParameters[ReportMonth] )`.

When adding **titles or subtitles** for YTD visuals, use the same `ReportMonthStart` pattern; do not reference `pReportMonth` inside measure text logic unless exposed as a column.

---

## MEASURES TABLE

Create a dedicated measures table (if not already present): Modeling > New Table > `STACP_Measures = {1}`, then hide the table. All YTD measures go here for organization.

If `STACP_Measures` already exists, add measures there. Otherwise create new.

---

## Page 1: Community_Outreach (was Out_Reach)

**Source table:** `___Combined_Outreach_All`
**Date column:** `Date`
**Existing measures:** `Outreach Sessions`, `Outreach Total Hours`, `Outreach Total Attendees`

### DAX Measures

```dax
Outreach Events YTD =
CALCULATE(
    COUNTROWS('___Combined_Outreach_All'),
    '___Combined_Outreach_All'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Combined_Outreach_All'[Date] <= EOMONTH(pReportMonth, 0)
)
```

```dax
Outreach Hours YTD =
CALCULATE(
    SUM('___Combined_Outreach_All'[Event Duration (Hours)]),
    '___Combined_Outreach_All'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Combined_Outreach_All'[Date] <= EOMONTH(pReportMonth, 0)
)
```

```dax
Outreach Attendees YTD =
CALCULATE(
    SUM('___Combined_Outreach_All'[Number of Police Department Attendees]),
    '___Combined_Outreach_All'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Combined_Outreach_All'[Date] <= EOMONTH(pReportMonth, 0)
)
```

### Visual Instructions
1. Add 3 **Card** visuals across the top of the page
2. Fields: `[Outreach Events YTD]`, `[Outreach Hours YTD]`, `[Outreach Attendees YTD]`
3. Card titles: "Total Events YTD", "Total Hours YTD", "Total Attendees YTD"
4. Format: Match existing card style (navy background #1a2744, gold accent #c8a84b, white text)

---

## Page 2: Training_And_Qualifications (was Policy_And_Training_Qual)

**Source tables:** `___In_Person_Training`, `___Cost_of_Training`
**Date columns:** `___In_Person_Training[Start date]`, `___Cost_of_Training[Period_Sort]` (YYYYMM integer)

### DAX Measures

```dax
Training Classes YTD =
CALCULATE(
    COUNTROWS('___In_Person_Training'),
    '___In_Person_Training'[Start date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___In_Person_Training'[Start date] <= EOMONTH(pReportMonth, 0)
)
```

```dax
Training Duration YTD =
CALCULATE(
    SUM('___In_Person_Training'[Course Duration]),
    '___In_Person_Training'[Start date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___In_Person_Training'[Start date] <= EOMONTH(pReportMonth, 0)
)
```

```dax
Training Cost YTD =
CALCULATE(
    SUM('___Cost_of_Training'[Cost]),
    '___Cost_of_Training'[Period_Sort] >= YEAR(pReportMonth) * 100 + 1,
    '___Cost_of_Training'[Period_Sort] <= YEAR(pReportMonth) * 100 + MONTH(pReportMonth)
)
```

```dax
Training Attendees YTD =
CALCULATE(
    SUM('___In_Person_Training'[Attendees Count]),
    '___In_Person_Training'[Start date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___In_Person_Training'[Start date] <= EOMONTH(pReportMonth, 0)
)
```

```dax
In-Person Training YTD =
CALCULATE(
    COUNTROWS('___In_Person_Training'),
    '___In_Person_Training'[Start date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___In_Person_Training'[Start date] <= EOMONTH(pReportMonth, 0)
)
```

```dax
Online Training YTD =
CALCULATE(
    SUM('___Cost_of_Training'[Cost]),
    '___Cost_of_Training'[Period_Sort] >= YEAR(pReportMonth) * 100 + 1,
    '___Cost_of_Training'[Period_Sort] <= YEAR(pReportMonth) * 100 + MONTH(pReportMonth),
    '___Cost_of_Training'[Delivery_Type] = "Online"
)
```

### Visual Instructions
1. Add 5 **Card** visuals in a row across the top
2. Fields: `[Training Classes YTD]`, `[Training Duration YTD]`, `[Training Cost YTD]` (format as currency), `[In-Person Training YTD]`, `[Online Training YTD]` (format as currency)
3. Card titles: "Classes Attended YTD", "Course Duration YTD", "Total Cost YTD", "In-Person YTD", "Online Training YTD"

---

## Page 3: Records_Evidence (was REMU)

**Source table:** `___REMU`
**Date column:** `PeriodDate`
**Category column:** `Tracked Items`

### DAX Measures

The REMU table uses `Tracked Items` to identify each metric. Each KPI filters to the specific item name.

```dax
REMU Records Requests YTD =
CALCULATE(
    SUM('___REMU'[Total]),
    '___REMU'[PeriodDate] >= DATE(YEAR(pReportMonth), 1, 1),
    '___REMU'[PeriodDate] <= EOMONTH(pReportMonth, 0),
    '___REMU'[Tracked Items] = "Records Requests"
)
```

```dax
REMU OPRA Requests YTD =
CALCULATE(
    SUM('___REMU'[Total]),
    '___REMU'[PeriodDate] >= DATE(YEAR(pReportMonth), 1, 1),
    '___REMU'[PeriodDate] <= EOMONTH(pReportMonth, 0),
    '___REMU'[Tracked Items] = "OPRA Requests"
)
```

```dax
REMU Discovery Requests YTD =
CALCULATE(
    SUM('___REMU'[Total]),
    '___REMU'[PeriodDate] >= DATE(YEAR(pReportMonth), 1, 1),
    '___REMU'[PeriodDate] <= EOMONTH(pReportMonth, 0),
    '___REMU'[Tracked Items] = "Discovery Requests"
)
```

```dax
REMU NIBRS Entries YTD =
CALCULATE(
    SUM('___REMU'[Total]),
    '___REMU'[PeriodDate] >= DATE(YEAR(pReportMonth), 1, 1),
    '___REMU'[PeriodDate] <= EOMONTH(pReportMonth, 0),
    '___REMU'[Tracked Items] = "NIBRS Entries"
)
```

```dax
REMU Applications Permits YTD =
CALCULATE(
    SUM('___REMU'[Total]),
    '___REMU'[PeriodDate] >= DATE(YEAR(pReportMonth), 1, 1),
    '___REMU'[PeriodDate] <= EOMONTH(pReportMonth, 0),
    '___REMU'[Tracked Items] = "Application(s) - Permit(s)"
)
```

```dax
REMU Background Checks YTD =
CALCULATE(
    SUM('___REMU'[Total]),
    '___REMU'[PeriodDate] >= DATE(YEAR(pReportMonth), 1, 1),
    '___REMU'[PeriodDate] <= EOMONTH(pReportMonth, 0),
    '___REMU'[Tracked Items] = "Background Checks"
)
```

```dax
REMU Evidence Received YTD =
CALCULATE(
    SUM('___REMU'[Total]),
    '___REMU'[PeriodDate] >= DATE(YEAR(pReportMonth), 1, 1),
    '___REMU'[PeriodDate] <= EOMONTH(pReportMonth, 0),
    '___REMU'[Tracked Items] = "Evidence Received"
)
```

### Visual Instructions
1. Add 7 **Card** visuals (two rows of 3-4)
2. Use the measures above
3. **IMPORTANT:** Verify exact `Tracked Items` values match the REMU workbook. If a measure returns blank, the string doesn't match exactly. Check with: `DISTINCT('___REMU'[Tracked Items])` in a table visual.

---

## Page 4: Crime_Suppression (was Crime_Suppression_Bureau)

**Source table:** `___CSB_Monthly`
**Date column:** `Date`
**Category column:** `CSB_Category`

### DAX Measures

```dax
CSB Arrests YTD =
CALCULATE(
    SUM('___CSB_Monthly'[Value]),
    '___CSB_Monthly'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___CSB_Monthly'[Date] <= EOMONTH(pReportMonth, 0),
    '___CSB_Monthly'[CSB_Category] = "Arrests"
)
```

```dax
CSB Currency Seized YTD =
CALCULATE(
    SUM('___CSB_Monthly'[Value]),
    '___CSB_Monthly'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___CSB_Monthly'[Date] <= EOMONTH(pReportMonth, 0),
    '___CSB_Monthly'[CSB_Category] = "Currency Seized"
)
```

```dax
CSB Drug Arrests YTD =
CALCULATE(
    SUM('___CSB_Monthly'[Value]),
    '___CSB_Monthly'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___CSB_Monthly'[Date] <= EOMONTH(pReportMonth, 0),
    '___CSB_Monthly'[CSB_Category] = "Drug-Related Arrests"
)
```

```dax
CSB Generated Complaints YTD =
CALCULATE(
    SUM('___CSB_Monthly'[Value]),
    '___CSB_Monthly'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___CSB_Monthly'[Date] <= EOMONTH(pReportMonth, 0),
    '___CSB_Monthly'[CSB_Category] = "Generated Complaints"
)
```

```dax
CSB High Value Items YTD =
CALCULATE(
    SUM('___CSB_Monthly'[Value]),
    '___CSB_Monthly'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___CSB_Monthly'[Date] <= EOMONTH(pReportMonth, 0),
    '___CSB_Monthly'[CSB_Category] = "High Value Items Seized"
)
```

```dax
CSB MV Thefts YTD =
CALCULATE(
    SUM('___CSB_Monthly'[Value]),
    '___CSB_Monthly'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___CSB_Monthly'[Date] <= EOMONTH(pReportMonth, 0),
    '___CSB_Monthly'[CSB_Category] = "Motor Vehicle Thefts"
)
```

```dax
CSB Weapons Seized YTD =
CALCULATE(
    SUM('___CSB_Monthly'[Value]),
    '___CSB_Monthly'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___CSB_Monthly'[Date] <= EOMONTH(pReportMonth, 0),
    '___CSB_Monthly'[CSB_Category] = "Weapons Seized"
)
```

### Visual Instructions
1. Add 7 **Card** visuals across top
2. Format `Currency Seized` card as currency ($)
3. Verify exact `CSB_Category` values with a table visual first

---

## Page 5: Detective_Dispositions (was Detective_Case_Disposition)

**Source table:** `___Det_case_dispositions_clearance`
**Date column:** `Date`
**Category column:** `Closed Case Dispositions`

### DAX Measures

```dax
Det Active Admin Closed YTD =
CALCULATE(
    SUM('___Det_case_dispositions_clearance'[Value]),
    '___Det_case_dispositions_clearance'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Det_case_dispositions_clearance'[Date] <= EOMONTH(pReportMonth, 0),
    '___Det_case_dispositions_clearance'[Closed Case Dispositions] = "Active / Administratively Closed"
)
```

```dax
Det Arrest YTD =
CALCULATE(
    SUM('___Det_case_dispositions_clearance'[Value]),
    '___Det_case_dispositions_clearance'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Det_case_dispositions_clearance'[Date] <= EOMONTH(pReportMonth, 0),
    '___Det_case_dispositions_clearance'[Closed Case Dispositions] = "Arrest"
)
```

```dax
Det Complaint Signed YTD =
CALCULATE(
    SUM('___Det_case_dispositions_clearance'[Value]),
    '___Det_case_dispositions_clearance'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Det_case_dispositions_clearance'[Date] <= EOMONTH(pReportMonth, 0),
    '___Det_case_dispositions_clearance'[Closed Case Dispositions] = "Complaint Signed"
)
```

```dax
Det Ex Cleared Closed YTD =
CALCULATE(
    SUM('___Det_case_dispositions_clearance'[Value]),
    '___Det_case_dispositions_clearance'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Det_case_dispositions_clearance'[Date] <= EOMONTH(pReportMonth, 0),
    '___Det_case_dispositions_clearance'[Closed Case Dispositions] = "Ex Cleared/Closed"
)
```

```dax
Det Unfounded Closed YTD =
CALCULATE(
    SUM('___Det_case_dispositions_clearance'[Value]),
    '___Det_case_dispositions_clearance'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Det_case_dispositions_clearance'[Date] <= EOMONTH(pReportMonth, 0),
    '___Det_case_dispositions_clearance'[Closed Case Dispositions] = "Unfounded/Closed"
)
```

### Visual Instructions
1. Add 5 **Card** visuals across top
2. Verify exact disposition category names match the data

---

## Page 6: Detectives_Part_A (was Detective_1)

**Source table:** `___Detectives`
**Date column:** `Date`
**Category column:** `Tracked Items`

### DAX Measures

```dax
Det Agg Assault YTD =
CALCULATE(
    SUM('___Detectives'[Value]),
    '___Detectives'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Detectives'[Date] <= EOMONTH(pReportMonth, 0),
    '___Detectives'[Tracked Items] = "Aggravated Assault"
)
```

```dax
Det Arson YTD =
CALCULATE(
    SUM('___Detectives'[Value]),
    '___Detectives'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Detectives'[Date] <= EOMONTH(pReportMonth, 0),
    '___Detectives'[Tracked Items] = "Arson"
)
```

```dax
Det Bias YTD =
CALCULATE(
    SUM('___Detectives'[Value]),
    '___Detectives'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Detectives'[Date] <= EOMONTH(pReportMonth, 0),
    '___Detectives'[Tracked Items] = "Bias"
)
```

```dax
Det Burglary Auto YTD =
CALCULATE(
    SUM('___Detectives'[Value]),
    '___Detectives'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Detectives'[Date] <= EOMONTH(pReportMonth, 0),
    '___Detectives'[Tracked Items] = "Burglary-Auto"
)
```

```dax
Det Burglary Commercial YTD =
CALCULATE(
    SUM('___Detectives'[Value]),
    '___Detectives'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Detectives'[Date] <= EOMONTH(pReportMonth, 0),
    '___Detectives'[Tracked Items] = "Burglary-Commercial"
)
```

```dax
Det Burglary Residence YTD =
CALCULATE(
    SUM('___Detectives'[Value]),
    '___Detectives'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Detectives'[Date] <= EOMONTH(pReportMonth, 0),
    '___Detectives'[Tracked Items] = "Burglary-Residence"
)
```

```dax
Det Criminal Sexual Contact YTD =
CALCULATE(
    SUM('___Detectives'[Value]),
    '___Detectives'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Detectives'[Date] <= EOMONTH(pReportMonth, 0),
    '___Detectives'[Tracked Items] = "Criminal Sexual Contact"
)
```

---

## Page 7: Detectives_Part_B (was Detective_1 Part B)

**Source table:** `___Detectives`
**Date column:** `Date`
**Category column:** `Tracked Items`

### DAX Measures

```dax
Det Firearm Background YTD =
CALCULATE(
    SUM('___Detectives'[Value]),
    '___Detectives'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Detectives'[Date] <= EOMONTH(pReportMonth, 0),
    '___Detectives'[Tracked Items] = "Firearm Background Checks"
)
```

```dax
Det Firearm Investigations YTD =
CALCULATE(
    SUM('___Detectives'[Value]),
    '___Detectives'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Detectives'[Date] <= EOMONTH(pReportMonth, 0),
    '___Detectives'[Tracked Items] = "Firearm Investigations"
)
```

```dax
Det Generated Complaints YTD =
CALCULATE(
    SUM('___Detectives'[Value]),
    '___Detectives'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Detectives'[Date] <= EOMONTH(pReportMonth, 0),
    '___Detectives'[Tracked Items] = "Generated Complaints"
)
```

```dax
Det Lewdness YTD =
CALCULATE(
    SUM('___Detectives'[Value]),
    '___Detectives'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Detectives'[Date] <= EOMONTH(pReportMonth, 0),
    '___Detectives'[Tracked Items] = "Lewdness"
)
```

```dax
Det MV Theft YTD =
CALCULATE(
    SUM('___Detectives'[Value]),
    '___Detectives'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Detectives'[Date] <= EOMONTH(pReportMonth, 0),
    '___Detectives'[Tracked Items] = "Motor Vehicle Theft"
)
```

```dax
Det Robbery YTD =
CALCULATE(
    SUM('___Detectives'[Value]),
    '___Detectives'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Detectives'[Date] <= EOMONTH(pReportMonth, 0),
    '___Detectives'[Tracked Items] = "Robbery"
)
```

```dax
Det Sexual Assault YTD =
CALCULATE(
    SUM('___Detectives'[Value]),
    '___Detectives'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Detectives'[Date] <= EOMONTH(pReportMonth, 0),
    '___Detectives'[Tracked Items] = "Sexual Assault"
)
```

```dax
Det Terroristic Threats YTD =
CALCULATE(
    SUM('___Detectives'[Value]),
    '___Detectives'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Detectives'[Date] <= EOMONTH(pReportMonth, 0),
    '___Detectives'[Tracked Items] = "Terroristic Threats"
)
```

```dax
Det Theft YTD =
CALCULATE(
    SUM('___Detectives'[Value]),
    '___Detectives'[Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___Detectives'[Date] <= EOMONTH(pReportMonth, 0),
    '___Detectives'[Tracked Items] = "Theft"
)
```

---

## Page 8: STACP_Part_1 (was STACP_Pt1)

**Source table:** `___STACP_pt_1_2`
**Date column:** `Report_Start_Date` / `Report_End_Date`
**Category column:** `Tracked Items`
**Filter:** `Source_Category = "Part 1"` (if applicable — verify in data)

### DAX Measures

For STACP, the date filter uses `Report_End_Date` (end of reporting period):

```dax
STACP1 Arrests YTD =
CALCULATE(
    SUM('___STACP_pt_1_2'[Value]),
    '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0),
    '___STACP_pt_1_2'[Tracked Items] = "Arrests"
)
```

```dax
STACP1 Assaults YTD =
CALCULATE(
    SUM('___STACP_pt_1_2'[Value]),
    '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0),
    '___STACP_pt_1_2'[Tracked Items] = "Assaults"
)
```

```dax
STACP1 Burglary YTD =
CALCULATE(
    SUM('___STACP_pt_1_2'[Value]),
    '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0),
    '___STACP_pt_1_2'[Tracked Items] = "Burglary"
)
```

```dax
STACP1 CDS YTD =
CALCULATE(
    SUM('___STACP_pt_1_2'[Value]),
    '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0),
    '___STACP_pt_1_2'[Tracked Items] = "CDS"
)
```

```dax
STACP1 Child Abuse YTD =
CALCULATE(
    SUM('___STACP_pt_1_2'[Value]),
    '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0),
    '___STACP_pt_1_2'[Tracked Items] = "Child Abuse"
)
```

```dax
STACP1 Child Endangerment YTD =
CALCULATE(
    SUM('___STACP_pt_1_2'[Value]),
    '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0),
    '___STACP_pt_1_2'[Tracked Items] = "Child Endangerment"
)
```

```dax
STACP1 Criminal Mischief YTD =
CALCULATE(
    SUM('___STACP_pt_1_2'[Value]),
    '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0),
    '___STACP_pt_1_2'[Tracked Items] = "Criminal Mischief"
)
```

```dax
STACP1 Curbside Warning YTD =
CALCULATE(
    SUM('___STACP_pt_1_2'[Value]),
    '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0),
    '___STACP_pt_1_2'[Tracked Items] = "Curbside Warning"
)
```

```dax
STACP1 Cyber Harassment YTD =
CALCULATE(
    SUM('___STACP_pt_1_2'[Value]),
    '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0),
    '___STACP_pt_1_2'[Tracked Items] = "Cyber Harassment"
)
```

```dax
STACP1 DCPP Notification YTD =
CALCULATE(
    SUM('___STACP_pt_1_2'[Value]),
    '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0),
    '___STACP_pt_1_2'[Tracked Items] = "DCP&P Notification"
)
```

```dax
STACP1 DCPP Referrals YTD =
CALCULATE(
    SUM('___STACP_pt_1_2'[Value]),
    '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0),
    '___STACP_pt_1_2'[Tracked Items] = "DCP&P Referral(s)"
)
```

```dax
STACP1 Juvenile Complaints YTD =
CALCULATE(
    SUM('___STACP_pt_1_2'[Value]),
    '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0),
    '___STACP_pt_1_2'[Tracked Items] = "Juvenile Complaints"
)
```

```dax
STACP1 Juvenile Incident YTD =
CALCULATE(
    SUM('___STACP_pt_1_2'[Value]),
    '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0),
    '___STACP_pt_1_2'[Tracked Items] = "Juvenile Incident"
)
```

```dax
STACP1 Juvenile Short Term Custody YTD =
CALCULATE(
    SUM('___STACP_pt_1_2'[Value]),
    '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1),
    '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0),
    '___STACP_pt_1_2'[Tracked Items] = "Juvenile Short-Term Custody"
)
```

---

## Page 9: STACP_Part_2 (was STACP_Pt2)

**Source table:** `___STACP_pt_1_2`
**Same pattern as Part 1**

### DAX Measures

```dax
STACP2 Luring YTD =
CALCULATE(SUM('___STACP_pt_1_2'[Value]), '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1), '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0), '___STACP_pt_1_2'[Tracked Items] = "Luring")
```

```dax
STACP2 Missing Person YTD =
CALCULATE(SUM('___STACP_pt_1_2'[Value]), '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1), '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0), '___STACP_pt_1_2'[Tracked Items] = "Missing Person")
```

```dax
STACP2 Station House Adj YTD =
CALCULATE(SUM('___STACP_pt_1_2'[Value]), '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1), '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0), '___STACP_pt_1_2'[Tracked Items] = "Station House Adjustments")
```

```dax
STACP2 Terroristic Threats YTD =
CALCULATE(SUM('___STACP_pt_1_2'[Value]), '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1), '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0), '___STACP_pt_1_2'[Tracked Items] = "Terroristic Threats")
```

```dax
STACP2 Theft YTD =
CALCULATE(SUM('___STACP_pt_1_2'[Value]), '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1), '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0), '___STACP_pt_1_2'[Tracked Items] = "Theft")
```

```dax
STACP2 Threat Assessments YTD =
CALCULATE(SUM('___STACP_pt_1_2'[Value]), '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1), '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0), '___STACP_pt_1_2'[Tracked Items] = "Threat Assessments")
```

```dax
STACP2 Trespassing YTD =
CALCULATE(SUM('___STACP_pt_1_2'[Value]), '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1), '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0), '___STACP_pt_1_2'[Tracked Items] = "Trespassing")
```

```dax
STACP2 Underage Alcohol YTD =
CALCULATE(SUM('___STACP_pt_1_2'[Value]), '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1), '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0), '___STACP_pt_1_2'[Tracked Items] = "Underage Possession of Alcohol")
```

```dax
STACP2 Underage CDS YTD =
CALCULATE(SUM('___STACP_pt_1_2'[Value]), '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1), '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0), '___STACP_pt_1_2'[Tracked Items] = "Underage Possession of CDs")
```

```dax
STACP2 Weapons YTD =
CALCULATE(SUM('___STACP_pt_1_2'[Value]), '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1), '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0), '___STACP_pt_1_2'[Tracked Items] = "Weapons")
```

```dax
STACP2 Welfare Checks YTD =
CALCULATE(SUM('___STACP_pt_1_2'[Value]), '___STACP_pt_1_2'[Report_End_Date] >= DATE(YEAR(pReportMonth), 1, 1), '___STACP_pt_1_2'[Report_End_Date] <= EOMONTH(pReportMonth, 0), '___STACP_pt_1_2'[Tracked Items] = "Welfare Checks")
```

---

## Page 10: Traffic_Crashes (was Traffic_MVA)

**Source table:** `___Traffic`
**Date column:** `Date`
**Category column:** `Tracked Items`

### DAX Measures

```dax
Traffic All MVA YTD =
CALCULATE(SUM('___Traffic'[Value]), '___Traffic'[Date] >= DATE(YEAR(pReportMonth), 1, 1), '___Traffic'[Date] <= EOMONTH(pReportMonth, 0), '___Traffic'[Tracked Items] = "All Motor Vehicle Accidents")
```

```dax
Traffic Bicyclist Struck YTD =
CALCULATE(SUM('___Traffic'[Value]), '___Traffic'[Date] >= DATE(YEAR(pReportMonth), 1, 1), '___Traffic'[Date] <= EOMONTH(pReportMonth, 0), '___Traffic'[Tracked Items] = "Bicyclist Struck")
```

```dax
Traffic Hit Run YTD =
CALCULATE(SUM('___Traffic'[Value]), '___Traffic'[Date] >= DATE(YEAR(pReportMonth), 1, 1), '___Traffic'[Date] <= EOMONTH(pReportMonth, 0), '___Traffic'[Tracked Items] = "Hit & Run")
```

```dax
Traffic Pedestrian Struck YTD =
CALCULATE(SUM('___Traffic'[Value]), '___Traffic'[Date] >= DATE(YEAR(pReportMonth), 1, 1), '___Traffic'[Date] <= EOMONTH(pReportMonth, 0), '___Traffic'[Tracked Items] = "Pedestrian Struck")
```

```dax
Traffic Police Vehicle YTD =
CALCULATE(SUM('___Traffic'[Value]), '___Traffic'[Date] >= DATE(YEAR(pReportMonth), 1, 1), '___Traffic'[Date] <= EOMONTH(pReportMonth, 0), '___Traffic'[Tracked Items] = "Police Vehicle")
```

```dax
Traffic With Injury YTD =
CALCULATE(SUM('___Traffic'[Value]), '___Traffic'[Date] >= DATE(YEAR(pReportMonth), 1, 1), '___Traffic'[Date] <= EOMONTH(pReportMonth, 0), '___Traffic'[Tracked Items] = "With Injury")
```

---

## Page 11: Traffic_Enforcement (was Traffic)

**Source table:** `___Traffic`
**Date column:** `Date`
**Category column:** `Tracked Items`

### DAX Measures

```dax
Traffic DUI YTD =
CALCULATE(SUM('___Traffic'[Value]), '___Traffic'[Date] >= DATE(YEAR(pReportMonth), 1, 1), '___Traffic'[Date] <= EOMONTH(pReportMonth, 0), '___Traffic'[Tracked Items] = "DUI Incidents")
```

```dax
Traffic Fatal YTD =
CALCULATE(SUM('___Traffic'[Value]), '___Traffic'[Date] >= DATE(YEAR(pReportMonth), 1, 1), '___Traffic'[Date] <= EOMONTH(pReportMonth, 0), '___Traffic'[Tracked Items] = "Fatal Incidents")
```

```dax
Traffic Assigned MVA HitRun YTD =
CALCULATE(SUM('___Traffic'[Value]), '___Traffic'[Date] >= DATE(YEAR(pReportMonth), 1, 1), '___Traffic'[Date] <= EOMONTH(pReportMonth, 0), '___Traffic'[Tracked Items] = "Assigned MVA Hit & Run Investigations")
```

```dax
Traffic Closed MVA HitRun YTD =
CALCULATE(SUM('___Traffic'[Value]), '___Traffic'[Date] >= DATE(YEAR(pReportMonth), 1, 1), '___Traffic'[Date] <= EOMONTH(pReportMonth, 0), '___Traffic'[Tracked Items] = "Closed MVA Hit & Run Investigations")
```

```dax
Traffic Officer Accident Reviews YTD =
CALCULATE(SUM('___Traffic'[Value]), '___Traffic'[Date] >= DATE(YEAR(pReportMonth), 1, 1), '___Traffic'[Date] <= EOMONTH(pReportMonth, 0), '___Traffic'[Tracked Items] = "Officer-Involved Accident Reviews")
```

```dax
Traffic MV Stops YTD =
CALCULATE(SUM('___Traffic'[Value]), '___Traffic'[Date] >= DATE(YEAR(pReportMonth), 1, 1), '___Traffic'[Date] <= EOMONTH(pReportMonth, 0), '___Traffic'[Tracked Items] = "Motor Vehicle Stops")
```

```dax
Traffic City Ord Violations YTD =
CALCULATE(SUM('___Traffic'[Value]), '___Traffic'[Date] >= DATE(YEAR(pReportMonth), 1, 1), '___Traffic'[Date] <= EOMONTH(pReportMonth, 0), '___Traffic'[Tracked Items] = "City Ordinance Violations Issued")
```

```dax
Traffic City Ord Warnings YTD =
CALCULATE(SUM('___Traffic'[Value]), '___Traffic'[Date] >= DATE(YEAR(pReportMonth), 1, 1), '___Traffic'[Date] <= EOMONTH(pReportMonth, 0), '___Traffic'[Tracked Items] = "City Ordinance Warnings Issued")
```

```dax
Traffic Parking Fees YTD =
CALCULATE(SUM('___Traffic'[Value]), '___Traffic'[Date] >= DATE(YEAR(pReportMonth), 1, 1), '___Traffic'[Date] <= EOMONTH(pReportMonth, 0), '___Traffic'[Tracked Items] = "Parking Fees Collected")
```

---

## Page 12: ESU_Operations (was ESU)

**Source table:** `ESU_13Month`
**Date column:** `MonthKey` (date type, 1st of month)
**Category column:** `TrackedItem`

### DAX Measures

```dax
ESU Arrests YTD =
CALCULATE(SUM('ESU_13Month'[Total]), 'ESU_13Month'[MonthKey] >= DATE(YEAR(pReportMonth), 1, 1), 'ESU_13Month'[MonthKey] <= EOMONTH(pReportMonth, 0), 'ESU_13Month'[TrackedItem] = "Arrest(s)")
```

```dax
ESU Assist Other Bureau YTD =
CALCULATE(SUM('ESU_13Month'[Total]), 'ESU_13Month'[MonthKey] >= DATE(YEAR(pReportMonth), 1, 1), 'ESU_13Month'[MonthKey] <= EOMONTH(pReportMonth, 0), 'ESU_13Month'[TrackedItem] = "Assist Other Bureau")
```

```dax
ESU OOS YTD =
CALCULATE(SUM('ESU_13Month'[Total]), 'ESU_13Month'[MonthKey] >= DATE(YEAR(pReportMonth), 1, 1), 'ESU_13Month'[MonthKey] <= EOMONTH(pReportMonth, 0), 'ESU_13Month'[TrackedItem] = "ESU OOS")
```

```dax
ESU Single Operator YTD =
CALCULATE(SUM('ESU_13Month'[Total]), 'ESU_13Month'[MonthKey] >= DATE(YEAR(pReportMonth), 1, 1), 'ESU_13Month'[MonthKey] <= EOMONTH(pReportMonth, 0), 'ESU_13Month'[TrackedItem] = "ESU Single Operator")
```

```dax
ESU Forcible Entries YTD =
CALCULATE(SUM('ESU_13Month'[Total]), 'ESU_13Month'[MonthKey] >= DATE(YEAR(pReportMonth), 1, 1), 'ESU_13Month'[MonthKey] <= EOMONTH(pReportMonth, 0), 'ESU_13Month'[TrackedItem] = "Forcible Entries")
```

```dax
ESU ICS Functions YTD =
CALCULATE(SUM('ESU_13Month'[Total]), 'ESU_13Month'[MonthKey] >= DATE(YEAR(pReportMonth), 1, 1), 'ESU_13Month'[MonthKey] <= EOMONTH(pReportMonth, 0), 'ESU_13Month'[TrackedItem] = "ICS Functions (IAPs/AARs)")
```

```dax
ESU MV Lock Outs YTD =
CALCULATE(SUM('ESU_13Month'[Total]), 'ESU_13Month'[MonthKey] >= DATE(YEAR(pReportMonth), 1, 1), 'ESU_13Month'[MonthKey] <= EOMONTH(pReportMonth, 0), 'ESU_13Month'[TrackedItem] = "MV Lock Outs")
```

```dax
ESU Targeted Area Patrols YTD =
CALCULATE(SUM('ESU_13Month'[Total]), 'ESU_13Month'[MonthKey] >= DATE(YEAR(pReportMonth), 1, 1), 'ESU_13Month'[MonthKey] <= EOMONTH(pReportMonth, 0), 'ESU_13Month'[TrackedItem] = "Targeted Area Patrols")
```

---

## Page 13: Patrol_Division (was Patrol)

**Source table:** `___Patrol`
**Date column:** `PeriodDate`
**Category column:** `Tracked Items`

### DAX Measures

```dax
Patrol ARRIVE Referral YTD =
CALCULATE(SUM('___Patrol'[Total]), '___Patrol'[PeriodDate] >= DATE(YEAR(pReportMonth), 1, 1), '___Patrol'[PeriodDate] <= EOMONTH(pReportMonth, 0), '___Patrol'[Tracked Items] = "Arrive Program Referral")
```

```dax
Patrol Calls for Service YTD =
CALCULATE(SUM('___Patrol'[Total]), '___Patrol'[PeriodDate] >= DATE(YEAR(pReportMonth), 1, 1), '___Patrol'[PeriodDate] <= EOMONTH(pReportMonth, 0), '___Patrol'[Tracked Items] = "Calls for Service")
```

```dax
Patrol CDS Arrests YTD =
CALCULATE(SUM('___Patrol'[Total]), '___Patrol'[PeriodDate] >= DATE(YEAR(pReportMonth), 1, 1), '___Patrol'[PeriodDate] <= EOMONTH(pReportMonth, 0), '___Patrol'[Tracked Items] = "CDS Arrests")
```

```dax
Patrol DUI Arrests YTD =
CALCULATE(SUM('___Patrol'[Total]), '___Patrol'[PeriodDate] >= DATE(YEAR(pReportMonth), 1, 1), '___Patrol'[PeriodDate] <= EOMONTH(pReportMonth, 0), '___Patrol'[Tracked Items] = "DUI Arrests")
```

```dax
Patrol DV Arrests YTD =
CALCULATE(SUM('___Patrol'[Total]), '___Patrol'[PeriodDate] >= DATE(YEAR(pReportMonth), 1, 1), '___Patrol'[PeriodDate] <= EOMONTH(pReportMonth, 0), '___Patrol'[Tracked Items] = "DV Arrests")
```

```dax
Patrol DV Incidents YTD =
CALCULATE(SUM('___Patrol'[Total]), '___Patrol'[PeriodDate] >= DATE(YEAR(pReportMonth), 1, 1), '___Patrol'[PeriodDate] <= EOMONTH(pReportMonth, 0), '___Patrol'[Tracked Items] = "DV Incidents")
```

```dax
Patrol Mental Health YTD =
CALCULATE(SUM('___Patrol'[Total]), '___Patrol'[PeriodDate] >= DATE(YEAR(pReportMonth), 1, 1), '___Patrol'[PeriodDate] <= EOMONTH(pReportMonth, 0), '___Patrol'[Tracked Items] = "Mental Health Calls")
```

```dax
Patrol MV Stops YTD =
CALCULATE(SUM('___Patrol'[Total]), '___Patrol'[PeriodDate] >= DATE(YEAR(pReportMonth), 1, 1), '___Patrol'[PeriodDate] <= EOMONTH(pReportMonth, 0), '___Patrol'[Tracked Items] = "Motor Vehicle Stops")
```

```dax
Patrol NARCAN YTD =
CALCULATE(SUM('___Patrol'[Total]), '___Patrol'[PeriodDate] >= DATE(YEAR(pReportMonth), 1, 1), '___Patrol'[PeriodDate] <= EOMONTH(pReportMonth, 0), '___Patrol'[Tracked Items] = "NARCAN Deployment")
```

```dax
Patrol Self Initiated Arrests YTD =
CALCULATE(SUM('___Patrol'[Total]), '___Patrol'[PeriodDate] >= DATE(YEAR(pReportMonth), 1, 1), '___Patrol'[PeriodDate] <= EOMONTH(pReportMonth, 0), '___Patrol'[Tracked Items] = "Self-Initiated Arrests")
```

---

## Page 14: Summons_YTD (NEW PAGE)

**Source table:** `summons_13month_trend`
**Date column:** `ISSUE_DATE`
**Type column:** `TYPE` (values: "M" for Moving, "P" for Parking)

### DAX Measures

```dax
Summons Moving YTD =
CALCULATE(
    SUM('summons_13month_trend'[TICKET_COUNT]),
    'summons_13month_trend'[ISSUE_DATE] >= DATE(YEAR(pReportMonth), 1, 1),
    'summons_13month_trend'[ISSUE_DATE] <= EOMONTH(pReportMonth, 0),
    'summons_13month_trend'[TYPE] = "M"
)
```

```dax
Summons Parking YTD =
CALCULATE(
    SUM('summons_13month_trend'[TICKET_COUNT]),
    'summons_13month_trend'[ISSUE_DATE] >= DATE(YEAR(pReportMonth), 1, 1),
    'summons_13month_trend'[ISSUE_DATE] <= EOMONTH(pReportMonth, 0),
    'summons_13month_trend'[TYPE] = "P"
)
```

```dax
Summons Total YTD =
CALCULATE(
    SUM('summons_13month_trend'[TICKET_COUNT]),
    'summons_13month_trend'[ISSUE_DATE] >= DATE(YEAR(pReportMonth), 1, 1),
    'summons_13month_trend'[ISSUE_DATE] <= EOMONTH(pReportMonth, 0)
)
```

```dax
Summons YTD Subtitle =
VAR StartDate = DATE(YEAR(pReportMonth), 1, 1)
VAR EndDate = EOMONTH(pReportMonth, 0)
RETURN
"Year-to-Date Summons Activity (" & FORMAT(StartDate, "MMMM") & " - " & FORMAT(EndDate, "MMMM yyyy") & ")"
```

### Revenue Measures (Placeholder — requires FeeSchedule table in data model)

These measures require a `FeeSchedule` table joined to `summons_13month_trend` on `STATUTE`:

```dax
// PLACEHOLDER: requires FeeSchedule table
Summons Revenue Moving YTD =
CALCULATE(
    SUMX(
        'summons_13month_trend',
        RELATED('FeeSchedule'[fine_amount]) * 'summons_13month_trend'[TICKET_COUNT]
    ),
    'summons_13month_trend'[ISSUE_DATE] >= DATE(YEAR(pReportMonth), 1, 1),
    'summons_13month_trend'[ISSUE_DATE] <= EOMONTH(pReportMonth, 0),
    'summons_13month_trend'[TYPE] = "M"
)
```

### Visual Instructions — New Page Setup
1. **Create new page:** Right-click page tabs > New Page > rename to `Summons_YTD`
2. **Canvas:** Set background to match existing pages
3. **KPI Cards (top row):** Add 2 Card visuals
   - `[Summons Moving YTD]` — title "Total Moving Summons YTD"
   - `[Summons Parking YTD]` — title "Total Parking Summons YTD"
4. **Matrix: All Bureaus YTD**
   - Rows: `summons_all_bureaus[WG2]`
   - Columns: `summons_all_bureaus[TYPE]`
   - Values: SUM of TICKET_COUNT (filtered to YTD date range)
5. **Matrix: Top 5 Parking YTD**
   - Rows: `summons_top5_parking[Officer]`
   - Values: SUM of count column
6. **Matrix: Top 5 Moving YTD**
   - Rows: `summons_top5_moving[Officer]`
   - Values: SUM of count column

---

## Page 15: Arrest_13_Month (was Arrest_13)

**Source table:** `___Arrest_13Month`
**Date column:** `Arrest Date`

### DAX Measures

```dax
Arrests YTD =
VAR ReportMonthStart = MAX ( '___DimMonth'[MonthStart] )
VAR YtdStart = DATE ( YEAR ( ReportMonthStart ), 1, 1 )
VAR YtdEnd = EOMONTH ( ReportMonthStart, 0 )
RETURN
    CALCULATE (
        COUNTROWS ( '___Arrest_13Month' ),
        '___Arrest_13Month'[Arrest Date] >= YtdStart,
        '___Arrest_13Month'[Arrest Date] <= YtdEnd
    )
```

**Title / subtitle (examples, DAX-safe):**

```dax
Title Top 5 Arrests YTD =
VAR ReportMonthStart = MAX ( '___DimMonth'[MonthStart] )
VAR YtdStart = DATE ( YEAR ( ReportMonthStart ), 1, 1 )
VAR YtdEnd = EOMONTH ( ReportMonthStart, 0 )
RETURN
    "Top 5 Arresting Officers (YTD "
        & FORMAT ( YtdStart, "MMM yyyy" )
        & " - "
        & FORMAT ( YtdEnd, "MMM yyyy" )
        & ")"
```

```dax
Subtitle Top 5 Arrests YTD =
VAR ReportMonthStart = MAX ( '___DimMonth'[MonthStart] )
VAR YtdStart = DATE ( YEAR ( ReportMonthStart ), 1, 1 )
VAR YtdEnd = EOMONTH ( ReportMonthStart, 0 )
RETURN
    "YTD "
        & FORMAT ( YtdStart, "MMM yyyy" )
        & " - "
        & FORMAT ( YtdEnd, "MMM yyyy" )
        & " - Top 5 by arrest count"
```

### Visual Instructions
1. Add a **Matrix** table modeled after the existing "Top 5 Arrests" table
2. Rows: `___Arrest_13Month[Officer of Record]`
3. Values: `[Arrests YTD]`
4. Filter: Top N = 5 by `[Arrests YTD]`

**`Home_Category` on `___Arrest_13Month`:** Current M (`m_code/arrests/___Arrest_13Month.m`) sets only **`Local`** and **`Out-of-Town`**. Percent-of-total KPIs should use those two buckets (e.g. `Arrest Local %` and `Arrest Out-of-Town %`). Finer **In-County / Out-of-County / Out-of-State** shares require different source logic (e.g. `___Arrest_Distro` enrichment) or expanding the M step that builds `Home_Category`.

---

## Global Visual Recommendations

### Response_Time Page
- **Chart reorder:** Drag line charts top-to-bottom: Routine > Urgent > Emergency
- **Color audit:** Ensure each response type has distinct, accessible colors:
  - Routine: Navy (#1a2744)
  - Urgent: Gold (#c8a84b)
  - Emergency: Dark Red (#b71c1c)

### Benchmark Page
- **Donut chart recommendation:** Replace with a **clustered bar chart** showing incident types by count. Donut charts are poor for comparing proportions when there are many categories. A bar chart provides clearer analytical value and easier comparison.

### Canvas Background
- **Recommendation:** Use a very light gray (#f5f5f5) or transparent background. Avoid pure white — a subtle gray provides better visual hierarchy and reduces eye strain on projected displays. Maintain navy (#1a2744) header bands.

---

## Verification Checklist

After entering all measures, verify each one returns data:

1. Create a temporary **Table** visual on a blank page
2. Add each YTD measure as a column
3. If any measure returns BLANK:
   - The `Tracked Items` string doesn't match exactly (check capitalization, spaces, special characters)
   - Add `DISTINCT(Table[Tracked Items])` to see actual values
   - Update the filter string in the DAX measure accordingly
4. Delete the temporary table visual when done

---

## Known String Value Corrections (from Export Verification)

The following exact string values were confirmed from Power BI visual exports. If a DAX measure returns blank, compare against these verified values:

| Table | Column | Verified Value (from export CSV) |
|---|---|---|
| `___REMU` | Tracked Items | `Application(s) - Permit(s)` (NOT "Applications / Permits") |
| `ESU_13Month` | TrackedItem | `Arrest(s)` (NOT "Arrests") |
| `___Det_case_dispositions_clearance` | Closed Case Dispositions | `Active / Administratively Closed` (spaces around `/`) |
| `___CSB_Monthly` | CSB_Category | Values in TMDL match `Tracked Items` in export — verify exact casing |
| `___STACP_pt_1_2` | Tracked Items | Export has trailing space in header (`Tracked Items `) — M code should trim |
| `___Traffic` | Tracked Items | Export has `Criminal Warrant Arrest`, `Motor Vehicle Crash - P.R.` — verify all |
| `___Patrol` | Tracked Items | `Arrive Program Referral` confirmed exact |

**First step when implementing:** For each page, create a temp table visual with `DISTINCT(Table[CategoryColumn])` to see all actual values before entering measures.

---

## Total Measure Count: ~95

| Page | Measures |
|------|----------|
| Community_Outreach | 3 |
| Training_And_Qualifications | 6 |
| Records_Evidence | 7 |
| Crime_Suppression | 7 |
| Detective_Dispositions | 5 |
| Detectives_Part_A | 7 |
| Detectives_Part_B | 9 |
| STACP_Part_1 | 14 |
| STACP_Part_2 | 11 |
| Traffic_Crashes | 6 |
| Traffic_Enforcement | 9 |
| ESU_Operations | 8 |
| Patrol_Division | 10 |
| Summons_YTD | 4 (+2 revenue placeholders) |
| Arrest_13_Month | 1 |
| **TOTAL** | **~97** |
