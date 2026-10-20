"""
MCP 클라이언트 실습: 터미널에 켜 둔 DART MCP 서버(우리가 만든 서버)와 Tavily 공식 MCP 서버(남이 만든 서버)에
연결해 LangGraph Agent가 두 서버의 도구를 함께 쓴다.
"""

import asyncio
import os
import sys
from typing import Annotated

import truststore
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from config.llm import get_llm

truststore.inject_into_ssl()  # 사내망에서 Tavily(인터넷 HTTPS)에 연결할 때 회사 인증서를 믿게 한다
load_dotenv()


async def reachable(connection: dict) -> bool:
    """이 연결 설정으로 MCP 서버에 10초 안에 닿으면 True. 사내망에서 막힌 서버는 빼고 진행하려고 쓴다."""
    try:
        await asyncio.wait_for(MultiServerMCPClient({"check": connection}).get_tools(), timeout=10)
        return True
    except Exception:  # 연결 실패는 여러 오류가 한데 묶여(ExceptionGroup) 올라온다
        return False


# ── MCP 서버 연결 설정 ────────────────────────────────────────────────────────
# dart: 2장에서 터미널에 켜 둔 우리 서버. SSE는 켜 둔 서버에 주소로 접속하고,
#       stdio는 노트북이 서버 파일을 직접 실행해 표준 입출력으로 주고받는다.
CONNECTIONS = {
    "sse": {"transport": "sse", "url": "http://localhost:8000/sse"},
    "stdio": {"transport": "stdio", "command": sys.executable, "args": ["mcp_server.py", "--stdio"]},
}
TRANSPORT = "sse"
MCP_CONFIG = {"dart": CONNECTIONS[TRANSPORT]}

# tavily: Tavily가 인터넷에 운영하는 공식 MCP 서버(남이 만든 서버). HTTP로 접속하고, 키는 주소가 아니라
#         머리말(headers)에 넣는다(오류 메시지에 키가 찍히지 않게). 키가 있고 연결될 때만 더한다
TAVILY = {
    "transport": "streamable_http",
    "url": "https://mcp.tavily.com/mcp/",
    "headers": {"Authorization": f"Bearer {os.getenv('TAVILY_API_KEY', '').strip()}"},
}
if os.getenv("TAVILY_API_KEY", "").strip() and await reachable(TAVILY):
    MCP_CONFIG["tavily"] = TAVILY
print("사용할 MCP 서버:", ", ".join(MCP_CONFIG))
if "tavily" not in MCP_CONFIG:
    print("Tavily는 뺐습니다(TAVILY_API_KEY가 없거나 Tavily 서버에 연결되지 않음). DART 도구만으로 진행합니다.")

# TODO: MCP 설정으로 MultiServerMCPClient를 생성해 주세요.
client = MultiServerMCPClient(MCP_CONFIG)

# get_tools()는 서버에 연결해 도구 목록을 가져온다.
# TODO: MCP 서버에서 도구 목록을 가져와 주세요.
tools = await client.get_tools()
# Tavily 도구는 검색(tavily_search)만 쓴다. 나머지 넷(extract·crawl·map·research)은 크레딧을 많이 쓴다
tools = [t for t in tools if not t.name.startswith("tavily_") or t.name == "tavily_search"]
print("=== 사용 가능한 MCP 도구 ===")
for t in tools:
    print(f"  - {t.name}: {t.description.strip().splitlines()[0][:70]}")
print()

# TODO: 가져온 MCP 도구를 LLM과 ToolNode에 연결해 주세요.
llm = get_llm().bind_tools(tools)
tool_node = ToolNode(tools)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent_node(state: State) -> dict:
    # TODO: State의 messages를 도구가 연결된 LLM에 전달해 주세요.
    return {"messages": [llm.invoke(state["messages"])]}


builder = StateGraph(State)
builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)
builder.add_edge(START, "agent")
# TODO: tools_condition으로 도구 호출 여부를 분기하고 tools 이후 agent로 돌아오게 연결해 주세요.
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

# TODO: 그래프를 컴파일해 주세요.
app = builder.compile()

# 도구를 사용해 요청 처리
questions = [
    "삼성전자 최근 30일 공시를 알려 줘.",
    "SK하이닉스의 2025년 매출액과 영업이익은 얼마야?",
    "삼성전자 관련 최신 뉴스를 검색하고, DART 최근 공시와 함께 세 줄로 정리해 줘.",
]

for question in questions:
    mcp_graph_result = await app.ainvoke({"messages": [HumanMessage(content=question)]})
    results = mcp_graph_result["messages"]
    for m in results:
        m.pretty_print()
    print()
