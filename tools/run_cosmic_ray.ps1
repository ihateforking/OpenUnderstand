$ErrorActionPreference = "Stop"
$repository = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$cosmicRay = Join-Path $repository ".venv\Scripts\cosmic-ray.exe"
$cosmicRayReport = Join-Path $repository ".venv\Scripts\cr-report.exe"
$cosmicRayRate = Join-Path $repository ".venv\Scripts\cr-rate.exe"
$config = Join-Path $repository "cosmic-ray.toml"
$session = Join-Path $repository "cosmic-ray-session.sqlite"
$baselineSession = Join-Path $repository "cosmic-ray-baseline.sqlite"

if (-not (Test-Path $cosmicRay) -or -not (Test-Path $cosmicRayReport) -or -not (Test-Path $cosmicRayRate)) {
    throw "Cosmic Ray is not installed in $repository\.venv"
}

Push-Location $repository
try {
    & $cosmicRay baseline --session-file $baselineSession $config
    & $cosmicRay init --force $config $session
    & $cosmicRay exec $config $session
    & $cosmicRayReport --show-diff $session
    & $cosmicRayRate $session
}
finally {
    Pop-Location
}

if ($LASTEXITCODE -ne 0) {
    throw "Cosmic Ray exited with code $LASTEXITCODE"
}
