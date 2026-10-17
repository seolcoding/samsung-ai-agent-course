"""동물보험 챗봇을 8단계로 발전시키는 학습 내용. 화면의 글은 모두 여기서 고친다."""

COMMON_QUESTION = "보험금 청구 절차와 필요한 서류를 알려줘."
MEMORY_TELL = "우리 강아지 이름은 콩이야. 기억해 줘."
MEMORY_ASK = "우리 강아지 이름이 뭐였지?"
PHOTO_QUESTION = "고양이 사진을 보여 주고 출처도 알려줘."
LAPSE_QUESTION = "보험료를 깜빡하고 안 냈는데 계약을 다시 살릴 수 있어?"
COST_QUESTION = "진료비 35000원, 검사비 45000원, 약값 12000원이면 모두 얼마야?"

STAGES = {
    1: {
        "name": "날것의 LLM API", "slug": "raw_llm", "icon": "chat",
        "change": "OpenAI SDK로 질문을 모델에 그대로 보냅니다. 도구도 문서도 기억도 없는 LLM의 맨얼굴입니다.",
        "why": "LLM이 무엇을 못 하는지 직접 겪어 봐야, 다음 단계에서 붙이는 부품이 왜 필요한지 보입니다.",
        "concepts": ["Chat Completions", "messages", "환각", "무상태"],
        "memory": False,
        "diagram": """flowchart TD
  Q[질문] --> M["messages = [user: 질문]"] --> S[OpenAI SDK] --> L[LLM] --> A[답변]""",
        "code": '''from openai import OpenAI

client = OpenAI()                       # OPENAI_API_KEY를 환경변수에서 읽는다
response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": question}],
)
print(response.choices[0].message.content)''',
        "prompt": """OpenAI SDK로 질문 하나를 보내고 답을 출력하는 Streamlit 채팅 앱을 만들어 줘.

- 모델 이름과 API 키는 환경변수(OPENAI_MODEL, OPENAI_API_KEY)에서 읽는다.
- st.chat_input으로 질문을 받고, client.chat.completions.create의
  messages에는 이번 질문 하나만 넣는다.
- 답은 st.chat_message("assistant")로 보여 준다.
- 화면에는 이전 질문과 답을 계속 보여 주되, 모델에는 이전 대화를 보내지 않는다.""",
        "checks": [
            "질문을 보내면 모델의 답이 화면에 나온다",
            "보험 PDF 질문에 '문서를 볼 수 없다'고 하거나 지어낸다",
            "사진을 직접 보여 주지 못한다",
            "강아지 이름을 말한 뒤 다시 물으면 기억하지 못한다",
        ],
        "examples": [COMMON_QUESTION, PHOTO_QUESTION, MEMORY_TELL, MEMORY_ASK],
        "notes": """- 이 단계에서 확인할 **한계 네 가지**: ① 우리 문서를 모른다 ② 사진·실시간 정보를 가져오지 못한다 ③ 이전 대화를 기억하지 못한다 ④ 모르면서 그럴듯하게 지어낼 수 있다.
- 사진을 달라고 하면 모델이 그럴듯한 이미지 주소를 지어내기도 합니다. 이 앱은 그런 주소를 그림으로 그리지 않고 "확인 안 됨"으로 표시합니다. 실제로 찾아온 사진은 4단계 도구부터입니다.
- 화면에는 대화가 쌓여 보여도, API는 매번 `messages`에 넣은 것만 봅니다. 이전 대화를 기억하는 것처럼 보이게 하려면 우리가 직접 이전 대화를 다시 보내야 합니다(3단계).
- 남은 단계는 이 한계를 하나씩 메웁니다: 형식(2) → 기억(3) → 도구(4·5) → 문서(6·7) → 스스로 점검(8).""",
    },
    2: {
        "name": "프롬프트 템플릿", "slug": "prompt_template", "icon": "edit_note",
        "change": "LangChain의 ChatPromptTemplate으로 역할과 답변 형식을 변수로 만들어, 매번 같은 규칙으로 답하게 합니다.",
        "why": "같은 질문이라도 지시를 어떻게 주느냐에 따라 답의 말투·형식·신중함이 달라집니다.",
        "concepts": ["ChatPromptTemplate", "system / human", "입력 변수", "ChatOpenAI"],
        "memory": False,
        "diagram": """flowchart TD
  V["변수: 역할 · 답변 형식 · 질문"] --> T[ChatPromptTemplate]
  T --> P["system: 너는 {role}다 ...
human: {question}"] --> L[ChatOpenAI] --> A[답변]""",
        "code": '''prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 {role}다. 한국어로 {style} 형식으로 답한다.\\n"
               "모르는 내용은 추측하지 말고 확인할 수 없다고 말한다."),
    ("human", "{question}"),
])
llm = ChatOpenAI(model=MODEL)

messages = prompt.invoke({"role": role, "style": style, "question": question})
answer = llm.invoke(messages).content''',
        "prompt": """1단계 앱을 LangChain으로 바꿔 줘.

- ChatOpenAI(config.llm의 get_llm())로 모델을 만든다.
- ChatPromptTemplate에 system(역할·답변 형식·"모르면 확인할 수 없다고 말한다")과
  human({question})을 둔다. 변수는 role, style, question.
- 사이드바에 역할(st.text_input)과 답변 형식(짧은 문단/글머리표, st.segmented_control)을 두고,
  바꾸면 다음 질문부터 반영되게 해 줘.
- 실제로 모델에 들어간 메시지를 st.expander에 보여 줘.""",
        "checks": [
            "역할·형식·질문이 실제 프롬프트에 들어간다",
            "답변 형식을 바꾸면 같은 질문의 답 모양이 바뀐다",
            "보험 질문에 지어내지 않고 확인할 수 없다고 답한다",
            "프롬프트만으로 문서 지식이 생기지 않음을 확인했다",
        ],
        "examples": [COMMON_QUESTION, "반려견 보험에 가입할 때 주의할 점을 알려줘."],
        "notes": """- 1단계와 같은 보험 질문을 해 보세요. "모르면 모른다고 말하라"는 지시 덕분에 지어내는 일은 줄지만, **문서 지식이 생기지는 않습니다.**
- 템플릿은 문자열 이어 붙이기를 대신하는 부품입니다. 변수를 바꿔 끼우기 쉽고, 실제로 들어간 메시지를 확인하기 쉽습니다.
- 아직 이전 대화를 기억하지 못합니다. → 3단계에서 체인에 대화 기록을 붙입니다.""",
    },
    3: {
        "name": "LCEL 체인 + 대화 기억", "slug": "lcel_chain", "icon": "link",
        "change": "프롬프트 | 모델 | 파서를 하나의 체인으로 잇고, 이전 대화를 MessagesPlaceholder로 함께 보내 기억하게 합니다.",
        "why": "부품을 | 로 이으면 갈아 끼우기 쉽고, 대화 기록을 넣는 자리도 템플릿 안에 정해 둘 수 있습니다.",
        "concepts": ["LCEL |", "Runnable", "StrOutputParser", "MessagesPlaceholder", "stream"],
        "memory": True,
        "diagram": """flowchart TD
  H[(이전 대화)] --> P
  Q[질문] --> P["prompt
system · history · human"]
  P --> L[llm] --> O[StrOutputParser] --> A[답변 스트림]
  A -->|이번 질문과 답 저장| H""",
        "code": '''prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 {role}다. 한국어로 {style} 형식으로 답한다."),
    MessagesPlaceholder("history"),          # 이전 대화가 들어갈 자리
    ("human", "{question}"),
])
chain = prompt | llm | StrOutputParser()

history = []                                 # [("human", ...), ("ai", ...), ...]
for piece in chain.stream({"role": role, "style": style,
                           "history": history, "question": question}):
    print(piece, end="")
history += [("human", question), ("ai", answer)]''',
        "prompt": """2단계 앱을 LCEL 체인으로 바꾸고 대화를 기억하게 해 줘.

- chain = prompt | llm | StrOutputParser()
- 프롬프트의 system과 human 사이에 MessagesPlaceholder("history")를 넣는다.
- 대화 기록은 st.session_state에 [("human", 질문), ("ai", 답)] 형태로 쌓고,
  매 질문마다 history로 넘긴다.
- 답은 st.write_stream(chain.stream(...))으로 흘러나오게 보여 준다.
- '대화 지우기' 버튼으로 기록을 비울 수 있게 해 줘.""",
        "checks": [
            "체인이 prompt | llm | parser 순서로 연결된다",
            "답이 흘러나오듯 표시된다",
            "강아지 이름을 말한 뒤 다시 물으면 기억한다",
            "대화를 지우면 다시 기억하지 못한다",
        ],
        "examples": [MEMORY_TELL, MEMORY_ASK, COMMON_QUESTION],
        "notes": """- **기억의 정체**: 모델이 기억하는 것이 아니라, 우리가 이전 대화를 매번 다시 보내는 것입니다. 대화가 길어지면 보내는 글자 수(비용)도 늘어납니다.
- 아래 **실행 기록**에서 history에 이전 대화가 실제로 들어간 것을 확인하세요.
- 수업 1-3의 `RunnableWithMessageHistory`는 이 기록 관리를 자동으로 해 주는 포장지입니다.
- **한계**: 여전히 문서·사진·실시간 정보를 가져오지 못합니다. → 4단계에서 도구를 붙입니다.""",
    },
    4: {
        "name": "Tool Calling", "slug": "tool_calling", "icon": "build",
        "change": "모델에게 위키피디아·사진·합계·PDF 쪽 읽기 도구를 알려 줍니다. 모델이 도구를 고르면 파이썬이 실행해 결과를 돌려줍니다.",
        "why": "모델이 못 하는 일(조회·계산·파일 읽기)은 우리 코드가 하고, 모델은 무엇을 할지만 정합니다.",
        "concepts": ["@tool", "bind_tools", "tool_calls", "ToolMessage", "호출 루프"],
        "memory": True,
        "diagram": """flowchart TD
  Q[질문 + 이전 대화] --> M[LLM + 도구 목록]
  M -->|tool_calls| T["파이썬이 도구 실행
위키피디아 · 사진 · 합계 · PDF 쪽 읽기"]
  T -->|ToolMessage| M
  M -->|도구 필요 없음| A[최종 답변]""",
        "code": '''@tool
def insurance_pdf_page(page: int) -> dict:
    """동물보험 PDF의 지정한 쪽(1~28)을 읽는다."""
    ...

tools = {t.name: t for t in [wikipedia_search, animal_photo, cost_sum, insurance_pdf_page]}
llm_with_tools = llm.bind_tools(list(tools.values()))

messages = [SystemMessage(system), *history, HumanMessage(question)]
for _ in range(MAX_TOOL_ROUNDS):
    response = llm_with_tools.invoke(messages)
    messages.append(response)
    if not response.tool_calls:                 # 도구가 더 필요 없으면 끝
        break
    for call in response.tool_calls:            # 모델이 고른 도구를 파이썬이 실행
        result = tools[call["name"]].invoke(call["args"])
        messages.append(ToolMessage(json.dumps(result), tool_call_id=call["id"]))
answer = response.content''',
        "prompt": """3단계 챗봇에 도구를 붙여 모델이 골라 쓰게 해 줘.

도구 4개를 @tool로 만든다(docstring에 언제 쓰는지 적는다):
- wikipedia_search(query): 동물 위키피디아 요약과 URL
- animal_photo(animal): Wikimedia Commons 사진과 저작자·라이선스
- cost_sum(amounts): 비용 합계
- insurance_pdf_page(page): 보험 PDF의 지정 쪽(1~28) 텍스트

llm.bind_tools로 연결하고, tool_calls가 없을 때까지 도구 실행 → ToolMessage 전달을 반복한다.
반복은 최대 8회. 이전 대화(history)는 3단계처럼 함께 보낸다.
화면에는 호출된 도구 이름·인수·결과를 펼쳐 볼 수 있게 보여 줘.""",
        "checks": [
            "질문에 맞는 도구가 호출된다(사진→animal_photo, 합계→cost_sum)",
            "도구 결과가 ToolMessage로 모델에 돌아가 최종 답이 나온다",
            "사진의 출처·저작자·라이선스가 보인다",
            "보험 질문에서 모델이 몇 쪽을 읽을지 짐작하며 헤매는 것을 확인했다",
        ],
        "examples": [PHOTO_QUESTION, COST_QUESTION, COMMON_QUESTION],
        "notes": """- 보험 질문을 해 보고 **실행 기록**을 펼쳐 보세요. 모델은 28쪽 중 어디에 답이 있는지 몰라 쪽번호를 짐작해 여러 번 읽습니다. 이 앱은 질문당 4쪽까지만 읽게 막아 두었습니다. 그 안에 못 찾으면 못 찾았다고 답해야 합니다. → 6단계에서 "질문과 비슷한 부분을 찾아 주는" 검색(RAG)으로 해결합니다.
- 도구의 docstring이 곧 모델에게 주는 설명서입니다. 설명이 모호하면 엉뚱한 도구를 고릅니다.
- 반복 횟수 제한이 없으면 모델이 도구를 끝없이 부를 수 있습니다.""",
    },
    5: {
        "name": "LangGraph 기본", "slug": "langgraph", "icon": "account_tree",
        "change": "4단계의 for 문 루프를 agent·tools 노드와 조건부 분기로 옮기고, 대화 기억은 checkpointer가 맡습니다.",
        "why": "흐름이 그래프로 드러나면 노드를 더하거나 중간 상태를 저장·관찰하기 쉬워집니다.",
        "concepts": ["State", "Node", "Edge", "조건부 분기", "checkpointer · thread_id"],
        "memory": True,
        "diagram": None,
        "code": '''builder = StateGraph(AgentState)
builder.add_node("agent", agent)        # 모델: 도구 요청 또는 최종 답변
builder.add_node("tools", tools_node)   # 파이썬: 도구 실행

def route(state):                       # 도구 요청이 있으면 tools, 없으면 끝
    return "tools" if state["messages"][-1].tool_calls else END

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", route, {"tools": "tools", END: END})
builder.add_edge("tools", "agent")
graph = builder.compile(checkpointer=MemorySaver())   # 대화 기억

config = {"configurable": {"thread_id": "수강생-1"}}  # 같은 thread_id = 같은 대화
graph.invoke({"messages": [HumanMessage(question)]}, config)''',
        "prompt": """4단계 챗봇의 도구 호출 for 문을 LangGraph로 바꿔 줘.

- State: messages(add_messages로 누적)
- 노드 agent: llm_with_tools.invoke(messages) 결과를 추가
- 노드 tools: 마지막 메시지의 tool_calls를 실행하고 ToolMessage를 추가
- START → agent, agent → (tool_calls 있으면) tools / (없으면) END, tools → agent
- compile(checkpointer=MemorySaver())로 대화를 기억하고,
  thread_id는 st.session_state에 정해 둔 값을 쓴다. history를 직접 넘기지 않는다.
- graph.get_graph().draw_mermaid()로 그래프 그림을 보여 주고,
  graph.stream(stream_mode="updates")로 방문한 노드 순서를 기록해 줘.""",
        "checks": [
            "그림의 agent·tools·END 연결이 코드와 같다",
            "방문 순서가 agent → tools → agent 처럼 기록된다",
            "history를 넘기지 않아도 checkpointer로 이전 대화를 기억한다",
            "4단계와 같은 질문에 비슷한 도구 호출이 일어난다",
        ],
        "examples": ["고양이의 특징을 위키피디아에서 찾아 알려줘.", MEMORY_TELL, MEMORY_ASK, COMMON_QUESTION],
        "notes": """- 4단계와 같은 질문을 해 보세요. 하는 일은 같고, **방문 순서**가 새로 보입니다.
- 위 그림은 손으로 그린 것이 아니라 실행에 쓰는 그래프의 `draw_mermaid()` 결과입니다.
- 3단계는 우리가 history를 들고 다녔지만, 여기서는 checkpointer가 thread_id별로 State를 저장합니다. thread_id를 바꾸면 새 대화가 됩니다.
- **한계**: 도구가 있어도 보험 PDF에서 답을 찾는 일은 여전히 짐작에 기댑니다. → 6단계 RAG.""",
    },
    6: {
        "name": "Naive 벡터 RAG", "slug": "naive_rag", "icon": "search",
        "change": "PDF를 잘게 나눠 임베딩해 두고, 질문과 비슷한 청크를 찾아 프롬프트에 넣어 답하게 합니다.",
        "why": "모델을 다시 학습시키지 않고 우리 문서를 근거로 답하게 하는 가장 기본적인 방법입니다.",
        "concepts": ["불러오기", "나누기", "임베딩·저장", "검색", "생성", "[PDF N쪽]"],
        "memory": True,
        "diagram": """flowchart TD
  P[PDF] --> S["① 불러오기 ② 나누기 ③ 임베딩"] --> V[(Chroma)]
  Q[질문] --> R["④ 검색 top_k"]
  V --> R --> C["[PDF N쪽] 붙인 context"]
  C --> G["⑤ prompt | llm | parser"]
  Q --> G
  G --> A["답변 + [PDF N쪽]"]""",
        "code": '''# ①불러오기 ②나누기 ③임베딩·저장 — 앱 시작 때 한 번
docs = PyPDFLoader(PDF_PATH).load()                  # PDF 한 쪽 = Document 하나
chunks = RecursiveCharacterTextSplitter(
    chunk_size=600, chunk_overlap=100).split_documents(docs)
store = Chroma.from_documents(chunks, get_embeddings())
retriever = store.as_retriever(search_kwargs={"k": 3})

# ④검색 ⑤생성 — 질문마다
rag_chain = (
    {"context": itemgetter("question") | retriever | format_docs,
     "question": itemgetter("question"), "history": itemgetter("history")}
    | rag_prompt            # "context만 근거로 답하고 [PDF N쪽]을 붙인다"
    | llm
    | StrOutputParser()
)
answer = rag_chain.invoke({"question": question, "history": history})''',
        "prompt": """data/meritz_pet_insurance.pdf로 답하는 Naive RAG 챗봇을 만들어 줘.

1. PyPDFLoader로 쪽 단위로 불러오고, RecursiveCharacterTextSplitter(600, 100)로 나눈다.
2. config.embeddings의 get_embeddings()로 Chroma에 저장한다(@st.cache_resource로 한 번만).
3. retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
4. format_docs는 청크마다 앞에 [PDF {쪽번호}쪽]을 붙여 합친다.
5. 프롬프트: "context만 근거로 답한다. 문장 끝에 [PDF N쪽]을 붙인다.
   context에 없으면 '문서에서 확인할 수 없습니다'라고 답한다." + 3단계의 history 자리.
6. 체인으로 연결하고, 답변 아래 st.expander에 검색된 청크와 쪽번호를 보여 줘.""",
        "checks": [
            "청구 절차 질문에 PDF 내용과 [PDF N쪽]으로 답한다",
            "답변의 쪽번호가 검색된 청크의 쪽번호와 맞는다",
            "문서에 없는 질문(월 보험료)에 지어내지 않는다",
            "4단계보다 LLM 호출이 적고 빠른 것을 확인했다",
        ],
        "examples": [COMMON_QUESTION, "우리 집 반려견의 월 보험료는 얼마야?", LAPSE_QUESTION],
        "notes": """- 4단계와 같은 보험 질문을 해 보세요. 쪽을 짐작하지 않고 한 번의 검색으로 근거를 찾습니다.
- 수업 1-4 실습은 `PDFMinerLoader`로 PDF 전체를 문서 하나로 읽었습니다. 근거 쪽번호를 보이려면 쪽 단위로 읽는 `PyPDFLoader`가 편합니다.
- 청크가 너무 크면 엉뚱한 내용이 섞이고, 너무 작으면 문장이 잘립니다. 아래 **설정**에서 청크 크기와 검색 수를 바꿔 보세요.
- **한계**: 질문을 그대로 검색하므로 말투가 문서와 다르면("깜빡하고 안 냈어") 못 찾고, 비슷해 보이기만 한 청크도 섞입니다. → 7단계 Advanced RAG.""",
    },
    7: {
        "name": "Advanced RAG", "slug": "advanced_rag", "icon": "manage_search",
        "change": "검색 앞뒤를 보강합니다. 질문을 검색어로 다시 쓰고(Query Rewrite), 벡터+키워드로 찾고(Hybrid), 관련도로 다시 줄 세웁니다(Re-ranking).",
        "why": "RAG의 답 품질은 검색이 좌우합니다. 검색이 틀리면 생성이 좋아도 답이 흔들립니다.",
        "concepts": ["Query Rewrite", "Hybrid Search", "RRF", "Re-ranking"],
        "memory": True,
        "diagram": """flowchart TD
  Q[질문] --> W["① Query Rewrite
LLM이 검색어 3개로"]
  W --> VS[벡터 검색]
  W --> KS[키워드 검색]
  VS --> F["② Hybrid: 순위 합치기 RRF"]
  KS --> F
  F --> R["③ Re-ranking
LLM이 관련도 0~3점"]
  R --> G["상위 top_k로 생성"] --> A["답변 + [PDF N쪽]"]""",
        "code": '''# ① Query Rewrite: 말투가 달라도 찾을 수 있게 검색어를 여러 개 만든다
queries = [question] + rewrite_chain.invoke({"question": question})

# ② Hybrid Search: 벡터(의미) + 키워드(글자) 결과를 순위로 합친다(RRF)
ranked = {}
for q in queries:
    for results in (store.similarity_search(q, k=6), keyword_search(q, k=6)):
        for rank, doc in enumerate(results):
            ranked[doc.id] = ranked.get(doc.id, 0) + 1 / (60 + rank)
candidates = sorted(ranked, key=ranked.get, reverse=True)[:8]

# ③ Re-ranking: LLM이 질문과의 관련도를 0~3점으로 매기고 상위만 쓴다
scores = rerank_chain.invoke({"question": question, "chunks": candidates})
context = format_docs(top_k_by_score(candidates, scores))
answer = (rag_prompt | llm | StrOutputParser()).invoke(
    {"context": context, "question": question, "history": history})''',
        "prompt": """6단계 Naive RAG의 검색을 세 가지로 보강해 줘.

1. Query Rewrite: LLM에게 질문을 약관 문서에서 찾기 좋은 검색어 3개로 바꾸게 하고
   JSON 목록으로 받는다. 원래 질문도 함께 쓴다.
2. Hybrid Search: 검색어마다 벡터 검색 6개 + 키워드 검색 6개를 하고,
   RRF(1/(60+순위))로 점수를 합쳐 상위 8개 후보를 고른다.
   키워드 검색은 글자 두 개씩 겹치는 비율로 간단히 구현한다.
3. Re-ranking: 후보 8개를 LLM에게 주고 질문과의 관련도를 0~3점 JSON으로 받아
   1점 이상 중 상위 3개만 context로 쓴다. JSON 해석에 실패하면 RRF 순서를 쓴다.
각 단계의 결과(검색어, 후보, 점수)를 st.expander에 보여 줘.""",
        "checks": [
            "검색어가 질문과 다른 표현으로 늘어난 것을 확인했다",
            "벡터와 키워드 검색 결과가 합쳐진 후보 목록이 보인다",
            "관련 없는 후보가 낮은 점수로 빠진다",
            "6단계에서 못 찾던 질문을 찾거나, 근거가 더 정확해졌다",
        ],
        "examples": [COMMON_QUESTION, LAPSE_QUESTION,
                     "통원 치료비에서 자기부담금은 얼마씩 빠져?"],
        "notes": """- 6단계에도 있는 질문("보험료를 깜빡하고 안 냈는데…")을 해 보고 6단계의 근거 쪽번호와 비교하세요.
- **Query Rewrite**는 사용자 말투와 문서 말투의 차이를 메웁니다("깜빡하고 안 냄" → "보험료 납입 연체", "부활").
- **Hybrid**: 벡터 검색은 뜻이 비슷한 것을, 키워드 검색은 "자기부담금"처럼 정확한 용어를 잘 찾습니다. RRF는 점수 대신 순위로 합쳐서 두 방식의 점수 단위가 달라도 됩니다.
- **Re-ranking**은 "비슷해 보이기만 한" 청크를 걸러 냅니다. LLM 호출이 늘어 느려지고 비용이 듭니다.
- **한계**: 정해진 순서로만 움직입니다. 사진·계산·여러 자료가 섞인 질문은 못 다룹니다. → 8단계에서 에이전트가 스스로 계획합니다.""",
    },
    8: {
        "name": "에이전틱 흐름", "slug": "agentic", "icon": "groups",
        "change": "LangGraph로 조사(researcher) → 작성(writer) → 검토(reviewer)를 나눕니다. 조사자는 RAG 검색·위키·사진·합계 도구를 스스로 골라 쓰고, 검토에서 걸리면 최대 2회 다시 씁니다.",
        "why": "정해진 파이프라인 대신 필요한 자료를 스스로 모으고, 근거와 어긋난 답을 스스로 고칠 기회를 줍니다.",
        "concepts": ["Agentic RAG", "역할 분리", "피드백 루프", "종료 조건"],
        "memory": True,
        "diagram": None,
        "code": '''builder.add_node("researcher", researcher)        # RAG 검색·위키·사진·합계 도구로 근거 수집
builder.add_node("researcher_tools", tools_node)
builder.add_node("writer", writer)                # 근거만으로 답변 작성
builder.add_node("reviewer", reviewer)            # 근거와 대조 → {"passed", "feedback"}

builder.add_edge(START, "researcher")
builder.add_conditional_edges("researcher", research_route)  # 도구 더 → tools / 끝 → writer
builder.add_edge("researcher_tools", "researcher")
builder.add_edge("writer", "reviewer")

def review_route(state):            # 통과 또는 2회 재작성 → 끝, 아니면 다시 작성
    if state["review"]["passed"] or state["rewrites"] >= 2:
        return END
    return "writer"
builder.add_conditional_edges("reviewer", review_route)''',
        "prompt": """5단계 그래프와 6단계 RAG 검색을 합쳐, 조사·작성·검토 3역할 에이전트를 만들어 줘.

- researcher: insurance_search(벡터 검색)·wikipedia_search·animal_photo·cost_sum 도구로
  근거를 모은다(5단계 agent·tools 루프와 같은 구조).
- writer: 질문, 모은 도구 결과, 이전 검토 의견을 받아 답변을 쓴다.
- reviewer: 답변을 도구 결과와 대조해 JSON {"passed": true/false, "feedback": "..."}만 출력한다.
- reviewer → passed면 END, 아니면 writer로. 재작성은 최대 2회.
- JSON을 해석할 수 없으면 실패로 표시하고 끝낸다.
화면에 방문 순서, 초안, 검토 의견을 펼쳐 볼 수 있게 보여 줘.""",
        "checks": [
            "보험과 동물이 섞인 질문에 필요한 도구를 각각 골라 쓴다",
            "검토 의견이 다음 writer 입력에 들어간다",
            "재작성 2회 뒤에도 미통과면 그 상태가 표시된다",
            "검토 결과를 정확성 점수로 표현하지 않는다",
        ],
        "examples": ["고양이의 특징과 보험금 청구 서류를 함께 알려줘.", COMMON_QUESTION],
        "notes": """- LLM 호출이 가장 많고 느립니다. 정확도가 중요하고 시간이 덜 중요한 일에 씁니다.
- 검토도 LLM이 합니다. "검토 통과"는 정답 보증이 아니라 **근거와 어긋나지 않는다는 모델의 의견**입니다.
- 검토 응답을 JSON으로 받는 이유: 다음 노드로 갈지 코드가 판단해야 하기 때문입니다. 형식이 깨지면 실패로 처리합니다.
- 다음 과정(M2)의 멀티 에이전트·하네스가 이 구조를 더 키운 것입니다.""",
    },
    9: {
        "name": "비교·자기채점", "slug": "review", "icon": "compare",
        "change": "같은 질문을 1~8단계에서 실행한 결과를 나란히 놓고, 무엇이 왜 달라졌는지 판단합니다.",
        "why": "AI가 만든 결과를 검토하고 다시 지시하는 힘이 이 과정의 목표입니다.",
        "concepts": ["근거 충실도", "비용·속도", "실패 분석", "다시 지시하기"],
        "checks": [
            "같은 질문의 단계별 답변을 비교했다",
            "답변의 쪽번호가 근거와 맞는지 확인했다",
            "단계가 올라갈수록 늘어난 LLM 호출 수와 시간을 확인했다",
            "내 앱에서 실패한 기준 하나와 다시 줄 지시를 적었다",
        ],
        "examples": [COMMON_QUESTION],
    },
}

RUN_STAGES = range(1, 9)
GROUPS = [("LLM 다루기", "한계를 겪고, 형식과 기억을 더한다", [1, 2, 3]),
          ("도구와 흐름", "모델이 도구를 고르고, 흐름을 그래프로", [4, 5]),
          ("문서 근거 RAG", "우리 문서에서 찾아 근거로 답한다", [6, 7]),
          ("에이전트", "스스로 자료를 모으고 점검한다", [8])]
ANSWER_STYLES = ["짧은 문단", "글머리표"]
