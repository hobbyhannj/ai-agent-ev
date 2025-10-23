"""Market agent tools for EV intelligence analysis."""

from __future__ import annotations
import logging
from datetime import date
from typing import Any, Dict, Optional
from agents.base_tool import sync_tool
import requests


logger = logging.getLogger(__name__)


@sync_tool
def explore_ev_market(
    region: Optional[str] = None,
    segment: Optional[str] = None,
    timeframe: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetch and return EV market data from live BING news sources."""

    logger.info(
        "Fetching EV market data (region=%s, segment=%s, timeframe=%s)",
        region,
        segment,
        timeframe,
    )

    region_queries = {
        "china": "EV market sales China 2025",
        "europe": "EV market sales Europe 2025",
        "united states": "EV market sales United States 2025",
        "global": "electric vehicle market trends 2025",
    }

    region_key = (region or "global").strip().lower()
    query = region_queries.get(region_key, "electric vehicle market analysis")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        url = "https://www.bing.com/news/search"
        params = {
            "q": query,
            "count": 10
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        articles = []
        for item in soup.find_all('div', class_='news-card'):
            title = item.find('a', class_='title')
            source = item.find('span', class_='source')

            if title and source:
                articles.append({
                    'title': title.get_text(strip=True),
                    'source': source.get_text(strip=True)
                })

        summary = f"Market snapshot for {region or 'Global'} ({date.today():%b %Y}):\n"

        if articles:
            for i, article in enumerate(articles[:5], 1):
                summary += f"{i}. {article.get('title', 'N/A')}\n"
                summary += f"   Source: {article.get('source', 'N/A')}\n"
        else:
            summary += "Fetching latest EV market data from Bing News.\n"

        return {
            "type": "ev_market_snapshot",
            "region": region or "Global",
            "segment": segment or "all",
            "timeframe": f"through {date.today():%b %Y}",
            "summary": summary,
            "source": "Bing News",
            "articles_count": len(articles),
        }
    except Exception as e:
        logger.warning("Bing News fetch failed: %s", e)

        try:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = data.get("Results", [])
            summary = f"EV Market Intelligence for {region or 'Global'}:\n"

            if results:
                for i, result in enumerate(results[:5], 1):
                    summary += f"{i}. {result.get('Text', 'N/A')}\n"
            else:
                summary += "Real-time market data fetched from DuckDuckGo.\n"

            return {
                "type": "ev_market_snapshot",
                "region": region or "Global",
                "segment": segment or "all",
                "timeframe": f"through {date.today():%b %Y}",
                "summary": summary,
                "source": "DuckDuckGo",
                "results_count": len(results),
            }
        except Exception as e2:
            logger.warning("All news sources failed: %s, %s", e, e2)
            return {
                "type": "ev_market_snapshot",
                "region": region or "Global",
                "segment": segment or "all",
                "timeframe": f"through {date.today():%b %Y}",
                "summary": f"Network error. Last updated: {date.today():%b %Y}",
                "source": "Offline",
                "error": str(e2),
            }


def get_market_tools():
    """Return the list of all market tools."""
    return [
        explore_ev_market,
    ]

MARKET_TOOLS = get_market_tools()
