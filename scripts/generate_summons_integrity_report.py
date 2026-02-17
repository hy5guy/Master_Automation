"""
Monthly Summons Data Integrity Report Generator
===============================================

Purpose: Generate monthly data quality metrics for summons attribution
Author: R. A. Carucci
Date: 2026-02-17

This script creates a comprehensive data integrity report tracking:
- Match rates to Assignment Master
- UNKNOWN badge trends
- Bureau attribution accuracy
- High-volume officer verification
- Data quality scores over time

Usage:
    python scripts/generate_summons_integrity_report.py --month "01-26"
    
Output:
    reports/summons_integrity_YYYYMM.md
    reports/summons_integrity_YYYYMM.xlsx
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import argparse


def generate_integrity_report(summons_file, output_dir='reports', report_month=None):
    """
    Generate comprehensive data integrity report for summons data.
    
    Parameters:
    -----------
    summons_file : str or Path
        Path to summons_powerbi_latest.xlsx
    output_dir : str
        Directory to save reports (default: 'reports')
    report_month : str
        Month to analyze (e.g., "01-26" MM-YY). If None, uses most recent.
    
    Returns:
    --------
    dict
        Summary statistics and metrics
    """
    
    print("=" * 70)
    print("MONTHLY SUMMONS DATA INTEGRITY REPORT")
    print("=" * 70)
    
    # Load data
    print("\n[1/7] Loading summons data...")
    df = pd.read_excel(summons_file, sheet_name='Summons_Data')
    print(f"  ✓ Total records: {len(df):,}")
    
    # Determine report month
    if report_month is None:
        report_month = df[df['ETL_VERSION'] == 'ETICKET_CURRENT']['Month_Year'].max()
    
    print(f"  ✓ Report Month: {report_month}")
    
    # Filter to report month
    monthly_data = df[df['Month_Year'] == report_month]
    print(f"  ✓ Monthly records: {len(monthly_data):,}")
    
    # ========================================================================
    # SECTION 1: MATCH RATE ANALYSIS
    # ========================================================================
    print("\n[2/7] Analyzing match rates...")
    
    total_records = len(monthly_data)
    matched = monthly_data['ASSIGNMENT_FOUND'].fillna(False).sum()
    unknown = (monthly_data['WG2'] == 'UNKNOWN').sum()
    match_rate = (matched / total_records * 100) if total_records > 0 else 0
    unknown_rate = (unknown / total_records * 100) if total_records > 0 else 0
    
    match_metrics = {
        'total_records': total_records,
        'matched': matched,
        'unknown': unknown,
        'match_rate': match_rate,
        'unknown_rate': unknown_rate
    }
    
    print(f"  ✓ Match Rate: {match_rate:.1f}%")
    print(f"  ✓ Unknown Rate: {unknown_rate:.1f}%")
    
    # ========================================================================
    # SECTION 2: BUREAU DISTRIBUTION
    # ========================================================================
    print("\n[3/7] Analyzing bureau distribution...")
    
    bureau_summary = monthly_data.groupby(['WG2', 'TYPE']).agg({
        'TICKET_COUNT': 'sum',
        'PADDED_BADGE_NUMBER': 'nunique'
    }).rename(columns={'PADDED_BADGE_NUMBER': 'Officer_Count'})
    
    # Calculate bureau percentages
    bureau_totals = bureau_summary.groupby(level=0)['TICKET_COUNT'].sum()
    total_tickets = bureau_totals.sum()
    bureau_pct = (bureau_totals / total_tickets * 100).round(1)
    
    print(f"  ✓ Active Bureaus: {len(bureau_totals)}")
    print(f"  ✓ Total Tickets: {total_tickets:,}")
    
    # ========================================================================
    # SECTION 3: UNKNOWN BADGE ANALYSIS
    # ========================================================================
    print("\n[4/7] Analyzing UNKNOWN badges...")
    
    unknown_data = monthly_data[monthly_data['WG2'] == 'UNKNOWN']
    
    if len(unknown_data) > 0:
        unknown_badges = unknown_data.groupby('PADDED_BADGE_NUMBER').agg({
            'OFFICER_DISPLAY_NAME': 'first',
            'TICKET_COUNT': 'sum',
            'TYPE': lambda x: f"M:{(x=='M').sum()}, P:{(x=='P').sum()}"
        }).sort_values('TICKET_COUNT', ascending=False)
        
        # Check for PEO badges in UNKNOWN (should be rare after remediation)
        peo_unknown = unknown_badges[
            unknown_badges.index.str.match(r'^20[0-9]{2}$', na=False)
        ]
        
        print(f"  ✓ Unknown Badges: {len(unknown_badges)}")
        print(f"  ✓ PEO Badges in Unknown: {len(peo_unknown)} ⚠" if len(peo_unknown) > 0 else "  ✓ No PEO badges in Unknown ✅")
    else:
        unknown_badges = pd.DataFrame()
        peo_unknown = pd.DataFrame()
        print(f"  ✓ No UNKNOWN badges! Perfect attribution ✅")
    
    # ========================================================================
    # SECTION 4: HIGH-VOLUME OFFICER VERIFICATION
    # ========================================================================
    print("\n[5/7] Verifying high-volume officers...")
    
    # Top 10 officers by ticket count
    top_officers = monthly_data.groupby(['PADDED_BADGE_NUMBER', 'WG2']).agg({
        'OFFICER_DISPLAY_NAME': 'first',
        'TICKET_COUNT': 'sum'
    }).sort_values('TICKET_COUNT', ascending=False).head(10)
    
    # Check if any top officers are UNKNOWN
    top_unknown = top_officers[top_officers['WG2'] == 'UNKNOWN']
    
    print(f"  ✓ Top 10 Officers identified")
    if len(top_unknown) > 0:
        print(f"  ⚠ WARNING: {len(top_unknown)} high-volume officers in UNKNOWN!")
    else:
        print(f"  ✓ All top officers correctly attributed ✅")
    
    # ========================================================================
    # SECTION 5: OVERRIDE LOG ANALYSIS
    # ========================================================================
    print("\n[6/7] Checking override log...")
    
    override_log_path = Path('logs/summons_badge_overrides.txt')
    override_used = False
    
    if override_log_path.exists():
        # Check if log was updated today
        log_mtime = datetime.fromtimestamp(override_log_path.stat().st_mtime)
        today = datetime.now().date()
        
        if log_mtime.date() == today:
            override_used = True
            print(f"  ⚠ Overrides were used today - Review log: {override_log_path}")
        else:
            print(f"  ✓ No recent overrides (last: {log_mtime.strftime('%Y-%m-%d')})")
    else:
        print(f"  ✓ No override log found (clean run)")
    
    # ========================================================================
    # SECTION 6: TRAFFIC BUREAU SPECIFIC CHECK
    # ========================================================================
    print("\n[7/7] Validating Traffic Bureau attribution...")
    
    traffic = monthly_data[monthly_data['WG2'] == 'TRAFFIC BUREAU']
    traffic_m = traffic[traffic['TYPE'] == 'M']['TICKET_COUNT'].sum()
    traffic_p = traffic[traffic['TYPE'] == 'P']['TICKET_COUNT'].sum()
    traffic_total = traffic_m + traffic_p
    
    # Check if Traffic Bureau has reasonable ticket counts
    traffic_healthy = traffic_total > 2000  # Expect >2000 tickets/month for Traffic
    
    print(f"  ✓ Traffic Bureau: M:{traffic_m}, P:{traffic_p}, Total:{traffic_total}")
    
    if traffic_healthy:
        print(f"  ✓ Traffic Bureau attribution looks healthy ✅")
    else:
        print(f"  ⚠ WARNING: Traffic Bureau count seems low!")
    
    # ========================================================================
    # GENERATE REPORT FILES
    # ========================================================================
    print("\n" + "=" * 70)
    print("GENERATING REPORT FILES")
    print("=" * 70)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate report timestamp
    report_date = datetime.now()
    year_month = report_date.strftime('%Y%m')
    
    # ========================================================================
    # MARKDOWN REPORT
    # ========================================================================
    md_file = output_path / f'summons_integrity_{year_month}.md'
    
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# Summons Data Integrity Report\n\n")
        f.write(f"**Report Month:** {report_month}  \n")
        f.write(f"**Generated:** {report_date.strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**Source:** {summons_file}  \n\n")
        
        f.write("---\n\n")
        f.write("## Executive Summary\n\n")
        f.write(f"| Metric | Value | Status |\n")
        f.write(f"|--------|-------|--------|\n")
        f.write(f"| Total Records | {total_records:,} | ✅ |\n")
        f.write(f"| Match Rate | {match_rate:.1f}% | {'✅' if match_rate >= 95 else '⚠'} |\n")
        f.write(f"| Unknown Rate | {unknown_rate:.1f}% | {'✅' if unknown_rate <= 5 else '⚠'} |\n")
        f.write(f"| Unknown Badges | {len(unknown_badges)} | {'✅' if len(unknown_badges) <= 20 else '⚠'} |\n")
        f.write(f"| PEO in Unknown | {len(peo_unknown)} | {'✅' if len(peo_unknown) == 0 else '⚠'} |\n")
        f.write(f"| Overrides Used | {'Yes' if override_used else 'No'} | {'⚠' if override_used else '✅'} |\n\n")
        
        f.write("---\n\n")
        f.write("## Bureau Distribution\n\n")
        f.write(f"| Bureau/Division | Moving (M) | Parking (P) | Total | % of Total |\n")
        f.write(f"|-----------------|------------|-------------|-------|------------|\n")
        
        for bureau in bureau_totals.index:
            bureau_data = bureau_summary.loc[bureau]
            m_count = bureau_data.loc['M', 'TICKET_COUNT'] if 'M' in bureau_data.index else 0
            p_count = bureau_data.loc['P', 'TICKET_COUNT'] if 'P' in bureau_data.index else 0
            total = bureau_totals[bureau]
            pct = bureau_pct[bureau]
            f.write(f"| {bureau} | {m_count:,} | {p_count:,} | {total:,} | {pct}% |\n")
        
        f.write("\n---\n\n")
        f.write("## Unknown Badge Details\n\n")
        
        if len(unknown_badges) > 0:
            f.write(f"**Total Unknown Badges:** {len(unknown_badges)}\n\n")
            f.write(f"| Badge | Officer Name | Tickets | Type Breakdown |\n")
            f.write(f"|-------|--------------|---------|----------------|\n")
            
            for badge, row in unknown_badges.head(20).iterrows():
                f.write(f"| {badge} | {row['OFFICER_DISPLAY_NAME']} | {row['TICKET_COUNT']} | {row['TYPE']} |\n")
            
            if len(unknown_badges) > 20:
                f.write(f"\n*({len(unknown_badges) - 20} additional badges not shown)*\n")
            
            if len(peo_unknown) > 0:
                f.write(f"\n### ⚠ PEO Badges in Unknown\n\n")
                f.write(f"**Action Required:** These PEO badges should be added to Assignment_Master_V2.csv\n\n")
                for badge, row in peo_unknown.iterrows():
                    f.write(f"- Badge {badge}: {row['TICKET_COUNT']} tickets\n")
        else:
            f.write(f"✅ **No unknown badges detected!** Perfect attribution.\n")
        
        f.write("\n---\n\n")
        f.write("## Top 10 High-Volume Officers\n\n")
        f.write(f"| Rank | Badge | Officer | Bureau | Tickets |\n")
        f.write(f"|------|-------|---------|--------|----------|\n")
        
        for idx, (badge, row) in enumerate(top_officers.iterrows(), 1):
            wg2 = row['WG2'][1] if isinstance(row['WG2'], tuple) else row['WG2']
            f.write(f"| {idx} | {badge[0]} | {row['OFFICER_DISPLAY_NAME']} | {wg2} | {row['TICKET_COUNT']} |\n")
        
        f.write("\n---\n\n")
        f.write("## Recommendations\n\n")
        
        if match_rate < 95:
            f.write(f"- ⚠ **Match rate below 95%** - Review Assignment_Master_V2.csv for missing officers\n")
        
        if len(peo_unknown) > 0:
            f.write(f"- ⚠ **PEO badges in UNKNOWN** - Add these to Assignment Master immediately\n")
        
        if override_used:
            f.write(f"- ⚠ **Overrides were used** - Review `logs/summons_badge_overrides.txt` and update Assignment Master\n")
        
        if len(top_unknown) > 0:
            f.write(f"- ⚠ **High-volume officers in UNKNOWN** - These officers need immediate attribution\n")
        
        if not traffic_healthy:
            f.write(f"- ⚠ **Traffic Bureau count low** - Investigate potential attribution issues\n")
        
        if match_rate >= 95 and len(peo_unknown) == 0 and not override_used and traffic_healthy:
            f.write(f"✅ **All data quality checks passed!** No action required.\n")
        
        f.write(f"\n---\n\n")
        f.write(f"*Report generated by summons_etl_normalize.py*  \n")
        f.write(f"*Next review: {(report_date.replace(day=1) + pd.DateOffset(months=1)).strftime('%Y-%m-%d')}*\n")
    
    print(f"\n✓ Markdown report: {md_file}")
    
    # ========================================================================
    # EXCEL REPORT
    # ========================================================================
    excel_file = output_path / f'summons_integrity_{year_month}.xlsx'
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Summary sheet
        summary_data = {
            'Metric': ['Report Month', 'Total Records', 'Match Rate', 'Unknown Rate', 
                      'Unknown Badges', 'PEO in Unknown', 'Overrides Used'],
            'Value': [report_month, total_records, f"{match_rate:.1f}%", f"{unknown_rate:.1f}%",
                     len(unknown_badges), len(peo_unknown), 'Yes' if override_used else 'No'],
            'Status': ['', '✅', '✅' if match_rate >= 95 else '⚠', 
                      '✅' if unknown_rate <= 5 else '⚠',
                      '✅' if len(unknown_badges) <= 20 else '⚠',
                      '✅' if len(peo_unknown) == 0 else '⚠',
                      '⚠' if override_used else '✅']
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        # Bureau distribution
        bureau_summary.to_excel(writer, sheet_name='Bureau_Distribution')
        
        # Unknown badges
        if len(unknown_badges) > 0:
            unknown_badges.to_excel(writer, sheet_name='Unknown_Badges')
        
        # Top officers
        top_officers.to_excel(writer, sheet_name='Top_Officers')
    
    print(f"✓ Excel report: {excel_file}")
    
    # ========================================================================
    # RETURN SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("REPORT GENERATION COMPLETE")
    print("=" * 70)
    
    return {
        'report_month': report_month,
        'match_rate': match_rate,
        'unknown_rate': unknown_rate,
        'unknown_count': len(unknown_badges),
        'peo_unknown_count': len(peo_unknown),
        'override_used': override_used,
        'traffic_total': traffic_total,
        'md_file': str(md_file),
        'excel_file': str(excel_file)
    }


def main():
    """Command-line interface for report generation."""
    parser = argparse.ArgumentParser(
        description='Generate monthly summons data integrity report'
    )
    parser.add_argument(
        '--summons-file',
        default='03_Staging/Summons/summons_powerbi_latest.xlsx',
        help='Path to summons data file'
    )
    parser.add_argument(
        '--output-dir',
        default='reports',
        help='Output directory for reports'
    )
    parser.add_argument(
        '--month',
        help='Month to analyze (e.g., "01-26"). Defaults to most recent.'
    )
    
    args = parser.parse_args()
    
    # Generate report
    summary = generate_integrity_report(
        summons_file=args.summons_file,
        output_dir=args.output_dir,
        report_month=args.month
    )
    
    print(f"\n📊 Summary:")
    print(f"  Match Rate: {summary['match_rate']:.1f}%")
    print(f"  Unknown Badges: {summary['unknown_count']}")
    print(f"  Reports saved to: {args.output_dir}/")


if __name__ == '__main__':
    main()
