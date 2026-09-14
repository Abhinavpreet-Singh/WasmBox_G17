# Architecture (draft — expand through Week 2 Day 10)

## Overview

WasmBox is a three-tier system:

1. **React dashboard** (`frontend/`) — Monaco IDE, Security Lab, plugin library, observability embeds.
2. **FastAPI control plane** (`src/api/`) — compile, run, CRUD, webhooks, WebSocket, Prometheus.
3. **Sandbox runtime** (`src/sandbox/`) — AST guard, Dockerized compiler client, Wasmtime execution, host functions.

Persistence (`src/storage/`) starts as SQLite, migrates to PostgreSQL in Week 3.

## Request paths

| Path | Handler | Notes |
| --- | --- | --- |
| `GET /health` | `routes/health.py` | Liveness |
| `POST /api/compile` | `routes/compile.py` | Week 2 Day 7 |
| `POST /api/run` | `routes/run.py` | Week 2 Day 8 |
| `POST /api/lint` | compile route | Week 2 Day 6 |
| `GET/POST /api/plugins` | `routes/plugins.py` | Week 3 Day 14 |
| `POST /hooks/{plugin_id}` | `routes/webhooks.py` | Week 4 Day 18 |
| `GET /metrics` | `routes/metrics.py` | Week 4 Day 19 |
| `WS /ws/executions` | `websocket.py` | Week 2 Day 9 |

## Sandbox boundary

```
User Python
  → ast_guard (host never sees dangerous syntax)
  → compiler_client → .wasm bytes
  → runtime.py (Wasmtime Store + limits)
  → optional host_functions.py (capability-gated)
  → stdout / metrics / Execution row
```

## Compile → Run data flow

1. **Author** writes Python in the Playground and hits *Run*.
2. **`POST /api/run`** (`routes/run.py`) receives `{ source }` or `{ artifact_id }` to
   re-run something already compiled.
3. **Security classifier** (`security/classifier.py`) tags the source with an attack
   type (`safe`, `filesystem`, `network`, `process`, etc.) before anything else happens,
   purely for observability — it doesn't block execution by itself.
4. **AST guard** (`sandbox/ast_guard.py`) parses the source and rejects blocked imports
   (`os`, `socket`, `subprocess`) and blocked calls (`open`, `eval`, `exec`). A `blocked`
   status with the violation reason short-circuits the request here.
5. **Compiler client** (`sandbox/compiler_client.py`) only runs on guard-clean source —
   ships it to the Dockerized `extism-py` compiler and gets `.wasm` bytes + a SHA-256 back.
6. **Run** — `sandbox/extism_runtime.py`'s `run_extism_artifact()` loads the artifact
   through the Extism host SDK (`extism.Plugin`, WASI-enabled) on a daemon thread with a
   5-second wall-clock timeout, and calls the plugin's exported `greet` function.
7. **Capabilities** (`sandbox/capabilities.py`) gate which host functions the plugin
   gets: `run_extism_artifact()` takes an optional `capabilities: CapabilitySet`, and
   `host_functions.build_host_functions()` only registers `db_query` / `http_fetch` when
   the matching flag is set. No capabilities granted = no host functions registered =
   no way for the plugin to call out of the sandbox.
8. The frontend opts into the DB bridge per execution via `allow_db_bridge` on
   `POST /api/run`.
9. Every execution — result, duration, attack type — is persisted via
   `storage/repository.py` and surfaced on `/api/executions` (used by Operations.jsx)
   and in Prometheus counters (`GET /metrics`, used by Metrics.jsx).

\`\`\`mermaid
sequenceDiagram
    participant UI as Playground
    participant API as POST /api/run
    participant Classifier as classifier.py
    participant Guard as ast_guard.py
    participant Compiler as compiler_client.py
    participant Runtime as extism_runtime.py
    participant Host as host_functions.py

    UI->>API: POST /api/run {source, allow_db_bridge}
    API->>Classifier: classify_source(source)
    API->>Guard: lint_source(source)
    alt violations found
        Guard-->>API: violations[]
        API-->>UI: status=blocked
    else clean
        API->>Compiler: compile_python(source)
        Compiler-->>API: artifact_id, wasm_sha256
        API->>Runtime: run_extism_artifact(wasm_path, capabilities)
        Runtime->>Host: build_host_functions(capabilities)
        Host-->>Runtime: [db_query] only if ALLOW_DB_BRIDGE set
        Runtime-->>API: stdout, stderr, duration_ms, status
        API-->>UI: ExecutionResult
    end
\`\`\`

## Observability

Prometheus scrapes `host.docker.internal:8001/metrics`. Grafana provisioning lives in `infra/grafana/`.

See [WasmBox-PROJECT.md](../WasmBox-PROJECT.md) for the full mermaid diagram and daily build order.
