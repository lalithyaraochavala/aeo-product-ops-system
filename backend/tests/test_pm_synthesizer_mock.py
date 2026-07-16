from app.agents.pm_synthesizer_mock import mock_synthesize

TECHNICAL_SEO_OUTPUT = {
    "issues": [
        {"severity": "high", "issue": "No JSON-LD schema markup detected", "recommendation": "Add JSON-LD structured data."},
    ],
}
AEO_SIGNAL_OUTPUT = {
    "target_domain": "acme.com",
    "citation_rate": 0.0,
    "query_results": [
        {
            "query": "best widget",
            "target_cited": False,
            "target_reasoning": "acme.com was not cited for \"best widget\".",
            "competitors": [{"url": "https://competitor.com", "cited": True, "reasoning": "competitor.com was cited."}],
        },
    ],
}
CONTENT_STRATEGY_OUTPUT = {
    "recommendations": [
        {"recommendation": "Add FAQPage or Product JSON-LD schema to the page.", "based_on": "Technical SEO Agent found no JSON-LD schema markup present."},
        {"recommendation": "Add a direct-answer paragraph.", "based_on": "AEO Signal Agent found this page was not cited for the buyer query \"best widget\"."},
    ],
}
COMPETITIVE_INTEL_OUTPUT = {
    "citation_share": {"acme.com": 0.0, "https://competitor.com": 1.0},
    "queries_losing": [{"query": "best widget", "winning_competitors": ["https://competitor.com"]}],
    "narrative": "https://competitor.com currently leads citation share over acme.com.",
}


def test_technical_seo_and_content_strategy_duplicate_are_not_both_included():
    result = mock_synthesize(
        TECHNICAL_SEO_OUTPUT, AEO_SIGNAL_OUTPUT, CONTENT_STRATEGY_OUTPUT, COMPETITIVE_INTEL_OUTPUT
    )
    json_ld_items = [item for item in result["roadmap"] if "json-ld" in item["title"].lower()]
    assert len(json_ld_items) == 1


def test_roadmap_always_includes_a_competitive_intel_item():
    result = mock_synthesize(
        TECHNICAL_SEO_OUTPUT, AEO_SIGNAL_OUTPUT, CONTENT_STRATEGY_OUTPUT, COMPETITIVE_INTEL_OUTPUT
    )
    sources = [item["source"] for item in result["roadmap"]]
    assert "competitive_intel" in sources


def test_roadmap_includes_competitive_intel_item_even_with_no_losing_queries():
    competitive_intel_no_losses = {
        "citation_share": {"acme.com": 1.0, "https://competitor.com": 1.0},
        "queries_losing": [],
        "narrative": "It's a tie for citation share leadership between acme.com, https://competitor.com.",
    }
    result = mock_synthesize(
        TECHNICAL_SEO_OUTPUT, AEO_SIGNAL_OUTPUT, CONTENT_STRATEGY_OUTPUT, competitive_intel_no_losses
    )
    sources = [item["source"] for item in result["roadmap"]]
    assert "competitive_intel" in sources


def test_prd_problem_statement_and_proposed_solution_are_not_duplicates():
    result = mock_synthesize(
        TECHNICAL_SEO_OUTPUT, AEO_SIGNAL_OUTPUT, CONTENT_STRATEGY_OUTPUT, COMPETITIVE_INTEL_OUTPUT
    )
    prd = result["prd"]
    assert prd["problem_statement"] != prd["proposed_solution"]
    assert "JSON-LD structured data" in prd["proposed_solution"]
    assert "citing" in prd["problem_statement"].lower()
