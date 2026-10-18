# 1-3 교안 노트북 — 1단계 목차 (v1, 2026-09-28)

> 2026-10-18: 실습 노트북에서 "AI에게 물어보기" 절을 뺐다(`dev/AGENTS.md`). 아래의 물어보기 항목은 지난 설계 기록이고 빌드에 쓰이지 않는다.

- **원본 PDF**: `docs/raw/Chapter01/day01/1-3-langchain-framework-deep-dive.pdf` (14쪽)
- **권 제목**: LangChain 프레임워크 깊이 있는 학습 → `# [LEC] LangChain 프레임워크 깊이 있는 학습`, `# [LAB] LangChain 실습`
- **원본 코드**: `src/raw/Chapter01/02-langchain/` 5개 — `01_lcel_runnable.py`, `02_tool_calling.py`, `03_output_parser.py`, `04_memory_runnable.py`, `05_memory_langgraph.py` (솔루션: `src/solution/Chapter01/02-langchain/` 같은 이름)
- **커리큘럼**: 1.3 LangChain 프레임워크 깊이 학습, 1일차 2.0H(120분). 배분 초안: LEC 40분 + LAB 70분 + 정리 10분
- **LLM 경로**: 기본 `LLM_PROVIDER=samsung`(사내 게이트웨이), 사외 준비는 `openai`. 사내 전용(RAGaaS 등) 코드는 없다.
- **LAB 빌드**: 기존 뼈대 `lessons/drafts/labs/02-langchain.json`(draft, 구획 marker·TODO blank 범위만 있음)을 채운다.

## 1. LEC 목차

PDF 순서 그대로. 표지·목차(p1–2)는 맨 위 준비 셀 다음에 보여 준다. 간지(p3, p8, p12)는 각 장 첫 슬라이드로 붙인다.

| # | 절 제목 | 슬라이드 | 핵심 메시지 (근거 쪽) | 퀴즈 (4지선다, 한 줄 질문) |
|---|---|---|---|---|
| 1 | LCEL과 Runnable | p3 | — (장 제목) | — |
| 1.1 | LCEL의 설계 철학 | p4–5 | LCEL은 프롬프트·모델·파서·함수를 하나의 흐름으로 잇고, `\|`는 앞 단계 출력을 다음 단계 입력으로 넘긴다(p4). 흐름을 선언적으로 읽을 수 있고 동기·비동기·스트리밍·배치를 같은 구조로 다룬다(p5). **왜 배우나**: 복잡한 Agent도 "입력을 변환해 다음 단위로 넘기는 흐름"으로 읽을 수 있다(p4) | `prompt \| model \| parser`에서 `\|`가 하는 일은? |
| 1.2 | Runnable 인터페이스 | p6–7 | 프롬프트·LLM·파서·함수가 모두 Runnable로 연결되고, 같은 체인을 `invoke`/`batch`/`stream`으로 실행한다(p6). Passthrough는 입력을 그대로 전달, Lambda는 일반 함수를 감싸고, Parallel은 여러 결과를 묶는다(p7). **왜 배우나**: 검색 결과·질문·메타데이터를 한 프롬프트 입력으로 모을 때 쓴다(p7) | 일반 함수를 체인 안의 실행 단위로 감싸는 것은? |
| 2 | Tool Calling | p8 | — (장 제목) | — |
| 2.1 | Tool Schema와 도구 선택 | p9 | 모델은 답 대신 도구와 인자를 구조화된 형태로 고른다. 스키마는 이름·설명·인자·타입을 알려 주고, 좋은 설명은 "언제 쓰는지"를 말한다(p9) | 좋은 도구 설명에 꼭 들어가야 하는 것은? |
| 2.2 | 응답 파싱과 실행 흐름 | p10–11 | 모델은 도구 이름과 인자만 만들고, 실행은 애플리케이션이 한다. 결과는 다시 모델 입력으로 들어간다(p10). Agent는 판단 → 선택 → 관찰 → 반복/종료를 되풀이한다(p11). **왜 배우나**: 11차수 진행 원칙대로 "등록 방법"보다 "모델이 어떻게 고르고 호출이 어떻게 반복되는지"를 구조로 설명한다 | 도구 함수를 실제로 실행하는 주체는? |
| 3 | 구조화된 출력과 메모리 | p12 | — (장 제목) | — |
| 3.1 | Output Parser와 Pydantic | p13 | 파서는 텍스트 출력을 프로그램이 쓸 수 있는 구조로 바꾸고 형식을 확인한다. Pydantic은 필드 이름·타입·설명을 전달하고 잘못된 타입·누락 필드를 검증한다(p13). **왜 배우나**: 평가·라우팅·저장·UI 표시처럼 정해진 구조가 필요한 작업에 쓴다(p13) | Pydantic 스키마로 할 수 있는 일은? |
| 3.2 | Buffer, Summary, VectorStoreRetriever Memory | p14 | Buffer는 대화를 그대로, Summary는 요약해서, VectorStoreRetriever는 관련 기억만 검색해 넣는다. 정확도·비용·지연시간의 균형으로 고른다. 중요한 상태는 별도 데이터 구조로 저장한다(p14). **왜 배우나**: 모델은 이전 대화를 기억하지 않으므로 코드가 다시 넣어 줘야 한다(1-2의 Context Window와 연결) | 긴 대화에서 컨텍스트 사용량을 줄이려면 어떤 메모리가 알맞은가? |
| 4 | 정리 퀴즈 | — | 세 장의 핵심 | 4문항: `\|`의 역할 / Runnable 실행 방식(`batch`) / 도구 실행 주체 / 메모리 전략 선택 |

퀴즈 정답·선택지는 `assets/quizzes/1-3/`에 파일로 둔다(1-2와 같은 방식). 수강생 글에 쪽 표시를 넣지 않는다.

## 2. LAB 목차

장 번호는 1-2 LAB처럼 `1. 실습 방법` 다음 2부터. 예제/과제 판단: 01~04의 TODO 개념(LCEL, Runnable, Tool Calling, Output Parser, 메모리)은 이 권 LEC에서 배우므로 **과제**. 05는 LangGraph(StateGraph·노드·엣지·compile)를 쓰는데 LangGraph는 2-1에서 배우므로 **예제**. 03 방법 2(`with_structured_output`)는 PDF에 없어서 **예제**(7절 질문 1).

| 장 (원본) | 구획 | 종류 | CHANGE_HERE 후보 / WRITE_HERE로 쓸 TODO (원본 줄) | 성공 기준 초안 | 실행 제약 |
|---|---|---|---|---|---|
| **2. LCEL과 Runnable** (`01_lcel_runnable.py`) | 2.1 기본 체인 만들기 | 과제 | WRITE_HERE ① `# TODO: system, human 메시지 튜플을 작성해 주세요.`(30) → 빈칸: system·human 튜플 2줄. ② `# TODO: 위에 정의한 프롬프트, 모델, 출력 파서를 파이프라인 연산자로 연결해 주세요.`(44) → 빈칸: `chain = prompt \| model \| parser` | 🟢 다음 셀의 `invoke` 답이 주제를 3문장 안팎으로 설명한다 · 🟢 `chain`이 prompt → model → parser 순서다 · ⛔ 답이 문자열이 아니라 `AIMessage(...)`로 나온다 → parser가 빠졌는지 확인 | LLM 호출 1회 |
| | 2.2 invoke·stream·batch 실행 | 예제 | CHANGE_HERE `answer = chain.invoke({'topic': 'LLM'})`(솔루션 46) — 주제 바꾸기 | 🟢 invoke 답, stream 조각 출력, batch 두 주제 답이 모두 나온다 · 🟢 바꾼 주제로 답이 바뀐다 · ⛔ `KeyError: topic` → 중괄호 이름을 지웠는지 확인 | LLM 호출 4회(stream 1, batch 2) |
| | 2.3 RunnableParallel | 예제 | CHANGE_HERE `answers = runnable.invoke({'country': '베트남'})`(76) — 나라 바꾸기 | 🟢 pros·cons 두 목록이 모두 출력된다 · 🟢 dict 방식(92–102)도 같은 모양으로 나온다 · ⛔ 한쪽이 `None` → 키 이름(pros/cons)과 `get` 이름이 다른지 확인 | LLM 호출 4회, **출력이 길다**(5항목 × 4) |
| | 2.4 RunnablePassthrough | 예제 | CHANGE_HERE `print(passthrough.invoke({'question': 'RunnablePassthrough의 역할이 뭐야?'}))`(112) — 질문 바꾸기 | 🟢 원래 `question`과 새 `length`가 함께 든 dict가 나온다 · ⛔ `length`가 없다 | LLM 호출 1회 |
| | 2.5 RunnableLambda | 예제 | CHANGE_HERE `print(RunnableLambda(translate_acronym).invoke('GPT'))`(131) — `'LLM'`이나 사전에 없는 약어로 바꾸기 | 🟢 사전에 있는 약어는 풀어 쓴 이름, 없는 약어는 그대로 나온다 · 🟢 마지막 체인이 풀어 쓴 이름으로 설명한다 · ⛔ 사전에 없는 약어에서 오류가 난다 | LLM 호출 1회 |
| **3. 도구 호출** (`02_tool_calling.py`) | 3.1 도구 정의 | 예제(보기만) | 없음. `@tool`·docstring·타입 힌트가 LEC 2.1의 스키마(이름·설명·인자·타입)가 된다는 점만 본다 | — | 호출 없음 |
| | 3.2 도구 등록 | 과제 | WRITE_HERE ③ `# TODO: LLM에 연결할 도구 목록을 작성해 주세요.`(52) → `tools = [...]` · ④ `# TODO: bind_tools()를 사용해 LLM에 도구 스키마를 연결해 주세요.`(58) → `llm_with_tools = ...` · ⑤ `# TODO: 도구 이름으로 실제 도구를 찾을 수 있도록 매핑을 만들어 주세요.`(64) → `tool_map = ...` | 🟢 `tool_map`을 출력하면 `get_weather`, `calculate` 두 이름이 보인다 · ⛔ 3.3 실행에서 `KeyError` → 매핑 키가 도구 이름과 다른지 확인 | 호출 없음 |
| | 3.3 수동 도구 호출 루프 + 실행 | 과제 | WRITE_HERE ⑥ `# TODO: tool_calls의 이름과 인자를 사용해 해당 도구를 실행해 주세요.`(90) → 빈칸 2줄: 도구 찾기·`invoke(call['args'])`. CHANGE_HERE `print(run_with_tools('서울 날씨 알려줘'))`(104) — 도시 바꾸기(`'대전'`처럼 가짜 데이터에 없는 도시도) | 🟢 출력된 호출 정보에 도구 이름과 인자(`{'city': '서울'}`)가 보인다 · 🟢 최종 답이 도구 결과(맑음, 22°C)를 쓴다 · ⛔ 호출 정보 줄 없이 날씨를 지어낸다 → 도구가 연결됐는지 확인 | LLM 호출 질문당 2회 이상(3질문), **사내 게이트웨이 tool calling 미확인** |
| **4. 구조화된 출력** (`03_output_parser.py`) | 4.1 출력 스키마 | 예제(보기만) | 없음. `MovieReview`의 필드·타입·설명을 본다 | — | 호출 없음 |
| | 4.2 방법 1: PydanticOutputParser | 과제 | WRITE_HERE ⑦ `# TODO: MovieReview 스키마를 사용하는 PydanticOutputParser를 생성해 주세요.`(40) · ⑧ `# TODO: format_instructions가 포함된 프롬프트를 구성해 주세요.`(43) · ⑨ `# TODO: 프롬프트, LLM, 파서를 LCEL 체인으로 연결해 주세요.`(49) | 🟢 제목·장르·평점·요약·추천 5줄이 모두 나온다 · 🟢 평점이 숫자, 추천이 ✓/✗다 · ⛔ `OutputParserException` → 프롬프트에 형식 지시(`format_instructions`)가 들어갔는지 확인 | LLM 호출 1회 |
| | 4.3 방법 2: with_structured_output | 예제 | 솔루션 코드(원본은 전부 주석)로 채운다. CHANGE_HERE `review2: MovieReview = chain2.invoke({'movie': '기생충'})`(솔루션 71) — 영화 바꾸기 | 🟢 방법 1과 같은 5줄이 형식 지시 없이 나온다 · ⛔ 응답 형식 관련 오류 → 강사에게 알린다(사내 지원 미확인) | LLM 호출 1회, **사내 json_schema 응답 형식 미확인** |
| **5. 세션 메모리** (`04_memory_runnable.py`) | 5.1 세션 저장소 | 과제 | WRITE_HERE ⑩ `# TODO: session_id별 InMemoryChatMessageHistory를 생성하고 반환해 주세요.`(29) → 함수 몸통(없으면 만들고, 있으면 꺼내 반환) | 🟢 5.3에서 세션 A가 이름을 기억한다 · ⛔ 두 번째 질문에서도 이름을 모른다 → 매번 새 기록을 만드는지 확인 | 호출 없음 |
| | 5.2 체인과 기록 연결 | 과제 | WRITE_HERE ⑪ `# TODO: RunnableWithMessageHistory로 체인과 세션 히스토리를 연결해 주세요.`(65) → `chain_with_history = RunnableWithMessageHistory(...)` | 🟢 `input`·`history` 이름이 프롬프트와 맞는다 · ⛔ `KeyError: history`/`input` | **deprecation 경고**(5절) |
| | 5.3 세션 A·B 실행과 기록 확인 | 예제 | CHANGE_HERE `r1 = chain_with_history.invoke({'input': '내 이름은 홍길동이야.'}, config=config_a)`(78) — 이름 바꾸기 | 🟢 세션 A 두 번째 답에 이름이 나온다 · 🟢 세션 B는 이름을 모른다 · 🟢 저장된 메시지가 사람/AI 4줄이다 · ⛔ 세션 B도 이름을 안다 → `session_id`가 같은지 확인 | LLM 호출 3회 |
| **6. 상태 안에 담는 메모리** (`05_memory_langgraph.py`) | 6.1 State와 노드 | 예제 | 솔루션 코드로 채운다(TODO 3개는 모두 정답 코드로, `# TODO` 주석은 지운다) | — | 호출 없음 |
| | 6.2 그래프 빌드 | 예제 | 없음. 노드 1개·START/END 엣지·`MemorySaver`로 compile하는 모양만 본다 | — | 호출 없음 |
| | 6.3 스레드 A·B와 스냅샷 | 예제 | CHANGE_HERE `config_b = {'configurable': {'thread_id': 'thread_B'}}`(62) — `'thread_A'`로 바꾸기 | 🟢 바꾸기 전: B는 이름을 모른다 · 🟢 `thread_A`로 바꾸면 B도 홍길동을 안다 · ⛔ 스레드 A도 이름을 모른다 → checkpointer가 compile에 들어갔는지 확인 | LLM 호출 3회 |
| | 6.4 AI에게 물어보기 | — | 힌트: 5장 세션 메모리 셀과 이 장 셀을 붙여 넣고, 대화 기록이 어디에 저장되는지 비교해 달라고 한다(코드는 고치지 말라고 적는다) | 🟢 5장은 체인 밖 저장소, 6장은 State 안이라고 짚는다 · ⛔ 코드를 새로 써 온다 → 고치지 말라고 다시 적는다 | 호출 없음 |
| **7. 정리** | — | — | 1-2 LAB처럼 장별 요약 표(무엇을 연결했나 / 결과가 어디 나오나) | — | — |

과제마다 프롬프트 힌트(3문장 이내)와 접힌 "정답 보기"를 붙인다. 지시문 완성본은 주지 않는다.

## 3. 원본·솔루션 차이와 고른 쪽

| 파일 | 차이 | 고른 쪽 | 이유 |
|---|---|---|---|
| 01 | raw는 `invoke`/`stream`/`batch` 실행 줄이 주석, 솔루션은 실행 | 솔루션 | p6의 세 실행 방식을 실제로 본다 |
| 01 | 프롬프트 문구: raw `초보자에게 … 설명해 줘`(마침표 없음), 솔루션 `초급자에게 … 설명해줘.` | 솔루션 | 정답 보기와 빈칸 대상이 한 벌이 되게 한다. 뜻 차이 없음 |
| 01 | raw에만 강사 말투 주석(`# 가우스`, `# 사용자가 입력한 값 -> …`, `# 파이썬 주석처리 -> … ctrl + /`, `# 이거 내가 맘음대로 지을 수 있음!`, `translate_acronym` 안의 주석 2줄) | 솔루션 | 화면이 깔끔하다. "키 이름은 자유롭게 정한다"는 내용만 2.3 설명 글로 옮긴다 |
| 02 | raw에만 `print(call)` | **raw 유지** | 호출 정보(도구 이름·인자·id)가 화면에 보여 p10 구조를 그대로 확인한다. 3.3 성공 기준이 이 줄에 기댄다 |
| 02 | raw `tool_map` 위 `'''{'get_weahter': …}'''` 문자열(오타 포함) + `{tool.name: tool for tool in tools}` / 솔루션 `{t.name: t for t in tools}` | 솔루션 | 오타 문자열이 없고, `tool` 이름이 데코레이터 `@tool`과 겹치지 않는다 |
| 02 | raw에만 강사 주석(25–30, 59–60줄) | 솔루션 | 화면 정리. "docstring과 타입 힌트도 모델에게 주는 힌트"는 3.1 설명 글로 옮긴다 |
| 03 | 방법 2·비교 요약이 raw는 전부 주석(TODO 포함), 솔루션은 실행 | 솔루션 | 커리큘럼 "Output Parser vs with_structured_output() 비교"를 실행으로 보인다 |
| 03 | system 프롬프트: raw `응답해. {format_instructions}`, 솔루션 `응답해.\n{format_instructions}` | 솔루션 | 형식 지시가 줄을 바꿔 들어가 읽기 쉽다 |
| 04 | raw에만 대화 누적 모양을 보여 주는 `'''…'''` 문자열(46–61줄)과 TODO 안 주석 | 솔루션 코드 + raw 문자열 내용은 5.2 설명 글(마크다운)로 | 코드는 깔끔하게, "두 번째 요청에 첫 대화가 다시 들어간다"는 그림은 살린다 |
| 04 | `history_messages_key='history'` 끝 쉼표 | 솔루션 | 차이 없음(형식만) |
| 05 | raw는 TODO 3곳이 빈 상태(`return {'messages': []}`, `checkpointer = None`, `app = None`) | 솔루션 | 예제이므로 완성 코드로 실행 |

## 4. 원본끼리·슬라이드와 어긋나는 곳 (고치지 않고 강사용 메모로)

1. **p4 코드는 `ChatOpenAI(model="gpt-4.1-mini")`**, 실습은 `get_llm()`. 1-2에서 배운 래퍼를 쓴다고만 말한다.
2. **p7 순서(Passthrough → Lambda → Parallel)와 코드 순서(Parallel → Passthrough → Lambda)가 다르다.** 원본 코드 순서를 유지한다.
3. **p7 "Passthrough는 입력을 그대로 전달"**, 코드는 `RunnablePassthrough.assign(length=…)`로 필드를 더한다. 설명 글에 "그대로 넘기면서 값을 덧붙일 수도 있다"를 적는다.
4. **p10 JSON 모양(`tool`/`arguments`)과 LangChain `tool_calls`(`name`/`args`/`id`)가 다르다.** `print(call)` 출력으로 대응을 보여 준다.
5. **p14의 세 메모리 중 코드는 Buffer 방식만 구현한다.** Summary·VectorStoreRetriever 실습 코드는 없다(원본 그대로 둔다).
6. **03 비교 표와 주석의 "function-calling 보장", "GPT-4o 이상 기본 권장"**: 현재 langchain-openai 1.6.6의 `with_structured_output` 기본 방식은 `json_schema`(응답 형식 지정)이지 function calling이 아니다. 원본 출력은 그대로 두고 강사용 메모에만 적는다.
7. **02 `calculate`는 `eval`을 쓴다**(builtins 비움). 수업용 가짜 도구라 그대로 둔다. 질문 받으면 "실서비스에서는 쓰지 않는다"고만 답한다.

## 5. 실행 제약·위험과 처리 제안

| 위험 | 위치 | 처리 제안 |
|---|---|---|
| 사내 게이트웨이의 tool calling(`bind_tools`) 지원 미확인 | 3장 | 강의장 사전 확인. 실패하면 3.3은 성공 기준과 정답 보기만 읽고 넘어간다 |
| 사내 게이트웨이의 `json_schema` 응답 형식 지원 미확인 | 4.3 | 사전 확인. 안 되면 강사용 메모에 "method='function_calling'으로 바꾸면 된다"를 적되 코드는 원본 유지(7절 질문 아님, 확인 결과 보고 결정) |
| `RunnableWithMessageHistory` deprecation 경고(langchain-core 1.3.3부터, 2.0에서 제거 예정). QC는 경고 없는 실행을 요구 | 5.2 | 7절 질문 2 |
| 원본 코드·출력 안의 파일 경로: 02의 주석 `05-langgraph/03_tool_node.py 참고`(76, 112–113줄), 04 출력 문자열 `LangGraph 방식(05_memory_langgraph.py)`(107줄), 각 파일 머리 docstring의 `python …py` 실행 안내 | 3·5장 | docstring은 접힌 준비 셀에 들어가 보이지 않게 한다. 주석·출력 문자열은 7절 질문 3 |
| LLM 호출이 많고 출력이 길다(01만 약 10회, LAB 전체 약 25회) | 2.3 등 | 2.3 앞에 "출력이 길다, pros/cons 첫 줄만 본다"를 먼저 알린다 |
| 실행 순서 의존: 01은 `prompt`·`chain` 이름을 뒤에서 다시 정의, 05는 같은 커널에서 다시 실행하면 thread 기록이 쌓인다 | 2장, 6장 | 장 첫머리 준비 셀부터 위에서 차례로 실행하라고 안내(1-2와 같음). 6장 재실행 시 이름이 두 번 저장되는 것은 정상이라고 강사용 메모에 적는다 |
| `input()`, 파일 쓰기, 외부 서비스, 메일 발송 | — | 없음 |

## 6. 커리큘럼 1.3 항목 대조 (`docs/CURRICULUM.md`)

| 커리큘럼 항목 | LEC | LAB |
|---|---|---|
| LCEL 설계 철학과 Pipe(`\|`) 기반 체인 구성 | 1.1 | 2.1–2.2 |
| Runnable 인터페이스: Parallel / Passthrough / Lambda | 1.2 | 2.3–2.5 |
| Tool Calling 메커니즘: 스키마 기반 도구 선택, 수동 루프 처리 | 2.1–2.2 | 3장 |
| Output Parser vs with_structured_output() 비교 | 3.1 (Parser·Pydantic만. `with_structured_output`은 PDF에 없음) | 4장 |
| 메모리 전략 1: RunnableWithMessageHistory 세션 메모리 | 3.2 (Buffer 개념) | 5장 |
| 메모리 전략 2: LangGraph + MemorySaver 상태 내장 메모리 | 없음 (PDF에 없음) | 6장 (예제) |
| [실습] 날씨/계산 도구 자율 도구 선택 체인 | — | 3장 |
| [실습] 구조화 출력(MovieReview) 파싱 및 안정성 비교 | — | 4장 (비교 요약 표 출력 포함) |
| (PDF에만) Summary / VectorStoreRetriever Memory | 3.2 | 없음 |

## 7. 사용자에게 물어볼 것

1. **03 방법 2(`with_structured_output`)를 예제로 둘까요?** PDF에 없는 개념이라 규칙상 예제로 판단했습니다. 정답이 한 줄(`llm.with_structured_output(MovieReview)`)이고 Pydantic·Tool Calling은 이 권에서 배우므로 과제로 돌려도 됩니다.
2. **04의 deprecation 경고를 어떻게 할까요?** (가) 접힌 준비 셀에서 이 경고만 숨긴다(QC 통과, 강사용 메모에 "LangGraph 방식을 권장한다는 경고"라고 적음) (나) 그대로 보여 주고 "그래서 다음 장에서 LangGraph 방식을 본다"는 연결로 쓴다(QC 경고 기준과 부딪힘). 추천은 (가).
3. **원본 코드 안의 파일 경로를 고쳐도 될까요?** 02 주석 3줄(`05-langgraph/03_tool_node.py 참고`)과 04 출력 문자열(`05_memory_langgraph.py`)입니다. 추천: 주석은 지우고, 출력 문자열의 파일 이름만 "LangGraph 방식"으로 줄입니다. 원본 내용 변경이라 확인을 받습니다.
