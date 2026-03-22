import pandas as pd

# Read the current Summons staging file
df = pd.read_excel(
    r"C:\Users\carucci_r\OneDrive - City of Hackensack\03_Staging\Summons\summons_powerbi_latest.xlsx",
    sheet_name="Summons_Data"
)

print(f"Total rows: {len(df)}")
print(f"\nColumns ({len(df.columns)}):")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. {col}")

if "TYPE" in df.columns:
    print(f"\nTYPE counts:")
    print(df["TYPE"].value_counts())
else:
    print("\n⚠️ No TYPE column found!")

if "Month_Year" in df.columns:
    print(f"\nMonth_Year samples:")
    print(df["Month_Year"].value_counts().head(10))

if "YearMonthKey" in df.columns:
    print(f"\nYearMonthKey samples:")
    print(df["YearMonthKey"].value_counts().head(10))
else:
    print("\n⚠️ No YearMonthKey column found!")

# Check for Case Type Code and Statute columns
if "Case Type Code" in df.columns:
    print(f"\nCase Type Code distribution:")
    print(df["Case Type Code"].value_counts())

if "Statute" in df.columns:
    print(f"\nStatute samples (Title 39):")
    title39 = df[df["Statute"].astype(str).str.startswith("39:", na=False)]
    print(f"  Total Title 39 violations: {len(title39)}")
    if "TYPE" in df.columns:
        print(f"  Title 39 classified as M: {(title39['TYPE'] == 'M').sum()}")
        print(f"  Title 39 classified as P: {(title39['TYPE'] == 'P').sum()}")
