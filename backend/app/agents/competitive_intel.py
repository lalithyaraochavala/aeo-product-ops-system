import uuid

from sqlmodel import Session

from ..db import get_latest_agent_result
from .competitive_intel_mock import mock_generate_competitive_benchmark


def run_competitive_intel_agent(run_id: uuid.UUID, session: Session) -> dict:
    aeo_signal_result = get_latest_agent_result(session, run_id, "aeo_signal")

    if aeo_signal_result is None:
        raise ValueError("No aeo_signal result found for this run — run that agent first.")

    return mock_generate_competitive_benchmark(aeo_signal_result.raw_output)
