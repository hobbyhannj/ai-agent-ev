# EV Market Analysis by Multi-Agent with Supervisor

LangGraph 기반 멀티 에이전트 구조를 활용해 EV 시장과 관련된 다층 데이터를 수집·교차 분석하고, 최종 결과를 PDF 보고서로 출력합니다.

---

## 1. 프로젝트 개요
- **주제**: 전기차 시장 트렌드 분석 Agent 개발
- **목적**: 사용자의 질문을 입력으로 받아 시장, 정책, OEM, 공급망, 금융 레이어 데이터를 종합 분석한 뒤 Mobility Briefing 스타일의 PDF 보고서를 자동 생성
- **주요 활용처**: 전기차 산업을 추적하는 투자자, 애널리스트, 전략 기획 담당자

### 주제 선정 이유
1. 전기차 산업은 정책, 제조사, 공급망, 금융이 복잡하게 얽혀 있어 단일 소스 분석으로는 한계가 존재
2. LangGraph의 멀티 에이전트 구조가 레이어별 분석과 상호 검증에 적합
3. 자동 생성된 심층 보고서는 실제 의사결정 업무에 즉시 적용 가능

### 핵심 기능
1. **5개 레이어 병렬 데이터 수집**: 시장(Market), 정책(Policy), 완성차(OEM), 공급망(Supply Chain), 금융(Finance)
2. **Cross-layer 상관관계 분석**: 예) 리튬 가격 상승 → 배터리 기업 수익성 및 주가 영향
3. **다단계 검증 체계**: Cross-Layer Validation → Report Quality Check → Hallucination Check 순으로 신뢰도 확보
~~4. 쿼리 캐싱: 유사 질문(유사도 > threshold)에 대해 응답 속도 향상~~
5. **자동 PDF 패키징**: LLM이 메타데이터·차트를 설계하고 FastAPI 서비스를 통해 WeasyPrint PDF 생성

---

## 2. LangGraph 아키텍처
LangGraph는 다음과 같은 순서로 동작합니다.

```
                   ┌───────────────────────────────┐
                   │           Supervisor           │
                   │  (모든 단계의 진입·종료를 담당)  │
                   └──────────────┬────────────────┘
                                  │
         ┌──────────────┬─────────┼──────────┬──────────────┐
         ▼              ▼         ▼          ▼              ▼
     market_agent   policy_agent  oem_agent  supply_agent   finance_agent
         │              │         │          │              │
         └──────┬───────┴─────────┴──────────┴──────┬───────┘
                │                                   │
                ▼                                   ▼
        ┌───────────────┐                 ┌─────────────────┐
        │ Aggregation    │                 │  Validation Seq  │
        │ (cross-layer)  │                 │ (검증 체인 시작) │
        └──────┬─────────┘                 └────────┬────────┘
               │                                    │
               ▼                                    ▼
     ┌────────────────────┐          ┌────────────────────────┐
     │ cross_layer_validation │ → │ report_quality_check │ → │ hallucination_check │
     └────────────────────┘          └────────────────────────┘
                                               │
                                               ▼
                                       ┌────────────┐
                                       │ Supervisor │  ← 종료 및 Report finalize
                                       │ (exit loop)│
                                       └────────────┘

```

- Supervisor는 사용자 지시를 바탕으로 다섯 개 분석 에이전트를 호출하고, 결과를 공유 상태(SupervisorState)에 통합합니다.
- 검증 에이전트들은 순차적으로 실행되며 필요 시 재시도를 요청하거나 경고를 추가합니다.
- 최종 보고서는 `main.py`에서 수집한 후 LLM 메타데이터 생성 → 차트 렌더링 → FastAPI PDF 서비스 호출 순으로 처리됩니다.

---

## 3. 저장소 구조
```
.
├── agents/                     # 에이전트
│   ├── __init__.py
│   ├── analysis.py             # 5개 분석 에이전트 정의
│   └── validation.py           # 3개 검증 에이전트 정의
├── main.py                     # LangGraph 실행
├── print/                      # FastAPI 기반 프린트 서버
│   ├── __init__.py
│   ├── app.py                 
│   ├── main.py                
│   └── templates/
│       └── report.html         # HTML 템플릿
├── states/
│   ├── __init__.py
│   └── state.py                
├── supervisor/
│   ├── __init__.py
│   └── builder.py             
├── templates/                  # 프롬프트
│   ├── __init__.py
│   ├── market.py
│   ├── policy.py
│   ├── oem.py
│   ├── supply_chain.py
│   ├── finance.py
│   ├── cross_layer_validation.py
│   ├── report_quality_check.py
│   └── hallucination_check.py
├── tools/                      # 툴
│   ├── __init__.py
│   └── tools.py               
├── requirements.txt
└── README.md
```

---

## 4. 보고서 목차
1. **EXECUTIVE SUMMARY**: 사용자 질문 요약, 핵심 발견, 주요 수치, 결론
2. **MARKET OVERVIEW**: 글로벌/국가별 시장 규모, 성장률, 원자재 가격 및 거시 지표, EV 판매량·원자재 가격 차트
3. **POLICY/REGULATION**: 국가별 정책·보조금 비교, 규제 타임라인
4. **OEM ANALYSIS**: 주요 완성차 전략, 생산 계획, 점유율, 파트너십/M&A
5. **SUPPLY CHAIN ANALYSIS**: 배터리 공급망 구조, 기술 트렌드, 리스크, 밸류체인 다이어그램
6. **FINANCIAL OUTLOOK**: EV 관련 주가 및 밸류에이션, 감성 분석, 섹터별 수익률 비교
7. **CROSS-LAYER INSIGHTS**: 정책·원자재·OEM·금융 간 상호 영향 사례 및 인사이트
8. **REFERENCES**: 뉴스, 정부 자료, 기업 IR, 리서치 리포트, 금융 데이터 출처

각 섹션은 분석 에이전트의 결과와 검증 피드백을 바탕으로 자동 작성됩니다.

---

## 5. 변경 사항
- **LLM 메타데이터 생성**: 제목, 부제, 요약, 작성자/수신자 정보, 로고 URL, 차트 설계안을 LLM이 자동 산출
- **차트 자동 렌더링**: LLM이 제안한 시계열/막대형 데이터를 Matplotlib로 시각화하여 PDF에 삽입 (최대 4개)
- **Mobility 스타일 PDF**: 커버 페이지, 메타데이터 배너, 차트 갤러리, 안정적인 페이지 브레이크를 지원하는 HTML/CSS 템플릿
- **FastAPI PDF 서비스 고도화**: `POST /pdf`가 Base64 차트와 요약을 받아 WeasyPrint로 즉시 PDF 변환
- **의존성 추가**: `matplotlib`, `numpy`를 포함해 시각화 파이프라인을 구축

---

## 6. 실행 방법
### 6.1 환경 구성
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 6.2 LangGraph 워크플로 실행 및 PDF 출력
1. FastAPI PDF 서버 기동
   ```bash
   uvicorn print.main:app --host 0.0.0.0 --port 8080
   ```
2. Supervisor 실행 (LLM 메타데이터 및 차트 자동 생성)
   ```bash
   python main.py "2025년 일본 전기차 시장 전망 보고서를 작성해줘" \
     --pdf-output Mobility_New_Years_Briefing_2025.pdf
   ```
   - `--print-server-url`로 PDF 서버 주소를 변경할 수 있습니다.
   - 실행 후 `Mobility_New_Years_Briefing_2025.pdf`가 생성되며, 커버/차트가 자동 포함됩니다.

---

## 7. PDF 렌더링 API 요약
- **엔드포인트**
  - `POST /render`: HTML 미리보기 반환
  - `POST /pdf`: PDF 스트림 응답 (다운로드 가능)
- **요청 본문 (예시)**
  ```json
  {
    "title": "Mobility New Year's Briefing 2025",
    "subtitle": "EV Transformation Outlook for Japan",
    "prepared_for": "Mobility Strategy Team",
    "prepared_by": "EV Market Supervisor",
    "summary": "시장 성장은 정책 지원과 충전 인프라 확장에 힘입어 가속화되고 있습니다.",
    "logo_url": "https://example.com/logo.svg",
    "charts": [
      {
        "title": "EV Sales Mix",
        "caption": "Source: METI, JADA",
        "media_type": "image/png",
        "image_base64": "<base64 데이터>"
      }
    ],
    "report": "=== Final Report ===\n\n1. EXECUTIVE SUMMARY ..."
  }
  ```
- Supervisor CLI는 위 스키마를 LLM과 Matplotlib로 자동 채웁니다.

---