from __future__ import annotations
from agents.analysis_agents.market_agent.prompt import MARKET_PROMPT_TEXT
from agents.analysis_agents.market_agent.tool import MARKET_TOOLS
from agents.base_agent import build_base_agent


def get_market_agent(model: str = "gpt-4o-mini", debug: bool = False):

    return build_base_agent(
        name="market_agent",
        system_prompt=MARKET_PROMPT_TEXT,
        tools=MARKET_TOOLS,
        model=model,
        temperature=0.2,
        debug=debug,
    )

