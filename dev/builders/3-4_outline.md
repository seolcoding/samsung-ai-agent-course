# 3-4 교안 노트북 — 목차 (v1, 2026-09-28)

- **권 제목**: LangGraph 심화 (PDF 제목 "3-4 LangGraph 심화")
- **원본 슬라이드**: `course/Chapter02/slides/day01/3-4-langgraph-advanced.pdf` (10쪽. 표지 p1, 목차 p2, 장 표지 p3·p5·p8, 본문 5쪽: p4·p6·p7·p9·p10)
- **원본 코드**: `course/Chapter02/code/raw/03-langgraph-advanced/` 4개 (TODO 합계 20개)
  - `01_subgraph.py` (TODO 5개)
  - `02_persistence.py` (TODO 5개)
  - `03_memory_store.py` (TODO 5개. 75행 compile 결함 있음, 4절)
  - `04_parallel_execution.py` (TODO 5개)
- **앞 권에서 배운 것(예제/과제 판단 근거)**: M1 2-1에서 `StateGraph`·노드/엣지·`compile`·조건부 엣지·`MemorySaver`+`thread_id`·`add_messages` Reducer(개념)를 다뤘다. `invoke`로 그래프를 부르는 것도 M1 전체에서 썼다. 이 권에서 처음 나오는 API는 `SqliteSaver`, `get_state_history`(이력·time-travel), `InMemoryStore`(`put`/`search`, `compile(store=)`), `Send`다. 이것들은 **예제**로 둔다(5절 질문 1).
- **커리큘럼**: 3일차 3.4 "LangGraph 심화" 3.0H. 슬라이드 본문이 5쪽뿐이라 이 목차는 **LEC 약 40분 + LAB 약 120분 + 여유 20분**을 가정한다(5절 질문 2).
- **산출물**: `course/Chapter02/notebooks/3-4_langgraph_advanced_LEC.ipynb`, `course/Chapter02/notebooks/3-4_langgraph_advanced_LAB.ipynb` (LAB spec은 `dev/builders/labs/Chapter02/03-langgraph-advanced.json`, 아직 없음)
- **실행 검증**: 이 목차 단계에서는 코드를 실행하지 않았다. 호출 수·체크포인트 수는 코드 구조와 설치된 LangGraph 1.2.12 소스로 추정한 값이다. `dev/docs/VALIDATION.md`의 사외 실행(solution 38개)에 이 폴더가 따로 적혀 있지는 않다.

## 1. LEC 목차

슬라이드 PDF.js + C 수준 설명(슬라이드 요약, 내용 있는 곳만 "왜 배우나") + 4지선다 퀴즈. 코드 셀 없음.

| # | 절 제목 | 슬라이드 | 핵심 메시지 (근거 쪽) | 왜 배우나 | 퀴즈 |
|---|---|---|---|---|---|
| 1 | 도입 | p1–2 | 세 장: Subgraph → Persistence(Checkpointer, Memory Store) → Parallel Execution(Fan-out/Fan-in, Send) (p2) | — | — |
| 2 | Subgraph | p3–4 | 독립적으로 컴파일한 그래프를 상위 그래프의 노드처럼 쓴다. 기능 단위로 나누고, Subgraph마다 State를 따로 정의하며, 요약·번역·문서 처리처럼 반복되는 흐름을 재사용한다. 부모 노드 함수 안에서 자식 그래프를 `invoke`한다 (p4) | 그래프가 커지면 한 덩어리로는 읽기도 고치기도 어렵다. 반복되는 흐름을 한 번 만들어 여러 곳에서 쓴다 (p4) | 슬라이드의 방식에서 자식 그래프를 부모 그래프에 연결하는 방법은? (부모 노드 함수 안에서 컴파일된 자식 그래프를 호출) |
| 3 | Checkpointer | p5–6 | 실행 중 State를 저장해 같은 thread에서 이어서 실행한다. MemorySaver는 프로세스 메모리(개발/데모용), SqliteSaver는 SQLite 파일(재시작 후에도 유지). `thread_id`로 사용자·세션별 흐름을 나눈다. 실행 이력을 조회하고 과거 체크포인트에서 다시 실행할 수 있다 (p6) | M1에서 쓴 MemorySaver는 프로그램이 끝나면 기록이 사라진다. 저장 위치를 고르고, 지난 시점으로 되돌아가는 방법을 더한다 (p6) | 프로그램을 다시 시작해도 대화 상태가 남아야 할 때 고를 체크포인터는? (SqliteSaver) |
| 4 | Memory Store | p7 | Checkpointer와 별도로 사용자별 장기 기억을 저장한다. thread를 넘어 공유되고, namespace로 사용자·조직·프로젝트별 기억을 나눈다. 사용자 선호, 반복 업무 규칙, 중요한 사실을 담는다. `compile(checkpointer=…, store=…)`로 둘을 함께 넘긴다 (p7) | Checkpointer는 thread 단위라 새 대화(thread)를 열면 앞 대화 내용을 모른다. 대화를 넘어 남길 정보는 따로 둔다 (p6·p7) | 새 thread에서도 사용자의 취미를 기억하게 하려면 무엇에 저장해야 하나? (Memory Store) / namespace의 역할은? |
| 5 | Fan-out, Fan-in | p8–9 | 하나의 입력을 여러 작업으로 나눠 병렬 실행한 뒤 다시 합친다. START에서 두 노드로 엣지를 내면 fan-out, 두 노드에서 한 노드로 모으면 fan-in. 장단점 분석·여러 문서 요약·다중 검색처럼 **독립** 작업에 맞다. 병렬 결과를 합치려면 State 병합 규칙을 분명히 설계해야 한다 (p9) | 서로 기다릴 필요 없는 작업을 차례로 돌리면 시간만 늘어난다 (p9 "독립 작업") | Fan-out/Fan-in에 알맞지 **않은** 작업은? (앞 단계 결과가 있어야 하는 작업) |
| 6 | Send | p10 | 실행 시점에 Worker 수를 정한다. `Send("worker", state)`로 노드에 별도 입력을 보내고, 조건부 Edge에서 `list[Send]`를 반환하면 Worker가 병렬로 생긴다. 입력 리스트 길이에 따라 작업 수가 달라질 때 쓴다. 결과를 누적하려면 Annotated reducer 같은 병합 전략이 필요하다 (p10) | 질문이 몇 개 올지 그래프를 만들 때 모를 수 있다. 정적 fan-out은 노드 수가 고정이다 (p9·p10) | 정적 fan-out 대신 Send를 쓰는 상황은? (입력 리스트 길이에 따라 작업 수가 달라질 때) |
| 7 | 정리 퀴즈 | — | 세 장의 핵심 | — | 4지선다 3문항: ① Checkpointer / Store 중 알맞은 쪽 고르기(대화 이어 가기 vs 사용자 선호 저장) ② MemorySaver와 SqliteSaver의 차이 ③ 병렬 결과를 합칠 때 필요한 것(병합 규칙·reducer) |

- 퀴즈는 모두 4지선다. 정답은 슬라이드 문구에서만 만든다. 수강생 글에는 쪽 표시를 넣지 않는다.
- 3절 "M1에서 쓴 MemorySaver"는 커리큘럼 2.2·M1 2-1 실습에 근거한다.

## 2. LAB 목차

첫 구획(접힌 준비 셀) → 보이는 코드 셀. 셀은 위에서부터 차례로 실행한다. 행 번호는 raw 기준.

| 장 | 원본 | 구분 | CHANGE_HERE 후보 / WRITE_HERE로 바꿀 TODO | 성공 기준 초안 | 실행 제약 |
|---|---|---|---|---|---|
| 1 | (환경 확인) | — | — | — | 공통 셀 |
| 2 | `01_subgraph.py` | **과제** (3곳) | ① 37행 `# TODO: summarize, translate 노드와 START/END 엣지를 연결해 주세요.` → 빈칸 38–42행<br>② 64행 `# TODO: summary_subgraph를 호출해 document를 요약/번역해 주세요.` → 빈칸 66–70행(65행 메모 주석 "따라간다ㅓ"는 뺀다)<br>③ 85행 `# TODO: 부모 그래프의 실행 순서를 START → fetch_document → summarize_document → respond → END로 연결해 주세요.` → 빈칸 86–89행<br>44행·91행 compile TODO는 한 줄짜리라 빈칸으로 두지 않고 채운 채 보통 주석으로 바꾼다 | 🟢 `영문 요약:` 뒤에 영어 한 문장이 나온다<br>🟢 `최종 답변:` 뒤에 문서 내용(LLM 등장, AI가 하는 일)을 담은 한국어 답이 나온다<br>⛔ `KeyError: 'text'` 또는 `'summary'` → 자식 그래프에 넘기는 dict 키가 SummaryState와 다르다<br>⛔ 영문 요약이 한국어다 → translate로 가는 엣지가 빠졌다 | LLM 3회, 30초 안팎. 그래프는 맨 끝 `app.invoke` 셀에서 돈다 → 세 빈칸을 모두 채운 뒤 실행한다고 과제 머리에 적는다 |
| 3 | `02_persistence.py` 앞부분 (MemorySaver) | **과제** (3곳) | ① 26행 `# TODO: system 메시지와 State의 messages를 함께 LLM에 전달해 주세요.` → 빈칸 27행<br>② 31행 `# TODO: chatbot 노드와 START/END 엣지를 연결해 주세요.` → 빈칸 32–34행<br>③ 44행 `# TODO: MemorySaver 체크포인터로 그래프를 컴파일해 주세요.` → 빈칸 45행 | 🟢 `=== 1. MemorySaver (휘발성) ===` 아래 답에 "홍길동"이 나온다<br>⛔ "이름을 모른다"고 답한다 → compile에 체크포인터가 빠졌거나 두 호출의 `config`가 다르다 | LLM 2회, 20초 안팎. 셀을 나눠 1~50행(MemorySaver)까지를 이 장에 둔다 |
| 4 | `02_persistence.py` 뒷부분 (SqliteSaver·time-travel) | **예제** | 57행·76행 TODO는 채운 채 보통 주석으로 바꾼다. 54행 DB 경로는 patch 필요(4절)<br>CHANGE_HERE: 77행 되돌아갈 체크포인트<br>`past_config = checkpoints[0].config`<br>(번호를 바꿔 "취미를 말하기 전" 시점으로 가면 답이 달라지는지 본다. 목록 출력 patch 필요, 4절) | 🟢 `=== 2. SqliteSaver (영속성) ===` 아래 답에 "독서"가 나온다<br>🟢 `저장된 체크포인트 수:`와 체크포인트 목록이 나온다<br>🟢 (바꾼 뒤) 취미를 말하기 전 시점을 고르면 AI가 취미를 모른다고 답한다<br>⛔ `NameError: name '__file__'` → patch 누락(강사 확인) | LLM 3회, 30초 안팎. **파일을 쓴다**(`checkpoints.db`). 다시 실행할 때마다 같은 thread에 기록이 쌓인다(4절) |
| 5 | `03_memory_store.py` | **예제** + AI에게 물어보기 | 30·44·64·71행 TODO는 채운 채 보통 주석으로 바꾼다. 75–76행은 슬라이드와 같은 `app = builder.compile(checkpointer=MemorySaver(), store=store)`로 바꿔 넣는다(4절)<br>CHANGE_HERE: 92행 세션 2의 사용자<br>`print(chat('user_001', 'session_2', '내 이름이랑 취미 알아?'))`<br>(`'user_002'`로 바꿔 namespace가 사용자별로 나뉘는지 본다)<br>물어보기: `chatbot` 함수와 compile 줄을 붙여 넣고 "chatbot은 store를 어디서 가져오나, compile에 넘긴 store는 이 코드에서 쓰이나"를 설명받기(고치지 말 것) | 🟢 세션 1 답 앞에 `[기억 저장: …]`이 보이고, 세션 2(새 thread)에서 이름·취미를 말한다<br>🟢 `Store에 저장된 장기 기억` 아래 `[fact_0] …`처럼 사실이 한 줄 이상 나온다<br>🟢 (바꾼 뒤) user_002는 이름·취미를 모른다. 목록은 여전히 user_001 것이 나온다<br>🟢 (물어보기) 노드가 전역 변수 `store`를 직접 쓴다는 점을 짚었다<br>⛔ 기억 목록이 비었다 → LLM이 `[기억 저장: …]` 형식을 안 지켰다. 다시 실행 | LLM 2회, 20초 안팎. 결과가 LLM의 형식 준수에 달려 있다(4절) |
| 6 | `04_parallel_execution.py` 앞부분 (정적 병렬) | **과제** (1곳) | ① 51행 `# TODO: START에서 pros/cons를 병렬로 실행하고 summary에서 합쳐 END로 이어 주세요.` → 빈칸 52–60행(54–59행 강사 메모 주석 포함 구간)<br>61행 compile TODO는 채운 채 둔다 | 🟢 `장점:`·`단점:`·`결론:` 세 줄이 나오고 결론이 장점과 단점을 함께 말한다<br>🟢 정답과 비교해 START에서 나가는 엣지가 두 개다<br>⛔ pros → cons → summary처럼 차례로 이었다(결과는 비슷하게 나와도 병렬이 아니다) → 정답 보기와 엣지를 비교 | LLM 3회, 20~30초. 직렬로 이어도 화면이 거의 같아 **출력만으로는 병렬 여부를 가를 수 없다** → 성공 기준에 "정답 보기와 엣지 비교"를 넣는다 |
| 7 | `04_parallel_execution.py` 뒷부분 (Send) | **예제** + AI에게 물어보기 | 94·111·114행 TODO는 채운 채 보통 주석으로 바꾼다(95–100행 강사 메모 주석은 뺀다)<br>CHANGE_HERE: 120행 질문 목록<br>`queries = ['LangGraph란?', 'RAG란?', 'MCP란?']`<br>(질문을 하나 더 넣어 worker가 그만큼 늘어나는지 본다)<br>물어보기: `DynamicState`·`worker_node`를 붙여 넣고 "`results`의 `Annotated[..., lambda a, b: a + b]`가 없으면 어떻게 되나"를 설명받기 | 🟢 질문 수만큼 `[질문] 답` 줄이 나온다(원본 3줄)<br>🟢 (바꾼 뒤) 넣은 질문 수만큼 줄이 늘어난다<br>🟢 (물어보기) 여러 worker가 같은 `results`에 쓰므로 합치는 규칙이 필요하다는 점을 짚었다<br>⛔ 줄 수가 질문 수보다 적다 → 질문 목록 문법을 다시 본다 | LLM 질문 수만큼(원본 3회), 병렬이라 10~20초 |
| 8 | 정리 | — | — | — | — |

- 합계: 과제 3장(빈칸 7곳), 예제 3장(CHANGE_HERE 3곳 + 물어보기 2개).
- 커리큘럼 대조(3.4): Subgraph 모듈화 → LAB 2 / MemorySaver vs SqliteSaver, 이력과 time-travel → LAB 3–4 / Checkpointer와 Store 역할 분리 → LAB 5 / 정적 fan-out·fan-in, 동적 Send → LAB 6–7 / [실습] 병렬 질의 처리 및 결과 집계 → LAB 7. 이 [실습]이 예제뿐이라는 점은 5절 질문 1.

## 3. 원본·솔루션 차이와 고른 쪽

| 파일 | 차이 | 고른 쪽 | 이유 |
|---|---|---|---|
| `01_subgraph.py` | ① TODO 5개가 raw에만 있다<br>② raw 64–65행에 메모 주석(오타 "따라간다ㅓ"), 호출을 여러 줄로 씀(`response`) / 솔루션은 한 줄(`result`)<br>③ 솔루션에 긴 강사 메모 docstring(summarize_node), 주석 처리된 확장 구상 그림, 주석 처리된 서브그래프 단독 호출 코드가 있다 | **raw** (메모 주석 뺌) | 과제에 TODO가 필요하다. 솔루션의 메모·주석 코드는 화면만 길게 한다. 정답 보기에는 raw의 여러 줄 호출을 쓴다(dict 키가 한눈에 보임) |
| `02_persistence.py` | ① TODO 5개가 raw에만 있다<br>② 솔루션에 주석 처리된 `# mem_app = builder.compile()`<br>③ **time-travel 대상**: raw `checkpoints[0]`(가장 최근) / 솔루션 `checkpoints[-1]`(가장 오래된 것, 주석 "가장 오래된 체크포인트")<br>④ time-travel 질문: raw "내 취미가 뭐라고 했더라?" / 솔루션 "독서 말고 다른 취미도 있어?" | **raw 기반 + ③은 CHANGE_HERE로** | `get_state_history`는 최신부터 돌려주므로 raw의 `[0]`은 되돌아가지 않은 것과 같다. 솔루션의 `[-1]`은 첫 입력 전(값이 빈) 시점으로 추정되고, 질문에 "독서"가 들어 있어 기억 여부를 가를 수 없다. raw 질문을 두고 번호를 수강생이 바꿔 보게 한다 |
| `03_memory_store.py` | ① TODO 5개가 raw에만 있다<br>② **76행**: raw `app = builder.compile()` / 솔루션 `builder.compile(checkpointer=MemorySaver(), store=store)` | **raw 기반 + 76행은 솔루션** | raw는 75행 TODO가 요구하는 것과 슬라이드 p7의 compile 줄을 따르지 않는다(알려진 결함, 4절) |
| `04_parallel_execution.py` | ① TODO 5개가 raw에만 있다<br>② raw 39행 `print(state['cons'], state['pros'])` 디버그 출력이 있다<br>③ raw에 강사 메모 주석(54–59행 fan-in 설명, 95–100행 for문/리스트 컴프리헨션, 109–110·118–119행) / 솔루션은 짧은 주석 "둘 다 끝나야 summary 시작 (fan-in)" | **raw 기반 + 39행 뺌 + 주석은 솔루션 쪽** | 39행은 장단점 전문을 한 번 더 찍어 화면이 길어진다. 솔루션 주석이 짧고 fan-out/fan-in 용어가 슬라이드와 맞다. raw 54–59행 설명은 정답 보기 해설로 옮길 수 있다 |

## 4. 실행 제약·위험과 처리 제안

| 항목 | 내용 | 노트북 처리 제안 |
|---|---|---|
| **03 compile 결함** (AGENTS.md 7절) | raw 76행 `builder.compile()`에 checkpointer·store가 없다. 슬라이드 p7은 `compile(checkpointer=MemorySaver(), store=store)`다. 그런데 `chatbot`이 전역 변수 `store`를 직접 쓰므로 **raw로 실행해도 화면이 똑같이 나온다**(조용히 틀리는 경우). 솔루션처럼 `store=store`를 넘겨도 이 코드의 노드는 그것을 받지 않는다(LangGraph는 노드가 `store` 인자를 선언할 때만 넣어 준다. 1.2.12 소스 `_internal/_runnable.py` 확인) | spec `patch`로 76행을 슬라이드와 같은 줄로 바꾼다(원본 파일은 그대로). 차이는 물어보기 소재로 쓴다(LAB 5). 노드를 `store` 인자로 받게 고치는 것은 원본에 없으므로 하지 않는다(5절 질문 3) |
| **02 DB 파일 위치** | 54행 `DB_PATH = os.path.join(os.path.dirname(__file__), 'checkpoints.db')`. 스크립트로 돌리면 `.py` 옆(`course/Chapter02/code/raw/03-langgraph-advanced/`)에 파일이 생긴다. 노트북 커널에는 보통 `__file__`이 없어 `NameError`가 난다(VS Code 동작은 제작 단계에서 확인) | spec `patch`로 `DB_PATH = 'checkpoints.db'`(노트북 폴더)로 바꾼다. `.gitignore`에 `*.db`가 있어 커밋되지 않는다. AGENTS.md 9절대로 이전 회차의 `checkpoints.db`가 남았던 적이 있다 |
| **02 재실행 누적** | thread_id가 `'persistent_demo'`로 고정이다. SQLite 파일은 커널을 다시 켜도 남으므로 셀을 다시 돌릴 때마다 같은 thread에 메시지·체크포인트가 쌓인다. 호출 1번에 체크포인트가 약 3개(입력·시작·chatbot) 생기므로 첫 실행 "저장된 체크포인트 수"는 6으로 추정되고, 다시 돌리면 time-travel 분기 3개와 새 6개가 더해진다. 번호로 고르는 time-travel 대상도 실행할 때마다 달라진다 | 누적은 "재시작해도 남는다"(p6)의 증거이므로 지우지 않고 설명 글로 짚는다. 처음부터 다시 보려면 thread_id를 바꾸거나 파일을 지우면 된다고 한 줄 적는다(5절 질문 4). `with sqlite3.connect(...)`는 연결을 닫지 않는다(커밋만). 셀을 여러 번 돌려도 오류는 없을 것으로 보이나 제작 단계에서 확인 |
| **02 time-travel 목록** | 71–72행은 앞 3개만, `cp.values["messages"]`로 출력한다. 가장 오래된 체크포인트는 값이 빈 것으로 추정되어 전부 출력하면 `KeyError`가 날 수 있다 | CHANGE_HERE로 번호를 고르려면 번호와 메시지 수를 함께 보여야 한다. spec `patch`로 `for i, cp in enumerate(checkpoints):` + `cp.values.get("messages", [])`로 바꾸는 안을 제안한다(원본 동작과 달라지므로 5절 질문 4에서 함께 확인) |
| 03 LLM 형식 의존 | 장기 기억 저장은 LLM이 답 앞에 `[기억 저장: …]`을 붙여야만 된다(정규식 `\[기억 저장: (.+?)\]`, 콜론 뒤 공백 하나). 형식을 안 지키면 아무것도 저장되지 않고 세션 2가 모른다고 답한다. 이 태그는 사용자 답에도 그대로 보인다 | ⛔ 성공 기준에 "다시 실행"을 적는다. 사내 모델 준수율은 강의장 사전 확인 |
| 03 key 번호 | `key = f'fact_{len(memories) + i}'`인데 `store.search` 기본 limit가 10이라 기억이 10개를 넘으면 같은 key로 덮어쓴다. 수업 흐름(2회 호출)에서는 생기지 않는다 | 다루지 않는다 |
| 04 직렬로 채워도 통과처럼 보임 | 정적 병렬 과제는 pros → cons → summary로 이어도 출력이 비슷하다 | 성공 기준에 "정답 보기와 엣지 비교"를 넣는다(LAB 6) |
| 사내 게이트웨이 | 이 폴더는 `bind_tools`·`with_structured_output`을 쓰지 않는다. 평범한 `llm.invoke`만 쓴다 | 앞 권과 같은 조건. 추가 확인 없음 |
| 실행 시간 | LLM 합계 약 13회(01: 3, 02: 3+2, 03: 2, 04: 3+3). 수강생이 CHANGE_HERE로 다시 돌려도 LAB 실행만 5분 안팎 | LAB 120분 안에 충분히 들어간다. 제작 단계에서 실측해 강사 메모에 적는다 |
| 커널 상태 | 02와 03은 둘 다 `State`, `chatbot`, `builder`를 정의한다. 02 뒤에 03을 실행하면 덮어쓴다. 03을 먼저 돌린 뒤 02의 셀을 다시 돌리면 03의 `chatbot`이 남아 있지 않은지 확인 필요 | 장마다 필요한 정의를 그 장 첫 셀에 두고 "장 안에서 위에서부터 차례로 실행"을 적는다 |
| 외부 서비스·input()·메일 | 없음. 01의 문서는 코드 안의 고정 문자열이다 | — |

## 5. 확인이 필요한 질문

1. 이 권에서 처음 나오는 `SqliteSaver`·time-travel·`InMemoryStore`·`Send`를 모두 예제로 두었습니다. 그래서 커리큘럼의 [실습] "병렬 질의 처리 및 결과 집계"(`Send`)가 예제뿐입니다. 같은 권 LEC에서 슬라이드 p10이 코드를 그대로 보여 주므로 `fan_out`(94행)과 동적 그래프 연결(111행)을 과제로 올릴까요?
2. 3.0H를 LEC 약 40분 + LAB 약 120분 + 여유 20분으로 가정했습니다. 슬라이드 본문이 5쪽이라 LEC를 이보다 줄여도 될까요?
3. 03의 compile 결함은 76행을 슬라이드 줄로 바꾸고 "compile에 넘긴 store가 이 코드에서 실제로 쓰이나"를 물어보기로 다루는 안입니다. 노드가 `store` 인자를 받도록 코드까지 고칠까요, 이 안으로 둘까요?
4. 02 SqliteSaver 셀: DB를 노트북 폴더의 `checkpoints.db`로 두고, 누적을 지우지 않으며, 체크포인트 목록을 번호와 함께 모두 보여 주도록 patch하는 안이 괜찮을까요?
