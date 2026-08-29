# WasmBox — Team Task Board

**Updated:** 2026-08-29 (Week 2 · Day 6/7)  
**Repo:** `WasmBox_G17` · branch per person below

---

## Project status snapshot

| Day | Focus | Status |
|-----|-------|--------|
| 1–3 | Bootstrap, WASM run, limits | Done |
| 4–5 | UI shell, Playground stubs | Done (Simin) |
| 6 | AST guard + `POST /api/lint` | Done (Shifana) |
| 6/7 | Compile guard + compiler client | In progress (Abhinavpreet) |
| 7 | Real Docker compile → `.wasm` | Started — needs Docker image build |

**Tests:** 12+ passing · **Next gate:** Mid Review (Day 10) — compile → run → stdout in UI

---

## Abhinavpreet Singh Arora (Lead) — `Abhinavpreet`

1. Merge latest `main`, finish `compiler_client.py` + real `POST /api/compile` flow (guard → Docker → SHA-256).
2. Build compiler image: `docker compose build compiler` and verify `hello_plugin.py` compiles to `artifacts/*.wasm`.
3. Wire `POST /api/run` to load compiled artifacts from `artifacts/` (Day 8 run pipeline start).
4. Add `GET /metrics` route exposing Prometheus counters from `src/metrics/prometheus.py`.
5. Review + merge open PRs from Simin, Shifana, and Surya; keep `main` green.

---

## Shifana Parveen R — `Shifana`

1. `git merge main` — sync AST guard + compile changes from lead.
2. Expand `tests/test_sandbox_security.py` — file read, env leak, subprocess attempts (Week 3 Day 11 prep).
3. Stub `src/sandbox/host_functions.py` — `db_query` over in-memory fixture rows.
4. Add `capabilities.py` flag `ALLOW_DB_BRIDGE` and document in `docs/security-model.md`.
5. Add compile-error counter stub in `src/metrics/prometheus.py` (`wasmbox_compile_errors_total`).

---

## Noore Simin — `simin`

1. `git merge main` — pull latest compile + lint API changes.
2. Add **Lint** button in `Playground.jsx` → `POST /api/lint`; show violations panel under Monaco.
3. Add Monaco **error markers** on violation `line` / `col` from lint response.
4. On **Compile** when `status === "blocked"`, render violations list (not just generic error).
5. Add **compilation log panel** (show `compiler_log` from compile response) — Day 7 UI.

---

## Surya Sankar — `Surya`

1. Create branch from `main`: `git checkout -b Surya` (branch is currently at scaffold only).
2. Implement `src/api/routes/metrics.py` — mount `GET /metrics` with `prometheus_client.generate_latest()`.
3. Build `Metrics.jsx` stat cards — parse `wasmbox_sandbox_timeouts_total`, `wasmbox_oom_total` from `/metrics`.
4. Scaffold `Operations.jsx` — sandbox health summary + placeholder violations table.
5. Draft `docs/architecture.md` data-flow section (compile → guard → WASM → run).

---

## Workflow (all members)

```bash
git fetch --all
git checkout <your-branch>
git merge main
# work only in your assigned files
pytest   # backend
cd frontend && npm run dev   # frontend on :5174
```

**Ports:** API `8001` · Vite `5174` · Grafana `3002` · Prometheus `9091`

---

*5 tasks per member · update this file when a day gate is completed.*
