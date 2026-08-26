$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "==> WasmBox setup"
python -m venv .venv
& "$Root\.venv\Scripts\Activate.ps1"
python -m pip install -U pip
pip install -r requirements.txt

New-Item -ItemType Directory -Force -Path artifacts, wasmbox-data, plugins\examples | Out-Null

if (Get-Command docker -ErrorAction SilentlyContinue) {
  Write-Host "==> Starting infra (postgres, prometheus, grafana)"
  docker compose up -d postgres prometheus grafana
} else {
  Write-Host "Docker not found - skipping optional infrastructure."
}

Write-Host ""
Write-Host "Done. Next:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload"
Write-Host "  cd frontend; npm install; npm run dev"
