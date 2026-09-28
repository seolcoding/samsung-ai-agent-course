from typing import Annotated, Literal

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()

llm = get_llm()


# ── Supervisor 가 내리는 라우팅 결정 스키마 ─────────────────────────────────────

class RouteDecision(BaseModel):
    next: Literal['researcher', 'writer', 'critic', 'FINISH']
    reason: str

supervisor_llm = llm.with_structured_output(RouteDecision)


# ── Critic 이 분석하는 치명적 오류 스키마 ──────────────────────────────────────

class CriticFeedback(BaseModel):
    has_fatal_error: bool
    error_type: str  # 'factual_error', 'logical_error', 'missing_key_point', 'none'
    description: str
    suggestion: str


critic_llm = llm.with_structured_output(CriticFeedback)


# ── 공유 State ────────────────────────────────────────────────────────────────

class State(TypedDict):
    messages: Annotated[list, add_messages]
    next: str                       # Supervisor 가 결정한 다음 에이전트
    research_result: str
    draft: str
    critic_feedback: str            # Critic 의 개선점 피드백
    revision_count: int             # 수정 횟수 (무한 루프 방지)


# ── Supervisor ────────────────────────────────────────────────────────────────
# 사용자의 요청과 현재 진행 상황을 보고 어떤 에이전트를 호출할지 결정한다.

SUPERVISOR_PROMPT = """너는 멀티 에이전트 시스템의 Supervisor 야.
다음 에이전트 중 하나를 선택해 작업을 지시하거나 완료를 선언해줘.

- researcher: 웹 검색으로 정보를 수집해야 할 때
- writer: 수집된 정보를 바탕으로 글을 작성해야 할 때
- critic: 작성된 초안의 치명적 오류를 분석해야 할 때
- FINISH: 모든 작업이 완료됐을 때

현재 상황:
- 리서치 완료 여부: {research_done}
- 초안 작성 여부: {draft_done}
- Critic 피드백 존재: {critic_done}
- 현재 수정 횟수: {revision_count}

주의:
- Critic 이 치명적 오류를 찾았다면 writer 를 호출해서 수정하게 해줘.
- 수정 횟수가 4 회를 넘었다면 FINISH 를 선택해줘.
"""


def supervisor_node(state: State) -> dict:
    prompt = SUPERVISOR_PROMPT.format(
        research_done='완료' if state.get('research_result') else '미완료',
        draft_done='완료' if state.get('draft') else '미완료',
        critic_done='있음' if state.get('critic_feedback') else '없음',
        revision_count=state.get('revision_count', 0),
    )
    decision = supervisor_llm.invoke([
        SystemMessage(content=prompt),
        *state['messages'],
    ])
    return {
        'next': decision.next,
        'messages': [
            AIMessage(content=f'[Supervisor → {decision.next}] {decision.reason}')
        ]
    }


# ── Researcher ────────────────────────────────────────────────────────────────

def researcher_node(state: State) -> dict:
    system = SystemMessage(content='너는 리서처야. 주제를 조사해서 핵심 정보를 정리해줘.')
    topic = state['messages'][0].content   # 사용자의 원래 요청
    result = llm.invoke([
        system,
        HumanMessage(content=f'다음 주제를 조사해줘: {topic}\n(실제 검색 대신 알고 있는 내용으로 답해줘.)'),
    ])
    return {
        'research_result': result.content,
        'messages': [AIMessage(content=f'[Researcher 완료]\n{result.content}')],
    }


# ── Writer ────────────────────────────────────────────────────────────────────

def writer_node(state: State) -> dict:
    system = SystemMessage(content='너는 작가야. 리서치 결과를 바탕으로 완성도 높은 글을 써줘.')
    
    # Critic 피드백이 있다면 이를 반영하여 수정
    if state.get('critic_feedback'):
        prompt = f"""
        다음 리서치 결과로 글을 수정해줘.

        [기존 초안]
        {state['draft']}

        [Critic 피드백 - 치명적 오류]
        {state['critic_feedback']}

        위 피드백을 반영하여 치명적 오류를 수정한 새로운 버전을 작성해줘.
        """
    else:
        prompt = f'다음 리서치 결과로 글을 써줘:\n\n{state["research_result"]}. 단 의도적으로 치명적인 오류를 섞어 넣어줘'
    
    result = llm.invoke([
        system,
        HumanMessage(content=prompt),
    ])
    return {
        'draft': result.content,
        'critic_feedback': '',
        'revision_count': state.get('revision_count', 0) + 1,
        'messages': [AIMessage(content=f'[Writer 완료 - 수정 {state.get("revision_count", 0) + 1}번째]\n{result.content}')],
    }


# ── Critic ────────────────────────────────────────────────────────────────────

CRITIC_PROMPT = """너는 치명적 오류만 분석하는 Critic 이야.
다음 기준에서 **치명적 오류**만 찾아내:
1. 사실적 오류 (Fact-checking 실패)
2. 논리적 모순 (앞뒤 내용이 맞지 않음)
3. 핵심 요구사항 누락 (사용자 요청을 충족하지 못함)

사소한 문체, 오타, 스타일 문제는 무시해.
치명적 오류가 없다면 has_fatal_error=False 로 응답해.
"""


def critic_node(state: State) -> dict:
    feedback = critic_llm.invoke([
        SystemMessage(content=CRITIC_PROMPT),
        HumanMessage(content=f'다음 초안을 분석해줘:\n\n{state["draft"]}'),
    ])
    
    if feedback.has_fatal_error:
        critic_msg = f"[치명적 오류 발견: {feedback.error_type}]\n{feedback.description}\n\n[개선 제안]\n{feedback.suggestion}"
    else:
        critic_msg = "[치명적 오류 없음]\n초안이 양호합니다."
    
    return {
        'critic_feedback': critic_msg if feedback.has_fatal_error else '',
        'messages': [AIMessage(content=f'[Critic 완료]\n{critic_msg}')],
    }


# ── 라우팅 함수 ───────────────────────────────────────────────────────────────

def route(state: State) -> Literal['researcher', 'writer', 'critic', '__end__']:
    return state['next'] if state['next'] != 'FINISH' else END


# ── 그래프 조립 ───────────────────────────────────────────────────────────────

builder = StateGraph(State)
builder.add_node('supervisor', supervisor_node)
builder.add_node('researcher', researcher_node)
builder.add_node('writer', writer_node)
builder.add_node('critic', critic_node)
builder.add_edge(START, 'supervisor')
builder.add_conditional_edges('supervisor', route)

# 각 노드 완료 후 Supervisor 에게 보고
builder.add_edge('researcher', 'supervisor')
builder.add_edge('writer', 'supervisor')
builder.add_edge('critic', 'supervisor')
app = builder.compile()


# ── stream 형식으로 실행 (각 노드별 실시간 진행 확인) ─────────────────────────

print('=== Agent 실행 시작 ===')

for chunk in app.stream({
    'messages': [HumanMessage(content='LangGraph Multi-Agent 시스템에 대한 블로그 포스트를 써줘.')],
    'next': '',
    'research_result': '',
    'draft': '',
    'critic_feedback': '',
    'revision_count': 0,
}):
    for node_name in chunk.keys():
        print(f'========= [{node_name}] =========')
        message_type = chunk[node_name]['messages'][0].__class__.__name__
        if message_type == 'AIMessage':
            print('AIMessage')
        elif message_type == 'ToolMessage':
            print('ToolMessage')
        print(chunk[node_name]['messages'][0].content[:100])

