from __future__ import annotations
from agents.analysis_agents.finance_agent.prompt import FINANCE_PROMPT_TEXT
from agents.analysis_agents.finance_agent.tool import FINANCE_TOOLS
from agents.base_agent import build_base_agent


def get_finance_agent(model: str = "gpt-4o-mini", debug: bool = False):

    return build_base_agent(
        name="finance_agent",
        system_prompt=FINANCE_PROMPT_TEXT,
        tools=FINANCE_TOOLS,
        model=model,
        temperature=0.2,
        debug=debug,
    )
