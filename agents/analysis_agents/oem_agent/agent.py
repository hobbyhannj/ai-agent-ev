from __future__ import annotations
from agents.analysis_agents.oem_agent.prompt import OEM_PROMPT_TEXT
from agents.analysis_agents.oem_agent.tool import OEM_TOOLS
from agents.base_agent import build_base_agent


def get_oem_agent(model: str = "gpt-4o-mini", debug: bool = False):

    return build_base_agent(
        name="oem_agent",
        system_prompt=OEM_PROMPT_TEXT,
        tools=OEM_TOOLS,
        model=model,
        temperature=0.2,
        debug=debug,
    )

