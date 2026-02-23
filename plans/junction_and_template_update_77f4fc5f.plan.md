---
name: Junction and Template Update
overview: Create a Windows junction so C:\Users\carucci_r resolves to C:\Users\RobertCarucci on this laptop, then finish pasting all 25 M code queries into the Power BI template and verify they load without errors.
todos:
  - id: create-junction
    content: "Create Windows junction: mklink /J C:\\Users\\carucci_r C:\\Users\\RobertCarucci (requires Admin prompt)"
    status: pending
  - id: verify-junction
    content: "Verify junction works: dir C:\\Users\\carucci_r\\OneDrive* shows the OneDrive folder"
    status: pending
  - id: paste-remaining
    content: Paste remaining 16 M code queries into Power BI template (Drone through Training)
    status: pending
  - id: verify-queries
    content: Reopen Power BI and verify path errors are resolved for previously-pasted queries
    status: pending
  - id: fix-patrol-traffic
    content: Apply remaining fixes to ___Patrol.m and ___Traffic.m
    status: pending
isProject: false
---

# Create Junction and Complete Template M Code Update

## Step 1: Create the Windows Junction (one-time setup)

Run this single command in an **elevated (Admin) PowerShell** or **Command Prompt**:

```cmd
mklink /J C:\Users\carucci_r C:\Users\RobertCarucci
```

This creates a directory junction. After this, any path starting with `C:\Users\carucci_r\` will transparently resolve to `C:\Users\RobertCarucci\`.

**To verify it worked:**

```cmd
dir C:\Users\carucci_r\OneDrive*
```

You should see your `OneDrive - City of Hackensack` folder listed.

**To remove later (if ever needed):**

```cmd
rmdir C:\Users\carucci_r
```

(This only removes the junction link, NOT the actual files.)

## Step 2: Resume Pasting M Code into Power BI Template

You completed through Detectives. Remaining queries to paste (skip the `//` comment header lines when copying):

**Drone (1 query)**

- `___Drone` <-- [m_code/drone/___Drone.m](m_code/drone/___Drone.m)

**ESU (3 queries)**

- `ESU_13Month` <-- [m_code/esu/ESU_13Month.m](m_code/esu/ESU_13Month.m)
- `MonthlyActivity` <-- [m_code/esu/MonthlyActivity.m](m_code/esu/MonthlyActivity.m)
- `TrackedItems` <-- [m_code/esu/TrackedItems.m](m_code/esu/TrackedItems.m)

**Overtime (1 query)**

- `___Overtime_Timeoff_v3` <-- [m_code/overtime/___Overtime_Timeoff_v3.m](m_code/overtime/___Overtime_Timeoff_v3.m)

**Response Time (1 query)**

- `___ResponseTimeCalculator` <-- [m_code/response_time/___ResponseTimeCalculator.m](m_code/response_time/___ResponseTimeCalculator.m)

**Shared (1 query)**

- `___DimMonth` <-- [m_code/shared/___DimMonth.m](m_code/shared/___DimMonth.m)

**SSOCC (1 query)**

- `TAS_Dispatcher_Incident` <-- [m_code/ssocc/TAS_Dispatcher_Incident.m](m_code/ssocc/TAS_Dispatcher_Incident.m)

**STACP (3 queries)**

- `___STACP_pt_1_2` <-- [m_code/stacp/___STACP_pt_1_2.m](m_code/stacp/___STACP_pt_1_2.m)
- `STACP_DIAGNOSTIC` <-- [m_code/stacp/STACP_DIAGNOSTIC.m](m_code/stacp/STACP_DIAGNOSTIC.m)
- `___Social_Media` <-- [m_code/stacp/___Social_Media.m](m_code/stacp/___Social_Media.m)

**Summons (4 queries)**

- `summons_13month_trend` <-- [m_code/summons/summons_13month_trend.m](m_code/summons/summons_13month_trend.m)
- `summons_all_bureaus` <-- [m_code/summons/summons_all_bureaus.m](m_code/summons/summons_all_bureaus.m)
- `summons_top5_moving` <-- [m_code/summons/summons_top5_moving.m](m_code/summons/summons_top5_moving.m)
- `summons_top5_parking` <-- [m_code/summons/summons_top5_parking.m](m_code/summons/summons_top5_parking.m)

**Training (1 query)**

- `___Cost_of_Training` <-- [m_code/training/___Cost_of_Training.m](m_code/training/___Cost_of_Training.m)

## Step 3: Verify Queries Load (with junction active)

After the junction is in place and all queries are pasted:

- Close and reopen Power BI Desktop (to clear cached path errors)
- Open the template
- Check that previously-errored queries (Arrests, Community, CSB, Detectives) now resolve
- Queries may still show "no data" if source files haven't synced to this laptop via OneDrive, but the path errors should be gone

## Step 4: Remaining Fixes (Patrol and Traffic)

These two queries still need code fixes (not just paste):

- `___Patrol` -- needs `ReportMonth = pReportMonth` binding + `{"01-26", Int64.Type}` column
- `___Traffic` -- needs `{"01-26", Int64.Type}` added to column type declaration

These can be fixed after verifying the other queries work.