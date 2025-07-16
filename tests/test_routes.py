import asyncio
import importlib
import os

from fastapi.testclient import TestClient
from sqlalchemy import insert

"""Integration tests for FastAPI routes."""


def setup_module(module):
    if os.path.exists("test_routes.db"):
        os.remove("test_routes.db")
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_routes.db"
    global models
    models = importlib.import_module("app.models")
    importlib.reload(models)
    global app
    app_module = importlib.import_module("app.main")
    importlib.reload(app_module)
    app = app_module.app
    asyncio.run(init_db())


def teardown_module(module):
    asyncio.run(models.engine.dispose())
    if os.path.exists("test_routes.db"):
        os.remove("test_routes.db")


async def init_db() -> None:
    async with models.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    async with models.async_session() as session:
        job1 = {
            "company": "Firm",
            "city": "Lodz",
            "title": "Kierowca c+e",
            "salary_min": 100,
            "salary_max": 200,
            "url": "http://x.com",
        }
        job1["job_hash"] = models.Job.make_hash(
            job1["company"],
            job1["city"],
            job1["title"],
        )
        await session.execute(insert(models.Job).values(**job1))

        job2 = {
            "company": "Firm2",
            "city": "Gdansk",
            "title": "Kierowca",
            "salary_min": None,
            "salary_max": None,
            "url": "http://y.com",
        }
        job2["job_hash"] = models.Job.make_hash(
            job2["company"],
            job2["city"],
            job2["title"],
        )
        await session.execute(insert(models.Job).values(**job2))

        await session.commit()


def test_jobs_route() -> None:
    client = TestClient(app)
    resp = client.get("/jobs")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_jobs_route_with_salary() -> None:
    client = TestClient(app)
    resp = client.get("/jobs", params={"with_salary": "true"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_search_route() -> None:
    client = TestClient(app)
    resp = client.get("/search", params={"q": "Kierowca"})
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_index_route_html() -> None:
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Kierowca c+e" in resp.text


def test_job_detail_route() -> None:
    client = TestClient(app)
    resp = client.get("/jobs/1")
    assert resp.status_code == 200
    assert "Kierowca c+e" in resp.text


def test_job_detail_not_found() -> None:
    client = TestClient(app)
    resp = client.get("/jobs/999")
    assert resp.status_code == 404
