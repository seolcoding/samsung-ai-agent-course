"""
캡스톤 MCP 파일시스템 서버

data/ 폴더의 문서를 Researcher 에이전트가 검색할 수 있도록 MCP 도구로 제공한다.

실행 (solution.py 실행 전 먼저 실행):
  python course/Chapter02/code/solution/06-capstone/mcp_server.py
"""

import os
from pathlib import Path

from fastmcp import FastMCP

DATA_DIR = Path(__file__).parent / 'data'

mcp = FastMCP('capstone-filesystem')


@mcp.tool()
def list_docs() -> list[str]:
    """data/ 폴더에 있는 문서 목록을 반환한다."""
    return [f.name for f in DATA_DIR.glob('*.md')]


@mcp.tool()
def read_doc(filename: str) -> str:
    """data/ 폴더의 문서를 읽어 전체 내용을 반환한다."""
    path = DATA_DIR / filename
    if not path.exists():
        return f'파일 없음: {filename}'
    return path.read_text(encoding='utf-8')


@mcp.tool()
def search_docs(keyword: str) -> str:
    """data/ 폴더의 모든 문서에서 키워드를 검색해 관련 단락을 반환한다."""
    results = []
    for doc_path in DATA_DIR.glob('*.md'):
        content = doc_path.read_text(encoding='utf-8')
        # 키워드가 포함된 단락만 추출
        paragraphs = [p.strip() for p in content.split('\n\n') if keyword in p]
        if paragraphs:
            results.append(f'[{doc_path.name}]\n' + '\n'.join(paragraphs[:3]))
    return '\n\n'.join(results) if results else f'"{keyword}" 검색 결과 없음'


if __name__ == '__main__':
    # SSE 모드로 실행 — solution.py가 http://localhost:8001/sse 로 연결
    mcp.run(transport='sse', host='0.0.0.0', port=8001)
