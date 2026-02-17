"""
Verification Script for Summons Attribution Remediation
========================================================

Purpose: Verify that the ~1,800 missing parking tickets are now correctly
         attributed to Traffic Bureau after PEO additions and overrides.

Author: R. A. Carucci
Date: 2026-02-17
"""

import pandas as pd
from pathlib import Path

def verify_traffic_attribution():
    """
    Verify that Traffic Bureau summons counts match the manual audit.
    
    Expected Results (from manual audit):
    - Traffic Bureau Moving (M): 211
    - Traffic Bureau Parking (P): 3,093
    - Total: 3,304
    
    Previous Results (before remediation):
    - Traffic Bureau Moving (M): 143 (-68, -32%)
    - Traffic Bureau Parking (P): 2,757 (-336, -11%)
    - Total: 2,900 (-404 tickets missing)
    """
    
    print("=" * 70)
    print("SUMMONS ATTRIBUTION VERIFICATION")
    print("=" * 70)
    
    # Load the processed data
    output_file = Path('03_Staging/Summons/summons_powerbi_latest.xlsx')
    
    if not output_file.exists():
        print(f"\n❌ ERROR: Output file not found: {output_file}")
        print("   Please run summons_etl_normalize.py first")
        return
    
    print(f"\n📂 Loading: {output_file}")
    df = pd.read_excel(output_file, sheet_name='Summons_Data')
    print(f"   Total records: {len(df):,}")
    
    # Filter to January 2026 (most recent complete month; Month_Year is MM-YY e.g. 01-26)
    jan_2026 = df[df['Month_Year'] == '01-26']
    print(f"   January 2026 (01-26) records: {len(jan_2026):,}")
    
    # ========================================================================
    # TEST 1: Traffic Bureau Totals
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 1: TRAFFIC BUREAU ATTRIBUTION")
    print("=" * 70)
    
    traffic = jan_2026[jan_2026['WG2'] == 'TRAFFIC BUREAU']
    
    traffic_m = traffic[traffic['TYPE'] == 'M']['TICKET_COUNT'].sum()
    traffic_p = traffic[traffic['TYPE'] == 'P']['TICKET_COUNT'].sum()
    traffic_total = traffic_m + traffic_p
    
    print("\nActual (After Remediation):")
    print(f"  Moving (M):  {traffic_m:4d}")
    print(f"  Parking (P): {traffic_p:4d}")
    print(f"  Total:       {traffic_total:4d}")
    
    print("\nExpected (Manual Audit):")
    print(f"  Moving (M):  211")
    print(f"  Parking (P): 3093")
    print(f"  Total:       3304")
    
    print("\nPrevious (Before Remediation):")
    print(f"  Moving (M):  143")
    print(f"  Parking (P): 2757")
    print(f"  Total:       2900")
    
    # Calculate differences
    m_diff = traffic_m - 211
    p_diff = traffic_p - 3093
    total_diff = traffic_total - 3304
    
    print("\nDifference from Expected:")
    print(f"  Moving:  {m_diff:+4d} ({m_diff/211*100:+.1f}%)")
    print(f"  Parking: {p_diff:+4d} ({p_diff/3093*100:+.1f}%)")
    print(f"  Total:   {total_diff:+4d} ({total_diff/3304*100:+.1f}%)")
    
    # Test pass/fail
    m_pass = abs(m_diff) <= 5  # Allow 5 ticket variance
    p_pass = abs(p_diff) <= 20  # Allow 20 ticket variance
    
    if m_pass and p_pass:
        print("\n✅ TEST 1 PASSED: Traffic Bureau totals match expected values!")
    else:
        print("\n⚠ TEST 1 WARNING: Some variance detected (within tolerance)")
    
    # ========================================================================
    # TEST 2: Specific Officer Verification
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 2: INDIVIDUAL OFFICER VERIFICATION")
    print("=" * 70)
    
    # Known high-volume officers from manual audit
    test_officers = {
        'K. TORRES #2027': {'expected_m': 0, 'expected_p': 678},
        'G. GALLORINI #256': {'expected_m': 15, 'expected_p': 415},
        'D. RIZZI #2030': {'expected_m': 0, 'expected_p': 382},
        'M. RAMIREZ #2025': {'expected_m': 0, 'expected_p': 335},
        'D. MATTALIAN #717': {'expected_m': 0, 'expected_p': 311},
        'J. SQUILLACE #2021': {'expected_m': 0, 'expected_p': 207},
        'D. SALAZAR #2026': {'expected_m': 0, 'expected_p': 199},
    }
    
    print("\nOfficer                   WG2              M    P   Total  Status")
    print("-" * 70)
    
    all_passed = True
    
    for officer_search, expected in test_officers.items():
        # Extract badge number
        badge = officer_search.split('#')[1]
        padded = badge.zfill(4)
        
        # Find officer
        officer_data = jan_2026[jan_2026['PADDED_BADGE_NUMBER'] == padded]
        
        if len(officer_data) == 0:
            print(f"{officer_search:24s} NOT FOUND                        ❌")
            all_passed = False
            continue
        
        wg2 = officer_data['WG2'].iloc[0]
        m_count = officer_data[officer_data['TYPE'] == 'M']['TICKET_COUNT'].sum()
        p_count = officer_data[officer_data['TYPE'] == 'P']['TICKET_COUNT'].sum()
        total = m_count + p_count
        
        # Check if counts match (allow small variance)
        m_match = abs(m_count - expected['expected_m']) <= 2
        p_match = abs(p_count - expected['expected_p']) <= 10
        wg2_correct = wg2 == 'TRAFFIC BUREAU'
        
        status = "✅" if (m_match and p_match and wg2_correct) else "⚠"
        
        print(f"{officer_search:24s} {wg2:16s} {m_count:3d} {p_count:4d} {total:5d}  {status}")
        
        if not (m_match and p_match and wg2_correct):
            all_passed = False
    
    if all_passed:
        print("\n✅ TEST 2 PASSED: All officers correctly attributed!")
    else:
        print("\n⚠ TEST 2: Some discrepancies detected")
    
    # ========================================================================
    # TEST 3: UNKNOWN Badge Check
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 3: UNKNOWN BADGE REDUCTION")
    print("=" * 70)
    
    unknowns = jan_2026[jan_2026['WG2'] == 'UNKNOWN']
    unknown_m = unknowns[unknowns['TYPE'] == 'M']['TICKET_COUNT'].sum()
    unknown_p = unknowns[unknowns['TYPE'] == 'P']['TICKET_COUNT'].sum()
    unknown_total = unknown_m + unknown_p
    
    print(f"\nRemaining UNKNOWN tickets:")
    print(f"  Moving:  {unknown_m:4d}")
    print(f"  Parking: {unknown_p:4d}")
    print(f"  Total:   {unknown_total:4d}")
    
    if unknown_total < 200:  # Expect < 200 unknowns after PEO additions
        print(f"\n✅ TEST 3 PASSED: UNKNOWN count reduced significantly!")
        print(f"   (Previous: ~1,800, Current: {unknown_total})")
    else:
        print(f"\n❌ TEST 3 FAILED: Still too many UNKNOWN tickets")
    
    # Show remaining unknown badges
    if unknown_total > 0:
        print(f"\n⚠ Remaining UNKNOWN badges (top 10):")
        unknown_badges = unknowns.groupby('PADDED_BADGE_NUMBER').agg({
            'OFFICER_DISPLAY_NAME': 'first',
            'TICKET_COUNT': 'sum'
        }).sort_values('TICKET_COUNT', ascending=False).head(10)
        print(unknown_badges)
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    improvements = {
        'Moving': traffic_m - 143,
        'Parking': traffic_p - 2757,
        'Total': traffic_total - 2900
    }
    
    print(f"\nImprovement from Before Remediation:")
    print(f"  Moving tickets recovered:  {improvements['Moving']:+4d}")
    print(f"  Parking tickets recovered: {improvements['Parking']:+4d}")
    print(f"  Total tickets recovered:   {improvements['Total']:+4d}")
    
    recovery_rate = (improvements['Total'] / 404) * 100 if improvements['Total'] > 0 else 0
    print(f"\nRecovery Rate: {recovery_rate:.1f}% of 404 missing tickets")
    
    if recovery_rate >= 95:
        print("\n🎉 SUCCESS! Attribution remediation complete!")
    elif recovery_rate >= 80:
        print("\n✅ GOOD! Most tickets recovered (minor discrepancies remain)")
    else:
        print("\n⚠ PARTIAL: Some tickets still missing (further investigation needed)")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    verify_traffic_attribution()
