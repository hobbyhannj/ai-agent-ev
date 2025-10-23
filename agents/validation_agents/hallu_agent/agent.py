from __future__ import annotations
from agents.validation_agents.hallu_agent.prompt import HALLU_PROMPT_TEXT
from agents.validation_agents.hallu_agent.tool import HALLU_TOOLS
from agents.base_agent import build_base_agent


def get_hallu_agent(model: str = "gpt-4o-mini", debug: bool = False):

    return build_base_agent(
        name="hallu_agent",
        system_prompt=HALLU_PROMPT_TEXT,
        tools=HALLU_TOOLS,
        model=model,
        temperature=0.2,
        debug=debug,
    )

