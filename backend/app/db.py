import os
import uuid

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine, select

from .models import AgentResult

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./aeo.db"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def get_latest_agent_result(session: Session, run_id: uuid.UUID, agent_name: str):
    return session.exec(
        select(AgentResult)
        .where(AgentResult.run_id == run_id, AgentResult.agent_name == agent_name)
        .order_by(AgentResult.created_at.desc())
    ).first()
