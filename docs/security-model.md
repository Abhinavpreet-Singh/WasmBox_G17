# Security model (draft — complete by Week 4 Day 20)

## Principle

**Customer Python never executes on the host interpreter.** All user code paths:

1. Static analysis (`src/sandbox/ast_guard.py`)
2. Compilation to WASM (Dockerized Extism)
3. Execution in Wasmtime with resource limits
4. Optional capability-gated host calls

## Threats and mitigations

| Threat | Mitigation |
| --- | --- |
| Arbitrary code execution on host | No `exec`/`eval`; WASM only |
| Filesystem read (`/etc/passwd`) | AST blocks `open`; WASM has no FS capability |
| Network exfiltration | AST blocks `socket`; no WASI network |
| Subprocess spawn | AST blocks `subprocess`, `os.system` |
| CPU exhaustion (`while True`) | Fuel / epoch timeout; &lt;100 ms kill |
| Memory exhaustion | Wasmtime memory limit; OOM counter |
| Cross-tenant data leak | `tenant_id` on all plugin queries |
| Webhook abuse | HMAC-SHA256 + timestamp skew check |
| Malicious WASM upload | Compile path only; verify SHA on run |

## Host functions

Host functions are the **only** escape hatch. Initial scope:

- `db_query(fixture_id, sql)` — reads from in-memory fixture DB, not customer SQL
- (P1) `http_fetch(url)` — allowlist domains only

Plugins must declare capabilities at compile/run time. UI shows capability matrix.

## Network isolation (Week 3 Day 12)

Document here: WASI config used, proof that socket syscalls are unavailable, and Security Lab test IDs.

## Audit log

Each execution records: `tenant_id`, `plugin_version_id`, `wasm_sha256`, `duration_ms`, `status`, `capabilities`, `stdout` (truncated).
