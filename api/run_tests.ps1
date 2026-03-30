# Reads testresults_dir from pytest.ini and saves each test file's output there.
# To change the output folder, update testresults_dir in pytest.ini.

$config = Get-Content "pytest.ini" | Where-Object { $_ -match "testresults_dir" }
$resultsDir = ($config -split "=")[1].Trim()

New-Item -ItemType Directory -Force -Path $resultsDir | Out-Null

Get-ChildItem "tests/unit/test_*.py", "tests/integration/test_*.py" | ForEach-Object {
    $testFile = $_.FullName
    $baseName = $_.BaseName
    $category = Split-Path (Split-Path $testFile -Parent) -Leaf
    $outputFile = Join-Path $resultsDir "${category}_${baseName}.txt"

    Write-Host "Running [$category] $($_.Name) -> $outputFile"
    python -m pytest $testFile -v --tb=short 2>&1 | Tee-Object -FilePath $outputFile
}

Write-Host ""
Write-Host "All results saved to: $resultsDir"
