# MOCKED — replace with real Anthropic API call once billing is set up.
# Real version will send the technical_seo and aeo_signal findings to
# Claude, asking it to propose specific content edits grounded in those
# findings, returning this same JSON shape.


def mock_generate_content_recommendations(technical_seo_output: dict, aeo_signal_output: dict) -> dict:
    recommendations = []

    if not technical_seo_output.get("raw_findings", {}).get("json_ld_present"):
        recommendations.append({
            "recommendation": "Add FAQPage or Product JSON-LD schema to the page.",
            "based_on": "Technical SEO Agent found no JSON-LD schema markup present.",
        })

    if not technical_seo_output.get("raw_findings", {}).get("meta_description"):
        recommendations.append({
            "recommendation": "Write a concise meta description that directly states what the page offers.",
            "based_on": "Technical SEO Agent found no meta description on the page.",
        })

    if technical_seo_output.get("raw_findings", {}).get("h1_count") == 0:
        recommendations.append({
            "recommendation": "Add a single, clear H1 stating the page's primary topic, with a direct-answer paragraph immediately below it.",
            "based_on": "Technical SEO Agent found no H1 heading on the page.",
        })

    for query_result in aeo_signal_output.get("query_results", []):
        if not query_result.get("target_cited"):
            recommendations.append({
                "recommendation": f"Add a direct-answer paragraph near the top of the page that explicitly answers \"{query_result['query']}\", so answer engines can extract it as a citable snippet.",
                "based_on": f"AEO Signal Agent found this page was not cited for the buyer query \"{query_result['query']}\".",
            })

    if len(recommendations) < 2:
        recommendations.append({
            "recommendation": "Add a comparison or buyer's-guide section covering how this product stacks up against alternatives.",
            "based_on": "No major technical SEO or citation gaps found; this strengthens AEO visibility further.",
        })

    # Cap at 4, prioritizing technical fixes first since they were added first
    recommendations = recommendations[:4]

    return {
        "summary": f"{len(recommendations)} content recommendation(s) generated from technical SEO and AEO signal findings.",
        "recommendations": recommendations,
    }
