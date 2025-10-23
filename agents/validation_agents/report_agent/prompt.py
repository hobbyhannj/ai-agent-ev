from __future__ import annotations
from agents.base_prompt import build_prompt

REPORT_PROMPT_TEXT = (
    "You are the Report Quality Reviewer. "
    "Assess overall structure, clarity, completeness, and factual accuracy "
    "of the generated EV market report."
)

REPORT_PROMPT = build_prompt(REPORT_PROMPT_TEXT)

