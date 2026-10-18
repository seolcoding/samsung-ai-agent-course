"""3-2 과제: MCP 서버를 직접 띄우는 Agent

이 파일 하나가 MCP 서버이자 클라이언트입니다.
- 그냥 실행하면 클라이언트(main)가 돕니다.
- 클라이언트가 이 파일을 `--server`를 붙여 다시 실행하면 서버만 돕니다(stdio 방식).

서버 쪽 코드(도구 함수 등)에서는 print()를 쓰지 않습니다. stdio 방식에서는 서버의 표준 출력이
서버와 클라이언트가 MCP 메시지를 주고받는 통로라서, 서버에서 print()한 글자는 화면에 나오지 않고
버려집니다(라이브러리 버전에 따라서는 연결이 깨지기도 합니다).
"""

import asyncio
import sys
from typing import Annotated

from dotenv import load_dotenv
from fastmcp import FastMCP
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()

llm = get_llm()


# ── 서버: 이 파일을 --server로 실행하면 이 부분만 쓰입니다 ──────────────────────
mcp = FastMCP("용어 사전 서버")

GLOSSARY = {
    "MCP": "Model Context Protocol: LLM 앱과 외부 도구·데이터를 표준 방식으로 연결하는 프로토콜",
    "RAG": "Retrieval-Augmented Generation: 문서를 검색해 답변의 근거로 쓰는 방식",
    "LangGraph": "노드와 엣지로 Agent 흐름을 그래프로 만드는 라이브러리",
}

# ✍️ 목표 1: @mcp.tool()로 도구 2개를 등록합니다
#   - 용어 사전 찾기: 용어를 받아 GLOSSARY에서 뜻을 돌려줌
#   - 글자 수 세기: 문장을 받아 공백을 포함한 글자 수를 돌려줌
@mcp.tool()
def lookup_term(term: str) -> str:
    """AI 용어 사전에서 용어의 뜻을 찾는다. 용어는 MCP, RAG, LangGraph 중 하나."""
    return GLOSSARY.get(term, f"사전에 '{term}'이(가) 없습니다.")


@mcp.tool()
def count_characters(text: str) -> int:
    """문장의 글자 수를 공백을 포함해 센다."""
    return len(text)


# ✍️ 목표 4-1: @mcp.resource()로 사전 정보, @mcp.prompt()로 질문 템플릿을 정의합니다
@mcp.resource("glossary://terms")
def list_terms() -> str:
    """용어 사전에 있는 용어 목록을 제공한다."""
    return ", ".join(GLOSSARY)


@mcp.prompt()
def explain_term_prompt(term: str) -> str:
    """용어를 쉽게 설명해 달라는 질문을 만든다."""
    return f"'{term}'을(를) 코딩을 모르는 사람도 알 수 있게 쉽게 설명해 줘."


# ── 클라이언트: 이 파일을 서버로 띄워 stdio로 연결합니다 ────────────────────────
class State(TypedDict):
    messages: Annotated[list, add_messages]


async def main():
    # ✍️ 목표 2: MultiServerMCPClient를 stdio로 연결하고 get_tools()로 도구 목록을 받아 출력합니다
    client = MultiServerMCPClient({
        "glossary": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [__file__, "--server"],
        },
    })
    tools = await client.get_tools()
    print("=== 사용 가능한 MCP 도구 ===")
    for t in tools:
        print(f"  - {t.name}: {t.description}")

    # ✍️ 목표 3: 받은 도구로 LangGraph Agent를 만들고 두 질문에 답하게 합니다
    llm_with_tools = llm.bind_tools(tools)

    def agent_node(state: State) -> dict:
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    builder = StateGraph(State)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    mcp_graph = builder.compile()

    for question in ["MCP가 무슨 뜻이야? 사전에서 찾아 줘.", "'에이전트 개발 교육'은 몇 글자야?"]:
        print(f"\n### 질문: {question}")
        mcp_graph_result = await mcp_graph.ainvoke({"messages": [HumanMessage(content=question)]})
        results = mcp_graph_result["messages"]
        for m in results:
            m.pretty_print()

    # ✍️ 목표 4-2: 서버의 Resource와 Prompt를 읽어 출력합니다
    resources = await client.get_resources("glossary", uris=["glossary://terms"])
    print("\n=== Resource ===")
    for r in resources:
        print(f"  {r.metadata['uri']}: {r.as_string()}")

    prompt_messages = await client.get_prompt("glossary", "explain_term_prompt", arguments={"term": "RAG"})
    print("\n=== Prompt ===")
    for m in prompt_messages:
        print(f"  {m.content}")


if __name__ == "__main__":
    if "--server" in sys.argv:
        # 서버 시작 안내 그림(배너)과 INFO 로그는 끕니다. 오류는 그대로 보입니다
        mcp.run(transport="stdio", show_banner=False, log_level="WARNING")
    else:
        asyncio.run(main())
