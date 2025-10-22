"""Simplified SupervisorGraph for EV Market Intelligence."""

from __future__ import annotations
from typing import Any, Dict, Optional, Union

# 최신 구조에서는 langgraph_supervisor에서 import
from langgraph_supervisor import create_supervisor
from langchain_core.prompts import ChatPromptTemplate

def build_supervisor_workflow(
    llm: Any,
    analysis_agents: Dict[str, Any],
    validation_agents: Dict[str, Any],
    supervisor_prompt: Union[str, ChatPromptTemplate],
    supervisor_tools: Optional[list[Any]] = None,
):
    """Return a compiled Supervisor workflow (simplified + clean)."""

    # 1. Combine all agents (dict 병합)
    all_agents = {**analysis_agents, **validation_agents}

    # 2. Supervisor 생성 (LLM 제어 에이전트)
    workflow = create_supervisor(
        agents=list(all_agents.values()),   # agents 리스트 전달
        model=llm,                          # LLM 객체 (ChatOpenAI 등)
        prompt=supervisor_prompt,           # system-level prompt
        tools=supervisor_tools or [],       # supervisor-level 도구
        parallel_tool_calls=False,          # 병렬 호출 비활성화 (필요시 True)
    ).compile()  # 그래프 컴파일

    # 3. Supervisor 실행기
    def run_supervisor(task_input: str, state: Optional[dict] = None):
        """Run the compiled workflow with basic loop + guard."""
        state = state or {"steps": 0, "max_steps": 25}
        while state["steps"] < state["max_steps"]:
            result = workflow.invoke({
                "messages": [
                    {"role": "user", "content": task_input}
                ]
            })
            state["steps"] += 1

            # Supervisor 결과 로그
            print(f"\n[Step {state['steps']}] Supervisor output:")
            print(result)

            # 종료 조건
            if isinstance(result, dict) and "final_report" in result:
                return result["final_report"]
            if isinstance(result, str) and "report" in result.lower():
                return result

        raise RuntimeError("Supervisor exceeded step limit — possible infinite loop.")

    return run_supervisor