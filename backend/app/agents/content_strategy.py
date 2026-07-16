import uuid

from sqlmodel import Session

from ..db import get_latest_agent_result
from .content_strategy_mock import mock_generate_content_recommendations


def run_content_strategy_agent(run_id: uuid.UUID, session: Session) -> dict:
    technical_seo_result = get_latest_agent_result(session, run_id, "technical_seo")
    aeo_signal_result = get_latest_agent_result(session, run_id, "aeo_signal")

    if technical_seo_result is None:
        raise ValueError("No technical_seo result found for this run — run that agent first.")
    if aeo_signal_result is None:
        raise ValueError("No aeo_signal result found for this run — run that agent first.")

    return mock_generate_content_recommendations(technical_seo_result.raw_output, aeo_signal_result.raw_output)
