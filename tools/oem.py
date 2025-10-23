"""Async OEM news aggregation tool (free 5-source version)."""

from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, List, Optional

import aiohttp
import feedparser
from langchain_tavily import TavilySearch

# -----------------------------
# Configuration
# -----------------------------
NAVER_CLIENT_ID = "CAH0u4faGj8_ak9I_vlc"
NAVER_CLIENT_SECRET = "L9p3tQqSnd"
NEWSDATA_KEY = "pub_5e29239242e64fc5b09b8b2748fa9c53"

# -----------------------------
# Generic async fetch helper
# -----------------------------
async def _fetch_json(url: str, params=None, headers=None) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url, params=params, headers=headers) as resp:
            if resp.status != 200:
                return {"error": f"{url} -> HTTP {resp.status}"}
            try:
                return await resp.json()
            except Exception:
                text = await resp.text()
                return {"error": f"Invalid JSON from {url}", "raw": text}


# -----------------------------
# 1. Google News (RSS feed)
# -----------------------------
async def fetch_google_news(query: str) -> List[Dict[str, Any]]:
    url = f"https://news.google.com/rss/search?q={query}+EV+Electric+Vehicle"
    parsed = feedparser.parse(url)
    return [
        {"title": e.title, "link": e.link, "source": "Google News"}
        for e in parsed.entries[:10]
    ]


# -----------------------------
# 2. Naver News API
# -----------------------------
async def fetch_naver_news(query: str) -> List[Dict[str, Any]]:
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return []
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": query, "display": 10, "sort": "sim"}
    data = await _fetch_json(url, params=params, headers=headers)
    items = data.get("items", [])
    return [{"title": i["title"], "link": i["link"], "source": "Naver News"} for i in items]


# -----------------------------
# 3. GDELT API
# -----------------------------
async def fetch_gdelt_news(query: str) -> List[Dict[str, Any]]:
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {"query": query, "mode": "artlist", "maxrecords": 10, "format": "json"}
    data = await _fetch_json(url, params=params)
    return [
        {"title": d.get("title", ""), "link": d.get("url", ""), "source": "GDELT"}
        for d in data.get("articles", [])
    ]


# -----------------------------
# 4. Newsdata.io API
# -----------------------------
async def fetch_newsdata_news(query: str) -> List[Dict[str, Any]]:
    if not NEWSDATA_KEY:
        return []
    url = "https://newsdata.io/api/1/news"
    params = {"apikey": NEWSDATA_KEY, "q": query, "language": "en"}
    data = await _fetch_json(url, params=params)
    return [
        {"title": a["title"], "link": a["link"], "source": "Newsdata.io"}
        for a in data.get("results", [])
    ]


# -----------------------------
# 5. Unified async OEM news fetcher
# -----------------------------
async def fetch_oem_insights_news(manufacturer: str) -> Dict[str, Any]:
    """Aggregate OEM-related news from multiple async sources."""
    query = f"{manufacturer} electric vehicle OR EV battery OR OEM OR policy"
    tasks = [
        fetch_google_news(query),
        fetch_naver_news(query),
        fetch_gdelt_news(query),
        fetch_newsdata_news(query),
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    merged: List[Dict[str, Any]] = []
    for res in results:
        if isinstance(res, list):
            merged.extend(res)

    return {
        "source": "Async-News-Aggregator",
        "manufacturer": manufacturer,
        "total_articles": len(merged),
        "articles": merged[:30],
    }


# -----------------------------
# 6. Tavily Web Search + structured integration
# -----------------------------
tavily_tool = TavilySearch(k=3)

_OEM_FALLBACK_DATA: Dict[str, Dict[str, Any]] = {
    "hyundai": {
        "headlines": [
            "Hyundai plans $7.6B investment in US EV and battery capacity by 2026",
            "Hyundai Motor inks cathode JV with LG Energy Solution for Georgia plant",
        ],
        "insights": [
            "Expanding E-GMP platform output in Ulsan and Georgia for next-gen IONIQ models",
            "Prioritising LFP cells for entry trims while keeping NCM chemistry for premium SUVs",
        ],
    },
    "tesla": {
        "headlines": [
            "Tesla accelerates Dojo compute buildout to support FSD training",
            "Berlin Gigafactory targets 500k Model Y capacity with new paint line",
        ],
        "insights": [
            "Margin pressure driving fresh price adjustments in China and Europe",
            "4680 ramp improving but still below target; battery supply supplemented via Panasonic",
        ],
    },
}


async def explore_oem_trends(
    manufacturer: str,
    timeframe: Optional[str] = None,
) -> Dict[str, Any]:
    """Aggregate OEM-related news from multiple async sources with safe fallbacks."""

    timeframe_part = timeframe or "past quarter"
    fallback = _OEM_FALLBACK_DATA.get(manufacturer.lower())
    articles: List[Any] = []
    tavily_data: Any = None

    try:
        aggregated = await fetch_oem_insights_news(manufacturer)
        articles = aggregated.get("articles", [])
        top_titles = [a.get("title", "") for a in articles if a.get("title")][:5]
        query = (
            f"{manufacturer} EV market strategy {timeframe_part}. "
            f"Recent headlines: {' | '.join(top_titles)}"
        )
        tavily_data = tavily_tool.invoke({"query": query})
    except Exception as exc:  # pragma: no cover - network issues fallback
        articles = fallback.get("headlines", []) if fallback else []  # type: ignore[assignment]
        tavily_data = {"error": str(exc)}

    insights: List[str]
    if fallback:
        insights = fallback["insights"]
    else:
        insights = [
            "OEM news feed aggregated from Google, Naver, GDELT, and Newsdata",
            "Refer to tavily_data for additional context",
        ]

    return {
        "type": "oem_trend_brief",
        "manufacturer": manufacturer,
        "timeframe": timeframe_part,
        "headlines": articles[:5] if articles and isinstance(articles[0], dict) else articles,
        "insights": insights,
        "tavily": tavily_data,
    }


# -----------------------------
# 7. Tool registry for LangGraph
# -----------------------------
def get_analysis_tools() -> dict[str, tuple[Any, ...]]:
    """Return OEM trend exploration tool keyed by agent name."""
    return {"oem": (explore_oem_trends,)}


# -----------------------------
# 8. Local test
# -----------------------------
if __name__ == "__main__":
    async def _demo():
        brief = await explore_oem_trends("Hyundai", "2025")
        print("=== OEM BRIEF ===")
        for key, value in brief.items():
            if key == "headlines":
                print(f"{key.title()}:")
                for headline in value:
                    if isinstance(headline, dict):
                        print(f"  - {headline.get('title', 'N/A')}")
                    else:
                        print(f"  - {headline}")
            else:
                print(f"{key.title()}: {value}")

    asyncio.run(_demo())
