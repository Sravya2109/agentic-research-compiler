from __future__ import annotations

import os

from dotenv import load_dotenv
from tavily import TavilyClient

from schemas.report import SearchResult


load_dotenv()


def _get_client() -> TavilyClient:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY is not set")
    return TavilyClient(api_key=api_key)


def run_search(query_strings: list[str], max_results_per_query: int = 3) -> list[SearchResult]:
    client = _get_client()
    results: list[SearchResult] = []
    seen_urls: set[str] = set()

    for query in query_strings:
        if len(results) >= 10:
            break
        try:
            response = client.search(query=query, search_depth="advanced", max_results=max_results_per_query)
            for item in response.get("results", []):
                url = item.get("url")
                if not url or url in seen_urls:
                    continue

                seen_urls.add(url)
                results.append(
                    SearchResult(
                        url=url,
                        title=item.get("title", ""),
                        snippet=item.get("content", item.get("snippet", "")),
                        published_date=item.get("published_date"),
                    )
                )
        except Exception:
            continue

    return results


def build_search_queries(main_query: str, sub_tasks: list[str]) -> list[str]:
    combined_queries = [main_query, *sub_tasks]
    unique_queries: list[str] = []
    seen_queries: set[str] = set()

    for query in combined_queries:
        if query in seen_queries:
            continue
        seen_queries.add(query)
        unique_queries.append(query)
        if len(unique_queries) >= 5:
            break

    return unique_queries
