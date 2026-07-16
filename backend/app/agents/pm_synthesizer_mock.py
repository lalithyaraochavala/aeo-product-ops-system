# MOCKED — replace with real Anthropic API call once billing is set up.
# Real version will send all four upstream agents' findings to Claude,
# asking it to synthesize a RICE-scored roadmap, a one-page PRD for the
# top item, and a plain-English stakeholder summary, returning this same
# JSON shape.

import hashlib


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


def _build_roadmap_item(title: str, description: str) -> dict:
    reach, impact, confidence, effort = _score(title)
    rice_score = round(reach * impact * confidence / effort, 2)
    return {
        "title": title,
        "description": description,
        "reach": reach,
        "impact": impact,
        "confidence": confidence,
        "effort": effort,
        "rice_score": rice_score,
    }


def _build_roadmap(
    technical_seo_output: dict,
    aeo_signal_output: dict,
    content_strategy_output: dict,
    competitive_intel_output: dict,
) -> list[dict]:
    items = []

    high_severity_issues = [
        issue for issue in technical_seo_output.get("issues", []) if issue.get("severity") == "high"
    ]
    for issue in high_severity_issues[:2]:
        items.append(_build_roadmap_item(
            title=f"Fix: {issue['issue']}",
            description=f"{issue['recommendation']} (Technical SEO Agent flagged this as high severity.)",
        ))

    uncited_queries = [q for q in aeo_signal_output.get("query_results", []) if not q.get("target_cited")]
    if uncited_queries:
        query = uncited_queries[0]
        items.append(_build_roadmap_item(
            title=f'Increase AEO visibility for "{query["query"]}"',
            description=f"{query['target_reasoning']} (AEO Signal Agent.)",
        ))

    queries_losing = competitive_intel_output.get("queries_losing", [])
    if queries_losing:
        losing = queries_losing[0]
        competitors = ", ".join(losing["winning_competitors"])
        items.append(_build_roadmap_item(
            title=f'Close competitive gap on "{losing["query"]}"',
            description=f"{competitors} are currently cited for this query while the target is not. (Competitive Intel Agent.)",
        ))

    existing_titles = {item["title"] for item in items}
    for rec in content_strategy_output.get("recommendations", []):
        title = f"Content fix: {rec['recommendation']}"
        based_on = rec.get("based_on", "").lower()
        is_technical_fix = any(keyword in based_on for keyword in ("json-ld", "meta description", "h1"))
        if title not in existing_titles and is_technical_fix:
            items.append(_build_roadmap_item(
                title=title,
                description=f"{rec['based_on']} (Content Strategy Agent.)",
            ))
            break

    if len(items) < 3:
        citation_rate = aeo_signal_output.get("citation_rate", 0)
        items.append(_build_roadmap_item(
            title="Establish an ongoing AEO monitoring cadence",
            description=f"Current citation rate is {citation_rate:.0%}. Re-run buyer query tests monthly to catch regressions and confirm fixes are working. (PM Synthesizer Agent.)",
        ))

    items.sort(key=lambda item: item["rice_score"], reverse=True)
    return items[:5]


def _build_prd(top_item: dict, aeo_signal_output: dict, competitive_intel_output: dict) -> dict:
    citation_rate = aeo_signal_output.get("citation_rate", 0)
    target_domain = aeo_signal_output.get("target_domain", "the target site")

    return {
        "title": top_item["title"],
        "problem_statement": (
            f"{target_domain} is currently cited in only {citation_rate:.0%} of the buyer queries tested. "
            f"{top_item['description']}"
        ),
        "proposed_solution": top_item["description"],
        "success_metric": (
            f"Citation rate for {target_domain} improves from {citation_rate:.0%} on the next AEO Signal re-test "
            f"of the same buyer queries."
        ),
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

    return (
        f"Right now, AI search tools cite {target_domain} in only {citation_rate:.0%} of the buyer questions we tested. "
        f"{narrative} "
        f"The single highest-priority fix is: {top_item['title']}. "
        f"We recommend starting there, then re-testing to confirm citation rates improve before moving to the rest of the roadmap."
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
    prd = _build_prd(roadmap[0], aeo_signal_output, competitive_intel_output)
    stakeholder_summary = _build_stakeholder_summary(roadmap, aeo_signal_output, competitive_intel_output)

    return {
        "roadmap": roadmap,
        "prd": prd,
        "stakeholder_summary": stakeholder_summary,
    }
