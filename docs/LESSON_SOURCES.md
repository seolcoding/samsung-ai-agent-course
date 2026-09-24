# 통합 교안의 출처와 실행 범위

학습자 정본은 `lessons/day01.ipynb`~`day04.ipynb`다. 이 문서는 원본을 어떻게 재배치했는지 기록한다. 이론의 세부 쪽수와 63개 의미 번호는 [조립 지도](INTEGRATED_LESSONS.md)를 따른다. PDF 원본은 수정하지 않았다.

## 블록별 대응

| 통합 번호 | 원본 PDF와 범위 | 원본 코드 | 통합본의 실행과 보완 |
| --- | --- | --- | --- |
| 1.1.1~1.1.5 | 1-1, 2~22쪽 | M1 기초 설명 | 포함 관계·도구 제안·검사·반복 종료를 작은 Python 예제로 재구성. 환경 점검 추가 |
| 1.2.1~1.2.5 | 1-2, 4~19쪽 | Chapter01/01-llm-api | 토큰 선택 비유·컨텍스트·MockTransport 요청/응답. 실제 모델은 get_llm() 분기 |
| 1.3.1~1.3.5 | 1-3, 4~14쪽 | Chapter01/02-langchain | LCEL·create_agent·Pydantic·세션 이력. 실제 LangChain에 명시적 모델 대역 사용 |
| 2.1.1~2.1.5 | 1-4, 4~19쪽 | Chapter01/03-rag | 1일차 폴더에 있던 RAG를 커리큘럼 2일차로 이동. 합성 문서·실제 splitter/Chroma·RAGaaS mock |
| 2.2.1~2.2.5 | 2-1, 4~10쪽 및 상태·승인 설명 | Chapter01/04-langgraph | 실제 StateGraph·ToolNode·interrupt/Command. 외부 메일 발송을 포함하지 않음 |
| 2.3.1~2.3.5 | 2-2·2-3의 역할 분리와 UI | Chapter01/05-multi-agent, 06-rag-streamlit | 역할별 입출력·Streamlit 채팅·근거 없음 경로. 고정 Workflow와 자율 Agent 구분 |
| 3.1.1~3.1.4 | 3-1, 4~11쪽 | Chapter02/00-review | M1 복습·패키지 점검·실제 ASGI 요청/응답·실패 경계 |
| 3.2.1~3.2.4 | 3-2, 4~12쪽 | Chapter02/01-mcp | FastMCP Tools/Resources/Prompts, in-memory 및 별도 프로세스 stdio 실행 |
| 3.3.1~3.3.4 | 3-3, 4~15쪽 | Chapter02/02-a2a | A2A SDK 1.x Card·JSON-RPC·즉시 Message. 장기 Task는 개념 설명과 확장 과제 |
| 3.4.1~3.4.5 | 3-4, 3~10쪽 | Chapter02/03-langgraph-advanced | Subgraph·Checkpointer+Store·Send·Reducer·빈 입력과 중복 처리 |
| 4.1.1~4.1.5 | 4-1, 4~22쪽 | Chapter02/04-harness | 목표·실행·검사 루프, 실제 Skill 파일과 DeepAgents/FilesystemBackend |
| 4.2.1~4.2.5 | 4-2, 4~13쪽 | Chapter02/05-observability | 로컬 Callback·규칙 검사·선택적 Langfuse 전송/Judge. 공식 사례 보완 |
| 4.3.1~4.3.6 | 4-3, 2~9쪽 | Chapter02/06-capstone | 검증 가능한 규칙 Supervisor·MCP·작성 전 승인·Writer·검사·완성 Streamlit 앱 |

원본 PDF 위치는 [COURSE_MAP.md](COURSE_MAP.md), 의미 번호별 시간은 [INSTRUCTOR_TIMING.md](INSTRUCTOR_TIMING.md)에 있다. 원본 코드의 파일명·순서를 그대로 복제하지 않았으며 새로운 구현은 `src/courseware/`에 모았다.

## 공식 보완 자료

- 그림 제작: [OpenAI Image prompting guide](https://developers.openai.com/api/docs/guides/image-prompting). GPT Image 2.5 교육용 시각자료 가이드를 참고해 대상·목표·관계·제약을 명시했다. 이미지 생성 도구의 실제 모델 ID는 제공되지 않는다.
- 그래프 재개: [LangGraph interrupt](https://reference.langchain.com/python/langgraph/types/interrupt), [Command](https://reference.langchain.com/python/langgraph/types/Command), [Send](https://reference.langchain.com/python/langgraph/types/Send).
- MCP 연결: [FastMCP transports](https://gofastmcp.com/clients/transports). 교안 코드는 잠금 파일의 3.4.7로 검증한다.
- A2A 변경: [공식 SDK 1.0 migration](https://github.com/a2aproject/a2a-python/blob/main/docs/migrations/v1_0/README.md).
- 관측: [Langfuse instrumentation](https://langfuse.com/docs/observability/sdk/instrumentation), [LangChain integration](https://langfuse.com/integrations/frameworks/langchain).
- 사례: [Moody’s, The rise of the digital colleague](https://www.moodys.com/web/en/us/insights/resources/the-rise-of-the-digital-colleague.pdf), [Salesforce, View Test Results](https://trailhead.salesforce.com/content/learn/modules/agentforce-agent-testing/view-test-results). 공개 자료의 관점과 수업용 적용을 구분한다. 특정 제품의 현재 성능이나 Langfuse 사용 여부를 주장하지 않는다.

확인일: 2026-09-24. 최신 웹 문서와 잠금 파일의 API가 다를 수 있으므로 실제 실행 검증은 설치된 패키지를 기준으로 한다.

## 그림 원본과 프롬프트

개념 그림 8개는 내장 image_gen으로 생성했다. 정확한 도식 16개는 Graphviz 원본을 함께 둔다. 24개 모두 노트북에 attachment로 포함하며 각각 한국어 설명을 붙인다. 이미지의 짧은 영문 라벨은 아래 설명에서 해석한다.

| 개념 그림 | 의미 번호 | 생성 프롬프트 |
| --- | --- | --- |
| agent_control.png | 1.1.2 | course_visual_prompts.json의 agent_control |
| context_window.png | 1.2.2 | context_window |
| rag_evidence.png | 2.1.1 | rag_evidence |
| multiagent_review.png | 2.3.2 | multiagent_review |
| mcp_a2a.png | 3.3.1 | mcp_a2a |
| memory_scopes.png | 3.4.2 | memory_scopes |
| harness_loop.png | 4.1.1 | harness_loop |
| trace_quality.png | 4.2.1 | trace_quality |

- 개념 이미지: [lessons/assets/suite](../lessons/assets/suite/)
- 도식 `.dot`·`.svg`·`.png`: [lessons/assets/diagrams](../lessons/assets/diagrams/)
- [공통 제작 틀](templates/course_visual_brief.md) · [실제 생성 프롬프트](templates/course_visual_prompts.json)
- 각 이미지 셀의 `metadata.asset_source`에 원본 경로를 기록했다. 이미지를 바꾸면 노트북 attachment도 갱신한다.

## 구현 범위와 대체 이유

- 기본 실행은 실제 LangChain/LangGraph/MCP/A2A/Chroma/DeepAgents/Streamlit을 사용한다. 모델 응답·임베딩·자료는 명시된 교육용 대역이다. 그 결과는 실제 모델 품질이나 사내 연결 검증을 의미하지 않는다.
- API 기본 요청 형태는 Chat Completions 관점으로 설명한다. reasoning·temperature·도구 호출 지원은 `src/config/`에서 모델과 provider별로 확인한다.
- RAGaaS 모의 응답은 2.1.4에서 별도로 검사한다. 캡스톤은 합성 자료를 제공하는 MCP 검색을 사용한다. 웹 검색·사내 RAGaaS 연결은 승인된 환경에서 어댑터를 추가할 확장 과제다.
- 캡스톤 승인은 **작성 전 근거 승인**이다. 초안 발행 승인이 필요한 업무라면 작성 후 두 번째 승인 노드를 추가한다. 기본 앱은 실제 발행·전송을 하지 않는다.
- 원본 전체를 최신 SDK로 마이그레이션한 것은 아니다. 기존 raw/solution의 알려진 결함은 AGENTS.md에 남겨 두고 통합본의 검증 범위와 구분한다.
