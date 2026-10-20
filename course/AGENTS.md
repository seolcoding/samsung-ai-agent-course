# AGENTS.md — 수강생 자료 (AI 코딩 도우미용)

"AI Agent 개발" 과정의 수강생 자료다. 수강생은 코딩이 낯선 사람이 많다. 쉬운 말로 짧게, 결과부터 말한다.

## 폴더

- `course/ChapterNN/notebooks/` 수업 노트북(`_LEC` 강의, `_LAB` 실습)과 `data/`. `course/ChapterNN/tasks/` 실습별 과제 `<번호>_task.py`.
- `code/` 받은 원본 코드(참고용), `slides/` 슬라이드 PDF, `assets/` 노트북 화면 도구, `course/config/` 모델·임베딩·RAG 설정.
- `course/Chapter02/capstone/` 4일차 캡스톤 폴더. 수강생이 AI와 직접 고친다(안내는 그 폴더의 README.md).

## 실습 노트북

- 1·2일차는 값 바꾸기판이다. `# ✍️ CHANGE_HERE:` 위의 "바꿔 볼 값"을 바로 아래 줄의 그 자리에 붙여 넣고 다시 실행한 뒤 되돌린다.
- 결과는 접힌 "무슨 일이 생기나"에 있다. 먼저 실행해 보게 한 뒤 무엇이 왜 달라졌는지 설명한다.
- 3·4일차는 객관식판이다. `# ✅ CHOOSE_HERE:` 아래 같은 번호(1️⃣~4️⃣) 줄을 모두 골라 `Ctrl + /`로 푼다. `pass  # 그대로 둡니다`는 둔다.
- 정답을 바로 말하지 말고 보기마다 무엇이 다른지 설명해 고르게 돕는다. 결과는 🟢/⛔ 기준과 비교하고, 해설은 접힌 "정답 보기"에 있다.
- 디버그 출력(`set_debug(True)`)이 길어도 정상이다. 도구 호출 때 섞이는 `KeyError('input')` 줄은 결과와 상관없다.
- 표시된 자리 밖은 고치지 않는다. 셀은 위에서부터 실행된 것으로 보고, 부탁받지 않은 기능·예외 처리를 더하지 않는다.
- Streamlit 앱을 띄우는 셀은 끝나지 않으니 ■로 멈추고 다음 셀로 간다. `input()` 셀에는 답을 입력하게 한다.

## 과제 (`course/ChapterNN/tasks/<번호>_task.py`)

- 파일의 `# ✍️ N.` 자리 2곳, 그 아래 `# ✨` 힌트, 맨 아래 확인 코드를 읽고, 확인 코드의 기준에 맞게 `✍️` 자리만 구현한다.
- 실행은 저장소 맨 위에서 파일 맨 위의 ▶️ 명령으로 한다. 챗봇 앱(1-2·1-3·1-4·2-1·2-3)은 브라우저가 열리고, 끝낼 때는 터미널에서 `Ctrl + C`.
- 구현 뒤 실행해 ✅ 확인(🟢/⛔/❔)을 함께 본다(챗봇은 사이드바 "✅ 과제 확인"). ⛔면 그 자리만 고치고, 실행 못 했으면 통과라고 하지 않는다.
- 고치는 파일은 과제 파일 하나다(4-1은 `4-1_skills/meeting-summary/SKILL.md`도). 화면·확인 코드·설정 줄은 고치지 않는다.
- 설명 → 작은 힌트 → 필요한 만큼 코드 순서로 돕는다. 통째로 써 달라고 하면 써 주고 흐름을 짧게 설명한다.

## 서버 실습 (3-2 MCP, 3-3 A2A, 캡스톤)

- 노트북 폴더의 서버 파일은 모두 완성된 서버다. 3-2는 `basic_mcp_server.py`(기본)·`dart_mcp_server.py`(실전), 3-3은 `a2a_server.py`(기본)·`friends_a2a_server.py`(실전). VS Code 새 터미널에서 `uv run python course/Chapter02/notebooks/basic_mcp_server.py`처럼 띄운다.
- 서버를 켜 둔 채 노트북의 클라이언트 셀을 실행한다. 서버를 고쳤으면 저장 → `Ctrl + C` → 다시 띄우고 연결 셀부터 다시 실행한다.
- 포트는 기본 MCP 8000, DART MCP 8002, 기본 A2A 8001, 친구 A2A 8003, 캡스톤 MCP 8001. "address already in use"·`[Errno 10048]`이면 앞 서버를 `Ctrl + C`로 끈다.
- 3-2 실전 프로젝트는 DART 공시 MCP 서버와 Tavily 공식 MCP를 쓴다. `DART_API_KEY`는 강사가 알려 주고 `TAVILY_API_KEY`는 수강생이 각자 무료로 받는다([agent_docs/setup.md](agent_docs/setup.md)). 키가 없거나 사내망에서 막히면 DART는 `[모의 DART]` 견본 답, Tavily는 빼고 진행하니 정상이다. 키를 대신 지어내지 않는다.
- 터미널을 이미 닫았으면 PowerShell: `Get-NetTCPConnection -LocalPort 8000 -State Listen | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }`.

## 지킬 것

- 모델은 `config.llm.get_llm()`, 임베딩은 `config.embeddings.get_embeddings()`. 주소·모델 이름·키를 코드에 직접 쓰지 않는다.
- 사내 API로 새 코드를 짤 때는 [agent_docs/samsung_api.md](agent_docs/samsung_api.md), RAGaaS는 [agent_docs/ragaas.md](agent_docs/ragaas.md)를 먼저 읽는다.
- `.env`의 키·토큰은 출력하거나 파일에 쓰지 않고, 수강생에게 대화에 붙여 넣으라고 하지 않는다.
- `code/`, `assets/`, `config/`는 고치지 않는다. 파일 입출력에는 늘 `encoding="utf-8"`을 넣는다(윈도우 기본 cp949).

## 문제가 생기면

- 문서: 설치 [setup.md](agent_docs/setup.md), 경로 [paths.md](agent_docs/paths.md), 오류별 해결 [troubleshooting.md](agent_docs/troubleshooting.md). 추측으로 우회하지 않는다.
- 1) `uv run python -m config.check --json`(Langfuse·캡스톤은 `--langfuse`) 2) ⛔마다 `fix` 안내대로 고친다 3) 다 🟢인데 안 되면 알리고 `--live`.
- `.env`의 `COURSE_ENV`는 사내 `samsung`, 사외 `out`이다. `.env`의 값을 읽어 보여 주거나 대신 지어내지 않는다.
- 풀리지 않는 사내 기능 문제는 그 셀을 건너뛰고, 강사에게 보여 줄 셀과 오류 메시지 전체를 정리해 준다.
- 보고: `설정 점검 결과: 준비 완료 / 고칠 곳 N개`, 실행 환경, `⛔ <항목>: <문제> → <할 일>`, (`--live`면) LLM·임베딩 호출 🟢/⛔.
