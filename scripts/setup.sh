#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> WasmBox setup"
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

mkdir -p artifacts wasmbox-data plugins/examples

if command -v docker >/dev/null 2>&1; then
  echo "==> Starting infra (postgres, prometheus, grafana)"
  docker compose up -d postgres prometheus grafana
else
  echo "Docker not found — skip infra. Install Docker for Postgres + observability."
fi

echo ""
echo "Done. Next:"
echo "  source .venv/bin/activate"
echo "  uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload"
echo "  cd frontend && npm install && npm run dev"
