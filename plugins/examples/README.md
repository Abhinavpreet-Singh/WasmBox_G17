# Example plugins — benign Python sources and prebuilt WASM (Week 1 Day 2+)

Place `hello.wasm` and `infinite_loop.wasm` here after Day 2–3 tasks.
Week 2 adds Extism Python PDK examples (`json_formatter.py`, etc.).

## Usage

Compile any example plugin:

```bash
docker compose --profile compile run --rm compiler compile /work/hello_plugin.py -o /artifacts/hello.wasm
```
