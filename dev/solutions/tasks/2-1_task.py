"""2-1 과제: 도구 두 개를 쓰는 그래프 Agent"""

from dotenv import load_dotenv

from config.llm import get_llm

load_dotenv()

llm = get_llm()


# 아래에 AI와 함께 코드를 작성합니다
from typing import Annotated

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict


@tool
def get_exchange_rate(amount_usd: float) -> str:
    """달러(USD) 금액을 원화(KRW)로 환산한다. 환율은 1달러 = 1,400원으로 고정."""
    return f"{amount_usd}달러는 {amount_usd * 1400:,.0f}원입니다. (1달러 = 1,400원)"


@tool
def get_weather(city: str) -> str:
    """도시의 날씨를 알려준다. 날씨는 항상 맑음 23도로 고정."""
    return f"{city}의 날씨는 맑음, 기온은 23도입니다."


tools = [get_exchange_rate, get_weather]
llm_with_tools = llm.bind_tools(tools)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent_node(state: State) -> dict:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


builder = StateGraph(State)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")
app = builder.compile()

print(app.get_graph().draw_ascii())

for question in ["100달러를 원화로 환산하면 얼마야?", "서울 날씨 알려줘"]:
    print(f"\n=== {question} ===")
    tool_graph_result = app.invoke({"messages": [HumanMessage(content=question)]})
    results = tool_graph_result["messages"]
    for m in results:
        m.pretty_print()
