# Extism Python compile toolchain — used via docker compose --profile compile
FROM python:3.12-slim

ARG EXTISM_PY_VERSION=v0.1.5

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates tar binaryen \
    && rm -rf /var/lib/apt/lists/*

# extism-py is distributed as a prebuilt binary from the extism/python-pdk
# GitHub releases (NOT a pip package). Fetch the linux x86_64 tarball and
# install the binary + its bundled wasm runtime under /usr/local.
RUN set -eux; \
    curl -fsSL -o /tmp/extism-py.tar.gz \
        "https://github.com/extism/python-pdk/releases/download/${EXTISM_PY_VERSION}/extism-py-x86_64-linux-${EXTISM_PY_VERSION}.tar.gz"; \
    tar -xzf /tmp/extism-py.tar.gz -C /usr/local --strip-components=1; \
    rm /tmp/extism-py.tar.gz; \
    extism-py --version

WORKDIR /work
VOLUME ["/artifacts"]

# Usage: docker run -v ./artifacts:/artifacts wasmbox-compiler compile plugin.py -o /artifacts/plugin.wasm
ENTRYPOINT ["extism-py"]
