from __future__ import annotations
from agents.base_prompt import build_prompt

OEM_PROMPT_TEXT = (
    "You are the OEM Analyst. "
    "Track automakers' production plans, technology investments, "
    "and strategic partnerships in the EV sector."
)

OEM_PROMPT = build_prompt(OEM_PROMPT_TEXT)

