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

from dotenv import load_dotenv
from fastmcp import FastMCP

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


# ✍️ 목표 4-1: @mcp.resource()로 사전 정보, @mcp.prompt()로 질문 템플릿을 정의합니다


# ── 클라이언트: 이 파일을 서버로 띄워 stdio로 연결합니다 ────────────────────────
async def main():
    # ✍️ 목표 2: MultiServerMCPClient를 stdio로 연결하고 get_tools()로 도구 목록을 받아 출력합니다
    print("=== 사용 가능한 MCP 도구 ===")
    print("  (아직 없습니다. 목표 2를 작성합니다)")

    # ✍️ 목표 3: 받은 도구로 LangGraph Agent를 만들고 두 질문에 답하게 합니다
    print("\n(목표 3을 아직 작성하지 않았습니다)")

    # ✍️ 목표 4-2: 서버의 Resource와 Prompt를 읽어 출력합니다
    print("\n(목표 4를 아직 작성하지 않았습니다)")


if __name__ == "__main__":
    if "--server" in sys.argv:
        # 서버 시작 안내 그림(배너)과 INFO 로그는 끕니다. 오류는 그대로 보입니다
        mcp.run(transport="stdio", show_banner=False, log_level="WARNING")
    else:
        asyncio.run(main())
