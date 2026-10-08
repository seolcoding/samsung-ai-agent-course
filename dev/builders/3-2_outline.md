# 3-2 교안 노트북 — 목차 (v1, 2026-09-28)

- **권 제목**: MCP - Model Context Protocol (PDF 제목 "3-2 MCP - Model Context Protocol")
- **원본 슬라이드**: `course/Chapter02/slides/day01/3-2-model-context-protocol.pdf` (12쪽. 표지 p1, 목차 p2, 장 표지 p3·p7·p10, 본문 7쪽)
- **원본 코드**: `course/Chapter02/code/raw/01-mcp/` 2개
  - `01_mcp_server.py` 서버 (TODO 2개: 21행 데코레이터 안내, 91행 "MCP 서버 모드 정의". 둘 다 아래에 채울 빈칸이 없는 설명성 TODO)
  - `02_mcp_client.py` 클라이언트 (TODO 7개: 31·59·62·72·83·90·96행)
- **커리큘럼**: 3일차 3.2 "MCP" 1.5H. 이 목차는 **LEC 25분 + LAB 65분**을 가정한다(LAB에 서버 켜기·터미널 오가기 시간이 더 든다).
- **산출물**: `course/Chapter02/notebooks/3-2_mcp_LEC.ipynb`, `course/Chapter02/notebooks/3-2_mcp_LAB.ipynb` (spec `dev/builders/labs/Chapter02/01-mcp.json`, 아직 없음)
- **서버 파일**: LAB 셀이 `%%writefile`로 `course/Chapter02/notebooks/mcp_server.py`를 쓴다. 포트 **8000**, 주소 `http://localhost:8000/sse`
- **실행 검증**: 이 목차 단계에서는 코드를 실행하지 않았다. 동작 설명은 코드와 설치된 라이브러리(fastmcp 3.4.7, langchain-mcp-adapters 0.3.2) 소스를 읽고 추정한 것이다. solution 쪽 SSE 서버+클라이언트는 사외 OpenAI로 실행 검증된 기록이 있다(`dev/docs/VALIDATION.md`: 도구 5개 발견, 시간·BMI·할 일 도구 호출).

## 1. LEC 목차

슬라이드 PDF.js + C 수준 설명(슬라이드 요약, 내용 있는 곳만 "왜 배우나") + 4지선다 퀴즈. 코드 셀 없음.

| # | 절 제목 | 슬라이드 | 핵심 메시지 (근거 쪽) | 왜 배우나 | 퀴즈 |
|---|---|---|---|---|---|
| 1 | 도입 | p1–2 | 세 장: MCP(문제점·등장·구성요소) → Server 구현(FastMCP, 3대 Primitive) → Client 구현(LangChain 연결, get_tools) (p2) | — | — |
| 2 | 함수 호출의 문제점 | p3–4 | Function Calling은 도구 연결 방식이 앱마다 흩어진다. 이름·설명·스키마를 앱 코드에서 직접 관리하고, 도구가 늘수록 연결·권한 코드가 늘고, 다른 Agent·앱에서 재사용하기 어렵고, 시스템마다 연결 방식이 달라 유지보수가 복잡하다 (p4) | 1일차 Tool Calling·LangGraph에서 도구를 Agent 코드 안에 직접 정의했다. 그 방식이 어디서 막히는지 짚는다 | Function Calling 방식의 문제로 슬라이드가 든 것이 **아닌** 것은? (보기 셋은 p4 네 항목 중 셋, 오답 하나는 "LLM이 도구를 호출할 수 없다") |
| 3 | MCP의 등장 | p5 | MCP = LLM 앱과 외부 도구·데이터를 표준 방식으로 잇는 프로토콜. Agent가 도구를 품는 대신 MCP Server가 제공하고, Host가 필요한 Server에 연결하며, 도구 구현과 Agent 실행 로직을 분리할 수 있다 (p5) | p4의 문제(재사용 어려움)를 "도구는 서버에, Agent는 연결만"으로 푼다 | MCP에서 도구와 데이터를 **제공하는** 쪽은? (Server / Host / Client / LLM) |
| 4 | 구성요소 (Server, Host, Client) | p6 | Server = 도구·데이터·프롬프트를 MCP 형태로 제공, Host = 사용자가 실제로 쓰는 LLM 앱, Client = Host 안에서 Server와 통신하는 연결 계층. 그림에서 `client.py`가 Host 자리에 있다 (p6) | 실습 구조와 같다: 터미널에 띄우는 서버가 Server, 노트북의 Agent가 Host, 그 안의 연결 객체가 Client | "Host 안에서 MCP Server와 통신하는 연결 계층"은? |
| 5 | FastMCP | p7–8 | FastMCP로 MCP Server를 빠르게 만든다. 데코레이터로 Tool·Resource·Prompt를 정의하고, HTTP/SSE 모드와 stdio 모드로 실행할 수 있다. Claude Code 같은 Host와는 stdio로 연결한다. 코드 예: `mcp.run(transport="sse", host="0.0.0.0", port=8000)` (p8) | 전송 방식 두 가지를 여기서 구분한다(설명 문장): SSE는 서버를 먼저 따로 켜 두고 주소로 접속, stdio는 Host가 서버 프로그램을 직접 실행해 입출력으로 주고받는다. 실습은 SSE로 하고 stdio는 한 줄 바꿔 비교한다 | FastMCP로 만든 서버를 실행하는 방식 두 가지로 알맞은 것은? (HTTP/SSE·stdio / REST·gRPC / …) |
| 6 | Resources, Tools, Prompts | p9 | 3대 Primitive: Tools = LLM이 행동하려고 호출하는 함수, Resources = LLM·Host가 읽는 데이터·맥락(등록된 서버 정보를 얻기 위함), Prompts = 반복해서 쓰는 프롬프트 템플릿(단축 명령어로 제공하기도) (p9) | 실습 서버에 셋이 모두 있다. 클라이언트가 `get_tools`로 가져오는 것은 Tools뿐이라는 점과 이어진다 | 반복해서 쓸 수 있는 프롬프트 템플릿에 해당하는 Primitive는? |
| 7 | LangChain으로 연결 | p10–11 | `langchain_mcp_adapters`의 `MultiServerMCPClient`로 연결한다. 설정에 서버 이름·transport·url을 쓰고, 한 Client로 여러 Server를 동시에 다루며, 가져온 도구는 LangChain/LangGraph Tool처럼 쓴다 (p11) | — | MCP 설정(MCP_CONFIG)에 쓰는 항목이 **아닌** 것은? (서버 이름 / transport / url / 모델 이름) |
| 8 | get_tools | p12 | `get_tools`는 Server에 접속해 Tool 이름·설명을 읽고, LLM이 이해하는 스키마로 바꾸고, `bind_tools`에 넘겨 Tool Calling 대상으로 쓰게 한다. 이후 다른 LangChain Tool처럼 쓴다 (p12) | 1일차에 배운 `bind_tools`·ToolNode를 그대로 쓴다. 새로 배우는 것은 "도구를 어디서 가져오느냐"뿐이다 | `get_tools`로 가져온 도구를 LLM에 넘길 때 쓰는 메서드는? |
| 9 | 정리 퀴즈 | — | 세 장의 핵심 | — | 4지선다 3문항: ① 상황 → 구성요소 짝짓기(Server/Host/Client) ② 설명 → Primitive 짝짓기 ③ Claude Code 같은 Host와 연결할 때 쓰는 방식(stdio) |

- 퀴즈는 모두 4지선다. 정답은 슬라이드 문구에서만 만든다. 5절 "왜 배우나"의 SSE/stdio 설명은 커리큘럼 3.2 "SSE/stdio 전송 방식 이해"에 근거한 설명 문장이며 퀴즈 정답으로 쓰지 않는다.
- 11차수 피드백에 "mcp가 무엇인지", "어려운 용어" 요청이 있다. 2–4절 설명은 용어(프로토콜, Host, 전송 방식)를 한 문장씩 풀어 쓴다.

## 2. LAB 목차

첫 구획(접힌 준비 셀) → 보이는 코드 셀. 서버는 셀로 파일을 쓰고 터미널에서 띄운다. 클라이언트는 노트북 셀에서 top-level `await`로 실행한다.

| 장 | 원본 | 구분 | CHANGE_HERE 후보 / WRITE_HERE로 바꿀 TODO | 성공 기준 초안 | 실행 제약 |
|---|---|---|---|---|---|
| 1 | (환경 확인) | — | — | — | 공통 셀 |
| 2 | `01_mcp_server.py` → `mcp_server.py` | **예제** + AI에게 물어보기 | 서버 코드를 구획 5개로 나눠 `%%writefile mcp_server.py`(첫 구획), `%%writefile -a mcp_server.py`(나머지)로 쓴다: ① 불러오기·`mcp = FastMCP('AI 강의 튜토리얼 서버')` ② Tool 5개 ③ Resource ④ Prompt ⑤ 실행(SSE 기본, `--stdio`면 stdio).<br>CHANGE_HERE: 28행 `"""현재 날짜와 시간을 반환한다."""` (도구 설명. 예: "현재 날짜와 시간을 한국 시간으로 알려 준다"로 바꾼 뒤 서버를 껐다 켜고 3장 도구 목록 셀을 다시 실행하면 설명이 바뀐다. p12 "Tool 이름과 설명을 읽어옴"을 눈으로 확인)<br>터미널 명령: `uv run python course/Chapter02/notebooks/mcp_server.py`<br>물어보기: 서버 코드 전체를 붙여 넣고 "Tool·Resource·Prompt 데코레이터가 각각 무엇을 등록하는지, 클라이언트가 도구를 가져오면 몇 개가 보일지"를 설명받기(고치지 말 것) | 🟢 터미널에 `MCP 서버 시작: http://localhost:8000/sse`, `종료하려면 Ctrl+C` 두 줄이 나오고 명령이 끝나지 않고 기다린다(그 아래 FastMCP 배너가 이어진다. 배너 모양은 제작 때 실측해 적는다)<br>🟢 (물어보기) 도구는 5개(`get_current_time`, `calculate_bmi`, `add_task`, `list_tasks`, `complete_task`)이고 Resource·Prompt는 도구 목록에 들어가지 않는다는 점을 짚었다<br>⛔ 명령이 곧바로 끝나고 오류가 나온다 → 오류 끝줄을 AI에게 보여 준다. `address already in use`면 이미 켜 둔 서버가 있는 것이다(그 터미널에서 Ctrl+C) | LLM 호출 없음. 포트 8000을 연다. 서버 터미널은 3·4장 동안 켜 둔다 |
| 3 | `02_mcp_client.py` | **예제 + 과제** (빈칸 6곳) | 클라이언트를 `main()` 밖으로 풀어 구획마다 셀로 나눈다(3절·4절 참고).<br>**3.1 연결 설정 (예제)** 31행 TODO(연결 방식 정의)는 빈칸 대신 설명으로 쓰고, SSE·stdio 설정을 둘 다 적어 둔 뒤 한 줄로 고른다:<br>`# ✍️ CHANGE_HERE: 'sse'를 'stdio'로 바꾸면 서버를 노트북이 직접 실행합니다`<br>`TRANSPORT = 'sse'` (기본값은 SSE. stdio 비교는 4장)<br>**3.2 연결하고 도구 가져오기 (과제)**<br>① 59행 `# TODO: MCP 설정으로 MultiServerMCPClient를 생성해 주세요.` → 빈칸 60행<br>② 62행 `# TODO: MCP 서버에서 도구 목록을 가져와 주세요.` → 빈칸 65행 (`await` 포함)<br>**3.3 Agent 그래프 (과제, 1일차 복습)**<br>③ 72행 `# TODO: 가져온 MCP 도구를 LLM과 ToolNode에 연결해 주세요.` → 빈칸 74·76행<br>④ 83행 `# TODO: State의 messages를 도구가 연결된 LLM에 전달해 주세요.` → 빈칸 84행<br>⑤ 90행 `# TODO: tools_condition으로 도구 호출 여부를 분기하고 tools 이후 agent로 돌아오게 연결해 주세요.` → 빈칸 93–94행<br>⑥ 96행 `# TODO: 그래프를 컴파일해 주세요.` → 빈칸 97행<br>**3.4 질문하기 (예제)** CHANGE_HERE: 101행 `'지금 몇 시야?',` (예: "MCP가 뭐야?"처럼 도구가 필요 없는 질문으로 바꿔 도구를 거치지 않고 끝나는지 본다) | 🟢 (3.2) `=== 사용 가능한 MCP 도구 ===` 아래 5줄(`- get_current_time: 현재 날짜와 시간을 반환한다.` 등)이 나온다<br>⛔ (3.2) 연결 오류(`ConnectError`, `Connection refused` 등) → 2장 서버 터미널이 켜져 있는지 본다<br>🟢 (3.4) Q1 답에 지금 시각, Q2 답에 BMI 22.9·정상, Q3 답에 "LangGraph 공부"(우선순위 3)가 든 목록이 나온다<br>🟢 (3.4 바꾼 뒤) 도구 없이 바로 답한다<br>⛔ (3.4) 답에 시각·BMI 숫자가 없고 "알 수 없다"는 식이다 → ③(`bind_tools`)과 ⑤(조건부 엣지)를 다시 본다<br>(참고) 서버를 켠 채로 다시 실행하면 할 일이 계속 쌓인다. 서버가 켜져 있는 동안 목록을 기억하기 때문이며 정상이다 | LLM 약 6~7회(질문 3개 × 도구 호출 1회 + 답 1회, Q3는 도구 2개), 약 30초~1분 추정. 과제 빈칸 ③~⑥을 모두 채워야 3.4가 돈다는 점을 3.3 머리에 적는다 |
| 4 | (3장 셀 재사용) | **예제** — stdio로 바꿔 보기 | 3.1의 `TRANSPORT = 'sse'`를 `'stdio'`로 바꾸고 3.1~3.4를 다시 실행한다. stdio 설정은 노트북이 `mcp_server.py --stdio`를 직접 실행한다(서버 터미널은 켜 둬도 꺼도 된다) | 🟢 서버 터미널을 꺼도 도구 5개가 똑같이 나온다<br>🟢 Q1·Q2 답은 SSE 때와 같다<br>🟢 Q3에서 추가한 할 일이 목록에 안 보이거나 목록이 비어 있다고 답할 수 있다: stdio는 도구를 부를 때마다 서버를 새로 띄워서 기억이 이어지지 않는다(코드 읽기로 추정, 제작 때 실측해 확정)<br>⛔ `FileNotFoundError`·`NotImplementedError` → 강사에게 알린다(4절 위험 참고) | LLM 약 6~7회. 도구 호출마다 서버 프로세스를 새로 띄워 조금 느리다 |
| 5 | 정리 | — | — | — | 서버 터미널 Ctrl+C로 끄기 안내 |

- 예제/과제 기준:
  - 서버는 **예제**. 원본 TODO 2개 아래에 채울 줄이 없고(설명성), 서버가 켜져야 나머지가 모두 돈다. 코딩이 낯선 수강생에게 터미널 서버 디버깅까지 과제로 주면 LAB이 서버에서 멈출 위험이 크다(5절 질문 1).
  - 클라이언트 ①② (`MultiServerMCPClient`, `get_tools`)는 LEC 7–8절 슬라이드 코드와 같으므로 **과제**. ③~⑥은 1일차 LangGraph(ToolNode·조건부 엣지·컴파일)와 Tool Calling(`bind_tools`) 복습이라 **과제**.
  - 31행 TODO(연결 방식 두 가지)는 알려진 결함 부분이라 빈칸으로 내지 않고 **예제 CHANGE_HERE 한 줄**로 바꾼다(아래 결함 처리).
- **SSE/stdio 결함 처리 제안**: raw 클라이언트는 stdio가 켜져 있고 SSE가 주석 처리되어 있어, 슬라이드(p8·p11)의 SSE 설정이 실행되지 않는다. 노트북에서는 다음처럼 바꾼다(spec `patch`, 원본 파일은 그대로).
  ```python
  # SSE: 터미널에 켜 둔 서버에 주소로 접속한다
  # stdio: 노트북이 서버 파일을 직접 실행해 입출력으로 주고받는다
  CONNECTIONS = {
      'sse': {'transport': 'sse', 'url': 'http://localhost:8000/sse'},
      'stdio': {'transport': 'stdio', 'command': sys.executable, 'args': ['mcp_server.py', '--stdio']},
  }
  # ✍️ CHANGE_HERE: 'sse'를 'stdio'로 바꾸면 서버를 노트북이 직접 실행합니다
  TRANSPORT = 'sse'
  MCP_CONFIG = {'tutorial': CONNECTIONS[TRANSPORT]}
  ```
  - 기본 실행은 SSE 하나로 슬라이드 p11과 같은 화면을 만든다. stdio는 4장에서 한 줄만 바꿔 비교한다.
  - stdio의 `command`는 원본 `"python"` 대신 `sys.executable`(노트북 커널의 파이썬)을, 경로는 원본의 저장소 기준 경로 대신 노트북 폴더 기준 `mcp_server.py`를 쓴다. 원본 그대로면 노트북에서 경로가 맞지 않아 실패한다.
- 합계: LAB 본문 3장(서버 예제 1장 + 물어보기, 클라이언트 1장 = CHANGE_HERE 2곳 + 빈칸 6곳, stdio 비교 예제 1장).

## 3. 원본·솔루션 차이와 고른 쪽

| 파일 | 차이 | 고른 쪽 | 이유 |
|---|---|---|---|
| `01_mcp_server.py` | 실행 코드는 같다. raw에는 TODO 2줄(21·91행), solution에는 TODO 대신 이전 강사 메모 주석(슬랙 MCP 예, "python 외 언어로도 서버를 만들 수 있다" 등 약 20줄)이 있다 | **raw** (TODO 두 줄은 지우고, 머리 docstring 정리) | 메모 주석 없이 짧다. 두 TODO는 아래에 채울 줄이 없어 보이는 코드에 남기면 QC FAIL이다. docstring 5·7–12행과 99행 주석은 `01_mcp_server.py`·`02_mcp_client.py`·Claude Code 등록 명령을 가리키므로 "터미널에서 띄운다(기본 SSE, 포트 8000), `--stdio`면 stdio"로 줄인다 |
| `02_mcp_client.py` 연결 설정 | raw: stdio 활성, SSE 주석. solution: SSE 활성, stdio 주석. solution에 "상용 Host는 이 설정만 등록하면 된다" 메모 | **둘 다 쓰지 않고 2절의 CONNECTIONS + TRANSPORT 한 줄** | 슬라이드와 같은 SSE를 기본으로 하고, stdio도 지우지 않고 한 줄로 비교하게 한다 |
| `02_mcp_client.py` 나머지 | raw에만 TODO 7개와 TODO 보조 주석(63–64·73·75·91–92행), 쓰지 않는 주석 66행 `# local_tools = [ ] + [tools]`, 78–81행 노드 설명 메모. solution은 TODO 대신 다른 메모 주석이 있고, 마지막 출력이 `print(result)`(상태 전체를 찍어 길다) | **raw** | 빈칸 과제에 TODO가 필요하다. 출력이 `A: …` 한 줄이라 읽기 쉽다. 보조 주석은 WRITE_HERE 설명(`explain`)으로 옮기고, 66·78–81행은 지운다 |
| `02_mcp_client.py` 구조 | 둘 다 `async def main()` 안에 전부 있고 `asyncio.run(main())`로 실행 | **노트북용으로 풀어 쓴다**(patch) | 노트북은 이미 이벤트 루프가 돌아 `asyncio.run`이 오류를 낸다. `main()`을 풀어 top-level `await`로 쓰면 구획(연결 설정 / 도구 가져오기 / 그래프 / 질문)마다 셀이 나뉘어 빈칸 6곳이 한 셀에 몰리지 않는다. `load_dotenv()`는 준비 셀로 옮긴다 |

## 4. 실행 제약·위험과 처리 제안

| 항목 | 내용 | 노트북 처리 제안 |
|---|---|---|
| SSE/stdio 설정 불일치 (알려진 결함) | raw는 stdio가 켜져 있어 슬라이드의 SSE가 한 번도 실행되지 않는다. raw의 stdio 경로도 저장소 기준이라 노트북 폴더에서는 틀린다 | 2절의 CONNECTIONS + `TRANSPORT = 'sse'` 한 줄로 바꾼다. 원본 파일은 고치지 않는다 |
| stdio에서 할 일 목록이 이어지지 않음 | langchain-mcp-adapters 0.3.2는 세션 없이 가져온 도구를 부를 때마다 새 세션을 연다(`tools.py` 460–466행). stdio에서는 호출마다 서버 프로세스가 새로 떠서 `_tasks`가 비어 있을 것으로 본다. SSE는 서버 한 개가 계속 떠 있어 목록이 남는다 | 조용히 틀리는 것처럼 보이지 않도록 4장 성공 기준에 미리 적어 두고 두 방식의 차이로 설명한다. 제작 때 실측해 문구를 확정한다 |
| Windows 노트북에서 stdio | 노트북 커널의 이벤트 루프 종류에 따라 하위 프로세스 실행(`NotImplementedError`)이 막힐 수 있다. **미확인** | 강의장 사전 확인 목록에 올린다. 안 되면 4장은 강사 화면 시연으로 바꾼다(강사 메모) |
| 서버 주소 `0.0.0.0` | 슬라이드 p8과 같게 둔다. Windows에서 방화벽 허용 창이 뜰 수 있다(미확인). localhost 접속에는 영향이 없을 것으로 본다 | 강사 메모에 "창이 뜨면 취소해도 된다(확인 후)"를 적는다. 코드는 슬라이드와 같게 둔다 |
| 포트 | MCP 8000, 3-3 A2A는 8001. 겹치지 않는다. 같은 서버를 두 번 띄우면 8000 충돌 | 2장 ⛔에 `address already in use` 안내 |
| 서버 수정 반영 | 서버 파일을 고쳐도 켜진 서버에는 반영되지 않는다 | 빌더 공통 안내(TERMINAL_NOTE 4번: Ctrl+C → 셀 재실행 → 다시 띄우기)를 그대로 쓴다. CHANGE_HERE(도구 설명) 안내에도 한 줄 적는다 |
| 터미널 안내와 QC | 빌더 공통 안내 `uv run python course/Chapter02/notebooks/mcp_server.py`는 마크다운에 `course/`·`.py`가 들어가 QC 규칙(수강생 글 FILE_REF) FAIL에 걸린다 | 5절 질문 3 (3-3 A2A도 같은 문제) |
| 서버 배너 | fastmcp 3.4.7은 시작할 때 배너(로고, 버전, 서버 이름)를 출력한다(라이브러리 코드 확인). Windows 콘솔에서 글자가 깨지는지 **미확인** | 제작 때 실측해 2장 성공 기준에 실제 화면 문구를 적는다 |
| 사내 게이트웨이 도구 호출 | 클라이언트는 `bind_tools`를 쓴다. 사내 게이트웨이 지원 **미검증** | 1일차 Tool Calling 확인 결과를 따른다. 강의장 사전 확인 목록 |
| 외부 서비스·파일 쓰기 | 외부 API 없음(시간·BMI·할 일 모두 로컬). 파일 쓰기는 `%%writefile`로 노트북 폴더에 `mcp_server.py` 하나 | — |
| 실행 시간 | LLM 호출 3장 약 6~7회, 4장 약 6~7회. 1분 안팎씩(추정) | LAB 65분 안에 들어간다고 본다. 제작 단계에서 실측 |

## 5. 확인이 필요한 질문

1. 서버를 **예제**로 두었습니다(원본 TODO 아래 채울 줄이 없음). 커리큘럼의 "MCP 서버 구현"을 살려 실행 구획(91–100행 `if __name__` 블록)을 과제 빈칸으로 낼까요?
2. 4장(stdio로 바꿔 보기)을 모두 함께 하는 장으로 둘까요, 조기 완료자용 선택 장으로 둘까요?
3. 빌더 공통 터미널 안내의 명령 줄(`course/…/mcp_server.py`)이 QC 수강생 글 규칙에 걸립니다. QC에서 터미널 명령 코드 블록을 예외로 둘까요, 안내를 "이 폴더의 서버 파일" 식으로 바꿀까요?
