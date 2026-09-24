"""교육 자료 검색 MCP 서버. python -m courseware.mcp_server --stdio 로 실행한다."""

import argparse

from fastmcp import FastMCP
from courseware.knowledge import retrieve


def build_mcp() -> FastMCP:
    server = FastMCP("Course Knowledge — synthetic data")

    @server.tool()
    def search_knowledge(query: str, k: int = 2) -> list[dict]:
        """교육용 AI Agent 문서를 검색한다. 실제 사내 문서는 포함하지 않는다."""
        if not 1 <= k <= 5:
            raise ValueError("k는 1 이상 5 이하여야 합니다.")
        return retrieve(query, k=k)

    @server.resource("course://notice")
    def notice() -> str:
        return "이 서버는 교육용 모의 자료만 제공합니다."

    @server.prompt()
    def evidence_answer(question: str) -> str:
        return f"질문: {question}\n검색 자료만 근거로 답하고 문서 ID를 붙이세요. 근거가 없으면 모른다고 답하세요."

    return server


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdio", action="store_true")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = build_mcp()
    if args.stdio:
        server.run(transport="stdio", show_banner=False)
    else:
        server.run(transport="http", host="127.0.0.1", port=args.port, show_banner=False)
