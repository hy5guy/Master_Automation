"""
Diagnose Traffic Bureau Attribution Gap
=========================================

Compare actual ETL output vs. expected manual audit to identify missing officers.
"""

import pandas as pd

print("="*70)
print("TRAFFIC BUREAU ATTRIBUTION GAP ANALYSIS")
print("="*70)

# Load processed data
df = pd.read_excel(r'C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx', 
                   sheet_name='Summons_Data')

# Filter to January 2026
jan = df[df['Month_Year'] == '01-26']

print(f"\nTotal January 2026 (01-26) records: {len(jan):,}")

# Expected values from manual audit (Gemini's calculation)
expected_traffic_m = 211
expected_traffic_p = 3093

# Actual values
traffic = jan[jan['WG2'] == 'TRAFFIC BUREAU']
actual_traffic_m = traffic[traffic['TYPE'] == 'M']['TICKET_COUNT'].sum()
actual_traffic_p = traffic[traffic['TYPE'] == 'P']['TICKET_COUNT'].sum()

print(f"\n{'='*70}")
print("TRAFFIC BUREAU COMPARISON")
print(f"{'='*70}")
print(f"\n                Expected    Actual    Gap")
print(f"Moving (M):     {expected_traffic_m:4d}       {actual_traffic_m:4d}    {actual_traffic_m - expected_traffic_m:+4d}")
print(f"Parking (P):    {expected_traffic_p:4d}      {actual_traffic_p:4d}    {actual_traffic_p - expected_traffic_p:+4d}")

# Check Patrol Division (might have Traffic officers)
print(f"\n{'='*70}")
print("PATROL DIVISION (Check for Traffic Officers)")
print(f"{'='*70}")

patrol = jan[jan['WG2'] == 'PATROL DIVISION']
patrol_summary = patrol.groupby('PADDED_BADGE_NUMBER').agg({
    'OFFICER_DISPLAY_NAME': 'first',
    'TYPE': lambda x: f"M:{(x=='M').sum()}, P:{(x=='P').sum()}",
    'TICKET_COUNT': 'sum'
}).sort_values('TICKET_COUNT', ascending=False)

print(f"\nTop Patrol Division Officers:")
print(patrol_summary.head(15))

# Check if any have high parking counts (possible Traffic officers)
high_parking_patrol = patrol[(patrol['TYPE'] == 'P')].groupby('PADDED_BADGE_NUMBER').agg({
    'OFFICER_DISPLAY_NAME': 'first',
    'TICKET_COUNT': 'sum'
}).sort_values('TICKET_COUNT', ascending=False).head(10)

if len(high_parking_patrol) > 0:
    print(f"\n⚠ High-Volume Parking Officers in PATROL (might belong in TRAFFIC):")
    print(high_parking_patrol)

# Compare to manual audit officers
print(f"\n{'='*70}")
print("MANUAL AUDIT OFFICERS - LOCATION CHECK")
print(f"{'='*70}")

traffic_audit_officers = {
    '2027': 'K. TORRES',
    '0256': 'G. GALLORINI',
    '2030': 'D. RIZZI',
    '2025': 'M. RAMIREZ',
    '0717': 'D. MATTALIAN',
    '0329': 'D. FRANCAVILLA',
    '2021': 'J. SQUILLACE',
    '0138': 'M. JACOBSEN',
    '0327': "M. O'NEILL",
    '2022': 'D. CASSIDY'
}

print(f"\nChecking where manual audit officers are mapped:\n")
print(f"{'Badge':<8} {'Name':<20} {'Current WG2':<25} {'M':<5} {'P':<5}")
print(f"{'-'*70}")

for badge, name in traffic_audit_officers.items():
    officer = jan[jan['PADDED_BADGE_NUMBER'] == badge]
    
    if len(officer) == 0:
        print(f"{badge:<8} {name:<20} NOT FOUND IN DATA")
    else:
        wg2 = officer['WG2'].iloc[0]
        m_count = officer[officer['TYPE'] == 'M']['TICKET_COUNT'].sum()
        p_count = officer[officer['TYPE'] == 'P']['TICKET_COUNT'].sum()
        
        status = "✅" if wg2 == "TRAFFIC BUREAU" else "⚠"
        print(f"{badge:<8} {name:<20} {wg2:<25} {m_count:<5} {p_count:<5} {status}")

# Summary of gaps
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")

all_bureaus = jan.groupby('WG2').agg({
    'TICKET_COUNT': 'sum'
}).sort_values('TICKET_COUNT', ascending=False)

print(f"\nAll Bureau Totals:")
print(all_bureaus)

print(f"\n⚠ ACTION ITEMS:")
print(f"  1. Review officers listed above with ⚠ marker")
print(f"  2. Update their WG2 in Assignment_Master_V2.csv to TRAFFIC BUREAU")
print(f"  3. Re-run ETL: python run_summons_etl.py")
