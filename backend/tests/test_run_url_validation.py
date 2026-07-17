import pytest
from pydantic import ValidationError

from app.models import RunCreate


def test_markdown_wrapped_target_url_is_rejected():
    """The exact bug: a markdown-wrapped link like "[label](url)" pasted
    into the target URL field parses to an empty netloc via urlparse, and
    _domain()'s fallback used to return that raw garbage unchanged,
    embedding literal bracket syntax into every generated report string.
    Rejecting it here, at the API boundary, is the actual fix."""
    with pytest.raises(ValidationError):
        RunCreate(target_url="[www.g2.com](https://www.g2.com)", competitor_urls=[], buyer_queries=["q"])


def test_markdown_wrapped_competitor_url_is_rejected():
    with pytest.raises(ValidationError):
        RunCreate(
            target_url="https://www.g2.com",
            competitor_urls=["[bad](https://bad.com)"],
            buyer_queries=["q"],
        )


def test_schemeless_url_is_rejected():
    with pytest.raises(ValidationError):
        RunCreate(target_url="www.g2.com", competitor_urls=[], buyer_queries=["q"])


def test_valid_url_is_accepted():
    run = RunCreate(
        target_url="https://www.g2.com",
        competitor_urls=["https://www.trustradius.com"],
        buyer_queries=["best crm software"],
    )
    assert run.target_url == "https://www.g2.com"
