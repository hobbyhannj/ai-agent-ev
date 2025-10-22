from typing import Any, Dict, Protocol

from langgraph.prebuilt import create_react_agent

ANALYSIS_AGENT_SEQUENCE = [
    "market",
    "policy",
    "oem",
    "supply_chain",
    "finance"
    ]


class PromptProvider(Protocol):
    def render(self, agent_name: str) -> Any:
        ...


def build_analysis_agents(
    llm: Any,
    prompts: PromptProvider,
    tools: list[Any] | None = None,
    overrides: dict[str, str] | None = None,
) -> Dict[str, Any]:
    """Build all analysis agents with LLM, tools, and prompt templates."""
    agents: Dict[str, Any] = {}
    overrides = overrides or {}

    for name in ANALYSIS_AGENT_SEQUENCE:
        prompt_text = overrides.get(name, prompts.render(name))
        agents[name] = create_react_agent(
            model=llm,
            tools=tools or [],
            prompt=prompt_text,
        )

    return agents
