# AI Agent 개발 프로젝트 교육 — 교안 저장소

삼성전자 DS부문 AX·PI센터 "AI Agent 개발 프로젝트 교육"(4일, 32시간)의 교안과 실습 자료입니다.
이 문서는 저장소를 처음 받은 담당자를 위한 안내입니다. 무엇이 어디에 있는지, 수강생에게 무엇을 나눠 주는지, 새 판을 어떻게 만드는지를 설명합니다.

## 한눈에 보기

- 수업은 **주피터 노트북**으로 합니다. 개념은 강의 노트북(`_LEC`), 실습은 실습 노트북(`_LAB`)으로 진행합니다.
- 실습은 수강생이 사내 Coding AI(CodeMate)에게 지시하고 결과를 검토하는 방식입니다. 강의·실습 내용은 받은 원본(컨플루언스 자료의 Python 코드·교안 PDF)을 그대로 두고, 전달 방식만 노트북으로 바꿨습니다.
- 수강생에게 나눠 줄 자료는 **공개 저장소(github.com/seolcoding/samsung-ai-agent-course)의 `study` 브랜치**(기본 브랜치)입니다. 로컬 `study` 브랜치(`dev/release.sh`가 만듦, `course/`와 설치 파일만)를 그대로 올립니다. 강사용 자료까지 모두 든 브랜치는 공개 저장소의 `dev`입니다.

## 과정 구성

| 일차 | 노트북 | 주제 |
| --- | --- | --- |
| 1일차 | 1-1 ~ 1-3 | AI Agent Design Thinking, LLM API, LangChain |
| 2일차 | 1-4 ~ 2-3 | RAG, LangGraph, Multi-Agent, Streamlit RAG 서비스 |
| 3일차 | 3-1 ~ 3-4 | M1 복습, MCP, A2A, LangGraph 심화 |
| 4일차 | 4-1 ~ 4-3 | Harness Engineering, Langfuse 관측·평가, 캡스톤 프로젝트 |

1·2일차는 `course/Chapter01/`(M1), 3·4일차는 `course/Chapter02/`(M2)입니다. 모듈과 시간의 정본은 [커리큘럼](dev/docs/CURRICULUM.md)입니다.

## 브랜치

| 브랜치 | 들어 있는 것 | 누가 쓰나 |
| --- | --- | --- |
| `main` | 완성본 전체: 수강생 자료 + 강사용 자료(강사본 노트북, 빌더, 검사 도구, 문서) | 강사·담당자. 검사를 통과한 판만 합칩니다 |
| `study` | 수강생 자료만: `course/`, 설치 파일, 수강생용 안내 | 수강생. 이 브랜치나 zip을 나눠 줍니다 |
| `dev` | 앞으로 고칠 작업 | 강사·개발자 |

고치는 흐름은 한 방향입니다.

```text
dev (고치고 검사) → main (합치기) → study (dev/release.sh가 main에서 만든다)
```

- `study`는 `main`과 이력이 섞이지 않는 별도 브랜치입니다. 강사용 자료는 `study`의 이력에도 들어가지 않습니다.
- `study`에서 직접 고치지 않습니다. 고칠 것은 `dev`에서 고친 뒤 위 흐름을 다시 탑니다.

## 폴더

| 위치 | 들어 있는 것 |
| --- | --- |
| `course/` | **수강생 자료**. `study` 브랜치로 나가는 부분입니다 |
| `course/ChapterNN/notebooks/` | 수업 노트북(수강생본, 강사 메모 없음)과 실습 데이터 |
| `course/Chapter02/capstone/` | 4일차 캡스톤 프로젝트 폴더 |
| `course/ChapterNN/code/raw/`, `code/solution/` | 받은 원본 실습 코드와 정답 |
| `course/ChapterNN/slides/` | 교안 PDF |
| `course/config/` | 사내·사외 연결 설정(모델·임베딩·RAGaaS) |
| `course/agent_docs/` | 설치·경로·오류 해결 안내 |
| `dev/` | **강사·개발용**. 수강생에게 나가지 않습니다 |
| `dev/instructor/` | 강사본 노트북(강사용 메모 포함) |
| `dev/builders/`, `dev/qc/`, `dev/tests/` | 노트북을 만드는 빌더, 노트북 검사 도구, 테스트 |
| `dev/release.sh` | `main`에서 `study` 브랜치와 전달용 zip을 만드는 스크립트 |
| `dev/docs/` | 커리큘럼, 수강생 피드백 정리, 검증 기록 |
| `dev/materials/` | 커리큘럼 제안서, 인수인계서, 설문 원본 |
| `pyproject.toml`, `uv.lock`, `.env.sample` | 설치 파일과 연결 설정 견본 |
| `AGENTS.md` | 강사와 AI 도우미를 위한 작업 규칙·배경 |

## 강의장 PC 준비

강의장 PC는 계정별로 초기화되므로 1일차에 수강생과 함께 설치합니다(1.5~2시간). 순서는 [수강생 안내](course/README.md)와 [설치 안내](course/agent_docs/setup.md)에 있습니다. 요약하면 다음과 같습니다.

1. `uv` 설치 → 저장소 맨 위에서 `uv sync`
2. `.env.sample`을 복사해 `.env`를 만들고 `COURSE_ENV=samsung`(사내)과 사내 API 값을 채웁니다.
3. `uv run python -m config.check`로 점검합니다. ⛔ 줄이 없으면 준비가 끝난 것입니다.

## 새 판 만들기 (강사·관리자)

1. `dev`에서 고칩니다. 노트북은 직접 고치지 않고 `dev/builders/`의 글·spec을 고친 뒤 다시 빌드합니다(방법은 [dev/AGENTS.md](dev/AGENTS.md)).
2. 검사합니다.

   ```bash
   uv run python -m unittest discover -s dev/tests -p 'test_*.py'
   uv run python dev/qc/notebook_qc.py
   ```

3. `main`에 합치고 `study`와 zip을 만듭니다.

   ```bash
   git switch main
   git merge dev
   bash dev/release.sh v6
   git switch dev
   git push origin study dev   # 공개 저장소에 올립니다. 수강생은 study를 받습니다
   ```

   zip은 `~/800_Archives/830_Courses/samsung_ds_ai_developer/`에 생깁니다.

## 수업 전에 확인할 것

- **사내 게이트웨이의 도구 호출과 구조화 출력:** 3·4일차(MCP, A2A, Harness, 캡스톤)는 모든 단계가 도구 호출에 기대는데, 사내 게이트웨이에서는 아직 확인하지 못했습니다. 강의장에서 가장 먼저 점검할 항목입니다.
- **사내 패키지 미러:** `uv.lock`에 고정한 버전이 사내 미러에 있는지 확인합니다. 특히 하한을 올린 `a2a-sdk>=1.1.5`, `deepagents>=0.7.18`, `langfuse>=4.15.4`, `fastmcp>=3.4.7`입니다.
- **Langfuse:** 4일차 관측 실습에 쓸 서버 주소와 프로젝트 키를 정합니다.
- **Windows 강의장 PC에서 한 번 실행:** 이 교안은 macOS에서 만들고 Windows 조건(한국어 인코딩, 경로, 포트)을 코드로 흉내 내 점검했습니다. 실제 강의장 PC에서도 한 번 실행해 봅니다.

## 보안 주의

- `.env`에는 사내 키가 들어갑니다. Git에 올리지 않습니다(`.gitignore`에 들어 있습니다).
- `dev/materials/`에는 교육 계정이 적힌 인수인계 자료가 있습니다. 수강생에게는 `study` 브랜치만 나눠 주고, 이 저장소를 외부나 원격 저장소에 올리기 전에는 이 폴더를 확인합니다.
