from app.agents.competitive_intel_mock import mock_generate_competitive_benchmark


def test_all_zero_citation_share_is_reported_as_no_leader():
    aeo_signal_output = {
        "target_domain": "acme.com",
        "query_results": [
            {
                "query": "best widget",
                "target_cited": False,
                "competitors": [{"url": "https://competitor.com", "cited": False}],
            }
        ],
    }

    result = mock_generate_competitive_benchmark(aeo_signal_output)

    assert result["citation_share"] == {"acme.com": 0.0, "https://competitor.com": 0.0}
    assert "leads" not in result["narrative"]
    assert "no domain was cited" in result["narrative"].lower()


def test_nonzero_tie_is_reported_as_a_tie():
    aeo_signal_output = {
        "target_domain": "acme.com",
        "query_results": [
            {
                "query": "best widget",
                "target_cited": True,
                "competitors": [{"url": "https://competitor.com", "cited": True}],
            }
        ],
    }

    result = mock_generate_competitive_benchmark(aeo_signal_output)

    assert result["citation_share"] == {"acme.com": 1.0, "https://competitor.com": 1.0}
    assert "tie" in result["narrative"].lower()


def test_clear_leader_still_reported_correctly():
    aeo_signal_output = {
        "target_domain": "acme.com",
        "query_results": [
            {
                "query": "best widget",
                "target_cited": False,
                "competitors": [{"url": "https://competitor.com", "cited": True}],
            }
        ],
    }

    result = mock_generate_competitive_benchmark(aeo_signal_output)

    assert result["citation_share"] == {"acme.com": 0.0, "https://competitor.com": 1.0}
    assert "https://competitor.com currently leads" in result["narrative"]
