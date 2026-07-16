import uuid

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from .db import create_db_and_tables, get_session
from .models import Run

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
