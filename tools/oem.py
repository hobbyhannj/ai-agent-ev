"""Async OEM news aggregation tool (free 5-source version)."""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

import aiohttp
import feedparser
from urllib.parse import quote_plus
from langchain_tavily import TavilySearch


logger = logging.getLogger(__name__)

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
    encoded = quote_plus(f"{query} EV Electric Vehicle")
    url = f"https://news.google.com/rss/search?q={encoded}"
    try:
        loop = asyncio.get_event_loop()
        parsed = await loop.run_in_executor(None, feedparser.parse, url)
    except Exception as exc:  # pragma: no cover - network failures
        logger.warning("Google News fetch failed: %s", exc)
        return []
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
        if d.get("url")
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
        {"title": a["title"], "link": a.get("link"), "source": "Newsdata.io"}
        for a in data.get("results", [])
        if a.get("link")
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
        elif isinstance(res, Exception):
            logger.warning("OEM news source failed: %s", res)

    unique_articles: List[Dict[str, Any]] = []
    seen_links: set[str] = set()
    for article in merged:
        link = article.get("link")
        if not link:
            continue
        if link in seen_links:
            continue
        seen_links.add(link)
        unique_articles.append(article)

    return {
        "source": "Async-News-Aggregator",
        "manufacturer": manufacturer,
        "total_articles": len(unique_articles),
        "articles": unique_articles[:10],
    }


# -----------------------------
# 6. Tavily Web Search + structured integration
# -----------------------------
tavily_tool = TavilySearch(k=3)

async def explore_oem_trends(
    manufacturer: str,
    timeframe: Optional[str] = None,
) -> Dict[str, Any]:
    """Aggregate OEM-related news from multiple async sources (network-required)."""

    timeframe_part = timeframe or "past quarter"
    articles: List[Dict[str, Any]] = []
    tavily_data: Any = None

    try:
        aggregated = await fetch_oem_insights_news(manufacturer)
        articles = aggregated.get("articles", [])
    except Exception as exc:  # pragma: no cover - network issues fallback
        logger.warning("OEM aggregate fetch failed: %s", exc)

    try:
        top_titles = [a.get("title", "") for a in articles if a.get("title")][:5]
        query = (
            f"{manufacturer} EV market strategy {timeframe_part}. "
            f"Recent headlines: {' | '.join(top_titles)}"
        )
        tavily_data = tavily_tool.invoke({"query": query})
    except Exception as exc:  # pragma: no cover - when Tavily unavailable
        tavily_data = {"error": str(exc)}

    insights: List[str]
    if articles:
        insights = [
            "수집된 최신 뉴스 기반으로 OEM 전략을 파악하세요.",
            "기사에 명시된 투자, 생산, 파트너십 동향을 중심으로 전략적 시사점을 도출하십시오.",
        ]
    else:
        insights = [
            "네트워크 데이터가 부족합니다. 추가 조사를 위해 수동으로 뉴스 소스를 확인하십시오.",
        ]

    references = [a.get("link") for a in articles if a.get("link")]
    references = [ref for ref in references if isinstance(ref, str)]

    return {
        "type": "oem_trend_brief",
        "manufacturer": manufacturer,
        "timeframe": timeframe_part,
        "articles": articles[:5],
        "insights": insights,
        "tavily": tavily_data,
        "references": references,
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
            if key == "articles":
                print("기사 목록:")
                for article in value:
                    if isinstance(article, dict):
                        print(f"  - {article.get('title', 'N/A')} -> {article.get('link', '')}")
                    else:
                        print(f"  - {article}")
            else:
                print(f"{key.title()}: {value}")

    asyncio.run(_demo())
