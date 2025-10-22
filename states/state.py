from typing import Dict, List, Optional, Literal
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
    max_steps: int = 20
    final_report: Optional[str] = None

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
