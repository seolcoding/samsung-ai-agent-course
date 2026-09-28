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


# TODO: search_web 도구를 LLM과 ToolNode에 연결해 주세요.
llm = get_llm().bind_tools([search_web])
tool_node = ToolNode([search_web])


def agent_node(state: State) -> dict:
    # TODO: State의 messages를 도구가 연결된 LLM에 전달해 주세요.
    return {'messages': [llm.invoke(state['messages'])]}


builder = StateGraph(State)
builder.add_node('agent', agent_node)
builder.add_node('tools', tool_node)
builder.add_edge(START, 'agent')
# TODO: tools_condition으로 도구 호출 여부를 분기하고 tools 이후 agent로 돌아오게 연결해 주세요.
builder.add_conditional_edges('agent', tools_condition)
builder.add_edge('tools', 'agent')
# TODO: LangGraph Agent를 컴파일해 주세요.
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

        # TODO: 내부 LangGraph Agent를 비동기로 호출하고 최종 답변을 추출해 주세요.
        result = await langgraph_agent.ainvoke({
            'messages': [HumanMessage(content=user_text)]
        })
        answer = result['messages'][-1].content

        # t.Message: protobuf 기반 응답 메시지
        # t.Part(text=...): 텍스트 파트 (1.x에서는 TextPart 대신 Part.text 직접 사용)
        # TODO: A2A Message를 만들어 EventQueue에 발행해 주세요.
        await event_queue.enqueue_event(
            t.Message(
                role=t.Role.ROLE_AGENT,
                parts=[t.Part(text=answer)],
                task_id=context.task_id,
                context_id=context.context_id,
                message_id=str(uuid.uuid4()),
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


# ── Agent Card ────────────────────────────────────────────────────────────────
# Agent Card: 이 에이전트가 무엇을 할 수 있는지 설명하는 메타데이터.
# 클라이언트는 /.well-known/agent-card.json에서 이를 읽어 에이전트를 발견(discover)한다.

# TODO: Agent Card에 이름, 설명, 입출력 모드, capability, skill 정보를 작성해 주세요.
agent_card = t.AgentCard(
    name='Researcher Agent',
    description='주제를 토대로 웹에서 정보를 조사하고 요약해서 제공합니다.',
    version='1.0.0',
    capabilities=t.AgentCapabilities(streaming=False),
    default_input_modes=['text'], 
    default_output_modes=['text'], 
    supported_interfaces=[t.AgentInterface(url='http://localhost:8001')],
    skills=[
        t.AgentSkill(
            id='web_research',
            name='웹 리서치',
            description='주제를 검색해 핵심 정보를 수집하고 정리합니다.',
            tags=['research', 'web'],
            examples=['AI Agent 기술 트렌드 조사', '랭그래프 최신 기능 알려줘.']
        )
    ]
)

# ── Starlette 앱 조립 ─────────────────────────────────────────────────────────

queue_manager = InMemoryQueueManager()
task_store = InMemoryTaskStore()

request_handler = DefaultRequestHandlerV2(
    # TODO: AgentExecutor, TaskStore, AgentCard, QueueManager를 연결해 주세요.
    agent_executor=ResearcherExecutor(),
    task_store=task_store,
    queue_manager=queue_manager,
    agent_card=agent_card
)

# TODO: Agent Card 라우트와 JSON-RPC 라우트를 생성해 주세요.
routes: list[Route] = [
    *create_agent_card_routes(agent_card),
    *create_jsonrpc_routes(request_handler, rpc_url='/')
]

app = Starlette(routes=routes)

if __name__ == '__main__':
    print('Researcher A2A 서버 시작: http://localhost:8001')
    print('Agent Card: http://localhost:8001/.well-known/agent-card.json')
    uvicorn.run(app, host='0.0.0.0', port=8001)
