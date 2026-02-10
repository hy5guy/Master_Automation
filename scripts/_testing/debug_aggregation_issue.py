#!/usr/bin/env python3
"""Debug script to investigate why only 58 calls appear in final output"""

import pandas as pd
import sys
import os
sys.path.insert(0, 'scripts')

# Import functions from the main script
from process_cad_data_for_powerbi_FINAL import (
    load_cad_call_type_mapping,
    load_and_combine_excel_files,
    standardize_columns,
    remove_duplicates,
    create_dates_and_times,
    calculate_response_times,
    apply_incident_to_response_type_mapping,
    clean_response_types,
    apply_filters,
    create_year_month
)

print("=" * 70)
print("DEBUGGING AGGREGATION ISSUE")
print("=" * 70)

# Run through the pipeline
call_type_mapping = load_cad_call_type_mapping()
df = load_and_combine_excel_files()
df = standardize_columns(df)
df = remove_duplicates(df)
df = create_dates_and_times(df)
df = calculate_response_times(df)
df = apply_incident_to_response_type_mapping(df, call_type_mapping)
df = clean_response_types(df)
df = apply_filters(df)
df = create_year_month(df)

print("\n" + "=" * 70)
print("BEFORE AGGREGATION - DATA QUALITY CHECK")
print("=" * 70)

print(f"\nTotal records: {len(df):,}")
print(f"Records with YearMonth: {df['YearMonth'].notna().sum():,}")
print(f"Records with Response Type: {df['Response Type'].notna().sum():,}")
print(f"Records with Response_Time_Minutes: {df['Response_Time_Minutes'].notna().sum():,}")
print(f"Records with ReportNumberNew: {df['ReportNumberNew'].notna().sum():,}")

print(f"\nYearMonth distribution:")
print(df['YearMonth'].value_counts())

print(f"\nResponse Type distribution:")
print(df['Response Type'].value_counts())

print(f"\nChecking for records with missing YearMonth or Response Type:")
missing_yearmonth = df['YearMonth'].isna().sum()
missing_response_type = df['Response Type'].isna().sum()
print(f"  Missing YearMonth: {missing_yearmonth:,}")
print(f"  Missing Response Type: {missing_response_type:,}")

# Check the grouping that will happen
print(f"\nGrouping check:")
group_sizes = df.groupby(['YearMonth', 'Response Type']).size()
print(f"Unique YearMonth+Response Type combinations: {len(group_sizes)}")
print("\nGroup sizes:")
print(group_sizes)

# Check if ReportNumberNew is present for all records
print(f"\nReportNumberNew check:")
missing_reportnum = df['ReportNumberNew'].isna().sum()
print(f"  Missing ReportNumberNew: {missing_reportnum:,}")
if missing_reportnum > 0:
    print("  WARNING: Some records missing ReportNumberNew will not be counted!")

# Simulate the aggregation
print(f"\n" + "=" * 70)
print("SIMULATING AGGREGATION")
print("=" * 70)

df_valid = df[df['Response_Time_Minutes'].notna()].copy()
print(f"\nRecords with valid response times for aggregation: {len(df_valid):,}")

# Check if all records have YearMonth and Response Type
has_both = df_valid['YearMonth'].notna() & df_valid['Response Type'].notna()
print(f"Records with both YearMonth AND Response Type: {has_both.sum():,}")

# Filter to only records that can be grouped
df_groupable = df_valid[df_valid['YearMonth'].notna() & df_valid['Response Type'].notna()].copy()
print(f"Records that can be grouped (have YearMonth and Response Type): {len(df_groupable):,}")

# Now simulate the actual aggregation
if len(df_groupable) > 0:
    grouped = df_groupable.groupby(['YearMonth', 'Response Type']).agg({
        'ReportNumberNew': 'count',
        'Response_Time_Minutes': ['mean', 'min', 'max']
    }).reset_index()
    
    grouped.columns = ['YearMonth', 'Response_Type', 'Count', 'Avg_Response_Time', 'Min_Response_Time', 'Max_Response_Time']
    
    print(f"\nAggregated results:")
    print(grouped.to_string(index=False))
    
    total_count = grouped['Count'].sum()
    print(f"\nTotal Count sum: {total_count:,}")
    print(f"Expected (from groupable records): {len(df_groupable):,}")
    print(f"Difference: {len(df_groupable) - total_count:,}")
    
    if total_count != len(df_groupable):
        print("\n⚠️  ISSUE FOUND: Count doesn't match number of records!")
        print("This suggests ReportNumberNew might have duplicates or nulls within groups")
        
        # Check for duplicate ReportNumberNew within groups
        print("\nChecking for duplicate ReportNumberNew within groups...")
        for name, group in df_groupable.groupby(['YearMonth', 'Response Type']):
            duplicates = group['ReportNumberNew'].duplicated().sum()
            nulls = group['ReportNumberNew'].isna().sum()
            if duplicates > 0 or nulls > 0:
                print(f"  Group {name}: {duplicates} duplicates, {nulls} nulls, total: {len(group)}")

