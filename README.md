# 삼성전자 DS AI Agent 교육

업무 자료·실습 코드·교안을 모은 프로젝트다. 작업 위치는 `~/100_Dev/samsung_ds_ai_developer`이다.

## 자료 찾기

| 위치 | 내용 |
| --- | --- |
| [작업 지침](AGENTS.md) | 교육 개편 방향, 실행 환경, 작업 규칙, 기존에 발견한 결함 |
| [강의 자료 지도](docs/COURSE_MAP.md) | 4일 과정의 PDF·실습·노트북 위치 |
| [통합 교안 작성 규칙](docs/INTEGRATED_LESSONS.md) · [노트북 틀](lessons/_template.ipynb) | 슬라이드·설명·실습을 한 권으로 만드는 구조와 이름 |
| [교안 PDF](docs/raw/) | 교안 정본 14개 |
| [주피터 노트북 안내](docs/NOTEBOOKS.md) | 교안·실습 노트북의 위치와 실행 순서 |
| [M1 실습](src/raw/Chapter01/) | 1·2일차 Python 실습 |
| [M2 실습](src/raw/Chapter02/) | 3·4일차 Python 실습 (`00-review/` ~ `06-capstone/`) |
| [정답본](src/solution/) | Python 실습 정답 |
| [공통 설정](src/config/) · [패키지 목록](pyproject.toml) | 환경에 따른 API 연결 코드와 Python 의존성 |
| [슬라이드 해설 노트북](docs/notebooks/) | PDF별 학습용 노트북. 실행 노트북은 각 Python 파일 옆에 있음 |

`lessons/`는 제작 중인 통합 교안의 최종 위치다. 현재는 작성 틀을 마련했으며 완성된 주제별 교안은 아직 없다. 기존 PDF·해설·코드 노트북은 원본 자료로 유지한다.

## 실행 환경 선택

[.env.sample](.env.sample)을 복사해 맥북에는 `.env` 또는 `.env.external`, 사내 PC에는 `.env.internal`을 만든다. 실제 키와 주소는 복사한 파일에만 입력한다. 이 파일들은 Git에서 제외된다.

| 환경 파일 | 바꿀 값 | 동작 |
| --- | --- | --- |
| `.env` 또는 `.env.external` | `LLM_PROVIDER=openai`, `EMBED_PROVIDER=openai`, `RAG_PROVIDER=mock`; OpenAI 키·모델명 입력 | OpenAI LLM·임베딩 사용, RAGaaS는 모의 응답 |
| `.env.internal` | 세 PROVIDER를 `samsung`으로 변경; 사내 주소·모델명·인증 값 입력 | 사내 LLM·임베딩·RAGaaS 사용 |

프로젝트 루트에서 환경 파일을 지정해 실행한다. 맥북 예: `uv run --env-file .env python src/raw/Chapter01/01-llm-api/03_langchain.py`. 내부에서는 `.env.internal`을 지정한다. 환경을 선택하는 기준은 실행 명령이며, 사내 URL의 응답 여부로 자동 전환하지 않는다. 사내 API가 일시적으로 실패하면 오류를 확인하고 원인을 조사한다.

`RAG_PROVIDER=mock`의 검색 내용에는 `[MOCK RAGaaS]`가 표시된다. 이 응답은 API 흐름 확인용이며 실제 보험 약관이나 사내 문서의 검색 결과가 아니다. Langfuse 예제는 별도 `LANGFUSE_*` 설정이 필요하다.

## 자료 시점

9월 17일 확정된 실습 개편 방향과 9월 21일 코드 점검 내용은 [AGENTS.md](AGENTS.md)에 있다. 이전 메일·첨부·전달받은 ZIP·준비 기록은 저장소 밖의 강의 아카이브에 보관한다.

## Git과 테스트

구조 정리 작업은 `refactor/course-layout` 브랜치에 있다. `main`과 `organize/consolidate-20260924`는 이전 상태를 보존한다. 통합 전 코드 기준점은 `6f8db3c`이다.

경로·환경 분기 테스트: `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`. `uv sync` 후에는 프로젝트의 `.venv`에서 실습을 실행한다. 실제 키가 든 `.env`는 Git에서 제외한다.

## 통합 기록

2026-09-24 아래 자료를 이 위치로 모았다.

- `~/200_Vault/220_Projects/samsung_elec_agent`: 업무 문서와 원본 첨부.
- `~/200_Vault/220_Projects/samsung_ds_ai_developer`: 전달받은 교안 ZIP.
- 기존 `2026-AI-PD-main/`: Git 저장소, 실습 코드와 교안 PDF.

전체 백업·이동 목록·복구 절차는 `~/_MANIFESTS/samsung_ds_consolidation_20260924/`에 있다. 이번 폴더 개편과 보관 자료 분리 기록은 `~/_MANIFESTS/samsung_ds_course_layout_20260924.md`에 있다.
