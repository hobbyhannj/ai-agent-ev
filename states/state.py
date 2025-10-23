from datetime import datetime
from typing import Any, Dict, List, Optional, Literal, Set
from dataclasses import dataclass, field

AgentName = Literal[
    "market",
    "policy",
    "oem",
    "supply_chain",
    "finance",
    "cross_layer_validation",
    "report_quality_check",
    "hallucination_check",
    "supervisor"
]

@dataclass
class SupervisorState:
    """Shared supervisor state (simplified and practical)."""

    task_input: str
    current_agent: Optional[AgentName] = None
    notes: Dict[AgentName, List[str]] = field(default_factory=dict)
    decisions: List[str] = field(default_factory=list)
    retry_count: int = 0
    total_steps: int = 0
    max_retries: int = 2
    max_steps: int = 75
    final_report: Optional[str] = None
    history: List[Dict[str, Any]] = field(default_factory=list)
    stage: Literal["analysis", "validation", "final", "done"] = "analysis"
    completed_analysis: Set[AgentName] = field(default_factory=set)
    completed_validation: Set[AgentName] = field(default_factory=set)

    def log(self, agent: AgentName, message: str):
        self.notes.setdefault(agent, []).append(message)

    def step(self, agent: AgentName):
        """Track step count and prevent infinite loops."""
        self.current_agent = agent
        self.total_steps += 1
        if self.total_steps > self.max_steps:
            raise RuntimeError("Exceeded max step limit — possible loop detected.")
        if self.retry_count > self.max_retries:
            raise RuntimeError(f"Too many retries for agent {agent}.")

    def record_decision(self, decision: str):
        self.decisions.append(decision)

    def reset_retry(self):
        self.retry_count = 0

    def snapshot(self, *, agent: AgentName, result: Any) -> Dict[str, Any]:
        """Capture a serialisable view of the supervisor's progress."""

        def _serialise(value: Any) -> Any:
            if isinstance(value, (str, int, float, bool)) or value is None:
                return value
            if isinstance(value, dict):
                return {key: _serialise(val) for key, val in value.items()}
            if isinstance(value, (list, tuple)):
                return [_serialise(item) for item in value]
            if isinstance(value, set):
                return [_serialise(item) for item in sorted(value)]
            return str(value)

        entry = {
            "step": self.total_steps,
            "agent": agent,
            "result": _serialise(result),
            "notes": list(self.notes.get(agent, [])),
            "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
        }
        self.history.append(entry)
        return entry
