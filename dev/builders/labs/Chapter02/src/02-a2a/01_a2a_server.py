"""
A2A 서버: 친구 일정 Agent 세 명(메시·호날두·음바페)을 A2A로 띄우기

A2A(Agent-to-Agent)는 Google이 제안한 Agent 사이 통신 표준이다.
서버 하나에 친구 Agent 세 명을 주소만 다르게 띄운다.
  http://127.0.0.1:8001/messi/   http://127.0.0.1:8001/ronaldo/   http://127.0.0.1:8001/mbappe/
일정은 수업용으로 지어낸 것이다(실제 선수 일정이 아니다).
"""

import uuid
from typing import Annotated

import a2a.types as t
import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers.default_request_handler_v2 import (
    DefaultRequestHandlerV2,
)
from a2a.server.routes.agent_card_routes import create_agent_card_routes
from a2a.server.routes.jsonrpc_routes import create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from starlette.applications import Starlette
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()


# ── 친구들의 이번 주 일정 (수업용으로 지어낸 일정) ──────────────────────────────
# 요일마다 세 시간대(10시·14시·19시)가 있다. busy에 적히지 않은 시간은 비어 있다.
DAYS = ["월", "화", "수", "목", "금", "토", "일"]
TIMES = ["10시", "14시", "19시"]

FRIENDS = {
    "messi": {
        "name": "메시",
        "style": "차분하고 겸손한 말투",
        "busy": {
            "월": {"10시": "팀 훈련", "19시": "인터 마이애미 경기"},
            "화": {"10시": "팀 훈련", "14시": "광고 촬영", "19시": "자선 행사"},
            "수": {"10시": "팀 훈련", "19시": "대표팀 영상 미팅"},
            "목": {"10시": "팀 훈련", "14시": "재활 운동"},
            "금": {"10시": "팀 훈련", "19시": "가족 저녁"},
            "토": {"14시": "가족 나들이", "19시": "리그 경기"},
            "일": {"10시": "가족 브런치"},
        },
    },
    "ronaldo": {
        "name": "호날두",
        "style": "자신감 넘치는 말투로, 마지막에 'Siuuu!'를 붙인다",
        "busy": {
            "월": {"10시": "헬스장", "14시": "광고 촬영", "19시": "야간 헬스장"},
            "화": {"10시": "헬스장", "19시": "알나스르 경기"},
            "수": {"10시": "헬스장"},
            "목": {"10시": "헬스장", "14시": "인터뷰"},
            "금": {"10시": "헬스장", "14시": "수영", "19시": "다큐 촬영"},
            "토": {"14시": "사인회", "19시": "팬 미팅"},
            "일": {"14시": "회복 훈련", "19시": "알나스르 경기"},
        },
    },
    "mbappe": {
        "name": "음바페",
        "style": "빠르고 밝은 말투",
        "busy": {
            "월": {"10시": "팀 훈련", "19시": "챔피언스리그 경기"},
            "화": {"10시": "팀 훈련"},
            "수": {"10시": "팀 훈련", "14시": "스폰서 행사", "19시": "게임 방송"},
            "목": {"10시": "팀 훈련"},
            "금": {"10시": "팀 훈련", "19시": "대표팀 소집"},
            "토": {"19시": "라리가 경기"},
            "일": {"10시": "회복 훈련", "14시": "가족 식사", "19시": "영화 보기"},
        },
    },
}


# ── 친구 Agent 만들기 ─────────────────────────────────────────────────────────
# 친구마다 같은 모양의 작은 LangGraph Agent를 만든다. 도구는 그 친구의 일정만 본다.


class State(TypedDict):
    messages: Annotated[list, add_messages]


def make_friend_agent(friend: str):
    info = FRIENDS[friend]
    booked = {}  # 서버가 켜져 있는 동안 잡은 약속({요일: {시간: 약속}}). 서버를 다시 띄우면 비워진다

    @tool
    def check_schedule() -> str:
        """이번 주(월~일) 10시·14시·19시 일정을 알려 준다. 일정이 없으면 '비어 있음'."""
        print(f"[{friend}] check_schedule()")
        week = []
        for day in DAYS:
            plans = {**info["busy"].get(day, {}), **booked.get(day, {})}
            week.append(
                f"{day}: "
                + ", ".join(f"{time} {plans.get(time, '비어 있음')}" for time in TIMES)
            )
        return "\n".join(week)

    @tool
    def book_match(day: str, time: str, host: str) -> str:
        """비어 있는 시간에 축구 약속을 잡는다. day는 '목'처럼 요일 한 글자, time은 10시·14시·19시 중 하나, host는 약속을 잡는 사람."""
        print(f"[{friend}] book_match({day}, {time}, {host})")
        day, time = day.strip()[:1], time.strip()
        if day not in DAYS or time not in TIMES:
            return (
                "요일은 월~일 한 글자, 시간은 10시·14시·19시 중 하나로 다시 요청합니다."
            )
        plan = booked.get(day, {}).get(time) or info["busy"].get(day, {}).get(time)
        if plan:
            return f"{day} {time}에는 이미 '{plan}' 일정이 있어 잡을 수 없습니다."
        booked.setdefault(day, {})[time] = f"축구 약속({host})"
        return f"{day} {time}에 {host}와(과) 축구 약속을 잡았습니다."

    tools = [check_schedule, book_match]
    # TODO: 친구의 두 도구를 LLM과 ToolNode에 연결해 주세요.
    llm = get_llm().bind_tools(tools)
    tool_node = ToolNode(tools)

    system = SystemMessage(
        content=(
            f"너는 {info['name']}의 일정 비서 Agent다. 일정은 수업용으로 지어낸 것이다. "
            "일정을 물으면 check_schedule로 확인하고, 물어본 시간대에 비어 있는 요일을 빠짐없이 말한다. "
            "약속을 잡아 달라고 하면 바로 book_match로 잡는다(book_match가 비었는지 스스로 확인한다). "
            f"답은 한국어 두세 문장으로, {info['style']}으로 한다."
        )
    )

    def agent_node(state: State) -> dict:
        return {"messages": [llm.invoke([system] + state["messages"])]}

    builder = StateGraph(State)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tool_node)
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    return builder.compile()


friend_agents = {friend: make_friend_agent(friend) for friend in FRIENDS}


# ── A2A AgentExecutor ─────────────────────────────────────────────────────────
# AgentExecutor.execute(): A2A 요청(RequestContext)에서 메시지 글을 읽어
# 친구 Agent를 실행하고, 답을 A2A Message로 감싸 EventQueue에 보낸다.


class FriendExecutor(AgentExecutor):
    def __init__(self, agent):
        self.agent = agent  # 이 실행기가 맡은 친구 Agent

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # context.get_user_input(): 받은 메시지의 텍스트 파트를 모아 문자열로 돌려준다
        user_text = context.get_user_input() or ""

        # TODO: 친구 Agent를 비동기로 실행하고 마지막 답을 꺼내 주세요.
        result = await self.agent.ainvoke(
            {"messages": [HumanMessage(content=user_text)]}
        )
        answer = result["messages"][-1].content

        # t.Message: A2A 응답 메시지. t.Part(text=...): 텍스트 파트
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
# Agent Card: 이 Agent가 누구이고 무엇을 할 수 있는지 적은 자기소개(메타데이터).
# 다른 Agent는 <주소>/.well-known/agent-card.json에서 이 카드를 읽어 친구를 찾는다(discover).


def make_card(friend: str) -> t.AgentCard:
    info = FRIENDS[friend]
    return t.AgentCard(
        name=f"{info['name']} 일정 Agent",
        description=f"{info['name']}의 이번 주 일정을 알려 주고, 비어 있는 시간에 축구 약속을 잡습니다(수업용 가상 일정).",
        version="1.0.0",
        capabilities=t.AgentCapabilities(streaming=False),
        default_input_modes=["text"],
        default_output_modes=["text"],
        supported_interfaces=[t.AgentInterface(url=f"http://127.0.0.1:8001/{friend}/")],
        skills=[
            t.AgentSkill(
                id="soccer_schedule",
                name="일정 확인·축구 약속",
                description="이번 주 빈 시간을 알려 주고, 비어 있는 시간에 축구 약속을 잡습니다.",
                tags=["schedule", "soccer"],
                examples=[
                    "이번 주 저녁 19시에 비는 날 알려 줘",
                    "목요일 19시에 축구 약속 잡아 줘",
                ],
            )
        ],
    )


# ── Starlette 앱 조립 ─────────────────────────────────────────────────────────
# 서버 하나에 친구 세 명을 주소만 다르게 단다: /messi/, /ronaldo/, /mbappe/
# 친구마다 카드 주소(/<친구>/.well-known/agent-card.json)와 요청을 받는 주소(/<친구>/)가 있다.

routes = []
for friend, agent in friend_agents.items():
    card = make_card(friend)
    handler = DefaultRequestHandlerV2(
        agent_executor=FriendExecutor(agent),
        task_store=InMemoryTaskStore(),
        agent_card=card,
    )
    routes += create_agent_card_routes(
        card, card_url=f"/{friend}/.well-known/agent-card.json"
    )
    routes += create_jsonrpc_routes(handler, rpc_url=f"/{friend}/")

app = Starlette(routes=routes)

if __name__ == "__main__":
    print("친구 일정 A2A 서버 시작: http://localhost:8001")
    for friend in FRIENDS:
        print(
            f"  {FRIENDS[friend]['name']}: http://localhost:8001/{friend}/.well-known/agent-card.json"
        )
    # 127.0.0.1: 이 PC에서 오는 요청만 받는다. 0.0.0.0이면 다른 PC의 요청도 받는다.
    uvicorn.run(app, host="127.0.0.1", port=8001)
