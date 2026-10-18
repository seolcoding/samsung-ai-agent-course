"""2-2 과제(강사용 정답): Supervisor가 이끄는 Researcher·Writer·Reviewer 팀

실행(저장소 맨 위에서): uv run --env-file .env python course/Chapter01/tasks/2-2/2-2_task.py
"""
from typing import Annotated, Literal

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()

llm = get_llm()

TOPIC = "AI Agent 기술의 현황과 전망을 조사해서 짧은 글로 써 줘."
MAX_REVISIONS = 2  # Reviewer가 "수정"을 내도 다시 쓰는 것은 이 횟수까지
REVIEW_RULE = "글이 5문장 이하이고, 마지막 줄이 '한 줄 요약:'으로 시작해야 통과다."


@tool
def search_web(query: str) -> str:
    """웹에서 주제를 조사한다."""
    return (
        f'["{query}" 검색 결과]\n'
        "- 주요 동향: 최근 급격한 성장세를 보이고 있음\n"
        "- 핵심 기술 요소: 도구 호출, 계획 세우기, 기억\n"
        "- 주요 플레이어: OpenAI, Anthropic, Google DeepMind\n"
        "- 미래 전망: 향후 3년간 지속적인 발전이 예상됨"
    )


class State(TypedDict):
    messages: Annotated[list, add_messages]
    next: str              # Supervisor가 고른 다음 차례
    research_result: str   # Researcher가 모은 정보
    draft: str             # Writer가 쓴 글
    review: str            # Reviewer의 판정("통과" 또는 "수정")과 의견
    revision_count: int    # Writer가 다시 쓴 횟수


# ✍️ 목표 1·2: researcher 노드(검색 도구를 가진 모델)와 researcher_tools 노드, writer 노드
researcher_llm = llm.bind_tools([search_web])
researcher_tool_node = ToolNode([search_web])


def researcher_node(state: State) -> dict:
    system = SystemMessage(content="너는 리서처야. search_web 도구로 주제를 조사하고, 찾은 정보를 정리해 줘.")
    return {"messages": [researcher_llm.invoke([system] + state["messages"])]}


def researcher_tools_node(state: State) -> dict:
    tool_result = researcher_tool_node.invoke(state)
    return {"messages": tool_result["messages"], "research_result": tool_result["messages"][-1].content}


def researcher_condition(state: State) -> Literal["researcher_tools", "supervisor"]:
    if state["messages"][-1].tool_calls:
        return "researcher_tools"
    return "supervisor"


def writer_node(state: State) -> dict:
    prompt = f"다음 리서치 결과로 짧은 글을 써 줘.\n\n[리서치 결과]\n{state['research_result']}"
    if state.get("review"):
        prompt += f"\n\n[기존 글]\n{state['draft']}\n\n[Reviewer 의견]\n{state['review']}\n의견을 반영해 다시 써 줘."
    response = llm.invoke([SystemMessage(content="너는 작가야."), HumanMessage(content=prompt)])
    count = state["revision_count"] + 1 if state.get("review") else state["revision_count"]
    return {
        "draft": response.content,
        "revision_count": count,
        "messages": [AIMessage(content=f"[Writer 완료 - 다시 쓴 횟수 {count}]\n{response.content}")],
    }


# ✍️ 목표 3: Supervisor가 구조화 출력으로 다음 차례(researcher / writer / FINISH)를 고르고 그 결정을 메시지로 남깁니다
class RouteDecision(BaseModel):
    next: Literal["researcher", "writer", "FINISH"]
    reason: str


supervisor_llm = llm.with_structured_output(RouteDecision)


def supervisor_node(state: State) -> dict:
    status = (
        "너는 팀의 Supervisor야. 다음 차례를 골라.\n"
        "- researcher: 아직 조사하지 않았을 때\n"
        "- writer: 조사는 끝났고 글이 아직 없을 때\n"
        "- FINISH: 글이 있고 Reviewer 판정이 끝났을 때\n"
        f"조사: {'완료' if state['research_result'] else '미완료'}, "
        f"글: {'있음' if state['draft'] else '없음'}, Reviewer 판정: {state['review'] or '없음'}"
    )
    decision = supervisor_llm.invoke([SystemMessage(content=status), *state["messages"][:1]])
    return {"next": decision.next, "messages": [AIMessage(content=f"[Supervisor → {decision.next}] {decision.reason}")]}


def supervisor_route(state: State) -> Literal["researcher", "writer", "__end__"]:
    return END if state["next"] == "FINISH" else state["next"]


# ✍️ 목표 4: reviewer 노드가 "통과/수정"을 내고, 수정이면 MAX_REVISIONS번까지만 writer로 돌려보냅니다
class Review(BaseModel):
    verdict: Literal["통과", "수정"]
    comment: str


reviewer_llm = llm.with_structured_output(Review)


def reviewer_node(state: State) -> dict:
    review = reviewer_llm.invoke([
        SystemMessage(content=f"너는 Reviewer야. 기준: {REVIEW_RULE} 기준을 지키면 통과, 아니면 수정과 고칠 점을 내."),
        HumanMessage(content=state["draft"]),
    ])
    return {
        "review": f"{review.verdict}: {review.comment}",
        "messages": [AIMessage(content=f"[Reviewer: {review.verdict}] {review.comment}")],
    }


def reviewer_route(state: State) -> Literal["writer", "supervisor"]:
    if state["review"].startswith("수정") and state["revision_count"] < MAX_REVISIONS:
        return "writer"
    return "supervisor"


builder = StateGraph(State)
builder.add_node("supervisor", supervisor_node)
builder.add_node("researcher", researcher_node)
builder.add_node("researcher_tools", researcher_tools_node)
builder.add_node("writer", writer_node)
builder.add_node("reviewer", reviewer_node)
builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", supervisor_route)
builder.add_conditional_edges("researcher", researcher_condition)
builder.add_edge("researcher_tools", "researcher")
builder.add_edge("writer", "reviewer")
builder.add_conditional_edges("reviewer", reviewer_route)
multi_agent_graph = builder.compile()


# ── 실행(그대로 둡니다): 노드마다 이름과 새 메시지를 보여 주고, 마지막에 흐름과 글을 출력합니다 ──
if multi_agent_graph is None:
    print("아직 그래프를 만들지 않았습니다. README.md의 할 일을 AI와 함께 작성합니다.")
else:
    flow, final = [], {}
    for chunk in multi_agent_graph.stream({
        "messages": [HumanMessage(content=TOPIC)],
        "next": "", "research_result": "", "draft": "", "review": "", "revision_count": 0,
    }, stream_mode="updates"):
        for node_name, update in chunk.items():
            flow.append(node_name)
            final.update(update or {})
            print(f"\n========= [{node_name}] =========")
            for m in (update or {}).get("messages", []):
                m.pretty_print()
    print("\n=== 흐름 ===")
    print(" → ".join(flow))
    print(f"\n=== 최종 글 (다시 쓴 횟수 {final.get('revision_count', 0)}) ===")
    print(final.get("draft", ""))
