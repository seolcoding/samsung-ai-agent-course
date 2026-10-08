"""
MCP 클라이언트 실습

01_mcp_server.py에서 만든 로컬 MCP 서버에 연결해
LangGraph Agent가 도구로 사용하는 예제.

사전 준비:
  터미널 A에서 먼저 실행: python 01_mcp_server.py
  터미널 B에서 이 파일 실행: python 02_mcp_client.py
"""

import asyncio
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()


# ── MCP 서버 연결 설정 ────────────────────────────────────────────────────────
# SSE(Server-Sent Events): HTTP 기반 MCP 연결 방식.
# 01_mcp_server.py를 HTTP 모드로 실행하면 /sse 엔드포인트가 열린다.

'''
    'MCP 서버 이름': {
        '실행 방식': sse / stdio,
        '요청 경로':
        '실행 명령어': 
        '추가 인자 목록': 
    }
'''

# 상용화 되어 있는 MCP Host를 사용하는 경우에는, 아래의 설정만 HOST에 등록함으로써 `특정 MCP Server`` 사용할 준비 끗

# 주석 처리 및 해제 -> ctrl + / 
MCP_CONFIG = {
    'tutorial': {
        'transport': 'sse',
        'url': 'http://localhost:8000/sse',
    },
    # 'tutorial': {
    #     "transport": "stdio",
    #     "command": "python",
    #     "args": ["course/Chapter02/code/raw/01-mcp/01_mcp_server.py", '--stdio'],
    # },
}


class State(TypedDict):
    messages: Annotated[list, add_messages]


async def main():
    # MultiServerMCPClient의 첫번째 인자: 연결 대상 들
    client = MultiServerMCPClient(MCP_CONFIG)
    # get_tools()는 서버에 연결해 도구 목록을 가져온다.
    tools = await client.get_tools()

    print('=== 사용 가능한 MCP 도구 ===')
    for t in tools:
        print(f'  - {t.name}: {t.description}')
    print()

    llm = get_llm().bind_tools(tools)
    tool_node = ToolNode(tools)

    def agent_node(state: State) -> dict:
        # 랭체인에서 어떠한 실행 -> invoke 메서드
        # 하나의 Runnable한 인터페이스 실행 -> invoke 메서드

        # 에이전트 노드: 사용자가 입력한 메시지기반 답변 생성
            # 상태에 있는 사용자 입력값을 LLM에게 전달
        return {'messages': [llm.invoke(state['messages'])]}

    builder = StateGraph(State)
    builder.add_node('agent', agent_node)
    builder.add_node('tools', tool_node)
    
    builder.add_edge(START, 'agent')
    builder.add_conditional_edges('agent', tools_condition)
            # edge(from, to) -> 조건부, 도구들
            #                -> 어떤 상황에서 어떤 도구들을 호출해야 하는지 처리하기 복잡하다
            #                -> 도구 종류도 천차만별 (MCP 서버마다), 도구 이름도 천차만별...
    builder.add_edge('tools', 'agent')
    app = builder.compile()

    # 도구를 사용해 요청 처리
    questions = [
        '지금 몇 시야?',
        '체중 70kg, 키 175cm면 BMI가 얼마야?',
        '할 일 목록에 "LangGraph 공부" (우선순위 3)를 추가하고 현재 목록을 보여줘.',
    ]

    for question in questions:
        print(f'Q: {question}')
        result = await app.ainvoke({
            'messages': [HumanMessage(content=question)],
        })
        # print(f'A: {result["messages"][-1].content}')
        print(result)
        print()


if __name__ == '__main__':
    asyncio.run(main())
