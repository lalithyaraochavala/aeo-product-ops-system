from typing import Callable

import requests
from sqlmodel import Session

from .models import AgentResult, Run


def run_and_persist_agent(
    session: Session, run: Run, agent_name: str, agent_fn: Callable[[], dict]
) -> AgentResult:
    try:
        output = agent_fn()
        status = "success"
    except (requests.RequestException, ValueError) as exc:
        output = {"error": str(exc)}
        status = "error"

    result = AgentResult(run_id=run.id, agent_name=agent_name, raw_output=output, status=status)
    session.add(result)
    session.commit()
    session.refresh(result)
    return result
