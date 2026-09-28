# AGENTS.md — 수강생 자료 (AI 코딩 도우미용)

이 폴더는 "AI Agent 개발" 과정의 수강생 자료입니다. 수강생은 코딩이 낯선 사람이 많습니다. 쉬운 말로 짧게 설명하고, 결과부터 말합니다.

## 폴더 지도

- `ChapterNN/notebooks/` 수업 노트북. `_LEC`는 강의(슬라이드·설명·퀴즈), `_LAB`은 실습. `data/`는 실습 자료.
- `ChapterNN/code/raw/` 받은 원본 실습 코드, `ChapterNN/code/solution/` 그 정답. 참고용이며 수업은 노트북으로 한다.
- `ChapterNN/slides/` 강의 슬라이드 PDF.
- `ChapterNN/assets/` 그 챕터 노트북의 화면 도구(슬라이드 뷰어, 퀴즈).
- `config/` 모델·임베딩·RAG 연결 설정(챕터 공통).

## 실습 노트북에서 도울 때

- `# ✍️ WRITE_HERE:` 아래 `...  # ✍️ 여기를 채웁니다` 줄(빈칸)만 채운다. 빈칸 밖의 줄은 고치지 않는다.
- `# ✍️ CHANGE_HERE:` 바로 아래 줄은 값만 바꾼다.
- 새 기능, 예외 처리, 재시도를 부탁받지 않았으면 더하지 않는다.
- 코드를 준 뒤에는 각 줄이 하는 일을 짧게 설명한다. 오류가 나면 원인부터 설명한다.
- 셀은 위에서부터 차례로 실행된다고 보고, 앞 셀에서 만든 이름을 그대로 쓴다.

## 지킬 것

- 모델은 `config.llm.get_llm()`, 임베딩은 `config.embeddings.get_embeddings()`로 부른다. 주소·모델 이름·키를 코드에 직접 쓰지 않는다.
- `.env`의 키와 토큰은 출력하거나 파일에 쓰지 않는다.
- `code/`, `assets/`, `config/`의 파일은 고치지 않는다.

## 문제가 생기면 (설치·경로·연결)

아래 문서를 먼저 읽고, 그 순서대로 진단한 뒤 수강생 PC를 설정해 준다. 추측으로 코드를 고쳐 우회하지 않는다.

- 설치·커널·`.env`·모델 부르는 법: [agent_docs/setup.md](agent_docs/setup.md)
- 파일을 못 찾을 때, 경로를 쓸 때: [agent_docs/paths.md](agent_docs/paths.md)
- 오류 메시지별 원인과 해결: [agent_docs/troubleshooting.md](agent_docs/troubleshooting.md)

진단 순서:
1. 오류의 마지막 줄을 읽고 troubleshooting.md에서 찾는다.
2. 커널이 저장소 `.venv`인지, `os.getcwd()`가 `…/course/ChapterNN/notebooks`인지 본다.
3. 설치 문제면 저장소 맨 위에서 `uv sync --extra notebooks`를 안내하거나 실행한다.
4. 연결 문제면 노트북 맨 위 환경 점검 셀을 실행해 빠진 설정 이름을 확인한다. `.env`의 값은 출력하지 않는다.
5. 고친 뒤 맨 위 셀부터 다시 실행한다. 사내 기능 지원 여부처럼 문서에 "확인되지 않음"으로 적힌 것은 강사에게 알린다.
