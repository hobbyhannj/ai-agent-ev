from __future__ import annotations
from agents.base_prompt import build_prompt

HALLU_PROMPT_TEXT = (
    "You are the Hallucination Auditor. "
    "Identify unsupported claims and require verifiable sources "
    "for every factual statement."
)

HALLU_PROMPT = build_prompt(HALLU_PROMPT_TEXT)

