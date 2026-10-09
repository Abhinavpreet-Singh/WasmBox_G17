# WasmBox

**Secure Multi-Tenant Plugin Sandbox**
Axlero Solutions, Group 17

WasmBox lets SaaS customers write Python plugins in a browser IDE and run them safely on shared infrastructure. The server never executes raw customer Python. Every submission is screened by a static AST guard, compiled to WebAssembly, and executed inside a Wasmtime sandbox with hard memory and CPU limits.

---

## The problem

Platforms that accept customer code face a bad choice. Running `exec(user_code)` on the host is a security incident waiting to happen. Spinning up a container per plugin is slow and expensive at scale.

WasmBox takes a third path.

| Risk | WasmBox answer |
| --- | --- |
| `exec()` on the API host | Never happens. WASM bytecode only. |
| One container per tenant plugin | One shared runtime, isolated by capabilities |
| No proof the sandbox holds | Security Lab runs real attacks and shows why each is denied |
| Opaque executions | SHA-256 bytecode fingerprint, timing breakdown, Prometheus metrics |

---

## How it works

```
Monaco editor
   |
   v
POST /api/compile    1. AST guard rejects os, socket, subprocess, open, eval
   |                 2. extism-py compiles Python to .wasm inside Docker
   |                 3. SHA-256 fingerprint recorded
   v
POST /api/run        4. Wasmtime executes with memory cap and fuel limit
   |                 5. Host functions are the only bridge out, granted per run
   v
WS /ws/executions    6. stdout streams live to the dashboard
   |
   v
PostgreSQL           7. Execution row feeds Overview, Metrics and Security Lab
```

Three independent layers of defense:

1. **Static.** The AST guard blocks dangerous imports and calls before anything compiles.
2. **Compile.** Translating to WASM removes the Python runtime and its escape hatches.
3. **Runtime.** Wasmtime enforces memory and CPU caps with no filesystem or network access.

A plugin reaches the host database only if the execution was explicitly granted the `ALLOW_DB_BRIDGE` capability. Without it the host function is never registered, so the import does not resolve and the plugin cannot call what does not exist.

---

## Quick start

Requirements: Python 3.11 or newer, Node 20 or newer, Docker Desktop.

**1. Infrastructure**

```bash
docker compose up -d postgres prometheus grafana
docker compose build compiler
```

**2. Backend**

```powershell
.\scripts\setup.ps1
.\.venv\Scripts\Activate.ps1
uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload
```

On macOS or Linux use `bash scripts/setup.sh` and `source .venv/bin/activate`.

**3. Frontend**

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5174. The API health check is at http://localhost:8001/health.

---

## Ports

| Service | Port | Notes |
| --- | --- | --- |
| API | 8001 | FastAPI and WebSocket |
| Frontend | 5174 | Vite dev server, proxies to 8001 |
| PostgreSQL | 5433 | Plugins, versions, executions |
| Prometheus | 9091 | Scrapes the API `/metrics` endpoint |
| Grafana | 3002 | Login admin / admin |
| Redis | 6380 | Optional, `--profile full` |

These ports avoid collisions with the StreamForge project in the same monorepo.

---

## Writing a plugin

Plugins use the Extism Python PDK. The exported function must be named `greet`, and output is written with `extism.output_str()` rather than returned.

**Basic plugin**

```python
import extism

@extism.plugin_fn
def greet():
    extism.output_str("Hello from WasmBox!")
```

**Computation with the standard library**

```python
import extism
import json

@extism.plugin_fn
def greet():
    orders = [
        {"item": "widget", "qty": 3, "price": 4.50},
        {"item": "gadget", "qty": 1, "price": 19.00},
    ]
    total = sum(o["qty"] * o["price"] for o in orders)
    extism.output_str(json.dumps({"line_items": len(orders), "total": round(total, 2)}))
```

**Host database bridge**

Requires the "Allow safe DB bridge" toggle in the Playground. The host function reads a fixture table by name and never executes plugin supplied SQL.

```python
import extism

@extism.import_fn("wasmbox", "db_query")
def db_query(table: str) -> str: ...

@extism.plugin_fn
def greet():
    users = db_query("users")
    extism.output_str("Rows: " + str(users))
```

With the toggle off, the same plugin fails with `unknown import: wasmbox::db_query has not been defined`. That contrast is the capability model in action.

Three templates ship in the Playground: Hello World, JSON Formatter and Webhook Transform.

---

## Dashboard

| Page | Purpose |
| --- | --- |
| Overview | Sandbox health and recent executions |
| Playground | Monaco editor, templates, compile, run, live stdout, violations |
| Plugins | Saved plugins, versions, fingerprints, webhook details |
| Security Lab | Curated attacks, denial reasons, live threat feed |
| Operations | Violations, logs and sandbox health |
| Metrics | Prometheus counters with Grafana links |

### Security Lab

The Security Lab turns the sandbox from a claim into a demonstration.

- Attack classification recorded on every execution through `attack_type`
- Attack scenario cards showing blocked status and the reason
- Live threat feed from `GET /api/security/feed`, refreshing every 5 seconds
- Aggregated counters from `GET /api/security/stats`
- Color coded security score bar
- Denials are attributed to their layer: AST guard, runtime limit or missing capability

---

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Service status and sandbox limits |
| GET | `/metrics` | Prometheus exposition |
| POST | `/api/lint` | AST guard only, returns structured violations |
| POST | `/api/compile` | Guard, compile to WASM, return fingerprint |
| POST | `/api/run` | Compile and execute source |
| POST | `/api/run/wasm` | Execute a prebuilt artifact |
| GET | `/api/executions` | Execution history |
| GET, POST | `/api/plugins` | List and save plugins |
| GET | `/api/plugins/{id}/versions` | Version history |
| POST | `/api/plugins/{id}/run` | Run a saved plugin |
| GET | `/api/security/feed` | Recent attack attempts |
| GET | `/api/security/stats` | Aggregated security counters |
| POST | `/hooks/{plugin_id}` | Webhook ingress, HMAC verified |
| WS | `/ws/executions` | Live execution stream |

### Webhook example

Requests are authenticated with an HMAC SHA-256 signature over the raw body, sent in the `X-Hub-Signature-256` header.

```bash
BODY='{"order_id": 42}'
SIG="sha256=$(printf '%s' "$BODY" | openssl dgst -sha256 -hmac 'wasmbox-super-secret' | awk '{print $2}')"

curl -X POST http://localhost:8001/hooks/<plugin_id> \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: $SIG" \
  -d "$BODY"
```

A missing or incorrect signature is rejected with 401 before the plugin runs.

---

## Security model

Rules enforced in code:

1. No `exec()`, `eval()` or subprocess execution of customer Python on the host.
2. The AST guard runs before compilation and returns structured violations to the editor.
3. The WASM sandbox has no filesystem and no network.
4. Host functions are the only bridge out, and each is gated by a capability flag.
5. Artifacts are addressed by a server generated id, never by a client supplied filename.
6. Webhook bodies must carry a valid HMAC signature.

Blocked modules: `os`, `socket`, `subprocess`, `ctypes`, `importlib`, `builtins`
Blocked calls: `open`, `eval`, `exec`, `__import__`, `compile`, `breakpoint`
Blocked attributes: `system`, `popen`, `spawn`, `fork`, `execve`

Full threat model: [docs/security-model.md](docs/security-model.md).

---

## Tech stack

| Layer | Technology |
| --- | --- |
| API | FastAPI, uvicorn, WebSocket |
| Sandbox | Wasmtime via wasmtime-py |
| Plugin model | Extism Python PDK |
| Compiler | extism-py in Docker |
| Static analysis | Custom AST walker |
| Database | PostgreSQL with SQLAlchemy |
| Metrics | prometheus-client, Grafana |
| Frontend | React 19, Vite, Tailwind 4, Monaco |
| Tests | pytest |

---

## Configuration

The database DSN is read from the `WASMBOX_DATABASE_URL` environment variable. It defaults to the Postgres container defined in `docker-compose.yml`:

```
WASMBOX_DATABASE_URL=postgresql+psycopg2://wasmbox:wasmbox@localhost:5433/wasmbox
```

For a quick local run without Postgres, SQLite also works:

```
WASMBOX_DATABASE_URL=sqlite:///./wasmbox.db
```

---

## Tests

```bash
pytest tests/ -v
```

Fourteen suites cover the AST guard, runtime limits, capabilities, host functions, the compiler client, the WebSocket stream and the security classifier. Tests that need the API on port 8001 skip automatically when it is not running, and the compiler integration test needs Docker and the `wasmbox-compiler:local` image.

---

## Troubleshooting

**Blank page in the browser.** Check the browser console. A missing export or an undefined constant in a React page blanks the whole app.

**Frontend cannot reach the API.** Confirm the Vite proxy in `frontend/vite.config.js` targets port 8001.

**"Docker is not available".** Start Docker Desktop and build the compiler image with `docker compose build compiler`. The first compile after an idle period occasionally times out, so retry once.

**"No exports found".** Import the module as `import extism`, decorate with `@extism.plugin_fn`, and name the function `greet`.

**Database connection refused.** Confirm the Postgres container is healthy, or point `WASMBOX_DATABASE_URL` at SQLite.

---

## Repository layout

```
wasmbox/
  src/
    api/          FastAPI app, routes, WebSocket
    sandbox/      AST guard, compiler client, runtime, capabilities, host functions
    storage/      SQLAlchemy models, session, repository
    metrics/      Prometheus counters
  frontend/       React dashboard
  compiler/       Dockerfile for the extism-py toolchain
  plugins/        Example and malicious plugin samples
  infra/          Prometheus and Grafana configuration
  tests/          pytest suites
  docs/           Architecture and security model
```

---

## Contributing

Branch off `main` and open a pull request against `main`. Each feature area has its own branch: `Abhinavpreet`, `Surya`, `Shifana`, `Meven`, `Simin`. All pull requests require passing tests before merge.

---

## Documentation

- [docs/architecture.md](docs/architecture.md), system design
- [docs/security-model.md](docs/security-model.md), threat model
- [WasmBox-PROJECT.md](WasmBox-PROJECT.md), delivery plan and definition of done
- [frontend/STRUCTURE.md](frontend/STRUCTURE.md), React layout
