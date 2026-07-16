# MOCKED — replace with real Anthropic API call once billing is set up.
# Real version will send `findings` to Claude with a system prompt asking it
# to interpret the parsed SEO signals and return this same JSON shape.


def mock_interpret_technical_seo(findings: dict) -> dict:
    issues = []

    if not findings["json_ld_present"]:
        issues.append({
            "severity": "high",
            "issue": "No JSON-LD schema markup detected",
            "recommendation": "Add JSON-LD structured data (e.g. Product, Organization, or FAQPage schema) so AI answer engines can parse page entities directly.",
        })

    if not findings["title"]:
        issues.append({
            "severity": "high",
            "issue": "Missing <title> tag",
            "recommendation": "Add a descriptive, keyword-relevant title tag.",
        })

    if not findings["meta_description"]:
        issues.append({
            "severity": "medium",
            "issue": "Missing meta description",
            "recommendation": "Add a concise meta description summarizing the page's core value proposition.",
        })

    if findings["h1_count"] == 0:
        issues.append({
            "severity": "medium",
            "issue": "No H1 heading found",
            "recommendation": "Add a single, clear H1 that states the page's primary topic.",
        })
    elif findings["h1_count"] > 1:
        issues.append({
            "severity": "low",
            "issue": f"{findings['h1_count']} H1 headings found",
            "recommendation": "Use a single H1 per page; demote extras to H2/H3.",
        })

    score = max(0, 100 - 25 * len([i for i in issues if i["severity"] == "high"])
                - 10 * len([i for i in issues if i["severity"] == "medium"])
                - 5 * len([i for i in issues if i["severity"] == "low"]))

    return {
        "summary": f"Found {len(issues)} technical SEO issue(s) affecting AI-answer-engine visibility."
        if issues else "No major technical SEO issues detected.",
        "score": score,
        "issues": issues,
        "raw_findings": findings,
    }
