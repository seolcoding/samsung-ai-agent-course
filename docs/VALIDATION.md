# 통합 교안 검증 기록

검증일: 2026-09-24. 환경: macOS, 프로젝트 `.venv`, Python 3.12.7. 브랜치: `feat/integrated-course-suite`.

## 검증 결과

| 대상 | 실행과 확인 | 결과 |
| --- | --- | --- |
| 통합 교안 | day01~day04, 새 커널에서 위에서 아래로 실행 | 4권·67개 코드 셀 통과 |
| 코드 옆 동반 노트북 | courseware의 6권, 각각 새 커널 실행 | 18개 코드 셀 통과 |
| 의미 번호 | 4권의 제목·metadata·강사용 배분표 대조 | 13개 블록·63개 주제 일치 |
| 시간 배분 | 의미 번호별 배정 합계 | 매일 480분, 전체 1,920분 |
| 그림 | attachment 존재·원본 경로·그림 설명·범위 설명 검사 | 생성 이미지 8개 + 도식 16개 포함 |
| 자동 테스트 | 기존 환경/경로 테스트 + 새 캡스톤/화면 테스트 | 19개 통과 |
| 기본 캡스톤 | 승인·거절·근거 없음·잘못된 승인값·새 thread | 기대 경로 통과 |
| MCP | FastMCP in-memory 및 별도 Python 프로세스 stdio | 도구 발견·정상 호출·입력 오류 확인 |
| A2A | SDK 1.x Agent Card·JSON-RPC·Message, HTTPX ASGI | 출처 포함 응답 확인 |
| Streamlit | AppTest 질문/승인/거절 + Aside 실제 브라우저 | 조사→근거 확인→승인→보고서·검사 결과 표시 |
| 시각 검토 | HTML의 개념 그림·한국어 캡션, 캡스톤 도식·화면 | 문자·연결·설명 읽기 확인 |
| 파일 상태 | 출력 비움·로컬 링크·git diff --check | 확인 완료 |

1일차의 토큰 선택 예제는 낮은 확률 후보도 보이도록 난수 시드를 조정한 뒤 해당 노트북을 다시 실행했다. 경고 안내 문구도 보완했다. 학생용 파일에는 실행 결과를 저장하지 않았다.

## 재현 명령

프로젝트 루트에서 실행한다.

```bash
uv sync --extra notebooks
uv run --extra notebooks python tests/validate_lessons.py --execute --companions
uv run --extra notebooks python -m unittest discover -s tests -p 'test_*.py'
uv run --extra notebooks streamlit run src/courseware/app.py
```

검증 실행본·읽기용 HTML은 `docs/_build/lessons/`와 `docs/_build/courseware/`에 생성한다. 이 폴더는 Git 제외 대상이다. 원본 노트북과 생성 이미지는 저장소에 포함한다. HTML은 읽기용이며 실행은 VS Code의 `.ipynb`에서 한다.

## 버전과 관찰된 경고

`uv.lock`으로 설치 버전을 고정했다. 기존 패키지 버전의 변경은 없으며 노트북 extra에 필요한 패키지가 추가됐다.

- LangChain 1.4.2, LangGraph 1.2.12, FastMCP 3.4.7, A2A SDK 1.1.5.
- DeepAgents 0.7.18, Langfuse 4.15.4, Streamlit 1.64.0.
- nbclient 0.11.0, nbformat 5.11.1, ipykernel 7.3.0.
- 1.3.4는 원본의 RunnableWithMessageHistory와 InMemoryChatMessageHistory를 비교 학습하며 deprecation 경고가 발생한다. 새 구현은 2.2.4·3.4.2의 Checkpointer를 따른다. 경고의 의미를 본문에 표시했다.
- AppTest는 브라우저 서버 밖에서 실행되어 ScriptRunContext 경고를 출력할 수 있다. 실제 위젯 동작과 결과를 assertion으로 확인했다.
- A2A 1.1.5의 즉시 응답 정리 중 Dispatcher 경고가 별도 호출에서 관찰됐다. Card·Message의 결과 검사는 통과했다. 장기 Task·취소는 검증 범위에 포함하지 않는다.
- 커널 시작 시 로컬 TCP 연결에 대한 IPKernel 경고가 출력된다. 이는 셀 실패를 뜻하지 않으며 검증은 로컬 커널에서 수행했다.

## 실제 연결로 확인할 범위

기본 모드는 외부 API를 호출하지 않는다. 자료·모델 대역은 교육용이라고 표시한다. LangChain·LangGraph·MCP·A2A·Chroma·DeepAgents·Streamlit 자체는 실제 라이브러리를 실행했다.

### 사외 실제 연결 (2026-09-26)

`.env`(`LLM_PROVIDER=openai`, `EMBED_PROVIDER=openai`, `RAG_PROVIDER=mock`, `gpt-6-luna`, `text-embedding-3-small`)로 day01~day04를 `RUN_LIVE=True`, `ENABLE_LANGFUSE=True`로 바꾼 임시 사본에서 새 커널로 실행했다. 저장소의 노트북은 바꾸지 않았다.

| 대상 | 결과 |
| --- | --- |
| 텍스트 응답·LCEL 체인 (1.2, 1.3) | 한국어 응답 확인 |
| 도구 호출 Agent (create_agent, LangGraph ToolNode) | `multiply` 호출 → 42, 72 결과로 최종 답변 |
| 임베딩 (2.1) | 7개 청크, 1536차원 |
| DeepAgents Skill 읽기 | 보고서 Skill 규칙을 요약 |
| 구조화 출력 Judge | `JudgeResult` 반환. 근거에 없는 "교육 자료입니다."를 지적 |
| 캡스톤 승인·거절·근거 없음 | 실제 모델 Writer가 출처 ID를 붙여 작성. 거절·근거 없음 경로에서 Writer 미실행 |
| Langfuse | `auth_check` 통과, Trace 생성과 observation 5개 저장을 API로 조회 |

- `gpt-6` 계열은 langchain-openai 1.6.6에서 도구가 있으면 Responses API로 자동 전환된다. 이때 `content`가 dict 목록으로 출력되어 사내 경로(Chat Completions, 문자열)와 화면이 달랐다. `src/config/llm.py`에서 `use_responses_api=False`로 고정해 두 경로의 출력 형식을 맞췄다.
- Langfuse 실습 셀은 모의 모델을 기록하므로 "LLM model을 해석하지 못했다"는 경고가 출력된다. 기록 자체는 저장된다.

### 기존 실습 코드의 사외 실제 연결 (2026-09-26)

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

### 사내 API 설정 공통화

사내 LLM·임베딩·RAGaaS의 주소와 인증 헤더를 `src/config/samsung.py`의 `llm_config()`, `embedding_config()`, `ragaas_config()`로 모았다. `config/llm.py`·`embeddings.py`·`ragaas.py`와 `01_requests`·`02_openai`·`02_embeddings`(raw·solution, 옆 노트북 포함)가 이 함수를 쓴다. 헤더 이름과 값의 출처는 원본과 같다. 공통 임베딩은 `02_embeddings.py`와 같이 10개씩 나눠 요청한다.

### 사내 임베딩·RAGaaS 기준

사내 임베딩과 RAGaaS는 원본 교안 코드(최초 커밋 `addae97`)가 사내에서 동작한다고 보고, 현재 코드의 요청이 원본과 같은지 대조했다. 사내망 실행은 하지 않았다.

| 대상 | 원본과의 차이 | 처리 |
| --- | --- | --- |
| 임베딩 `config/embeddings.py` | 주소 `/v1/embeddings`, `x-dep-ticket` 헤더, `{"input": texts}` 동일. 필수값 검사·timeout 추가 | timeout을 120초로 설정 |
| RAGaaS `config/ragaas.py` | 주소·`x-dep-ticket`·`api-key` 헤더 동일. `json=` 전송은 `data=json.dumps()`와 같은 본문 | 원본에 없던 timeout 중 `insert-doc`은 300초로 설정 |
| `src/raw/.../05_ragaas.py` | 원본은 `rp-aicoa-meritz-pet` 인덱스를 코드에 고정. 개편본은 `index_name` 환경변수가 없으면 실패 | 원본 인덱스로 되돌림 |
| 캡스톤 정답 `rag_search` | 원본 요청의 `fields_exclude` 누락 | 원본 요청으로 되돌림 |
| 2.1.4 교안 셀 | 원본에 없는 요청 필드(`size`) 사용, 항상 mock | 원본 요청으로 바꾸고 `RUN_LIVE`와 `RAG_PROVIDER`를 따름 |

- 원본 정답본 `05_ragaas.py`·캡스톤은 `api-key` 헤더 없이 요청했다. 원본 실습본과 이 프로젝트 규칙(AGENTS.md 6절 5번)에 따라 두 헤더를 모두 보낸다.

아래는 아직 실행하지 않았다.

- 삼성 사내 LLM의 실제 응답과 도구 호출.
- 강의장 Windows PC의 설치, CodeMate UI, 사내 프록시·방화벽·컨플루언스 최신 과제.
- 기존 `src/raw/`·`src/solution/` 전체의 최신 SDK 이관.

실제 연결을 선택한 경우 오류를 자동으로 mock으로 바꾸지 않는다. 실행 조건은 [강사용 안내](INSTRUCTOR_GUIDE.md), 연결 구성은 [환경 설정](../src/config/)을 따른다.
