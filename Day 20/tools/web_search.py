"""Web Search Tool: Search provider supporting live API queries with safe mock fallback."""

from __future__ import annotations
import os
import requests
from typing import Any, Dict, List, Optional
from core.errors import ExternalServiceError, ValidationError
from tools.base import BaseTool

# Realistic mock knowledge index for offline demonstration
MOCK_KNOWLEDGE_BASE = [
    {
        "keywords": ["ai", "artificial intelligence", "developments", "news"],
        "title": "State of Artificial Intelligence in 2026: Agentic Systems and Neurosymbolic AI",
        "url": "https://techpulse-daily.org/ai-developments-2026",
        "snippet": "Recent breakthroughs in agentic AI architectures show autonomous tool invocation, self-correcting code loops, and multi-agent coordination reaching enterprise production.",
    },
    {
        "keywords": ["python", "programming", "tools", "async"],
        "title": "Python 3.12+ Modern Function Calling Frameworks",
        "url": "https://developer-hub.io/python/function-calling-patterns",
        "snippet": "Explore how type hints, Pydantic schemas, and AST-based safe evaluation can construct enterprise-grade agent toolchains with zero security vulnerabilities.",
    },
    {
        "keywords": ["langgraph", "workflow", "agents", "langchain"],
        "title": "Orchestrating Complex Agent Workflows with LangGraph",
        "url": "https://ai-insights.com/langgraph-workflows",
        "snippet": "LangGraph enables cyclic graphs, persistent memory checkpointing, and dynamic human-in-the-loop validation for robust generative AI pipelines.",
    },
    {
        "keywords": ["weather", "climate", "forecast"],
        "title": "Global Meteorological Monitoring Network",
        "url": "https://global-weather-archive.org/reports",
        "snippet": "Real-time atmospheric condition reporting, precipitation radar, and planetary temperature anomaly tracking updated every hour.",
    },
]


class WebSearchTool(BaseTool):
    """Executes web queries with configurable API integration and realistic offline mock fallback."""

    name = "web_search"
    description = (
        "Search the web for up-to-date information, news, documentation, and articles. "
        "Returns a structured list of results with title, url, and snippet."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query keywords to look up.",
            },
            "num_results": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 5).",
            },
        },
        "required": ["query"],
    }
    examples = [
        {"query": "Latest developments in artificial intelligence"},
        {"query": "Python function calling patterns", "num_results": 3},
    ]

    def _query_live_api(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """Query live search API using configured environment credentials."""
        api_key = os.getenv("WEB_SEARCH_API_KEY")
        endpoint = os.getenv("WEB_SEARCH_ENDPOINT", "https://api.bing.microsoft.com/v7.0/search")

        headers = {"Ocp-Apim-Subscription-Key": api_key}
        params = {"q": query, "count": num_results}

        try:
            resp = requests.get(endpoint, headers=headers, params=params, timeout=5.0)
            if resp.status_code == 429:
                raise ExternalServiceError("Web Search API rate limit exceeded (HTTP 429).", tool_name=self.name)
            if resp.status_code != 200:
                raise ExternalServiceError(
                    f"Web Search API returned error status {resp.status_code}: {resp.text[:200]}",
                    tool_name=self.name,
                )

            data = resp.json()
            web_pages = data.get("webPages", {}).get("value", [])
            results = []
            for item in web_pages[:num_results]:
                results.append({
                    "title": item.get("name", "No Title"),
                    "url": item.get("url", ""),
                    "snippet": item.get("snippet", ""),
                })
            return results
        except requests.Timeout:
            raise ExternalServiceError("Web Search API request timed out after 5 seconds.", tool_name=self.name)
        except requests.RequestException as e:
            raise ExternalServiceError(f"Web Search network failure: {str(e)}", tool_name=self.name)

    def _query_mock(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """Return realistic indexed search results matching query terms."""
        query_words = set(query.lower().split())
        matched = []

        for entry in MOCK_KNOWLEDGE_BASE:
            score = sum(1 for kw in entry["keywords"] if any(w in kw or kw in w for w in query_words))
            if score > 0 or not matched:
                matched.append({
                    "title": entry["title"],
                    "url": entry["url"],
                    "snippet": entry["snippet"],
                })

        if not matched:
            matched.append({
                "title": f"Web Results for '{query}'",
                "url": f"https://mock-search.local/search?q={query.replace(' ', '+')}",
                "snippet": f"Simulated index record matching query '{query}'. In production, provide WEB_SEARCH_API_KEY for live results.",
            })

        return matched[:num_results]

    def run(self, query: str, num_results: int = 5, simulate_error: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Execute web search and return structured output."""
        if not query or not query.strip():
            raise ValidationError("Search query cannot be empty.", tool_name=self.name)

        clean_query = query.strip()
        num_results = max(1, min(10, num_results))

        # Error simulation hook for testing
        if simulate_error == "timeout":
            raise ExternalServiceError("Web Search API request timed out after 5.0 seconds.", tool_name=self.name)
        if simulate_error == "rate_limit":
            raise ExternalServiceError("Web Search API rate limit exceeded (HTTP 429).", tool_name=self.name)
        if simulate_error == "api_failure":
            raise ExternalServiceError("Web Search API 500 Internal Server Error.", tool_name=self.name)

        api_key = os.getenv("WEB_SEARCH_API_KEY")
        if api_key:
            results = self._query_live_api(clean_query, num_results)
            source = "live"
        else:
            results = self._query_mock(clean_query, num_results)
            source = "mock (offline mode - configure WEB_SEARCH_API_KEY for live results)"

        return {
            "query": clean_query,
            "total_results": len(results),
            "source": source,
            "results": results,
        }
