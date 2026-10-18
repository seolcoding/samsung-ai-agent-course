"""3-4 과제 · thread 기억과 Store 기억

▶️ 실행   uv run --env-file .env python course/Chapter02/tasks/3-4_task.py
✅ 확인   실행하면 맨 끝에 🟢/⛔가 나옵니다
🆘 막히면 오류 메시지 전체를 AI에게 붙여 넣기
"""

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

USER_ID = "user_001"
USER_INFO = "이름은 이지수, 취미는 피아노 연주"


class State(TypedDict):
    messages: Annotated[list, add_messages]


def make_builder(node) -> StateGraph:
    """노드 하나짜리 그래프 뼈대: START → chatbot → END"""
    builder = StateGraph(State)
    builder.add_node("chatbot", node)
    builder.add_edge(START, "chatbot")
    builder.add_edge("chatbot", END)
    return builder


def chatbot(state: State) -> dict:
    system = SystemMessage(content="너는 친절한 AI 어시스턴트야. 한두 문장으로 답해.")
    return {"messages": [llm.invoke([system] + state["messages"])]}


chat_builder = make_builder(chatbot)

print("=== 1. MemorySaver와 thread_id ===")
# ✍️ 1. thread마다 대화를 따로 기억하기
# ✨ chat_graph = chat_builder.compile(checkpointer=MemorySaver()) · thread_a: "내 이름은 홍길동이야." → "내 이름이 뭐야?" · thread_b: "내 이름이 뭐야?" · get_state 메시지 수
chat_graph = chat_builder.compile(checkpointer=MemorySaver())
config_a = {"configurable": {"thread_id": "thread_a"}}
config_b = {"configurable": {"thread_id": "thread_b"}}

chat_graph.invoke({"messages": [HumanMessage(content="내 이름은 홍길동이야.")]}, config_a)
for config in [config_a, config_b]:
    chat_graph_result = chat_graph.invoke({"messages": [HumanMessage(content="내 이름이 뭐야?")]}, config)
    print(f"[{config['configurable']['thread_id']}] {chat_graph_result['messages'][-1].content}")

print(f"thread_a 메시지 수: {len(chat_graph.get_state(config_a).values['messages'])}")
print(f"thread_b 메시지 수: {len(chat_graph.get_state(config_b).values['messages'])}")


print("\n=== 2. InMemoryStore ===")
store = InMemoryStore()

# ✍️ 2. Store에 사용자 정보 저장 · 꺼내기
# ✨ store.put: ("memories", USER_ID) · "profile" · {"fact": USER_INFO} → recall: store.search(("memories", user_id)) → fact 합쳐 return
store.put(("memories", USER_ID), "profile", {"fact": USER_INFO})


def recall(user_id: str) -> str:
    memories = store.search(("memories", user_id))
    return "\n".join(f"- {m.value['fact']}" for m in memories) or "없음"


def memory_chatbot(state: State) -> dict:
    system = SystemMessage(content=f"너는 친절한 AI 어시스턴트야.\n사용자 정보:\n{recall(USER_ID)}")
    return {"messages": [llm.invoke([system] + state["messages"])]}


store_graph = make_builder(memory_chatbot).compile(checkpointer=MemorySaver(), store=store)
print(f"Store에서 꺼낸 정보: {recall(USER_ID)}")
config_new = {"configurable": {"thread_id": "session_2"}}  # 처음 쓰는 thread
store_graph_result = store_graph.invoke({"messages": [HumanMessage(content="내 이름이랑 취미 알아?")]}, config_new)
results = store_graph_result["messages"]
for m in results:
    m.pretty_print()
print(f"session_2 메시지 수: {len(store_graph.get_state(config_new).values['messages'])}")


# ── ✅ 확인 (바꾸지 않습니다) ──
print("\n✅ 확인")
graph = globals().get("chat_graph")
if graph is None:
    print("⛔ 1. 아직 작성하지 않았습니다")
elif not isinstance(graph.checkpointer, MemorySaver):
    print("⛔ 1. chat_graph를 MemorySaver로 compile해야 합니다")
else:
    a, b = (graph.get_state({"configurable": {"thread_id": t}}).values.get("messages", []) for t in ("thread_a", "thread_b"))
    if (len(a), len(b)) != (4, 2):
        print(f"⛔ 1. 메시지 수가 thread_a 4·thread_b 2여야 합니다(지금 {len(a)}·{len(b)})")
    elif "홍길동" not in a[-1].content or "홍길동" in b[-1].content:
        print("⛔ 1. thread_a만 이름(홍길동)을 기억해야 합니다")
    else:
        print("🟢 1. thread_a는 대화를 이어 가고 thread_b는 따로 시작합니다")
answer = store_graph_result["messages"][-1].content
if "아직 작성하지 않았습니다" in recall(USER_ID):
    print("⛔ 2. 아직 작성하지 않았습니다")
elif not store.search(("memories", USER_ID)) or "이지수" in recall("other_user"):
    print("⛔ 2. Store에 put하고, recall은 받은 user_id의 namespace를 search해야 합니다")
elif len(results) != 2 or not ("지수" in answer and "피아노" in answer):
    print("⛔ 2. 새 thread session_2의 답에 Store의 정보(이지수·피아노)가 없습니다")
else:
    print("🟢 2. 새 thread에서도 Store에서 꺼낸 정보로 답했습니다")
