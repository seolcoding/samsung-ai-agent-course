# AGENTS.md — 수강생 자료 (AI 코딩 도우미용)

이 폴더는 "AI Agent 개발" 과정의 수강생 자료입니다. 수강생은 코딩이 낯선 사람이 많습니다. 쉬운 말로 짧게 설명하고, 결과부터 말합니다.

## 폴더 지도

- `ChapterNN/notebooks/` 수업 노트북. `_LEC`는 강의(슬라이드·설명·퀴즈), `_LAB`은 실습. `data/`는 실습 자료.
- `ChapterNN/code/raw/` 받은 원본 실습 코드, `ChapterNN/code/solution/` 그 정답. 참고용이며 수업은 노트북으로 한다.
- `ChapterNN/slides/` 강의 슬라이드 PDF.
- `ChapterNN/assets/` 그 챕터 노트북의 화면 도구(슬라이드 뷰어, 퀴즈).
- `config/` 모델·임베딩·RAG 연결 설정(챕터 공통).
- `Chapter02/capstone/` 4일차 캡스톤 프로젝트 폴더. 수강생이 AI와 함께 직접 고치는 곳이다(안내는 `4-3_capstone_LAB` 노트북과 이 폴더의 README.md).

## 실습 노트북에서 도울 때

- `# ✍️ WRITE_HERE:` 아래 `...  # ✍️ 여기를 채웁니다` 줄(빈칸)만 채운다. 빈칸 밖의 줄은 고치지 않는다.
- `# ✍️ CHANGE_HERE:` 바로 아래 줄은 값만 바꾼다.
- 새 기능, 예외 처리, 재시도를 부탁받지 않았으면 더하지 않는다.
- 코드를 준 뒤에는 각 줄이 하는 일을 짧게 설명한다. 오류가 나면 원인부터 설명한다.
- 셀은 위에서부터 차례로 실행된다고 보고, 앞 셀에서 만든 이름을 그대로 쓴다.
- `%%writefile`로 시작하는 셀은 서버·설정 파일을 노트북 폴더에 쓰는 셀이다. 첫 줄(`%%writefile …`)은 지우지 않는다.

## 서버를 띄우는 실습 (Chapter02: MCP·A2A·캡스톤)

- 서버는 VS Code **새 터미널**에서 저장소 맨 위 폴더 기준으로 띄운다. 예: `uv run python course/Chapter02/notebooks/mcp_server.py`. 노트북 셀에서 서버를 실행하지 않는다(커널이 멈춘다).
- 서버 터미널은 켜 둔 채 노트북으로 돌아와 클라이언트 셀을 실행한다. 서버 파일을 고쳤으면 터미널에서 Ctrl+C로 끄고 쓰기 셀을 다시 실행한 뒤 다시 띄운다.
- 포트: MCP 8000, A2A 8001, 캡스톤 MCP 서버 8001. `address already in use`가 나오면 앞 서버 터미널을 Ctrl+C로 끈다.

## 지킬 것

- 모델은 `config.llm.get_llm()`, 임베딩은 `config.embeddings.get_embeddings()`로 부른다. 주소·모델 이름·키를 코드에 직접 쓰지 않는다.
- `.env`의 키와 토큰은 출력하거나 파일에 쓰지 않는다.
- `code/`, `assets/`, `config/`의 파일은 고치지 않는다. `capstone/`은 고쳐도 된다.

## 문제가 생기면 (설치·경로·연결)

아래 문서를 먼저 읽고, 그 순서대로 진단한 뒤 수강생 PC를 설정해 준다. 추측으로 코드를 고쳐 우회하지 않는다.

- 설치·커널·`.env`·모델 부르는 법: [agent_docs/setup.md](course/agent_docs/setup.md)
- 파일을 못 찾을 때, 경로를 쓸 때: [agent_docs/paths.md](course/agent_docs/paths.md)
- 오류 메시지별 원인과 해결: [agent_docs/troubleshooting.md](course/agent_docs/troubleshooting.md)

진단 순서:
1. 저장소 맨 위에서 `uv run python -m config.check --json`을 실행한다(Langfuse 실습·캡스톤이면 `--langfuse`도 붙인다). 키·토큰 값은 나오지 않는다.
2. ⛔ 항목마다 `fix` 안내대로 고친다. 설치 문제는 `uv sync --extra notebooks`, 연결 방식은 `.env`의 `COURSE_ENV`(사내 `samsung`, 사외 `out`), 빠진 이름은 `.env`에 채우도록 안내한다. `.env`의 값을 읽어 보여 주거나 대신 지어내지 않는다.
3. 이름이 모두 🟢인데도 연결 오류가 나면, 수강생에게 알린 뒤 `--live`로 실제 호출을 한 번 해 본다.
4. 그래도 안 되면 오류 마지막 줄로 troubleshooting.md를 찾는다. 파일을 못 찾는 문제는 paths.md를 본다.
5. 고친 뒤 노트북은 맨 위 셀부터 다시 실행한다. 문서에 "확인되지 않음"으로 적힌 사내 기능 문제는 강사에게 알린다.

점검 결과는 수강생에게 이렇게 짧게 보고한다.

```
설정 점검 결과: 준비 완료 / 고칠 곳 N개
- 실행 환경: 사내(samsung) 또는 사외(out)
- ⛔ <항목>: <무엇이 문제인지> → <할 일>
- (--live를 했다면) LLM 호출 🟢/⛔, 임베딩 호출 🟢/⛔
```
