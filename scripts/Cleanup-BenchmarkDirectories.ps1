<#
.SYNOPSIS
Benchmark Directory Cleanup and Simplification

.DESCRIPTION
Consolidates complex _Benchmark structure into simple Benchmark\ structure.
Removes unnecessary complexity while preserving data.

.PARAMETER WhatIf
Shows what would be done without actually doing it (dry run)

.EXAMPLE
.\Cleanup-BenchmarkDirectories.ps1 -WhatIf
Preview changes without making them

.EXAMPLE
.\Cleanup-BenchmarkDirectories.ps1
Execute cleanup

.NOTES
Created: 2026-02-09
Purpose: Simplify duplicate Benchmark directory structure
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
        if (-not (Test-Path $folderPath)) {
            Write-Host "  [WOULD CREATE] $folderPath" -ForegroundColor Cyan
        } else {
            Write-Host "  [EXISTS] $folderPath" -ForegroundColor Gray
        }
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
    
    Write-Host "  Found $($allFiles.Count) data files in _Benchmark" -ForegroundColor Cyan
    
    if ($allFiles.Count -eq 0) {
        Write-Host "  Structure appears to be empty (no CSV or Excel files)" -ForegroundColor Yellow
    }
    else {
        Write-Host ""
        Write-Host "  Recent files:" -ForegroundColor Cyan
        $allFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 10 | ForEach-Object {
            $relativePath = $_.FullName.Replace($oldBenchmark, "").TrimStart('\')
            $sizeKB = [math]::Round($_.Length / 1KB, 1)
            Write-Host "    - $relativePath ($sizeKB KB)" -ForegroundColor Gray
        }
        
        if ($allFiles.Count > 10) {
            Write-Host "    ... and $($allFiles.Count - 10) more files" -ForegroundColor Gray
        }
    }
}
else {
    Write-Host "  _Benchmark directory not found" -ForegroundColor Yellow
    Write-Host "  (May already be cleaned up)" -ForegroundColor Gray
}

# Step 3: Copy January 2026 files if they exist
Write-Host ""
Write-Host "Step 3: Looking for January 2026 files..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path $oldBenchmark) {
    $jan2026Files = Get-ChildItem -Path $oldBenchmark -Recurse -File -ErrorAction SilentlyContinue |
                    Where-Object {
                        ($_.Name -like "*2026_01*" -or $_.Name -like "*jan*2026*" -or $_.Name -like "*january*2026*") -and
                        ($_.Name -like "*.csv" -or $_.Name -like "*.xlsx")
                    }
    
    if ($jan2026Files.Count -gt 0) {
        Write-Host "  Found $($jan2026Files.Count) January 2026 files" -ForegroundColor Cyan
        Write-Host ""
        
        foreach ($file in $jan2026Files) {
            # Determine event type from path
            $eventType = $null
            if ($file.FullName -like "*use_force*" -or $file.FullName -like "*use-force*") {
                $eventType = "use_force"
            }
            elseif ($file.FullName -like "*show_force*" -or $file.FullName -like "*show-force*") {
                $eventType = "show_force"
            }
            elseif ($file.FullName -like "*vehicle_pursuit*" -or $file.FullName -like "*pursuit*") {
                $eventType = "vehicle_pursuit"
            }
            
            if ($eventType) {
                $destPath = Join-Path $newBenchmark "$eventType\$($file.Name)"
                
                if ($WhatIf) {
                    Write-Host "  [WOULD COPY] $($file.Name)" -ForegroundColor Cyan
                    Write-Host "    From: ...$(Split-Path $file.FullName -Parent | Split-Path -Leaf)\$($file.Name)" -ForegroundColor Gray
                    Write-Host "    To: Benchmark\$eventType\$($file.Name)" -ForegroundColor Gray
                }
                else {
                    Copy-Item -Path $file.FullName -Destination $destPath -Force
                    Write-Host "  [COPIED] $($file.Name)" -ForegroundColor Green
                    Write-Host "    → Benchmark\$eventType\" -ForegroundColor Gray
                }
            }
            else {
                Write-Host "  [SKIPPED] $($file.Name) - could not determine event type" -ForegroundColor Yellow
            }
        }
    }
    else {
        Write-Host "  No January 2026 files found in _Benchmark" -ForegroundColor Gray
        Write-Host "  (Files may use different naming or not yet exported)" -ForegroundColor Gray
    }
}

# Step 4: Archive _Benchmark
Write-Host ""
Write-Host "Step 4: Archiving old _Benchmark structure..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path $oldBenchmark) {
    $archivePath = Join-Path (Split-Path $oldBenchmark -Parent) $archiveName
    
    if ($WhatIf) {
        Write-Host "  [WOULD RENAME] _Benchmark → $archiveName" -ForegroundColor Cyan
        Write-Host "    This preserves the old structure for safety" -ForegroundColor Gray
    }
    else {
        if (Test-Path $archivePath) {
            Write-Host "  [SKIPPED] Archive already exists: $archiveName" -ForegroundColor Yellow
        }
        else {
            Rename-Item -Path $oldBenchmark -NewName $archiveName
            Write-Host "  [ARCHIVED] _Benchmark → $archiveName" -ForegroundColor Green
            Write-Host "    Old structure preserved as archive" -ForegroundColor Gray
        }
    }
}
else {
    Write-Host "  _Benchmark directory not found (may already be archived)" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($WhatIf) {
    Write-Host "Preview of changes:" -ForegroundColor Yellow
} else {
    Write-Host "Changes completed:" -ForegroundColor Green
}

Write-Host ""
Write-Host "New Benchmark Structure:" -ForegroundColor Cyan
Write-Host "  Benchmark\" -ForegroundColor White
Write-Host "  ├── show_force\" -ForegroundColor Gray
Write-Host "  ├── use_force\" -ForegroundColor Gray
Write-Host "  └── vehicle_pursuit\" -ForegroundColor Gray
Write-Host ""

if (Test-Path $newBenchmark) {
    Write-Host "Files in new structure:" -ForegroundColor Cyan
    foreach ($type in $eventTypes) {
        $typePath = Join-Path $newBenchmark $type
        if (Test-Path $typePath) {
            $files = Get-ChildItem -Path $typePath -File -ErrorAction SilentlyContinue
            if ($files.Count -gt 0) {
                Write-Host "  $type\: $($files.Count) file(s)" -ForegroundColor Gray
                foreach ($file in $files) {
                    $sizeKB = [math]::Round($file.Length / 1KB, 1)
                    Write-Host "    - $($file.Name) ($sizeKB KB)" -ForegroundColor DarkGray
                }
            } else {
                Write-Host "  $type\: (empty)" -ForegroundColor DarkGray
            }
        }
    }
}

Write-Host ""

if ($WhatIf) {
    Write-Host "This was a dry run. Remove -WhatIf to execute cleanup." -ForegroundColor Magenta
    Write-Host ""
    Write-Host "Command to execute for real:" -ForegroundColor Yellow
    Write-Host "  .\Cleanup-BenchmarkDirectories.ps1" -ForegroundColor White
} else {
    Write-Host "✓ Cleanup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. ✓ New structure created" -ForegroundColor Gray
    Write-Host "  2. ✓ Old structure archived as: $archiveName" -ForegroundColor Gray
    Write-Host "  3. [ ] Verify files in: $newBenchmark" -ForegroundColor Gray
    Write-Host "  4. [ ] Update Power BI data source paths (if needed)" -ForegroundColor Gray
    Write-Host "  5. [ ] Test Power BI refresh" -ForegroundColor Gray
    Write-Host "  6. [ ] Delete archive after verification (optional)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To delete archive (after verification):" -ForegroundColor DarkGray
    Write-Host "  Remove-Item ""$archivePath"" -Recurse -Force" -ForegroundColor DarkGray
}

Write-Host ""
