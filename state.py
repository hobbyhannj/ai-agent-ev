"""State primitives used by the EV Market Intelligence supervisor graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, TypedDict

AgentKind = Literal[
    "analysis",
    "validation",
    "supervisor",
]

AnalysisAgentName = Literal[
    "market",
    "policy",
    "oem",
    "supply_chain",
    "finance",
]

ValidationAgentName = Literal[
    "cross_layer_validation",
    "report_quality_check",
    "hallucination_check",
]

SupervisorAgentName = Literal["supervisor"]

AgentName = Literal[
    "market",
    "policy",
    "oem",
    "supply_chain",
    "finance",
    "cross_layer_validation",
    "report_quality_check",
    "hallucination_check",
    "supervisor",
]


class AgentAttempt(TypedDict, total=False):
    """Trace data persisted for each agent run."""

    attempts: int
    last_output: str
    status: Literal["pending", "succeeded", "failed"]
    notes: List[str]


@dataclass(slots=True)
class SupervisorState:
    """Shared mutable state exchanged between supervisor and agents."""

    task_input: str
    analysis_notes: Dict[AnalysisAgentName, str] = field(default_factory=dict)
    validation_notes: Dict[ValidationAgentName, str] = field(default_factory=dict)
    report_outline: Optional[str] = None
    final_report: Optional[str] = None
    pending_validations: List[ValidationAgentName] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)
    retry_tracker: Dict[AgentName, int] = field(default_factory=dict)
    agent_attempts: Dict[AgentName, AgentAttempt] = field(default_factory=dict)
    max_retries: int = 2
    max_total_steps: int = 25
    total_steps: int = 0
    active_agent: Optional[AgentName] = None

    def register_step(self, agent: AgentName) -> None:
        """Increment counters and guard against runaway loops."""

        self.total_steps += 1
        attempts = self.retry_tracker.get(agent, 0)
        self.retry_tracker[agent] = attempts + 1
        self.active_agent = agent

    def check_loop_safeguards(self) -> None:
        """Raise if the supervisor exceeds retry or step limits."""

        if self.total_steps >= self.max_total_steps:
            raise RuntimeError(
                "Supervisor exceeded maximum total steps; aborting to avoid infinite loop."
            )
        if self.active_agent and self.retry_tracker.get(self.active_agent, 0) > self.max_retries:
            raise RuntimeError(
                f"Agent '{self.active_agent}' exceeded max retries ({self.max_retries})."
            )

    def mark_agent_result(
        self,
        agent: AgentName,
        status: Literal["pending", "succeeded", "failed"],
        output: str,
    ) -> None:
        """Persist the agent outcome for future supervisor decisions."""

        attempt = self.agent_attempts.setdefault(agent, AgentAttempt())
        attempt["attempts"] = attempt.get("attempts", 0) + 1
        attempt["last_output"] = output
        attempt.setdefault("notes", []).append(output)
        attempt["status"] = status

    def reset_agent_retry(self, agent: AgentName) -> None:
        """Clear retry tracking after a successful step."""

        self.retry_tracker[agent] = 0
        self.active_agent = None


class GraphState(TypedDict, total=False):
    """Typed mapping used by LangGraph nodes."""

    supervisor_state: SupervisorState
    last_agent: Optional[AgentName]
    task_input: str
    next_agent: AgentName
