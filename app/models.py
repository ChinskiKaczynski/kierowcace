from __future__ import annotations

import hashlib
import os
from typing import Optional

from sqlalchemy import Column, Integer, MetaData, Text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///data/jobs.db")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False},
)

async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base(metadata=MetaData())


def slug(text: str) -> str:
    """Return a slugified version of the provided text."""
    return "".join(c if c.isalnum() else "-" for c in text.lower())


class Job(Base):
    """SQLAlchemy model for job postings."""

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    company = Column(Text, nullable=False)
    city = Column(Text)
    title = Column(Text)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    url = Column(Text)
    job_hash = Column(Text, unique=True)

    @staticmethod
    def make_hash(company: str, city: Optional[str], title: str) -> str:
        """Compute unique job hash from fields."""
        base = f"{company}|{city or ''}|{slug(title)}"
        return hashlib.sha256(base.encode()).hexdigest()
