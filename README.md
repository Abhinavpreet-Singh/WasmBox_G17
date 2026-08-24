# WasmBox

**Axlero Solutions · G17 · Secure Multi-Tenant Plugin Sandbox**

Browser IDE → static AST guard → Python compiled to WASM → Wasmtime execution with hard limits → audit log, webhooks, and Security Lab.

---

## What it does

WasmBox lets SaaS customers write **Python plugins** in a Monaco editor. The backend never runs raw Python with `exec()`. Instead it **validates**, **compiles to WebAssembly** (Extism toolchain in Docker), and **executes in Wasmtime** with memory and CPU caps. Only **whitelisted host functions** (e.g. safe DB bridge) cross the sandbox boundary.

```
Monaco → POST /api/compile → AST guard → Docker compile → .wasm artifact
       → POST /api/run → Wasmtime → WebSocket stdout → React dashboard
       → POST /hooks/{id} → HMAC webhook trigger
```

---

## What makes it unique

- **Security Lab** — curated attacks with denial reasons (AST vs runtime vs capability)
- **Capability matrix** — stdio only → host DB bridge → webhook; visible per plugin
- **Compile vs run waterfall** — timing breakdown on every execution
- **Bytecode fingerprint** — SHA-256 of `.wasm` in audit log; version rollback
- **Multi-tenant demo** — `tenant_a` / `tenant_b` namespaces with quotas
- **StreamForge-style ops UI** — Overview, Playground, Plugins, Security Lab, Operations, Metrics

---

## Quick start

```powershell
cd wasmbox
.\scripts\setup.ps1
.\.venv\Scripts\Activate.ps1
uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload
```

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5174**. API health: **http://localhost:8001/health**.

Optional infra:

```bash
docker compose up -d postgres prometheus grafana
```

---

## Ports

| Service | Port |
| --- | --- |
| API | 8001 |
| Vite | 5174 |
| PostgreSQL | 5433 |
| Prometheus | 9091 |
| Grafana | 3002 (admin / admin) |

StreamForge uses different ports — both projects can run together in the monorepo.

---

## Compile toolchain

Python→WASM uses **extism-py** inside Docker (Week 2+):

```bash
docker compose build compiler
docker compose --profile compile run --rm -v ${PWD}/plugins/examples:/work compiler compile /work/hello_plugin.py -o /artifacts/hello.wasm
```

---

## Docs

- **[WasmBox-PROJECT.md](WasmBox-PROJECT.md)** — full 4-week daily plan, DoD, demo script
- **[docs/architecture.md](docs/architecture.md)** — system design
- **[docs/security-model.md](docs/security-model.md)** — threat model
- **[frontend/STRUCTURE.md](frontend/STRUCTURE.md)** — React layout

---

## Monorepo

This folder lives beside **[../streamforge/](../streamforge/)** (Month 1 — Kafka/Faust streaming). Same team, different domain: **security & WASM** instead of distributed events.

---

## Tests

```bash
pytest tests/ -v
```

`test_api_smoke.py` requires the API on `:8001` (skipped if not running).
