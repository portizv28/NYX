[CmdletBinding()]
param(
    [ValidateSet("Core", "Full")]
    [string]$Profile = "Full",
    [switch]$Dev
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $ProjectRoot ".venv"

if (-not (Test-Path $VenvPath)) {
    py -3 -m venv $VenvPath
}

$Python = Join-Path $VenvPath "Scripts\\python.exe"
& $Python -m pip install --upgrade pip

if ($Profile -eq "Core") {
    & $Python -m pip install -r (Join-Path $ProjectRoot "requirements\\base.txt")
} else {
    & $Python -m pip install -r (Join-Path $ProjectRoot "requirements.txt")
}

if ($Dev) {
    & $Python -m pip install -r (Join-Path $ProjectRoot "requirements\\dev.txt")
}

if (-not (Test-Path (Join-Path $ProjectRoot ".env"))) {
    Copy-Item (Join-Path $ProjectRoot ".env.example") (Join-Path $ProjectRoot ".env")
    Write-Host "Se ha creado .env. Revísalo antes de iniciar NYX."
}

Write-Host "NYX está preparado. Ejecuta: $Python main.py"
