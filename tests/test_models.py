import asyncio
import importlib
import os

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

"""Tests for Job model and deduplication."""

def setup_module(module):
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
    if os.path.exists("test.db"):
        os.remove("test.db")
    global models
    models = importlib.import_module("app.models")
    importlib.reload(models)
    asyncio.run(init_db())


def teardown_module(module):
    asyncio.run(models.engine.dispose())
    if os.path.exists("test.db"):
        os.remove("test.db")


async def init_db() -> None:
    async with models.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@pytest.mark.asyncio
async def test_deduplication() -> None:
    async with models.async_session() as session:
        job = {
            "company": "Test",
            "city": "Warszawa",
            "title": "Kierowca",
            "salary_min": 100,
            "salary_max": 200,
            "url": "http://example.com",
        }
        job["job_hash"] = models.Job.make_hash(
            job["company"],
            job["city"],
            job["title"],
        )
        await session.execute(models.Job.__table__.insert().values(**job))
        await session.commit()
        caught = False
        try:
            await session.execute(models.Job.__table__.insert().values(**job))
            await session.commit()
        except IntegrityError:
            await session.rollback()
            caught = True
        result = await session.execute(select(models.Job))
        rows = result.scalars().all()
        assert len(rows) == 1
        assert caught


def test_make_hash_uniqueness() -> None:
    hash1 = models.Job.make_hash("A", "B", "Driver")
    hash2 = models.Job.make_hash("A", "B", "Driver")
    hash3 = models.Job.make_hash("A", "C", "Driver")
    assert hash1 == hash2
    assert hash1 != hash3
