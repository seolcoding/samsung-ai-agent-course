# 커리큘럼과 자료 버전

2026-09-06 수집한 PPTX 두 개의 슬라이드 본문과 표를 읽어 정리했다. 두 파일은 각각 5장이다. 실습 코드의 실행이나 API 호환성을 검증한 결과는 아니다.

| 구분 | 수신일 | 표지 날짜 | 용도 |
| --- | --- | --- | --- |
| 이전 자료 | 2026-08-28 | 2026-05-22 | 제안 당시 공유한 커리큘럼 |
| 최신 수신 자료 | 2026-09-04 | 2026-09-03 | 10차수 종료 후 수정본. 준비의 우선 참고 자료 |

[이전 PPTX](../private/attachments/1a0478555b507e10/삼성전자_AI_Agent_개발_프로젝트_교육.pptx), [최신 PPTX](<../private/attachments/1a069d0b23566414/(10차수 종료) 삼성전자_AI_Agent_개발_프로젝트_교육_제안서_0903.pptx>)

## 최신 수신본의 4일 구성

| 일차 | 모듈 | 시간 |
| --- | --- | --- |
| 1일차 / M1 | AI Agent Design Thinking 및 개발 환경 구성 | 3.0H |
| 1일차 / M1 | LLM 작동 원리와 API 호출, get_llm 래퍼 | 3.0H |
| 1일차 / M1 | LangChain: LCEL, Tool Calling, Structured Output, Memory | 2.0H |
| 2일차 / M1 | RAG 이론과 핵심 모듈, RAGaaS 패턴 | 3.0H |
| 2일차 / M1 | LangGraph: StateGraph, 조건 분기, 도구 호출, 중단·재개, HITL | 3.0H |
| 2일차 / M1 | Multi-Agent 협업 입문 및 Streamlit RAG 서비스화 | 2.0H |
| 3일차 / M2 | M1 복습, 환경 구성, server/client 기초 | 2.0H |
| 3일차 / M2 | MCP: 구성요소, Tools/Resources/Prompts, FastMCP | 1.5H |
| 3일차 / M2 | A2A: Agent Card, Task, 위임과 상태 추적 | 1.5H |
| 3일차 / M2 | LangGraph 심화: Subgraph, Persistence, Store, 병렬 처리 | 3.0H |
| 4일차 / M2 | Harness Engineering, deepagents, FilesystemBackend, skills | 2.0H |
| 4일차 / M2 | Langfuse 관측·평가 및 Moody's·Salesforce 사례 소개 | 2.0H |
| 4일차 / M2 | 캡스톤: 자유 주제 또는 스켈레톤 코드 기반 개발 | 4.0H |

위 표의 시간을 합산하면 각 일차 8H, M1 16H, M2 16H, 한 차수 총 32H다. 2일차 Streamlit은 Multi-Agent 협업 입문 행에 함께 포함되며 독립적인 추가 2시간으로 계산하지 않는다. 출처는 최신 PPT 슬라이드 2~5다.

## 이전 자료와 달라진 점

- 1일차 Agent 사고방식·환경 준비가 1H에서 3H, LLM·호출 준비가 1.5H에서 3H로 늘었다. CodeMate가 환경 구성에 명시됐다.
- LangChain은 3.5H에서 2H로 줄었고 RAG는 1일차 2H에서 2일차 3H로 이동했다.
- 2일차 LangGraph는 3.5H에서 3H로 줄었다. 기존 별도 Streamlit 2.5H 항목은 Multi-Agent 협업 입문 2H 안에 포함됐다.
- 3일차 복습·환경 세팅은 0.5H에서 2H로 늘고 server/client 기초 실습이 추가됐다. MCP는 2H에서 1.5H, A2A는 2.5H에서 1.5H로 조정됐다.
- 4일차 Langfuse·평가 항목은 2H이며 기업 사례 소개가 추가됐다. 캡스톤은 3.5H에서 4H로 늘고 자유 주제 또는 스켈레톤 중 선택하도록 바뀌었다. 별도 0.5H 결과 정리 항목은 최신본에 없다.
- 이전본 4일차 Observability 시간은 원문에 `2.9H`로 적혀 있어 해당 일차 항목 합계가 8.9H다. 오타 여부를 단정하지 않고 원문 그대로 보존했다. 최신본 4일차 합계는 8H다.

## 메일의 환경 안내와 함께 확인할 부분

| PPT에 남아 있는 표현 | 메일·README 안내 | 사전 방문 확인 항목 |
| --- | --- | --- |
| PDF 로딩, 청킹, Chroma 구축 | 사내 문서의 Python 직접 열람 제한, 사내 RAG API로 커리큘럼 변경 | 로컬 문서 실습이 허용되는지, 실제 사용할 RAGaaS 예제와 대체 실습은 무엇인지 |
| 캡스톤 Researcher에 웹검색 포함 | 웹검색 MCP는 사내망 정책상 사용 불가 | 웹검색 단계의 사내 데이터·도구 대체 경로 |
| MCP 파일시스템 서버와 로컬 문서 검색 | 문서 접근 제약 및 MCP 정책 미확정 | 파일 접근이 허용된 실습 영역과 사용 가능한 서버 |
| OpenAI SDK 기반 호출 | 사내 교육용 REST API, 일부 OpenAI 호환 | 사내 base URL, 인증, 모델, streaming·tool calling·structured output 지원 |
| MCP SSE/stdio 실습 | SSE 개인 책임 사용, STDIO 코드 점검 필요라는 당시 안내 | 이번 교육에 허용되는 전송 방식과 점검 절차 |
| Langfuse 실습 | LangSmith 사용 불가, Langfuse 대체 및 LangSmith 강사 시연 안내 | Langfuse 접속·키·콜백 연결, 시연 범위와 배정 시간 |

표는 **원문 간 차이를 정리한 것**이다. 어느 항목이 현장에서 최종 승인됐는지는 메일만으로 확정하지 않는다. 환경 제약은 [8/28 메일](https://mail.google.com/mail/u/0/#all/1a046fd41a4b05ff), 도구·폴더 안내는 [9/4 첨부 README 사본](../private/attachments/1a069d0b23566414/README.redacted.txt)에 근거한다.

## 로컬에서 바로 읽을 자료

- [최신 PPT 텍스트 추출문](<../private/extracted/(10차수 종료) 삼성전자_AI_Agent_개발_프로젝트_교육_제안서_0903.md>)
- [이전 PPT 텍스트 추출문](../private/extracted/삼성전자_AI_Agent_개발_프로젝트_교육.md)
- [메일·첨부 원본 목록](SOURCES.md)

추출문은 PPT의 텍스트와 표 내용을 보존한 읽기용 자료다. 정확한 표 배치나 이미지가 필요하면 PPTX 원본을 확인한다.
