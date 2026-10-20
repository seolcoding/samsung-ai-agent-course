# 4-3 교안 노트북 — 목차 (v1, 2026-09-28)

- **권 제목**: 캡스톤 프로젝트: 리서치 자동화 멀티 에이전트 시스템 (PDF 1쪽 제목)
- **원본 슬라이드**: `course/Chapter02/slides/day02/4-3-research-automation-multi-agent-system.pdf` (9쪽. 표지 p1, 장 표지 없음, 본문 p2–p9). 글만 있는 슬라이드이고 구조 그림이 없다.
  - p2 Multi-Agent 시스템 설계 / p3–4 Workflow 구성 / p5 MCP, RAGaaS 활용 / p6–7 Deep Agents와 Langfuse / p8–9 보고서 품질 평가
- **원본 코드**: `course/Chapter02/code/raw/06-capstone/`
  - `starter.py` (TODO **11개**. 지시에는 12개로 적혀 있었으나 `grep TODO` 결과 11개다. 받은 zip 원본은 10개이고, 개편 때 `rag_search`의 TODO 1개가 더해졌다)
  - `data/ai_trends.md`(24행), `data/llm_market.md`(35행) — 솔루션과 같다
  - 정답에만 있는 것: `solution.py`, `mcp_server.py`, `skills/researcher/SKILL.md`, `skills/ds-report-writer/SKILL.md`
- **커리큘럼**: 4일차 4.3 "캡스톤 프로젝트: 리서치 자동화 멀티 에이전트 시스템" 4.0H. "4일 학습요소 통합 구현 (자유 주제 혹은 스켈레톤 코드 기반 개발 중 선택)". 블록 안 시간 배분은 커리큘럼에 없다. 이 목차는 **LEC 20분 + 안내 노트북 둘러보기·준비 20분 + 개발·실행·정답 비교 약 200분**을 가정한다.
- **산출물**
  - `course/Chapter02/notebooks/4-3_capstone_LEC.ipynb` (슬라이드·설명·퀴즈)
  - `course/Chapter02/notebooks/4-3_capstone_LAB.ipynb` (안내 노트북. 코드 빈칸 없음)
  - `course/Chapter02/capstone/` (수강생이 AI와 함께 고치는 프로젝트 폴더)
- **빌더**: `build_lab.py`는 원본 `.py`를 셀로 넣는 구조라 이 권과 맞지 않는다. LEC는 다른 권처럼 `build_lecture_4_3.py` + `4-3_cells.json`, 안내 노트북도 같은 방식(nbkit)으로 만들고, `capstone/` 폴더는 원본에서 복사·patch하는 짧은 스크립트로 만드는 안을 제안한다(원본 `code/`는 건드리지 않는다).
- **실행 검증**: 이 목차 단계에서는 실행하지 않았다. `dev/docs/VALIDATION.md`에 사외 OpenAI로 `mcp_server.py` + `solution.py`를 실행해 보고서 작성, Judge 종합 0.95, Langfuse 기록을 확인한 기록이 있다. 아래 호출 수·시간은 코드 구조로 추정한 값이다.

## 1. LEC 목차

C 수준(슬라이드 요약 + 내용 있는 곳만 "왜 배우나") + 4지선다 퀴즈. 코드 셀 없음. 슬라이드 글이 짧아서 각 절은 "이 기능을 앞 단원 어디서 배웠나"를 이어 주는 설명이 중심이다(연결은 커리큘럼 3.2·3.4·4.1·4.2와 M1 2.2에 근거).

| # | 절 제목 | 슬라이드 | 핵심 메시지 (근거 쪽) | 왜 배우나 | 퀴즈 |
|---|---|---|---|---|---|
| 1 | 도입 | p1–2 | 리서치 자동화 보고서 작성 Multi-Agent 시스템을 만든다 (p2) | 4일 동안 배운 LangGraph·HITL·MCP·RAGaaS·Deep Agents·Langfuse를 한 프로그램에 모은다 | — |
| 2 | 전체 흐름 | p3 | ① 주제 입력 ② Supervisor가 Researcher 실행 결정 ③ Researcher가 웹 검색·RAGaaS·MCP 문서 검색으로 자료 수집 ④ 사용자가 리서치 결과 확인·작성 승인 ⑤ Writer가 초안 작성 ⑥ 최종 보고서 평가·출력 (p3) | 개발 단계(체크리스트)가 이 여섯 단계를 그대로 따른다 | 흐름 순서 문제: "사용자가 보고서 작성을 승인하는 시점은?" (리서치 결과 확인 뒤, Writer 실행 전) |
| 3 | Human-in-the-loop | p4 | 자동 실행 중간에 사용자 승인을 받는다. 리서치 결과를 먼저 보여 주고, 승인하면 Writer 단계로 재개, 승인하지 않으면 작업 중단 (p4) | M1 LangGraph에서 본 중단·재개를 실제 흐름에 넣는다 | 사용자가 승인하지 **않으면**? (작업 중단) |
| 4 | MCP와 RAGaaS | p5 | MCP 서버가 `data` 경로의 파일을 도구로 제공한다. RAGaaS는 사내 지식베이스 검색을 API로 쓴다(사내망에서 호출). Researcher는 웹 검색과 내부 문서 검색을 함께 쓴다 (p5) | 3-2 MCP 서버·클라이언트, M1 RAGaaS 호출을 한 Agent의 도구로 합친다 | Researcher가 자료를 모으는 경로가 **아닌** 것은? (보기: 웹 검색 / RAGaaS / MCP 문서 검색 / Writer의 초안) |
| 5 | Deep Agents | p6 | `create_deep_agent`로 전문 Agent 생성, `FilesystemBackend`로 Skill 파일 접근, Researcher Skill과 Writer Skill 분리, MemorySaver로 Agent별 실행 상태 유지 (p6) | 4-1 하네스를 Agent 두 개에 나눠 적용한다. 역할별로 규칙 문서를 따로 두는 이유(2-2 역할 분리)와 이어진다 | `FilesystemBackend`의 역할은? (Skill 파일 접근) |
| 6 | Langfuse | p7 | CallbackHandler로 모델 호출 추적, Researcher·Writer 실행 Trace 기록, LLM Judge 평가도 별도 Trace로 기록, 평가 점수를 Langfuse Score로 저장 (p7) | 4-2에서 본 추적·점수를 캡스톤 결과 확인에 그대로 쓴다 | 평가 점수를 저장하는 곳은? (Langfuse Score) |
| 7 | 보고서 품질 평가 | p8–9 | LLM Judge가 Relevance(주제 관련)·Faithfulness(리서치 근거 충실)·Completeness(구성 완성)·Clarity(문장·구조 명확)로 평가. 항목마다 0.0~1.0 점수와 채점 근거, 평균 점수, Langfuse Score 기록 (p8–9) | 내가 만든 보고서를 스스로 점검하는 기준이다 | "리서치 근거에 충실한가"를 보는 항목은? (Faithfulness) |
| 8 | 정리 퀴즈 | — | 여섯 단계와 각 기술의 역할 | — | 4지선다 3문항: ① 단계 ↔ 기술 짝짓기(자료 수집=MCP·RAGaaS, 승인=HITL, 규칙=Skill, 기록=Langfuse) ② 네 평가 항목 중 "구성 완성"에 해당하는 것 ③ 점수 범위(0.0~1.0) |

- 퀴즈는 모두 4지선다, 정답은 위 슬라이드 문구에서만 만든다. 수강생 글에는 쪽 표시를 넣지 않는다.
- **배점**: 슬라이드 9쪽 어디에도 배점이 없다. 슬라이드의 "평가 기준"은 LLM Judge의 보고서 평가 네 항목(p8–9)뿐이다. 배점 표는 받은 zip의 `06-capstone/README.md`(현재 `dev/docs/guides/capstone_student.md`)에만 있다 → 2.3절·5절 질문 1.

## 2. 안내 노트북 `4-3_capstone_LAB.ipynb` 목차

코드 빈칸 없음. 코드 셀은 준비 셀(접힘), 환경 확인, 구조도 그리기만 둔다. 실제 코드는 `capstone/` 폴더의 파일을 AI와 함께 고치고 터미널에서 실행한다. 수강생 글의 파일 이름·경로는 모두 인라인 코드나 코드 블록 안에 쓴다(QC의 "수강생 글" 파일 언급 검사가 인라인 코드·코드 블록은 뺀다).

| 장 | 제목 | 내용 |
|---|---|---|
| 1 | 캡스톤 소개 | 만들 것 한 문장(p2), 여섯 단계(p3). 조기 완료자·3일차 예고 때 이 장만 먼저 봐도 되게 짧게 쓴다(11차수 피드백 2.5: 캡스톤 미리 안내) |
| 2 | 주제 고르기 | **A. 스켈레톤**: 제공 주제 "생성형 AI가 바꾸는 소프트웨어 개발의 미래" + `data/`의 문서 2개 그대로. **B. 자유 주제**: 같은 구조에 주제 문장, `data/`의 md 문서, Writer skill 양식을 자기 업무에 맞게 바꾼다. 둘 다 아래 체크리스트를 똑같이 통과해야 한다 |
| 3 | 구조도 (그림) | p3 흐름 + 코드 구조를 SVG 한 장으로: `START → supervisor → researcher → supervisor → (⏸ 승인) → writer → supervisor → END`, researcher 옆에 도구 3종(search_web·rag_search·MCP 3종), 두 Agent 옆에 skill 폴더, 아래에 Judge → Langfuse Score. 외부 CDN 없이 인라인 SVG |
| 4 | 폴더 둘러보기 | `capstone/` 파일 표(3절 표와 같은 내용, 각 파일이 흐름의 어디인지) |
| 5 | 준비 | ① 환경 확인 셀(`check_env(["RAG_PROVIDER"])` + Langfuse 확인) ② 터미널 A에서 MCP 서버 켜기(명령 코드 블록) ③ 🟢/⛔ |
| 6 | 단계별 체크리스트 | 아래 2.1 표의 7단계. 단계마다: 할 일 / 🟢·⛔ / 프롬프트 힌트(3문장 이내) / 접힌 "정답 보기"(solution.py의 해당 부분) |
| 7 | 전체 실행 | 터미널 B 명령, 승인(y/n) 입력 방법, 결과 보는 곳(보고서, 점수 막대, Langfuse 대시보드) |
| 8 | 정답과 비교하기 | ① 각 단계 접힌 정답과 내 코드를 나란히 놓고 AI에게 "다른 점과 그 차이가 결과에 주는 영향"을 리뷰받기(고치지 말 것) ② Judge 점수 네 항목을 정답 실행 점수와 비교 ③ Langfuse에서 trace·score 확인 |
| 9 | 평가 기준 | 2.3절 결정에 따라 채운다 |

### 2.1 단계별 체크리스트 (`starter.py` TODO 11개를 7단계로 묶음)

행 번호는 `course/Chapter02/code/raw/06-capstone/starter.py` 기준. 힌트는 무엇을 알려 주면 되는지만 말하고 지시문 완성본은 주지 않는다.

| 단계 | 묶는 TODO | 🟢 되어야 하는 것 | ⛔ 다시 할 신호 | 프롬프트 힌트 (초안) |
|---|---|---|---|---|
| 0 준비 | — | 터미널 A에 MCP 서버 시작 문구가 나오고 명령이 끝나지 않고 기다린다. 환경 확인 셀에 RAG 방식(사내 samsung / 사외 mock)이 🟢로 나온다 | `address already in use` → 8001 포트를 다른 서버(3일차 A2A 서버)가 쓰고 있다. 그 터미널을 Ctrl+C로 끈다 | — |
| 1 도구 | 48 `# TODO: 사용할 도구를 정의`<br>58–59 `# TODO: post_ragaas('retrieve-rrf', payload)를 Coding AI에게 구현하게 하고 / RAG_PROVIDER=mock일 때 결과에 [MOCK RAGaaS]가 표시되는지 검토하세요.` | 두 도구가 문자열을 돌려준다. 사외에서는 Researcher 결과의 출처나 Langfuse의 도구 출력에 `[MOCK RAGaaS] 질문: …`이 보이고, 사내에서는 실제 문서 본문이 보인다 | `None`이 돌아온다(함수 끝에 return 없음) / `KeyError: 'hits'` / 사내에서 401 → `RAG_API_KEY`와 `api-key` 헤더 확인 | 도구가 무엇을 받아 어떤 문자열을 돌려줘야 하는지 먼저 말한다. RAGaaS 요청에 넣을 값(인덱스 이름, 검색어, 결과 개수)과 응답에서 꺼낼 필드를 AI에게 알려 준다. 응답 모양은 사외 모의 응답으로 직접 확인한다 |
| 2 State | 64 `# TODO: 필요한 필드를 추가하세요.` | State에 주제·리서치 결과·초안·다음 차례가 들어 있다(정답: `topic`, `research_result`, `draft`, `next`) | 실행 중 `KeyError: 'topic'` 등 | 노드들이 서로 넘겨받아야 하는 값을 흐름 순서대로 적어 AI에게 보여 준다 |
| 3 두 Agent + MCP 연결 | 107 `# TODO: 자료조사 skill을 가진 Researcher Agent`<br>114 `# TODO: 보고서 작성 skill을 가진 Writer Agent` | 실행 첫머리에 `MCP 도구 로드: ['list_docs', 'read_doc', 'search_docs']`(순서는 다를 수 있음)가 나온다. Researcher는 도구 5개, Writer는 도구 없이 skill만 쓴다 | 연결 오류 → MCP 서버를 먼저 켠다 / skill을 못 찾음 → `skills/` 폴더 경로 확인 / `await` 관련 오류 → 아래 4절 "구조 함정" | 각 Agent에 줄 도구와 skill 폴더, 역할 밖 일을 하지 않게 할 system prompt를 AI에게 알려 준다. MCP 도구는 서버에서 비동기로 받아 온다는 점도 함께 말한다 |
| 4 노드 | 123 `# TODO: Supervisor 노드 정의`<br>131 `# TODO: Researcher 노드 정의`<br>136 `# TODO: Writer 노드 정의` | Supervisor가 "리서치 전 → researcher, 리서치 후 → writer, 초안 후 → END"로 고른다. `🔍 Researcher 실행 중...`, `✍️  Writer 실행 중...`이 한 번씩 나온다 | 같은 Agent가 되풀이된다 → Supervisor가 보는 상황(리서치·초안 완료 여부)이 전달되는지 확인 | Supervisor에게 지금 상황을 어떤 정보로 알려 줄지, 세 선택지를 언제 고르는지 먼저 정리해 AI에게 준다. Researcher·Writer 노드는 Agent 결과의 마지막 메시지를 State의 어느 필드에 넣는지 말한다 |
| 5 그래프·승인 | 149 `# TODO: 그래프 조립`<br>(151 `app = builder.compile()`은 TODO 표시가 없지만 여기서 함께 고친다) | 리서치 결과가 출력된 뒤 `보고서 작성을 시작할까요? (y/n)`에서 멈춘다. `n`이면 `취소됐습니다.`로 끝난다 | 멈추지 않고 곧장 Writer까지 간다 → 컴파일에 체크포인터와 Writer 앞 중단 설정이 있는지 확인 | 노드 사이 연결(시작, Supervisor의 갈림길, 각 Agent 뒤 복귀)을 그림처럼 말로 적어 AI에게 준다. Writer 실행 전에 멈춰야 한다는 조건과 멈춘 상태를 기억할 장치가 필요하다는 점을 함께 말한다 |
| 6 실행·재개 | 164 `# TODO: app.invoke로 실행하고 단계접 진행 상황 출력` | `y` 입력 뒤 `[DS-AI-RPT v2.1]` 양식의 보고서가 나온다. TL;DR이 3줄이고 현황 분석에 표가 있다(writer skill 규칙) | 승인 뒤 아무것도 안 나온다 → 재개할 때 같은 thread_id와 빈 입력으로 이어 부르는지 확인 | 1단계 실행 → 결과 보여 주기 → 사용자 입력 → 재개의 순서를 AI에게 알려 준다. 재개 방법은 M1 HITL에서 본 방식과 같다고 말한다 |
| 7 평가 | 100 `# TODO: 평가를 진행하고 Langfuse에 점수를 기록` | 관련성·근거충실도·완성도·명확성 네 줄의 막대와 점수·근거, `종합 점수`가 나온다. Langfuse 대시보드에 Judge trace와 score 4개가 보인다 | 점수는 나오는데 Langfuse에 없다 → `LANGFUSE_*` 키 확인 / 점수가 모두 1.0 → Judge 지시에 엄격 채점 조건이 있는지 확인 | 네 평가 항목의 뜻과 점수 범위를 슬라이드 문장 그대로 AI에게 준다. 점수를 어느 trace에 어떤 이름으로 남길지 말한다 |

- 단계 1~5는 코드만 바꾸고, 전체 확인은 6·7단계 실행에서 한 번에 한다. 단계별 중간 실행 확인 방법은 5절 질문 3.
- 과제 기준(앞에서 안 배운 것을 내지 않는다): `create_deep_agent`·skills(4-1), MCP 클라이언트(3-2), `interrupt_before`·재개(M1 2-1 HITL), Supervisor 구조화 출력(M1 2-2), `CallbackHandler`·`last_trace_id`·`create_score`(4-2 `04_evaluation.py`), `post_ragaas`(M1 RAGaaS) 모두 앞에서 다뤘다.

### 2.2 `course/Chapter02/capstone/` 폴더 구성

| 파일 | 가져오는 곳 | 손볼 점(복사본에서만) |
|---|---|---|
| `starter.py` | raw `starter.py` | docstring 11–13행의 raw/solution 경로 안내를 이 폴더 실행 명령으로 바꾼다. 164행 오타 "단계접" → "단계별". 쓰지 않는 import(`json`, `requests`)와 92–94행 쓰지 않는 변수 정리. 구조 함정 처리 여부는 5절 질문 2 |
| `mcp_server.py` | solution `mcp_server.py` | docstring 6–7행 실행 명령을 `uv run --env-file .env python course/Chapter02/capstone/mcp_server.py`로. 포트는 4절 제안에 따름 |
| `skills/researcher/SKILL.md` | solution | 그대로 (frontmatter 이름은 `research`, 폴더 이름은 `researcher`. 동작에는 영향 없음) |
| `skills/ds-report-writer/SKILL.md` | solution | 그대로 |
| `data/ai_trends.md`, `data/llm_market.md` | raw (solution과 같음) | 그대로 |
| `README.md` | 새로 씀 | 아래 요지 |

`README.md` 요지(짧게, 노트북 없이 폴더만 열어도 시작할 수 있게):
1. 만들 것 한 문장 + 여섯 단계(슬라이드 p3 문구)
2. 파일 표(위 표의 파일·역할)
3. 실행 순서: 터미널 A `uv run --env-file .env python course/Chapter02/capstone/mcp_server.py` → 터미널 B `uv run --env-file .env python course/Chapter02/capstone/starter.py` → 리서치 결과 확인 후 `y`/`n`
4. 사내/사외: `.env`의 `COURSE_ENV=samsung`이면 사내 RAGaaS(`index_name`, `RAG_API_KEY` 필요), `out`이면 모의 응답 `[MOCK RAGaaS]`
5. 단계 체크리스트 이름 7개(자세한 내용은 안내 노트북) — 파일 이름으로 가리키지 않고 "4-3 캡스톤 안내"로만 적는다
6. 자주 막히는 곳 3줄: 8001 포트 사용 중, MCP 서버 먼저, Langfuse 키
- README에 정답 경로(`code/solution/`)는 적지 않는다. 정답은 안내 노트북의 접힌 "정답 보기"로만 준다.

### 2.3 평가 기준 — 무엇을 옮길 수 있나

| 출처 | 내용 | 현재 코드와 맞나 |
|---|---|---|
| 슬라이드 p8–9 (정본) | 보고서 평가 4항목: Relevance, Faithfulness, Completeness, Clarity. 각 0.0~1.0, 항목별 근거, 평균, Langfuse Score | 맞다(solution `evaluate_report`) |
| 받은 zip `06-capstone/README.md` | 배점: Supervisor 라우팅 30 / HITL 25 / MCP 도구 연동 20 / **Streamlit UI 15** / skills.md 규칙 반영 10 | 어긋난다. 흐름이 "Writer 뒤 승인", 라우팅 값이 `FINISH`·`approval`이고, Streamlit UI를 요구한다. 현재 슬라이드·코드는 "Writer 앞 승인", `END`, UI 없음(터미널 `input()`) |
| 커리큘럼 4.3 | 통합 아키텍처·SKILL.md·MCP·`interrupt_before`·LLM Judge와 Langfuse 점수. Streamlit 언급 없음 | 맞다 |

- **Streamlit UI 배점 요구 여부**: 슬라이드(9쪽)와 커리큘럼 4.3 모두 Streamlit을 요구하지 않는다. 요구하는 곳은 받은 zip의 README 배점 표뿐이며 solution에도 UI가 없다. 제안: 안내 노트북 9장은 슬라이드 평가 4항목 + 체크리스트 7단계 통과 여부로 쓰고, README 배점 표는 옮기지 않는다. Streamlit은 조기 완료자 선택 과제로 한 줄만 둔다(`input()` 승인 흐름을 화면 버튼으로 바꿔야 해서 필수로 두기엔 크다). → 5절 질문 1.

## 3. 원본·솔루션 차이와 고른 쪽

| 파일 | 차이 | 고른 쪽 | 이유 |
|---|---|---|---|
| `starter.py` ↔ `solution.py` 구조 | starter는 Agent 생성(104–114행)과 그래프 컴파일(151행)이 **모듈 맨 위**에 있다. solution은 MCP 도구를 `await mcp_client.get_tools()`로 받아야 해서 Agent 생성·노드·그래프를 모두 `main()` 안에 둔다 | 정답 보기는 **solution** 구조 | starter 자리대로 채우면 MCP 도구를 넣을 수 없다(4절 구조 함정) |
| `starter.py` `evaluate_report` | 92–94행에 쓰지 않는 `langfuse`, `langfuse_handler`, `langfuse_config`가 있다. solution은 인자로 받은 `langfuse_client`를 쓴다 | **solution** | 쓰지 않는 변수가 수강생을 헷갈리게 한다 |
| `starter.py` import | 쓰지 않는 `json`, `requests`. `import config` 줄 없음(`from config.llm import`가 같은 일을 하므로 동작 차이 없음) | 복사본에서 정리 | 가독성 |
| `starter.py` 164행 | 오타 "단계접" | 고침 | — |
| `search_web` | starter는 본문 없음(→ `None`). solution은 고정 문자열 4줄을 돌려주는 가짜 검색 | solution | 정답 보기에 "검색은 흉내만 낸다"를 적는다 |
| `rag_search` | solution은 `RAG_PROVIDER=mock`이면 `index_name`이 없어도 `mock-capstone`을 쓴다. VALIDATION 기록대로 원본 요청의 `fields_exclude`를 되살렸다 | solution | — |
| `mcp_server.py`, `skills/` | raw에 없음(AGENTS.md 7절 알려진 결함, 배점 20점 항목) | solution에서 `capstone/`으로 복사 | 사용자 결정 |
| `data/` | 차이 없음 | raw | — |
| 받은 README(배점) | 슬라이드·코드와 흐름이 다름 | 슬라이드 | 2.3절 |

## 4. 실행 제약·위험과 처리 제안

| 항목 | 내용 | 처리 제안 |
|---|---|---|
| **8001 포트 충돌** | `mcp_server.py`(SSE, `0.0.0.0:8001`)와 3-3 A2A 서버(`01_a2a_server.py`, 8001)가 같은 포트다. VALIDATION에도 "두 서버를 동시에 띄우지 않는다"로 기록됨. 3-2 MCP 실습 서버는 8000 | 제안 A(기본): 포트는 그대로 두고, 준비 단계 ⛔와 README "자주 막히는 곳"에 `address already in use` → A2A 서버 터미널 Ctrl+C를 적는다. 제안 B: `capstone/` 복사본만 8002로 바꾸고 클라이언트 URL도 바꾼다(정답 보기 코드도 같이). 원본 solution과 숫자가 달라지는 대가가 있다 → 질문 4 |
| **사외 RAGaaS 모의 응답** | 코드로 확인(실행은 안 함): `COURSE_ENV=out` → `config/__init__.py`가 `RAG_PROVIDER=mock`을 채움 → `post_ragaas('retrieve-rrf', …)`가 네트워크 없이 `{"hits":{"hits":[{"_source":{"merge_title_content":"[MOCK RAGaaS] 질문: <검색어>. 이 문장은 API 요청·응답 흐름을 연습하기 위한 모의 자료이며 실제 사내 문서나 보험 약관의 내용이 아닙니다."}}]}}`를 돌려줌 → solution `rag_search`는 이 한 문장을 돌려준다. 키·인덱스 없이 동작 | 1단계 🟢에 `[MOCK RAGaaS]` 표시를 적는다. 모의 문장에 "보험 약관"이 들어 있어 보고서에 섞일 수 있음을 강사 메모에 적는다 |
| 사내 RAGaaS 인덱스 | `.env.sample`의 `index_name=rp-aicoa-meritz-pet`(펫보험 약관)이 캡스톤 주제(AI 트렌드)와 맞지 않는다. 검색 결과가 주제와 무관하면 Faithfulness·Relevance 판단이 흔들릴 수 있다 | 캡스톤용 사내 인덱스가 있는지 확인 목록에 올린다 |
| **구조 함정** | starter의 TODO 107·114가 모듈 맨 위에 있어, 그 자리에서 Agent를 만들면 비동기로 받아야 하는 MCP 도구를 넣을 수 없다. 151행 `compile()`에도 TODO 없이 체크포인터·중단 설정이 빠져 있다 | 3단계 힌트에 "MCP 도구는 비동기로 받아 온다"를 넣어 AI가 `main()` 안으로 옮기게 유도. 또는 복사본 starter를 solution 배치(main 안)로 바꿔 둔다 → 질문 2 |
| HITL 입력 | `input()`으로 y/n을 받는다. 노트북이 아니라 터미널 실행이라 문제 없음 | 7장에 "터미널에 y 입력 후 Enter" |
| Langfuse | `get_client()`·`CallbackHandler`가 `LANGFUSE_*` 키를 쓴다. 키가 없을 때 `last_trace_id`·`create_score` 동작은 **미확인** | 준비 단계에서 `config.check --langfuse`로 확인. 키 없이 실행 시 동작은 제작 단계에서 확인 |
| 사내 게이트웨이 | Supervisor·Judge의 `with_structured_output`, Deep Agent의 도구 호출이 모두 사내에서 **미검증** | 강의장 사전 확인 목록 |
| 실행 시간 | 한 번 실행에 LLM 약 10~15회(Supervisor 3, Researcher 도구 3회 이상 + 정리, Writer 1~2, Judge 1) 추정. 몇 분 걸림 | 제작 단계에서 실측해 강사 메모에 적는다 |
| Agent 파일 쓰기 | `FilesystemBackend(root_dir=capstone 폴더)`라 Deep Agent 기본 파일 도구로 이 폴더의 파일을 읽고 쓸 수 있다 | 강사 메모에 한 줄. 코드는 그대로 |
| 수강생 글의 파일 언급 | 안내 노트북은 `capstone/` 파일을 가리켜야 한다. QC는 인라인 코드·코드 블록 안의 파일 이름을 검사에서 뺀다 | 파일 이름·명령은 모두 인라인 코드·코드 블록으로 쓴다 |
| 11차수 피드백 | 캡스톤 시간 부족, 초반 예고 요청(2.5), 뒷자리 Langfuse 화면 안 보임 | 안내 노트북 1·2장을 3일차 예고에도 쓸 수 있게 짧게. Langfuse 확인은 수강생 각자 화면에서 |

## 5. 확인이 필요한 질문

1. 배점: 슬라이드에는 배점이 없고, 받은 zip README의 배점(Streamlit UI 15점 포함)은 현재 슬라이드·코드와 흐름이 다릅니다. 슬라이드 평가 4항목 + 체크리스트로 갈까요, 컨플루언스의 최신 배점이 따로 있나요?
2. 복사본 `starter.py`를 solution처럼 `main()` 안 배치로 바꿔 둘까요, 원본 배치 그대로 두고 힌트로 유도할까요?
3. 단계 1~5를 중간에 실행해 볼 방법(예: 단계별 확인 명령)을 둘까요, 6·7단계 전체 실행에서 한 번에 확인할까요?
4. MCP 서버 포트는 8001 그대로 두고 안내만 할까요, `capstone/` 복사본만 8002로 바꿀까요?
