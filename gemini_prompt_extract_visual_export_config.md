Great question! The good news is that **most of the logic is automatic** based on the CSV structure. However, there are a few settings per visual that need to be configured. Let me explain:

## What's Automatic vs What Needs Configuration

### ✅ Automatic (No Configuration Needed)
- **Date inference** - Reads CSV structure and figures it out
- **Column detection** - Finds period columns automatically
- **File format** - Handles Long/Wide formats automatically
- **Date parsing** - Now supports MM-YY and YY-MMM formats

### ⚙️ Needs Configuration (Per Visual)
1. **`enforce_13_month_window`** - Does this visual show a rolling 13-month window? (true/false)
2. **`requires_normalization`** - Does data need unpivoting/cleaning? (true/false)
3. **`normalizer_format`** - What format? ("summons", "training_cost", or default)
4. **`is_backfill_required`** - Should we copy to Backfill folder for ETL? (true/false)
5. **`target_folder`** - Which page does it appear on? (page name normalized)

---

## Current Status: 32 Visuals Configured

You already have most visuals configured! Here's what we have:

| Category | Visuals | 13-Month? | Normalized? | Backfill? |
|----------|---------|-----------|-------------|-----------|
| **Arrests** | 3 visuals | ❌ No | ❌ No | ❌ No |
| **Summons** | 4 visuals | ✅ 1 yes, 3 no | ✅ Yes | ✅ Yes |
| **Training** | 2 visuals | ✅ 1 yes, 1 no | ✅ 1 yes | ✅ 1 yes |
| **Response Time** | 2 visuals | ✅ Yes | ❌ No | ❌ No |
| **NIBRS** | 1 visual | ✅ Yes | ❌ No | ❌ No |
| **Benchmark** | 3 visuals | ✅ Yes | ❌ No | ❌ No |
| **Others** | 17 visuals | Various | ❌ No | ❌ No |

---

## When You Need More Info from Power BI

If you're adding **new visuals** or want to **verify existing ones**, here's the Gemini prompt:

---

## 🤖 Gemini Prompt: Extract Visual Export Configuration

```
I need you to analyze Power BI visual exports and provide configuration details for my automated processing pipeline. For each visual in my monthly report, please provide:

## Visual Information Needed

For each visual on each page, provide:

1. **Page Name**: The exact name of the Power BI report page
2. **Visual Name**: The exact title shown in the visual
3. **Export Filename**: What Power BI names the CSV when exported

## Data Structure Analysis

For each visual's exported CSV, analyze:

4. **Data Format**:
   - Is it "Long" format (one row per data point)?
   - Is it "Wide" format (months as columns)?
   - Example: Show first 5 rows

5. **Date Column Information**:
   - Does it have a date column? (Period, Month_Year, Date, etc.)
   - What format? (MM-YY like "12-25", YY-MMM like "25-Dec", etc.)
   - Does it have multiple date columns?
   - Example values

6. **Time Period Shown**:
   - Single month (current month only)?
   - Rolling 13 months (like Jan 2025 - Jan 2026)?
   - Multiple specific months?
   - All historical data?

7. **Data Columns**:
   - What are the column headers?
   - Any "Sum of" prefixes in column names?
   - Any special formatting needed?

## Configuration Decisions

Based on the analysis above, help me determine:

8. **13-Month Window Enforcement**:
   - Should this visual ALWAYS show exactly 13 months? (Yes/No)
   - Example: If it's a "rolling 13-month trend", answer Yes
   - Example: If it's "current month only" or "all history", answer No

9. **Normalization Needed**:
   - Does the export need cleaning? (Yes/No)
   - Remove "Sum of" prefixes? (Yes/No)
   - Unpivot from Wide to Long format? (Yes/No)
   - Special format type? (summons/training_cost/default)

10. **Backfill Required**:
    - Is this data used by ETL scripts? (Yes/No)
    - Should historical copies be saved? (Yes/No)

## Output Format

Please provide a JSON structure for each visual:

```json
{
  "visual_name": "Exact Visual Title",
  "page_name": "Page Name",
  "normalized_folder": "page_name_lowercase_with_underscores",
  "standardized_filename": "descriptive_snake_case_name",
  "data_format": "Long or Wide",
  "date_column": "Period or Month_Year or None",
  "date_format": "MM-YY or YY-MMM",
  "time_period": "Single month / 13-month rolling / All history",
  "enforce_13_month_window": true or false,
  "requires_normalization": true or false,
  "normalizer_format": "summons or training_cost or null",
  "is_backfill_required": true or false,
  "notes": "Any special considerations"
}
```

## Example Visuals to Analyze

Please analyze these visuals from my December 2025 monthly report:
[LIST YOUR VISUALS HERE OR ATTACH CSV EXPORTS]

## Additional Context

- Our pipeline processes exports monthly
- Data should represent the most recent complete month
- Some visuals feed into ETL scripts that need historical data
- We maintain a 13-month rolling window for trending visuals
```

---

## Quick Decision Guide

If you want to configure a visual yourself without Gemini, use this decision tree:

### Question 1: Does it show a rolling 13-month window?
- **YES** → `enforce_13_month_window: true`
  - Examples: "13-Month NIBRS Trend", "Monthly Accrual (last 13 months)", "Response Time Trend"
- **NO** → `enforce_13_month_window: false`
  - Examples: "Top 5 Leaders", "Current Month Arrests", "All-Time Statistics"

### Question 2: Is data in Wide format (months as columns)?
- **YES** → `requires_normalization: true`
  - Example: Columns like "01-25", "02-25", "03-25"...
- **NO** → `requires_normalization: false`
  - Example: One "Month" column with dates in rows

### Question 3: Does it feed ETL scripts or need history?
- **YES** → `is_backfill_required: true`
  - Examples: Summons, Training, Monthly Accrual
- **NO** → `is_backfill_required: false`
  - Examples: Most visuals (just for Power BI display)

### Question 4: What format type?
- **Summons data** → `normalizer_format: "summons"`
- **Training cost data** → `normalizer_format: "training_cost"`
- **Everything else** → `normalizer_format: null` (default)

---

## Your Current Configuration Status

All 32 of your visuals are already configured in `visual_export_mapping.json`! The system will:
- ✅ Automatically detect date format (MM-YY or YY-MMM)
- ✅ Automatically find period columns
- ✅ Use latest date for multi-month data
- ✅ Place files in correct page-based folders
- ✅ Apply 13-month enforcement where configured
- ✅ Normalize and backfill where configured

**You're ready to go!** Just export from Power BI and run the processor.

---

**Do you want me to:**
1. Show you the current configuration for any specific visual?
2. Help you add configuration for new visuals?
3. Review and adjust existing configurations?