# Master ETL Orchestrator
# Runs all configured Python ETL scripts in order

param(
    [string[]]$ScriptNames = @(),  # Run only specified scripts (empty = all)
    [switch]$DryRun,  # Preview what would run
    [switch]$SkipPowerBI  # Skip Power BI integration step
)

$ErrorActionPreference = 'Stop'

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$automationDir = Split-Path -Parent $scriptDir
$configPath = Join-Path $automationDir "config\scripts.json"

# Colors
$Green = "`e[32m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Cyan = "`e[34m"
$Reset = "`e[0m"

function Write-Step([string]$msg) { Write-Host "$Cyan>> $msg$Reset" }
function Write-Success([string]$msg) { Write-Host "$Green[OK] $msg$Reset" }
function Write-Warn([string]$msg) { Write-Host "$Yellow[WARN] $msg$Reset" }
function Write-Fail([string]$msg) { Write-Host "$Red[FAIL] $msg$Reset" }

# Load configuration
if (-not (Test-Path $configPath)) {
    Write-Fail "Configuration file not found: $configPath"
    exit 1
}

$config = Get-Content $configPath | ConvertFrom-Json
$settings = $config.settings
$scripts = $config.scripts | Where-Object { $_.enabled -eq $true } | Sort-Object order

# Filter to specific scripts if requested
if ($ScriptNames.Count -gt 0) {
    $scripts = $scripts | Where-Object { $_.name -in $ScriptNames }
    if ($scripts.Count -eq 0) {
        Write-Fail "No matching enabled scripts found"
        exit 1
    }
}

# Create log directory
$logDir = Join-Path $automationDir $settings.log_directory
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# Create timestamp
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$logFile = Join-Path $logDir "${timestamp}_ETL_Run.log"

function Write-Log([string]$message) {
    $logMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $message"
    Add-Content -Path $logFile -Value $logMessage
    Write-Host $message
}

Write-Log "=== Master ETL Orchestrator Started ==="
Write-Log "Timestamp: $timestamp"
Write-Log "Scripts to run: $($scripts.Count)"
Write-Log ""

if ($DryRun) {
    Write-Warn "DRY RUN MODE - No scripts will execute"
    Write-Log "DRY RUN MODE"
}

# Track results
$results = @()
$startTime = Get-Date

foreach ($scriptConfig in $scripts) {
    $scriptName = $scriptConfig.name
    $scriptPath = $scriptConfig.path
    $scriptFile = $scriptConfig.script
    $fullScriptPath = Join-Path $scriptPath $scriptFile
    
    Write-Log ""
    Write-Step "Processing: $scriptName"
    Write-Log "  Script: $fullScriptPath"
    Write-Log "  Order: $($scriptConfig.order)"
    
    if ($DryRun) {
        Write-Host "  [DRY RUN] Would execute: $fullScriptPath" -ForegroundColor Gray
        continue
    }
    
    # Check if script exists
    if (-not (Test-Path $fullScriptPath)) {
        Write-Fail "  Script not found: $fullScriptPath"
        Write-Log "  ERROR: Script file not found"
        $results += @{
            Name = $scriptName
            Status = "Failed"
            Error = "Script file not found"
            Duration = 0
        }
        if (-not $settings.continue_on_error) {
            Write-Fail "Stopping due to error (continue_on_error = false)"
            break
        }
        continue
    }
    
    # Change to script directory
    Push-Location $scriptPath
    
    try {
        $scriptStartTime = Get-Date
        $scriptLogFile = Join-Path $logDir "${timestamp}_${scriptName}.log"
        
        Write-Log "  Executing Python script..."
        Write-Log "  Log: $scriptLogFile"
        
        # Run Python script
        $pythonCmd = $settings.python_executable
        $timeoutSeconds = $scriptConfig.timeout_minutes * 60
        
        # Execute with timeout
        $process = Start-Process -FilePath $pythonCmd -ArgumentList $scriptFile -WorkingDirectory $scriptPath -NoNewWindow -PassThru -RedirectStandardOutput $scriptLogFile -RedirectStandardError "$scriptLogFile.err"
        
        # Wait with timeout
        $process.WaitForExit($timeoutSeconds * 1000)
        
        if (-not $process.HasExited) {
            Stop-Process -Id $process.Id -Force
            throw "Script exceeded timeout of $($scriptConfig.timeout_minutes) minutes"
        }
        
        $scriptDuration = (Get-Date) - $scriptStartTime
        
        if ($process.ExitCode -eq 0) {
            Write-Success "  Completed in $([math]::Round($scriptDuration.TotalSeconds, 2)) seconds"
            Write-Log "  SUCCESS: Exit code 0"
            
            # Find output files
            $outputFiles = @()
            foreach ($pattern in $scriptConfig.output_patterns) {
                # Check if pattern includes a path (contains backslash or forward slash)
                if ($pattern -match '[\\/]') {
                    # Pattern includes subdirectory path - resolve relative to script path
                    $searchPath = Join-Path $scriptPath $pattern
                    # Extract just the filename pattern for filtering
                    $fileName = Split-Path -Leaf $pattern
                    $dirPath = Split-Path -Parent $searchPath
                    if (Test-Path $dirPath) {
                        $found = Get-ChildItem -Path $dirPath -Filter $fileName -ErrorAction SilentlyContinue
                        $outputFiles += $found
                    }
                } else {
                    # Simple filename pattern - search recursively
                    $found = Get-ChildItem -Path $scriptPath -Filter $pattern -Recurse -ErrorAction SilentlyContinue
                    $outputFiles += $found
                }
            }
            
            Write-Log "  Output files found: $($outputFiles.Count)"
            
            # Copy to Power BI drop folder if enabled
            if ($scriptConfig.output_to_powerbi -and -not $SkipPowerBI) {
                $dropPath = $settings.powerbi_drop_path
                if (-not (Test-Path $dropPath)) {
                    Write-Warn "  Power BI drop folder not found: $dropPath"
                    Write-Log "  WARNING: Power BI drop folder not found"
                } else {
                    foreach ($file in $outputFiles) {
                        $destPath = Join-Path $dropPath $file.Name
                        Copy-Item -Path $file.FullName -Destination $destPath -Force
                        Write-Log "  Copied to Power BI: $($file.Name)"
                    }
                    Write-Success "  Copied $($outputFiles.Count) file(s) to Power BI drop folder"
                }
            }
            
            $results += @{
                Name = $scriptName
                Status = "Success"
                Error = $null
                Duration = $scriptDuration.TotalSeconds
                OutputFiles = $outputFiles.Count
            }
        } else {
            throw "Script exited with code $($process.ExitCode)"
        }
        
    } catch {
        $scriptDuration = (Get-Date) - $scriptStartTime
        Write-Fail "  Error: $_"
        Write-Log "  ERROR: $_"
        
        $results += @{
            Name = $scriptName
            Status = "Failed"
            Error = $_.Exception.Message
            Duration = $scriptDuration.TotalSeconds
        }
        
        if (-not $settings.continue_on_error) {
            Write-Fail "Stopping due to error (continue_on_error = false)"
            break
        }
    } finally {
        Pop-Location
    }
}

# Summary
$totalDuration = (Get-Date) - $startTime
$successCount = ($results | Where-Object { $_.Status -eq "Success" }).Count
$failCount = ($results | Where-Object { $_.Status -eq "Failed" }).Count

Write-Log ""
Write-Log "=== Execution Summary ==="
Write-Log "Total duration: $([math]::Round($totalDuration.TotalMinutes, 2)) minutes"
Write-Log "Success: $successCount"
Write-Log "Failed: $failCount"
Write-Log ""

Write-Host ""
Write-Host "=== Execution Summary ===" -ForegroundColor Cyan
Write-Host "Total duration: $([math]::Round($totalDuration.TotalMinutes, 2)) minutes" -ForegroundColor Cyan
Write-Host ""

Write-Host "Results:" -ForegroundColor Yellow
foreach ($result in $results) {
    if ($result.Status -eq "Success") {
        Write-Success "$($result.Name): Success ($([math]::Round($result.Duration, 2))s, $($result.OutputFiles) file(s))"
    } else {
        Write-Fail "$($result.Name): Failed - $($result.Error)"
    }
}

Write-Log "=== Master ETL Orchestrator Completed ==="
Write-Host ""
Write-Host "Full log: $logFile" -ForegroundColor Gray

if ($successCount -eq $results.Count) {
    Write-Success "All scripts completed successfully!"
    if (-not $SkipPowerBI) {
        Write-Host ""
        Write-Host "Next step: Run Power BI organization script" -ForegroundColor Cyan
        Write-Host "  cd C:\Dev\PowerBI_Date" -ForegroundColor Gray
        Write-Host "  .\tools\organize_backfill_exports.ps1" -ForegroundColor Gray
    }
    exit 0
} else {
    Write-Warn "Some scripts failed. Check logs for details."
    exit 1
}

