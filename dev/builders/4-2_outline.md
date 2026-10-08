# 4-2 교안 노트북 — 목차 (v1, 2026-09-28)

- **권 제목**: Langfuse 기반 Observability & Evaluation (PDF 1쪽 제목)
- **원본 슬라이드**: `course/Chapter02/slides/day02/4-2-langfuse-observability-and-evaluation.pdf` (13쪽. 표지 p1, 목차 p2, 장 표지 p3 "Langfuse"·p9 "Evaluation", 본문 9쪽)
- **원본 코드**: `course/Chapter02/code/raw/05-observability/` 5개. raw에도 TODO 아래 정답이 채워져 있다(의도된 배포 상태)
  - `01_tracing_basic.py` (TODO 2개)
  - `02_tracing_langgraph.py` (TODO 1개)
  - `03_observe_decorator.py` (TODO 없음)
  - `04_evaluation.py` (TODO 없음, `# ──` 구획 3개: 규칙 기반 / LLM-as-a-Judge / 수동 평가)
  - `05_rag_evaluation_extra.py` (TODO 없음, 파일 이름에 "Extra")
- **커리큘럼**: 4일차 4.2 "Observability & Evaluation (Langfuse)" 2.0H. 이 목차는 **LEC 35분 + LAB 85분**을 가정한다(슬라이드 본문이 9쪽으로 짧고, 커리큘럼 [실습] 항목이 대시보드 확인이라 LAB에 시간을 더 준다). 커리큘럼 근거가 있는 배분은 아니다.
- **산출물**: `course/Chapter02/notebooks/4-2_observability_LEC.ipynb`, `course/Chapter02/notebooks/4-2_observability_LAB.ipynb` (`build_lab.py` UNITS에 `"05-observability": ("4-2", "observability")` 등록됨. spec `dev/builders/labs/Chapter02/05-observability.json`은 아직 없음)
- **실행 검증**: 이 목차 단계에서는 코드를 실행하지 않았다. `dev/docs/VALIDATION.md`에 solution 01~05가 사외 OpenAI + Langfuse로 정상 기록됐다는 기록이 있다. 호출 수·시간은 코드 구조로 추정한 값이다.
- **Langfuse 서버**: 받은 코드 주석과 `.env.sample`은 클라우드 주소(`jp.cloud.langfuse.com`)다. 준비는 강사 맥의 self-host(`infra/langfuse/`) 기준이며 코드는 그대로 두고 `.env`의 `LANGFUSE_BASE_URL`과 키만 바꾼다. 설치 버전 langfuse 4.15.4.

## 1. LEC 목차

슬라이드 PDF.js + C 수준 설명(슬라이드 요약, 내용 있는 곳만 "왜 배우나") + 4지선다 퀴즈. 코드 셀 없음.

| # | 절 제목 | 슬라이드 | 핵심 메시지 (근거 쪽) | 왜 배우나 | 퀴즈 |
|---|---|---|---|---|---|
| 1 | 도입 | p1–2 | 두 장: Langfuse(Trace, CallbackHandler, @observe) → Evaluation(Rule-based, LLM-as-a-Judge) (p2) | — | — |
| 2 | Langfuse란 | p3–4 | LLM 애플리케이션을 관찰·평가하는 오픈소스 Observability 플랫폼. 프롬프트·모델 호출·도구 호출·지연시간·비용·오류를 Trace 단위로 기록한다. LangChain·LangGraph·OpenAI SDK·Python SDK와 연동하고, 클라우드 또는 Docker Compose로 자체 설치할 수 있다 (p4) | — | Langfuse가 Trace 단위로 기록하는 것이 **아닌** 것은? (프롬프트 / 지연시간 / 비용 / 수강생 PC 사양 같은 오답) |
| 3 | 왜 추적하나 | p5 | 같은 입력처럼 보여도 내부 경로가 달라진다. 실제 전달된 프롬프트, 호출된 도구와 입력, 지연·비용이 생긴 단계, 실패가 모델·컨텍스트·도구 중 어디 문제인지를 확인해야 한다. Trace는 "감으로 추측하지 않고 실행 기록으로 확인"하게 한다 (p5) | M1에서 만든 RAG·LangGraph Agent는 print로만 봤다. 답이 틀렸을 때 어느 단계 탓인지 가르는 도구가 필요하다 | 실패한 응답에서 Trace로 가려내려는 원인으로 슬라이드에 **없는** 것은? |
| 4 | Trace | p6 | 실행 과정을 단계별로 기록한 데이터: 프롬프트 입력, 모델 호출, 도구 호출, LangGraph 노드 실행, 각 단계의 입력·출력·지연시간·오류. 하나의 요청이 내부에서 어떻게 처리됐는지 재구성한다 (p6) | — | Trace를 보면 알 수 있는 것은? |
| 5 | CallbackHandler | p7 | LangChain·LangGraph 실행 이벤트를 Langfuse로 보내는 연결 지점. Chain·Runnable·Tool·LLM 호출을 자동 수집한다. `config`의 `callbacks`로 전달하거나, `with_config`로 기본 설정으로 붙인다 (p7) | 실습 첫 두 장의 빈칸이 바로 이 연결이다 | CallbackHandler를 체인에 전달하는 방법으로 알맞은 것은? (`config={"callbacks": [...]}`) |
| 6 | @observe | p8 | 일반 Python 함수를 Trace 또는 Span으로 기록하는 데코레이터. LangChain 밖의 검색·후처리·평가·파일 생성도 같은 요청 안에서 LLM 호출과 함께 볼 수 있다 (p8) | RAG의 검색 단계처럼 체인 밖에 있는 코드는 CallbackHandler만으로는 보이지 않는다 | CallbackHandler 대신 @observe가 필요한 경우는? |
| 7 | Evaluation | p9–10 | 트레이싱만으로는 답변 품질을 알 수 없다. 응답의 좋고 나쁨을 Score로 남기면 품질 추세를 정량적으로 본다. Observability는 실행 기록, Evaluation은 결과 품질을 수치와 근거로 남긴다 (p10) | — | Observability와 Evaluation의 차이를 바르게 말한 것은? |
| 8 | Rule-based Evaluation | p11 | 코드로 명확히 판단할 조건(예시 포함, 키워드 포함, 답변 길이)을 본다. 단순하지만 안정적이고, 빠르고 저렴하며, 재현성이 높다. 정성적 품질 판단에는 한계가 있다 (p11) | — | 규칙 기반 평가의 한계로 알맞은 것은? |
| 9 | LLM-as-a-Judge | p12–13 | 별도 LLM이 유용성·관련성·근거 충실성·완성도를 평가한다. 규칙으로 판단하기 어려운 정성적 품질에 쓴다. 평가 기준을 구체적으로 쓰고, 점수 범위를 고정해 근거 없는 높은 점수를 막고, 가능하면 규칙 기반과 함께 쓴다 (p12, p13) | 4-3 캡스톤의 "최종 보고서 자동 평가(LLM Judge)와 Langfuse 점수 기록"이 이 방식이다(커리큘럼 4.3) | LLM Judge를 쓸 때 슬라이드가 권하는 것이 **아닌** 것은? |
| 10 | 정리 퀴즈 | — | 두 장의 핵심 | — | 4지선다 3문항: ① 상황 → 도구 짝짓기(체인 호출 추적 = CallbackHandler / 체인 밖 함수 = @observe) ② 상황 → 평가 방식(키워드 포함 = 규칙 / 설명의 완성도 = LLM Judge) ③ Trace와 Score가 각각 남기는 것 |

- 퀴즈는 모두 4지선다. 정답은 슬라이드 문구에서만 만든다.
- 커리큘럼 4.2의 "에이전트 활용 소개: Moody's와 Salesforce 사 예시"는 **슬라이드·코드 어디에도 없다.** 절을 만들지 않았다(5절 질문 1).
- 커리큘럼의 "사용자 피드백" 평가와 "다차원 점수화(정확성/관련성/완성도)"는 슬라이드에 없고 코드에만 있다(04 셋째 구획, 05). LEC에서는 다루지 않고 LAB에서 코드로 설명한다.
- 강사용 메모: 슬라이드 p7의 `"Langfuse가 뭐야?"` 예시, p11의 `has_sources`는 요약 예시다. 실제 실습 코드의 규칙은 `has_example`(키워드 목록)이다.

## 2. LAB 목차

첫 구획(접힌 준비 셀) → 보이는 코드 셀. 셀은 위에서부터 차례로 실행한다. 모든 장의 성공 기준에 **Langfuse 화면 확인**이 들어간다. 실행 결과(print)는 콜백을 붙였든 안 붙였든 똑같이 보이므로, 이 권에서는 대시보드가 유일한 판단 근거다.

| 장 | 원본 | 구분 | CHANGE_HERE 후보 / WRITE_HERE로 바꿀 TODO | 성공 기준 초안 | 실행 제약 |
|---|---|---|---|---|---|
| 1 | (환경 확인) | — | — | 🟢 `check_env(["LANGFUSE"])`가 준비 완료를 출력한다 (4절 "키가 틀려도 조용히 넘어감" 처리 제안 참고) | 공통 셀 + Langfuse 점검 |
| 2 | `01_tracing_basic.py` | **과제** (2곳) | ① 43행 `# TODO: chain.invoke를 호출하면서, config의 callback으로 \`langfuse_handler\`를 전달하세요.` → 빈칸 44–47행 `result = chain.invoke(…, config={'callbacks': [langfuse_handler]})`<br>② 58행 같은 TODO → 빈칸 59행 `answer = chain.invoke(q, config={'callbacks': [langfuse_handler]})` | 🟢 셀 출력에 답변 1개와 Q/A 2쌍이 나오고 끝에 `Tracing에서 확인`이 찍힌다<br>🟢 Langfuse 화면 Tracing 목록에 새 trace가 **3개** 생겼다. 하나를 열면 프롬프트 → 모델 호출 → 출력 파서 단계와 입력·출력·지연시간이 보인다<br>⛔ 셀은 정상인데 새 trace가 없거나 1개뿐이다 → `callbacks`를 두 곳 모두 넘겼는지 확인한다 | LLM 3회, 약 10~20초. 서버 불필요(Langfuse 서버만 필요) |
| 3 | `02_tracing_langgraph.py` | **과제** (1곳) | 60행 `# TODO: 그래프를 컴파일 하면서, with_config 메서드를 통해 callback으로 \`langfuse_handler\`를 전달하세요.` → 빈칸 61행 `app = builder.compile().with_config({'callbacks': [langfuse_handler]})` | 🟢 Q/A 2쌍이 나오고 답에 날씨(예: `맑음 23°C`)가 들어 있다<br>🟢 Tracing에 새 trace 2개. "부산이랑 제주" trace를 열면 agent → tools(get_weather) → agent 노드 순서가 보인다<br>⛔ 답은 나오는데 새 trace가 없다 → `invoke`가 아니라 **그래프**에 콜백을 붙였는지 확인한다 | LLM 약 4~6회, 약 20~40초. `bind_tools` 사용(사내 게이트웨이는 M1 2-1과 같은 조건) |
| 4 | `03_observe_decorator.py` | **예제** + AI에게 물어보기 | CHANGE_HERE: 31행 `@observe(name='retrieve-documents')` (이름을 바꿔 대시보드 트리에 바뀐 이름이 보이는지 확인)<br>물어보기: `rag_pipeline`을 붙여 넣고 "60–63행에서 `callbacks`를 빼면 trace 트리가 어떻게 달라지는가"를 설명받기(고치지 말 것) | 🟢 Q/A 2쌍이 나온다<br>🟢 Tracing의 새 trace를 열면 `rag-pipeline` 아래에 `retrieve-documents`(바꾼 이름), `format-context`, LLM 호출이 자식으로 보인다<br>🟢 (물어보기) LLM 호출이 트리에서 빠지고 @observe 함수만 남는다는 점을 짚었다<br>⛔ trace가 `rag-pipeline` 하나만 있고 자식이 없다 → 셀을 처음부터 다시 실행한다 | LLM 2회, 약 10초 |
| 5 | `04_evaluation.py` 구획 1 "규칙 기반 평가" | **예제** + AI에게 물어보기 | CHANGE_HERE: 32행(`run_chain` 안) `('system', '한국어로 간결하게 답변하세요. 반드시 예시를 포함하세요.'),` (뒤 문장을 지워 `has-example` 점수가 바뀌는지 본다)<br>물어보기: 50행 `has_example = any(keyword in answer1 for keyword in ['예:', '예를 들어', '예시', '[', '('])`를 붙여 넣고 "이 규칙이 예시 없는 답도 1.0으로 볼 수 있는가"를 리뷰받기 | 🟢 `예시 포함 여부: ✓ (score=1.0)` 같은 줄이 나온다<br>🟢 Langfuse의 해당 trace(또는 Scores 화면)에 `has-example` 점수와 코멘트 "예시 포함 여부 자동 검사"가 보인다<br>🟢 (물어보기) `'('`·`'['`는 괄호만 있어도 참이 되어 규칙이 느슨하다는 점을 짚었다<br>⛔ 점수가 화면에 없다 → 이 구획 끝까지 실행한 뒤 마지막 장의 `flush` 셀을 실행한다(4절) | LLM 1회. 구획을 나눠도 `run_chain`·`langfuse`는 앞 셀에서 정의되므로 순서대로 실행해야 한다 |
| 6 | `04_evaluation.py` 구획 2 "LLM-as-a-Judge" | **예제** + AI에게 물어보기 | CHANGE_HERE: 72행 judge 시스템 프롬프트 `('system', '아래 답변의 품질을 0.0~1.0 사이 숫자 하나만 출력하세요. 다른 텍스트는 출력하지 마세요.'),` (평가 기준 한 가지를 넣어 점수가 달라지는지 본다. 슬라이드 p13 "평가 기준을 구체적으로")<br>물어보기: 78–82행을 붙여 넣고 "Judge가 숫자가 아닌 글을 돌려주면 어떤 점수가 기록되는가"를 리뷰받기 | 🟢 `LLM 채점 점수: 0.x`가 나온다<br>🟢 Langfuse의 해당 trace에 `llm-judge-quality` 점수와 "LLM 자동 채점: …" 코멘트가 보인다<br>🟢 (물어보기) 변환 실패 시 조용히 0.5가 기록된다는 점을 짚었다<br>⛔ 점수가 정확히 0.5이고 코멘트에 숫자가 아닌 글이 있다 → Judge 프롬프트를 다시 본다 | LLM 2회(답변 1 + Judge 1). Judge 호출은 콜백을 넘기지 않아 trace가 따로 생기지 않는다(원본 의도) |
| 7 | `04_evaluation.py` 구획 3 "수동 평가 시뮬레이션" + `flush` | **예제** | CHANGE_HERE: 105행 `user_feedback = 1.0` (0.0으로 바꿔 👎를 기록) | 🟢 `사용자 평가: 👍 (score=…)`가 나오고 마지막 줄 `✓ 대시보드 [Scores] 탭에서 평가 결과를 확인하세요.`가 찍힌다<br>🟢 Langfuse Scores 화면에 `has-example`, `llm-judge-quality`, `user-feedback` 세 이름의 점수가 보인다<br>⛔ 세 점수 중 빠진 것이 있다 → 해당 구획 셀을 다시 실행하고 이 셀을 다시 실행한다 | LLM 1회. 출력 문구는 "👍" 고정이라 0.0으로 바꿔도 화면 글자는 그대로다(강사 메모) |
| 8 | `05_rag_evaluation_extra.py` | **예제** (배치는 5절 질문 2) | CHANGE_HERE: 122행 `'doc_key': 'noise',       # 날씨 문서 → 완전히 엉뚱함` (`'rag'`로 바꿔 CASE C의 정확성이 오르는지 본다) | 🟢 CASE A·B·C마다 `채점 → 정확성: … \| 관련성: … \| 완성도: …`와 `근거:` 줄이 나온다<br>🟢 CASE A 점수가 B·C보다 높다(LLM 판단이라 숫자는 매번 다르다)<br>🟢 Langfuse의 각 trace에 `correctness`·`relevance`·`completeness` 세 점수가 붙어 있고, 트리에 `rag-pipeline` → `retrieve`·`generate`가 보인다<br>⛔ 세 케이스 점수가 모두 같다 → CHANGE_HERE 줄과 Judge 응답을 다시 본다 | LLM 6회(생성 3 + Judge 3), 약 30초~1분. `with_structured_output`(EvalScore) 사용 — 사내 게이트웨이 미검증 |
| 9 | 정리 | — | — | — | — |

- **예제/과제 기준**: TODO는 01의 두 곳, 02의 한 곳뿐이다. 콜백 전달(`config={"callbacks": [...]}`, `with_config`)은 이 권 LEC 5절(슬라이드 p7)에 코드 그대로 나오므로 **과제**로 낸다. LangGraph 그래프·ToolNode·`tools_condition`은 M1 2-1에서 배웠다. 03~05는 TODO가 없어 **예제 + AI에게 물어보기**.
- **04를 구획 3개로 나눈다**: 원본에 `# ──` 구획 머리가 있어 빌더가 그대로 자를 수 있다. 커리큘럼의 평가 방법 3가지(규칙 기반, 사용자 피드백, LLM-as-a-Judge)가 장 하나씩에 대응한다. 원본 순서(규칙 → Judge → 수동)를 따른다.
- **flush**: 원본 다섯 파일 모두 마지막에 `langfuse.flush()`가 있다. 노트북에서도 각 장의 마지막 셀에 그대로 둔다(4절).
- 합계: LAB 본문 7장(과제 2장 = 빈칸 3곳, 예제 5장 = CHANGE_HERE 6곳 + 물어보기 3개).

## 3. 원본·솔루션 차이와 고른 쪽

| 파일 | 차이 | 고른 쪽 | 이유 |
|---|---|---|---|
| `01`~`03`, `05` | docstring의 "실행:" 경로 한 줄(`raw/` ↔ `solution/`)뿐 | raw | TODO 주석이 raw·solution 모두 있고 코드가 같다. docstring은 노트북에 넣지 않는다(4절 "받은 주석의 클라우드 주소·경로") |
| `04_evaluation.py` | raw 102–104행에 이전 강사 메모 주석 3줄("랜덤한 상황에 에이전트 2개를 병렬적으로 실행한 결과를…")이 있고 들여쓰기가 어긋나 있다. solution에는 없다 | **solution** | 메모 내용이 코드와 관계없고(병렬 실행·승인 대기는 이 코드에 없음) 들여쓰기가 어긋나 읽기 어렵다 |

그 밖에 raw·solution 공통으로 손볼 것(노트북 spec의 `patch`로만, 원본은 그대로):

| 파일·행 | 내용 | 제안 |
|---|---|---|
| `01` 1–18행 docstring | `cloud.langfuse.com`에서 키 발급, `LANGFUSE_BASE_URL=https://jp.cloud.langfuse.com`, `.py` 실행 경로 | 노트북에서는 docstring을 빼고 장 설명 마크다운에 "핵심 개념"만 옮긴다. 수강생 글에 파일 경로·클라우드 주소를 쓰지 않는다 |
| `04` 46행 주석 | `# get_trace_id(): 직전 invoke에서…` — 코드는 `handler1.last_trace_id`를 쓴다 | 주석을 `# last_trace_id: 직전 invoke에서 생성된 trace의 ID`로 patch. 주석과 코드가 다르면 AI 리뷰 때 혼란을 준다 |

## 4. 실행 제약·위험과 처리 제안

| 항목 | 내용 | 노트북 처리 제안 |
|---|---|---|
| flush | langfuse 4.15.4는 이벤트를 모아 두었다가 보낸다(기본 5초 간격, 512개 단위). 스크립트는 곧 종료되므로 `flush()`가 없으면 누락된다. 노트북은 커널이 살아 있어 몇 초 뒤 전송되지만, 바로 대시보드를 보면 trace·score가 아직 없을 수 있다 | 원본대로 각 장 마지막에 `langfuse.flush()`를 둔다. 성공 기준 ⛔에 "flush 셀 실행 후 화면 새로고침"을 적는다. `shutdown()`은 부르지 않는다(이후 장에서 클라이언트를 다시 써야 함) |
| 키가 틀려도 조용히 넘어감 | 키가 비었거나 틀리면 Langfuse는 경고만 내고 코드는 정상 실행된다. print 결과가 똑같아 "조용히 틀린 데모"가 된다. `check_env(["LANGFUSE"])`는 키 **이름**만 본다 | 준비 셀에서 `get_client().auth_check()`를 한 번 불러 연결까지 확인한다(🟢/⛔ 출력). 빌더 공통 셀 변경이 필요하므로 제작 단계에서 결정 |
| 셀 사이 공유 객체 | `get_client()`는 한 커널에서 같은 객체를 돌려준다. 장마다 `CallbackHandler()`를 새로 만든다(원본과 같음). 04의 `run_chain`·`llm`·`langfuse`는 구획 1에서 정의되어 구획 2·3이 쓴다 | 04 구획 머리에 "위 셀부터 순서대로"를 적는다 |
| `.env` 읽기 | `load_dotenv()`는 노트북 폴더에서 위로 올라가며 `.env`를 찾는다. CallbackHandler·get_client는 **만들 때** 환경변수를 읽는다 | 준비 셀에서 `.env`를 먼저 읽는다(다른 권과 같은 준비 셀). 원본의 `load_dotenv()` 줄은 그대로 둬도 무해 |
| Langfuse 서버 위치 | 받은 코드는 클라우드, 준비는 강사 맥 self-host. 강의장에서 어느 주소·계정을 쓸지 미정 | 5절 질문 3 |
| 여러 수강생의 trace가 섞임 | 수강생이 한 Langfuse 프로젝트를 같이 쓰면 Tracing 목록에 남의 trace가 섞여 성공 기준("새 trace 3개")을 판단하기 어렵다 | 5절 질문 3과 같이 정한다. 코드 변경 없이 하려면 CHANGE_HERE로 질문 문장에 자기 이름을 넣어 찾게 하는 방법이 있다 |
| 사내 게이트웨이 | 02는 `bind_tools`, 05는 `with_structured_output`(json_schema 방식) 사용. 사내 미검증 | 강의장 사전 확인 목록에 올린다. 05가 실패하면 강사 화면 시연으로 대체 |
| Judge 점수 파싱 | 04는 Judge 응답을 `float()`로 바꾸고 실패하면 **0.5를 조용히 기록**한다 | 코드는 고치지 않고 6장 물어보기(리뷰) 소재로 쓴다 |
| 화면 가독성 | 11차수 피드백: 뒷자리에서 Langfuse 화면이 하나도 안 보였다 | 대시보드 확인은 수강생 각자 PC 화면에서 하도록 성공 기준을 쓴다. 강사 화면은 확대(강사 메모) |
| 실행 시간 | LAB 전체 LLM 약 20회, 실행 합계 3~4분(추정). CHANGE_HERE로 한 번씩 더 돌리면 두 배 | LAB 85분 안에 든다고 본다. 대시보드 탐색 시간이 더 든다. 제작 단계에서 실측 |
| input()·파일 쓰기·메일 발송·별도 서버 | 없음(Langfuse 서버 접속만 필요) | — |

## 5. 확인이 필요한 질문

1. 커리큘럼 4.2의 "Moody's와 Salesforce 사 예시"가 슬라이드·코드에 없습니다. 지어내지 않으려면 (a) 이 항목을 빼거나 (b) 근거 자료를 받아 LEC 끝에 한 절을 넣어야 합니다. 예전 통합본 빌드 결과(`dev/docs/_build/lessons/day04.ipynb`)에 공개 자료 링크가 달린 두 문단이 남아 있는데, 이를 근거로 써도 될까요?
2. `05_rag_evaluation_extra.py`는 이름이 "Extra"지만 커리큘럼 "다차원 점수화(정확성/관련성/완성도)"를 다루는 유일한 코드입니다. 제안: 모두 함께 하는 마지막 예제(8장)로 두고, 시간이 모자라면 강사 시연으로 바꿉니다. 선택(심화, 조기 완료자용)으로 둘까요?
3. 강의장 Langfuse는 어느 주소로, 수강생마다 프로젝트(키)를 따로 줄까요, 한 프로젝트를 같이 쓸까요? 같이 쓰면 자기 trace를 찾는 방법을 성공 기준에 넣어야 합니다.
