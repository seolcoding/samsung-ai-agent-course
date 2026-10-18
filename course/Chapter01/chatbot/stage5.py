"""챗봇 5단계(2-3): 하나로 합친 최종 챗봇

실행(저장소 맨 위에서): uv run --env-file .env streamlit run course/Chapter01/chatbot/stage5.py
"""
import os
from pathlib import Path
from typing import Literal

import streamlit as st
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PDFMinerLoader
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from config.embeddings import get_embeddings
from config.llm import get_llm
from config.ragaas import post_ragaas
from ui import add_message, log_step, run_chat

load_dotenv()

llm = get_llm()

# 사이드바: 답 방식과 말투 고르기
mode = st.sidebar.selectbox("답 방식", ["대화", "계산기 도구", "정리 카드", "약관 질문", "에이전트"])
style = st.sidebar.selectbox("답 말투", ["친절하게", "한 문장으로", "초등학생에게 설명하듯"])
search_method = st.sidebar.selectbox("검색 방식", ["로컬 Chroma", "사내 RAGaaS"])
need_approval = st.sidebar.toggle("도구 실행 전 승인 받기")


# ── 답 방식 "대화" ────────────────────────────────────────────────────────────
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 친절한 AI 도우미야. 답은 {style} 해 줘."),
    MessagesPlaceholder("history"),
    ("human", "{question}"),
])

chain = prompt | llm | StrOutputParser()


def chat_answer(question, history):
    inputs = {"style": style, "history": history, "question": question}
    log_step("모델에 보낸 메시지", [(m.type, m.content) for m in prompt.invoke(inputs).to_messages()])
    count = 0
    for text in chain.stream(inputs):
        count += 1
        yield text
    log_step("받은 조각 수", count)


# ── 답 방식 "계산기 도구" ─────────────────────────────────────────────────────
@tool
def calculate(expression: str) -> str:
    """수식을 계산한다. 예: '1234 * 5678'"""
    return str(eval(expression, {"__builtins__": {}}))  # noqa: S307


tools = [calculate]
tool_map = {t.name: t for t in tools}
llm_with_tools = llm.bind_tools(tools)


def tool_answer(question):
    messages = [HumanMessage(content=question)]
    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)
        if not response.tool_calls:
            return response.content
        for call in response.tool_calls:
            result = tool_map[call["name"]].invoke(call["args"])
            log_step("도구 실행", f"{call['name']}({call['args']}) → {result}")
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))


# ── 답 방식 "정리 카드" ───────────────────────────────────────────────────────
class Card(BaseModel):
    title: str = Field(description="제목")
    summary: str = Field(description="한 줄 요약")
    points: list[str] = Field(description="핵심 3가지")


parser = PydanticOutputParser(pydantic_object=Card)
card_prompt = ChatPromptTemplate.from_messages([
    ("system", "질문에 대한 답을 정리 카드로 만들어. {format_instructions}"),
    ("human", "{question}"),
]).partial(format_instructions=parser.get_format_instructions())
card_chain = card_prompt | llm | parser


def card_answer(question):
    card = card_chain.invoke({"question": question})
    log_step("받은 카드", card)
    lines = [f"### {card.title}", card.summary] + [f"- {point}" for point in card.points]
    return "\n".join(lines)


# ── 답 방식 "약관 질문" ───────────────────────────────────────────────────────
PDF_PATH = Path(__file__).resolve().parent.parent / "notebooks" / "data" / "meritz_pet_insurance.pdf"


@st.cache_resource
def load_vectorstore():
    documents = PDFMinerLoader(str(PDF_PATH)).load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=75).split_documents(documents)
    vectorstore = Chroma.from_documents(chunks, embedding=get_embeddings())
    print(f"[벡터 저장소] 청크 {len(chunks)}개 저장", flush=True)
    return vectorstore


def search(question):
    if search_method == "사내 RAGaaS":
        payload = {
            "index_name": os.getenv("index_name"),
            "permission_groups": ["rag-public"],
            "query_text": question,
            "num_result_doc": 3,
            "fields_exclude": ["v_merge_title_content"],
        }
        hits = post_ragaas("retrieve-rrf", payload).json()["hits"]["hits"]
        return [hit["_source"]["merge_title_content"] for hit in hits]
    retriever = load_vectorstore().as_retriever(search_kwargs={"k": 3})
    return [doc.page_content for doc in retriever.invoke(question)]


rag_prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 펫보험 약관 안내 도우미야. 아래 context만 근거로 답해. "
               "context에 없는 내용이면 '문서에서 확인할 수 없습니다'라고만 답해.\n\ncontext:\n{context}"),
    ("human", "{question}"),
])
rag_chain = rag_prompt | llm | StrOutputParser()


def rag_answer(question):
    texts = search(question)
    log_step(f"근거 ({search_method}, {len(texts)}개)", "\n\n---\n\n".join(texts))
    return rag_chain.stream({"context": "\n\n".join(texts), "question": question})


# ── 답 방식 "에이전트" ────────────────────────────────────────────────────────
@tool
def search_policy(query: str) -> str:
    """펫보험 약관에서 보장 내용·보험금·한도·자기부담금을 찾는다. 펫보험 약관에 관한 질문일 때만 쓴다."""
    return "\n\n".join(search(query))


agent_tools = [search_policy]
agent_llm = llm.bind_tools(agent_tools)
AGENT_SYSTEM = SystemMessage(
    content="너는 펫보험 상담 챗봇이야. 펫보험 약관에 관한 질문이면 search_policy로 찾아 그 내용으로 답하고, "
            "인사나 일반 질문에는 도구 없이 바로 답해."
)


def agent_node(state: MessagesState) -> dict:
    return {"messages": [agent_llm.invoke([AGENT_SYSTEM] + state["messages"])]}


def route(state: MessagesState) -> Literal["tools", "__end__"]:
    if state["messages"][-1].tool_calls:
        return "tools"
    return END


builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(agent_tools))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", route)
builder.add_edge("tools", "agent")


@st.cache_resource
def get_memory():
    return MemorySaver()


agent_graph = builder.compile(
    checkpointer=get_memory(),
    interrupt_before=["tools"] if need_approval else None,
)


def run_graph(graph_input, config):
    """(그대로 둡니다) 그래프를 실행하며 지나간 노드를 기록하고, 마지막 답(또는 승인 요청)을 돌려줍니다."""
    nodes = []
    for update in agent_graph.stream(graph_input, config, stream_mode="updates"):
        for name, value in update.items():
            if name == "__interrupt__":
                continue
            nodes.append(name)
            if name == "tools":
                log_step("도구 결과", value["messages"][-1].content)
    log_step("노드 순서", " → ".join(nodes))
    state = agent_graph.get_state(config)
    if state.next:  # tools 앞에서 멈춰 있음
        calls = state.values["messages"][-1].tool_calls
        return "⏸ 도구를 실행하기 전에 승인이 필요합니다: " + ", ".join(f"{c['name']}({c['args']})" for c in calls)
    return state.values["messages"][-1].content


def agent_answer(question):
    load_vectorstore()  # (그대로 둡니다) 도구는 다른 스레드에서 돌아 화면 기능을 못 쓰므로 벡터 저장소를 먼저 만들어 둡니다
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    return run_graph({"messages": [HumanMessage(content=question)]}, config)


def resume(approved):
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    if not approved:
        calls = agent_graph.get_state(config).values["messages"][-1].tool_calls
        rejections = [ToolMessage(content="사용자가 도구 실행을 거부했습니다.", tool_call_id=c["id"]) for c in calls]
        agent_graph.update_state(config, {"messages": rejections}, as_node="tools")
    return run_graph(None, config)


def approval_buttons():
    """그래프가 tools 앞에서 멈춰 있으면 승인/거부 버튼을 보여 줍니다(그대로 둡니다)."""
    if agent_graph is None or agent_graph.checkpointer is None:
        return
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    if not agent_graph.get_state(config).next:
        return
    left, right = st.columns(2)
    if left.button("승인"):
        add_message("assistant", resume(True))
        st.rerun()
    if right.button("거부"):
        add_message("assistant", resume(False))
        st.rerun()


def answer(question, history):
    # ✍️ 목표 1: "답 방식"을 고르지 않아도 에이전트 하나가 일반·약관·기억·계산 질문에 모두 답하게 합니다
    #            (answer는 agent_answer만 부르고, 에이전트 도구에 calculate를 더하고, "답 방식" 선택 상자는 지웁니다)
    if mode == "에이전트":
        return agent_answer(question)
    if mode == "약관 질문":
        return rag_answer(question)
    if mode == "계산기 도구":
        return tool_answer(question)
    if mode == "정리 카드":
        return card_answer(question)
    return chat_answer(question, history)


run_chat(answer, "나의 챗봇 - 5단계")
approval_buttons()
