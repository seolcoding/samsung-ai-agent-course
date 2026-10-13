# AGENTS.md — 수강생 자료 (AI 코딩 도우미용)

이 폴더는 "AI Agent 개발" 과정의 수강생 자료입니다. 수강생은 코딩이 낯선 사람이 많습니다. 쉬운 말로 짧게 설명하고, 결과부터 말합니다.

## 폴더 지도

- `ChapterNN/notebooks/` 수업 노트북. `_LEC`는 강의(슬라이드·설명·퀴즈), `_LAB_MC`는 객관식판 실습(수강생이 쓰는 것), `_LAB`은 옛 빈칸판 실습. `data/`는 실습 자료.
- `ChapterNN/code/raw/` 받은 원본 실습 코드, `ChapterNN/code/solution/` 그 정답. 참고용이며 수업은 노트북으로 한다.
- `ChapterNN/slides/` 강의 슬라이드 PDF.
- `ChapterNN/assets/` 그 챕터 노트북의 화면 도구(슬라이드 뷰어, 퀴즈).
- `config/` 모델·임베딩·RAG 연결 설정(챕터 공통).
- `Chapter02/capstone/` 4일차 캡스톤 프로젝트 폴더. 수강생이 AI와 함께 직접 고치는 곳이다(안내는 `4-3_capstone_LAB` 노트북과 이 폴더의 README.md).

## 실습 노트북에서 도울 때

수강생은 객관식판 실습 노트북(`_LAB_MC`)을 쓴다. 빈칸을 채우는 것이 아니라 주석으로 된 보기 중 하나를 골라 주석을 푸는 방식이다.

- `# ✅ CHOOSE_HERE:` 아래에 보기 4개가 주석으로 들어 있다. 줄 끝의 번호(1️⃣~4️⃣)와 설명으로 보기를 구분한다. 한 보기가 여러 줄이면 같은 번호가 붙은 줄을 모두 푼다.
  - 푸는 법(Windows): 같은 번호의 줄을 모두 선택하고 `Ctrl + /`. 다시 주석 처리할 때도 같다.
  - 보기 밖의 줄, 다른 보기의 줄은 고치지 않는다. 보기에 없는 코드를 새로 써 주지 않는다.
  - 보기를 대신 골라 달라고 하면 바로 정답을 말하지 말고, 보기마다 무엇이 다른지와 셀을 실행하면 어떻게 될지를 설명해 수강생이 고르게 돕는다. 보기마다의 해설은 접힌 "정답 보기"에 있다.
  - 함수 몸통 맨 밑의 `pass  # 그대로 둡니다`는 지우지 않는다. 보기를 푼 뒤에도 그대로 둔다.
- `# ✍️ CHANGE_HERE:` 바로 아래 줄은 값만 바꿔 다시 실행한다(바꿔 보기 예제).
- 실행 결과는 셀 아래 **성공 기준**(🟢 되어야 하는 것, ⛔ 다시 해야 하는 신호)과 비교한다. ⛔이면 푼 줄을 다시 주석 처리하고 다른 보기를 고르게 한다.
- 맨 위 설정 셀의 LangChain 디버그(`set_debug(True)`)는 기본으로 켜져 있다. 출력이 길어도 정상이다.
- 오류가 나면 수강생에게 오류 메시지 전체를 붙여 넣게 하고, 원인부터 쉬운 말로 설명한다.
- 셀은 위에서부터 차례로 실행된다고 보고, 앞 셀에서 만든 이름을 그대로 쓴다.
- 새 기능, 예외 처리, 재시도를 부탁받지 않았으면 더하지 않는다.
- 옛 실습 노트북(`_LAB`, `_MC` 없음)도 폴더에 남아 있다. 그쪽은 `# ✍️ WRITE_HERE:` 아래 `...  # ✍️ 여기를 채웁니다` 줄(빈칸)만 채우는 방식이다. 수강생이 그 노트북을 열었으면 `_LAB_MC`를 쓰도록 알려 준다(4-3 캡스톤은 `_LAB`만 있다).

## 서버를 띄우는 실습 (Chapter02: MCP·A2A·캡스톤)

- 3-2 MCP, 3-3 A2A 노트북 폴더에는 **정답이 모두 들어간 서버 파일**(`mcp_server.py`, `a2a_server.py`)이 미리 들어 있다. 노트북 셀은 그 코드를 나눠 보여 주고 보기를 고르는 곳이며, 셀을 실행해도 서버 파일은 바뀌지 않는다.
- 서버는 VS Code **새 터미널**에서 저장소 맨 위 폴더 기준으로 띄운다. 예: `uv run python course/Chapter02/notebooks/mcp_server.py`. 노트북 셀에서 서버를 실행하지 않는다(커널이 멈춘다).
- 서버 터미널은 켜 둔 채 노트북으로 돌아와 클라이언트 셀을 실행한다.
- 서버 쪽을 바꿔 보는 예제(도구 설명, Agent Card 문구 등)는 노트북 셀이 아니라 폴더의 `.py` 파일을 고치고 저장(`Ctrl + S`)한 뒤, 터미널에서 Ctrl+C로 끄고 같은 명령으로 다시 띄운다. 그다음 연결 셀부터 다시 실행한다.
- 포트: MCP 8000, A2A 8001, 캡스톤 MCP 서버 8001. `error while attempting to bind on address`(맥 `address already in use`, Windows `[Errno 10048]`)가 나오면 앞 서버 터미널을 Ctrl+C로 끈다. 터미널을 이미 닫았으면 PowerShell에서 `Get-NetTCPConnection -LocalPort 8000 -State Listen | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }`(포트 번호는 바꿔서)로 끈다.
- 캡스톤(`Chapter02/capstone/`)은 수강생이 AI와 함께 서버·코드 파일을 직접 고친다.

## 지킬 것

- 모델은 `config.llm.get_llm()`, 임베딩은 `config.embeddings.get_embeddings()`로 부른다. 주소·모델 이름·키를 코드에 직접 쓰지 않는다.
- 사내(삼성) LLM·임베딩으로 새 코드(셀, 캡스톤, 새 Agent)를 만들 때는 먼저 [agent_docs/samsung_api.md](agent_docs/samsung_api.md)를 읽는다. LangChain과 맞추는 법, 참조할 코드, 저장소 밖에서 쓰는 코드가 있다. 사내 RAGaaS는 [agent_docs/ragaas.md](agent_docs/ragaas.md)를 읽는다.
- `.env`의 키와 토큰은 출력하거나 파일에 쓰지 않는다.
- `code/`, `assets/`, `config/`의 파일은 고치지 않는다. `capstone/`은 고쳐도 된다.
- 텍스트 파일을 읽고 쓰는 코드는 늘 `encoding="utf-8"`을 넣는다. 수강생 PC는 윈도우라 기본값(cp949)으로 열면 한글 파일이 깨진다.

## 문제가 생기면 (설치·경로·연결)

아래 문서를 먼저 읽고, 그 순서대로 진단한 뒤 수강생 PC를 설정해 준다. 추측으로 코드를 고쳐 우회하지 않는다.

- 설치·커널·`.env`·모델 부르는 법: [agent_docs/setup.md](agent_docs/setup.md)
- 파일을 못 찾을 때, 경로를 쓸 때: [agent_docs/paths.md](agent_docs/paths.md)
- 오류 메시지별 원인과 해결: [agent_docs/troubleshooting.md](agent_docs/troubleshooting.md)
- 사내 LLM·임베딩을 LangChain에서 쓰는 법과 참조 코드: [agent_docs/samsung_api.md](agent_docs/samsung_api.md)
- 사내 RAGaaS 올리기·검색·지우기와 참조 코드: [agent_docs/ragaas.md](agent_docs/ragaas.md)

진단 순서:
1. 저장소 맨 위에서 `uv run python -m config.check --json`을 실행한다(Langfuse 실습·캡스톤이면 `--langfuse`도 붙인다). 키·토큰 값은 나오지 않는다.
2. ⛔ 항목마다 `fix` 안내대로 고친다. 설치 문제는 `uv sync --extra notebooks`, 연결 방식은 `.env`의 `COURSE_ENV`(사내 `samsung`, 사외 `out`), 빠진 이름은 `.env`에 채우도록 안내한다. `.env`의 값을 읽어 보여 주거나 대신 지어내지 않는다.
3. 이름이 모두 🟢인데도 연결 오류가 나면, 수강생에게 알린 뒤 `--live`로 실제 호출을 한 번 해 본다.
4. 그래도 안 되면 오류 메시지로 troubleshooting.md를 찾는다. 파일을 못 찾는 문제는 paths.md를 본다.
5. 고친 뒤 노트북은 맨 위 셀부터 다시 실행한다. Streamlit 앱을 띄우는 셀은 끝나지 않으니 ■로 멈추고 다음 셀로 넘어가게 하고, `input()` 셀에는 답을 입력하게 한다. 문서에 "확인되지 않음"으로 적힌 사내 기능 문제는 troubleshooting.md의 순서대로 먼저 확인하고, 풀리지 않으면 그 셀은 건너뛰고 다음 절을 진행하게 한 뒤 강사에게 보여 줄 내용(셀, 오류 메시지 전체)을 정리해 준다.

점검 결과는 수강생에게 이렇게 짧게 보고한다.

```
설정 점검 결과: 준비 완료 / 고칠 곳 N개
- 실행 환경: 사내(samsung) 또는 사외(out)
- ⛔ <항목>: <무엇이 문제인지> → <할 일>
- (--live를 했다면) LLM 호출 🟢/⛔, 임베딩 호출 🟢/⛔
```
