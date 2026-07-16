# MOCKED — replace with real Anthropic API call once billing is set up.
# Real version will send the aeo_signal per-competitor citation data to
# Claude, asking it to synthesize a competitive benchmark narrative,
# returning this same JSON shape.


def mock_generate_competitive_benchmark(aeo_signal_output: dict) -> dict:
    query_results = aeo_signal_output.get("query_results", [])
    target_domain = aeo_signal_output.get("target_domain", "the target site")

    citation_counts: dict[str, int] = {target_domain: 0}
    losing_queries = []

    for query_result in query_results:
        target_cited = query_result.get("target_cited", False)
        if target_cited:
            citation_counts[target_domain] += 1

        winning_competitors = []
        for competitor in query_result.get("competitors", []):
            domain = competitor["url"]
            citation_counts.setdefault(domain, 0)
            if competitor.get("cited"):
                citation_counts[domain] += 1
                if not target_cited:
                    winning_competitors.append(domain)

        if winning_competitors:
            losing_queries.append({
                "query": query_result["query"],
                "winning_competitors": winning_competitors,
            })

    total_queries = len(query_results) or 1
    citation_share = {
        domain: round(count / total_queries, 2) for domain, count in citation_counts.items()
    }

    if citation_share:
        top_share = max(citation_share.values())
        leaders = [domain for domain, share in citation_share.items() if share == top_share]
    else:
        top_share = 0
        leaders = [target_domain]

    if top_share == 0:
        narrative = "No domain was cited for the queries tested — there's no established citation leader yet, which is an opportunity to be the first cited source."
    elif len(leaders) > 1:
        tied_domains = ", ".join(leaders)
        narrative = f"It's a tie for citation share leadership between {tied_domains}. No single domain has pulled ahead yet."
    elif leaders[0] == target_domain:
        narrative = f"{target_domain} currently leads citation share among the tracked domains, but should keep closing gaps on the queries listed below."
    else:
        leader = leaders[0]
        narrative = f"{leader} currently leads citation share over {target_domain}. The clearest opportunity is closing the gap on the queries where competitors are cited and {target_domain} is not."

    return {
        "citation_share": citation_share,
        "queries_losing": losing_queries,
        "narrative": narrative,
    }
