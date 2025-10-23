"""
File: test.py
Author: 한정석
Date: 2025. 10. 23.
Last Modified: 2025. 10. 23.
Description:
    - Multi-agent EV market intelligence system
    - Deterministic supervisor: analysis -> validation -> report generation
    - PDF export with reportlab
"""
import asyncio

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from agents.analysis_agents.finance_agent.tool import FINANCE_TOOLS
from agents.analysis_agents.market_agent.tool import MARKET_TOOLS
from agents.analysis_agents.oem_agent.tool import OEM_TOOLS
from agents.analysis_agents.policy_agent.tool import POLICY_TOOLS
from agents.analysis_agents.supply_agent.tool import SUPPLY_TOOLS
from agents.validation_agents.cross_agent.tool import CROSS_TOOLS
from agents.validation_agents.hallu_agent.tool import HALLU_TOOLS
from agents.validation_agents.report_agent.tool import REPORT_TOOLS

from supervisor.workflow import build_supervisor_workflow
from supervisor.report_generator import generate_pdf_report, generate_text_report


# Analysis Agents
finance_agent = create_react_agent(
    model="openai:gpt-4o",
    tools=FINANCE_TOOLS,
    prompt="You are a finance analysis agent. Analyze capital markets, funding flows, stock movements.",
    name="finance_agent"
)

market_agent = create_react_agent(
    model="openai:gpt-4o",
    tools=MARKET_TOOLS,
    prompt="You are a market analysis agent. Analyze global EV demand, pricing trends, consumer sentiment.",
    name="market_agent"
)

oem_agent = create_react_agent(
    model="openai:gpt-4o",
    tools=OEM_TOOLS,
    prompt="You are an OEM strategy agent. Track automakers' production plans and partnerships.",
    name="oem_agent"
)

policy_agent = create_react_agent(
    model="openai:gpt-4o",
    tools=POLICY_TOOLS,
    prompt="You are a policy analysis agent. Evaluate government policies and regulations.",
    name="policy_agent"
)

supply_agent = create_react_agent(
    model="openai:gpt-4o",
    tools=SUPPLY_TOOLS,
    prompt="You are a supply chain agent. Analyze material sourcing and supply health.",
    name="supply_agent"
)

# Validation Agents
cross_agent = create_react_agent(
    model="openai:gpt-4o",
    tools=CROSS_TOOLS,
    prompt="You are a cross-layer validator. Ensure consistency among all analyses.",
    name="cross_agent"
)

hallu_agent = create_react_agent(
    model="openai:gpt-4o",
    tools=HALLU_TOOLS,
    prompt="You are a hallucination auditor. Identify unsupported claims.",
    name="hallu_agent"
)

report_agent = create_react_agent(
    model="openai:gpt-4o",
    tools=REPORT_TOOLS,
    prompt="You are a report quality reviewer. Assess structure and completeness.",
    name="report_agent"
)

# Agent dictionaries
analysis_agents = {
    "finance_agent": finance_agent,
    "market_agent": market_agent,
    "oem_agent": oem_agent,
    "policy_agent": policy_agent,
    "supply_agent": supply_agent,
}

validation_agents = {
    "cross_agent": cross_agent,
    "hallu_agent": hallu_agent,
    "report_agent": report_agent,
}


async def run_analysis(query: str) -> None:
    """Run deterministic supervisor workflow and generate reports."""

    supervisor = build_supervisor_workflow(
        analysis_agents=analysis_agents,
        validation_agents=validation_agents,
    )

    print("=" * 80)
    print("EV MARKET INTELLIGENCE - SUPERVISOR WORKFLOW")
    print("=" * 80)
    print(f"Query: {query}\n")

    state = await supervisor(query)

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

    print(f"\nSteps executed: {state.total_steps}")
    print(f"Stage: {state.stage}")
    print(f"Retries: {state.retry_count}\n")

    print("FINAL REPORT:")
    print("-" * 80)
    print(state.final_report)
    print("-" * 80)

    try:
        text_path = generate_text_report(state.final_report)
        print(f"\nText report saved: {text_path}")
    except Exception as e:
        print(f"Text report generation failed: {e}")

    try:
        pdf_path = generate_pdf_report(state.final_report)
        print(f"PDF report saved: {pdf_path}")
    except ImportError:
        print("PDF generation skipped: reportlab not installed. Run: pip install reportlab")
    except Exception as e:
        print(f"PDF generation failed: {e}")


if __name__ == "__main__":
    load_dotenv()

    query = (
        "Provide comprehensive EV industry analysis covering all critical aspects: "
        "finance trends, market dynamics, OEM strategies, policy landscape, and supply chain status"
    )

    asyncio.run(run_analysis(query))
