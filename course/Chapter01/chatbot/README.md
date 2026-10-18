# 나의 챗봇 (1·2일차 챗봇 트랙)

장을 배울 때마다 같은 챗봇을 한 단계씩 키웁니다.

| 단계 | 실습 | 고칠 파일 | 더하는 것 |
|---|---|---|---|
| 1단계 | 1-2 LLM API | `stage1.py` | LangChain 호출, 답을 조각으로 보여 주기, 프롬프트 템플릿 |
| 2단계 | 1-3 LangChain | `stage2.py` | LCEL 체인, 대화 기억, 계산기 도구, 정리 카드 |
| 3단계 | 1-4 RAG | `stage3.py` | 약관 검색(RAG), 근거 보여 주기, 사내 RAGaaS |
| 4단계 | 2-1 LangGraph | `stage4.py` | 에이전트 그래프, 그래프 기억, 사람 승인 |
| 5단계 | 2-3 Streamlit | `stage5.py` | 하나로 합친 최종 챗봇 |

공통으로 알아 둘 것:

- 화면(입력창, 대화 기록, "대화 지우기" 버튼)은 `ui.py`가 그립니다. `ui.py`는 고치지 않습니다(5단계에서 열어 읽어 봅니다).
- 단계 파일에서 주로 바꾸는 곳은 질문에 답하는 `answer(question, history)` 함수입니다. `question`은 이번 질문, `history`는 앞의 대화(`{"role": ..., "content": ...}` 목록)입니다. 답은 문자열로 돌려주거나, 글자 조각을 하나씩 `yield`로 내보냅니다.
- `log_step("제목", 내용)`을 부르면 답 아래에 접힌 상자(실행 기록)가 생기고, 터미널에도 같은 내용이 찍힙니다. 채점할 때 이 기록을 봅니다.
- 고칠 자리는 `# ✍️ 목표 N:` 주석으로 표시되어 있습니다. 채우기 전에도 앱은 뜨고, 앞 단계까지의 기능은 그대로 동작합니다.
- 각 단계 파일에는 **앞 단계 완성본이 이미 들어 있습니다.** 앞 단계를 다 못 했어도 그 단계 파일부터 시작하면 됩니다.

실행은 저장소 맨 위 폴더의 터미널에서 합니다. 브라우저에 챗봇이 열립니다. 끝낼 때는 터미널에서 `Ctrl + C`를 누릅니다. 파일을 고친 뒤에는 저장(`Ctrl + S`)하고 브라우저에서 `R`을 누르면 다시 읽습니다.

막히면 오류 메시지는 마지막 줄만이 아니라 **오류 메시지 전체**(터미널과 브라우저에 나온 것)를 복사해 AI에게 붙여 넣고, 원인과 고칠 곳을 물어봅니다.

---

## 1단계: LangChain으로 부르고 답을 조각으로 보여 주기 (1-2)

### 학습 목표

3. LangChain(`get_llm()`)으로 호출하고 `stream()`으로 답을 조각 단위로 화면에 보여 줄 수 있다
4. system·user를 나눈 `ChatPromptTemplate`에 변수를 넣어 호출할 수 있다

(목표 1·2는 터미널 과제 `course/Chapter01/tasks/1-2/`에서 합니다.)

### 준비

`course/Chapter01/chatbot/stage1.py`를 엽니다. 사이드바의 "답 말투" 선택 상자(`style`)와 `llm = get_llm()`은 이미 있습니다.

### 할 일

- **목표 4**: `prompt`를 system 메시지(역할과 `{style}` 말투)와 human 메시지(`{question}`)로 나눈 `ChatPromptTemplate`으로 만듭니다. `answer` 안에서 `style`과 `question`을 넣어 보낼 메시지를 만들고, `log_step("모델에 보낸 메시지", …)`로 남깁니다.
- **목표 3**: 그 메시지를 `llm.stream()`으로 보내 받은 조각의 글자(`content`)를 하나씩 `yield`합니다. 다 받은 뒤 받은 조각 수를 `log_step("받은 조각 수", …)`으로 남깁니다. 맨 아래 `return "아직 답하는 코드가 없습니다…"` 줄은 지웁니다.

### 프롬프트 힌트

- **목표 4**: 템플릿의 두 메시지에 무엇을 쓰고 변수 이름을 무엇으로 할지(`style`, `question`) AI에게 정해 줍니다. 사이드바에서 고른 `style`이 system 메시지에 들어가야 한다고 적습니다.
- **목표 3**: `ui.py`가 제너레이터를 받으면 `st.write_stream`으로 보여 준다고 알려 주고, `answer`가 `llm.stream()`의 조각을 `yield`하게 해 달라고 합니다. 조각 수를 세어 `log_step`으로 남기라는 것도 적습니다.

### 실행

```
uv run --env-file .env streamlit run course/Chapter01/chatbot/stage1.py
```

말투를 바꿔 가며 질문해 봅니다. 답이 글자 조각으로 이어서 나타나고, 답 아래 "모델에 보낸 메시지", "받은 조각 수" 상자가 생기면 됩니다.

### 채점받기

AI에게 **"챗봇 1단계 채점해 줘"**라고 말합니다.

---

## 2단계: 기억하고 도구 쓰는 챗봇 (1-3)

### 학습 목표

1. `prompt | llm | StrOutputParser()` LCEL 체인으로 답할 수 있다
2. `MessagesPlaceholder("history")`에 이전 대화를 넣어 앞의 말을 기억하게 할 수 있다
3. `@tool`을 `bind_tools`로 연결하고 `tool_calls`를 실행해 `ToolMessage`로 돌려 최종 답을 받을 수 있다
4. Pydantic 스키마로 답을 정해진 모양으로 받아 보여 줄 수 있다

### 준비

`course/Chapter01/chatbot/stage2.py`를 엽니다. 사이드바에 "답 방식"(대화 / 계산기 도구 / 정리 카드)이 생겼습니다. 답 방식마다 답하는 함수가 하나씩 있습니다(`chat_answer`, `tool_answer`, `card_answer`). "대화"에는 1단계 완성본이 들어 있습니다.

### 할 일

- **목표 1** (`chat_answer`): `chain = prompt | llm | StrOutputParser()`를 만들고, `chat_answer`가 `chain.stream()`으로 받은 글자 조각을 `yield`하게 바꿉니다. "모델에 보낸 메시지"와 "받은 조각 수" 기록은 그대로 남깁니다.
- **목표 2** (`prompt`): `prompt`의 system과 human 사이에 `MessagesPlaceholder("history")`를 넣고, 체인을 부를 때 `history`(앞의 대화)를 함께 넣습니다.
- **목표 3** (`tool_answer`): 수식을 계산하는 `@tool` 함수를 만들어 `llm.bind_tools`로 연결합니다. 답에 `tool_calls`가 있으면 그 도구를 실행해 결과를 `ToolMessage`로 돌려주고, 도구 호출이 없는 최종 답을 돌려줍니다. 도구를 실행할 때마다 `log_step("도구 실행", …)`으로 도구 이름·인자·결과를 남깁니다.
- **목표 4** (`card_answer`): 제목(`title`)·한 줄 요약(`summary`)·핵심 3가지(`points`)를 담는 Pydantic 스키마를 만들고, `PydanticOutputParser`로 답을 그 모양으로 받습니다. 받은 카드는 `log_step("받은 카드", …)`으로 남기고, 화면에는 제목·요약·핵심 목록을 마크다운 글로 바꿔 돌려줍니다.

### 프롬프트 힌트

- **목표 1**: 지금 `chat_answer`의 1단계 코드를 LCEL 체인 방식으로 바꿔 달라고 하고, 체인 모양(`prompt | llm | StrOutputParser()`)을 직접 적어 줍니다. 조각을 `yield`하는 방식과 `log_step` 기록은 그대로 두라고 적습니다.
- **목표 2**: `history`가 `{"role": ..., "content": ...}` 목록이라는 것과, 템플릿 어디에 `MessagesPlaceholder`를 넣을지 알려 줍니다. 무엇을 확인할지(이름을 말한 뒤 "내 이름이 뭐야?")도 적어 주면 좋습니다.
- **목표 3**: 노트북에서 본 수동 도구 호출 루프(`bind_tools` → `tool_calls` → 도구 실행 → `ToolMessage`)대로 짜 달라고 합니다. 도구가 할 일과 `log_step`으로 남길 내용을 정해 줍니다.
- **목표 4**: 스키마의 칸 이름과 뜻을 정해 주고, 노트북에서 본 `PydanticOutputParser`와 `format_instructions` 방식으로 받게 합니다. 화면에 보여 줄 모양(제목, 요약, 핵심 목록)도 적어 줍니다.

### 실행

```
uv run --env-file .env streamlit run course/Chapter01/chatbot/stage2.py
```

"대화"에서 "내 이름은 민수야" 다음에 "내 이름이 뭐야?"를 묻고, "계산기 도구"에서 "1234 곱하기 5678은 얼마야?"를, "정리 카드"에서 "재택근무의 장단점을 정리해 줘."를 물어봅니다.

### 채점받기

AI에게 **"챗봇 2단계 채점해 줘"**라고 말합니다.

---

## 3단계: 약관 RAG 챗봇 (1-4)

### 학습 목표

1. PDF 읽기·분할·`get_embeddings()`·Chroma 저장을 `@st.cache_resource`로 한 번만 만들 수 있다
2. `as_retriever(search_kwargs={"k": 3})`로 찾은 청크를 context로 넣어 답하고 근거를 보여 줄 수 있다
3. 맥락에 없는 질문에는 "문서에서 확인할 수 없습니다"라고 답하게 할 수 있다
4. 검색 방식(로컬 Chroma / 사내 RAGaaS)을 골라 두 검색 결과를 비교할 수 있다(사내망)

### 준비

`course/Chapter01/chatbot/stage3.py`를 엽니다. "답 방식"에 "약관 질문"이, 사이드바에 "검색 방식"(로컬 Chroma / 사내 RAGaaS)이 생겼습니다. 약관 PDF 위치는 `PDF_PATH`에 이미 있습니다(노트북 폴더의 `data/meritz_pet_insurance.pdf`). 채울 곳은 "약관 질문" 부분(`search`, `rag_answer`와 그 위)입니다.

### 할 일

- **목표 1**: `@st.cache_resource`를 붙인 함수 `load_vectorstore()`를 만듭니다. `PDFMinerLoader`로 PDF를 읽고, `RecursiveCharacterTextSplitter`(500자, 겹침 75자)로 나누고, `get_embeddings()`로 Chroma에 저장해 돌려줍니다. 저장한 뒤 `print(f"[벡터 저장소] 청크 {개수}개 저장")`을 남깁니다.
- **목표 2**: `search(question)`이 `as_retriever(search_kwargs={"k": 3})`로 찾은 청크 3개의 글(`page_content`) 목록을 돌려주게 합니다. `rag_answer`는 찾은 글을 `log_step("근거 (검색 방식, 개수)", …)`으로 남기고, 글을 합쳐 프롬프트의 `{context}`에 넣어 답을 조각으로 돌려줍니다(`… | llm | StrOutputParser()` 체인의 `.stream()`).
- **목표 3**: 프롬프트의 system 메시지에 "context만 근거로 답하고, context에 없으면 '문서에서 확인할 수 없습니다'라고만 답하라"는 규칙을 넣습니다.
- **목표 4**: 검색 방식이 "사내 RAGaaS"이면 `config.ragaas`의 `post_ragaas("retrieve-rrf", payload)`로 찾은 글 3개를 돌려주게 `search`를 나눕니다. 사외 PC에서는 `[MOCK RAGaaS]`로 시작하는 연습용 글이 오고, 실제 약관 검색은 사내망에서만 됩니다.

### 프롬프트 힌트

- **목표 1**: 노트북에서 본 순서(읽기 → 나누기 → 임베딩 → Chroma)를 함수 하나로 묶고 `@st.cache_resource`를 붙여 달라고 합니다. Streamlit은 질문마다 파일 전체를 다시 실행하므로, 한 번만 만들어야 하는 까닭도 함께 설명해 달라고 하면 좋습니다.
- **목표 2·3**: `search`가 돌려줄 것(글 3개 목록)과 `rag_answer`가 할 일(근거 기록 → context에 넣기 → 조각으로 답)을 차례대로 적어 줍니다. 문서에 없는 질문에 할 말을 따옴표로 정확히 적어 줍니다.
- **목표 4**: `course/agent_docs/ragaas.md`의 검색(`retrieve-rrf`) 예시대로 `post_ragaas`를 쓰라고 하고, 주소·키를 코드에 쓰지 말라고 적습니다. 검색 방식에 따라 `search` 안에서 갈라지게 해 달라고 합니다.

### 실행

```
uv run --env-file .env streamlit run course/Chapter01/chatbot/stage3.py
```

"약관 질문"에서 "반려견이 수술을 받으면 수술비도 보장되나요?"와 "삼성전자의 오늘 주가는 얼마야?"를 물어봅니다. 첫 질문은 PDF를 읽고 임베딩하느라 조금 걸립니다. 같은 질문을 검색 방식만 바꿔 다시 물어 근거 상자를 비교합니다.

### 채점받기

AI에게 **"챗봇 3단계 채점해 줘"**라고 말합니다.

---

## 4단계: LangGraph 에이전트 챗봇 (2-1)

### 학습 목표

1. `StateGraph`에 agent 노드와 `ToolNode`를 넣고 `Literal` 반환 갈림길 함수로 conditional edge를 이어 compile할 수 있다
2. 약관 검색을 `@tool search_policy`로 바꿔 약관 질문에서만 tools 노드를 거치게 할 수 있다
3. `MemorySaver`와 `thread_id`로 대화 기억을 그래프에 맡길 수 있다
4. `interrupt_before`로 도구 실행 전에 멈추고 승인·거부로 재개할 수 있다

### 준비

`course/Chapter01/chatbot/stage4.py`를 엽니다. "답 방식"에 "에이전트"가, 사이드바에 "도구 실행 전 승인 받기" 토글(`need_approval`)이 생겼습니다. 채울 곳은 "에이전트" 부분입니다. 그 안의 `run_graph`(그래프를 실행하며 지나간 노드를 `log_step("노드 순서", …)`로 남기고 마지막 답을 돌려줌)와 `approval_buttons`(그래프가 멈춰 있으면 승인/거부 버튼을 보여 줌)는 이미 있으니 그대로 둡니다.

### 할 일

- **목표 2**: 3단계의 `search(question)`을 쓰는 `@tool search_policy(query: str) -> str`를 만듭니다. docstring에 "펫보험 약관에 관한 질문일 때만 쓴다"처럼 언제 쓰는지 적습니다.
- **목표 1**: `StateGraph(MessagesState)`에 `"agent"` 노드(도구를 `bind_tools`한 모델을 부름, 인사·일반 질문은 도구 없이 답하라는 system 메시지를 앞에 붙임)와 `"tools"` 노드(`ToolNode`)를 넣습니다. 반환 타입이 `Literal["tools", "__end__"]`인 갈림길 함수로 `add_conditional_edges("agent", …)`를 잇고, tools → agent로 되돌아가는 엣지를 넣어 `agent_graph`로 compile합니다.
- **목표 3**: `@st.cache_resource`로 한 번만 만든 `MemorySaver()`를 compile의 `checkpointer`로 줍니다. `agent_answer`는 `{"configurable": {"thread_id": st.session_state.thread_id}}`를 config로 만들고, `history`가 아니라 **이번 질문 하나만** 넣어 `run_graph`로 실행합니다.
- **목표 4**: 토글이 켜져 있으면 `interrupt_before=["tools"]`로 compile합니다. `resume(approved)`는 승인이면 `run_graph(None, config)`로 멈춘 곳부터 이어 가고, 거부면 대기 중인 도구 호출마다 거부 `ToolMessage`를 만들어 `agent_graph.update_state(config, …, as_node="tools")`로 넣은 뒤 이어 갑니다.

### 프롬프트 힌트

- **목표 1·2**: 노트북에서 본 agent → tools → agent 그래프를 직접 조립하되, `tools_condition` 대신 반환 타입이 `Literal`인 갈림길 함수를 쓰라고 적습니다. 도구의 docstring과 system 메시지가 "언제 도구를 쓸지"를 정한다는 것도 알려 줍니다.
- **목표 3**: Streamlit은 질문마다 파일을 다시 실행하므로 `MemorySaver`를 `@st.cache_resource`로 한 번만 만들어야 한다고 알려 줍니다. 그래프에 질문 하나만 넣고 기억은 `thread_id`에 맡기라고 적습니다.
- **목표 4**: 노트북의 사람 승인(`interrupt_before`, `invoke(None, …)`, `update_state(…, as_node="tools")`) 방식대로 `resume`을 짜 달라고 합니다. 버튼 코드(`approval_buttons`)는 고치지 말라고 적습니다.

### 실행

```
uv run --env-file .env streamlit run course/Chapter01/chatbot/stage4.py
```

"에이전트"에서 "안녕! 내 이름은 민수야." → "반려견이 수술을 받으면 수술비도 보장되나요?" → "내 이름이 뭐야?"를 묻고 "노드 순서" 상자를 봅니다. 토글을 켜고 약관 질문을 하면 승인/거부 버튼이 나옵니다. "대화 지우기"를 누르면 새 `thread_id`로 바뀌어 이름을 잊습니다.

### 채점받기

AI에게 **"챗봇 4단계 채점해 줘"**라고 말합니다.

---

## 5단계: 하나로 합친 최종 챗봇 (2-3)

### 학습 목표

1. 일반 질문·약관 질문·기억 질문이 한 화면에서 모두 동작하는 최종 챗봇을 완성할 수 있다

### 준비

`course/Chapter01/chatbot/stage5.py`를 엽니다. 4단계 완성본이 들어 있습니다. 지금은 사이드바에서 "답 방식"을 골라야 기능이 바뀝니다. 이번에는 고르지 않아도 되는 챗봇으로 합칩니다.

먼저 `course/Chapter01/chatbot/ui.py`를 열어 읽어 봅니다(고치지는 않습니다). AI에게 이 파일을 붙여 넣고, `st.session_state`에 무엇을 두는지, 질문을 입력하면 파일이 위에서부터 다시 실행된다는 것이 무슨 뜻인지, `st.write_stream`이 언제 쓰이는지 설명해 달라고 합니다.

### 할 일

- **목표 1**: `answer`가 "답 방식"과 관계없이 늘 `agent_answer`를 부르게 합니다. 에이전트 도구 목록(`agent_tools`)에 2단계의 `calculate`를 더하고, system 메시지에 "계산이 필요하면 calculate를 쓴다"를 더합니다. 쓰지 않게 된 사이드바 "답 방식" 선택 상자는 지웁니다. 그 밖의 함수(`chat_answer` 등)는 남겨 두어도 됩니다.

### 프롬프트 힌트

- **목표 1**: 무엇을 하나로 합치려는지(일반 질문은 바로 답, 약관 질문은 `search_policy`, 계산은 `calculate`, 이름은 그래프 기억) AI에게 먼저 설명합니다. "답 방식" 선택 상자를 지울 때 그 이름(`mode`)을 쓰는 곳도 함께 정리해 달라고 합니다.

### 실행

```
uv run --env-file .env streamlit run course/Chapter01/chatbot/stage5.py
```

아무것도 고르지 않고 "안녕! 내 이름은 민수야." → "반려견이 수술을 받으면 수술비도 보장되나요?" → "내 이름이 뭐야?" → "1234 곱하기 5678은 얼마야?"를 차례로 물어봅니다.

### 채점받기

AI에게 **"챗봇 5단계 채점해 줘"**라고 말합니다.
