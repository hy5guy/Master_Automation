#!/usr/bin/env python3
"""Quick script to find the badge number in e-ticket that's not in Assignment Master."""

import pandas as pd
from pathlib import Path

# Paths
ETICKET_EXPORT = Path(
    r"C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Summons\E_Ticket\2025\2025_12_eticket_export.csv"
)
ASSIGNMENT_CSV = Path(
    r"C:\Users\carucci_r\OneDrive - City of Hackensack\09_Reference\Personnel\Assignment_Master_V2.csv"
)

# Load e-ticket export
with ETICKET_EXPORT.open("r", encoding="utf-8", errors="ignore") as f:
    header_line = f.readline().rstrip("\n")
    header = header_line.split(";")
    rows = []
    for line in f:
        line = line.rstrip("\n")
        if not line:
            continue
        if line.startswith('"'):
            try:
                inner = line.split('"', 2)[1]
            except Exception:
                inner = line.strip('"')
            parts = inner.split(";")
        else:
            parts = line.split(";")
        if len(parts) < 10:
            continue
        row = dict(zip(header, parts + [""] * max(0, len(header) - len(parts))))
        rows.append(row)
eticket_df = pd.DataFrame(rows)

# Normalize e-ticket Officer Id
eticket_officer_ids = eticket_df["Officer Id"].astype(str).str.strip()
eticket_officer_ids = eticket_officer_ids.str.replace(".0", "", regex=False)
eticket_officer_ids = eticket_officer_ids.str.zfill(4)
eticket_unique = set(eticket_officer_ids.unique())

# Load Assignment Master
assignment_df = pd.read_csv(ASSIGNMENT_CSV, dtype=str)
assignment_padded = assignment_df["PADDED_BADGE_NUMBER"].astype(str).str.strip()
assignment_padded = assignment_padded.str.replace(".0", "", regex=False)
assignment_padded = assignment_padded.str.zfill(4)
assignment_unique = set(assignment_padded.unique())

# Find missing
eticket_only = eticket_unique - assignment_unique

print(f"E-ticket unique Officer Ids: {len(eticket_unique)}")
print(f"Assignment Master unique PADDED_BADGE_NUMBER: {len(assignment_unique)}")
print(f"\nBadge numbers in e-ticket but NOT in Assignment Master:")
for badge in sorted(list(eticket_only)):
    print(f"  - {badge}")
