# 3-1 교안 노트북 — 목차 (v1, 2026-09-28)

- **권 제목**: 과정1 리뷰 & 과정2 목표 (PDF 제목 "3-1 과정1 리뷰 & 과정2 목표". 커리큘럼 이름은 "과정1 복습 & 심화 방향 정렬")
- **원본 슬라이드**: `course/Chapter02/slides/day01/3-1-course-one-review-and-advanced-direction.pdf` (11쪽. 표지 p1, 목차 p2, 장 표지 p3·p7, 본문 7쪽)
- **원본 코드**: `course/Chapter02/code/raw/00-review/` 4개, **TODO 없음**. 네 파일 모두 M1 코드와 같다(아래 3절)
  - `00_langchain.py` (TODO 없음) = M1 `01-llm-api/03_langchain.py`
  - `01_researcher_writer.py` (TODO 없음) = M1 `05-multi-agent/01_researcher_writer.py`의 TODO를 채운 모양
  - `02_tool_calling.py` (TODO 없음) = M1 `02-langchain/02_tool_calling.py`(솔루션)
  - `03_langchain_rag.py` (TODO 없음) = M1 `03-rag/04_langchain_rag.py`(솔루션). `data/meritz_pet_insurance.pdf`를 읽는다
- **커리큘럼**: 3일차 3.1 "과정1 복습 & 심화 방향 정렬" 2.0H. 항목은 ① LLM/Agent/LangChain/RAG/LangGraph 핵심 복습 ② 과정 2 목표 정렬 ③ 개발 환경 구성(VS Code, CodeMate, venv, .env) ④ [실습] 코드로 server, client 기초 이해 ⑤ [실습] review 코드로 기초 구성요소 재확인.
- **시간 분배 가정**: LEC 30분(과정 2 목표가 "3일차 시작 커리큘럼 소개 30분 이내" 운영 요청을 겸한다) + 환경 확인 20분 + LAB 60분 + 여유 10분. 슬라이드에 환경 구성·server/client 내용이 없어 이 가정은 5절 질문 1·2의 답에 따라 바뀐다.
- **산출물**: `course/Chapter02/notebooks/3-1_review_LEC.ipynb`, `course/Chapter02/notebooks/3-1_review_LAB.ipynb` (`build_lab.py`의 UNITS에 `"00-review": ("3-1", "review")`가 이미 있다. spec은 `dev/builders/labs/Chapter02/00-review.json`, 아직 없음)
- **실행 검증**: 이 목차 단계에서는 코드를 실행하지 않았다. `VALIDATION.md`에 `00-review/03_langchain_rag`(솔루션)가 사외에서 답한 뒤 입력을 기다리는 구조로 확인된 기록만 있다. 호출 수·시간은 코드 구조로 추정한 값이다.

## 1. LEC 목차

슬라이드 PDF.js + C 수준 설명(슬라이드 요약, 내용 있는 곳만 "왜 배우나") + 4지선다 퀴즈. 코드 셀 없음.

| # | 절 제목 | 슬라이드 | 핵심 메시지 (근거 쪽) | 왜 배우나 | 퀴즈 |
|---|---|---|---|---|---|
| 1 | 도입 | p1–2 | 두 장: 과정 1 리뷰(LLM·Agent·LangChain, RAG, LangGraph) → 과정 2 목표(MCP와 A2A, LangGraph 심화, Harness Engineering, Observability) (p2) | — | — |
| 2 | LLM, Agent, LangChain | p3–4 | LLM은 "다음에 어떤 말이 나올까"를 예측하는 모델. Function(Tool) Calling은 LLM 출력을 해석해 컴퓨터 기능을 실행하는 것. Agent는 함수 호출과 결과 검토를 반복해 복잡한 작업을 처리하는 LLM 파이프라인. LangChain(LangGraph)은 LLM 워크플로를 만드는 라이브러리 (p4). 슬라이드 코드는 `prompt | model | parser` 체인 (p4) | 과정 2의 MCP·A2A는 모두 "도구를 부르고 결과를 검토하는 반복" 위에 올라간다. 이 정의를 먼저 맞춘다 | Agent를 가장 잘 설명한 것은? (함수 호출과 결과 검토를 반복하는 LLM 파이프라인) |
| 3 | RAG (Streamlit) | p5 | 문서를 쪼개 의미 비교가 가능한 형태로 바꾸고, 질문과 가장 연관된 문서를 검색해, 답을 만들 때 문서 내용을 더한다. 예시는 M1의 보험 약관 QA 챗봇 (p5) | — | RAG의 단계가 **아닌** 것은? (보기: 문서 쪼개기 / 유사 문서 검색 / 답변에 문서 내용 더하기 / 모델 재학습) |
| 4 | 복잡한 Agent 표현을 위한 LangGraph | p6 | 실행 흐름을 그래프로 표현해 분기·반복을 다룬다. State로 실행 맥락 관리, Node·Edge로 흐름 구성, Conditional Edge로 조건부 분기, ToolNode·Human-in-the-loop 같은 패턴 표현. 그림: 사용자 요청 → Supervisor → Research/Writer/Critic Agent → 최종 답변 (p6) | — | 조건에 따라 다음 노드를 고르는 요소는? (Conditional Edge) |
| 5 | MCP와 A2A | p7–8 | MCP는 Agent와 Tool·데이터 소스를 연결하고, A2A는 Agent와 Agent 사이에서 작업을 위임한다. 둘 다 "표준 방식으로 연결"하는 흐름 (p8) | 3일차 오후 두 권(MCP, A2A)의 출발점이다. 무엇과 무엇을 잇는지로 둘을 구분한다 | 한 Agent가 다른 Agent에게 작업을 맡기는 표준은? (A2A) |
| 6 | LangGraph 심화 | p9 | Subgraph로 모듈화, Persistence로 상태 저장·재개, Parallel Execution으로 병렬 처리, Memory Store로 장기 기억 관리 (p9) | — | 장기 기억을 관리하는 기능은? (Memory Store) |
| 7 | Harness Engineering | p10 | Agent가 안정적으로 일하도록 실행 환경과 맥락을 설계하는 관점. 컨텍스트 제공 방식 설계, 도구 사용 조건·실패 복구 전략 정의, Skill·지침·파일 구조를 Agent가 읽기 쉽게 정리 (p10) | 이 과정의 실습 방식(AI와 함께 코드 작성)이 곧 하네스 설계의 대상이다. 교육 목표 3(하네스·루프 엔지니어링)과 이어진다 | Harness Engineering에서 다루는 것이 **아닌** 것은? (보기: 컨텍스트 제공 / 도구 사용 조건·실패 복구 / Skill·지침·파일 구조 정리 / 모델 가중치 학습) |
| 8 | Observability | p11 | Agent가 실제로 어떻게 실행됐는지 추적·평가한다. Trace로 모델 호출·도구 실행·체인 흐름 확인, Score로 응답 품질 수치화, Langfuse로 로그·평가 관리, RAG·Agent 응답을 지속 개선 (p11) | — | 응답 품질을 수치로 나타내는 것은? (Score) |
| 9 | 정리 퀴즈 | — | 두 장의 핵심 | — | 4지선다 3문항: ① 상황 → 과정 2 주제 짝짓기(도구 연결=MCP / 병렬 처리=LangGraph 심화 / 실행 추적=Observability) ② Function Calling의 정의 ③ LangGraph에서 실행 맥락을 관리하는 것(State) |

- 퀴즈는 모두 4지선다, 정답은 슬라이드 문구에서만 만든다. 수강생 글·퀴즈에 쪽 표시를 넣지 않는다.
- "왜 배우나"의 3일차 오후 연결은 커리큘럼(3.2, 3.3), 교육 목표 3은 루트 AGENTS.md 2절에 근거한다.
- p4 슬라이드 코드(`ChatPromptTemplate` 체인)는 LAB의 `00_langchain.py`(메시지 목록 + `invoke`/`stream`)와 모양이 다르다. 슬라이드로만 보여 준다.

## 2. LAB 목차

첫 구획(접힌 준비 셀) → 보이는 코드 셀. TODO가 없으므로 네 장 모두 **예제 + AI에게 물어보기**(힌트 3문장 이내 + 🟢/⛔). 과제 없음.

| 장 | 원본 | 구분 | CHANGE_HERE 후보 | 성공 기준 초안 | 실행 제약 |
|---|---|---|---|---|---|
| 1 | (환경 확인) | — | — | 공통 "환경 점검" 셀(`check_env(["EMBED_PROVIDER"])`, 4장이 임베딩을 쓴다). 🟢 점검 결과가 모두 🟢 ⛔ ⛔ 표시 줄이 있으면 그 줄의 안내대로 `.env`를 고친다 | 호출 없음. 커리큘럼 ③ 개발 환경 구성은 이 장과 강사 진행으로 처리(5절 질문 1) |
| 2 | `00_langchain.py` | **예제** + 물어보기 | CHANGE_HERE: 16행<br>`HumanMessage(content='LLM이 무엇인지 3문장으로 설명해줘.'),`<br>(설명받고 싶은 개념으로 바꿔 본다. 예: RAG, Agent)<br>물어보기: `invoke`와 `stream`이 같은 `messages`를 받는데 출력이 어떻게 다른지 설명받기 | 🟢 같은 주제의 답이 두 번 나온다(한 번에 / 조금씩 이어서)<br>🟢 (물어보기) `stream`은 조각(chunk)을 차례로 돌려주고 `end=''`로 이어 붙인다는 점을 짚었다<br>⛔ 두 번째 답이 한 글자마다 줄이 바뀐다 → `end=''`가 지워졌는지 본다 | LLM 2회, 수 초~20초 |
| 3 | `02_tool_calling.py` | **예제** + 물어보기 | CHANGE_HERE: 92행<br>`print(run_with_tools('서울과 부산 날씨를 비교해줘'))`<br>(예: "제주 기온에 2를 곱해줘"로 두 도구를 이어 쓰게 한다)<br>물어보기: `run_with_tools`의 `while` 루프가 언제 끝나는지, `tool_call_id`가 왜 필요한지 설명받기 | 🟢 질문마다 `tool_calls`가 채워진 응답 → 마지막에 `tool_calls`가 빈 응답과 최종 답이 나온다<br>🟢 복합 질문에서 `get_weather`가 도시 수만큼 호출된다<br>🟢 (물어보기) `tool_calls`가 없을 때 끝난다, 도구 결과를 어느 호출의 답인지 짝지으려고 id를 쓴다<br>⛔ 날씨 질문에 "데이터를 찾을 수 없습니다"만 나온다 → 가짜 데이터에 있는 도시(서울·부산·제주)인지 본다 | LLM 6~8회, 약 30초~1분. raw의 `print(response)`는 응답 객체 전체를 찍어 출력이 길다(3절) |
| 4 | `01_researcher_writer.py` | **예제** + 물어보기 | CHANGE_HERE: 122행<br>`'messages': [HumanMessage(content='AI Agent 기술의 현황과 전망을 조사해서 글로 써줘.')],`<br>(조사할 주제를 바꿔 본다)<br>물어보기: `researcher_condition`과 엣지 네 줄을 붙여 넣고 노드가 실행되는 순서를 그림처럼 설명받기(고치지 말 것) | 🟢 "=== 최종 글 ===" 아래 서론·본론·결론 구조의 글이 나오고 가짜 검색 결과 문구(주요 플레이어: OpenAI, Anthropic, Google DeepMind 등)가 들어 있다<br>🟢 (물어보기) researcher → researcher_tools → researcher → writer 순서와 "`tool_calls`가 없으면 writer로 간다"를 짚었다<br>⛔ 셀이 끝나지 않는다 → 실행을 중지(■)하고 요청 문장을 다시 본다 | LLM 3회 안팎, 약 30초~1분. 가짜 검색 도구라 외부 호출 없음 |
| 5 | `03_langchain_rag.py` | **예제** + 물어보기 | CHANGE_HERE: 질문 변수(원본 56–60행의 `while True` + `input()`을 질문 한 번 실행으로 바꾼 뒤. M1 1-4와 같은 처리)<br>(약관에 대해 묻고 싶은 것으로 바꾼다)<br>물어보기: `{'context': retriever | format_docs, 'question': RunnablePassthrough()}`에서 질문 하나가 어디로 흘러가는지 설명받기 | 🟢 "RAG ready" 뒤 약관 내용에 근거한 답이 조금씩 출력된다<br>🟢 (물어보기) 질문이 검색기와 프롬프트 양쪽으로 가고, 검색 결과가 `context`가 된다는 점을 짚었다<br>⛔ 약관과 상관없는 일반론만 나온다 → 질문이 약관에 있는 내용인지, 검색 개수 `k`가 너무 작지 않은지 본다 | 임베딩 요청(청크 50개 안팎, 10개씩이면 약 5회) + LLM 1회, 약 30초~1분. PDF를 `notebooks/data/`에 둬야 한다 |
| 6 | 정리 | — | — | — | — |

- 장 순서: 슬라이드 순서(LLM·LangChain → Tool Calling → Agent·LangGraph → RAG)가 아니라 원본 파일 번호를 따르면 01(researcher_writer)이 02(tool_calling)보다 앞선다. 도구 호출 루프를 먼저 봐야 LangGraph의 `ToolNode`·조건부 엣지가 읽히므로 위 표는 00 → 02 → 01 → 03 순서를 제안한다(5절 질문 4).
- 네 장 모두 M1에서 한 번 실행·작성한 코드다. 이 권의 LAB은 "새로 배우기"가 아니라 "AI에게 설명을 받아 구조를 다시 읽기"에 무게를 둔다(커리큘럼 ⑤ "review 코드로 기초 구성요소 재확인").
- 합계: 예제 4장 = CHANGE_HERE 4곳 + 물어보기 4개.

## 3. 원본·솔루션 차이와 고른 쪽

| 파일 | 차이 | 고른 쪽 | 이유 |
|---|---|---|---|
| `00_langchain.py` | 차이 없음 | raw | — |
| `01_researcher_writer.py` | raw에만 이전 강사 메모 주석 13줄(19–24행 "LLM은 어떻게 도구를 사용하고…", 49–55행 "bind_tools의 역할은…") | **솔루션** | 코드는 같고 주석만 다르다. 메모 주석은 들여쓰기가 들쭉날쭉한 말투 메모라 셀에서 읽기 어렵다. "docstring이 LLM에게 도구 설명이 된다"는 내용은 3장(`02_tool_calling`)의 원본 주석에 이미 있다 |
| `02_tool_calling.py` | raw 68행에만 `print(response)` | **raw** | 이 줄이 없으면 최종 답만 보여 도구 호출 과정이 화면에 안 나온다. 복습 목적상 과정이 보이는 쪽을 고른다. 다만 응답 객체 전체라 길다. M1 1-3 LAB처럼 `print(call)`로 바꾸는 patch도 가능(5절 질문 3) |
| `03_langchain_rag.py` | 차이 없음 | raw | — |

노트북에서만 손볼 것(spec의 `patch`, 원본 파일은 그대로. M1 spec과 같은 처리):

- `02_tool_calling.py`: 독스트링의 `실행: python 02_tool_calling.py` 줄, 60행·94–95행의 `05-langgraph/03_tool_node.py 참고` 경로 주석(수강생 글에 `.py` 금지).
- `03_langchain_rag.py`: `PDF_PATH`를 `Path(__file__)…` 대신 `data/…` 상대 경로로, `while True` + `input()`을 질문 변수 한 번 실행으로, `Chroma().delete_collection()` 추가(한 커널에서 다시 실행하면 청크가 쌓여 검색 결과가 중복됨. M1 1-4에서 확인), `langchain-community` 경고 숨김.
- 네 파일 공통: `from config.llm import get_llm`이 노트북 폴더에서 불리도록 준비 셀의 경로 처리는 M1 LAB 공통 셀을 따른다.

## 4. 실행 제약·위험과 처리 제안

| 항목 | 내용 | 노트북 처리 제안 |
|---|---|---|
| 사내 게이트웨이 도구 호출 | 3·4장이 `bind_tools`를 쓴다. 사내 동작 **미확인**(M1 1-3·2-1과 같은 조건) | M1 확인 결과를 따른다. 안 되면 성공 기준·출력 설명으로 진행(강사 메모) |
| 사내 임베딩 | 5장이 `get_embeddings()`로 청크 50개 안팎을 보낸다. 사내 임베딩은 원본 코드 기준으로 대조만 했고 실행하지 않았다 | M1 1-4와 같은 조건. 환경 점검 셀에 `EMBED_PROVIDER`를 넣는다 |
| 사외 준비 | `COURSE_ENV=out`(OpenAI)으로 네 파일 실행 가능할 것으로 본다. 03은 솔루션으로 사외 확인 기록이 있다 | 제작 단계에서 실측 |
| `input()` 반복 | 원본 03은 `while True` + `input()`이라 노트북 셀이 끝나지 않는다 | 질문 변수 한 번 실행으로 patch(M1 1-4 결정과 같음) |
| 데이터 파일 | `course/Chapter02/notebooks/`가 아직 없다. 5장은 `notebooks/data/meritz_pet_insurance.pdf`가 필요하다 | 빌드 때 `code/raw/00-review/data/`의 PDF를 `notebooks/data/`로 복사(M1과 같은 파일) |
| 반복 멈춤 장치 | 4장 researcher ↔ tools 반복에 횟수 제한이 없다 | ⛔에 "실행 중지(■)"를 적는다. 코드는 고치지 않는다 |
| 실행 시간 | 네 장 합계 약 2~4분(추정). CHANGE_HERE로 한 번씩 더 돌려도 LAB 60분 안에 들어간다 | 제작 단계에서 실측해 강사 메모에 적는다 |
| 슬라이드와 코드 모양 차이 | p4 슬라이드 코드는 프롬프트 템플릿 체인, 2장 코드는 메시지 목록 호출 | LEC에서는 슬라이드만, LAB 2장 소개에 "같은 모델을 메시지 목록으로 부른다"고 한 줄 적는다 |
| 알려진 결함(AGENTS.md 7절) | 이 단원 코드에는 해당 없음 | — |
| input()·파일 쓰기·메일 발송·서버 | 03의 `input()` 외에는 없음. 서버를 띄우는 코드 없음 | — |

## 5. 확인이 필요한 질문

1. **개발 환경 구성(VS Code, CodeMate, venv, .env)**: 슬라이드·코드에 없습니다. 3일차에 PC를 다시 셋팅해야 하는지(계정별 초기화 정책) 모릅니다. LAB 1장 환경 점검 셀 + 강사 진행으로 둘까요, 셋팅 장을 따로 둘까요?
2. **"[실습] 코드로 server, client 기초 이해"**: 3-1 슬라이드와 `00-review` 네 파일 어디에도 server/client 코드·설명이 없습니다(인수인계서·피드백에도 언급 없음). 원본에서 server/client 쌍은 `01-mcp`(01_mcp_server/02_mcp_client)와 `02-a2a`(01_a2a_server/02_a2a_client)뿐입니다. (가) 3-2·3-3 실습이 이를 맡는 것으로 보고 3-1에서는 빼기, (나) 3-1에 서버를 터미널에서 띄우고 노트북에서 부르는 흐름을 미리 연습하는 장을 새로 만들기(근거 코드 없음) 중 어느 쪽입니까?
3. `02_tool_calling.py`의 `print(response)`(raw)를 그대로 둘까요, M1 1-3처럼 `print(call)`로 바꿔 짧게 보여 줄까요?
4. LAB 장 순서를 원본 번호(00→01→02→03)로 둘까요, 제안한 00→02→01→03으로 둘까요?
5. 운영 요청 "3일차에 캡스톤 예고"는 3-1 슬라이드에 없습니다. LEC 끝에 짧은 예고 절을 둘까요(근거 자료 필요), 강사 구두로 둘까요?
