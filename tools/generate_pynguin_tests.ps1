param(
    [int]$SearchTime = 10
)

$ErrorActionPreference = "Stop"
$repository = (Resolve-Path (Join-Path $PSScriptRoot ".." )).Path
$python = Join-Path $repository ".venv\Scripts\python.exe"
$pynguin = Join-Path $repository ".venv\Scripts\pynguin.exe"

if (-not (Test-Path $pynguin)) {
    throw "Pynguin is not installed in $repository\.venv"
}

$env:PYNGUIN_DANGER_AWARE = "true"
$env:PYTHONPATH = "$repository;$repository\openunderstand"

& $pynguin `
    --project-path $repository `
    --module-name openunderstand.oudb.models `
    --output-path (Join-Path $repository "artifacts\pynguin-raw") `
    --report-dir (Join-Path $repository "artifacts\pynguin-report") `
    --maximum-search-time $SearchTime `
    --maximum-test-executions 500 `
    --maximum-test-execution-timeout 1 `
    --seed 403131043 `
    --assertion-generation NONE `
    --no-xfail true `
    --subprocess false `
    --subprocess-if-recommended false `
    --use-master-worker false `
    --format-with-black true

if ($LASTEXITCODE -ne 0) {
    throw "Pynguin exited with code $LASTEXITCODE"
}
