from typing import Any, Dict
from typing import Protocol

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
    tools: list[Any] | None = None,
    overrides: dict[str, str] | None = None,
) -> Dict[str, Any]:
    """Build all validation agents (cross-layer, quality, hallucination)."""
    agents: Dict[str, Any] = {}
    overrides = overrides or {}

    for name in VALIDATION_AGENT_SEQUENCE:
        prompt_text = overrides.get(name, prompts.render(name))
        agents[name] = create_react_agent(
            model=llm,
            tools=tools or [],
            prompt=prompt_text,
        )

    return agents
