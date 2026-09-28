# 문제 해결

먼저 저장소 맨 위에서 `uv run python -m config.check`를 실행해 ⛔ 줄을 고친다(설정 문제는 대부분 여기서 잡힌다). 그다음 오류 메시지의 **마지막 줄**(오류 이름과 설명)을 읽고 아래 표에서 찾는다. 해결한 뒤에는 **맨 위 셀부터 다시 실행**한다.
설치·`.env`는 [setup.md](setup.md), 경로는 [paths.md](paths.md)를 함께 본다.
키·토큰 값은 절대 출력하지 않는다. 있는지만 확인한다: `import os; print(bool(os.getenv("OPENAI_API_KEY")))`

## 설치·커널

| 증상 | 원인 | 해결 |
|---|---|---|
| `ModuleNotFoundError: No module named 'config'` (또는 `dotenv`, `langchain_…`, `openai`) | 저장소 `.venv`가 아닌 커널을 골랐거나 설치를 안 함 | 커널을 저장소 `.venv`로 고른다. 그래도 나오면 저장소 맨 위에서 `uv sync --extra notebooks` |
| `No module named 'jupyterquiz'` | `notebooks` 묶음 없이 설치함 | `uv sync --extra notebooks` |
| `No module named 'assets'` | 준비 셀을 건너뛰었거나, 노트북이 다른 폴더에서 실행됨 | 맨 위 준비 셀부터 실행. `os.getcwd()`가 `…/course/ChapterNN/notebooks`인지 확인([paths.md](paths.md)) |
| `uv: command not found` | uv 미설치 또는 PATH에 없음 | uv를 설치하고 터미널을 새로 연다 |

## 화면(슬라이드·퀴즈)

| 증상 | 원인 | 해결 |
|---|---|---|
| 슬라이드 자리에 "⛔ 슬라이드가 보이지 않으면" 안내만 보임 | 노트북을 다시 열어 화면 스크립트가 아직 안 돎 | 1. 바로 위 셀을 다시 실행 2. 안 되면 맨 위 셀부터 다시 실행 |
| 퀴즈·버튼이 눌리지 않음 | 같은 이유 | 그 셀을 다시 실행 |
| `FileNotFoundError: …/assets/quizzes/…` | 노트북 폴더가 아닌 곳에서 실행됨 | [paths.md](paths.md)의 "노트북 폴더 기준" 확인 |

## 연결 설정(.env)

| 증상 | 원인 | 해결 |
|---|---|---|
| 환경 점검 셀: "준비가 덜 되었습니다. 빠진 설정 N개" | `.env`에 필요한 이름이 없음 | 괄호 안 이름을 `.env`에 채운다([setup.md](setup.md) 표) |
| `RuntimeError: OPENAI_MODEL 환경변수가 필요합니다` 등 | 같은 이유 | 같은 해결 |
| `RuntimeError: 사내 API 설정이 부족합니다: [...]` | `LLM_PROVIDER`(또는 EMBED·RAG)가 `samsung`인데 사내 값이 없음 | 사외 PC면 `LLM_PROVIDER=openai`, `EMBED_PROVIDER=openai`, `RAG_PROVIDER=mock`. 사내 PC면 강사가 준 사내 값 |
| `ValueError: 지원하지 않는 LLM_PROVIDER` | 값 오타 | `openai` 또는 `samsung` |
| `.env`를 고쳤는데 그대로임 | 커널이 예전 값을 기억함 | 커널 다시 시작 후 맨 위부터 실행 |
| 값이 `# …`로 시작하는 글자로 들어감(주소·모델 이름이 이상함) | `KEY=   # 설명`처럼 빈 값 뒤에 주석을 붙임 | 설명은 윗줄로 옮기고 `KEY=값`만 남긴다 |
| 사내 PC인데 OpenAI로 연결하려 함 / 사외 PC인데 사내 주소로 연결하려 함 | `.env`의 `COURSE_ENV`가 틀렸거나, 따로 적은 `*_PROVIDER`가 덮어씀 | 사내 `COURSE_ENV=samsung`, 사외 `COURSE_ENV=out`. 따로 적은 `LLM_PROVIDER` 등은 지운다 |
| `.env`를 못 찾음 | 이름이 `.env`가 아님(예: `.env.txt`, `.env.external`) 또는 위치가 다름 | 저장소 맨 위에 정확히 `.env`로 둔다. 윈도우 탐색기는 확장자를 숨기니 주의 |

## LLM·API 호출

| 증상 | 원인 | 해결 |
|---|---|---|
| `AuthenticationError` / 401 | 키가 틀리거나 만료됨 | `.env`의 키를 강사에게 다시 받는다. 키를 화면에 출력해 확인하지 않는다 |
| `NotFoundError` / 404, "model … does not exist" | 모델 이름이 틀림 | `.env`의 `OPENAI_MODEL`(사내는 `model`) 값을 확인 |
| `APIConnectionError`, 연결 시간 초과 | 네트워크. 사내 값은 사내망에서만, `openai`는 인터넷이 필요 | 네트워크 확인. 사외에서는 `openai` 설정을 쓴다 |
| `RateLimitError` / 429 | 짧은 시간에 요청이 몰림 | 잠시 뒤 다시 실행 |
| 사내 환경에서 SDK 셀(`client.responses…`), 도구 호출(`bind_tools`), 구조화 출력(`with_structured_output`)만 실패 | 사내 게이트웨이가 그 기능을 지원하는지 아직 확인되지 않음 | 오류 메시지를 강사에게 알린다. 코드를 바꿔 우회하지 않는다 |
| 사내 RAGaaS 인증 실패 | `rag_api_key`(api-key 헤더)와 `rag_credential_key`(x-dep-ticket) 둘 다 필요 | 두 값이 모두 있는지 확인. 사외에서는 `RAG_PROVIDER=mock` |

## 실습 중

| 증상 | 원인 | 해결 |
|---|---|---|
| 빈칸(`...`)을 안 채우고 실행해 결과가 이상함 | `...`는 파이썬에서 오류 없이 지나간다 | `# ✍️ WRITE_HERE:` 아래 빈칸을 채운 뒤 실행 |
| `SyntaxError` | 채운 코드의 쉼표·괄호·들여쓰기 | 오류 줄 번호 근처를 본다. 빈칸 줄의 들여쓰기를 그대로 둔다 |
| 셀이 끝나지 않음(반복이 계속됨) | 멈추는 조건이 없는 흐름 | 셀 실행 중지(■) |
| 셀이 입력을 기다리며 멈춤 | `input()` 셀 | VS Code 위쪽 입력창에 답을 입력 |
| 같은 셀을 다시 실행하니 결과가 쌓임(대화 기록, 검색 결과 중복) | 앞 실행의 값이 메모리에 남음 | 커널 다시 시작 후 맨 위부터 실행 |
| `LangChainDeprecationWarning` 등 경고 | 라이브러리 안내 문구 | 무시해도 된다 |

## Streamlit 앱(파일로 띄우는 실습)

| 증상 | 원인 | 해결 |
|---|---|---|
| `No module named streamlit` | 커널이 저장소 `.venv`가 아님 | 커널 확인 |
| 첫 실행에서 이메일을 묻고 멈춤 | Streamlit 첫 실행 안내 | 셀을 멈추고 실행 명령 끝에 `--server.headless true`를 붙여 다시 실행, 주소(`http://localhost:8501`)를 직접 연다 |
| "Port 8501 is already in use" | 앞 앱이 아직 떠 있음 | 앞 셀을 멈추거나 `--server.port 8502` |
| 앱이 떠 있는 동안 다른 셀이 안 돎 | 앱 셀이 커널을 붙잡고 있음 | 앱 셀을 멈춘(■) 뒤 진행 |
| 파일을 고쳤는데 앱이 그대로 | 파일 쓰기 셀을 다시 안 돌림 | 앱 멈춤 → 파일 쓰기 셀 → 앱 셀 순서로 다시 실행 |

## 그래도 안 되면

오류 메시지 전체(키 값이 없는지 확인한 뒤), 실행한 셀, `os.getcwd()` 결과, 고른 커널 이름을 강사에게 알린다.
