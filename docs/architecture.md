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

## Observability

Prometheus scrapes `host.docker.internal:8001/metrics`. Grafana provisioning lives in `infra/grafana/`.

See [WasmBox-PROJECT.md](../WasmBox-PROJECT.md) for the full mermaid diagram and daily build order.
