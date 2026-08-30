# WasmBox — Team Task Board

**Updated:** 2026-08-30 (Week 2 · Day 7/8)  
**Repo:** `WasmBox_G17` · branch per person below

---

## Project status snapshot

| Day | Focus | Status |
|-----|-------|--------|
| 1–5 | Foundation + Playground | Done |
| 6 | AST guard + `POST /api/lint` | Done (Shifana) |
| 7 | Docker compile → `artifacts/*.wasm` | Done — needs `docker compose build compiler` |
| 8 | `POST /api/run` compile → Extism execute | Done (Abhinavpreet) |
| 9 | WebSocket live stdout | Next |

**Tests:** 20+ passing · **Next gate:** Mid Review (Day 10)

---

## Abhinavpreet Singh Arora (Lead) — `Abhinavpreet`

1. Build + verify compiler image: `docker compose build compiler` then compile `hello_plugin.py`.
2. E2E smoke: `POST /api/compile` → `POST /api/run` with `artifact_id` → stdout in API.
3. Day 9: implement `/ws/executions` WebSocket streaming in `src/api/websocket.py`.
4. Day 10: polish `Overview.jsx` executions table with fingerprint prefix + status.
5. Review team PRs; update `docs/architecture.md` for Mid Review demo script.

---

## Shifana Parveen R — `Shifana`

1. `git merge main` — sync compile/run pipeline changes.
2. Expand `tests/test_sandbox_security.py` — file read, env leak, subprocess attempts.
3. Stub `src/sandbox/host_functions.py` — `db_query` over in-memory fixture rows.
4. Add `ALLOW_DB_BRIDGE` capability flag in `capabilities.py` + security docs.
5. Wire `wasmbox_compile_errors_total` increment tests in compile error paths.

---

## Noore Simin — `simin`

1. `git merge main` — pull compile/run + metrics API.
2. Add **Lint** button → `POST /api/lint`; violations panel under Monaco.
3. Monaco error markers on violation `line` / `col`.
4. Update **Compile** button label (remove "stub"); show `wasm_sha256` + `compiler_log`.
5. Wire **Run** button to `POST /api/run` with editor `source` (full compile → run E2E).

---

## Surya Sankar — `Surya`

1. Create branch from `main`: `git checkout -b Surya`.
2. Build `Metrics.jsx` stat cards from live `GET /metrics` (timeouts, OOM, compile errors).
3. Scaffold `Operations.jsx` — sandbox health + violations placeholder table.
4. Add auto-refresh (30s) on Metrics page using `lib/observability.js`.
5. Draft `docs/architecture.md` compile → guard → WASM → run section.

---

## Workflow (all members)

```bash
git fetch --all
git checkout <your-branch>
git merge main
pytest
cd frontend && npm run dev   # :5174
uvicorn src.api.main:app --port 8001 --reload
```

**Ports:** API `8001` · Vite `5174` · Grafana `3002` · Prometheus `9091`

---

*5 tasks per member · update this file when a day gate is completed.*
