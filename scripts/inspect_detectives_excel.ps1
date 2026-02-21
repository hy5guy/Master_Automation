Import-Module ImportExcel

$excelPath = "C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Detectives\detectives_monthly.xlsx"

Write-Output "=== INSPECTING EXCEL FILE ==="
Write-Output "File: $excelPath"
Write-Output ""

$excel = Open-ExcelPackage -Path $excelPath

Write-Output "=== WORKSHEETS ==="
$excel.Workbook.Worksheets | ForEach-Object {
    Write-Output "Sheet: $($_.Name)"
}
Write-Output ""

Write-Output "=== TABLES IN WORKBOOK ==="
$excel.Workbook.Worksheets | ForEach-Object {
    $sheet = $_
    if ($sheet.Tables.Count -gt 0) {
        $sheet.Tables | ForEach-Object {
            Write-Output "Sheet: $($sheet.Name) | Table: $($_.Name) | Range: $($_.Address)"
        }
    }
}
Write-Output ""

# Check the _mom_det table specifically
Write-Output "=== CHECKING _mom_det TABLE ==="
$momDetSheet = $excel.Workbook.Worksheets | Where-Object { $_.Tables.Name -contains "_mom_det" }
if ($momDetSheet) {
    $momDetTable = $momDetSheet.Tables | Where-Object { $_.Name -eq "_mom_det" }
    Write-Output "Table Found: $($momDetTable.Name)"
    Write-Output "Address: $($momDetTable.Address)"
    
    # Get column headers
    $startRow = $momDetTable.Address.Start.Row
    $endCol = $momDetTable.Address.End.Column
    
    Write-Output "`nColumn Headers:"
    for ($col = 1; $col -le $endCol; $col++) {
        $header = $momDetSheet.Cells[$startRow, $col].Value
        Write-Output "  Column $col`: $header"
    }
    
    # Get first few data rows
    Write-Output "`nFirst 3 data rows:"
    for ($row = $startRow + 1; $row -le [Math]::Min($startRow + 3, $momDetTable.Address.End.Row); $row++) {
        $rowData = @()
        for ($col = 1; $col -le $endCol; $col++) {
            $rowData += $momDetSheet.Cells[$row, $col].Value
        }
        Write-Output "  Row $row`: $($rowData -join ' | ')"
    }
}

Close-ExcelPackage $excel -NoSave

Write-Output ""
Write-Output "=== INSPECTION COMPLETE ==="
