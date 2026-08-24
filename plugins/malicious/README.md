# Attack samples for Security Lab — NEVER execute as raw Python on the host.
# These are compiled/run only inside WASM after AST guard + sandbox (Week 3).

## infinite_loop.py (concept)
```python
while True:
    pass
```
Expected: fuel/timeout kill in <100ms wall clock.

## file_read.py (concept)
```python
open("/etc/passwd").read()
```
Expected: AST guard rejects before compile.

## socket_connect.py (concept)
```python
import socket
socket.create_connection(("example.com", 80))
```
Expected: AST guard rejects; WASM has no network capability.
