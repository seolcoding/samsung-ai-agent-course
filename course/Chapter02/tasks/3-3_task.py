"""3-3 과제 · 번역 Agent를 A2A로 띄우고 불러 보기

▶️ 실행   uv run --env-file .env python course/Chapter02/tasks/3-3_task.py
✅ 확인   실행하면 맨 끝에 🟢/⛔가 나옵니다
🆘 막히면 오류 메시지 전체를 AI에게 붙여 넣기
"""

import asyncio
import inspect
import socket
import uuid

import a2a.types as t
import httpx
import uvicorn
from a2a.client import A2ACardResolver, BaseClient, ClientConfig
from a2a.client.transports import JsonRpcTransport
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandlerV2
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.utils.constants import PROTOCOL_VERSION_1_0, VERSION_HEADER
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from starlette.applications import Starlette

from config.llm import get_llm

load_dotenv()
llm = get_llm()

with socket.socket() as s:  # 비어 있는 포트 하나를 고릅니다
    s.bind(("127.0.0.1", 0))
    PORT = s.getsockname()[1]
URL = f"http://127.0.0.1:{PORT}"
made = {"card": None, "sent": [], "reply": None}  # 맨 끝 확인에서 씁니다


def make_card():
    # ✍️ 1. 번역 Agent의 카드 만들기
    # ✨ t.AgentCard · name "Translator Agent" · supported_interfaces=[t.AgentInterface(url=URL)] · skills=[t.AgentSkill 한영 번역] · 3-3 LAB agent_card 참고
    print("(1. 아직 작성하지 않았습니다)")


class TranslatorExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        system = SystemMessage(content="받은 한국어 문장을 영어로만 번역해.")
        response = await llm.ainvoke([system, HumanMessage(content=context.get_user_input() or "")])
        made["sent"].append(response.content)
        await event_queue.enqueue_event(t.Message(
            role=t.Role.ROLE_AGENT, parts=[t.Part(text=response.content)],
            task_id=context.task_id, context_id=context.context_id, message_id=str(uuid.uuid4()),
        ))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


async def call_translator(http: httpx.AsyncClient, text: str) -> str:
    # ✍️ 2. 카드를 읽고 번역 맡기기
    # ✨ A2ACardResolver(http, URL) 카드 · JsonRpcTransport · BaseClient · t.SendMessageRequest → send_message → 응답 parts 글 return · 3-3 LAB call_researcher 참고
    return "(2. 아직 작성하지 않았습니다)"


async def main() -> None:
    agent_card = made["card"] = make_card()
    if agent_card is None:
        return
    handler = DefaultRequestHandlerV2(agent_executor=TranslatorExecutor(), task_store=InMemoryTaskStore(), agent_card=agent_card)
    app = Starlette(routes=[*create_agent_card_routes(agent_card), *create_jsonrpc_routes(handler, rpc_url="/")])

    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="warning"))
    serve_task = asyncio.create_task(server.serve())
    while not server.started:
        if serve_task.done():
            raise RuntimeError("서버를 띄우지 못했습니다. 위 오류 메시지를 확인합니다.")
        await asyncio.sleep(0.1)
    print(f"[서버] {URL} 에 잠깐 띄웠습니다.")
    try:
        async with httpx.AsyncClient(headers={VERSION_HEADER: PROTOCOL_VERSION_1_0}, timeout=60.0) as http:
            made["reply"] = await call_translator(http, "오늘 회의는 오후 3시에 시작합니다.")
            print(f"[번역 결과] {made['reply']}")
    finally:
        server.should_exit = True  # 오류가 나도 서버를 끕니다
        await serve_task
        print(f"[서버] 껐습니다(포트 {PORT}).")


asyncio.run(main())


# ── ✅ 확인 (바꾸지 않습니다) ──
print("\n✅ 확인")
card = made["card"]
if card is None:
    print("⛔ 1. 아직 작성하지 않았습니다")
elif card.name != "Translator Agent" or not card.skills or URL not in [i.url for i in card.supported_interfaces]:
    print("⛔ 1. 카드의 이름(Translator Agent)·스킬·주소(URL)를 확인합니다")
else:
    print("🟢 1. Translator Agent 카드에 스킬과 이 서버 주소가 있습니다")
if "아직 작성하지 않았습니다" in inspect.getsource(call_translator):
    print("⛔ 2. 아직 작성하지 않았습니다")
elif card is None:
    print("⛔ 2. 1의 카드가 있어야 서버를 띄워 확인합니다")
elif not made["sent"] or str(made["reply"]).strip() != made["sent"][-1].strip():
    print("⛔ 2. call_translator가 돌려준 글이 서버가 A2A로 보낸 번역과 다릅니다")
else:
    print("🟢 2. A2A로 번역을 맡기고 서버가 보낸 응답을 그대로 받았습니다")
