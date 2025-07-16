"""Scraper for OLX job listings."""

from __future__ import annotations

import json
from typing import List

import requests
from parsel import Selector
from sqlalchemy.exc import IntegrityError

from ..models import Job, async_session

BASE_URL = "https://www.olx.pl/praca/kierowca/"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def parse_jobs(html: str) -> List[dict]:
    """Parse jobs from OLX HTML listing."""
    sel = Selector(text=html)
    jobs = []
    for offer in sel.css(".css-1sw7q4x"):
        title = offer.css("a::text").get()
        url = offer.css("a::attr(href)").get()
        company = offer.css(".css-19yf5ek::text").get()
        city = offer.css(".css-1p8f3b8::text").get()
        salary = offer.css(".css-1q2w7lz::text").get()
        salary_min = salary_max = None
        if salary and "-" in salary:
            parts = salary.replace("zł", "").replace(" ", "").split("-")
            if len(parts) == 2:
                salary_min, salary_max = map(lambda x: int(x), parts)
        jobs.append(
            {
                "title": title,
                "url": url,
                "company": company,
                "city": city,
                "salary_min": salary_min,
                "salary_max": salary_max,
            }
        )
    return jobs


def scrape() -> None:  # pragma: no cover
    """Scrape OLX and save unique jobs to JSON Lines."""
    resp = requests.get(BASE_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    jobs = parse_jobs(resp.text)

    data_file = "data/jobs.jsonl"
    dup_file = "duplicates.log"

    async def _save() -> None:
        async with async_session() as session, \
            open(data_file, "a") as data_fp, \
            open(dup_file, "a") as dup_fp:
            for job in jobs:
                job_hash = Job.make_hash(
                    job["company"],
                    job["city"],
                    job["title"],
                )
                job["job_hash"] = job_hash
                try:
                    await session.execute(Job.__table__.insert().values(**job))
                    await session.commit()
                except IntegrityError:
                    await session.rollback()
                    dup_fp.write(json.dumps(job) + "\n")
                data_fp.write(json.dumps(job) + "\n")

    import asyncio

    asyncio.run(_save())
