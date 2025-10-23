# EV Market Intelligence Supervisor Skeleton

This repository contains a skeleton implementation of a Supervisor-based LangGraph architecture for an EV Market Intelligence system. It provides structure, shared state definitions, agent prompts, and supervision safeguards that can be extended into a production-grade workflow.

## Architecture Overview

- **Deterministic supervisor orchestration** coordinating analysis and validation agents in a fixed sequence.
- **Five analysis agents** (Market, Policy, OEM, Supply Chain, Finance) built with ReAct-style prompts.
- **Three validation agents** (Cross-layer Validation, Report Quality Check, Hallucination Check) reviewing outputs before publication.
- **Shared state** tracks task inputs, intermediate notes, decisions, and retry counts to prevent infinite loops.
- **Automatic PDF packaging**: the supervisor now asks the LLM for cover metadata, generates charts with Matplotlib, and streams a styled PDF via the FastAPI print service.

## Repository Layout

```
.
├── agents/
│   ├── __init__.py
│   ├── analysis.py
│   └── validation.py
├── main.py
├── print/
│   ├── __init__.py
│   ├── app.py
│   ├── main.py
│   └── templates/
│       └── report.html
├── states/
│   ├── __init__.py
│   └── state.py
├── supervisor/
│   ├── __init__.py
│   └── builder.py
├── templates/
│   ├── __init__.py
│   ├── market.py
│   ├── policy.py
│   ├── oem.py
│   ├── supply_chain.py
│   ├── finance.py
│   ├── cross_layer_validation.py
│   ├── report_quality_check.py
│   └── hallucination_check.py
├── tools/
│   ├── __init__.py
│   └── tools.py
├── requirements.txt
└── README.md
```

`main.py` assembles the workflow, orchestrates the LangGraph execution, and (when `--pdf-output` is supplied) calls the FastAPI PDF service in `print/` with LLM-generated metadata and charts.

## LangGraph Workflow

```
          ┌─────────────┐
          │  Supervisor │
          └──────┬──────┘
                 │
       ┌─────────▼─────────┐
       │ Analysis Fan-out  │
       └─────────┬─────────┘
         market  policy  oem
           │       │      │
         supply_chain   finance
                 │
          ┌──────▼──────┐
          │ Aggregation │   (shared state updates)
          └──────┬──────┘
                 │
       ┌─────────▼─────────┐
       │ Validation Chain  │
       └─────────┬─────────┘
      cross_layer_validation
             │
      report_quality_check
             │
      hallucination_check
             │
          ┌──▼──┐
          │Exit │
          └─────┘
```

- The supervisor schedules five analysis agents in parallel; their notes feed back into shared state.
- Validation agents run sequentially, each able to request retries or add warnings before finalizing `final_report`.
- `main.py` captures the final report, asks the LLM for cover/summary/chart plans, renders plots, and ships everything to the PDF service.

## 프로젝트 개요 (sk090-한정석-AI서비스-MINI-DAY-1)

- **주제**: 전기차 시장 트렌드 분석 Agent 개발
- **내용**: 사용자가 EV 시장을 질의하면 다중 레이어 데이터(시장, 정책, OEM, 공급망, 금융)를 수집·교차 분석해 PDF 보고서로 제공
- **주제 선정 이유**
  1. EV 산업은 정책·제조사·공급망·금융이 긴밀하게 얽혀 있어 통합 분석이 필수
  2. LangGraph 멀티 에이전트 구조가 레이어별 분석 및 상호 검증에 최적
  3. 실제 투자자·애널리스트가 활용 가능한 리서치 자동화 흐름 제공
- **핵심 기능**
  1. 5개 레이어 병렬 데이터 수집 (시장, 정책, 완성차, 공급망, 금융)
  2. Cross-layer 상관관계 분석 (예: 원자재 가격 → OEM 마진/주가 영향)
  3. 다단계 검증으로 보고서 신뢰도 보강
  4. 유사 쿼리 캐싱으로 반복 질문 응답 속도 향상
- **보고서 목차**: Executive Summary, Market Overview, Policy/Regulation, OEM Analysis, Supply Chain Analysis, Financial Outlook, Cross-layer Insights, References (자동 생성 PDF에 동일하게 반영)

## Recent Enhancements

- LLM이 제목·부제·요약·수신자·작성자를 자동 생성하고, 최대 4개의 차트 설계안을 만들어 Matplotlib로 시각화합니다.
- 새 템플릿은 Mobility briefing 스타일의 커버 페이지, 섹션별 여백 제어, 차트 갤러리를 포함합니다.
- FastAPI PDF 서비스가 표지 로고, 차트, 하이라이트 요약을 받아 WeasyPrint로 안정적인 페이지 브레이크를 유지합니다.
- `requirements.txt`에 Matplotlib/Numpy를 추가하여 차트 랜더링을 지원합니다.

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
