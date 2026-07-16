import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Run(SQLModel, table=True):
    __tablename__ = "runs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    target_url: str
    competitor_urls: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    buyer_queries: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: str = Field(default="pending")  # pending/running/complete/failed
    created_at: datetime = Field(default_factory=_now)
    parent_run_id: Optional[uuid.UUID] = Field(default=None, foreign_key="runs.id", index=True)


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
