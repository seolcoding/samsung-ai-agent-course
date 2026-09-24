# 삼성전자 DS AI Agent 교육

업무 자료·실습 코드·교안을 모은 프로젝트다. 작업 위치는 `~/100_Dev/samsung_ds_ai_developer`이다.

## 자료 찾기

| 위치 | 내용 |
| --- | --- |
| [작업 지침](AGENTS.md) | 교육 개편 방향, 실행 환경, 작업 규칙, 기존에 발견한 결함 |
| [업무 맥락](context/PROJECT_CONTEXT.md) | 메일 기반 일정·관계자·환경 안내. 2026-09-06 시점 기록 |
| [커리큘럼](context/CURRICULUM.md) | 전달받은 커리큘럼 비교 |
| [자료 출처](context/SOURCES.md) | 메일과 첨부자료 출처 |
| [교안 PDF](99_pdf/) | 교안 정본 14개 |
| [주피터 노트북 안내](NOTEBOOKS.md) | 교안·실습 노트북의 위치와 실행 순서 |
| [M1 실습](Chapter01/) | 1·2일차 실습 |
| [M2 실습](Chapter02/) | 3·4일차 실습 (`00-review/` ~ `06-capstone/`) |
| [정답본](solution/) | 실습 정답 |
| [공통 설정](config/) · [패키지 목록](pyproject.toml) | LLM 연결 코드와 Python 의존성 |
| [메일·첨부 원본](private/) | 로컬 보관 자료. Git 제외 |
| [전달받은 ZIP](source_archives/) | 원본 ZIP 2개. Git 제외 |

## 실행 환경 선택

[.env.sample](.env.sample)을 복사해 맥북에는 `.env.external`, 사내 PC에는 `.env.internal`을 만든다. 실제 키와 주소는 복사한 파일에만 입력한다. 두 파일은 Git에서 제외된다.

| 환경 파일 | 바꿀 값 | 동작 |
| --- | --- | --- |
| `.env.external` | `LLM_PROVIDER=openai`, `EMBED_PROVIDER=openai`, `RAG_PROVIDER=mock`; OpenAI 키·모델명 입력 | OpenAI LLM·임베딩 사용, RAGaaS는 모의 응답 |
| `.env.internal` | 세 PROVIDER를 `samsung`으로 변경; 사내 주소·모델명·인증 값 입력 | 사내 LLM·임베딩·RAGaaS 사용 |

프로젝트 루트에서 환경 파일을 지정해 실행한다. 예: `uv run --env-file .env.external python Chapter01/01-llm-api/03_langchain.py`. 내부에서는 `.env.internal`을 지정한다. 환경을 선택하는 기준은 실행 명령이며, 사내 URL의 응답 여부로 자동 전환하지 않는다. 사내 API가 일시적으로 실패하면 오류를 확인하고 원인을 조사한다.

`RAG_PROVIDER=mock`의 검색 내용에는 `[MOCK RAGaaS]`가 표시된다. 이 응답은 API 흐름 확인용이며 실제 보험 약관이나 사내 문서의 검색 결과가 아니다. Langfuse 예제는 별도 `LANGFUSE_*` 설정이 필요하다.

## 자료 시점

`context/`는 9월 6일 수집 기록을 보존한다. 9월 17일 확정된 실습 개편 방향과 9월 21일 코드 점검 내용은 [AGENTS.md](AGENTS.md)에 있다. 폴더 통합 과정에서 교육 내용이나 실습 코드는 수정하지 않았다.

## Git과 테스트

현재 작업 브랜치는 `main`이다. 코드와 업무 자료의 통합 이력, Chapter02 폴더 정리 이력을 모두 포함한다. 통합 전 코드 기준점은 `6f8db3c`이며, `organize/consolidate-20260924`는 통합·Chapter02 정리 상태(`2aecc12`)에 남겨 두었다.

격리 테스트 환경은 아직 만들지 않았다. 후속 테스트는 필요에 따라 프로젝트의 `.venv`에서 진행한다. `private/`와 `source_archives/`는 Git 복제나 worktree 생성 시 자동으로 복사되지 않는다.

## 통합 기록

2026-09-24 아래 자료를 이 위치로 모았다.

- `~/200_Vault/220_Projects/samsung_elec_agent`: 업무 문서와 원본 첨부.
- `~/200_Vault/220_Projects/samsung_ds_ai_developer`: 전달받은 교안 ZIP.
- 기존 `2026-AI-PD-main/`: Git 저장소, 실습 코드와 교안 PDF.

전체 백업·이동 목록·복구 절차는 `~/_MANIFESTS/samsung_ds_consolidation_20260924/`에 있다. 기존 폴더의 잔여 자료는 `~/000_Inbox/090_To_Delete/samsung_ds_consolidation_20260924/`에 보관했다.
