"""
A2A 클라이언트: 다른 Agent에게 작업을 위임하기

실행 순서:
  1. 터미널 1: python 01_a2a_server.py
  2. 터미널 2: python 02_a2a_client.py
"""

import asyncio
import uuid

import a2a.types as t
import httpx
from a2a.client.base_client import BaseClient
from a2a.client.card_resolver import A2ACardResolver
from a2a.client.client import ClientConfig
from a2a.client.transports.jsonrpc import JsonRpcTransport
from a2a.utils.constants import PROTOCOL_VERSION_1_0, VERSION_HEADER
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage


from config.llm import get_llm

load_dotenv()

RESEARCHER_URL = 'http://127.0.0.1:8001'


async def call_researcher(query: str) -> str:
    """A2A 프로토콜로 Researcher Agent에게 조사를 요청한다.

    A2A-Version 헤더를 명시해야 서버가 1.x 형식 요청임을 인식한다.
    헤더가 없으면 서버는 레거시(0.3) 버전으로 가정하여 거부한다.
    """
    headers = {VERSION_HEADER: PROTOCOL_VERSION_1_0}
    async with httpx.AsyncClient(headers=headers, timeout=60.0) as http:
        # 1. Agent Card 조회: 에이전트가 어떤 기능을 제공하는지 확인
        resolver = A2ACardResolver(http, RESEARCHER_URL)
        card = await resolver.get_agent_card()

        # 2. JSON-RPC 트랜스포트로 클라이언트 생성
        transport = JsonRpcTransport(http, card, f'{RESEARCHER_URL}/')
        client = BaseClient(card, ClientConfig(), transport, [])

        # 3. 메시지 전송
        req = t.SendMessageRequest(
            message=t.Message(
                role=t.Role.ROLE_USER,
                parts=[t.Part(text=query)],
                message_id=str(uuid.uuid4()),
            )
        )
        async for response in client.send_message(req):
            # StreamResponse.message: 에이전트가 반환한 Message 객체
            if response.HasField('message'):
                return ''.join(
                    part.text for part in response.message.parts if part.text
                )

    return '응답을 받지 못했습니다.'


async def main():
    # ── Agent Card 확인 ────────────────────────────────────────────────────────
    async with httpx.AsyncClient() as http:
        resp = await http.get(f'{RESEARCHER_URL}/.well-known/agent-card.json')
        card = resp.json()

    print('=== Researcher Agent Card ===')
    print(f'이름   : {card["name"]}')
    print(f'설명   : {card["description"]}')
    print(f'스킬   : {[s["name"] for s in card.get("skills", [])]}')
    print()

    # ── Researcher에게 조사 위임 ───────────────────────────────────────────────
    topic = 'LangGraph Multi-Agent 시스템의 실제 활용 사례'
    print(f'=== Researcher에게 위임: "{topic}" ===')
    research_result = await call_researcher(topic)
    print(f'리서치 결과:\n{research_result}\n')

    # ── Writer가 리서치 결과로 글 작성 ────────────────────────────────────────
    # Writer는 직접 LLM을 쓰지만, 리서치 작업은 Researcher에게 위임했다.
    # → 이종 Agent 간 역할 분리가 A2A의 핵심
    print('=== Writer가 블로그 포스트 작성 ===')
    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content='너는 전문 작가야. 리서치 결과를 바탕으로 블로그 포스트를 작성해줘.'),
        HumanMessage(content=f'리서치 결과:\n{research_result}\n\n이 내용으로 블로그 포스트를 작성해줘.'),
    ])
    print(response.content)


if __name__ == '__main__':
    asyncio.run(main())
