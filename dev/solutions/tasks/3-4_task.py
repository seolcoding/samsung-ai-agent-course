"""3-4 과제: 대화를 이어 가는 장단점 정리 그래프"""

from dotenv import load_dotenv

from config.llm import get_llm

load_dotenv()

llm = get_llm()


# 아래에 AI와 함께 코드를 작성합니다
from typing import Annotated

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class State(TypedDict):
    messages: Annotated[list, add_messages]
    pros: str
    cons: str


def pros_node(state: State) -> dict:
    system = SystemMessage(content="대화의 마지막 질문이 다루는 주제의 장점만 두 줄로 적어 줘. 머리말 없이 내용만 씁니다.")
    return {"pros": llm.invoke([system] + state["messages"]).content}


def cons_node(state: State) -> dict:
    system = SystemMessage(content="대화의 마지막 질문이 다루는 주제의 단점만 두 줄로 적어 줘. 머리말 없이 내용만 씁니다.")
    return {"cons": llm.invoke([system] + state["messages"]).content}


def merge_node(state: State) -> dict:
    answer = f"장점: {state['pros']}\n단점: {state['cons']}"
    return {"messages": [AIMessage(content=answer)]}


builder = StateGraph(State)
builder.add_node("pros", pros_node)
builder.add_node("cons", cons_node)
builder.add_node("merge", merge_node)
builder.add_edge(START, "pros")
builder.add_edge(START, "cons")
builder.add_edge("pros", "merge")
builder.add_edge("cons", "merge")
builder.add_edge("merge", END)
app = builder.compile(checkpointer=MemorySaver())

print(app.get_graph().draw_ascii())

config = {"configurable": {"thread_id": "user-1"}}
for question in ["재택근무의 장점과 단점을 알려줘", "그 주제를 팀장 입장에서 다시 정리해줘"]:
    print(f"\n=== {question} ===")
    pros_cons_result = app.invoke({"messages": [HumanMessage(content=question)]}, config)
    results = pros_cons_result["messages"]
    for m in results:
        m.pretty_print()
