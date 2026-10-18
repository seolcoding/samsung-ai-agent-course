"""3-3 과제: 번역 Agent를 A2A로 띄우고 불러 보기"""

from dotenv import load_dotenv

from config.llm import get_llm

load_dotenv()

llm = get_llm()


# 아래에 AI와 함께 코드를 작성합니다
import asyncio
import uuid

import a2a.types as t
import httpx
import uvicorn
from a2a.client.base_client import BaseClient
from a2a.client.card_resolver import A2ACardResolver
from a2a.client.client import ClientConfig
from a2a.client.transports.jsonrpc import JsonRpcTransport
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers.default_request_handler_v2 import DefaultRequestHandlerV2
from a2a.server.routes.agent_card_routes import create_agent_card_routes
from a2a.server.routes.jsonrpc_routes import create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.utils.constants import PROTOCOL_VERSION_1_0, VERSION_HEADER
from langchain_core.messages import HumanMessage, SystemMessage
from starlette.applications import Starlette

URL = "http://127.0.0.1:8011"


# ── 서버: 번역 Agent ─────────────────────────────────────────
class TranslatorExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_text = context.get_user_input() or ""
        response = await llm.ainvoke([
            SystemMessage(content="너는 번역가야. 받은 한국어 문장을 영어로만 번역해."),
            HumanMessage(content=user_text),
        ])
        await event_queue.enqueue_event(t.Message(
            role=t.Role.ROLE_AGENT,
            parts=[t.Part(text=response.content)],
            task_id=context.task_id,
            context_id=context.context_id,
            message_id=str(uuid.uuid4()),
        ))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


agent_card = t.AgentCard(
    name="Translator Agent",
    description="한국어 문장을 영어로 번역합니다.",
    version="1.0.0",
    capabilities=t.AgentCapabilities(streaming=False),
    default_input_modes=["text"],
    default_output_modes=["text"],
    supported_interfaces=[t.AgentInterface(url=URL)],
    skills=[t.AgentSkill(id="translate_ko_en", name="한영 번역",
                         description="한국어를 영어로 번역합니다.", tags=["translate"])],
)

request_handler = DefaultRequestHandlerV2(
    agent_executor=TranslatorExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=agent_card,
)
app = Starlette(routes=[
    *create_agent_card_routes(agent_card),
    *create_jsonrpc_routes(request_handler, rpc_url="/"),
])


# ── 클라이언트: 카드 조회 → 메시지 한 번 ────────────────────────
async def call_translator(text: str) -> None:
    headers = {VERSION_HEADER: PROTOCOL_VERSION_1_0}
    async with httpx.AsyncClient(headers=headers, timeout=60.0) as http:
        card = await A2ACardResolver(http, URL).get_agent_card()
        print(f"이름 : {card.name}")
        print(f"스킬 : {[s.name for s in card.skills]}")

        transport = JsonRpcTransport(http, card, f"{URL}/")
        client = BaseClient(card, ClientConfig(), transport, [])
        req = t.SendMessageRequest(message=t.Message(
            role=t.Role.ROLE_USER,
            parts=[t.Part(text=text)],
            message_id=str(uuid.uuid4()),
        ))
        print(f"보낸 문장: {text}")
        async for response in client.send_message(req):
            if response.HasField("message"):
                print("번역 결과:", "".join(p.text for p in response.message.parts))


async def main() -> None:
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8011, log_level="warning"))
    serve_task = asyncio.create_task(server.serve())
    while not server.started:  # 서버가 뜰 때까지 잠깐 기다린다
        await asyncio.sleep(0.1)
    try:
        await call_translator("오늘 회의는 오후 3시에 시작합니다.")
    finally:
        server.should_exit = True  # 서버를 끄고 끝날 때까지 기다린다
        await serve_task
        print("서버를 껐습니다.")


asyncio.run(main())
