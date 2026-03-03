// 🕒 2026-02-27-01-00-00
// Project: Master_Automation/response_time_filter_review_feedback
// Author: R. A. Carucci
// Purpose: Opus peer review of Cursor AI filter review plan — corrections, enhancements, and strategic recommendations

# Feedback on Response Time Filter Review Plan
## Opus Review of Cursor AI Plan (c318595a)

---

## Verdict: Good direction, but two of four problems are wrong or incomplete

The plan correctly identifies the core issue (bimodal Routine distribution from self-initiated activity) and proposes the right general approach (expand the admin filter). However, it contains a factual error in Problem 2, underscopes the fix in Problem 1, and should consider a structural alternative before committing to the type-by-type approach.

---

## Problem 1 — Self-Initiated Call Types: MOSTLY CORRECT, BUT UNDERSCOPED

### What the plan gets right

All 23 unique proposed types exist in `CallType_Categories.csv` and are mapped as Routine. The groupings are logical:

- **MV Violations / Traffic Violation** (4 types) — officer-initiated stops, officer already present
- **Patrol-variant types** (Business Check, Property Check, Municipal Property/Building Check, Targeted Area Patrol, ESU - Targeted Patrol, Virtual - Patrol) — same logic as already-excluded TAPS and Patrol Check
- **Community Engagement** (11 types including trailing-space variants) — officer-directed outreach, not a response
- **Checked Road Conditions** and **Field Contact / Information** — self-initiated

### What the plan gets wrong: it says "25 types" but there are really 23

The plan lists `Motor Vehicle Violation ????????? Private Property` and two trailing-space Community Engagement variants as separate items. These are **already handled by normalization** (the batch ETL strips non-ASCII and collapses whitespace before matching). Adding the base form is sufficient. This is a counting error, not a logic error.

### What the plan misses: 63 more types in "Administrative and Support"

The plan focuses on self-initiated *enforcement* activity but overlooks an entire category. There are **63 Routine types** in the "Administrative and Support" category of `CallType_Categories.csv` that are NOT in the current admin filter:

**High-confidence additional exclusions** (internal paperwork, not a response to a citizen call):

- Court processing: `Court Appearance`, `Court Order`, `Court - Municipal Prisoner`, `Court- Municipal Prisoner`
- Record dispositions: `Active/Administratively Closed`, `Exceptionally Cleared/Closed`, `Unfounded Incident`, `Unfounded/Closed`, `No Investigation` (×2), `Improper Records`, `Warrant Recall`
- Sex offender processing: `Sex Offender Registration`, `Sex Offender - General`, `Sex Offender - Serve Documents`, `Sex Offender - Serve Tier Papers`, `Sex Offender - Travel`, `Sex Offender Registration - Employment`, `Sex Offender Registration - School Enrollment`, `Sex Offender-Removal Order`, `Sex Offender-General`
- Property processing: `Property Disposition`, `Property Return`, `Property Returned - Court Ordered`, `Property Returned - Lost and Found`, `Surrender of Ammunition`, `Surrender of Weapon`, `Surrendered Firearm ID Card`, `Surrendered License Plates`
- Service/Process: `Service - Subpoena`, `Service - Summons`, `Service of TRO / FRO`
- Internal/clerical: `A.C.O.R.N. Test`, `Civil Defense Test`, `Computer Issue - Desktop` (×2 spacing variants), `Computer Issue - Vehicle`, `Fingerprints`, `Generator Test`, `Photography`, `Meeting`, `Group`
- Prisoner handling: `Prisoner Log` (×2), `Prisoner Transport`
- Informational: `General Information`, `Information`, `Notification Request`, `Warning Issued`
- Licensing: `ABC Liquor License Applicant`, `Canvassing / Peddling Permit`
- Other: `Conditional Dismissal Process`, `ICE Notification`, `Parole/Probation Registry`, `Peace Officer`, `Property Damage - Police Vehicle`, `Tampering: Public Records 2C:28-7`, `Transportation`, `U-Visa`, `Docket – Drop Off`, `Docket – Pick up`

**Requires analyst judgment:**

- `Follow-up Investigation`, `Investigation-Follow up` — could be a detective responding to a scene, or desk work. If desk work, exclude.

The current admin filter already excludes `Court Officer`, `Court - Federal`, `Court - Municipal`, `Court - Other Municipality`, `Court - Superior` — but misses `Court Appearance`, `Court Order`, and the prisoner variants. These are the same category of non-response activity.

### Recommendation

Combine the plan's 23 types with these ~60 Administrative and Support types into a single v1.17.18 update. Don't do two rounds of regeneration.

---

## Problem 2 — Admin List Discrepancy: FACTUALLY WRONG

### The plan says
> "`process_cad_data_13month_rolling.py` claims 101 types... The batch ETL has 92 types..."

### What I found

I programmatically extracted and compared both lists. **Both scripts have exactly 92 types, and the lists are identical.** Zero types in one that aren't in the other.

The "101" is a **documentation error** in both scripts' comments. The rolling script says `# ADMINISTRATIVE INCIDENTS - 101 TYPES (EXPANDED LIST)` at line 51 and `"STEP 3: Filter Administrative Incidents (101 types)"` at line 558. The batch ETL copied this claim verbatim. But the actual `ADMIN_INCIDENTS_RAW` set contains 92 unique strings in both files.

### How this happened

The rolling script was likely developed iteratively — at one point the list may have had 101 types, then some were consolidated or removed without updating the comment. When the batch ETL ported the list, it copied the comment along with the code.

### Recommendation

- **Delete Problem 2 from the plan entirely** — there is no reconciliation to do.
- **Fix the "101" comments** in both scripts to say "92" (or whatever the count is after the v1.17.18 additions). Better yet, add a runtime assertion: `logging.info(f"Admin filter: {len(ADMIN_INCIDENTS_NORM)} types loaded")` so the actual count is always logged.
- **The TODO `reconcile-lists` should be replaced** with: "fix documentation claiming 101 types; actual count is 92 in both scripts."

---

## Problem 3 — Response Type Priority Inconsistency: CORRECT BUT LOW PRIORITY

The observation is accurate — the rolling script drops the original CAD `Response Type` and maps everything via `CAD_CALL_TYPE.xlsx`, while the batch ETL correctly uses the CAD value first. For 2025+ data where ~96% of records have valid CAD Response Type values, the rolling script's approach discards good data.

However, this is a **low-priority issue** because:

1. The batch ETL is the script producing the Power BI CSVs. It has the correct priority.
2. The rolling script is the reference/older implementation and may not be actively producing reports.
3. The `CallType_Categories.csv` mappings align with the CAD values in the vast majority of cases — so the practical impact is near zero.

### Recommendation

Log it as tech debt. Don't let it delay the v1.17.18 filter fix. If the rolling script is ever refactored, adopt the batch ETL's priority cascade.

---

## Problem 4 — Unicode/Trailing-Space Variants: ALREADY HANDLED

The plan correctly identifies the concern but then correctly notes the normalization handles it. I verified this — the batch ETL's `_inc_norm` column applies `.str.strip().str.lower().str.replace(r'[^\x00-\x7F]', '', regex=True).str.replace(r'\s+', ' ', regex=True)`, which will match:

- `Motor Vehicle Violation ??? Private Property` → `motor vehicle violation private property` → matches `Motor Vehicle Violation - Private Property` after normalization (the dash is ASCII, so it's preserved... **wait, actually this needs checking**)

### ⚠️ ACTUAL ISSUE: Dash handling in normalization

The normalization strips non-ASCII but keeps ASCII dashes. The base string `Motor Vehicle Violation - Private Property` normalizes to `motor vehicle violation - private property`. The unicode variant `Motor Vehicle Violation \ufffd Private Property` normalizes to `motor vehicle violation  private property` (the replacement char is stripped, leaving a double space that gets collapsed to single). So the normalized forms are:

- Base: `motor vehicle violation - private property`
- Unicode: `motor vehicle violation private property`

**These are NOT the same string.** The normalization does NOT guarantee matching here. You need BOTH the base form AND the unicode-variant form in the exclusion list, OR you need to also strip dashes during normalization.

### Recommendation

Either:
- (A) Add both forms explicitly to the exclusion list (belt and suspenders), or
- (B) Enhance normalization to also strip dashes: `.str.replace(r'[-\u2013\u2014]', ' ', regex=True)` before the whitespace collapse

Option (B) is cleaner but changes existing matching behavior. Option (A) is safer for a v1.17.18 fix.

---

## Strategic Alternative: Time-Based Filter Instead of (or In Addition to) Type-Based

### The core problem with the type-by-type approach

After these 23 + ~60 additions, you'll have ~175 excluded types. But there are still **~235 remaining Routine types** in `CallType_Categories.csv` that will remain in the dataset. Some of those will also be self-initiated (e.g., `Suspicious Activity`, `Alarm`, `Vacant House` — officers may self-initiate these without a citizen call). Every time a new incident type appears in CAD, you'll need to decide whether to add it to the exclusion list. This is a whack-a-mole pattern.

### Alternative approach: dispatch-time-based filter

A self-initiated call has a near-zero gap between `Time Dispatched` and `Time Out` because the officer is already on scene. You could add a secondary filter:

```python
# After admin-type filter, also exclude records where officer was
# already on scene when dispatched (self-initiated)
dispatch_gap = (df["_tout"] - df["_td"]).dt.total_seconds()
df = df[dispatch_gap > 30]  # Keep only records where officer took >30 sec to arrive after dispatch
```

**Advantages:**
- Catches ALL self-initiated activity regardless of incident type
- No need to maintain a growing exclusion list
- Automatically handles new incident types
- The 30-second threshold is operationally defensible (an officer can't physically travel to a new location in under 30 seconds)

**Disadvantages:**
- Removes some edge cases where an officer happens to be very close to a dispatched call
- Applies to all metrics, not just Dispatch-to-On-Scene
- Needs careful documentation

### Recommendation

Don't implement this in v1.17.18 — it's a bigger methodology change. But consider it for v1.18.x as a more sustainable solution. For now, the type-based filter expansion is the right incremental fix.

---

## Revised TODO List

Here's my recommended replacement for the plan's TODO structure:

| ID | Task | Status | Notes |
|----|------|--------|-------|
| `analyst-confirm` | Analyst confirms the ~83 new exclusion types (23 self-initiated + ~60 admin/support) | pending | Split into "auto-approve" (obvious admin) and "review" (5-10 borderline types) |
| `fix-101-claim` | Fix "101 types" documentation in both scripts to reflect actual count | pending | Replaces `reconcile-lists` — there is no list discrepancy |
| `add-types-batch-etl` | Add confirmed types to `ADMIN_INCIDENTS_RAW` with v1.17.18 comment block | pending | Two new blocks: "Self-initiated enforcement" and "Administrative processing" |
| `add-runtime-count` | Add `logging.info(f"Admin filter: {len(ADMIN_INCIDENTS_NORM)} types")` to both scripts | pending | Prevents future count-claim drift |
| `verify-normalization` | Confirm unicode MV Violation variant is caught, or add explicit entry | pending | See Problem 4 dash-handling issue |
| `run-etl` | Re-run batch ETL to regenerate 25 monthly CSVs | pending | |
| `compare-output` | Pre/post comparison: Routine mean AND median for all three metrics, Jan-25 and Jan-26 | pending | Expect Routine Dispatch-to-Scene mean to increase and median to increase significantly |
| `update-docs` | CHANGELOG v1.17.18, update SUMMARY/README filter description | pending | |
| `future-dispatch-filter` | Evaluate time-based dispatch gap filter for v1.18.x | backlog | Strategic alternative to type-based exclusion |

---

## Summary of Changes to Plan

| Plan Item | Verdict | Action |
|-----------|---------|--------|
| Problem 1 (25 self-initiated types) | ✅ Correct, but underscoped | Expand to ~83 types (add Administrative and Support category) |
| Problem 2 (92 vs 101 discrepancy) | ❌ Factually wrong | Delete — both scripts have 92 identical types; fix the "101" comments |
| Problem 3 (Response Type priority) | ✅ Correct, low priority | Log as tech debt, don't block v1.17.18 |
| Problem 4 (Unicode/trailing space) | ⚠️ Partially wrong | Normalization handles trailing spaces but NOT dash-to-replacement-char substitution; verify or add explicit entries |
| Missing: Admin/Support category | Not in plan | Add ~60 types from "Administrative and Support" category |
| Missing: Runtime count logging | Not in plan | Add to prevent future documentation drift |
| Missing: Strategic alternative | Not in plan | Evaluate dispatch-time-based filter for v1.18.x |

---

*Review completed: 2026-02-27 | Reviewer: Claude Opus 4.6*
