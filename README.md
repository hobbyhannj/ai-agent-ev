# EV Market Intelligence Supervisor Skeleton

This repository contains a skeleton implementation of a Supervisor-based LangGraph architecture for an EV Market Intelligence system. It provides structure, shared state definitions, agent prompts, and supervision safeguards that can be extended into a production-grade workflow.

## Architecture Overview

- **Deterministic supervisor orchestration** coordinating analysis and validation agents in a fixed sequence.
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

Two supervisor entry points are available:

| Workflow | Module | Description |
| --- | --- | --- |
| Deterministic pipeline | `main.py` | Runs agents sequentially without LangGraph feedback loops. |
| Minimal LangGraph demo | `python -m supervisor_langgraph.main` | Direct implementation of the official `create_supervisor` example (flight/hotel assistants). |

Choose the entry point that best fits your experimentation needs, provide the OPENAI credentials in your environment, and run one of the commands above with the desired task prompt.
### PDF Rendering Service

The `print` package exposes a FastAPI application that converts supervisor reports into styled HTML or PDF documents.

- Start the service: `uvicorn print.main:app --host 0.0.0.0 --port 8080`
- `POST /render` returns the rendered HTML for quick previews.
- `POST /pdf` streams a downloadable PDF; the payload mirrors the JSON schema used by `/render`.
- Sample payload:

  ```json
  {
    "title": "2025 Japan EV Market Outlook",
    "subtitle": "Supervisor Consolidated Findings",
    "prepared_for": "Executive Team",
    "prepared_by": "EV Market Supervisor",
    "logo_url": "https://example.com/brandmark.svg",
    "summary": "Short executive overview highlighted on the first content page.",
    "charts": [
      {
        "title": "EV Sales Mix",
        "caption": "Source: Company filings, 2024.",
        "media_type": "image/png",
        "image_base64": "<base64 string>"
      }
    ],
    "report": "=== Final Report ===\n\n1. EXECUTIVE SUMMARY..."
  }
  ```

When running `main.py`, supply `--pdf-output report.pdf` (and optionally `--print-server-url`) and the workflow will ask the LLM to craft the title, summary, recipients, and chart blueprints automatically before calling the PDF service.

# ai-agent-ev
