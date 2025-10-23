from __future__ import annotations

import os
from typing import Any, Dict, Tuple

import aiohttp

ALPHAVANTAGE_BASE_URL = "https://www.alphavantage.co/query"
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

if not ALPHAVANTAGE_API_KEY:
    raise RuntimeError("Missing ALPHAVANTAGE_API_KEY in environment variables.")


async def fetch_intraday_data(ticker: str, interval: str = "5min") -> Dict[str, object]:
    """Fetch intraday (e.g., 1min, 5min, 15min) time-series data for a given ticker."""
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": ticker.upper(),
        "interval": interval,
        "apikey": ALPHAVANTAGE_API_KEY,
    }
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(ALPHAVANTAGE_BASE_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
    return {"source": "Alpha Vantage (Intraday)", "data": data}


async def fetch_daily_data(ticker: str) -> Dict[str, object]:
    """Fetch daily time-series data for a given ticker."""
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": ticker.upper(),
        "apikey": ALPHAVANTAGE_API_KEY,
    }
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(ALPHAVANTAGE_BASE_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
    return {"source": "Alpha Vantage (Daily)", "data": data}


async def fetch_weekly_data(ticker: str) -> Dict[str, object]:
    """Fetch weekly time-series data for a given ticker."""
    params = {
        "function": "TIME_SERIES_WEEKLY",
        "symbol": ticker.upper(),
        "apikey": ALPHAVANTAGE_API_KEY,
    }
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(ALPHAVANTAGE_BASE_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
    return {"source": "Alpha Vantage (Weekly)", "data": data}


async def fetch_monthly_data(ticker: str) -> Dict[str, object]:
    """Fetch monthly time-series data for a given ticker."""
    params = {
        "function": "TIME_SERIES_MONTHLY",
        "symbol": ticker.upper(),
        "apikey": ALPHAVANTAGE_API_KEY,
    }
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(ALPHAVANTAGE_BASE_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
    return {"source": "Alpha Vantage (Monthly)", "data": data}


async def fetch_global_quote(ticker: str) -> Dict[str, object]:
    """Fetch current price and market summary for a ticker."""
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": ticker.upper(),
        "apikey": ALPHAVANTAGE_API_KEY,
    }
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(ALPHAVANTAGE_BASE_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
    return {"source": "Alpha Vantage (Global Quote)", "data": data}


async def search_symbol(keyword: str) -> Dict[str, object]:
    """Search company symbols by keyword (e.g., 'Tesla', 'Hyundai')."""
    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": keyword,
        "apikey": ALPHAVANTAGE_API_KEY,
    }
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(ALPHAVANTAGE_BASE_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
    return {"source": "Alpha Vantage (Symbol Search)", "data": data}


async def fetch_market_status() -> Dict[str, object]:
    """Get current market open/close status for global exchanges."""
    params = {
        "function": "MARKET_STATUS",
        "apikey": ALPHAVANTAGE_API_KEY,
    }
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(ALPHAVANTAGE_BASE_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
    return {"source": "Alpha Vantage (Market Status)", "data": data}


# ---------------------------
# Tool registry
# ---------------------------

def get_analysis_tools() -> Dict[str, Tuple[Any, ...]]:
    """Return finance-related async tools keyed by agent name."""
    return {
        "finance": (
            fetch_intraday_data,
            fetch_daily_data,
            fetch_weekly_data,
            fetch_monthly_data,
            fetch_global_quote,
            search_symbol,
            fetch_market_status,
        )
    }
