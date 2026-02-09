# Benchmark Directory Cleanup Strategy & Implementation

**Date**: February 9, 2026  
**Goal**: Simplify Benchmark directory structure and eliminate duplication  
**Status**: Ready to implement

---

## Recommended Strategy: Simplified Single Location

### ✅ RECOMMENDED: Use This Simple Structure

```
05_EXPORTS\Benchmark\
├── show_force\
│   └── YYYY_MM_show_force_complete.csv
├── use_force\
│   └── YYYY_MM_use_force_complete.csv
└── vehicle_pursuit\
    └── YYYY_MM_vehicle_pursuit_complete.csv
```

**Benefits**:
- ✅ Simple 2-level structure (easy to navigate)
- ✅ Clear naming pattern
- ✅ One file per event type per month
- ✅ No confusing nested folders
- ✅ Scales easily (just add new YYYY_MM files)

---

## Why Your Instinct is Correct

### Unnecessary Complexity in _Benchmark

You're right to question these folders:

**1. `all_events_combined\`**
- **Purpose**: Likely combines all three event types
- **Issue**: Power BI can do this via relationships
- **Recommendation**: ❌ **NOT NEEDED** - Delete

**2. `by_event_type\`**
- **Purpose**: Duplicates the main event type folders
- **Issue**: Same data as `show_force\`, `use_force\`, `vehicle_pursuit\`
- **Recommendation**: ❌ **NOT NEEDED** - Delete (redundant)

**3. `by_time_period\`**
- **Purpose**: Organizes by time windows (rolling_13month, ytd_current)
- **Issue**: These can be calculated in Power BI using date filters
- **Recommendation**: ❌ **NOT NEEDED** - Delete

### The Only Structure You Need

**Three event type folders** (that's it!):
```
Benchmark\
├── show_force\      ← All show of force reports here
├── use_force\       ← All use of force reports here
└── vehicle_pursuit\ ← All vehicle pursuit reports here
```

Each folder contains monthly files with clear naming:
- `2026_01_use_force_complete.csv`
- `2026_02_use_force_complete.csv`
- etc.

---

## Implementation Plan

### Phase 1: Identify Active Data (10 minutes)

**Step 1**: Find where your January 2026 data actually is

```powershell
# Search for any January 2026 files
Get-ChildItem "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS" `
  -Recurse -File `
  -Include "*2026_01*","*jan*2026*","*january*2026*" `
  -ErrorAction SilentlyContinue |
  Where-Object {$_.FullName -like "*Benchmark*"} |
  Select-Object FullName, Length, LastWriteTime

# This will show you exactly where Jan 2026 files are
```

**Step 2**: Identify which files Power BI actually uses

- Open your Power BI report
- Go to Transform Data → Data Source Settings
- Check which Benchmark paths are referenced
- Note those specific file paths

### Phase 2: Create Clean Structure (5 minutes)

**Execute this PowerShell script**:

```powershell
# Create the simple Benchmark structure
$benchmarkBase = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark"

# Ensure base directory exists
if (-not (Test-Path $benchmarkBase)) {
    New-Item -ItemType Directory -Path $benchmarkBase -Force
}

# Create three event type folders
$eventTypes = @("show_force", "use_force", "vehicle_pursuit")

foreach ($type in $eventTypes) {
    $folderPath = Join-Path $benchmarkBase $type
    if (-not (Test-Path $folderPath)) {
        New-Item -ItemType Directory -Path $folderPath -Force
        Write-Host "Created: $folderPath" -ForegroundColor Green
    } else {
        Write-Host "Exists: $folderPath" -ForegroundColor Cyan
    }
}

Write-Host "`nClean Benchmark structure ready!" -ForegroundColor Green
```

### Phase 3: Move Active Files (10 minutes)

**If you have January 2026 data**, move it to the simple structure:

```powershell
# Example: Move use of force file
$sourcePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Benchmark\use_force\complete_report\full_year\2026\2026_01_use_force.csv"
$destPath = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark\use_force\2026_01_use_force_complete.csv"

if (Test-Path $sourcePath) {
    Copy-Item -Path $sourcePath -Destination $destPath -Force
    Write-Host "Copied: $sourcePath" -ForegroundColor Green
    Write-Host "To: $destPath" -ForegroundColor Green
}

# Repeat for show_force and vehicle_pursuit
```

### Phase 4: Archive or Delete _Benchmark (5 minutes)

**Option A: Archive** (if you want to keep old data)

```powershell
# Create archive folder
$archivePath = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Benchmark_ARCHIVE_2026_02_09"

# Rename _Benchmark to archive
Rename-Item `
  -Path "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Benchmark" `
  -NewName "_Benchmark_ARCHIVE_2026_02_09"

Write-Host "Archived: _Benchmark renamed to _Benchmark_ARCHIVE_2026_02_09" -ForegroundColor Yellow
```

**Option B: Delete** (if folders are empty or you don't need the complex structure)

```powershell
# CAUTION: Only run if you're sure you don't need the data
$toDelete = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Benchmark"

# Safety check: List what would be deleted
Get-ChildItem $toDelete -Recurse -File | Measure-Object | Select-Object Count

# If count is 0 or you've verified files aren't needed:
# Remove-Item -Path $toDelete -Recurse -Force
# Write-Host "Deleted: _Benchmark" -ForegroundColor Red
```

### Phase 5: Update Power BI Connections (15 minutes)

**If Power BI reads from _Benchmark**:

1. Open Power BI Desktop
2. Go to: Home → Transform Data → Data Source Settings
3. For each Benchmark query:
   - Click "Change Source"
   - Update path to new `Benchmark\` location
   - Update file name if needed
4. Click "Close & Apply"
5. Refresh data to verify

---

## Complete Cleanup Script

Here's a comprehensive script that does it all:

```powershell
<#
.SYNOPSIS
Benchmark Directory Cleanup and Simplification

.DESCRIPTION
Consolidates complex _Benchmark structure into simple Benchmark\ structure.
Preserves data, removes complexity.

.PARAMETER WhatIf
Shows what would be done without actually doing it

.EXAMPLE
.\Cleanup-BenchmarkDirectories.ps1 -WhatIf
Shows planned changes

.EXAMPLE
.\Cleanup-BenchmarkDirectories.ps1
Executes cleanup
#>

param(
    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'

# Paths
$oldBenchmark = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\_Benchmark"
$newBenchmark = "C:\Users\carucci_r\OneDrive - City of Hackensack\05_EXPORTS\Benchmark"
$archiveName = "_Benchmark_ARCHIVE_2026_02_09"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Benchmark Directory Cleanup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($WhatIf) {
    Write-Host "=== WHATIF MODE - No changes will be made ===" -ForegroundColor Magenta
    Write-Host ""
}

# Step 1: Create simple structure
Write-Host "Step 1: Creating clean Benchmark structure..." -ForegroundColor Yellow
Write-Host ""

$eventTypes = @("show_force", "use_force", "vehicle_pursuit")

foreach ($type in $eventTypes) {
    $folderPath = Join-Path $newBenchmark $type
    
    if ($WhatIf) {
        Write-Host "  [WOULD CREATE] $folderPath" -ForegroundColor Cyan
    }
    elseif (-not (Test-Path $folderPath)) {
        New-Item -ItemType Directory -Path $folderPath -Force | Out-Null
        Write-Host "  [CREATED] $folderPath" -ForegroundColor Green
    }
    else {
        Write-Host "  [EXISTS] $folderPath" -ForegroundColor Gray
    }
}

# Step 2: Find all data files in _Benchmark
Write-Host ""
Write-Host "Step 2: Scanning for data files in _Benchmark..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path $oldBenchmark) {
    $allFiles = Get-ChildItem -Path $oldBenchmark -Recurse -File -ErrorAction SilentlyContinue |
                Where-Object {$_.Name -like "*.csv" -or $_.Name -like "*.xlsx"}
    
    Write-Host "  Found $($allFiles.Count) files in _Benchmark" -ForegroundColor Cyan
    
    if ($allFiles.Count -eq 0) {
        Write-Host "  No data files found - structure appears to be empty" -ForegroundColor Yellow
    }
    else {
        Write-Host ""
        Write-Host "  Recent files:" -ForegroundColor Cyan
        $allFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | ForEach-Object {
            $relativePath = $_.FullName.Replace($oldBenchmark, "")
            Write-Host "    - $relativePath ($('{0:N0}' -f $_.Length) bytes)" -ForegroundColor Gray
        }
    }
}
else {
    Write-Host "  _Benchmark directory not found - may already be cleaned up" -ForegroundColor Yellow
}

# Step 3: Copy January 2026 files if they exist
Write-Host ""
Write-Host "Step 3: Looking for January 2026 files..." -ForegroundColor Yellow
Write-Host ""

$jan2026Files = Get-ChildItem -Path $oldBenchmark -Recurse -File -ErrorAction SilentlyContinue |
                Where-Object {$_.Name -like "*2026_01*" -or $_.Name -like "*jan*2026*"}

if ($jan2026Files.Count -gt 0) {
    Write-Host "  Found $($jan2026Files.Count) January 2026 files" -ForegroundColor Cyan
    
    foreach ($file in $jan2026Files) {
        # Determine event type from path
        $eventType = $null
        if ($file.FullName -like "*use_force*") { $eventType = "use_force" }
        elseif ($file.FullName -like "*show_force*") { $eventType = "show_force" }
        elseif ($file.FullName -like "*vehicle_pursuit*") { $eventType = "vehicle_pursuit" }
        
        if ($eventType) {
            $destPath = Join-Path $newBenchmark "$eventType\$($file.Name)"
            
            if ($WhatIf) {
                Write-Host "  [WOULD COPY] $($file.Name)" -ForegroundColor Cyan
                Write-Host "    From: $($file.DirectoryName)" -ForegroundColor Gray
                Write-Host "    To: $(Split-Path $destPath -Parent)" -ForegroundColor Gray
            }
            else {
                Copy-Item -Path $file.FullName -Destination $destPath -Force
                Write-Host "  [COPIED] $($file.Name) → $eventType\" -ForegroundColor Green
            }
        }
    }
}
else {
    Write-Host "  No January 2026 files found" -ForegroundColor Gray
    Write-Host "  (Files may be named differently or not yet exported)" -ForegroundColor Gray
}

# Step 4: Archive _Benchmark
Write-Host ""
Write-Host "Step 4: Archiving old _Benchmark structure..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path $oldBenchmark) {
    $archivePath = Join-Path (Split-Path $oldBenchmark -Parent) $archiveName
    
    if ($WhatIf) {
        Write-Host "  [WOULD RENAME] _Benchmark → $archiveName" -ForegroundColor Cyan
    }
    else {
        if (Test-Path $archivePath) {
            Write-Host "  [SKIPPED] Archive already exists: $archiveName" -ForegroundColor Yellow
        }
        else {
            Rename-Item -Path $oldBenchmark -NewName $archiveName
            Write-Host "  [ARCHIVED] _Benchmark → $archiveName" -ForegroundColor Green
        }
    }
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "New Structure:" -ForegroundColor Green
Write-Host "  $newBenchmark\" -ForegroundColor Gray
Write-Host "  ├── show_force\" -ForegroundColor Gray
Write-Host "  ├── use_force\" -ForegroundColor Gray
Write-Host "  └── vehicle_pursuit\" -ForegroundColor Gray
Write-Host ""

if ($WhatIf) {
    Write-Host "This was a dry run. Remove -WhatIf to execute." -ForegroundColor Magenta
}
else {
    Write-Host "✓ Cleanup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Verify files in: $newBenchmark" -ForegroundColor Gray
    Write-Host "  2. Update Power BI data source paths (if needed)" -ForegroundColor Gray
    Write-Host "  3. Test Power BI refresh" -ForegroundColor Gray
    Write-Host "  4. Delete archive after verification (optional)" -ForegroundColor Gray
}

Write-Host ""
```

---

## Decision Matrix

### Question: What Should We Do?

**Answer**: ✅ **Simplify to single Benchmark\ structure**

| Aspect | Keep Complex _Benchmark | Use Simple Benchmark\ | Recommendation |
|--------|------------------------|---------------------|----------------|
| Ease of Use | ❌ Hard to navigate | ✅ Very easy | **Simple** |
| Maintenance | ❌ Complex | ✅ Minimal | **Simple** |
| Power BI Setup | ❌ Complicated paths | ✅ Clean paths | **Simple** |
| Scalability | ❌ Pre-created future years | ✅ Add as needed | **Simple** |
| Monthly Workflow | ❌ Multiple folder decisions | ✅ One clear location | **Simple** |

---

## Your Questions Answered

### 1. Should we use only the `complete_report\all_time\` folders?

**Answer**: **No - use even simpler structure!**

Don't use:
- ❌ `_Benchmark\use_force\complete_report\all_time\`

Instead use:
- ✅ `Benchmark\use_force\`

**Reason**: You don't need the extra nesting. Just put monthly files directly in the event type folder.

### 2. Are these folders needed?

- **all_events_combined**: ❌ NO - Power BI can combine
- **by_event_type**: ❌ NO - Redundant with main folders
- **by_time_period**: ❌ NO - Power BI can filter by date

**Recommendation**: Delete all three. They add complexity without value.

### 3. How do I ensure this doesn't happen next month?

**Set clear rules**:

1. **One directory only**: `05_EXPORTS\Benchmark\`
2. **Three folders only**: `show_force\`, `use_force\`, `vehicle_pursuit\`
3. **File naming**: `YYYY_MM_eventtype_complete.csv`
4. **No subfolders**: Files go directly in event type folder

**Document it**:
```
Monthly Benchmark Export Process:
1. Export from Benchmark system
2. Name file: 2026_02_use_force_complete.csv
3. Save to: 05_EXPORTS\Benchmark\use_force\
4. Done!
```

---

## Recommendation: Execute Now

**Steps to complete today**:

1. **Run cleanup script** with `-WhatIf` first (safe preview)
2. **Review what it will do**
3. **Run cleanup script** for real
4. **Verify** files in new structure
5. **Update Power BI** paths (if needed)
6. **Test** Power BI refresh
7. **Delete archive** after verification (optional)

**Time required**: 30-45 minutes

**Benefits**:
- ✅ Clean structure going forward
- ✅ No confusion next month
- ✅ Easier to maintain
- ✅ Faster file operations

---

**Ready to execute cleanup?** I can save the script and we can run it now!

