# MOCKED — replace with real Anthropic web_search API call once billing is set up.
# Real version will send each buyer query to Claude with the web_search tool,
# then inspect the returned citations/sources for the target and competitor
# domains, returning this same JSON shape.

import hashlib
from urllib.parse import urlparse


def _domain(url: str) -> str:
    return urlparse(url).netloc or url


def _deterministic_cited(domain: str, query: str) -> bool:
    """Pseudo-random but reproducible per (domain, query) pair, so repeat
    runs against the same inputs are stable while different domains/queries
    still vary — a believable stand-in for real citation variance."""
    digest = hashlib.sha256(f"{domain}::{query}".encode()).hexdigest()
    return int(digest[:8], 16) % 100 < 55  # ~55% cited rate


def _reasoning(domain: str, query: str, cited: bool) -> str:
    if cited:
        return f"{domain} appeared as a cited source for \"{query}\", likely due to clear on-page answers to this query."
    return f"{domain} was not cited for \"{query}\" — the answer engine favored sources with more direct, structured coverage of this topic."


def mock_test_citations(target_url: str, competitor_urls: list[str], buyer_queries: list[str]) -> dict:
    target_domain = _domain(target_url)
    query_results = []

    for query in buyer_queries:
        target_cited = _deterministic_cited(target_domain, query)
        competitor_results = []
        for competitor_url in competitor_urls:
            competitor_domain = _domain(competitor_url)
            competitor_cited = _deterministic_cited(competitor_domain, query)
            competitor_results.append({
                "url": competitor_url,
                "cited": competitor_cited,
                "reasoning": _reasoning(competitor_domain, query, competitor_cited),
            })

        query_results.append({
            "query": query,
            "target_cited": target_cited,
            "target_reasoning": _reasoning(target_domain, query, target_cited),
            "competitors": competitor_results,
        })

    cited_count = sum(1 for q in query_results if q["target_cited"])
    total = len(query_results)
    citation_rate = round(cited_count / total, 2) if total else 0.0

    return {
        "target_domain": target_domain,
        "citation_rate": citation_rate,
        "summary": f"{target_domain} was cited in {cited_count} of {total} buyer queries tested.",
        "query_results": query_results,
    }
