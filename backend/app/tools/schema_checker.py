import extruct
import requests
from bs4 import BeautifulSoup


def fetch_and_parse(url: str, timeout: int = 10) -> dict:
    """Fetch a URL and parse it for schema markup, meta tags, and heading structure."""
    response = requests.get(url, timeout=timeout, headers={"User-Agent": "AEOProductOpsBot/1.0"})
    response.raise_for_status()
    html = response.text

    soup = BeautifulSoup(html, "html.parser")

    json_ld_data = extruct.extract(html, syntaxes=["json-ld"], base_url=url).get("json-ld", [])
    json_ld_types = sorted({item["@type"] for item in json_ld_data if isinstance(item.get("@type"), str)})

    title_tag = soup.find("title")
    meta_description_tag = soup.find("meta", attrs={"name": "description"})

    return {
        "url": url,
        "json_ld_present": bool(json_ld_data),
        "json_ld_types": json_ld_types,
        "title": title_tag.get_text(strip=True) if title_tag else None,
        "meta_description": meta_description_tag.get("content", "").strip() if meta_description_tag else None,
        "h1_count": len(soup.find_all("h1")),
        "h2_count": len(soup.find_all("h2")),
    }
