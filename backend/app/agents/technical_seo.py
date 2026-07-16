from ..tools.schema_checker import fetch_and_parse
from .technical_seo_mock import mock_interpret_technical_seo


def run_technical_seo_agent(target_url: str) -> dict:
    findings = fetch_and_parse(target_url)
    return mock_interpret_technical_seo(findings)
