# Extism Python compile toolchain — used via docker compose --profile compile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential clang llvm \
    && rm -rf /var/lib/apt/lists/*

# extism-py is the Extism Python PDK compiler that provides the
# `extism-py compile` CLI. Do NOT use plain `extism` here —
# that package is the host SDK only and does not ship the compiler binary.
RUN pip install --no-cache-dir extism-py

WORKDIR /work
VOLUME ["/artifacts"]

# Usage: docker run -v ./artifacts:/artifacts wasmbox-compiler compile plugin.py -o /artifacts/plugin.wasm
ENTRYPOINT ["extism-py"]
