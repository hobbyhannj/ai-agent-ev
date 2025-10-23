from __future__ import annotations
from agents.base_prompt import build_prompt
FINANCE_PROMPT_TEXT = (
    "You are the Finance Analyst. "
    "Review capital markets, funding flows, stock movements, "
    "and profitability indicators for EV-related companies."
)

FINANCE_PROMPT = build_prompt(FINANCE_PROMPT_TEXT)
