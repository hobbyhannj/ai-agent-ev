"""Supervisor state management."""

from __future__ import annotations
from typing import Any, Dict, List, Mapping, Optional
from datetime import datetime


class SupervisorState:
    """Maintains state across agent executions."""

    def __init__(self, task_input: str):
        self.task_input = task_input
        self.stage = "init"
        self.total_steps = 0
        self.retry_count = 0
        self.notes: Dict[str, List[str]] = {}
        self.history: List[Dict[str, Any]] = []
        self.decisions: List[str] = []
        self.final_report: Optional[str] = None
        self.timestamp = datetime.now()

    def step(self, agent_name: str) -> None:
        self.total_steps += 1
        if self.total_steps > 100:
            raise RuntimeError("Max steps exceeded")

    def log(self, agent_name: str, content: str) -> None:
        if agent_name not in self.notes:
            self.notes[agent_name] = []
        self.notes[agent_name].append(content)

    def record_decision(self, content: str) -> None:
        self.decisions.append(content)

    def snapshot(self, agent: str, result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "agent": agent,
            "stage": self.stage,
            "step": self.total_steps,
            "result": result,
            "timestamp": self.timestamp.isoformat(),
        }

    def add_to_history(self, snapshot: Dict[str, Any]) -> None:
        self.history.append(snapshot)

