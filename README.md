# 삼성전자 DS AI Agent 교육

삼성전자 DS AI Agent 교육의 실행형 교안·실습 프로젝트다. 작업 위치는 `~/100_Dev/samsung_ds_ai_developer`이다.

## 자료 찾기

| 위치 | 내용 |
| --- | --- |
| [작업 지침](AGENTS.md) | 교육 개편 방향, 실행 환경, 작업 규칙, 기존에 발견한 결함 |
| [커리큘럼 정본](docs/CURRICULUM.md) | 2026-09-03 커리큘럼(13개 블록·32시간)과 05-22 판 대비 변경점 |
| [11차수 수강생 피드백](docs/2026_11차수_수강생피드백.md) | 만족도 설문과 운영 측 수정 요청 5건 |
| [강의 자료 지도](docs/COURSE_MAP.md) | 4일 과정의 PDF·실습·노트북 위치 |
| [통합 교안 조립 지도](docs/INTEGRATED_LESSONS.md) · [노트북 틀](lessons/_template.ipynb) | `1.1`, `1.1.1` 번호에 맞춰 그림·설명·실습을 재배치하는 기준 |
| [강사용 시간 배분](docs/INSTRUCTOR_TIMING.md) | 같은 의미 번호에 연결된 4일·13개 블록의 운영 시간 |
| [최종 형태 시범본](lessons/_prototype_agent_loop.ipynb) | `1.1.2`·`1.1.3`: 그림·설명·코드·CodeMate 실습·검토를 한 권에 엮은 예 |
| [교안 PDF](docs/raw/) | 교안 정본 14개 |
| [주피터 노트북 안내](docs/NOTEBOOKS.md) | 교안·실습 노트북의 위치와 실행 순서 |
| [M1 실습](src/raw/Chapter01/) | 1·2일차 Python 실습 |
| [M2 실습](src/raw/Chapter02/) | 3·4일차 Python 실습 (`00-review/` ~ `06-capstone/`) |
| [정답본](src/solution/) | Python 실습 정답 |
| [공통 설정](src/config/) · [패키지 목록](pyproject.toml) | 환경에 따른 API 연결 코드와 Python 의존성 |
| [슬라이드 해설 노트북](docs/notebooks/) | PDF별 학습용 노트북. 실행 노트북은 각 Python 파일 옆에 있음 |

## 완성된 통합 교안

| 노트북 | 내용 | 세부 주제 |
| --- | --- | ---: |
| [1일차](lessons/day01.ipynb) | Agent 사고방식·LLM API·LangChain | 15 |
| [2일차](lessons/day02.ipynb) | RAG·LangGraph·Multi-Agent·Streamlit | 15 |
| [3일차](lessons/day03.ipynb) | 복습·MCP·A2A·상태·메모리·병렬 실행 | 17 |
| [4일차](lessons/day04.ipynb) | Harness·관측·평가·캡스톤 | 16 |

한 권 안에서 설명·그림·코드 실행·CodeMate 과제·검토가 이어진다. 13개 블록·63개 주제이며 학습자 제목은 의미 번호만 사용한다. 8개 생성 이미지와 16개 정확한 도식을 설명과 함께 첨부했다. 시간 배정은 [강사용 시간표](docs/INSTRUCTOR_TIMING.md)에 있다.

```bash
uv sync --extra notebooks
```

VS Code에서 노트북을 열고 프로젝트 `.venv` 커널을 선택한다. 기본은 외부 API 없이 실행하는 모드다. 실제 모델을 쓸 때만 첫 셀의 `RUN_LIVE`를, Langfuse 전송은 `ENABLE_LANGFUSE`를 켠다.

캡스톤 화면: `uv run --extra notebooks streamlit run src/courseware/app.py`

[강사용 검토 기준](docs/INSTRUCTOR_GUIDE.md) · [원본·그림 출처](docs/LESSON_SOURCES.md) · [실행 검증 기록](docs/VALIDATION.md). 기존 PDF·raw/solution은 비교 자료이며 통합본의 실행 구현은 [src/courseware](src/courseware/)에 있다.

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

구조 정리 기준은 `refactor/course-layout`, 통합 교안 작업은 `feat/integrated-course-suite` 브랜치에 있다. `main`과 `organize/consolidate-20260924`는 이전 상태를 보존한다. 통합 전 코드 기준점은 `6f8db3c`이다.

전체 교안 검증: `uv run --extra notebooks python tests/validate_lessons.py --execute --companions`.

경로·환경 분기·캡스톤 테스트: `uv run --extra notebooks python -m unittest discover -s tests -p 'test_*.py'`. `uv sync` 후에는 프로젝트의 `.venv`에서 실습을 실행한다. 실제 키가 든 `.env`는 Git에서 제외한다.

## 통합 기록

2026-09-24 아래 자료를 이 위치로 모았다.

- `~/200_Vault/220_Projects/samsung_elec_agent`: 업무 문서와 원본 첨부.
- `~/200_Vault/220_Projects/samsung_ds_ai_developer`: 전달받은 교안 ZIP.
- 기존 `2026-AI-PD-main/`: Git 저장소, 실습 코드와 교안 PDF.

전체 백업·이동 목록·복구 절차는 `~/_MANIFESTS/samsung_ds_consolidation_20260924/`에 있다. 이번 폴더 개편과 보관 자료 분리 기록은 `~/_MANIFESTS/samsung_ds_course_layout_20260924.md`에 있다.
