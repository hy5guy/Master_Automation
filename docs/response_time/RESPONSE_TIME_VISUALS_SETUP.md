# Response Time Calculator Line Chart and OutVsCall Visual

This doc explains how to fix the **response time calculator line chart** (Missing_References) and add the **___ResponseTime_OutVsCall** visual on the Response Time page.

## Why the line chart shows Missing_References

The error occurs when DAX measures reference tables or columns that no longer exist. The template previously used measures that referenced:

- `ResponseTimes` (raw table with columns like Time Out, Time of Call, Time Dispatched)
- `CAD_Raw`

The current data model uses **aggregated** tables from the golden-standard ETL:

| Query (table name in model) | Metric |
|----------------------------|--------|
| `___ResponseTimeCalculator` | Time Out − Time Dispatched |
| `___ResponseTime_OutVsCall` | Time Out − Time of Call |
| `___ResponseTime_DispVsCall` | Time Dispatched − Time of Call |

If the line chart (or any visual) uses a measure that still references `ResponseTimes` or `CAD_Raw`, Power BI returns **Missing_References**.

## Fix 1 — Response Time Calculator line chart

1. **Update the ___ResponseTimeCalculator query**  
   In Power BI: **Transform data → Power Query Editor**. Right-click **___ResponseTimeCalculator** → **Advanced Editor**. Replace all with the contents of:
   `m_code\response_time\___ResponseTimeCalculator.m`  
   Ensure the **pReportMonth** parameter exists and is set (e.g. `#date(2026, 2, 1)`).

2. **Fix or remove broken DAX measures**  
   - In **Model** or **Report** view, open the **Response Time** table (or wherever the old measures live).  
   - Delete or stop using any measure that references `ResponseTimes` or `CAD_Raw`.  
   - Add the measures from **response_time_measures.dax** (in the repo root) to a table that is used on the Response Time page (e.g. ___ResponseTimeCalculator or a dedicated “Measures” table).  
   - For the **line chart**, either:
     - Use the **column** `Average_Response_Time` from `___ResponseTimeCalculator` on the Y-axis, with **Date** or **MonthName** on X-axis and **Category** on Legend, **or**
     - Use the measure **Avg Response Time (Travel)** from response_time_measures.dax.

3. **Bind the line chart to ___ResponseTimeCalculator**  
   - **Data source**: Table = `___ResponseTimeCalculator`.  
   - **X-axis**: `Date` or `MonthName` or `Date_Sort_Key`.  
   - **Legend**: `Category` (or `Response_Type`).  
   - **Y-axis**: `Average_Response_Time` or measure **Avg Response Time (Travel)**.  
   - Remove any field that comes from `ResponseTimes` or `CAD_Raw`.

4. **Close & Apply**, then refresh. The line chart should load without Missing_References.

## Fix 2 — Add the ___ResponseTime_OutVsCall visual

This visual shows **Time Out − Time of Call** (full response: call receipt → officer on scene).

1. **Add the query if missing**  
   In Power Query Editor: **New Source → Blank Query**. Rename to **___ResponseTime_OutVsCall**. Open **Advanced Editor** and paste the contents of:
   `m_code\response_time\___ResponseTime_OutVsCall.m`  
   Ensure **pReportMonth** is defined in the template (same as other response time queries).

2. **Load the query**  
   Ensure **Close & Apply** is run so `___ResponseTime_OutVsCall` appears in the model.

3. **Create the line chart**  
   - Insert a **Line chart** on the Response Time page.  
   - **Data**: Table = `___ResponseTime_OutVsCall`.  
   - **X-axis**: `Date` or `MonthName`.  
   - **Legend**: `Category`.  
   - **Y-axis**: `Average_Response_Time` or measure **Avg Response Time (Total)** from response_time_measures.dax.

4. **Title** the visual e.g. “Average Response Time (Time Out − Time of Call)” so it’s clear it’s total response time.

## Optional — Time Dispatched − Time of Call visual

Repeat the same steps using:

- Query: **___ResponseTime_DispVsCall** (paste from `m_code\response_time\___ResponseTime_DispVsCall.m`).  
- Y-axis: `Average_Response_Time` or measure **Avg Response Time (Dispatch Queue)**.  
- Title e.g. “Average Response Time (Time Dispatched − Time of Call)”.

## Summary

- **Line chart fix**: Use table `___ResponseTimeCalculator`, columns `Date`/`MonthName`, `Category`, `Average_Response_Time` (or measure **Avg Response Time (Travel)**), and remove DAX that references `ResponseTimes` or `CAD_Raw`; add measures from **response_time_measures.dax**.
- **OutVsCall visual**: Add query **___ResponseTime_OutVsCall**, then a line chart with table `___ResponseTime_OutVsCall`, same axis/legend pattern, and **Avg Response Time (Total)** or `Average_Response_Time`.

All three M queries use the same schema (including **Count** and **MonthName**) so the same visual layout works for Calculator, OutVsCall, and DispVsCall.

---

## Title and subtitle for “Average Response Times” (Dispatch to On Scene)

The **___ResponseTimeCalculator** visual shows **Time Out − Time Dispatched** (time from dispatch to officer on scene). Use these so the label matches the metric:

| Use | Text |
|-----|------|
| **Title** | `Average Response Time (Dispatch to On Scene)` |
| **Subtitle** | `Values in mm:ss. Time from dispatch to officer on scene. Rolling 13 months.` |

In Power BI you can either type these into the visual’s **Title** and **Subtitle** settings, or use the DAX measures **RT Average Title** and **RT Average Subtitle** from `docs/response_time/2026_02_26_old_dax____ResponseTimeCalculator.dax` (paste those measures into the report and bind them to the visual’s title/subtitle if your report supports dynamic title/subtitle from measures).
