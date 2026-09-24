"""a2a-sdk 1.x의 실제 Card/JSON-RPC 경로. 답변 작성만 교육용 규칙으로 대체한다."""

import uuid

import a2a.types as t
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers.default_request_handler_v2 import DefaultRequestHandlerV2
from a2a.server.routes.agent_card_routes import create_agent_card_routes
from a2a.server.routes.jsonrpc_routes import create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from starlette.applications import Starlette

from courseware.knowledge import answer_from_documents


class ResearchExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        result = answer_from_documents(context.get_user_input() or "")
        await event_queue.enqueue_event(t.Message(
            role=t.Role.ROLE_AGENT,
            parts=[t.Part(text="[교육용 모의 Researcher]\n" + result["answer"])],
            task_id=context.task_id,
            context_id=context.context_id,
            message_id=str(uuid.uuid4()),
        ))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("이 즉시 응답 실습 서버는 장기 Task 취소를 지원하지 않습니다.")


def build_a2a_app(base_url: str = "http://127.0.0.1:8766") -> Starlette:
    card = t.AgentCard(
        name="Course Researcher",
        description="교육용 AI Agent 자료를 찾아 출처와 함께 반환합니다.",
        version="1.0.0",
        capabilities=t.AgentCapabilities(streaming=False),
        default_input_modes=["text"], default_output_modes=["text"],
        supported_interfaces=[t.AgentInterface(url=base_url + "/", protocol_binding="JSONRPC", protocol_version="1.0")],
        skills=[t.AgentSkill(id="research", name="교육 자료 조사", description="교육 자료에서 근거를 검색합니다.", tags=["research", "training"])],
    )
    handler = DefaultRequestHandlerV2(agent_executor=ResearchExecutor(), task_store=InMemoryTaskStore(), agent_card=card)
    return Starlette(routes=[*create_agent_card_routes(card), *create_jsonrpc_routes(handler, rpc_url="/")])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(build_a2a_app(), host="127.0.0.1", port=8766)
