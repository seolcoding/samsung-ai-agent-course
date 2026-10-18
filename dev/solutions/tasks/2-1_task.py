"""2-1 과제 · 약관 검색 도구를 쓰고 대화를 기억하는 LangGraph 챗봇

▶️ 실행   uv run --env-file .env python course/Chapter01/tasks/2-1_task.py
✅ 확인   사이드바 "✅ 과제 확인" 버튼
🆘 막히면 오류 메시지 전체를 AI에게 붙여 넣기
"""
import traceback
import uuid
from pathlib import Path
from typing import Literal

import streamlit as st
from langchain_chroma import Chroma
from langchain_community.document_loaders import PDFMinerLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from config.embeddings import get_embeddings
from config.llm import get_llm

if __name__ == "__main__" and not st.runtime.exists():  # python으로 실행하면 Streamlit 앱으로 띄웁니다
    import sys
    from streamlit.web import cli
    sys.argv = ["streamlit", "run", __file__, "--server.showEmailPrompt", "false", "--server.address", "127.0.0.1"]
    sys.exit(cli.main())

PDF_PATH = Path(__file__).resolve().parent.parent / "notebooks" / "data" / "meritz_pet_insurance.pdf"


@st.cache_resource  # 앱이 다시 실행돼도 PDF 읽기·임베딩은 처음 한 번만
def load_retriever():
    documents = PDFMinerLoader(str(PDF_PATH)).load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=75).split_documents(documents)
    return Chroma.from_documents(chunks, embedding=get_embeddings()).as_retriever(search_kwargs={"k": 3})


retriever = load_retriever()


@tool
def search_policy(query: str) -> str:
    """펫보험 약관에서 보장 내용·보험금·한도를 찾는다. 펫보험 약관 질문일 때만 쓴다."""
    return "\n\n".join(doc.page_content for doc in retriever.invoke(query))


tools = [search_policy]
llm = get_llm().bind_tools(tools)
SYSTEM = SystemMessage("너는 펫보험 상담 챗봇이야. 약관 질문이면 search_policy로 찾아 답하고, 인사·일반 질문은 도구 없이 답해.")


def agent(state: MessagesState) -> dict:
    return {"messages": [llm.invoke([SYSTEM] + state["messages"])]}


# ✍️ 1. agent·ToolNode 조건부 엣지 그래프 만들기
# ✨ StateGraph(MessagesState) · "agent"·"tools"(ToolNode) 노드 · 갈림길 함수 -> Literal["tools", "__end__"] · tools → agent
def route(state: MessagesState) -> Literal["tools", "__end__"]:
    if state["messages"][-1].tool_calls:
        return "tools"
    return END


builder = StateGraph(MessagesState)
builder.add_node("agent", agent)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", route)
builder.add_edge("tools", "agent")


def answer(question):
    if builder is None:
        raise NotImplementedError("✍️ 1. 아직 작성하지 않았습니다")
    # ✍️ 2. MemorySaver와 thread_id로 기억하기
    # ✨ MemorySaver는 st.session_state에 한 번만 · compile(checkpointer=…) · config thread_id = st.session_state.thread_id
    if "memory" not in st.session_state:
        st.session_state.memory = MemorySaver()
    graph = builder.compile(checkpointer=st.session_state.memory)
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    nodes, reply = [], ""
    for update in graph.stream({"messages": [HumanMessage(question)]}, config, stream_mode="updates"):
        for node, value in update.items():
            nodes.append(node)
            reply = value["messages"][-1].content
    LOG["노드 순서"] = " → ".join(nodes)
    print(f"[노드 순서] {LOG['노드 순서']}", flush=True)
    st.caption(f"노드 순서: {LOG['노드 순서']}")
    return reply


# ── 화면 (바꾸지 않습니다) ───────────────────────────────────────────────────
LOG = {}  # 거친 노드 순서(✅ 과제 확인이 봅니다)
st.title("나의 약관 상담 에이전트 (2-1 과제)")
if st.sidebar.button("대화 지우기") or "messages" not in st.session_state:
    st.session_state.messages, st.session_state.thread_id = [], str(uuid.uuid4())  # 새 대화 번호: 그래프 기억도 새로
for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])
if question := st.chat_input("질문을 입력하세요"):
    st.chat_message("user").markdown(question)
    with st.chat_message("assistant"):
        try:
            reply = answer(question)
            st.markdown(reply)
            st.session_state.messages += [{"role": "user", "content": question}, {"role": "assistant", "content": reply}]
        except Exception as error:  # 말풍선에는 한 줄, 터미널에는 오류 전체
            traceback.print_exc()
            st.error(f"⚠️ {error}")


# ── ✅ 확인 (바꾸지 않습니다) ────────────────────────────────────────────────
def check(name, test, why):  # test()가 참이면 🟢, 거짓이면 ⛔ why, 오류면 ⛔ 오류 메시지
    try:
        mark, note = ("🟢", "") if test() else ("⛔", why)
    except Exception as error:
        mark, note = "⛔", str(error)
    print(f"{mark} {name} {note}", flush=True)
    st.sidebar.write(f"{mark} {name}" + (f" — {note}" if note else ""))


def test_graph():
    st.session_state.thread_id = str(uuid.uuid4())  # 확인용 새 대화 번호
    answer("반려견이 수술을 받으면 수술비도 보장되나요?")
    return {"agent", "tools"} <= set(builder.nodes) and "tools" in LOG["노드 순서"]


def test_memory():
    st.session_state.thread_id = str(uuid.uuid4())
    answer("안녕! 내 이름은 민수야.")
    known = answer("내 이름이 뭐야?")
    st.session_state.thread_id = str(uuid.uuid4())  # 다른 대화에서는 몰라야 한다
    return "민수" in known and "민수" not in answer("내 이름이 뭐야?")


if st.sidebar.button("✅ 과제 확인"):
    st.sidebar.markdown("**✅ 확인**")
    scratch, my_thread = st.empty(), st.session_state.thread_id
    with scratch.container():  # 확인하며 그린 것은 끝나면 지운다
        check("1. 약관 질문이 tools 노드를 거쳤다", test_graph, "agent·tools 노드가 없거나 tools를 거치지 않았습니다")
        check("2. 같은 대화에서만 이름을 기억했다", test_memory, "이름을 기억하지 못했거나 다른 대화에서도 기억했습니다")
    scratch.empty()
    st.session_state.thread_id = my_thread  # 내 대화 번호로 되돌린다
