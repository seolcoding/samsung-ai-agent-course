# 3-3 교안 노트북 — 목차 (v1, 2026-09-28)

> 2026-10-18: 실습 노트북에서 "AI에게 물어보기" 절을 뺐다(`dev/AGENTS.md`). 아래의 물어보기 항목은 지난 설계 기록이고 빌드에 쓰이지 않는다.

- **권 제목**: A2A 프로토콜의 이해 (PDF 1쪽 제목 "3-3 A2A 프로토콜의 이해")
- **원본 슬라이드**: `course/Chapter02/slides/day01/3-3-a2a-protocol-understanding.pdf` (15쪽. 표지 p1, 목차 p2, 장 표지 p3·p6·p9·p13, 본문 9쪽). 슬라이드 코드(p10·p11·p12·p14·p15)는 이미 a2a-sdk 1.x 코드와 같다.
- **원본 코드**: `course/Chapter02/code/raw/02-a2a/` 2개 (설치된 `a2a-sdk` 1.1.5)
  - `01_a2a_server.py` (TODO 9개, 포트 8001)
  - `02_a2a_client.py` (TODO 3개)
- **커리큘럼**: 3일차 3.3 "A2A 프로토콜 이해와 위임 구조 실습" 1.5H. 이 목차는 **LEC 30분 + LAB 60분**을 가정한다. LAB에 터미널로 서버를 띄우고 다시 띄우는 시간이 들어가므로 LAB을 넉넉히 잡았다.
- **산출물**: `course/Chapter02/notebooks/3-3_a2a_LEC.ipynb`, `course/Chapter02/notebooks/3-3_a2a_LAB.ipynb` (빌더 spec `dev/builders/labs/Chapter02/02-a2a.json`, 아직 없음. `build_lab.py`의 UNITS에는 `"02-a2a": ("3-3", "a2a")`가 이미 있다)
- **서버 방식**: 서버 코드를 노트북 셀에 보여 주고, 빈칸을 채운 뒤 `%%writefile a2a_server.py`(둘째 구획부터 `%%writefile -a`)로 `course/Chapter02/notebooks/`에 쓴다. 새 터미널에서 `uv run python course/Chapter02/notebooks/a2a_server.py`로 띄운다(`build_lab.py`의 TERMINAL_NOTE). 클라이언트는 노트북 셀에서 top-level `await`로 실행한다.
- **실행 검증**: 이 목차 단계에서는 코드를 실행하지 않았다. solution은 사외 OpenAI로 서버 + 클라이언트 실행이 검증됐다(`dev/docs/VALIDATION.md`: Agent Card 조회, 응답 수신). 호출 수·시간은 코드 구조로 추정한 값이다.

## 1. LEC 목차

슬라이드 PDF.js + C 수준 설명(슬라이드 요약, 내용 있는 곳만 "왜 배우나") + 4지선다 퀴즈. 코드 셀 없음.

| # | 절 제목 | 슬라이드 | 핵심 메시지 (근거 쪽) | 왜 배우나 | 퀴즈 |
|---|---|---|---|---|---|
| 1 | 도입 | p1–2 | 네 장: Agent 2 Agent → 핵심 개념 → Server 구현 → Client 구현 (p2) | — | — |
| 2 | A2A 등장 배경 | p3–4 | A2A는 Agent가 다른 Agent에게 작업을 위임하고 결과를 주고받는 통신 프로토콜이다. Agent마다 역할·도구·실행 환경·프레임워크가 달라도 협업해야 하고, 요청하는 쪽은 상대의 내부 구현을 몰라도 된다 (p4) | M1에서 Researcher·Writer를 한 그래프 안에 두었다. 이 권에서는 Researcher를 따로 떨어진 서버로 두고 요청만 보낸다 | 요청하는 Agent가 상대 Agent에 대해 **몰라도 되는** 것은? (내부 구현) |
| 3 | MCP와 A2A의 차이 | p5 | 둘 다 연결 표준이지만 대상이 다르다. MCP는 Agent ↔ Tool·데이터 소스(도구 사용), A2A는 Agent ↔ Agent(작업 위임과 협업). 전문 Agent는 A2A로 일을 받고 안에서 MCP 도구를 쓸 수 있다 (p5) | 바로 앞 권(3-2)에서 MCP를 배웠다. 둘을 섞어 쓰는 구조의 기준이 된다 | A2A의 핵심으로 알맞은 것은? (작업 위임과 협업 / 도구 사용 / 데이터 소스 연결 / 화면 표시) |
| 4 | Agent Card | p6–7 | Agent가 자신이 누구이고 무엇을 할 수 있는지 외부에 설명하는 메타데이터. 이름·설명·제공 기능, 입출력 모드·연결 정보·Skill을 담고, 상대가 협업 가능성을 판단하는 기준이 된다 (p7) | — | Agent Card에 담는 내용이 **아닌** 것은? (내부 LangGraph 코드) |
| 5 | Task, Message, Artifact | p8 | Task = 위임되는 작업 단위, Message = 요청·질문·중간 응답, Artifact = 보고서·코드·파일·구조화 데이터 같은 산출물. 긴 작업은 Task 상태와 Message 이력으로 추적한다 (p8) | 실습 코드는 Message 한 번으로 답을 돌려준다. Task·Artifact는 개념으로만 다룬다(4절) | 보고서·파일 같은 산출물을 가리키는 것은? (Artifact) |
| 6 | AgentExecutor | p9–10 | A2A 요청을 실제 Agent 실행으로 잇는 서버의 핵심 클래스. RequestContext에서 입력과 task/context id를 읽고, 내부 LangGraph Agent를 실행하고, 결과를 EventQueue에 `t.Message`로 발행한다 (p10) | 안쪽은 M1에서 만든 LangGraph Agent 그대로다. A2A는 그 바깥을 감싸는 층이다 | AgentExecutor가 결과를 발행하는 곳은? (EventQueue) |
| 7 | AgentCard 코드 | p11 | 클라이언트가 능력·연결 정보를 발견하도록 `/.well-known/agent-card.json`에서 JSON으로 노출한다. 이름·설명·입출력 모드·지원 인터페이스·skills (p11) | — | Agent Card가 노출되는 주소는? (`/.well-known/agent-card.json`) |
| 8 | RequestHandler | p12 | 라우팅 계층과 실행 계층을 잇는 객체. `agent_executor`에 실행 로직을, `task_store`·`queue_manager`로 작업 상태와 이벤트를 관리한다. Agent Card 조회 라우트와 JSON-RPC 라우트를 앱에 등록한다 (p12) | — | `task_store`와 `queue_manager`가 맡는 일은? (작업 상태와 이벤트 관리) |
| 9 | A2ACardResolver | p13–14 | 원격 Agent의 Card를 읽어 통신을 준비한다. `A2A-Version` 헤더로 1.x 요청임을 밝히고, Card를 먼저 읽어 URL·기능·입출력 모드를 확인한 뒤 JSON-RPC transport와 Client를 만든다 (p14) | — | 클라이언트가 메시지를 보내기 **전에** 먼저 하는 일은? (Agent Card 조회) |
| 10 | SendMessageRequest | p15 | 사용자 요청을 A2A Message로 감싸 보낸다. 입력은 `t.Message`의 `parts`에 텍스트로 담고, `client.send_message(req)`가 응답 스트림을 돌려주면 응답 메시지의 `parts`에서 텍스트를 꺼낸다 (p15) | — | 사용자 입력 텍스트를 담는 곳은? (`t.Message`의 `parts`) |
| 11 | 정리 퀴즈 | — | 네 장의 핵심 | — | 4지선다 3문항: ① 상황 → MCP/A2A 고르기(p5) ② 서버 쪽 세 요소 중 "실제 실행을 잇는" 것(AgentExecutor, p10·p12) ③ 클라이언트 순서: Card 조회 → Client 생성 → 메시지 전송(p14·p15) |

- 퀴즈는 모두 4지선다. 정답은 슬라이드 문구에서만 만든다. 수강생 글에는 쪽 표시를 넣지 않는다.
- 슬라이드 p4·p5의 그림(배달앱·가게 Agent)은 그림 속 글자만 추출된다. 설명 글에서 예로 쓸 때 그림에 있는 이름만 쓴다.
- "왜 배우나"의 M1·3-2 연결은 커리큘럼(2.3, 3.2, 3.3)에 근거한다.

## 2. LAB 목차

첫 구획(접힌 준비 셀) → 보이는 코드 셀. 셀은 위에서부터 차례로 실행한다.

**과제·예제 고르기 기준**: LangGraph Agent 부분(TODO 4개)은 M1(1-3 도구 호출, 2-1 그래프·ToolNode·조건부 엣지)에서 배운 것이라 **과제**. A2A SDK 연결부(protobuf 타입, RequestHandler, 라우트, transport)는 처음 보고 1.x API라 AI도 옛 0.x 방식으로 쓰기 쉽다. 그래서 대부분 **예제**로 두고, 슬라이드에 코드가 그대로 있는 두 곳(p10 `ainvoke`, p15 `SendMessageRequest`)만 **과제**로 낸다. 과제 합계 빈칸 6곳(서버 5, 클라이언트 1), 예제의 TODO 6개는 TODO 주석을 설명 주석으로 바꾼다(`patch`, 3절).

| 장 | 원본 | 구분 | CHANGE_HERE 후보 / WRITE_HERE로 바꿀 TODO | 성공 기준 초안 | 실행 제약 |
|---|---|---|---|---|---|
| 1 | (환경 확인) | — | — | — | 공통 셀 |
| 2.1 | 서버: 불러오기 (1–41행) | 예제 | 없음. `%%writefile a2a_server.py` 첫 셀. 상단 docstring(8–12행, 파일 이름·`curl`)은 patch로 뺀다 | — | 파일만 쓴다 |
| 2.2 | 서버: 내부 LangGraph Agent (43–73행) | **과제** (4곳) | ① 55행 `# TODO: search_web 도구를 LLM과 ToolNode에 연결해 주세요.` → 빈칸 56–57행<br>② 61행 `# TODO: State의 messages를 도구가 연결된 LLM에 전달해 주세요.` → 빈칸 62행<br>③ 69행 `# TODO: tools_condition으로 도구 호출 여부를 분기하고 tools 이후 agent로 돌아오게 연결해 주세요.` → 빈칸 70–71행<br>④ 72행 `# TODO: LangGraph Agent를 컴파일해 주세요.` → 빈칸 73행 | 이 장만으로는 확인할 수 없다. 서버를 띄우고 3장 클라이언트까지 돌려야 보인다(과제 머리에 적는다)<br>🟢 3.4에서 리서치 결과 글이 나온다<br>⛔ 서버를 띄우자마자 터미널에 `NameError`(`tool_node` 등) → 빈칸이 남았다<br>⛔ 요청 때 서버 터미널에 Traceback(`'ellipsis' object has no attribute …`) → 빈칸이 남았다 | 파일만 쓴다 |
| 2.3 | 서버: A2A AgentExecutor (76–109행) | **과제** (1곳) + 예제 | ⑤ 89행 `# TODO: 내부 LangGraph Agent를 비동기로 호출하고 최종 답변을 추출해 주세요.` → 빈칸 90–93행<br>97행 `# TODO: A2A Message를 만들어 EventQueue에 발행해 주세요.` → 예제로 둔다(patch로 설명 주석 `# 결과를 A2A Message로 감싸 EventQueue에 발행한다`) | 🟢 3.4에서 리서치 결과 글이 나온다<br>⛔ 서버 터미널에 `NameError: … 'answer'` → 빈칸이 남았다<br>⛔ `invoke`로 썼다(`await` 없이) → 서버가 멈춘 듯 느려지거나 오류. 비동기 호출(`ainvoke`)로 다시 | 파일만 쓴다 |
| 2.4 | 서버: Agent Card (112–134행) | 예제 | CHANGE_HERE: 119행 `description='주어진 주제를 웹에서 조사하고 요약 정보를 제공합니다.',`(3절 patch 뒤 문구)<br>116행 TODO는 설명 주석으로 바꾼다 | 🟢 3.3의 "설명" 줄이 바꾼 문구로 나온다(서버를 다시 띄운 뒤)<br>⛔ 바꿨는데 예전 문구가 나온다 → 셀을 다시 실행해 파일을 쓰고, 터미널에서 Ctrl+C 뒤 다시 띄웠는지 확인 | 파일만 쓴다. 바꾸면 서버 재시작 필요 |
| 2.5 | 서버: Starlette 앱 조립 (136–160행) + 터미널 실행 안내 + AI에게 물어보기 | 예제 + 물어보기 | 142·149행 TODO는 설명 주석으로 바꾼다<br>물어보기: `ResearcherExecutor`·`request_handler`·`routes`를 붙여 넣고 "요청 한 건이 들어와 응답이 나갈 때까지 어떤 객체를 어떤 순서로 거치는지" 설명받기(고치지 말 것) | 🟢 터미널에 `Researcher A2A 서버 시작: …8001`과 `Uvicorn running on http://0.0.0.0:8001`이 나오고 명령이 끝나지 않는다<br>⛔ `SyntaxError`·`NameError`로 바로 끝난다 → 빈칸 확인 뒤 다시<br>⛔ `address already in use` → 8001을 쓰는 다른 서버(이전에 띄운 이 서버 등)를 끈다<br>🟢 (물어보기) 라우트 → RequestHandler → AgentExecutor → EventQueue 순서를 짚었다 | 서버는 LLM을 부르지 않고 기다린다 |
| 3.1 | 클라이언트: 준비 (1–26행) | — | 접힌 준비 셀. docstring(1–7행)은 patch로 뺀다 | — | — |
| 3.2 | 클라이언트: `call_researcher` (28–63행) | **과제** (1곳) + 예제 | ⑥ 47행 `# TODO: t.SendMessageRequest를 생성해주세요.` → 빈칸 48–54행<br>37·42행 TODO(CardResolver, transport·client 생성)는 예제로 둔다(설명 주석으로 바꿈) | 🟢 셀이 오류 없이 끝난다(함수 정의만 한다)<br>🟢 3.4에서 리서치 결과가 나온다<br>⛔ 3.4에서 `NameError: … 'req'` → 빈칸이 남았다<br>⛔ `message_id`·`role`을 빼서 오류 → 서버 쪽 `t.Message`(2.3)와 비교 | 정의만. 호출은 3.4 |
| 3.3 | 클라이언트: Agent Card 확인 (67–75행) | 예제 | 없음(2.4의 CHANGE_HERE 결과를 여기서 본다) | 🟢 `이름 : Researcher Agent`, 설명, `스킬 : ['웹 리서치']`가 나온다<br>⛔ `ConnectError`(연결 거부) → 서버 터미널이 켜져 있는지 확인 | 서버 필요. LLM 호출 없음 |
| 3.4 | 클라이언트: Researcher에게 위임 (77–81행) | 예제 | CHANGE_HERE: 78행 `topic = 'LangGraph Multi-Agent 시스템의 실제 활용 사례'` | 🟢 `=== Researcher에게 위임: "…" ===` 아래 리서치 결과 글이 나온다<br>🟢 바꾼 주제에 맞는 글이 나온다<br>⛔ `응답을 받지 못했습니다.` 또는 오류 → 서버 터미널의 Traceback을 먼저 본다 | 서버 필요. 서버 쪽 LLM 1~2회, 약 10~30초. httpx timeout 60초 |
| 3.5 | 클라이언트: Writer가 글 작성 (83–92행) + AI에게 물어보기 | 예제 + 물어보기 | CHANGE_HERE 없음<br>물어보기: 3.4·3.5 셀을 붙여 넣고 "어느 줄이 원격 Agent에게 일을 맡기고 어느 줄이 이 노트북에서 직접 LLM을 부르는지" 설명받기 | 🟢 리서치 결과를 바탕으로 한 블로그 글이 나온다<br>🟢 (물어보기) `call_researcher`는 A2A로 위임, `llm.invoke`는 로컬 호출임을 짚었다 | LLM 1회, 약 10~20초. 서버 불필요 |
| 4 | 정리 | — | — | — | 서버 터미널 Ctrl+C로 끄기 안내 |

- 합계: 과제 3구획(빈칸 6곳: 서버 4+1, 클라이언트 1), 예제 CHANGE_HERE 2곳(Card 설명, 위임 주제), 물어보기 2개.
- 클라이언트의 `main()`은 셀별로 풀어 쓴다(3.3·3.4·3.5, 4절 제안). `asyncio.run(main())` 대신 top-level `await`를 쓴다.
- 서버 파일 구획은 원본의 `# ──` 구분선 5개 그대로다(`split`). 첫 셀 `%%writefile a2a_server.py`, 나머지 `%%writefile -a a2a_server.py`.

## 3. 원본·솔루션 차이와 고른 쪽

| 파일 | 차이 | 고른 쪽 | 이유 |
|---|---|---|---|
| `01_a2a_server.py` | ① TODO 주석 9개가 raw에만 있다<br>② 솔루션 맨 위에 이전 강사 메모 주석(AgentExecutor·RequestContext, 들여쓰기 어긋남)<br>③ Card `description`: raw `'주제를 토대로 웹에서 정보를 조사하고 요약해서 제공합니다.'` / 솔루션 `'주어진 주제를 웹에서 조사하고 요약 정보를 제공합니다.'`<br>④ skill `examples` 둘째: raw `'랭그래프 최신 기능 알려줘.'` / 솔루션 `'LangGraph 최신 기능 알려줘'`<br>⑤ 인자 순서·끝 쉼표만 다른 곳(Message `message_id`, Card 입출력 모드, handler `agent_card`) | **raw** + patch ③④를 솔루션 문구로 | 과제에 TODO가 필요하다. ③은 솔루션이 슬라이드 p7·p11 문구와 같다. ④는 영문 표기가 앞 권과 맞다. ②는 읽기 어려워 넣지 않는다. ⑤는 포매터가 정리한다 |
| `02_a2a_client.py` | ① TODO 3개가 raw에만 있다<br>② `RESEARCHER_URL`: raw `'http://localhost:8001'` / 솔루션 `'http://127.0.0.1:8001'`<br>③ 빈 줄·끝 쉼표 | **raw** + patch ②를 솔루션 값으로 | 서버는 `0.0.0.0`(IPv4)에 뜬다. `localhost`가 IPv6(`::1`)로 먼저 풀리는 PC에서 연결이 늦거나 실패할 수 있다(미검증, Windows 강의장 PC 가능성). 솔루션 값이 VALIDATION에서 실행된 값이다 |

추가 patch(가독성, 노트북에서만):
- 두 파일 docstring의 `python 01_a2a_server.py`·`curl` 안내: 수강생은 `.py`를 보지 않으므로 뺀다(실행 안내는 TERMINAL_NOTE가 맡는다).
- 예제로 남기는 TODO 6개(서버 97·116·142·149행, 클라이언트 37·42행): `# TODO:` → 같은 내용의 설명 주석. QC가 보이는 코드의 `TODO`를 FAIL로 본다.
- 서버 80–82행 protobuf·gRPC 설명 주석: 비개발자에게 어려운 용어다. "1.x는 `a2a.types`의 타입으로 메시지를 만든다" 한 줄로 줄이는 안(5절 질문 3).

## 4. 실행 제약·위험과 처리 제안

| 항목 | 내용 | 노트북 처리 제안 |
|---|---|---|
| 도구 호출이 보이지 않음 | 서버는 HTTP 로그만 찍고 `search_web` 호출 여부를 보여 주지 않는다. 시스템 프롬프트가 없어 LLM이 검색 없이 답할 수도 있다. 2.2 빈칸 ③(조건부 엣지)을 잘못 채워도 답은 그럴듯하게 나와 **조용히 틀린다** | `search_web` 안에 `print(f'[search_web] {query}')` 한 줄을 patch로 넣어 서버 터미널에서 도구 호출을 보게 하는 안(5절 질문 1). 넣으면 🟢에 "서버 터미널에 `[search_web]` 줄"을 더한다 |
| 서버 쪽 오류가 클라이언트에 어떻게 보이는지 | 빈칸이 남은 채 요청하면 서버 안에서 예외가 난다. 클라이언트가 JSON-RPC 오류로 받는지, 기다리다 timeout인지 **미확인** | 제작 단계에서 빈칸 상태로 한 번 돌려 보고 ⛔ 문구를 실제 메시지로 맞춘다. 공통 안내: "클라이언트에서 오류가 나면 서버 터미널부터 본다" |
| 서버 재시작 | 서버 파일을 고치면(빈칸, CHANGE_HERE) 셀 다시 실행 → Ctrl+C → 다시 띄우기가 필요하다. 빠뜨리면 예전 코드로 돈다 | TERMINAL_NOTE 4번에 이미 있다. 2.4 ⛔에 한 번 더 적는다 |
| 포트 8001 | 캡스톤 `mcp_server.py`도 8001을 쓴다(VALIDATION). 3-2 MCP 서버는 8000이라 겹치지 않는다 | 4장 정리에 "서버 터미널 Ctrl+C로 끄기"를 둔다. 캡스톤 쪽 포트 변경은 4-3 목차에서 다룬다 |
| a2a-sdk 1.x | 설치 1.1.5, `pyproject.toml`에 `>=1.1.5,<2`. AI가 0.x 예시(`A2AStarletteApplication`, `TextPart` 등)로 답하기 쉽다 | SDK 연결부는 예제로 둔다(2절 기준). 과제 ⑤⑥ 힌트에 "코드 옆 주석과 같은 타입을 쓰게 하라"는 방향만 준다 |
| 사내 게이트웨이 도구 호출 | 서버의 `bind_tools`는 사내 게이트웨이 미검증 | 1-3·2-1 확인 결과를 따른다. 강의장 사전 확인 목록 |
| 사내 게이트웨이 응답 시간 | 클라이언트 httpx timeout 60초. 서버 쪽 LLM이 두 번(agent → tools → agent) 돌면 사내에서 60초를 넘길 수 있는지 **미확인** | 강의장 사전 확인. 넘으면 `timeout=60.0`을 CHANGE_HERE가 아닌 patch로 늘린다 |
| 서버 파일 위치 | `%%writefile`로 `course/Chapter02/notebooks/a2a_server.py`가 생긴다. `config` 패키지는 editable 설치(`course/`)라 이 위치에서도 import된다. `.env`는 `load_dotenv()`가 위 폴더로 올라가며 찾는다 | 생성 파일을 `.gitignore`·전달 브랜치에서 뺄지 3-2와 같이 정한다 |
| Task·Artifact 실습 없음 | 커리큘럼 3.3의 "task 생성/조회/완료 처리"는 코드에 없다. 서버는 Task를 만들지 않고 Message 하나로 답한다 | LEC 5절에서 개념만 다룬다. 코드는 더하지 않는다(YAGNI, 받은 내용 유지) |
| 실행 시간 | 한 번에 LLM 2~3회, 약 30초~1분 추정. CHANGE_HERE로 한두 번 더 돌려도 LAB 60분 안에 든다. 서버 재시작·빈칸 채우기 시간이 더 크다 | 제작 단계에서 실측해 강사 메모에 적는다 |
| input()·파일 쓰기·메일 발송 | 없음(`%%writefile` 제외) | — |

## 5. 커리큘럼 대조 (`dev/docs/CURRICULUM.md` 3.3)

| 커리큘럼 항목 | 위치 |
|---|---|
| MCP와 A2A의 역할 구분 | LEC 3 |
| Agent Card / Task / Message / Artifact | LEC 4·5·7 / LAB 2.4·3.3 |
| Task 상태 추적 기반 비동기 위임 모델 | LEC 5(개념만, 코드 없음) |
| [실습] LangGraph Agent를 A2A Server로 노출 | LAB 2 (과제 5곳 + 예제) |
| [실습] A2A Client로 task 생성/조회/완료 처리 | LAB 3 (메시지 전송·응답 수신만. 조회·완료 처리 코드는 원본에 없다) |
| [실습] Researcher(A2A) + Writer(로컬 LLM) 분업 흐름 | LAB 3.4·3.5 |

## 6. 확인이 필요한 질문

1. 서버 `search_web`에 호출 표시 `print` 한 줄을 넣어(노트북 patch) 도구 호출을 터미널에서 보이게 할까요? 넣지 않으면 조건부 엣지 빈칸을 잘못 채워도 결과가 그럴듯해 조용히 틀릴 수 있습니다.
2. 클라이언트 `main()`을 3개 셀(Card 확인 / 위임 / Writer)로 풀어 쓸까요, `await main()` 한 셀로 둘까요? 이 목차는 풀어 쓰는 쪽을 가정했습니다.
3. 서버의 protobuf·gRPC 설명 주석(80–82행)을 한 줄로 줄일까요, 원문대로 둘까요?
