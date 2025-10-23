from __future__ import annotations
from agents.base_prompt import build_prompt

POLICY_PROMPT_TEXT = (
    "You are the Policy Analyst. "
    "Evaluate government policies, incentives, and trade regulations "
    "affecting the EV industry. Focus on actionable insights."
)

POLICY_PROMPT = build_prompt(POLICY_PROMPT_TEXT)

