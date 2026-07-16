import uuid

from sqlmodel import Session

from ..db import get_latest_agent_result
from .pm_synthesizer_mock import mock_synthesize

REQUIRED_AGENTS = ["technical_seo", "aeo_signal", "content_strategy", "competitive_intel"]


def run_pm_synthesizer_agent(run_id: uuid.UUID, session: Session) -> dict:
    results = {name: get_latest_agent_result(session, run_id, name) for name in REQUIRED_AGENTS}
    missing = [name for name, result in results.items() if result is None]
    if missing:
        raise ValueError(f"Missing prior agent result(s) for this run: {', '.join(missing)} — run those agents first.")

    return mock_synthesize(
        technical_seo_output=results["technical_seo"].raw_output,
        aeo_signal_output=results["aeo_signal"].raw_output,
        content_strategy_output=results["content_strategy"].raw_output,
        competitive_intel_output=results["competitive_intel"].raw_output,
    )
