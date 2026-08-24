# WasmBox — Secure Multi-Tenant Plugin Sandbox

**Axlero Solutions Intern Project · Team of 6 · Month 2 (Project 2 of 2)**
Domain: Security & WebAssembly — Wasmtime + Extism + FastAPI + React + Monaco.

SaaS customers need custom data parsers and webhook transformers. Running their Python with `exec()` or spinning a Docker container per plugin is either unsafe or too slow. WasmBox compiles restricted user Python to **WebAssembly**, executes it in **Wasmtime** with hard memory and CPU caps, and exposes only **whitelisted host functions** (safe DB bridge, verified webhook ingress). A browser **Monaco IDE** and **Security Lab** make the sandbox story visible to reviewers in real time.

**We never run raw customer Python on the host.** Flow: static AST guard → compile (Dockerized Extism toolchain) → WASM artifact → Wasmtime sandbox → audit log.

---

## 1. Problem & use case

| Pain | WasmBox answer |
| --- | --- |
| `exec(user_code)` on the server | Forbidden — WASM bytecode only |
| Docker per tenant plugin | One shared runtime; isolation via capabilities + tenant namespaces |
| No proof attacks fail | Security Lab runs curated attacks with denial reasons |
| Black-box executions | Compile vs run waterfall, SHA-256 WASM fingerprint, Prometheus metrics |

**Demo narrative:** A logistics SaaS lets customers write a JSON row formatter in the browser → WasmBox compiles → runs in &lt;5 ms → webhook fires on inbound HTTP POST → malicious `while True` dies in milliseconds with a visible timeout counter.

---

## 2. Architecture

```mermaid
flowchart TB
  subgraph ui [React_Dashboard]
    Monaco[Monaco_Editor]
    Overview[Overview]
    Playground[Playground]
    Plugins[Plugins]
    SecurityLab[Security_Lab]
    Operations[Operations]
    Metrics[Metrics]
  end

  subgraph api [FastAPI_8001]
    Health[/health]
    Compile[POST_api_compile]
    Run[POST_api_run]
    PluginCRUD[api_plugins]
    Hooks[hooks_plugin_id]
    WS[/ws_executions]
    PromMetrics[/metrics]
  end

  subgraph sandbox [Sandbox]
    AST[ast_guard]
    CompilerClient[compiler_client_Docker]
    Runtime[wasmtime_runtime]
    Caps[capabilities]
    HostFn[host_functions]
  end

  subgraph persist [Data_Obs]
    SQLite[(SQLite_Week1_2)]
    Postgres[(Postgres_Week3_4)]
    Redis[(Redis_optional)]
    Prometheus[Prometheus_9091]
    Grafana[Grafana_3002]
  end

  Monaco --> Compile
  Monaco --> Run
  Compile --> AST --> CompilerClient
  Run --> Runtime
  Runtime --> Caps
  Runtime --> HostFn
  Run --> SQLite
  PluginCRUD --> Postgres
  Hooks --> Run
  Runtime --> WS
  api --> Prometheus
  Grafana --> Prometheus
```

### Data flow (happy path)

```
User edits Python in Monaco
  → POST /api/compile (AST guard, Docker extism-py compile, store .wasm + SHA-256)
  → POST /api/run (Wasmtime + limits, optional host db_query)
  → WebSocket stdout chunks + Execution row (duration_ms, status, fingerprint)
  → Overview / Operations tables update
```

---

## 3. Tech stack

| Layer | Technology | Role |
| --- | --- | --- |
| API | FastAPI + uvicorn | REST, OpenAPI, WebSocket, CORS for Vite |
| WASM runtime | wasmtime-py | Memory limits, fuel/epoch timeout, WASI stdio |
| Plugin model | Extism Python PDK | Real Python → `.wasm`; host function bridge |
| Compile | extism-py in Docker (`wasmbox-compiler`) | Reproducible builds; no Windows LLVM on host |
| Static guard | Custom AST walker + bandit patterns | Block `open`, `os`, `socket`, `subprocess`, `import *` |
| DB | SQLite → PostgreSQL | Plugins, versions, executions, tenants |
| Queue (P1) | Redis | Async webhook execution (Week 4) |
| Metrics | prometheus-client + Grafana | `wasmbox_*` counters; embed in Metrics page |
| Frontend | React 19, Vite 8, Tailwind 4, Lucide | StreamForge-style shell (no react-router) |
| Editor | @monaco-editor/react | Browser IDE; lint API hook in Week 2+ |
| Tests | pytest + httpx | Smoke, AST guard, sandbox security suite |

**Theme:** CSS variables in `frontend/src/index.css` (`--wb-bg`, `--wb-surface`, `--wb-accent`). Defaults match StreamForge neutrals; palette swap later without layout changes.

---

## 4. Port map (avoid StreamForge collisions)

| Service | Port | Notes |
| --- | --- | --- |
| WasmBox API | `8001` | `uvicorn src.api.main:app --port 8001` |
| WasmBox Vite | `5174` | `npm run dev` in `frontend/` |
| PostgreSQL | `5433` | `docker compose up postgres` |
| Redis (optional) | `6380` | `docker compose --profile full up redis` |
| Prometheus | `9091` | Scrapes `host.docker.internal:8001` |
| Grafana | `3002` | admin / admin |

StreamForge uses `8000`, `5173`, `9090`, `3001` — run both stacks side by side.

---

## 5. Definition of Done

### Mid Review (end of Week 2, Day 10)

- [ ] Monaco editor → **Compile** → **Run** → stdout in UI
- [ ] WebSocket live stdout during execution
- [ ] AST guard rejects obvious malware (`open`, `socket`, `subprocess`) before compile
- [ ] Wasmtime kills infinite-loop WASM artifact in &lt;100 ms wall clock
- [ ] `GET /health` + pytest smoke test green
- [ ] `docs/architecture.md` draft + README quick start
- [ ] Team commit cadence: ≥10 distinct days in prior 14 days (Axlero SOP)

### Final Review (end of Week 4, Day 20)

- [ ] **Security Lab** — each attack card shows blocked + reason + resource graph
- [ ] **Host function** `db_query` via capability toggle (fixture DB only)
- [ ] **Plugin CRUD** + versioning + rollback + WASM SHA fingerprint
- [ ] **Multi-tenant** demo (`tenant_a` / `tenant_b`) with isolation + quotas
- [ ] **Webhook** ingress with HMAC + external `curl` trigger
- [ ] **Metrics** + **Operations** pages (stat cards, Grafana/Prometheus embeds)
- [ ] **Template gallery** — 3 one-click plugins (JSON formatter, CSV map, webhook transform)
- [ ] `docs/security-model.md` complete — explains why raw Python never runs
- [ ] Full pytest suite green; 5-minute demo script rehearsed
- [ ] Team commit cadence: all 20 prior days (Axlero SOP)

---

## 6. Uniqueness / portfolio differentiators

### P0 — ship in 4 weeks

| Feature | Why it matters |
| --- | --- |
| **Security Lab** | Curated attacks with denial reason — not a one-off script |
| **Capability matrix** | stdio → host DB → webhook; per-plugin ACL visible in UI |
| **Compile vs run waterfall** | Every execution shows where time went |
| **Plugin library** | Save, version, rollback, template gallery |
| **Multi-tenant simulation** | Namespaces + runs/min and memory quotas |
| **Webhook + HMAC** | Real SaaS ingress pattern |
| **Bytecode fingerprint** | SHA-256 of `.wasm` in audit log |
| **Operations console** | Violations, logs, sandbox health (StreamForge analogue) |
| **Embedded observability** | Grafana/Prometheus tabs on Metrics page |

### P1 — pull if ahead

- OpenTelemetry trace IDs on executions
- Monaco side-by-side version diff
- WASM size / fuel consumption leaderboard
- CI-style preflight badge before deploy
- Redis-backed async webhook worker

---

## 7. Security rules (non-negotiable)

1. **No `exec()`, `eval()`, or subprocess of user Python** on the API host.
2. **AST guard runs before compile** — structured violations returned to Monaco.
3. **WASM sandbox** — no filesystem, no network unless explicitly granted via host functions.
4. **Host functions are the only bridge** — `db_query` reads a fixture in-memory DB; no raw SQL from plugin.
5. **Tenant isolation** — plugin IDs scoped to `tenant_id`; cross-tenant load returns 404.
6. **Webhook secrets** — HMAC-SHA256 on body; reject replayed timestamps &gt;5 min skew.
7. **Artifacts** — store `.wasm` on disk or DB blob; never trust filename from client.

See [docs/security-model.md](docs/security-model.md) for full threat model.

---

## 8. Environment setup

```powershell
# Windows (from wasmbox/)
.\scripts\setup.ps1
.\.venv\Scripts\Activate.ps1
uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload
```

```bash
# macOS/Linux
bash scripts/setup.sh
source .venv/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload
```

```bash
# Infra
docker compose up -d postgres prometheus grafana

# Compiler image (Week 2+)
docker compose build compiler
docker compose --profile compile run --rm compiler compile /work/plugin.py -o /artifacts/plugin.wasm

# Frontend
cd frontend && npm install && npm run dev
```

---

## 9. Four-week daily plan (20 working days)

Each day is one focused deliverable. Backend and frontend columns list concrete files/endpoints. **Done when** is the acceptance check for that day.

---

### Week 1 — Foundation: runtime + UI scaffold

**Week gate:** Prebuilt WASM executes with limits; dashboard shell navigable on `:5174`.

#### Day 1 — Repo bootstrap

| Area | Tasks |
| --- | --- |
| **Backend** | Finalize tree under `wasmbox/`; `requirements.txt`; `.gitignore`; `docker-compose.yml` skeleton; `GET /health` in `src/api/main.py` |
| **Frontend** | — |
| **Docs** | Scaffold `README.md`, this file |

**Done when:** `curl http://localhost:8001/health` returns `{"status":"ok","service":"wasmbox"}`.

---

#### Day 2 — Raw WASM run

| Area | Tasks |
| --- | --- |
| **Backend** | Implement `src/sandbox/runtime.py`: load prebuilt `.wasm` from `plugins/examples/`; stdin → stdout; return `duration_ms` |
| **API** | `POST /api/run/wasm` (artifact path or upload) — temporary endpoint until Day 8 |
| **Assets** | Add or build `hello.wasm` (WASI hello-world) into `plugins/examples/` |

**Done when:** API runs `hello.wasm` and returns stdout + timing.

---

#### Day 3 — Limits

| Area | Tasks |
| --- | --- |
| **Backend** | Memory cap on Wasmtime `Store`; fuel or epoch interruption; kill `infinite_loop.wasm` |
| **Metrics** | Stub counters in `src/metrics/prometheus.py`: `wasmbox_sandbox_timeouts_total`, `wasmbox_oom_total` |
| **Assets** | `infinite_loop.wasm` in `plugins/examples/` |

**Done when:** Infinite loop terminated in &lt;100 ms wall clock; timeout counter increments.

---

#### Day 4 — UI shell

| Area | Tasks |
| --- | --- |
| **Backend** | CORS for `http://localhost:5174` in `main.py` |
| **Frontend** | Vite + Tailwind 4; `AppShell`, `Sidebar`, `AppHeader`, `PageLayout`; `config/navigation.js` (6 pages); placeholder pages; port `5174` |
| **Frontend** | Mirror StreamForge layout: collapsible sidebar, page header |

**Done when:** UI at `http://localhost:5174` — all nav items switch pages.

---

#### Day 5 — Playground stub

| Area | Tasks |
| --- | --- |
| **Backend** | Pydantic models: `CompileRequest`, `RunRequest`, `ExecutionResult`; stub `POST /api/compile` and `POST /api/run` return mock JSON |
| **Frontend** | `Playground.jsx`: Monaco with default template; Run button calls stub API; show JSON response panel |
| **Deps** | Add `@monaco-editor/react` to `frontend/package.json` |

**Done when:** Editor visible; Run shows stub execution result.

---

### Week 2 — Compile pipeline + E2E run

**Mid Review target:** Day 10 demo — user code → WASM → stdout with AST blocking malware.

#### Day 6 — AST guard

| Area | Tasks |
| --- | --- |
| **Backend** | `src/sandbox/ast_guard.py`: walk AST; deny `import os/socket/subprocess`, `open()`, `eval`, `exec`, `import *` |
| **API** | `POST /api/lint` returns `{ violations: [{ line, col, message, rule }] }` |
| **Tests** | `tests/test_ast_guard.py` — file_read and socket samples fail |
| **Frontend** | Violations list under Monaco when lint/compile fails |

**Done when:** Malicious `.py` rejected with structured violations before compile.

---

#### Day 7 — Compiler service

| Area | Tasks |
| --- | --- |
| **Backend** | `compiler/Dockerfile`; `src/sandbox/compiler_client.py` — invoke Docker or local extism-py |
| **API** | Real `POST /api/compile` — guard → compile → write `artifacts/{id}.wasm`; return fingerprint SHA-256 |
| **Frontend** | Compile button; compilation log panel (stderr from compiler) |

**Done when:** Benign `hello_plugin.py` compiles to WASM artifact on disk.

---

#### Day 8 — Run pipeline

| Area | Tasks |
| --- | --- |
| **Backend** | Real `POST /api/run` — load artifact, Wasmtime execute, persist `Execution` (SQLite via `src/storage/`) |
| **Frontend** | stdout/stderr panels; latency ms badge; status (`ok`, `timeout`, `error`) |

**Done when:** Full compile → run from UI without stubs.

---

#### Day 9 — Live stream

| Area | Tasks |
| --- | --- |
| **Backend** | `src/api/websocket.py` — `/ws/executions` streams stdout chunks + terminal `done` event |
| **Frontend** | `AppProvider` WebSocket hook; live output panel in Playground (append chunks) |

**Done when:** Output streams while WASM runs (simulate chunked flush if needed).

---

#### Day 10 — Mid Review prep

| Area | Tasks |
| --- | --- |
| **Backend** | `tests/test_api_smoke.py`; polish error responses |
| **Docs** | `docs/architecture.md` draft; README quick start |
| **Frontend** | `Overview.jsx` — table of last 10 executions (time, status, duration, fingerprint prefix) |

**Done when:** Mid Review demo script: edit → compile → run → live stdout; show AST block on `open()`.

---

### Week 3 — Security lab + capabilities + persistence

**Week gate:** Security Lab green; host bridge works; plugins in Postgres; tenant isolation visible.

#### Day 11 — Security suite

| Area | Tasks |
| --- | --- |
| **Backend** | `tests/test_sandbox_security.py` — file read, env leak, subprocess attempts fail in WASM path |
| **API** | `POST /api/security/run` — run labeled attack scenario by id |
| **Frontend** | `SecurityLab.jsx` — attack cards (infinite loop, memory bomb, host escape attempt) |

**Done when:** Each attack shows **blocked** + human-readable **reason**.

---

#### Day 12 — Network isolation

| Area | Tasks |
| --- | --- |
| **Backend** | Document WASI capability denial; ensure no network imports in WASM config |
| **Docs** | `docs/security-model.md` — network section |
| **Frontend** | Security Lab card: socket/connect simulation (AST or runtime denial) |

**Done when:** Network denial demonstrated and documented.

---

#### Day 13 — Host functions

| Area | Tasks |
| --- | --- |
| **Backend** | `src/sandbox/host_functions.py` — `db_query` stub over in-memory fixture; `capabilities.py` flag `ALLOW_DB_BRIDGE` |
| **API** | Run request accepts `capabilities: ["stdio", "db_bridge"]` |
| **Frontend** | Playground toggle “Allow safe DB bridge”; sample plugin that calls host |

**Done when:** Plugin reads fixture rows only via host function.

---

#### Day 14 — Plugin CRUD

| Area | Tasks |
| --- | --- |
| **Backend** | `src/storage/models.py` — `Plugin`, `PluginVersion`; Postgres in compose; Alembic or create_all |
| **API** | `src/api/routes/plugins.py` — list, create, get, load source into editor |
| **Frontend** | `Plugins.jsx` — list, save, open in Playground |

**Done when:** Saved plugin reloads in editor and re-runs.

---

#### Day 15 — Tenants + quotas

| Area | Tasks |
| --- | --- |
| **Backend** | `tenant_id` on plugins; rate limit runs/min; per-tenant memory cap; 429 on quota exceed |
| **API** | Header `X-Tenant-Id` or query param for demo |
| **Frontend** | Tenant switcher (`tenant_a` / `tenant_b`); hide cross-tenant plugins |

**Done when:** Tenant B cannot load Tenant A plugins (404).

---

### Week 4 — Product polish, webhooks, observability, demo

**Final Review target:** Day 20 — full SaaS story in 5 minutes.

#### Day 16 — Versioning

| Area | Tasks |
| --- | --- |
| **Backend** | Version bump on save; rollback to prior `PluginVersion`; expose WASM SHA in API |
| **Frontend** | Version dropdown + rollback button; show fingerprint |

**Done when:** Rollback restores prior WASM hash verified in UI.

---

#### Day 17 — Templates

| Area | Tasks |
| --- | --- |
| **Backend** | Gallery API from `plugins/examples/` — JSON formatter, CSV row map, webhook body transform |
| **Frontend** | Template gallery modal in Playground; one-click load |

**Done when:** 3 templates compile and run in one click each.

---

#### Day 18 — Webhooks

| Area | Tasks |
| --- | --- |
| **Backend** | `POST /hooks/{plugin_id}` + HMAC validation; optional Redis async (`docker compose --profile full`) |
| **Frontend** | Webhook URL + secret display on Plugins page; copy curl example |

**Done when:** External `curl` triggers plugin run; bad HMAC rejected.

---

#### Day 19 — Observability

| Area | Tasks |
| --- | --- |
| **Backend** | Wire `wasmbox_executions_total`, `wasmbox_compile_errors_total`, `wasmbox_sandbox_timeouts_total`; mount `/metrics` |
| **Infra** | Grafana dashboard JSON polish in `infra/grafana/` |
| **Frontend** | `Metrics.jsx` + `Operations.jsx` — stat cards, Grafana/Prometheus embeds (`lib/observability.js`) |

**Done when:** Grafana embed shows execution rate from live runs.

---

#### Day 20 — Final Review

| Area | Tasks |
| --- | --- |
| **Backend** | pytest green; error message polish |
| **Docs** | Final `security-model.md`; **demo script** below embedded in this section |
| **Frontend** | Overview CTAs; empty states; copy pass |

**Done when:** Final demo rehearsed; all Final Review DoD checkboxes met.

---

## 10. Five-minute demo script (Final Review)

1. **Overview** — show recent executions table and sandbox health summary.
2. **Playground** — pick “JSON formatter” template → Compile (show SHA fingerprint) → Run → live stdout.
3. **Toggle DB bridge** — run host-function sample → show fixture query result.
4. **Security Lab** — run “infinite loop” → timeout in &lt;100 ms; run “file read” → AST blocked before compile.
5. **Plugins** — save plugin, bump version, rollback, show fingerprint change.
6. **Tenant switch** — `tenant_a` vs `tenant_b` isolation.
7. **Webhook** — `curl` with HMAC triggers run; show execution in Overview.
8. **Metrics** — Grafana embed: execution rate; Operations: timeout counter.
9. **Close** — “We never run customer Python — AST guard + WASM + capabilities.”

---

## 11. Project structure

```
wasmbox/
├── README.md
├── WasmBox-PROJECT.md          ← this file
├── requirements.txt
├── pyproject.toml
├── docker-compose.yml
├── .gitignore
├── scripts/setup.sh, setup.ps1
├── infra/prometheus.yml, alerts.yml, grafana/
├── compiler/Dockerfile
├── src/
│   ├── api/main.py, routes/, websocket.py
│   ├── sandbox/runtime.py, ast_guard.py, compiler_client.py, capabilities.py, host_functions.py
│   ├── storage/db.py, models.py
│   └── metrics/prometheus.py
├── plugins/examples/, plugins/malicious/
├── tests/
├── docs/architecture.md, security-model.md
└── frontend/                   ← see frontend/STRUCTURE.md
```

---

## 12. GitHub compliance (team-wide)

Same Axlero SOP as StreamForge:

- **Mid Review window:** commits on ≥10 different days in the prior 14 days.
- **Final Review window:** commits on all 20 of the prior 20 days.
- Collective requirement on the shared monorepo — any member’s commits count.

---

## 13. Risks & mitigations

| Risk | Mitigation |
| --- | --- |
| Python→WASM on Windows | Compile only in Docker; runtime on host via wasmtime-py |
| Extism vs raw Wasmtime drift | Week 1 raw WASM; Week 2+ user Python via Extism PDK |
| Port clashes with StreamForge | Use 8001 / 5174 / 3002 / 5433 / 9091 |
| Expectation of arbitrary Python | Document restricted subset + AST + WASM; never `exec()` |
| Monaco bundle size | Lazy-load editor on Playground route only |

---

*Full task list is day-by-day in §9. Member assignments will be added in `WORK_DISTRIBUTION.md` before Mid Review (StreamForge SOP §9.10).*
