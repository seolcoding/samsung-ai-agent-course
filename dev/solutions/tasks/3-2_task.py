"""3-2 과제: 서버를 직접 띄우는 stdio MCP Agent"""

from dotenv import load_dotenv

from config.llm import get_llm

load_dotenv()

llm = get_llm()


# 아래에 AI와 함께 코드를 작성합니다
import asyncio
import sys
from typing import Annotated

from fastmcp import FastMCP
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

# ── 서버: 이 파일을 --server로 실행하면 이 부분만 돈다 ──
mcp = FastMCP("용어 사전 서버")

GLOSSARY = {
    "MCP": "Model Context Protocol: LLM 앱과 외부 도구·데이터를 표준 방식으로 연결하는 프로토콜",
    "RAG": "Retrieval-Augmented Generation: 문서를 검색해 답변의 근거로 쓰는 방식",
    "LangGraph": "노드와 엣지로 Agent 흐름을 그래프로 만드는 라이브러리",
}


@mcp.tool()
def lookup_term(term: str) -> str:
    """AI 용어 사전에서 용어의 뜻을 찾는다. 용어는 MCP, RAG, LangGraph 중 하나."""
    return GLOSSARY.get(term, f"사전에 '{term}'이(가) 없습니다.")


@mcp.tool()
def count_characters(text: str) -> int:
    """문장의 글자 수를 공백을 포함해 센다."""
    return len(text)


# ── 클라이언트: 이 파일을 서버로 띄워 stdio로 연결한다 ──
class State(TypedDict):
    messages: Annotated[list, add_messages]


async def main():
    client = MultiServerMCPClient({
        "glossary": {"transport": "stdio", "command": sys.executable, "args": [__file__, "--server"]},
    })
    tools = await client.get_tools()
    print("=== 사용 가능한 MCP 도구 ===")
    for t in tools:
        print(f"  - {t.name}: {t.description}")

    llm_with_tools = llm.bind_tools(tools)

    def agent_node(state: State) -> dict:
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    builder = StateGraph(State)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    app = builder.compile()

    for question in ["MCP가 무슨 뜻이야? 사전에서 찾아 줘.", "'에이전트 개발 교육'은 몇 글자야?"]:
        print(f"\n### 질문: {question}")
        mcp_graph_result = await app.ainvoke({"messages": [HumanMessage(content=question)]})
        results = mcp_graph_result["messages"]
        for m in results:
            m.pretty_print()


if __name__ == "__main__":
    if "--server" in sys.argv:
        mcp.run(transport="stdio")
    else:
        asyncio.run(main())
