"""FastAPI entry point for the pypemesh backend."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import pypemesh_core

app = FastAPI(
    title="pypemesh API",
    version=pypemesh_core.__version__,
    description="Pipe stress analysis API. See /docs for endpoints.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://pypemesh.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Health(BaseModel):
    status: str
    core_version: str


@app.get("/health", response_model=Health)
async def health() -> Health:
    return Health(status="ok", core_version=pypemesh_core.__version__)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "pypemesh-backend",
        "version": pypemesh_core.__version__,
        "docs": "/docs",
    }
