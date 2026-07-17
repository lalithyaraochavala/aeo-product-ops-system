from __future__ import annotations

import re
import uuid

from sqlmodel import Session, select

from .db import get_latest_agent_result
from .models import RoadmapItem, Run


def _extract_quoted_query(title: str) -> str | None:
    match = re.search(r'"([^"]+)"', title)
    return match.group(1) if match else None


def resolve_parent_roadmap_items(session: Session, run: Run) -> None:
    """After a re-run's agents complete, checks whether the parent run's
    open roadmap items are resolved by the new data, closing the
    before/after loop. Matches on each item's title pattern against the
    specific finding it was generated from (see pm_synthesizer_mock.py):
    a technical_seo issue name, an aeo_signal query now cited, or a
    competitive_intel query no longer being lost. Items that don't match
    one of those specific patterns (e.g. a generic content or monitoring
    item) fall back to resolving only if the overall citation rate
    improved, since there's no more specific signal to check them against."""
    if run.parent_run_id is None:
        return

    open_items = session.exec(
        select(RoadmapItem).where(RoadmapItem.run_id == run.parent_run_id, RoadmapItem.status == "open")
    ).all()
    if not open_items:
        return

    technical_seo_result = get_latest_agent_result(session, run.id, "technical_seo")
    aeo_signal_result = get_latest_agent_result(session, run.id, "aeo_signal")
    competitive_intel_result = get_latest_agent_result(session, run.id, "competitive_intel")

    new_issue_names = set()
    if technical_seo_result and technical_seo_result.status == "success":
        new_issue_names = {issue["issue"] for issue in technical_seo_result.raw_output.get("issues", [])}

    new_cited_queries = set()
    citation_rate_improved = False
    if aeo_signal_result and aeo_signal_result.status == "success":
        new_cited_queries = {
            q["query"] for q in aeo_signal_result.raw_output.get("query_results", []) if q.get("target_cited")
        }
        parent_aeo_signal_result = get_latest_agent_result(session, run.parent_run_id, "aeo_signal")
        if parent_aeo_signal_result and parent_aeo_signal_result.status == "success":
            citation_rate_improved = aeo_signal_result.raw_output.get(
                "citation_rate", 0
            ) > parent_aeo_signal_result.raw_output.get("citation_rate", 0)

    new_losing_queries = set()
    if competitive_intel_result and competitive_intel_result.status == "success":
        new_losing_queries = {q["query"] for q in competitive_intel_result.raw_output.get("queries_losing", [])}

    for item in open_items:
        if item.title.startswith("Fix: "):
            issue_name = item.title.removeprefix("Fix: ")
            resolved = issue_name not in new_issue_names
        elif item.title.startswith("Increase AEO visibility for "):
            query = _extract_quoted_query(item.title)
            resolved = query is not None and query in new_cited_queries
        elif item.title.startswith("Close competitive gap on "):
            query = _extract_quoted_query(item.title)
            resolved = query is not None and query not in new_losing_queries
        else:
            resolved = citation_rate_improved

        if resolved:
            item.status = "resolved"
            session.add(item)

    session.commit()


def build_comparison(session: Session, run: Run) -> dict | None:
    """Returns before/after citation-rate data and the parent run's
    roadmap (with resolved/open status) for the report page's comparison
    view, or None if this run isn't a re-run or the needed data isn't
    available yet."""
    if run.parent_run_id is None:
        return None

    parent_aeo_signal_result = get_latest_agent_result(session, run.parent_run_id, "aeo_signal")
    current_aeo_signal_result = get_latest_agent_result(session, run.id, "aeo_signal")
    if (
        parent_aeo_signal_result is None
        or parent_aeo_signal_result.status != "success"
        or current_aeo_signal_result is None
        or current_aeo_signal_result.status != "success"
    ):
        return None

    parent_roadmap = session.exec(
        select(RoadmapItem).where(RoadmapItem.run_id == run.parent_run_id).order_by(RoadmapItem.rice_score.desc())
    ).all()

    return {
        "parent_run_id": str(run.parent_run_id),
        "citation_rate_before": parent_aeo_signal_result.raw_output.get("citation_rate", 0),
        "citation_rate_after": current_aeo_signal_result.raw_output.get("citation_rate", 0),
        "parent_roadmap": [
            {
                "id": str(item.id),
                "title": item.title,
                "status": item.status,
            }
            for item in parent_roadmap
        ],
    }
