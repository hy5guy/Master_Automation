import pandas as pd

df = pd.read_excel(r'C:\Users\RobertCarucci\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx', sheet_name='Summons_Data')
jan26 = df[df['YearMonthKey'] == 202601]
moving = jan26[jan26['TYPE'] == 'M']

print('Check Officer Id 138 (JACOBSEN from your Excel):')
jac = moving[moving['Officer Id'] == 138]
print(f'Total Moving records: {len(jac)}')
print()

if len(jac) > 0:
    print('Officer Last Name values:')
    print(jac['Officer Last Name'].value_counts())
    print()
    print('OFFICER_DISPLAY_NAME values:')
    print(jac['OFFICER_DISPLAY_NAME'].value_counts())
    print()
    print('PADDED_BADGE_NUMBER values:')
    print(jac['PADDED_BADGE_NUMBER'].value_counts())
else:
    print('No records found for Officer Id 138')
    print()
    print('Check what Officer Ids exist in Moving summons:')
    print(moving['Officer Id'].value_counts().head(20))
