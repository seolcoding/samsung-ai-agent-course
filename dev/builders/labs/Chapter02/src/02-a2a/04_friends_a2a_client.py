"""
A2A 클라이언트: 내 Agent가 친구 Agent 세 명에게 일정을 물어 축구 약속 잡기 (노트북 셀용)
"""

import uuid
from typing import Annotated, Literal

import a2a.types as t
import httpx
from a2a.client.base_client import BaseClient
from a2a.client.card_resolver import A2ACardResolver
from a2a.client.client import ClientConfig
from a2a.client.transports.jsonrpc import JsonRpcTransport
from a2a.utils.constants import PROTOCOL_VERSION_1_0, VERSION_HEADER
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()

SERVER_URL = "http://127.0.0.1:8003"  # 친구 일정 서버(friends_a2a_server.py)
FRIENDS = ["messi", "ronaldo", "mbappe"]
# A2A-Version 헤더: 서버가 1.x 형식 요청임을 알아보게 한다(없으면 예전 0.3 형식으로 보고 거절한다)
HEADERS = {VERSION_HEADER: PROTOCOL_VERSION_1_0}


# ── 친구 Agent Card 확인 ──────────────────────────────────────────────────────
# 친구마다 <주소>/.well-known/agent-card.json을 읽는다. 모델은 부르지 않는다
async with httpx.AsyncClient(headers=HEADERS) as http:
    for friend in FRIENDS:
        card = await A2ACardResolver(http, f"{SERVER_URL}/{friend}").get_agent_card()
        print(f"[{friend}] {card.name}: {card.description}")
        print(f"    스킬: {[skill.name for skill in card.skills]}")


# ── 친구 한 명에게 A2A로 메시지 보내기 ─────────────────────────────────────────
async def call_friend(friend: str, query: str) -> str:
    """A2A 프로토콜로 친구 Agent에게 메시지를 보내고 답 글을 돌려준다."""
    url = f"{SERVER_URL}/{friend}"
    async with httpx.AsyncClient(headers=HEADERS, timeout=120.0) as http:  # 친구 Agent도 모델을 불러 답하므로 넉넉히 기다린다
        # 1. Agent Card 조회
        card = await A2ACardResolver(http, url).get_agent_card()

        # 2. JSON-RPC 트랜스포트로 클라이언트 생성
        transport = JsonRpcTransport(http, card, f"{url}/")
        client = BaseClient(card, ClientConfig(), transport, [])

        # 3. 메시지 전송
        # 요청 메시지(SendMessageRequest): 보내는 사람(USER), 글 조각(Part), 메시지마다 다른 ID
        req = t.SendMessageRequest(
            message=t.Message(
                role=t.Role.ROLE_USER,
                parts=[t.Part(text=query)],
                message_id=str(uuid.uuid4()),
            )
        )

        async for response in client.send_message(req):
            # 응답의 message: 친구 Agent가 돌려준 Message
            if response.HasField("message"):
                return "".join(
                    part.text for part in response.message.parts if part.text
                )

    return "응답을 받지 못했습니다."


# ── 친구 한 명에게 먼저 물어보기 ───────────────────────────────────────────────
friend = "messi"
friend_answer = await call_friend(friend, "이번 주 저녁 19시에 비는 날 알려 줘.")
print(f"{friend}: {friend_answer}")


# ── 내 Agent(호스트) 만들기 ───────────────────────────────────────────────────
# 내 Agent는 친구의 일정을 모른다. ask_friend 도구로 친구 Agent에게 A2A로 물어볼 뿐이다.
@tool
async def ask_friend(
    friend: Literal["messi", "ronaldo", "mbappe"], message: str
) -> str:
    """친구 일정 Agent에게 A2A로 메시지를 보내고 답을 받는다. friend는 messi, ronaldo, mbappe 중 하나."""
    print(f"[나 → {friend}] {message}")
    try:
        answer = await call_friend(friend, message)
    except Exception as e:  # 친구 Agent가 늦거나 꺼져 있으면 셀을 멈추지 않고, 답이 없다는 사실을 내 Agent에게 알린다
        answer = f"(응답 없음: {type(e).__name__}) {friend} Agent가 답하지 않았습니다."
    print(f"[{friend} → 나] {answer}")
    return answer


class State(TypedDict):
    messages: Annotated[list, add_messages]


host_llm = get_llm().bind_tools([ask_friend])
HOST_SYSTEM = SystemMessage(
    content=(
        "너는 내 축구 약속을 잡아 주는 비서 Agent다. 친구는 messi, ronaldo, mbappe 세 명이다. "
        "1) ask_friend로 세 친구 모두에게 한꺼번에 요청한 시간대에 비는 요일을 묻는다. "
        "2) 세 친구의 답에 모두 들어 있는 요일만 후보로 삼는다. 한 명이라도 안 되는 요일은 후보가 아니다. "
        "3) 후보가 있으면 하나를 골라, 세 친구 모두에게 한꺼번에 ask_friend로 그 요일·시간에 약속을 잡아 달라고 한다. "
        "약속을 잡는 사람(host)은 '나'라고 메시지에 적는다. "
        "4) 후보가 없거나 답하지 않은 친구가 있으면 약속을 잡지 말고, 친구별로 비는 요일(또는 답이 없었다는 것)을 알려 준다. "
        "5) 마지막에 정한 요일과 시간을 한 줄로 알려 준다."
    )
)


async def host_node(state: State) -> dict:
    return {"messages": [await host_llm.ainvoke([HOST_SYSTEM] + state["messages"])]}


builder = StateGraph(State)
builder.add_node("host", host_node)
builder.add_node("tools", ToolNode([ask_friend]))
builder.add_edge(START, "host")
# tools_condition: 도구 호출이 있으면 tools로, 없으면 끝. tools 다음에는 host로 돌아와 결과를 본다
builder.add_conditional_edges("host", tools_condition)
builder.add_edge("tools", "host")
host_agent = builder.compile()


# ── 축구 약속 잡기 ─────────────────────────────────────────────────────────────
request = "이번 주 저녁 19시에 다 같이 축구 한 판 하자. 약속을 잡아 줘."
# 내 Agent를 비동기로 실행한다(ask_friend가 서버와 주고받는 동안 기다린다)
host_agent_result = await host_agent.ainvoke(
    {"messages": [HumanMessage(content=request)]}
)

results = host_agent_result["messages"]
for m in results:
    m.pretty_print()
