Import-Module ImportExcel

$excelPath = "C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Detectives\detectives_monthly.xlsx"

$excel = Open-ExcelPackage -Path $excelPath

# Check _mom_det table
$momDetSheet = $excel.Workbook.Worksheets | Where-Object { $_.Tables.Name -contains "_mom_det" }
$momDetTable = $momDetSheet.Tables | Where-Object { $_.Name -eq "_mom_det" }

Write-Output "=== _mom_det TABLE HEADERS ==="
Write-Output "Table Range: $($momDetTable.Address)"
$startRow = $momDetTable.Address.Start.Row
$endCol = $momDetTable.Address.End.Column

for ($col = 1; $col -le $endCol; $col++) {
    $header = $momDetSheet.Cells[$startRow, $col].Value
    Write-Output "Column $col : $header"
}

Write-Output ""
Write-Output "=== _mom_det SAMPLE DATA (Row 2) ==="
for ($col = 1; $col -le [Math]::Min($endCol, 35); $col++) {
    $value = $momDetSheet.Cells[$startRow + 1, $col].Value
    $header = $momDetSheet.Cells[$startRow, $col].Value
    Write-Output "$header : $value"
}

Write-Output ""
Write-Output "=== _CCD_MOM TABLE HEADERS ==="
$ccdSheet = $excel.Workbook.Worksheets | Where-Object { $_.Tables.Name -contains "_CCD_MOM" }
$ccdTable = $ccdSheet.Tables | Where-Object { $_.Name -eq "_CCD_MOM" }
Write-Output "Table Range: $($ccdTable.Address)"
$startRow2 = $ccdTable.Address.Start.Row
$endCol2 = $ccdTable.Address.End.Column

for ($col = 1; $col -le $endCol2; $col++) {
    $header = $ccdSheet.Cells[$startRow2, $col].Value
    Write-Output "Column $col : $header"
}

Close-ExcelPackage $excel -NoSave
