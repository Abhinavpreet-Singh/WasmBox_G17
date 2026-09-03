from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.compile import router as compile_router
from src.api.routes.health import router as health_router
from src.api.routes.metrics import router as metrics_router
from src.api.routes.run import router as run_router
from src.api.routes.lint import router as lint_router
from src.api.routes.executions import router as executions_router
from src.api.websocket import router as ws_router
from src.storage.db import engine
from src.storage.models import Base


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
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
app.include_router(executions_router)
app.include_router(ws_router)
