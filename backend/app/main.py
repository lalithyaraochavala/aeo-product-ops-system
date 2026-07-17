import uuid

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from .agent_runner import run_and_persist_agent
from .agents.aeo_signal import run_aeo_signal_agent
from .agents.competitive_intel import run_competitive_intel_agent
from .agents.content_strategy import run_content_strategy_agent
from .agents.pm_synthesizer import run_pm_synthesizer_agent
from .agents.technical_seo import run_technical_seo_agent
from .db import create_db_and_tables, get_latest_agent_result, get_session
from .models import AgentResult, RoadmapItem, Run, RunCreate
from .orchestrator import run_full_pipeline

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
def create_run(payload: RunCreate, session: Session = Depends(get_session)):
    run = Run(
        target_url=payload.target_url,
        competitor_urls=payload.competitor_urls,
        buyer_queries=payload.buyer_queries,
    )
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


def _get_run_or_404(run_id: uuid.UUID, session: Session) -> Run:
    run = session.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.post("/runs/{run_id}/technical-seo", response_model=AgentResult)
def run_technical_seo(run_id: uuid.UUID, session: Session = Depends(get_session)):
    run = _get_run_or_404(run_id, session)
    return run_and_persist_agent(session, run, "technical_seo", lambda: run_technical_seo_agent(run.target_url))


@app.post("/runs/{run_id}/aeo-signal", response_model=AgentResult)
def run_aeo_signal(run_id: uuid.UUID, session: Session = Depends(get_session)):
    run = _get_run_or_404(run_id, session)
    return run_and_persist_agent(session, run, "aeo_signal", lambda: run_aeo_signal_agent(run_id, session))


@app.post("/runs/{run_id}/content-strategy", response_model=AgentResult)
def run_content_strategy(run_id: uuid.UUID, session: Session = Depends(get_session)):
    run = _get_run_or_404(run_id, session)
    return run_and_persist_agent(session, run, "content_strategy", lambda: run_content_strategy_agent(run_id, session))


@app.post("/runs/{run_id}/competitive-intel", response_model=AgentResult)
def run_competitive_intel(run_id: uuid.UUID, session: Session = Depends(get_session)):
    run = _get_run_or_404(run_id, session)
    return run_and_persist_agent(session, run, "competitive_intel", lambda: run_competitive_intel_agent(run_id, session))


@app.post("/runs/{run_id}/synthesize", response_model=AgentResult)
def synthesize(run_id: uuid.UUID, session: Session = Depends(get_session)):
    run = _get_run_or_404(run_id, session)
    result = run_and_persist_agent(session, run, "pm_synthesizer", lambda: run_pm_synthesizer_agent(run_id, session))

    if result.status == "success":
        for item in result.raw_output["roadmap"]:
            session.add(RoadmapItem(
                run_id=run.id,
                title=item["title"],
                reach=item["reach"],
                impact=item["impact"],
                confidence=item["confidence"],
                effort=item["effort"],
                rice_score=item["rice_score"],
                description=item["description"],
                status="open",
            ))
        session.commit()

    return result


@app.get("/runs/{run_id}/roadmap", response_model=list[RoadmapItem])
def get_roadmap(run_id: uuid.UUID, session: Session = Depends(get_session)):
    _get_run_or_404(run_id, session)
    return session.exec(
        select(RoadmapItem).where(RoadmapItem.run_id == run_id).order_by(RoadmapItem.rice_score.desc())
    ).all()


@app.post("/runs/{run_id}/run-full-pipeline")
def run_full_pipeline_endpoint(run_id: uuid.UUID, session: Session = Depends(get_session)):
    _get_run_or_404(run_id, session)
    return run_full_pipeline(run_id, session)


@app.get("/runs/{run_id}/report")
def get_report(run_id: uuid.UUID, session: Session = Depends(get_session)):
    _get_run_or_404(run_id, session)
    result = get_latest_agent_result(session, run_id, "pm_synthesizer")
    if result is None or result.status != "success":
        raise HTTPException(status_code=404, detail="No completed synthesis report for this run yet")
    return result.raw_output
