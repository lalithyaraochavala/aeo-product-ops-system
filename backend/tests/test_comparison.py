from sqlmodel import Session, SQLModel, create_engine

from app.comparison import build_comparison, resolve_parent_roadmap_items
from app.models import AgentResult, RoadmapItem, Run


def _make_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def _make_run(session, parent_run_id=None):
    run = Run(target_url="https://acme.com", competitor_urls=[], buyer_queries=["best widget"], parent_run_id=parent_run_id)
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def test_resolve_parent_roadmap_items_flips_matching_items_to_resolved():
    session = _make_session()
    parent = _make_run(session)
    child = _make_run(session, parent_run_id=parent.id)

    # Parent's original roadmap: one item per matchable source type, all open.
    items = [
        RoadmapItem(run_id=parent.id, title="Fix: No JSON-LD schema markup detected", description="d",
                    reach=1, impact=1, confidence=1, effort=1, rice_score=1.0, status="open"),
        RoadmapItem(run_id=parent.id, title='Increase AEO visibility for "best widget"', description="d",
                    reach=1, impact=1, confidence=1, effort=1, rice_score=1.0, status="open"),
        RoadmapItem(run_id=parent.id, title='Close competitive gap on "best widget"', description="d",
                    reach=1, impact=1, confidence=1, effort=1, rice_score=1.0, status="open"),
        RoadmapItem(run_id=parent.id, title="Content fix: add a buyer's guide", description="d",
                    reach=1, impact=1, confidence=1, effort=1, rice_score=1.0, status="open"),
    ]
    for item in items:
        session.add(item)
    session.commit()

    # Parent's aeo_signal result (needed as the "before" citation rate baseline).
    session.add(AgentResult(run_id=parent.id, agent_name="aeo_signal", status="success", raw_output={
        "target_domain": "acme.com", "citation_rate": 0.0,
        "query_results": [{"query": "best widget", "target_cited": False}],
    }))

    # Child's fresh results: the JSON-LD issue is gone, the query is now cited,
    # and it's no longer a losing query — everything specific should resolve.
    # The generic "Content fix" item has no specific signal to check, so it
    # only resolves via the overall citation_rate improving (which it did:
    # 0.0 -> 1.0), so it should resolve too.
    session.add(AgentResult(run_id=child.id, agent_name="technical_seo", status="success", raw_output={
        "issues": [],  # no more issues — the JSON-LD one is resolved
    }))
    session.add(AgentResult(run_id=child.id, agent_name="aeo_signal", status="success", raw_output={
        "target_domain": "acme.com", "citation_rate": 1.0,
        "query_results": [{"query": "best widget", "target_cited": True}],
    }))
    session.add(AgentResult(run_id=child.id, agent_name="competitive_intel", status="success", raw_output={
        "queries_losing": [],  # no longer losing
    }))
    session.commit()

    resolve_parent_roadmap_items(session, child)

    session.refresh(items[0])
    session.refresh(items[1])
    session.refresh(items[2])
    session.refresh(items[3])
    assert items[0].status == "resolved"
    assert items[1].status == "resolved"
    assert items[2].status == "resolved"
    assert items[3].status == "resolved"


def test_resolve_parent_roadmap_items_leaves_unresolved_items_open():
    session = _make_session()
    parent = _make_run(session)
    child = _make_run(session, parent_run_id=parent.id)

    item = RoadmapItem(run_id=parent.id, title="Fix: No JSON-LD schema markup detected", description="d",
                        reach=1, impact=1, confidence=1, effort=1, rice_score=1.0, status="open")
    session.add(item)
    session.commit()

    session.add(AgentResult(run_id=parent.id, agent_name="aeo_signal", status="success", raw_output={
        "citation_rate": 0.0, "query_results": [],
    }))
    # Child still has the same issue — nothing resolved.
    session.add(AgentResult(run_id=child.id, agent_name="technical_seo", status="success", raw_output={
        "issues": [{"issue": "No JSON-LD schema markup detected"}],
    }))
    session.add(AgentResult(run_id=child.id, agent_name="aeo_signal", status="success", raw_output={
        "citation_rate": 0.0, "query_results": [],
    }))
    session.commit()

    resolve_parent_roadmap_items(session, child)

    session.refresh(item)
    assert item.status == "open"


def test_resolve_parent_roadmap_items_is_noop_for_non_rerun():
    session = _make_session()
    run = _make_run(session)
    # Should not raise even with no parent and no agent results at all.
    resolve_parent_roadmap_items(session, run)


def test_build_comparison_returns_none_when_not_a_rerun():
    session = _make_session()
    run = _make_run(session)
    assert build_comparison(session, run) is None


def test_build_comparison_returns_before_after_and_parent_roadmap():
    session = _make_session()
    parent = _make_run(session)
    child = _make_run(session, parent_run_id=parent.id)

    session.add(RoadmapItem(run_id=parent.id, title="Fix: X", description="d",
                             reach=1, impact=1, confidence=1, effort=1, rice_score=1.0, status="resolved"))
    session.add(AgentResult(run_id=parent.id, agent_name="aeo_signal", status="success",
                            raw_output={"citation_rate": 0.2}))
    session.add(AgentResult(run_id=child.id, agent_name="aeo_signal", status="success",
                            raw_output={"citation_rate": 0.8}))
    session.commit()

    comparison = build_comparison(session, child)
    assert comparison is not None
    assert comparison["citation_rate_before"] == 0.2
    assert comparison["citation_rate_after"] == 0.8
    assert comparison["parent_run_id"] == str(parent.id)
    assert len(comparison["parent_roadmap"]) == 1
    assert comparison["parent_roadmap"][0]["status"] == "resolved"
