import uuid

from sqlmodel import Session

from .agent_runner import run_and_persist_agent
from .agents.aeo_signal import run_aeo_signal_agent
from .agents.competitive_intel import run_competitive_intel_agent
from .agents.content_strategy import run_content_strategy_agent
from .agents.pm_synthesizer import run_pm_synthesizer_agent
from .agents.technical_seo import run_technical_seo_agent
from .models import RoadmapItem, Run

# Agents run in dependency order: content_strategy needs technical_seo +
# aeo_signal, competitive_intel needs aeo_signal, and pm_synthesizer needs
# all four. Each entry is (agent_name, callable taking (run, session)).
_PIPELINE_STEPS = [
    ("technical_seo", lambda run, session: run_technical_seo_agent(run.target_url)),
    ("aeo_signal", lambda run, session: run_aeo_signal_agent(run.id, session)),
    ("content_strategy", lambda run, session: run_content_strategy_agent(run.id, session)),
    ("competitive_intel", lambda run, session: run_competitive_intel_agent(run.id, session)),
]


def run_full_pipeline(run_id: uuid.UUID, session: Session) -> dict:
    run = session.get(Run, run_id)
    if run is None:
        raise ValueError(f"Run {run_id} not found")

    run.status = "running"
    session.add(run)
    session.commit()

    steps = []
    for agent_name, agent_fn in _PIPELINE_STEPS:
        result = run_and_persist_agent(session, run, agent_name, lambda: agent_fn(run, session))
        steps.append({"agent": agent_name, "status": result.status})

    # PM Synthesizer always runs, even if earlier agents failed — it has its
    # own dependency check (all four prior results must exist) and fails
    # gracefully on its own if that check doesn't pass.
    synth_result = run_and_persist_agent(
        session, run, "pm_synthesizer", lambda: run_pm_synthesizer_agent(run.id, session)
    )
    steps.append({"agent": "pm_synthesizer", "status": synth_result.status})

    if synth_result.status == "success":
        for item in synth_result.raw_output["roadmap"]:
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

    if synth_result.status == "error":
        run.status = "failed"
    elif all(step["status"] == "success" for step in steps):
        run.status = "complete"
    else:
        run.status = "partial"
    session.add(run)
    session.commit()

    return {
        "run_id": str(run.id),
        "status": run.status,
        "steps": steps,
        "synthesizer_output": synth_result.raw_output if synth_result.status == "success" else None,
    }
