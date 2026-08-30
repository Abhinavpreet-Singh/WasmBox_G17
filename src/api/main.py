from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.compile import router as compile_router
from src.api.routes.health import router as health_router
from src.api.routes.lint import router as lint_router
from src.api.routes.metrics import router as metrics_router
from src.api.routes.run import router as run_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


app = FastAPI(
    title="WasmBox API",
    description="Secure multi-tenant WASM plugin sandbox",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(compile_router)
app.include_router(run_router)
app.include_router(lint_router)
app.include_router(metrics_router)
