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
# TODO: 2가지 상황에 대해 MCP 연결 방식을 정의한다.
'''
    '서버의 이름' : {
        '실행 방식': sse / stdio
        '요청 경로': 
        '실행 명령어':
        '추가 인자 목록': 
    }
'''

MCP_CONFIG = {
    # 'tutorial': {
    #     'transport': 'sse',
    #     'url': 'http://localhost:8000/sse'
    # },
   'tutorial': {
        "transport": "stdio",
        "command": "python",
        "args": ["src/raw/Chapter02/01-mcp/01_mcp_server.py", '--stdio'],
    },
}


class State(TypedDict):
    messages: Annotated[list, add_messages]


async def main():
    # TODO: MCP 설정으로 MultiServerMCPClient를 생성해 주세요.
    client = MultiServerMCPClient(MCP_CONFIG)
    # get_tools()는 서버에 연결해 도구 목록을 가져온다.
    # TODO: MCP 서버에서 도구 목록을 가져와 주세요.
        # 서버로부터 정보를 받아와서, 도구화 하고, 내 agent로서도 동작을 해야한다.
        # 해당 작업은 비동기 처리
    tools = await client.get_tools()
    # local_tools = [ ] + [tools]
    print('=== 사용 가능한 MCP 도구 ===')
    for t in tools:
        print(f'  - {t.name}: {t.description}')
    print()

    # TODO: 가져온 MCP 도구를 LLM과 ToolNode에 연결해 주세요.
        # 내 LLM에게 bind_tools를 사용해서 내가 가진 도구 목록을 LLM에게 전달
    llm = get_llm().bind_tools(tools)
        # 그 도구들을 도구 노드로 변환
    tool_node = ToolNode(tools)

    # 우리 그래프에서 해당하는 노드에게 기대하는바
    # 정해진 어떤 LLM을 호출해서
        # 사용자가 보낸 메시지를 토대로
        # 새로운 문자을 만들어 내는 것
    def agent_node(state: State) -> dict:
        # TODO: State의 messages를 도구가 연결된 LLM에 전달해 주세요.
        return {'messages': [llm.invoke(state['messages'])]}

    builder = StateGraph(State)
    builder.add_node('agent', agent_node)
    builder.add_node('tools', tool_node)
    builder.add_edge(START, 'agent')
    # TODO: tools_condition으로 도구 호출 여부를 분기하고 tools 이후 agent로 돌아오게 연결해 주세요.
    # LLM이 도구를 사용해야 한다고 판단한다면 해당 도구를 호출
        # 그게 아니라면 END를...
    builder.add_conditional_edges('agent', tools_condition)
    builder.add_edge('tools', 'agent')

    # TODO: 그래프를 컴파일해 주세요.
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
        print(f'A: {result["messages"][-1].content}')
        print()


if __name__ == '__main__':
    asyncio.run(main())
