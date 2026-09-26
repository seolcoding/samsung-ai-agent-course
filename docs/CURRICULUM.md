# 커리큘럼 정본 (2026-09-03)

과정 커리큘럼의 정본은 [`raw/2026-09-03_커리큘럼_제안서.pptx`](raw/2026-09-03_커리큘럼_제안서.pptx)다. 10차수 종료 후 고친 판이다. 이 문서는 그 슬라이드 2~5쪽의 표를 글로 옮긴 것이다. 두 자료가 다르면 PPTX를 따른다.
이전 판인 [`raw/2026-05-22_커리큘럼_제안서.pptx`](raw/2026-05-22_커리큘럼_제안서.pptx)는 비교용으로만 둔다.

통합 교안의 블록 번호(`1.1`~`4.3`)와 블록별 총시간은 이 정본을 따른다. 세부 주제의 분 배정은 [INSTRUCTOR_TIMING.md](INSTRUCTOR_TIMING.md)에 있다.

| 일차 | 블록 | 모듈 | 시간 |
|---|---|---|---:|
| 1일차 | 1.1 | AI Agent Design Thinking | 3.0H |
| | 1.2 | LLM 작동 원리와 개발 환경 준비 | 3.0H |
| | 1.3 | LangChain 프레임워크 깊이 학습 | 2.0H |
| 2일차 | 2.1 | RAG 이론과 핵심 모듈 실습 | 3.0H |
| | 2.2 | LangGraph 정통 이론 & 고급 기능 실습 | 3.0H |
| | 2.3 | Multi-Agent 협업 입문 / Streamlit 기반 RAG 서비스화 | 2.0H |
| 3일차 | 3.1 | 과정1 복습 & 심화 방향 정렬 | 2.0H |
| | 3.2 | MCP | 1.5H |
| | 3.3 | A2A 프로토콜 이해와 위임 구조 실습 | 1.5H |
| | 3.4 | LangGraph 심화 | 3.0H |
| 4일차 | 4.1 | Harness Engineering 핵심 원칙 | 2.0H |
| | 4.2 | Observability & Evaluation (Langfuse) | 2.0H |
| | 4.3 | 캡스톤 프로젝트: 리서치 자동화 멀티 에이전트 시스템 | 4.0H |

Part1(M1) 16H, Part2(M2) 16H, 합계 32H.

---

## Part1: LangChain&LangGraph 기반 AI Agent 챗봇 개발 과정 (M1, 16H)

### 1.1 AI Agent Design Thinking — 1일차 3.0H

AI 관점의 문제 재정의와 Agent 사고방식 정립

- AI/ML/LLM의 관계와 LLM의 본질(다음 토큰 예측) 이해
- Chatbot에서 Agent로의 전환: 함수 호출(Function Calling)과 행동 루프
- ReAct(Reasoning + Acting) 패턴의 작동 원리와 한계
- LangChain과 LangGraph가 필요한 이유: 오케스트레이션과 상태 관리
- 개발 환경 구성: VS Code, CodeMate, venv, .env 기반 키 관리

### 1.2 LLM 작동 원리와 개발 환경 준비 — 1일차 3.0H

LLM API 실습을 위한 기반 정비

- LLM 학습/추론 흐름, Tokenization, Context Window 핵심 개념
- System/User/Assistant 역할 분리와 대화 구조 설계
- 모델 파라미터(Temperature, Top-p)와 출력 특성 이해
- [실습] OpenAI SDK 기반 single-turn / multi-turn / streaming 호출
- [실습] LangChain get_llm() 래퍼를 통한 모델 호출 일원화

### 1.3 LangChain 프레임워크 깊이 학습 — 1일차 2.0H

LCEL, Tool Calling, Structured Output, Memory

- LCEL 설계 철학과 Pipe(|) 기반 체인 구성
- Runnable 인터페이스: RunnableParallel / RunnablePassthrough / RunnableLambda
- Tool Calling 메커니즘: 스키마 기반 도구 선택, 수동 루프 처리
- Output Parser vs with_structured_output() 비교
- 메모리 전략 1: RunnableWithMessageHistory 기반 세션 메모리
- 메모리 전략 2: LangGraph + MemorySaver 기반 상태 내장 메모리
- [실습] 날씨/계산 도구를 활용한 자율 도구 선택 체인 구현
- [실습] 구조화 출력(MovieReview) 파싱 및 안정성 비교

### 2.1 RAG 이론과 핵심 모듈 실습 — 2일차 3.0H

문서 기반 QA 파이프라인의 표준 구현

- RAG vs Fine-tuning 역할 분리
- Naive → Advanced → Modular RAG 발전 흐름
- RAG 핵심 모듈: Loading / Splitting / Embedding / Storage / Retrieval / Generation
- 청킹 전략(Fixed/Recursive/Semantic)과 임베딩 모델 선택 관점
- [실습] PDF 로딩/청킹/벡터스토어(Chroma) 구축
- [실습] LangChain RAG 체인 구성 및 스트리밍 응답 구현
- [실습] RAGaaS API 기반 사내형 RAG 구현 패턴 이해

### 2.2 LangGraph 정통 이론 & 고급 기능 실습 — 2일차 3.0H

StateGraph 기반 제어 가능한 Agent 설계

- LangGraph 핵심 구성요소: Node / Edge / State / Reducer
- Conditional Edge로 분기 제어(언어 감지 라우팅)
- ToolNode + tools_condition 기반 ReAct 루프 자동화
- Checkpointer를 활용한 중단/재개와 상태 영속화
- Human-in-the-loop(interrupt_before) 승인/거부 패턴
- [실습] 조건부 라우팅 + 도구 호출 + 재개 가능한 그래프 구현
- [실습] 대화형 HITL CLI 에이전트 구현

### 2.3 Multi-Agent 협업 입문 / Streamlit 기반 RAG 서비스화 — 2일차 2.0H

단일 Agent에서 역할 분리형 협업으로 확장

- 단일 Agent 한계: 역할 혼재, 컨텍스트 비대화, 도구 복잡도 증가
- 패턴 이해: Researcher-Writer 분업과 Supervisor 라우팅
- Structured Output(RouteDecision)으로 라우팅 결정 안정화
- [실습] Researcher(조사) + Writer(작성) 2-Agent 구현
- [실습] Supervisor가 상태를 보고 researcher/writer/finish를 선택하는 흐름 구성
- Streamlit 소개
- [실습] Langchain을 활용한 보험 약관 QA 챗봇 UI 구현 및 스트리밍 응답 연결

## Part2: MCP·A2A·Harness 기반 Multi-Agent 개발 실전 교육 (M2, 16H)

### 3.1 과정1 복습 & 심화 방향 정렬 — 3일차 2.0H

과정 1 핵심 개념 리프레시와 확장 축 소개

- LLM/Agent/LangChain/RAG/LangGraph 핵심 복습
- 과정 2 목표 정렬: MCP, A2A, LangGraph 심화, Harness, Observability
- 개발 환경 구성: VS Code, CodeMate, venv, .env 기반 키 관리
- [실습] 코드로 server, client 기초 이해
- [실습] review 코드로 기초 구성요소 재확인

### 3.2 MCP — 3일차 1.5H

Model Context Protocol 표준 연동 실습

- MCP 등장 배경: 함수 호출 난립과 도구 표준화 필요성
- 구성요소: Server / Host / Client
- 프리미티브: Tools / Resources / Prompts
- FastMCP로 서버 구현 및 SSE/stdio 전송 방식 이해
- [실습] 시간/BMI/할일 관리 MCP 서버 구현
- [실습] LangGraph Agent에서 MCP 도구 로드 후 호출

### 3.3 A2A 프로토콜 이해와 위임 구조 실습 — 3일차 1.5H

Agent-to-Agent 통신 표준 적용

- MCP와 A2A의 역할 구분(Agent↔Tool vs Agent↔Agent)
- 핵심 개념: Agent Card / Task / Message / Artifact
- Task 상태 추적 기반 비동기 위임 모델 이해
- [실습] LangGraph Agent를 A2A Server로 노출
- [실습] A2A Client로 task 생성/조회/완료 처리 구현
- [실습] Researcher(A2A) + Writer(로컬 LLM) 분업 흐름 구성

### 3.4 LangGraph 심화 — 3일차 3.0H

복잡한 워크플로우를 위한 고급 패턴

- Subgraph 컴포지션으로 모듈화
- Persistence: MemorySaver vs SqliteSaver, checkpoint 이력과 time-travel
- Checkpointer와 Store의 역할 분리(단기 대화 상태 vs 장기 사용자 기억)
- Parallel Execution: 정적 fan-out/fan-in, 동적 Send API
- [실습] 병렬 질의 처리 및 결과 집계 그래프 구현

### 4.1 Harness Engineering 핵심 원칙 — 4일차 2.0H

모델이 아니라 실행 환경을 설계하는 관점

- Harness Engineering의 배경과 필요성
- Workflow vs Agent 선택 기준
- skills 문서 기반 행위 제어 원리
- [실습] deepagents + FilesystemBackend + skills 디렉토리로 에이전트 구성
- [실습] 범위 이탈 요청 거절(system prompt)과 스킬 기반 응답 제어

### 4.2 Observability & Evaluation (Langfuse) — 4일차 2.0H

운영 품질 측정을 위한 추적·평가 체계 구축

- CallbackHandler 기반 LangChain/LangGraph 트레이싱
- @observe 기반 비체인 로직 추적
- 평가 방법: 규칙 기반, 사용자 피드백, LLM-as-a-Judge
- 다차원 점수화: 정확성/관련성/완성도 등 지표 기록
- [실습] Langfuse 대시보드에서 trace와 score 검증
- 에이전트 활용 소개: Moody's와 Salesforce 사 예시

### 4.3 캡스톤 프로젝트: 리서치 자동화 멀티 에이전트 시스템 — 4일차 4.0H

4일 학습요소 통합 구현 (자유 주제 혹은 스켈레톤 코드 기반 개발 중 선택)

- 스켈레톤 코드 통합 아키텍처: Supervisor → Researcher(MCP+RAG+웹검색) → HITL 승인 → Writer
- Researcher/Writer 역할별 SKILL.md 적용
- MCP 파일시스템 서버 연동 + 로컬 문서 검색
- Human Approval(interrupt_before) 기반 승인형 작성 플로우
- 최종 보고서 자동 평가(LLM Judge)와 Langfuse 점수 기록

---

## 2026-05-22 판에서 바뀐 점

| 항목 | 05-22 판 | 09-03 정본 |
|---|---|---|
| 1일차 구성 | Design Thinking 1.0H · LLM 1.5H · LangChain 3.5H · RAG 2.0H | Design Thinking 3.0H · LLM 3.0H · LangChain 2.0H |
| 개발 환경 구성 | LLM 모듈 안, CodeMate 없음 | Design Thinking 모듈 안, CodeMate 포함 |
| RAG | 1일차 | 2일차 첫 블록 |
| Streamlit | 별도 모듈 2.5H | Multi-Agent 블록에 합침 |
| 3일차 복습 | 0.5H | 2.0H, 환경 구성·server/client 실습 추가 |
| MCP · A2A | 2.0H · 2.5H | 1.5H · 1.5H |
| Langfuse | 2.9H | 2.0H, Moody's·Salesforce 사례 추가 |
| 캡스톤 | 3.5H, end-to-end 실습 | 4.0H, 자유 주제 또는 스켈레톤 선택 |
| 결과 정리·운영 전환 가이드 (0.5H) | 있음 | 없음 |

## 수강생 피드백

11차수 만족도 설문과 운영 측 수정 요청은 [2026_11차수_수강생피드백.md](2026_11차수_수강생피드백.md)에 정리했다.
