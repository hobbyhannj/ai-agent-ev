from __future__ import annotations
from agents.analysis_agents.supply_agent.prompt import SUPPLY_PROMPT_TEXT
from agents.analysis_agents.supply_agent.tool import SUPPLY_TOOLS
from agents.base_agent import build_base_agent


def get_supply_agent(model: str = "gpt-4o-mini", debug: bool = False):

    return build_base_agent(
        name="supply_agent",
        system_prompt=SUPPLY_PROMPT_TEXT,
        tools=SUPPLY_TOOLS,
        model=model,
        temperature=0.2,
        debug=debug,
    )

