"""3-3 과제: 번역 Agent를 A2A로 띄우고 불러 보기

한 파일 안에서 번역 Agent를 A2A 서버로 잠깐 띄우고, 클라이언트가 카드를 읽어 번역을 맡깁니다.
서버를 띄우고 끄는 코드는 맨 아래에 미리 들어 있습니다. ✍️ 목표 1~3 자리만 채웁니다.
"""

import asyncio
import socket
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
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from starlette.applications import Starlette

from config.llm import get_llm

load_dotenv()
llm = get_llm()


def find_free_port() -> int:
    """이 PC에서 지금 비어 있는 포트 번호 하나를 고른다(실습 서버 8000·8001과 부딪히지 않게)."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


PORT = find_free_port()
URL = f"http://127.0.0.1:{PORT}"  # 카드의 주소와 클라이언트가 부를 주소
HEADERS = {VERSION_HEADER: PROTOCOL_VERSION_1_0}  # 클라이언트 요청에 붙이는 A2A 1.x 버전 헤더
QUESTION = "오늘 회의는 오후 3시에 시작합니다."


# ✍️ 목표 1: t.AgentCard와 t.AgentSkill로 Agent Card를 만듭니다(이름 "Translator Agent", 번역 Skill 하나, 주소 URL)
agent_card = t.AgentCard(
    name="Translator Agent",
    description="한국어 문장을 영어로 번역합니다.",
    version="1.0.0",
    capabilities=t.AgentCapabilities(streaming=False),
    default_input_modes=["text"],
    default_output_modes=["text"],
    supported_interfaces=[t.AgentInterface(url=URL)],
    skills=[
        t.AgentSkill(
            id="translate_ko_en",
            name="한영 번역",
            description="한국어 문장을 자연스러운 영어로 번역합니다.",
            tags=["translate"],
        )
    ],
)


# ✍️ 목표 2: 받은 글을 llm으로 영어로 번역해 t.Message로 EventQueue에 내보내는 AgentExecutor를 만들고,
#            RequestHandler와 카드 조회·JSON-RPC 라우트로 Starlette 앱(app)을 조립합니다
class TranslatorExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_text = context.get_user_input() or ""
        response = await llm.ainvoke([
            SystemMessage(content="너는 번역가야. 받은 한국어 문장을 영어로만 번역해."),
            HumanMessage(content=user_text),
        ])
        await event_queue.enqueue_event(
            t.Message(
                role=t.Role.ROLE_AGENT,
                parts=[t.Part(text=response.content)],
                task_id=context.task_id,
                context_id=context.context_id,
                message_id=str(uuid.uuid4()),
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


request_handler = DefaultRequestHandlerV2(
    agent_executor=TranslatorExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=agent_card,
)
app = Starlette(routes=[
    *create_agent_card_routes(agent_card),
    *create_jsonrpc_routes(request_handler, rpc_url="/"),
])


# ✍️ 목표 3: A2ACardResolver로 URL의 카드를 읽어 이름과 스킬 이름을 출력하고,
#            text를 메시지로 보내 응답 parts의 글을 출력합니다(요청에 HEADERS를 붙입니다)
async def call_translator(text: str) -> None:
    async with httpx.AsyncClient(headers=HEADERS, timeout=60.0) as http:
        card = await A2ACardResolver(http, URL).get_agent_card()
        print(f"[카드 조회] 이름: {card.name} / 스킬: {[s.name for s in card.skills]}")

        transport = JsonRpcTransport(http, card, f"{URL}/")
        client = BaseClient(card, ClientConfig(), transport, [])
        req = t.SendMessageRequest(
            message=t.Message(
                role=t.Role.ROLE_USER,
                parts=[t.Part(text=text)],
                message_id=str(uuid.uuid4()),
            )
        )
        print(f"[보낸 문장] {text}")
        async for response in client.send_message(req):
            if response.HasField("message"):
                print("[번역 결과]", "".join(p.text for p in response.message.parts if p.text))


# ── 여기부터는 고치지 않습니다: 서버를 잠깐 띄우고, 클라이언트를 부르고, 반드시 끈다 ──
async def main() -> None:
    if agent_card is None:
        print("(목표 1: 아직 비어 있습니다. Agent Card를 만듭니다)")
    else:
        print(f"[만든 카드] 이름: {agent_card.name} / 스킬: {[s.name for s in agent_card.skills]}")
    if app is None:
        print("(목표 2: 아직 비어 있습니다. AgentExecutor와 Starlette 앱을 만들면 서버를 띄웁니다)")
        return

    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="warning"))
    serve_task = asyncio.create_task(server.serve())
    while not server.started:  # 서버가 뜰 때까지 잠깐 기다린다
        if serve_task.done():
            raise RuntimeError("서버를 띄우지 못했습니다. 위 오류 메시지를 확인합니다.")
        await asyncio.sleep(0.1)
    print(f"[서버] {URL} 에 잠깐 띄웠습니다.")
    try:
        await call_translator(QUESTION)
    finally:
        server.should_exit = True  # 오류가 나도 서버를 끄고 끝날 때까지 기다린다
        await serve_task
        print(f"[서버] 껐습니다(포트 {PORT}).")


asyncio.run(main())
