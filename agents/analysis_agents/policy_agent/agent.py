from __future__ import annotations
from agents.analysis_agents.policy_agent.prompt import POLICY_PROMPT_TEXT
from agents.analysis_agents.policy_agent.tool import POLICY_TOOLS
from agents.base_agent import build_base_agent


def get_policy_agent(model: str = "gpt-4o-mini", debug: bool = False):

    return build_base_agent(
        name="policy_agent",
        system_prompt=POLICY_PROMPT_TEXT,
        tools=POLICY_TOOLS,
        model=model,
        temperature=0.2,
        debug=debug,
    )

