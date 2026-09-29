# 실행 검증 기록

> 2026-09-28 폴더 개편 전 기록이라 옛 경로를 쓴다. 지금 경로: `src/raw/ChapterNN/` → `course/ChapterNN/code/raw/`, `src/solution/ChapterNN/` → `course/ChapterNN/code/solution/`, `src/config/` → `course/config/`, `tests/` → `dev/tests/`.

기존 실습 코드(`src/raw/`·`src/solution/`)와 환경 설정(`src/config/`)의 검증 기록이다. 환경: macOS, 프로젝트 `.venv`, Python 3.12.7. 설치 버전은 `uv.lock`으로 고정한다.

환경·설정 테스트: `uv run --extra notebooks python -m unittest discover -s tests -p 'test_*.py'`

- `gpt-6` 계열은 langchain-openai 1.6.6에서 도구가 있으면 Responses API로 자동 전환된다. 이때 `content`가 dict 목록으로 나와 사내 경로(Chat Completions, 문자열)와 화면이 달랐다. `src/config/llm.py`에서 `use_responses_api=False`로 고정해 두 경로의 출력 형식을 맞췄다.

## 기존 실습 코드의 사외 실제 연결 (2026-09-26)

`src/solution/`의 실행 스크립트 38개를 같은 `.env`로 실행했다. MCP·A2A·캡스톤은 각 서버를 먼저 띄운 뒤 클라이언트를 실행했다.

| 대상 | 결과 |
| --- | --- |
| Chapter01 LLM API·LangChain·LangGraph·멀티에이전트 | 모두 정상 종료 |
| RAG (`03_vector_store`, `04_langchain_rag`, `00-review/03_langchain_rag`) | 질문에 답한 뒤 다음 입력을 기다리는 반복 구조. 입력이 끝나면 `EOFError`로 끝나며 오류가 아니다 |
| MCP (SSE 서버 + 클라이언트) | 도구 5개 발견, 시간·BMI·할 일 도구 호출 |
| A2A (서버 + 클라이언트) | Agent Card 조회, 응답 수신 |
| Observability 01~05 | Langfuse에 기록. LLM Judge·사용자 점수 출력 |
| 캡스톤 (`mcp_server.py` + `solution.py`) | 보고서 작성, Judge 종합 0.95, Langfuse 기록 |

- Langfuse에는 16개 trace, 127개 observation이 저장됐다. 실제 OpenAI 호출은 모델명(`gpt-6-luna`)·토큰·비용이 함께 기록됐다.
- 2026-09-16 이후 만든 Langfuse 조직에서는 `GET /api/public/traces` 같은 이전 조회 API가 410으로 막힌다. 교안 코드는 이 API를 쓰지 않는다. 검증 조회에는 `/api/public/v2/observations`를 썼다.
- 캡스톤 `mcp_server.py`는 A2A 서버(`01_a2a_server.py`)와 같은 8001 포트를 쓴다. 두 서버를 동시에 띄우지 않는다.

## 사내 API 설정 공통화

사내 LLM·임베딩·RAGaaS의 주소와 인증 헤더를 `src/config/samsung.py`의 `llm_config()`, `embedding_config()`, `ragaas_config()`로 모았다. `config/llm.py`·`embeddings.py`·`ragaas.py`와 `01_requests`·`02_openai`·`02_embeddings`(raw·solution, 옆 노트북 포함)가 이 함수를 쓴다. 헤더 이름과 값의 출처는 원본과 같다. 공통 임베딩은 `02_embeddings.py`와 같이 10개씩 나눠 요청한다.

## 사내 임베딩·RAGaaS 기준

사내 임베딩과 RAGaaS는 원본 교안 코드(최초 커밋 `addae97`)가 사내에서 동작한다고 보고, 현재 코드의 요청이 원본과 같은지 대조했다. 사내망 실행은 하지 않았다.

| 대상 | 원본과의 차이 | 처리 |
| --- | --- | --- |
| 임베딩 `config/embeddings.py` | 주소 `/v1/embeddings`, `x-dep-ticket` 헤더, `{"input": texts}` 동일. 필수값 검사·timeout 추가 | timeout을 120초로 설정 |
| RAGaaS `config/ragaas.py` | 주소·`x-dep-ticket`·`api-key` 헤더 동일. `json=` 전송은 `data=json.dumps()`와 같은 본문 | 원본에 없던 timeout 중 `insert-doc`은 300초로 설정 |
| `src/raw/.../05_ragaas.py` | 원본은 `rp-aicoa-meritz-pet` 인덱스를 코드에 고정. 개편본은 `index_name` 환경변수가 없으면 실패 | 원본 인덱스로 되돌림 |
| 캡스톤 정답 `rag_search` | 원본 요청의 `fields_exclude` 누락 | 원본 요청으로 되돌림 |

- 원본 정답본 `05_ragaas.py`·캡스톤은 `api-key` 헤더 없이 요청했다. 원본 실습본과 이 프로젝트 규칙(AGENTS.md 6절 5번)에 따라 두 헤더를 모두 보낸다.

아래는 아직 실행하지 않았다.

- 삼성 사내 LLM의 실제 응답과 도구 호출.
- 강의장 Windows PC의 설치, CodeMate UI, 사내 프록시·방화벽.
- 기존 `src/raw/`·`src/solution/` 전체의 최신 SDK 이관.

실제 연결을 선택한 경우 오류를 자동으로 mock으로 바꾸지 않는다. 연결 구성은 [환경 설정](../src/config/)을 따른다.
