# Master_Automation Migration Verification Script
# Verifies all paths and configurations after migration to OneDrive

$ErrorActionPreference = 'Continue'

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Master_Automation Migration Verification" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$issues = @()
$checks = @()

# ---------- Check 1: Config file path ----------
Write-Host "[1/8] Checking config file..." -ForegroundColor Yellow
$configPath = Join-Path $PSScriptRoot "config\scripts.json"
if (Test-Path $configPath) {
    $config = Get-Content $configPath | ConvertFrom-Json
    $dropPath = $config.settings.powerbi_drop_path
    $expectedPath = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date\_DropExports"
    
    if ($dropPath -eq $expectedPath) {
        Write-Host "  ✅ Config path correct: $dropPath" -ForegroundColor Green
        $checks += "Config path: ✅"
    }
    else {
        Write-Host "  ❌ Config path incorrect!" -ForegroundColor Red
        Write-Host "     Current: $dropPath" -ForegroundColor Red
        Write-Host "     Expected: $expectedPath" -ForegroundColor Yellow
        $issues += "Config path mismatch"
        $checks += "Config path: ❌"
    }
    
    # Verify drop path exists
    if (Test-Path $dropPath) {
        Write-Host "  ✅ Drop folder exists: $dropPath" -ForegroundColor Green
        $checks += "Drop folder exists: ✅"
    }
    else {
        Write-Host "  ❌ Drop folder missing: $dropPath" -ForegroundColor Red
        $issues += "Drop folder missing"
        $checks += "Drop folder exists: ❌"
    }
}
else {
    Write-Host "  ❌ Config file not found: $configPath" -ForegroundColor Red
    $issues += "Config file missing"
    $checks += "Config file: ❌"
}

# ---------- Check 2: PowerBI_Date location ----------
Write-Host "`n[2/8] Checking PowerBI_Date location..." -ForegroundColor Yellow
$powerBIPath = "C:\Users\carucci_r\OneDrive - City of Hackensack\PowerBI_Date"
if (Test-Path $powerBIPath) {
    Write-Host "  ✅ PowerBI_Date exists: $powerBIPath" -ForegroundColor Green
    $checks += "PowerBI_Date location: ✅"
    
    # Check key directories
    $keyDirs = @("Backfill", "DAX", "etl", "mCode", "tools", "_DropExports")
    foreach ($dir in $keyDirs) {
        $dirPath = Join-Path $powerBIPath $dir
        if (Test-Path $dirPath) {
            Write-Host "    ✅ $dir exists" -ForegroundColor Green
        }
        else {
            Write-Host "    ⚠️  $dir missing" -ForegroundColor Yellow
            $issues += "Missing directory: $dir"
        }
    }
}
else {
    Write-Host "  ❌ PowerBI_Date not found: $powerBIPath" -ForegroundColor Red
    $issues += "PowerBI_Date missing"
    $checks += "PowerBI_Date location: ❌"
}

# ---------- Check 3: Master_Automation junction ----------
Write-Host "`n[3/8] Checking Master_Automation junction..." -ForegroundColor Yellow
$junctionPath = Join-Path $powerBIPath "Master_Automation"
if (Test-Path $junctionPath) {
    $junctionItem = Get-Item $junctionPath -ErrorAction SilentlyContinue
    if ($junctionItem.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        Write-Host "  ✅ Junction exists: $junctionPath" -ForegroundColor Green
        $checks += "Master_Automation junction: ✅"
        
        # Verify junction target
        try {
            $out = & cmd /c "fsutil reparsepoint query `"$junctionPath`"" 2>$null
            if ($LASTEXITCODE -eq 0 -and $out) {
                $match = $out | Select-String -Pattern 'Substitute Name:\s*(.+)$'
                if ($match) {
                    $target = $match.Matches[0].Groups[1].Value.Trim()
                    # Remove NTFS junction prefix (\??\) if present - handle both formats
                    $target = $target -replace '^\\\\\?\\', ''
                    $target = $target -replace '^\\\?\?\\', ''
                    $expectedTarget = "C:\Users\carucci_r\OneDrive - City of Hackensack\Master_Automation"
                    # Normalize paths for comparison (remove trailing backslashes, case-insensitive)
                    $targetNormalized = $target.TrimEnd('\').ToLower()
                    $expectedNormalized = $expectedTarget.TrimEnd('\').ToLower()
                    if ($targetNormalized -eq $expectedNormalized) {
                        Write-Host "    ✅ Junction points to correct location" -ForegroundColor Green
                    }
                    else {
                        Write-Host "    ⚠️  Junction target: $target" -ForegroundColor Yellow
                        Write-Host "       Expected: $expectedTarget" -ForegroundColor Yellow
                        # Check if it's just a path normalization issue
                        if ($target -match [regex]::Escape($expectedTarget)) {
                            Write-Host "    ✅ Paths match (normalization difference)" -ForegroundColor Green
                        }
                        else {
                            $issues += "Junction target may be incorrect"
                        }
                    }
                }
            }
        }
        catch {
            Write-Host "    ⚠️  Could not verify junction target" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "  ⚠️  Path exists but is not a junction" -ForegroundColor Yellow
        $issues += "Master_Automation is not a junction"
    }
}
else {
    Write-Host "  ❌ Junction missing: $junctionPath" -ForegroundColor Red
    $issues += "Master_Automation junction missing"
    $checks += "Master_Automation junction: ❌"
}

# ---------- Check 4: ETL Script paths ----------
Write-Host "`n[4/8] Checking ETL script paths..." -ForegroundColor Yellow
if ($config) {
    $scriptIssues = 0
    foreach ($script in $config.scripts) {
        if ($script.enabled) {
            $scriptPath = $script.path
            $scriptFile = Join-Path $scriptPath $script.script
            
            if (Test-Path $scriptPath) {
                if (Test-Path $scriptFile) {
                    Write-Host "    ✅ $($script.name): $scriptFile" -ForegroundColor Green
                }
                else {
                    Write-Host "    ❌ $($script.name): Script file missing: $scriptFile" -ForegroundColor Red
                    $scriptIssues++
                    $issues += "Script missing: $($script.name)"
                }
            }
            else {
                Write-Host "    ❌ $($script.name): Path missing: $scriptPath" -ForegroundColor Red
                $scriptIssues++
                $issues += "Path missing: $($script.name)"
            }
        }
    }
    if ($scriptIssues -eq 0) {
        Write-Host "  ✅ All ETL script paths valid" -ForegroundColor Green
        $checks += "ETL script paths: ✅"
    }
    else {
        Write-Host "  ❌ Found $scriptIssues script path issue(s)" -ForegroundColor Red
        $checks += "ETL script paths: ❌"
    }
}

# ---------- Check 5: Script file path references ----------
Write-Host "`n[5/8] Checking script file path references..." -ForegroundColor Yellow
$scriptFile = Join-Path $PSScriptRoot "scripts\run_all_etl.ps1"
if (Test-Path $scriptFile) {
    $content = Get-Content $scriptFile -Raw
    $oldPathRefs = @()
    
    if ($content -match 'C:\\Dev\\PowerBI_Date') {
        $oldPathRefs += "run_all_etl.ps1"
        Write-Host "  ⚠️  Found old path reference in run_all_etl.ps1" -ForegroundColor Yellow
    }
    
    if ($oldPathRefs.Count -eq 0) {
        Write-Host "  ✅ No old path references found in scripts" -ForegroundColor Green
        $checks += "Script path references: ✅"
    }
    else {
        Write-Host "  ⚠️  Old path references found in: $($oldPathRefs -join ', ')" -ForegroundColor Yellow
        $issues += "Old path references in scripts"
        $checks += "Script path references: ⚠️"
    }
}

# ---------- Check 6: Documentation path references ----------
Write-Host "`n[6/8] Checking documentation path references..." -ForegroundColor Yellow
$docFiles = @(
    "README.md",
    "QUICK_START.md"
)
$docIssues = @()
foreach ($docFile in $docFiles) {
    $docPath = Join-Path $PSScriptRoot $docFile
    if (Test-Path $docPath) {
        $content = Get-Content $docPath -Raw
        if ($content -match 'C:\\Dev\\PowerBI_Date') {
            $docIssues += $docFile
        }
    }
}
if ($docIssues.Count -eq 0) {
    Write-Host "  ✅ No old path references in documentation" -ForegroundColor Green
    $checks += "Documentation paths: ✅"
}
else {
    Write-Host "  ⚠️  Old path references found in: $($docIssues -join ', ')" -ForegroundColor Yellow
    $issues += "Old path references in docs"
    $checks += "Documentation paths: ⚠️"
}

# ---------- Check 7: Python executable ----------
Write-Host "`n[7/8] Checking Python executable..." -ForegroundColor Yellow
if ($config) {
    $pythonExe = $config.settings.python_executable
    $pythonFound = $false
    
    # Try common Python paths
    $pythonPaths = @($pythonExe, "python", "python3", "py")
    foreach ($py in $pythonPaths) {
        try {
            $version = & $py --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✅ Python found: $py ($version)" -ForegroundColor Green
                $pythonFound = $true
                $checks += "Python executable: ✅"
                break
            }
        }
        catch {
            continue
        }
    }
    
    if (-not $pythonFound) {
        Write-Host "  ⚠️  Python executable not found: $pythonExe" -ForegroundColor Yellow
        $issues += "Python executable not found"
        $checks += "Python executable: ⚠️"
    }
}

# ---------- Check 8: Log directory ----------
Write-Host "`n[8/8] Checking log directory..." -ForegroundColor Yellow
if ($config) {
    $logDir = Join-Path $PSScriptRoot $config.settings.log_directory
    if (Test-Path $logDir) {
        Write-Host "  ✅ Log directory exists: $logDir" -ForegroundColor Green
        $checks += "Log directory: ✅"
    }
    else {
        Write-Host "  ⚠️  Log directory missing (will be created on first run): $logDir" -ForegroundColor Yellow
        $checks += "Log directory: ⚠️"
    }
}

# ---------- Summary ----------
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Verification Summary" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

foreach ($check in $checks) {
    Write-Host "  $check" -ForegroundColor $(if ($check -match '✅') { 'Green' } elseif ($check -match '❌') { 'Red' } else { 'Yellow' })
}

if ($issues.Count -eq 0) {
    Write-Host "`n✅ All checks passed! Migration verified successfully." -ForegroundColor Green
}
else {
    Write-Host "`n⚠️  Found $($issues.Count) issue(s) that need attention:" -ForegroundColor Yellow
    foreach ($issue in $issues) {
        Write-Host "  - $issue" -ForegroundColor Yellow
    }
}

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "1. Review any issues above" -ForegroundColor White
Write-Host "2. Fix outdated path references if found" -ForegroundColor White
Write-Host "3. Test ETL execution: .\scripts\run_all_etl.ps1 -DryRun" -ForegroundColor White
Write-Host "4. Run full ETL: .\scripts\run_all_etl.ps1" -ForegroundColor White

