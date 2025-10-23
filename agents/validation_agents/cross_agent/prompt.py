from __future__ import annotations
from agents.base_prompt import build_prompt

CROSS_PROMPT_TEXT = (
    "You are the Cross-Layer Validator. "
    "Ensure consistency and alignment among market, policy, OEM, "
    "supply chain, and finance insights."
)

CROSS_PROMPT = build_prompt(CROSS_PROMPT_TEXT)

