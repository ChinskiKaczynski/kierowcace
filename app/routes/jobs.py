"""FastAPI routes for job listings."""

from __future__ import annotations

from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.templating import Jinja2Templates
from starlette.templating import _TemplateResponse as TemplateResponse

from ..models import Job, async_session

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for dependency injection."""
    async with async_session() as session:
        yield session


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    with_salary: Optional[bool] = Query(False, alias="with_salary"),
    session: AsyncSession = Depends(get_session),
) -> TemplateResponse:
    """Render the list of jobs as HTML."""
    query = select(Job)
    if with_salary:
        query = query.where(
            Job.salary_min.isnot(None),
            Job.salary_max.isnot(None),
        )
    result = await session.execute(query)
    jobs = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "index.html",
        {"jobs": jobs, "with_salary": with_salary},
    )


@router.get("/jobs", response_model=None)
async def list_jobs(
    with_salary: Optional[bool] = Query(False, alias="with_salary"),
    session: AsyncSession = Depends(get_session),
) -> list[Job]:
    """Return jobs as JSON with optional salary filter."""
    query = select(Job)
    if with_salary:
        query = query.where(
            Job.salary_min.isnot(None),
            Job.salary_max.isnot(None),
        )
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/search", response_model=None)
async def search_jobs(
    q: str,
    session: AsyncSession = Depends(get_session),
) -> list[Job]:
    """Search jobs by title substring."""
    query = select(Job).where(Job.title.ilike(f"%{q}%"))
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/jobs/{job_id}", response_class=HTMLResponse)
async def get_job(
    request: Request,
    job_id: int,
    session: AsyncSession = Depends(get_session),
) -> TemplateResponse:
    """Return a single job page or raise 404."""
    job = await session.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return templates.TemplateResponse(
        request,
        "detail.html",
        {"job": job},
    )
