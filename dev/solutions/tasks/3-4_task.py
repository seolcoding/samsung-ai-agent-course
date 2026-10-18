"""3-4 과제: 그래프 나누고 기억하기 (강사용 정답)

course/Chapter02/tasks/3-4/3-4_task.py 를 완성한 모습이다.
실행(저장소 맨 위에서): uv run --env-file .env python dev/solutions/tasks/3-4_task.py
"""

import operator
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.store.memory import InMemoryStore
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()

llm = get_llm()

# 과제에 쓰는 값(그대로 둡니다)
DOCUMENT = (
    "인공지능은 인간의 지능을 모방하는 컴퓨터 시스템으로, 최근 LLM의 등장으로 급격히 발전했습니다. "
    "이제 AI는 텍스트 생성, 번역, 코딩 등 다양한 작업을 수행할 수 있습니다."
)
TOPIC = "재택근무"
USER_ID = "user_001"
USER_INFO = "이름은 이지수, 취미는 피아노 연주"


# ✍️ 목표 1: 서브그래프
print("=== 목표 1: 서브그래프 ===")


class SummaryState(TypedDict):
    text: str
    summary: str


def summarize_node(state: SummaryState) -> dict:
    result = llm.invoke(f"다음 텍스트를 한 문장으로 요약해줘:\n\n{state['text']}")
    return {"summary": result.content}


summary_builder = StateGraph(SummaryState)
summary_builder.add_node("summarize", summarize_node)
summary_builder.add_edge(START, "summarize")
summary_builder.add_edge("summarize", END)
summary_subgraph = summary_builder.compile()


class ParentState(TypedDict):
    document: str
    summary: str


def fetch_document(state: ParentState) -> dict:
    return {"document": DOCUMENT}


def summarize_document(state: ParentState) -> dict:
    response = summary_subgraph.invoke({"text": state["document"], "summary": ""})
    return {"summary": response["summary"]}


parent_builder = StateGraph(ParentState)
parent_builder.add_node("fetch_document", fetch_document)
parent_builder.add_node("summarize_document", summarize_document)
parent_builder.add_edge(START, "fetch_document")
parent_builder.add_edge("fetch_document", "summarize_document")
parent_builder.add_edge("summarize_document", END)
parent_graph = parent_builder.compile()

parent_graph_result = parent_graph.invoke({"document": "", "summary": ""})
print(f"부모 State의 summary: {parent_graph_result['summary']}")


# ✍️ 목표 2: fan-out/fan-in과 Annotated 리듀서
print("\n=== 목표 2: fan-out/fan-in ===")


class FanState(TypedDict):
    topic: str
    notes: Annotated[list[str], operator.add]


def pros_node(state: FanState) -> dict:
    result = llm.invoke(f"{state['topic']}의 장점을 한 문장으로 말해줘.")
    return {"notes": [f"장점: {result.content}"]}


def cons_node(state: FanState) -> dict:
    result = llm.invoke(f"{state['topic']}의 단점을 한 문장으로 말해줘.")
    return {"notes": [f"단점: {result.content}"]}


def merge_node(state: FanState) -> dict:
    print(f"merge가 받은 notes 수: {len(state['notes'])}")
    return {}


fan_builder = StateGraph(FanState)
fan_builder.add_node("pros", pros_node)
fan_builder.add_node("cons", cons_node)
fan_builder.add_node("merge", merge_node)
fan_builder.add_edge(START, "pros")
fan_builder.add_edge(START, "cons")
fan_builder.add_edge("pros", "merge")
fan_builder.add_edge("cons", "merge")
fan_builder.add_edge("merge", END)
fan_graph = fan_builder.compile()

print(fan_graph.get_graph().draw_ascii())
fan_graph_result = fan_graph.invoke({"topic": TOPIC, "notes": []})
for note in fan_graph_result["notes"]:
    print(note)


# ✍️ 목표 3: MemorySaver와 thread_id
print("\n=== 목표 3: MemorySaver와 thread_id ===")


class ChatState(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: ChatState) -> dict:
    system = SystemMessage(content="너는 친절한 AI 어시스턴트야. 한두 문장으로 답해.")
    return {"messages": [llm.invoke([system] + state["messages"])]}


chat_builder = StateGraph(ChatState)
chat_builder.add_node("chatbot", chatbot)
chat_builder.add_edge(START, "chatbot")
chat_builder.add_edge("chatbot", END)
chat_graph = chat_builder.compile(checkpointer=MemorySaver())

config_a = {"configurable": {"thread_id": "thread_a"}}
config_b = {"configurable": {"thread_id": "thread_b"}}

chat_graph.invoke({"messages": [HumanMessage(content="내 이름은 홍길동이야.")]}, config_a)
chat_graph_result = chat_graph.invoke({"messages": [HumanMessage(content="내 이름이 뭐야?")]}, config_a)
results = chat_graph_result["messages"]
for m in results:
    m.pretty_print()

chat_graph_result = chat_graph.invoke({"messages": [HumanMessage(content="내 이름이 뭐야?")]}, config_b)
results = chat_graph_result["messages"]
for m in results:
    m.pretty_print()

print(f"thread_a 메시지 수: {len(chat_graph.get_state(config_a).values['messages'])}")
print(f"thread_b 메시지 수: {len(chat_graph.get_state(config_b).values['messages'])}")


# ✍️ 목표 4: InMemoryStore put/search
print("\n=== 목표 4: InMemoryStore ===")

store = InMemoryStore()
namespace = ("memories", USER_ID)
store.put(namespace, "profile", {"fact": USER_INFO})


class StoreState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str


def memory_chatbot(state: StoreState) -> dict:
    memories = store.search(("memories", state["user_id"]))
    memory_text = "\n".join(f"- {m.value['fact']}" for m in memories) if memories else "없음"
    system = SystemMessage(content=f"너는 친절한 AI 어시스턴트야.\n\n사용자에 대해 알고 있는 정보:\n{memory_text}")
    return {"messages": [llm.invoke([system] + state["messages"])]}


store_builder = StateGraph(StoreState)
store_builder.add_node("chatbot", memory_chatbot)
store_builder.add_edge(START, "chatbot")
store_builder.add_edge("chatbot", END)
store_graph = store_builder.compile(checkpointer=MemorySaver(), store=store)

config_new = {"configurable": {"thread_id": "session_2"}}
store_graph_result = store_graph.invoke(
    {"messages": [HumanMessage(content="내 이름이랑 취미 알아?")], "user_id": USER_ID},
    config_new,
)
results = store_graph_result["messages"]
for m in results:
    m.pretty_print()

print(f"session_2 메시지 수: {len(store_graph.get_state(config_new).values['messages'])}")
for item in store.search(namespace):
    print(f"Store {item.namespace} [{item.key}] {item.value['fact']}")
