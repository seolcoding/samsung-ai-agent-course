"""2-2 과제: 기획자와 검토자 두 Agent"""

from dotenv import load_dotenv

from config.llm import get_llm

load_dotenv()

llm = get_llm()


# 아래에 AI와 함께 코드를 작성합니다
from typing import Annotated, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class State(TypedDict):
    messages: Annotated[list, add_messages]
    plan: str  # 기획자가 쓴 계획
    review: str  # 검토자의 의견
    rounds: int  # 고친 횟수


def planner_node(state: State):
    """계획을 3줄로 쓴다. 검토 의견이 있으면 반영한다."""
    prompt = "행사 계획을 3줄로 써 주세요."
    if state.get("review"):
        prompt += f"\n이전 계획: {state['plan']}\n검토 의견을 반영하세요: {state['review']}"
    msgs = [SystemMessage(content=prompt)] + state["messages"][:1]
    plan = llm.invoke(msgs).content
    return {"messages": [AIMessage(content=plan, name="planner")], "plan": plan}


def reviewer_node(state: State):
    """계획을 보고 '승인' 또는 '수정: 이유'로 답한다."""
    msgs = [
        SystemMessage(content="계획을 검토하세요. 충분하면 '승인', 아니면 '수정: 이유' 한 줄로만 답하세요."),
        HumanMessage(content=state["plan"]),
    ]
    review = llm.invoke(msgs).content
    rounds = state["rounds"] + (1 if review.startswith("수정") else 0)
    return {"messages": [AIMessage(content=review, name="reviewer")], "review": review, "rounds": rounds}


def route(state: State) -> Literal["planner", "__end__"]:
    if state["review"].startswith("수정") and state["rounds"] < 2:
        return "planner"
    return END


builder = StateGraph(State)
builder.add_node("planner", planner_node)
builder.add_node("reviewer", reviewer_node)
builder.add_edge(START, "planner")
builder.add_edge("planner", "reviewer")
builder.add_conditional_edges("reviewer", route)
graph = builder.compile()

graph_result = graph.invoke(
    {"messages": [HumanMessage(content="신입사원 환영 행사")], "plan": "", "review": "", "rounds": 0}
)
for m in graph_result["messages"]:
    m.pretty_print()

print("\n=== 최종 계획 ===")
print(graph_result["plan"])
