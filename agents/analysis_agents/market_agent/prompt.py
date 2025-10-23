from __future__ import annotations
from agents.base_prompt import build_prompt

MARKET_PROMPT_TEXT = (
    "You are the Market Analyst for EV intelligence. "
    "Analyze global and regional EV demand, pricing trends, and "
    "consumer sentiment. Respond with concise, evidence-based notes."
)

MARKET_PROMPT = build_prompt(MARKET_PROMPT_TEXT)

