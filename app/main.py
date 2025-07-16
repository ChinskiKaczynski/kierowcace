"""FastAPI application setup."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .models import Base, engine
from .routes import jobs as jobs_router


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover
    """Handle startup and shutdown events."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="KierowcaCE", lifespan=lifespan)

app.include_router(jobs_router.router)
