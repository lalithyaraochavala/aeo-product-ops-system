import uuid

import requests
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from .agents.aeo_signal import run_aeo_signal_agent
from .agents.competitive_intel import run_competitive_intel_agent
from .agents.content_strategy import run_content_strategy_agent
from .agents.technical_seo import run_technical_seo_agent
from .db import create_db_and_tables, get_session
from .models import AgentResult, Run

app = FastAPI(title="AEO Product Ops System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/runs", response_model=Run)
def create_run(run: Run, session: Session = Depends(get_session)):
    run.id = uuid.uuid4()
    run.status = "pending"
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


@app.get("/runs", response_model=list[Run])
def list_runs(session: Session = Depends(get_session)):
    return session.exec(select(Run).order_by(Run.created_at.desc())).all()


@app.get("/runs/{run_id}", response_model=Run)
def get_run(run_id: uuid.UUID, session: Session = Depends(get_session)):
    run = session.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.post("/runs/{run_id}/technical-seo", response_model=AgentResult)
def run_technical_seo(run_id: uuid.UUID, session: Session = Depends(get_session)):
    run = session.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    try:
        output = run_technical_seo_agent(run.target_url)
        status = "success"
    except requests.RequestException as exc:
        output = {"error": str(exc)}
        status = "error"

    result = AgentResult(run_id=run.id, agent_name="technical_seo", raw_output=output, status=status)
    session.add(result)
    session.commit()
    session.refresh(result)
    return result


@app.post("/runs/{run_id}/aeo-signal", response_model=AgentResult)
def run_aeo_signal(run_id: uuid.UUID, session: Session = Depends(get_session)):
    run = session.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    try:
        output = run_aeo_signal_agent(run_id, session)
        status = "success"
    except ValueError as exc:
        output = {"error": str(exc)}
        status = "error"

    result = AgentResult(run_id=run.id, agent_name="aeo_signal", raw_output=output, status=status)
    session.add(result)
    session.commit()
    session.refresh(result)
    return result


@app.post("/runs/{run_id}/content-strategy", response_model=AgentResult)
def run_content_strategy(run_id: uuid.UUID, session: Session = Depends(get_session)):
    run = session.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    try:
        output = run_content_strategy_agent(run_id, session)
        status = "success"
    except ValueError as exc:
        output = {"error": str(exc)}
        status = "error"

    result = AgentResult(run_id=run.id, agent_name="content_strategy", raw_output=output, status=status)
    session.add(result)
    session.commit()
    session.refresh(result)
    return result


@app.post("/runs/{run_id}/competitive-intel", response_model=AgentResult)
def run_competitive_intel(run_id: uuid.UUID, session: Session = Depends(get_session)):
    run = session.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    try:
        output = run_competitive_intel_agent(run_id, session)
        status = "success"
    except ValueError as exc:
        output = {"error": str(exc)}
        status = "error"

    result = AgentResult(run_id=run.id, agent_name="competitive_intel", raw_output=output, status=status)
    session.add(result)
    session.commit()
    session.refresh(result)
    return result
