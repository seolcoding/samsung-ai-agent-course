# 동물보험 챗봇 8단계 실습 견본 앱

날것의 LLM API에서 시작해 한계(문서·사진·기억 없음, 지어내기)를 겪고, LangChain 부품·도구·LangGraph·RAG를 하나씩 붙여 에이전트까지 가는 실습 가이드 앱입니다. 단계마다 써 보고, 구조와 핵심 코드를 보고, CodeMate로 직접 만들어 비교합니다.

프로젝트 루트에서 실행합니다.

```bash
uv run --env-file .env streamlit run dev/demos/rag_evolution/app.py --server.address 127.0.0.1 --server.port 8505
```

## 화면 구성

모든 단계 페이지가 같은 틀입니다. 핵심만 펼쳐 두고 나머지는 접어 둡니다.

| 영역 | 내용 |
|---|---|
| 써 보기 (왼쪽) | 단계별 예시 질문 버튼과 채팅. 첫 예시는 모든 단계 공통 질문 |
| 핵심 (오른쪽 탭) | 구조 그림 · 핵심 코드(줄인 코드) · 만들어 보기(CodeMate 지시문과 성공 기준) |
| 심화 (아래, 접힘) | 실행 기록 · 근거 원문 · 이 앱의 실제 실행 코드 · 설정 · 더 알아보기 |

| 단계 | 바뀌는 것 | 대화 기억 |
|---|---|---|
| 1. 날것의 LLM API | OpenAI SDK로 질문만 보냄. 문서·사진·기억이 없음을 체험 | 없음 |
| 2. 프롬프트 템플릿 | ChatPromptTemplate으로 역할·형식 고정 | 없음 |
| 3. LCEL 체인 + 대화 기억 | `prompt \| llm \| parser`, MessagesPlaceholder로 이전 대화 전달 | history |
| 4. Tool Calling | 위키피디아·사진·합계·PDF 쪽 읽기 도구. 보험 질문은 쪽을 짐작하다 4쪽 한도에서 멈춤 | history |
| 5. LangGraph 기본 | 4단계 루프를 agent·tools 그래프로 | checkpointer |
| 6. Naive 벡터 RAG | 불러오기→나누기→임베딩·저장→검색→생성, [PDF N쪽] | history |
| 7. Advanced RAG | Query Rewrite + Hybrid(벡터+키워드, RRF) + Re-ranking | history |
| 8. 에이전틱 흐름 | researcher(RAG 검색 등 도구) → writer → reviewer, 최대 2회 재작성 | history |
| 9. 비교·자기채점 | 같은 질문의 1~8단계 결과를 나란히, 한 번에 실행 가능 | - |

## 실행 모드 (사이드바)

| 모드 | 동작 | 필요한 설정 이름 |
|---|---|---|
| 녹화 재생 | `data/recorded_runs.json`에 저장한 실제 실행 결과를 다시 보여 줌. 예시 질문만 가능 | 없음 |
| OpenAI 실행 | 실제 호출 | `OPENAI_API_KEY`, `OPENAI_MODEL`, 6~8단계는 `OPENAI_EMBEDDING_MODEL`도 |
| 사내 실행 | 실제 호출 | `api_base_url`, `model`, `credential_key`, `send_system_name`, `user_id`, `embedding_api_url`, `embedding_x_dep_ticket` |

`LLM_PROVIDER`·`EMBED_PROVIDER`·`COURSE_ENV`가 처음 선택을 정합니다. Streamlit Secrets를 먼저 읽고, 없으면 환경변수를 읽습니다. 인증 값은 화면·기록·녹화 파일에 넣지 않습니다.

녹화를 새로 만들려면(실제 API 호출, 비용 발생):

```bash
uv run --env-file .env python dev/demos/rag_evolution/tests/record_runs.py        # 1~8단계 전체
uv run --env-file .env python dev/demos/rag_evolution/tests/record_runs.py 4 5    # 일부 단계만
```

단계마다 예시 질문을 위에서부터 한 대화로 이어 녹화합니다. 예시 질문이나 프롬프트를 바꾸면 녹화를 다시 만들어야 합니다. `backend.py`·`lesson.py`를 고친 뒤에는 Streamlit 서버를 다시 시작해야 반영됩니다. `tests/test_stages.py`가 모든 예시 질문의 녹화가 있는지 검사합니다.

## 자료

보험 PDF는 2024년 제공 문서의 복사본입니다(`data/pdf_manifest.json`에 원본 경로·SHA-256). 쪽번호는 PDF의 물리적 쪽번호입니다. 위키피디아·Wikimedia 사진은 실시간 외부 조회입니다.

화면의 글(설명·예시 질문·핵심 코드·지시문·성공 기준)은 모두 `lesson.py`에서 고칩니다. 흐름은 [DESIGN.md](DESIGN.md), 검증은 [VALIDATION.md](VALIDATION.md)에 있습니다.
