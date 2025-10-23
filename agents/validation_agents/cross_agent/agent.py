from __future__ import annotations
from agents.validation_agents.cross_agent.prompt import CROSS_PROMPT_TEXT
from agents.validation_agents.cross_agent.tool import CROSS_TOOLS
from agents.base_agent import build_base_agent


def get_cross_agent(model: str = "gpt-4o-mini", debug: bool = False):

    return build_base_agent(
        name="cross_agent",
        system_prompt=CROSS_PROMPT_TEXT,
        tools=CROSS_TOOLS,
        model=model,
        temperature=0.2,
        debug=debug,
    )

