from __future__ import annotations

from tavily import TavilyClient

from app.schemas import WebSearchResult
from app.utils import clean_text, require_env


def search_company(company_name: str, max_results: int = 5) -> list[WebSearchResult]:
    api_key = require_env("TAVILY_API_KEY")
    client = TavilyClient(api_key=api_key)
    query = (
        f'"{company_name}" ESG RSE ODD SDG developpement durable '
        "responsabilite sociale environnement climat controverse"
    )
    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=True,
        include_raw_content=False,
    )

    results: list[WebSearchResult] = []
    for item in response.get("results", [])[:max_results]:
        title = clean_text(item.get("title"), 300)
        url = clean_text(item.get("url"), 1000)
        content = clean_text(item.get("content"), 1500)
        if title and url:
            results.append(WebSearchResult(title=title, url=url, content=content))

    return results