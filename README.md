# EV Market Intelligence Supervisor Skeleton

This repository contains a skeleton implementation of a Supervisor-based LangGraph architecture for an EV Market Intelligence system. It provides structure, shared state definitions, agent prompts, and supervision safeguards that can be extended into a production-grade workflow.

## Architecture Overview

- **Supervisor-first orchestration** using `create_supervisor` to coordinate analysis and validation agents.
- **Five analysis agents** (Market, Policy, OEM, Supply Chain, Finance) built with ReAct-style prompts.
- **Three validation agents** (Cross-layer Validation, Report Quality Check, Hallucination Check) reviewing outputs before publication.
- **Shared state** tracks task inputs, intermediate notes, decisions, and retry counts to prevent infinite loops.
- **Tool skeletons** outline integrations for data access, report assembly, and audit logging.

## Project Layout

```
src/
  ev_market_supervisor/
    __init__.py
    main.py
    supervisor/
      __init__.py
      builder.py
    agents/
      __init__.py
      analysis.py
      validation.py
    prompts/
      __init__.py
      prompts.py
    states/
      __init__.py
      state.py
    tools/
      __init__.py
      tools.py
```

Extend each placeholder with domain-specific logic, tooling, and LangGraph wiring as your EV intelligence workflow evolves. `main.py` contains the high-level `build_workflow` helper to assemble the graph and relies on the class-based skeleton in the `agents`, `prompts`, `states`, `tools`, and `supervisor` packages.

## Getting Started

Install dependencies:

```bash
pip install -e .
```

Then wire your preferred LLM client, implement the tool stubs, and call `build_workflow` from `ev_market_supervisor.main` to compile the graph.
# ai-agent-ev
