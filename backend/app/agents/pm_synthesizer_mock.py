# MOCKED — replace with real Anthropic API call once billing is set up.
# Real version will send all four upstream agents' findings to Claude,
# asking it to synthesize a RICE-scored roadmap, a one-page PRD for the
# top item, and a plain-English stakeholder summary, returning this same
# JSON shape.

from __future__ import annotations

import hashlib
import re

# Keywords used to detect when a technical_seo issue and a content_strategy
# recommendation are about the same underlying topic, so we don't add both
# as separate roadmap items.
_TOPIC_KEYWORDS = {
    "json-ld": ["json-ld"],
    "meta_description": ["meta description"],
    "h1": ["h1 heading", "h1"],
}

# At or above this citation_rate, framing shifts from "close the gap" to
# "defend the lead" — "improves from 100%" or "only 100%" reads as
# contradictory, so text generation branches on this threshold.
_HIGH_CITATION_RATE_THRESHOLD = 0.7


def _citation_rate_clause(citation_rate: float, target_domain: str) -> str:
    """A standalone sentence describing current citation standing, framed
    appropriately for a low rate (a gap to close) vs. a high rate (a lead
    to defend)."""
    if citation_rate >= _HIGH_CITATION_RATE_THRESHOLD:
        return f"AI answer engines already cite {target_domain} in {citation_rate:.0%} of the buyer queries we tested"
    return f"AI answer engines cite {target_domain} in only {citation_rate:.0%} of the buyer queries we tested"


def _success_metric(citation_rate: float, target_domain: str) -> str:
    if citation_rate >= _HIGH_CITATION_RATE_THRESHOLD:
        return (
            f"Citation rate for {target_domain} holds at {citation_rate:.0%} or better on the next AEO Signal "
            f"re-test, confirming this strong position is defended rather than lost to competitors."
        )
    return (
        f"Citation rate for {target_domain} improves from {citation_rate:.0%} on the next AEO Signal re-test "
        f"of the same buyer queries."
    )


def _topic_for(text: str) -> str | None:
    text_lower = text.lower()
    for topic, keywords in _TOPIC_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return topic
    return None


def _strip_attribution(text: str) -> str:
    """Removes a trailing ' (X Agent....)' attribution note, for reuse in
    PRD prose where the inline attribution reads awkwardly."""
    return re.sub(r"\s*\([^)]*Agent[^)]*\)\s*$", "", text).strip()


def _score(seed: str) -> tuple[int, int, int, int]:
    """Deterministic 1-10 reach/impact/confidence/effort per item, so the
    same inputs always produce the same roadmap (stable for demos) while
    different findings still score differently."""
    digest = hashlib.sha256(seed.encode()).hexdigest()
    reach = 1 + int(digest[0:2], 16) % 10
    impact = 1 + int(digest[2:4], 16) % 10
    confidence = 1 + int(digest[4:6], 16) % 10
    effort = 1 + int(digest[6:8], 16) % 10
    return reach, impact, confidence, effort


def _build_roadmap_item(title: str, description: str, source: str) -> dict:
    reach, impact, confidence, effort = _score(title)
    rice_score = round(reach * impact * confidence / effort, 2)
    return {
        "title": title,
        "description": description,
        "source": source,  # internal only — not persisted to roadmap_items
        "reach": reach,
        "impact": impact,
        "confidence": confidence,
        "effort": effort,
        "rice_score": rice_score,
    }


def _competitive_intel_item(aeo_signal_output: dict, competitive_intel_output: dict, target_domain: str) -> dict:
    """Always produces one roadmap item from competitive_intel's findings,
    since it's a required upstream dependency and should always be
    represented — whether the target is losing a specific query, tied, or
    already leading."""
    queries_losing = competitive_intel_output.get("queries_losing", [])
    if queries_losing:
        losing = queries_losing[0]
        competitors = ", ".join(losing["winning_competitors"])
        return _build_roadmap_item(
            title=f'Close competitive gap on "{losing["query"]}"',
            description=f"{competitors} are currently cited for this query while {target_domain} is not. (Competitive Intel Agent.)",
            source="competitive_intel",
        )

    narrative = competitive_intel_output.get("narrative", "")
    return _build_roadmap_item(
        title="Strengthen citation-share position versus tracked competitors",
        description=f"{narrative} (Competitive Intel Agent.)",
        source="competitive_intel",
    )


def _build_roadmap(
    technical_seo_output: dict,
    aeo_signal_output: dict,
    content_strategy_output: dict,
    competitive_intel_output: dict,
) -> list[dict]:
    items = []
    covered_topics: set[str] = set()

    high_severity_issues = [
        issue for issue in technical_seo_output.get("issues", []) if issue.get("severity") == "high"
    ]
    for issue in high_severity_issues[:2]:
        topic = _topic_for(issue["issue"])
        if topic:
            covered_topics.add(topic)
        items.append(_build_roadmap_item(
            title=f"Fix: {issue['issue']}",
            description=f"{issue['recommendation']} (Technical SEO Agent flagged this as high severity.)",
            source="technical_seo",
        ))

    uncited_queries = [q for q in aeo_signal_output.get("query_results", []) if not q.get("target_cited")]
    if uncited_queries:
        query = uncited_queries[0]
        items.append(_build_roadmap_item(
            title=f'Increase AEO visibility for "{query["query"]}"',
            description=f"{query['target_reasoning']} (AEO Signal Agent.)",
            source="aeo_signal",
        ))

    target_domain = aeo_signal_output.get("target_domain", "the target site")
    items.append(_competitive_intel_item(aeo_signal_output, competitive_intel_output, target_domain))

    existing_titles = {item["title"] for item in items}
    for rec in content_strategy_output.get("recommendations", []):
        based_on = rec.get("based_on", "")
        based_on_lower = based_on.lower()
        if "buyer query" in based_on_lower:
            continue  # overlaps with the AEO Signal item already added above
        topic = _topic_for(based_on_lower)
        if topic and topic in covered_topics:
            continue  # same underlying issue as a technical_seo item already added
        title = f"Content fix: {rec['recommendation']}"
        if title in existing_titles:
            continue
        items.append(_build_roadmap_item(
            title=title,
            description=f"{based_on} (Content Strategy Agent.)",
            source="content_strategy",
        ))
        if topic:
            covered_topics.add(topic)
        break

    if len(items) < 3:
        citation_rate = aeo_signal_output.get("citation_rate", 0)
        items.append(_build_roadmap_item(
            title="Establish an ongoing AEO monitoring cadence",
            description=f"Current citation rate is {citation_rate:.0%}. Re-run buyer query tests monthly to catch regressions and confirm fixes are working. (PM Synthesizer Agent.)",
            source="monitoring",
        ))

    items.sort(key=lambda item: item["rice_score"], reverse=True)
    return items[:5]


def _build_prd(top_item: dict, aeo_signal_output: dict) -> dict:
    citation_rate = aeo_signal_output.get("citation_rate", 0)
    target_domain = aeo_signal_output.get("target_domain", "the target site")
    source = top_item.get("source")
    clean_description = _strip_attribution(top_item["description"])

    if source == "technical_seo":
        issue_name = top_item["title"].removeprefix("Fix: ")
        problem_statement = (
            f"{_citation_rate_clause(citation_rate, target_domain)}. The technical SEO audit found a likely "
            f"contributor: {issue_name}. Without it, answer engines have a harder time parsing what the page "
            f"is actually about."
        )
        proposed_solution = clean_description
    elif source == "aeo_signal":
        problem_statement = (
            f"{target_domain} is not currently cited for a real buyer query we tested ({top_item['title']}), "
            f"meaning a prospective buyer searching this way sees competitors' answers instead of ours."
        )
        proposed_solution = (
            "Add a direct-answer paragraph that explicitly and concisely answers this query near the top of "
            "the relevant page, formatted so an AI answer engine can extract it as a standalone citable snippet."
        )
    elif source == "competitive_intel":
        problem_statement = (
            f"On competitive citation standing: {clean_description} This puts {target_domain} at risk of "
            f"losing buyer mindshare to competitors who show up in AI-generated answers and we don't."
        )
        proposed_solution = (
            "Prioritize content and schema fixes on the specific queries where competitors are currently cited "
            f"and {target_domain} is not, closing the gap query-by-query rather than broadly."
        )
    elif source == "content_strategy":
        problem_statement = (
            f"{_citation_rate_clause(citation_rate, target_domain)}, and the page is missing on-page content "
            f"structure that AI answer engines typically pull citable answers from."
        )
        proposed_solution = clean_description
    else:  # monitoring fallback
        problem_statement = (
            f"{target_domain}'s AEO performance ({citation_rate:.0%} citation rate) hasn't been re-verified "
            f"since this audit, so regressions or improvements from future changes would go unnoticed."
        )
        proposed_solution = clean_description

    return {
        "title": top_item["title"],
        "problem_statement": problem_statement,
        "proposed_solution": proposed_solution,
        "success_metric": _success_metric(citation_rate, target_domain),
        "scope_in": [top_item["title"], "Re-testing the same buyer queries after the fix ships"],
        "scope_out": ["Unrelated roadmap items", "New buyer queries not already part of this run"],
    }


def _build_stakeholder_summary(
    roadmap: list[dict],
    aeo_signal_output: dict,
    competitive_intel_output: dict,
) -> str:
    citation_rate = aeo_signal_output.get("citation_rate", 0)
    target_domain = aeo_signal_output.get("target_domain", "our site")
    top_item = roadmap[0]
    narrative = competitive_intel_output.get("narrative", "")

    if citation_rate >= _HIGH_CITATION_RATE_THRESHOLD:
        closing = (
            "We recommend starting there to help defend this position, then re-testing to confirm citation "
            "rates hold steady before moving to the rest of the roadmap."
        )
    else:
        closing = (
            "We recommend starting there, then re-testing to confirm citation rates improve before moving to "
            "the rest of the roadmap."
        )

    return (
        f"Right now, {_citation_rate_clause(citation_rate, target_domain)}. "
        f"{narrative} "
        f"The single highest-priority action is: {top_item['title']}. "
        f"{closing}"
    )


def mock_synthesize(
    technical_seo_output: dict,
    aeo_signal_output: dict,
    content_strategy_output: dict,
    competitive_intel_output: dict,
) -> dict:
    roadmap = _build_roadmap(
        technical_seo_output, aeo_signal_output, content_strategy_output, competitive_intel_output
    )
    prd = _build_prd(roadmap[0], aeo_signal_output)
    stakeholder_summary = _build_stakeholder_summary(roadmap, aeo_signal_output, competitive_intel_output)

    return {
        "roadmap": roadmap,
        "prd": prd,
        "stakeholder_summary": stakeholder_summary,
    }
