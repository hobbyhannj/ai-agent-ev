from typing import Any, Dict, Mapping, Protocol, Sequence

from langgraph.prebuilt import create_react_agent

VALIDATION_AGENT_SEQUENCE = [
    "cross_layer_validation",
    "report_quality_check",
    "hallucination_check",
]


class PromptProvider(Protocol):
    def render(self, agent_name: str) -> Any:
        ...


def build_validation_agents(
    llm: Any,
    prompts: PromptProvider,
    tools: Mapping[str, Sequence[Any]] | None = None,
    overrides: dict[str, str] | None = None,
) -> Dict[str, Any]:
    """Build all validation agents (cross-layer, quality, hallucination)."""
    agents: Dict[str, Any] = {}
    overrides = overrides or {}
    tools = tools or {}

    for name in VALIDATION_AGENT_SEQUENCE:
        prompt_text = overrides.get(name, prompts.render(name))
        agent_tools = list(tools.get(name, ()))
        agents[name] = create_react_agent(
            model=llm,
            tools=agent_tools,
            prompt=prompt_text,
            name=name,
        )

    return agents
