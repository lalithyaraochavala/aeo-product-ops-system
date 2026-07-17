import uuid
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

from pydantic import BaseModel, field_validator
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _require_valid_url(value: str) -> str:
    """Rejects malformed URLs at the API boundary. Without this, a
    non-standard input (e.g. a markdown-wrapped link like
    "[label](https://example.com)" pasted into the URL field) parses to an
    empty netloc, and downstream code that falls back to the raw input on
    parse failure ends up embedding that raw garbage — brackets and all —
    into every generated report string."""
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"'{value}' is not a valid http(s) URL")
    return value


class Run(SQLModel, table=True):
    __tablename__ = "runs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    target_url: str
    competitor_urls: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    buyer_queries: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: str = Field(default="pending")  # pending/running/complete/failed
    created_at: datetime = Field(default_factory=_now)
    parent_run_id: Optional[uuid.UUID] = Field(default=None, foreign_key="runs.id", index=True)


class RunCreate(BaseModel):
    """Request body for POST /runs. A plain (non-table) Pydantic model,
    because SQLModel's table=True classes (like Run above) bypass Pydantic
    field validation on construction — validators on Run itself would
    silently never run."""

    target_url: str
    competitor_urls: list[str] = []
    buyer_queries: list[str] = []

    @field_validator("target_url")
    @classmethod
    def _validate_target_url(cls, v: str) -> str:
        return _require_valid_url(v)

    @field_validator("competitor_urls")
    @classmethod
    def _validate_competitor_urls(cls, v: list[str]) -> list[str]:
        for url in v:
            _require_valid_url(url)
        return v


class AgentResult(SQLModel, table=True):
    __tablename__ = "agent_results"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    run_id: uuid.UUID = Field(foreign_key="runs.id", index=True)
    agent_name: str  # technical_seo/aeo_signal/content_strategy/competitive_intel/pm_synthesizer
    raw_output: dict = Field(default_factory=dict, sa_column=Column(JSON))
    status: str = Field(default="success")  # success/error
    created_at: datetime = Field(default_factory=_now)


class RoadmapItem(SQLModel, table=True):
    __tablename__ = "roadmap_items"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    run_id: uuid.UUID = Field(foreign_key="runs.id", index=True)
    title: str
    reach: int
    impact: int
    confidence: int
    effort: int
    rice_score: float
    description: str
    status: str = Field(default="open")  # open/resolved
