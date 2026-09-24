"""
A2A 서버: LangGraph Agent를 A2A 프로토콜로 노출하기

A2A(Agent-to-Agent)는 Google이 제안한 에이전트 간 통신 표준이다.
에이전트를 HTTP 서비스로 노출하면 프레임워크에 관계없이 (LangGraph, CrewAI, AutoGen 등)
서로 통신할 수 있다.

실행:
  python 01_a2a_server.py   (포트 8001)

확인:
  curl http://localhost:8001/.well-known/agent-card.json
"""

import asyncio
import uuid
from typing import Annotated

import a2a.types as t
import uvicorn
# AgentExecutor: 실질적으로 에이전트를 실행하도록 하는 주체
    # 내부적으로 정의해둔 랭그래프 에이전트를 실행
# RequestContext
    # task, message | 메시지 자체를 발행하고 처리하는 로직
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers.default_request_handler_v2 import DefaultRequestHandlerV2
from a2a.server.routes.agent_card_routes import create_agent_card_routes
from a2a.server.routes.jsonrpc_routes import create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.events.in_memory_queue_manager import InMemoryQueueManager
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from starlette.applications import Starlette
from starlette.routing import Route
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()


# ── 내부 LangGraph Agent ──────────────────────────────────────────────────────

@tool
def search_web(query: str) -> str:
    """웹에서 정보를 검색한다."""
    return f'"{query}" 검색 결과: 해당 주제에 대한 최신 정보 (데모 데이터)'


class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = get_llm().bind_tools([search_web])
tool_node = ToolNode([search_web])


def agent_node(state: State) -> dict:
    return {'messages': [llm.invoke(state['messages'])]}


builder = StateGraph(State)
builder.add_node('agent', agent_node)
builder.add_node('tools', tool_node)
builder.add_edge(START, 'agent')
builder.add_conditional_edges('agent', tools_condition)
builder.add_edge('tools', 'agent')
langgraph_agent = builder.compile()


# ── A2A AgentExecutor ─────────────────────────────────────────────────────────
# AgentExecutor.execute(): RequestContext에서 사용자 메시지를 읽어
# EventQueue에 결과(Message)를 발행한다.
#
# a2a-sdk 1.x에서는 Pydantic 대신 protobuf 타입(a2a.types)을 사용한다.
# protobuf는 스키마를 .proto 파일로 정의하고, 언어별 코드를 자동 생성하는 직렬화 포맷이다.
# gRPC 기반의 크로스 플랫폼 통신을 위해 SDK가 protobuf로 전환됐다.

class ResearcherExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # context.get_user_input(): 사용자 메시지의 텍스트 파트를 모아 문자열로 반환
        user_text = context.get_user_input() or ''

        result = await langgraph_agent.ainvoke({
            'messages': [HumanMessage(content=user_text)]
        })
        answer = result['messages'][-1].content

        # t.Message: protobuf 기반 응답 메시지
        # t.Part(text=...): 텍스트 파트 (1.x에서는 TextPart 대신 Part.text 직접 사용)
        await event_queue.enqueue_event(
            t.Message(
                role=t.Role.ROLE_AGENT,
                parts=[t.Part(text=answer)],
                message_id=str(uuid.uuid4()),
                task_id=context.task_id,
                context_id=context.context_id,
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


# ── Agent Card ────────────────────────────────────────────────────────────────
# Agent Card: 이 에이전트가 무엇을 할 수 있는지 설명하는 메타데이터.
# 클라이언트는 /.well-known/agent-card.json에서 이를 읽어 에이전트를 발견(discover)한다.

agent_card = t.AgentCard(
    name='Researcher Agent',
    description='주어진 주제를 웹에서 조사하고 요약 정보를 제공합니다.',
    version='1.0.0',
    default_input_modes=['text'],
    default_output_modes=['text'],
    capabilities=t.AgentCapabilities(streaming=False),
    supported_interfaces=[t.AgentInterface(url='http://localhost:8001')],
    skills=[
        t.AgentSkill(
            id='web_research',
            name='웹 리서치',
            description='주제를 검색해 핵심 정보를 수집하고 정리합니다.',
            tags=['research', 'web'],
            examples=['AI Agent 기술 트렌드 조사', 'LangGraph 최신 기능 알려줘'],
        )
    ],
)

# ── Starlette 앱 조립 ─────────────────────────────────────────────────────────

queue_manager = InMemoryQueueManager()
task_store = InMemoryTaskStore()

request_handler = DefaultRequestHandlerV2(
    agent_executor=ResearcherExecutor(),
    task_store=task_store,
    agent_card=agent_card,
    queue_manager=queue_manager,
)

routes: list[Route] = [
    *create_agent_card_routes(agent_card),
    *create_jsonrpc_routes(request_handler, rpc_url='/'),
]

app = Starlette(routes=routes)

if __name__ == '__main__':
    print('Researcher A2A 서버 시작: http://localhost:8001')
    print('Agent Card: http://localhost:8001/.well-known/agent-card.json')
    uvicorn.run(app, host='0.0.0.0', port=8001)
