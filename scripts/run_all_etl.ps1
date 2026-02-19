# Master ETL Orchestrator
# Runs all configured Python ETL scripts in order

param(
    [string[]]$ScriptNames = @(),  # Run only specified scripts (empty = all)
    [switch]$DryRun,  # Preview what would run
    [switch]$SkipPowerBI,  # Skip Power BI integration step
    [switch]$ValidateInputs  # Validate required input files exist
)

$ErrorActionPreference = 'Stop'

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$automationDir = Split-Path -Parent $scriptDir
$configPath = Join-Path $automationDir "config\scripts.json"

# OneDrive base for paths (align with Python path_config; enables portability)
$OneDriveBase = $env:ONEDRIVE_BASE
if (-not $OneDriveBase) { $OneDriveBase = $env:ONEDRIVE_HACKENSACK }
if (-not $OneDriveBase) { $OneDriveBase = "C:\Users\carucci_r\OneDrive - City of Hackensack" }

# Colors
# PowerShell 7+ supports ANSI escape sequences; Windows PowerShell 5.1 typically does not.
$useAnsi = $false
try {
    $useAnsi = ($PSVersionTable.PSVersion.Major -ge 7) -and ($Host.UI -and $Host.UI.SupportsVirtualTerminal)
}
catch { $useAnsi = $false }

if ($useAnsi) {
    $Green = "`e[32m"
    $Yellow = "`e[33m"
    $Red = "`e[31m"
    $Cyan = "`e[34m"
    $Reset = "`e[0m"
}
else {
    $Green = ""
    $Yellow = ""
    $Red = ""
    $Cyan = ""
    $Reset = ""
}

function Write-Step([string]$msg) { Write-Host "$Cyan>> $msg$Reset" }
function Write-Success([string]$msg) { Write-Host "$Green[OK] $msg$Reset" }
function Write-Warn([string]$msg) { Write-Host "$Yellow[WARN] $msg$Reset" }
function Write-Fail([string]$msg) { Write-Host "$Red[FAIL] $msg$Reset" }

function Save-MonthlyReport {
    <#
    .SYNOPSIS
    Saves a copy of the monthly Power BI report to the correct directory structure.
    #>
    
    # Calculate previous month (subtract 1 calendar month from current date)
    $now = Get-Date
    $prevMonth = $now.AddMonths(-1)
    $year = $prevMonth.Year
    $monthNum = $prevMonth.Month.ToString("00")
    $monthName = $prevMonth.ToString("MMMM")
    $monthNameLower = $monthName.ToLower()
    
    # Format: YYYY_MM_Monthly_Report.pbix (e.g., 2025_12_Monthly_Report.pbix for December 2025)
    $reportFileName = "${year}_${monthNum}_Monthly_Report.pbix"
    
    # Base paths (use OneDrive base for portability)
    $templatesDir = Join-Path $OneDriveBase "15_Templates"
    $monthlyReportsBase = Join-Path $OneDriveBase "Shared Folder\Compstat\Monthly Reports"
    
    # Target directory: YEAR\MONTH_NUMBER_monthname (e.g., 2025\12_december)
    $targetDir = Join-Path $monthlyReportsBase $year
    $targetDir = Join-Path $targetDir "${monthNum}_${monthNameLower}"
    
    # Find source template/report file
    $sourceFile = $null
    
    # First, check if there's a template in 15_Templates
    # Prioritize files with "Template" in the name
    $templateFiles = Get-ChildItem -Path $templatesDir -Filter "*.pbix" -ErrorAction SilentlyContinue
    if ($templateFiles) {
        # Look for files with "Template" in the name first
        $templateNamed = $templateFiles | Where-Object { $_.Name -like "*Template*" }
        if ($templateNamed) {
            # Use the most recent template-named file
            $sourceFile = $templateNamed | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            Write-Log "Found template file: $($sourceFile.FullName)"
        }
        else {
            # Fall back to most recent file in Templates folder
            $sourceFile = $templateFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            Write-Log "Found template file: $($sourceFile.FullName)"
        }
    }
    
    # If no template found, look for the most recent report in Monthly Reports
    if (-not $sourceFile) {
        $existingReports = Get-ChildItem -Path $monthlyReportsBase -Filter "*.pbix" -Recurse -ErrorAction SilentlyContinue
        if ($existingReports) {
            $sourceFile = $existingReports | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            Write-Log "Found existing report file: $($sourceFile.FullName)"
        }
    }
    
    if (-not $sourceFile) {
        Write-Warn "No template or existing report found. Skipping monthly report save."
        Write-Log "WARNING: No template or existing report found. Expected locations:"
        Write-Log "  - Template: $templatesDir\*.pbix"
        Write-Log "  - Existing report: $monthlyReportsBase\**\*.pbix"
        return
    }
    
    try {
        # Create target directory if it doesn't exist
        if (-not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            Write-Log "Created directory: $targetDir"
        }
        
        # Copy to monthly reports directory
        $targetFile = Join-Path $targetDir $reportFileName
        Copy-Item -Path $sourceFile.FullName -Destination $targetFile -Force
        Write-Success "Saved monthly report: $targetFile"
        Write-Log "Copied report to: $targetFile"
        
        Write-Host ""
        Write-Host "Monthly Report Saved:" -ForegroundColor Cyan
        Write-Host "  Report: $targetFile" -ForegroundColor Gray
        Write-Host "  Source: $($sourceFile.FullName)" -ForegroundColor Gray
        
    }
    catch {
        Write-Fail "Error saving monthly report: $_"
        Write-Log "ERROR saving monthly report: $_"
    }
}

function Test-RequiredInputs {
    <#
    .SYNOPSIS
    Validates that required input files exist for each ETL script.
    #>
    param(
        [object]$ScriptConfig
    )
    
    $scriptName = $ScriptConfig.name
    $validationResults = @()
    $allValid = $true
    
    # Calculate previous month (rolling window typically ends on previous month)
    $now = Get-Date
    $prevMonth = $now.AddMonths(-1)
    $year = $prevMonth.Year
    $month = $prevMonth.Month.ToString("00")
    
    Write-Step "Validating input files for: $scriptName"
    
    switch ($scriptName) {
        "Summons" {
            # Format: YYYY/YYYY_MM_eticket_export.csv OR YYYY/month/YYYY_MM_eticket_export.csv
            $eticketBase = Join-Path $OneDriveBase "05_EXPORTS\_Summons\E_Ticket"
            
            # Try direct path first (e.g., 2026/2026_01_eticket_export.csv)
            $eticketPath = Join-Path $eticketBase "$year\$($year)_$($month)_eticket_export.csv"
            
            if (Test-Path $eticketPath) {
                Write-Success "  E-ticket export found: $eticketPath"
                $validationResults += [pscustomobject]@{ File = "E-ticket Export"; Path = $eticketPath; Status = "Found" }
            }
            else {
                # Try month subfolder path (e.g., 2026/month/2026_01_eticket_export.csv)
                $eticketPath = Join-Path $eticketBase "$year\month\$($year)_$($month)_eticket_export.csv"
                
                if (Test-Path $eticketPath) {
                    Write-Success "  E-ticket export found: $eticketPath"
                    $validationResults += [pscustomobject]@{ File = "E-ticket Export"; Path = $eticketPath; Status = "Found" }
                }
                else {
                    Write-Fail "  E-ticket export NOT found"
                    Write-Host "    Checked: $eticketBase\$year\$($year)_$($month)_eticket_export.csv" -ForegroundColor Gray
                    Write-Host "    Checked: $eticketBase\$year\month\$($year)_$($month)_eticket_export.csv" -ForegroundColor Gray
                    $validationResults += [pscustomobject]@{ File = "E-ticket Export"; Path = "Multiple paths checked"; Status = "Missing" }
                    $allValid = $false
                    
                    # Check if directory exists and list available files
                    $yearDir = Join-Path $eticketBase $year
                    if (Test-Path $yearDir) {
                        $availableFiles = Get-ChildItem -Path $yearDir -Filter "*.csv" -Recurse -ErrorAction SilentlyContinue
                        if ($availableFiles) {
                            Write-Warn "    Available files in ${yearDir}:"
                            foreach ($file in $availableFiles) {
                                $relativePath = $file.FullName.Replace($yearDir, "").TrimStart('\')
                                Write-Host "      - $relativePath" -ForegroundColor Gray
                            }
                        }
                    }
                    else {
                        Write-Warn "    Year directory not found: ${yearDir}"
                    }
                }
            }
        }
        
        "Response Times" {
            # NOTE: Source moved to timereport folder (2026-02-09)
            # Current structure: timereport/monthly/YYYY_MM_timereport.xlsx
            # Fallback: timereport/YYYY/YYYY_MM_Monthly_CAD.xlsx
            $cadBase = Join-Path $OneDriveBase "05_EXPORTS\_CAD\timereport"
            
            # Try monthly folder first (preferred structure)
            $monthlyFolder = Join-Path $cadBase "monthly"
            $cadPath = Join-Path $monthlyFolder "$($year)_$($month)_timereport.xlsx"
            
            if (Test-Path $cadPath) {
                Write-Success "  CAD timereport export found: $cadPath"
                $validationResults += [pscustomobject]@{ File = "CAD Timereport Export"; Path = $cadPath; Status = "Found" }
            }
            else {
                # Fallback: Try year-based structure
                $cadPath = Join-Path $cadBase "$year\$($year)_$($month)_Monthly_CAD.xlsx"
                
                if (Test-Path $cadPath) {
                    Write-Success "  CAD timereport export found: $cadPath"
                    $validationResults += [pscustomobject]@{ File = "CAD Timereport Export"; Path = $cadPath; Status = "Found" }
                }
                else {
                    Write-Fail "  CAD timereport export NOT found"
                    Write-Host "    Checked: $monthlyFolder\$($year)_$($month)_timereport.xlsx" -ForegroundColor Gray
                    Write-Host "    Checked: $cadBase\$year\$($year)_$($month)_Monthly_CAD.xlsx" -ForegroundColor Gray
                    $validationResults += [pscustomobject]@{ File = "CAD Timereport Export"; Path = "Multiple paths checked"; Status = "Missing" }
                    $allValid = $false
                    
                    # List available files in monthly folder
                    if (Test-Path $monthlyFolder) {
                        $availableFiles = Get-ChildItem -Path $monthlyFolder -Filter "*timereport.xlsx" -ErrorAction SilentlyContinue
                        if ($availableFiles) {
                            Write-Warn "    Available files in monthly folder:"
                            foreach ($file in $availableFiles) {
                                Write-Host "      - $($file.Name)" -ForegroundColor Gray
                            }
                        }
                    }
                }
            }
        }
        
        "Response Times Monthly Generator" {
            # Alias case - same validation as "Response Times"
            # NOTE: Source moved to timereport folder (2026-02-09)
            # Current structure: timereport/monthly/YYYY_MM_timereport.xlsx
            # Fallback: timereport/YYYY/YYYY_MM_Monthly_CAD.xlsx
            $cadBase = Join-Path $OneDriveBase "05_EXPORTS\_CAD\timereport"
            
            # Try monthly folder first (preferred structure)
            $monthlyFolder = Join-Path $cadBase "monthly"
            $cadPath = Join-Path $monthlyFolder "$($year)_$($month)_timereport.xlsx"
            
            if (Test-Path $cadPath) {
                Write-Success "  CAD timereport export found: $cadPath"
                $validationResults += [pscustomobject]@{ File = "CAD Timereport Export"; Path = $cadPath; Status = "Found" }
            }
            else {
                # Fallback: Try year-based structure
                $cadPath = Join-Path $cadBase "$year\$($year)_$($month)_Monthly_CAD.xlsx"
                
                if (Test-Path $cadPath) {
                    Write-Success "  CAD timereport export found: $cadPath"
                    $validationResults += [pscustomobject]@{ File = "CAD Timereport Export"; Path = $cadPath; Status = "Found" }
                }
                else {
                    Write-Fail "  CAD timereport export NOT found"
                    Write-Host "    Checked: $monthlyFolder\$($year)_$($month)_timereport.xlsx" -ForegroundColor Gray
                    Write-Host "    Checked: $cadBase\$year\$($year)_$($month)_Monthly_CAD.xlsx" -ForegroundColor Gray
                    $validationResults += [pscustomobject]@{ File = "CAD Timereport Export"; Path = "Multiple paths checked"; Status = "Missing" }
                    $allValid = $false
                    
                    # List available files in monthly folder
                    if (Test-Path $monthlyFolder) {
                        $availableFiles = Get-ChildItem -Path $monthlyFolder -Filter "*timereport.xlsx" -ErrorAction SilentlyContinue
                        if ($availableFiles) {
                            Write-Warn "    Available files in monthly folder:"
                            foreach ($file in $availableFiles) {
                                Write-Host "      - $($file.Name)" -ForegroundColor Gray
                            }
                        }
                    }
                }
            }
        }
        
        "Overtime TimeOff" {
            # Check for VCS time report exports (if known location)
            $vcsBase = Join-Path $OneDriveBase "05_EXPORTS"
            $vcsPath = Join-Path $vcsBase "_VCS_Time_Report"
            
            if (Test-Path $vcsPath) {
                Write-Success "  VCS Time Report export directory found: $vcsPath"
                $validationResults += [pscustomobject]@{ File = "VCS Time Report Directory"; Path = $vcsPath; Status = "Found" }
            }
            else {
                Write-Warn "  VCS Time Report export directory not found: $vcsPath (may use different location)"
                $validationResults += [pscustomobject]@{ File = "VCS Time Report Directory"; Path = $vcsPath; Status = "Unknown" }
            }
        }
        
        "Arrests" {
            # Arrests script may have specific input requirements - add if known
            Write-Host "  No specific input file validation configured for Arrests" -ForegroundColor Gray
            $validationResults += [pscustomobject]@{ File = "Arrest Data"; Path = "Unknown"; Status = "Not Validated" }
        }
        
        "Community Engagement" {
            # Community Engagement may have specific input requirements - add if known
            Write-Host "  No specific input file validation configured for Community Engagement" -ForegroundColor Gray
            $validationResults += [pscustomobject]@{ File = "Community Engagement Data"; Path = "Unknown"; Status = "Not Validated" }
        }
        
        default {
            Write-Host "  No input validation configured for: $scriptName" -ForegroundColor Gray
            $validationResults += [pscustomobject]@{ File = "Input Files"; Path = "Unknown"; Status = "Not Validated" }
        }
    }
    
    return @{
        ScriptName = $scriptName
        AllValid   = $allValid
        Results    = $validationResults
    }
}

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

# Validate input files if requested
if ($ValidateInputs -or $DryRun) {
    Write-Log ""
    Write-Log "=== Input File Validation ==="
    Write-Host ""
    Write-Host "=== Input File Validation ===" -ForegroundColor Cyan
    Write-Host ""
    
    $validationSummary = @()
    $allInputsValid = $true
    
    foreach ($scriptConfig in $scripts) {
        $validation = Test-RequiredInputs -ScriptConfig $scriptConfig
        $validationSummary += $validation
        
        if (-not $validation.AllValid) {
            $allInputsValid = $false
        }
        Write-Host ""
    }
    
    Write-Host "=== Validation Summary ===" -ForegroundColor Cyan
    Write-Log "=== Validation Summary ==="
    
    foreach ($validation in $validationSummary) {
        if ($validation.AllValid) {
            Write-Success "$($validation.ScriptName): All required inputs found"
            Write-Log "$($validation.ScriptName): All required inputs found"
        }
        else {
            Write-Fail "$($validation.ScriptName): Missing required inputs"
            Write-Log "$($validation.ScriptName): Missing required inputs"
            foreach ($result in $validation.Results) {
                if ($result.Status -eq "Missing") {
                    Write-Log "  MISSING: $($result.File) - $($result.Path)"
                }
            }
        }
    }
    
    Write-Host ""
    
    if (-not $allInputsValid) {
        Write-Fail "Some required input files are missing!"
        Write-Log "Validation failed: Some required input files are missing"
        if (-not $DryRun) {
            Write-Host ""
            Write-Host "You can still proceed, but scripts may fail if inputs are missing." -ForegroundColor Yellow
            $response = Read-Host "Continue anyway? (y/N)"
            if ($response -ne "y" -and $response -ne "Y") {
                Write-Host "Exiting..." -ForegroundColor Yellow
                exit 1
            }
        }
        else {
            Write-Warn "Dry run mode: Fix missing files before running actual ETL"
        }
    }
    else {
        Write-Success "All required input files validated!"
        Write-Log "Validation passed: All required input files found"
    }
    
    Write-Host ""
    Write-Log ""
    
    # If only validation was requested (without dry run), exit here
    if ($ValidateInputs -and -not $DryRun) {
        Write-Host "Validation complete. Use -DryRun to also preview script execution." -ForegroundColor Cyan
        exit 0
    }
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
        $results += [pscustomobject]@{
            Name     = $scriptName
            Status   = "Failed"
            Error    = "Script file not found"
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
        
        # Run Python script (cross-version reliable exit codes + stdout/stderr capture)
        $pythonCmd = $settings.python_executable
        $timeoutSeconds = [int]($scriptConfig.timeout_minutes * 60)

        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $pythonCmd
        
        # Handle script arguments if specified
        $scriptArgs = ""
        if ($scriptConfig.args) {
            $scriptArgs = $scriptConfig.args
            # Replace {REPORT_MONTH} token with calculated month
            $reportMonth = "$year-$monthNum"
            $scriptArgs = $scriptArgs -replace '\{REPORT_MONTH\}', $reportMonth
            $psi.Arguments = "`"$scriptFile`" $scriptArgs"
        } else {
            $psi.Arguments = $scriptFile
        }
        
        $psi.WorkingDirectory = $scriptPath
        $psi.UseShellExecute = $false
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $psi.CreateNoWindow = $true

        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $psi

        $null = $process.Start()
        $stdoutTask = $process.StandardOutput.ReadToEndAsync()
        $stderrTask = $process.StandardError.ReadToEndAsync()

        if (-not $process.WaitForExit($timeoutSeconds * 1000)) {
            try { $process.Kill() } catch {}
            throw "Script exceeded timeout of $($scriptConfig.timeout_minutes) minutes"
        }
        $process.WaitForExit()

        # Write logs after completion
        $stdoutTask.Result | Out-File -FilePath $scriptLogFile -Encoding utf8
        $stderrTask.Result | Out-File -FilePath "$scriptLogFile.err" -Encoding utf8

        $scriptDuration = (Get-Date) - $scriptStartTime
        $exitCode = $process.ExitCode
        if ($exitCode -eq 0) {
            Write-Success "  Completed in $([math]::Round($scriptDuration.TotalSeconds, 2)) seconds"
            Write-Log "  SUCCESS: Exit code 0"
            
            # Find output files
            # Supports:
            # - Simple patterns like "*.csv" (searched in script root)
            # - Relative subpaths like "output\FIXED_*.csv" (joined to script root)
            $outputFiles = @()
            foreach ($pattern in $scriptConfig.output_patterns) {
                if ([string]::IsNullOrWhiteSpace($pattern)) { continue }

                $isAbsolute = ($pattern -match '^[A-Za-z]:\\' -or $pattern -match '^\\\\')
                $hasSeparator = ($pattern -like "*\*" -or $pattern -like "*/*")

                if ($isAbsolute) {
                    $globPath = $pattern
                    $found = Get-ChildItem -Path $globPath -File -ErrorAction SilentlyContinue
                }
                elseif ($hasSeparator) {
                    $globPath = Join-Path $scriptPath $pattern
                    $found = Get-ChildItem -Path $globPath -File -ErrorAction SilentlyContinue
                }
                else {
                    $found = Get-ChildItem -Path $scriptPath -Filter $pattern -File -ErrorAction SilentlyContinue
                }

                if ($found) { $outputFiles += $found }
            }
            
            Write-Log "  Output files found: $($outputFiles.Count)"
            
            # Copy to Power BI drop folder if enabled
            if ($scriptConfig.output_to_powerbi -and -not $SkipPowerBI) {
                $dropPath = $settings.powerbi_drop_path
                if (-not (Test-Path $dropPath)) {
                    Write-Warn "  Power BI drop folder not found: $dropPath"
                    Write-Log "  WARNING: Power BI drop folder not found"
                }
                else {
                    foreach ($file in $outputFiles) {
                        $destPath = Join-Path $dropPath $file.Name
                        Copy-Item -Path $file.FullName -Destination $destPath -Force
                        Write-Log "  Copied to Power BI: $($file.Name)"
                    }
                    Write-Success "  Copied $($outputFiles.Count) file(s) to Power BI drop folder"
                }
            }
            
            $results += [pscustomobject]@{
                Name        = $scriptName
                Status      = "Success"
                Error       = $null
                Duration    = $scriptDuration.TotalSeconds
                OutputFiles = $outputFiles.Count
            }
        }
        else {
            throw "Script exited with code $exitCode"
        }
        
    }
    catch {
        $scriptDuration = (Get-Date) - $scriptStartTime
        Write-Fail "  Error: $_"
        Write-Log "  ERROR: $_"
        
        $results += [pscustomobject]@{
            Name     = $scriptName
            Status   = "Failed"
            Error    = $_.Exception.Message
            Duration = $scriptDuration.TotalSeconds
        }
        
        if (-not $settings.continue_on_error) {
            Write-Fail "Stopping due to error (continue_on_error = false)"
            break
        }
    }
    finally {
        Pop-Location
    }
}

# Visual Export Normalization – normalize raw Power BI visual exports in _DropExports before organize_backfill_exports
$dropPath = $settings.powerbi_drop_path
$normalizeScript = Join-Path $automationDir "scripts\normalize_visual_export_for_backfill.py"
$monthlyAccrualPattern = "*Monthly Accrual and Usage Summary*.csv"

if (Test-Path $dropPath) {
    Write-Log ""
    Write-Log "=== Visual Export Normalization ==="
    Write-Host ""
    Write-Step "Visual Export Normalization"
    $toNormalize = Get-ChildItem -Path $dropPath -Filter $monthlyAccrualPattern -File -ErrorAction SilentlyContinue
    if ($toNormalize.Count -eq 0) {
        Write-Host "  No files matching '$monthlyAccrualPattern' in $dropPath" -ForegroundColor Gray
        Write-Log "  No Monthly Accrual and Usage Summary CSVs found in drop folder"
    }
    else {
        foreach ($file in $toNormalize) {
            if ($DryRun) {
                Write-Host "  [DRY RUN] Would normalize: $($file.Name)" -ForegroundColor Gray
                Write-Log "  [DRY RUN] Would normalize: $($file.FullName)"
                continue
            }
            Write-Log "  Normalizing: $($file.FullName)"
            Write-Host "  Normalizing: $($file.Name)" -ForegroundColor Gray
            $normInput = $file.FullName
            $normOutput = $file.FullName
            try {
                $psiNorm = New-Object System.Diagnostics.ProcessStartInfo
                $psiNorm.FileName = $settings.python_executable
                $psiNorm.Arguments = "`"$normalizeScript`" --input `"$normInput`" --output `"$normOutput`""
                $psiNorm.WorkingDirectory = $automationDir
                $psiNorm.UseShellExecute = $false
                $psiNorm.RedirectStandardOutput = $true
                $psiNorm.RedirectStandardError = $true
                $psiNorm.CreateNoWindow = $true
                $procNorm = New-Object System.Diagnostics.Process
                $procNorm.StartInfo = $psiNorm
                $null = $procNorm.Start()
                $null = $procNorm.StandardOutput.ReadToEndAsync()
                $errNorm = $procNorm.StandardError.ReadToEndAsync()
                $procNorm.WaitForExit(60000)
                $exitNorm = $procNorm.ExitCode
                if ($exitNorm -eq 0) {
                    Write-Success "  Normalized: $($file.Name)"
                    Write-Log "  SUCCESS: Normalized $($file.Name)"
                }
                else {
                    Write-Warn "  Normalization failed for $($file.Name) (exit $exitNorm). Continuing."
                    Write-Log "  WARNING: Normalization failed for $($file.Name) - exit code $exitNorm"
                    if ($errNorm.Result) { Write-Log "  stderr: $($errNorm.Result.Trim())" }
                }
            }
            catch {
                Write-Warn "  Error normalizing $($file.Name): $_"
                Write-Log "  ERROR normalizing $($file.Name): $_"
            }
        }
    }
}
else {
    Write-Log "  Power BI drop path not found; skipping Visual Export Normalization: $dropPath"
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
    }
    else {
        Write-Fail "$($result.Name): Failed - $($result.Error)"
    }
}

Write-Log "=== Master ETL Orchestrator Completed ==="
Write-Host ""
Write-Host "Full log: $logFile" -ForegroundColor Gray

# Save monthly report copy (always attempt, regardless of script results)
Write-Log ""
Write-Log "=== Saving Monthly Report ==="
Write-Host ""
Write-Host "=== Saving Monthly Report ===" -ForegroundColor Cyan
Save-MonthlyReport

if ($successCount -eq $results.Count) {
    Write-Success "All scripts completed successfully!"
    
    if (-not $SkipPowerBI) {
        Write-Host ""
        Write-Host "Next step: Run Power BI organization script" -ForegroundColor Cyan
        Write-Host "  cd `"$OneDriveBase\PowerBI_Date`"" -ForegroundColor Gray
        Write-Host "  .\tools\organize_backfill_exports.ps1" -ForegroundColor Gray
    }
    exit 0
}
else {
    Write-Warn "Some scripts failed. Check logs for details."
    exit 1
}

