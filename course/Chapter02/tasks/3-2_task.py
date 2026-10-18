"""3-2 과제 · MCP 서버를 직접 띄우는 Agent

✍️ 할 곳  코드의 `# ✍️` 표시 2곳만 채웁니다 (`# ✨` 줄은 AI에게 말할 힌트)
▶️ 실행   uv run --env-file .env python course/Chapter02/tasks/3-2_task.py
✅ 확인   실행하면 맨 끝에 🟢/⛔가 나옵니다
🆘 막히면 오류 메시지 전체를 AI에게 붙여 넣기
"""

import asyncio
import sys
from typing import Annotated

from dotenv import load_dotenv
from fastmcp import FastMCP
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()
llm = get_llm()

# ── 서버: 클라이언트가 이 파일을 --server로 다시 실행합니다(서버 쪽에는 print()를 쓰지 않습니다) ──
mcp = FastMCP("용어 사전 서버")

GLOSSARY = {
    "MCP": "Model Context Protocol: LLM 앱과 외부 도구·데이터를 표준 방식으로 연결하는 프로토콜",
    "RAG": "Retrieval-Augmented Generation: 문서를 검색해 답변의 근거로 쓰는 방식",
    "LangGraph": "노드와 엣지로 Agent 흐름을 그래프로 만드는 라이브러리",
}

# ✍️ 1. MCP 도구 두 개 등록하기
# ✨ @mcp.tool() · 용어 → GLOSSARY에서 뜻 찾기 · 문장 → len(text) 글자 수 · docstring · print() 쓰지 않기


# ── 클라이언트 ──
QUESTIONS = ["MCP가 무슨 뜻이야? 사전에서 찾아 줘.", "'에이전트 개발 교육'은 몇 글자야?"]
seen = {"tools": [], "runs": {}}  # 받은 도구와 질문별 메시지(맨 끝 확인에서 씁니다)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def build_mcp_graph(tools):
    # ✍️ 2. MCP 도구를 붙인 Agent 그래프 만들기
    # ✨ llm.bind_tools(tools) · agent 노드 · ToolNode(tools) · tools_condition · tools → agent · return compile()
    print("(2. 아직 작성하지 않았습니다)")


async def main():
    client = MultiServerMCPClient({
        "glossary": {"transport": "stdio", "command": sys.executable, "args": [__file__, "--server"]},
    })
    tools = seen["tools"] = await client.get_tools()
    print("=== 사용 가능한 MCP 도구 ===")
    for t in tools:
        print(f"  - {t.name}: {t.description}")
    if not tools:
        print("(1. 아직 작성하지 않았습니다)")

    mcp_graph = build_mcp_graph(tools)
    if mcp_graph is None or not tools:
        return
    for question in QUESTIONS:
        print(f"\n### 질문: {question}")
        mcp_graph_result = await mcp_graph.ainvoke({"messages": [HumanMessage(content=question)]})
        results = seen["runs"][question] = mcp_graph_result["messages"]
        for m in results:
            m.pretty_print()


if __name__ == "__main__":
    if "--server" in sys.argv:
        mcp.run(transport="stdio", show_banner=False, log_level="WARNING")  # 배너·INFO 로그는 끕니다
    else:
        asyncio.run(main())


# ── ✅ 확인 (바꾸지 않습니다) ──
def tool_text(question: str) -> str:
    parts = [m.content for m in seen["runs"].get(question, []) if isinstance(m, ToolMessage)]
    return " ".join(p if isinstance(p, str) else " ".join(x.get("text", "") for x in p) for p in parts)


if __name__ == "__main__" and "--server" not in sys.argv:
    print("\n✅ 확인")
    if not seen["tools"]:
        print("⛔ 1. 아직 작성하지 않았습니다")
    elif len(seen["tools"]) != 2 or not all(t.description for t in seen["tools"]):
        print("⛔ 1. 설명(docstring)이 있는 MCP 도구가 2개여야 합니다")
    else:
        print("🟢 1. MCP 서버에서 설명이 있는 도구 2개를 받았습니다")
    if not seen["runs"]:
        print("⛔ 2. 아직 작성하지 않았습니다")
    elif "Model Context Protocol" not in tool_text(QUESTIONS[0]) or not any(n in tool_text(QUESTIONS[1]) for n in ("10", "12")):
        print("⛔ 2. 두 질문이 MCP 도구 결과(사전 뜻, 글자 수)를 받지 못했습니다")
    else:
        print("🟢 2. 두 질문 모두 MCP 도구를 거쳐 답했습니다")
