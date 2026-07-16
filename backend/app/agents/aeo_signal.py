import uuid

from sqlmodel import Session

from ..models import Run
from .aeo_signal_mock import mock_test_citations


def run_aeo_signal_agent(run_id: uuid.UUID, session: Session) -> dict:
    run = session.get(Run, run_id)
    if run is None:
        raise ValueError(f"Run {run_id} not found")
    return mock_test_citations(run.target_url, run.competitor_urls, run.buyer_queries)
