from __future__ import annotations
from agents.validation_agents.report_agent.prompt import REPORT_PROMPT_TEXT
from agents.validation_agents.report_agent.tool import REPORT_TOOLS
from agents.base_agent import build_base_agent


def get_report_agent(model: str = "gpt-4o-mini", debug: bool = False):

    return build_base_agent(
        name="report_agent",
        system_prompt=REPORT_PROMPT_TEXT,
        tools=REPORT_TOOLS,
        model=model,
        temperature=0.2,
        debug=debug,
    )

