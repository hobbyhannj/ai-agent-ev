"""Finance agent tools built on top of base_tool (with Alpha Vantage integration)."""

from __future__ import annotations
import os
from typing import Any, Dict
from agents.base_tool import sync_tool
import requests


logger = __import__('logging').getLogger(__name__)

ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
ALPHAVANTAGE_BASE_URL = "https://www.alphavantage.co/query"


@sync_tool
def fetch_financial_overview(company: str) -> Dict[str, Any]:
    """Fetch general financial overview for a given EV-related company from Alpha Vantage."""

    if not ALPHAVANTAGE_API_KEY:
        return {
            "source": "Alpha Vantage (Company Overview)",
            "symbol": company.upper(),
            "status": "Get free API key at https://www.alphavantage.co/",
            "instruction": "Set ALPHAVANTAGE_API_KEY environment variable"
        }

    try:
        params = {
            "function": "OVERVIEW",
            "symbol": company.upper(),
            "apikey": ALPHAVANTAGE_API_KEY,
        }

        response = requests.get(ALPHAVANTAGE_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "source": "Alpha Vantage (Company Overview)",
            "symbol": company.upper(),
            "data": data,
        }
    except Exception as e:
        return {
            "source": "Alpha Vantage (Company Overview)",
            "symbol": company.upper(),
            "error": str(e),
        }


@sync_tool
def fetch_intraday_data(symbol: str, interval: str = "5min") -> Dict[str, Any]:
    """Fetch intraday time-series data from Alpha Vantage."""

    if not ALPHAVANTAGE_API_KEY:
        return {
            "source": f"Alpha Vantage (Intraday {interval})",
            "symbol": symbol.upper(),
            "interval": interval,
            "status": "Get free API key at https://www.alphavantage.co/",
        }

    try:
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol.upper(),
            "interval": interval,
            "apikey": ALPHAVANTAGE_API_KEY,
        }

        response = requests.get(ALPHAVANTAGE_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "source": f"Alpha Vantage (Intraday {interval})",
            "symbol": symbol.upper(),
            "data": data,
        }
    except Exception as e:
        return {
            "source": f"Alpha Vantage (Intraday {interval})",
            "symbol": symbol.upper(),
            "error": str(e),
        }


@sync_tool
def fetch_daily_data(symbol: str) -> Dict[str, Any]:
    """Fetch daily stock price time-series from Alpha Vantage."""

    if not ALPHAVANTAGE_API_KEY:
        return {
            "source": "Alpha Vantage (Daily Prices)",
            "symbol": symbol.upper(),
            "status": "Get free API key at https://www.alphavantage.co/",
        }

    try:
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol.upper(),
            "apikey": ALPHAVANTAGE_API_KEY,
        }

        response = requests.get(ALPHAVANTAGE_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "source": "Alpha Vantage (Daily Prices)",
            "symbol": symbol.upper(),
            "data": data,
        }
    except Exception as e:
        return {
            "source": "Alpha Vantage (Daily Prices)",
            "symbol": symbol.upper(),
            "error": str(e),
        }


@sync_tool
def fetch_global_quote(symbol: str) -> Dict[str, Any]:
    """Fetch latest stock price quote from Alpha Vantage."""

    if not ALPHAVANTAGE_API_KEY:
        return {
            "source": "Alpha Vantage (Global Quote)",
            "symbol": symbol.upper(),
            "status": "Get free API key at https://www.alphavantage.co/",
        }

    try:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol.upper(),
            "apikey": ALPHAVANTAGE_API_KEY,
        }

        response = requests.get(ALPHAVANTAGE_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "source": "Alpha Vantage (Global Quote)",
            "symbol": symbol.upper(),
            "data": data,
        }
    except Exception as e:
        return {
            "source": "Alpha Vantage (Global Quote)",
            "symbol": symbol.upper(),
            "error": str(e),
        }


@sync_tool
def compare_market_performance(comp_a: str, comp_b: str) -> Dict[str, Any]:
    """Compare stock performance between two companies."""

    data_a = fetch_global_quote(comp_a)
    data_b = fetch_global_quote(comp_b)

    return {
        "source": "Alpha Vantage (Market Comparison)",
        "comparison": f"{comp_a} vs {comp_b}",
        "company_a": data_a,
        "company_b": data_b,
    }


def get_finance_tools():
    """Return the list of all finance tools."""
    return [
        fetch_financial_overview,
        fetch_intraday_data,
        fetch_daily_data,
        fetch_global_quote,
        compare_market_performance,
    ]

FINANCE_TOOLS = get_finance_tools()
