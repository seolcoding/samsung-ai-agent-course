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


# ── Supervisor가 내리는 라우팅 결정 스키마 ─────────────────────────────────────

class RouteDecision(BaseModel):
    next: Literal['researcher', 'writer', 'FINISH']
    reason: str


supervisor_llm = llm.with_structured_output(RouteDecision)


# ── 공유 State ────────────────────────────────────────────────────────────────

class State(TypedDict):
    messages: Annotated[list, add_messages]
    next: str               # Supervisor가 결정한 다음 에이전트
    research_result: str
    draft: str


# ── Supervisor ────────────────────────────────────────────────────────────────
# 사용자의 요청과 현재 진행 상황을 보고 어떤 에이전트를 호출할지 결정한다.

# 아래와 같이 프롬프트를 통해서 제어하는것은 한계가 있었다.
    # 그래서 -> Pydantic 등으로 명확히 출력 결과를 제어 하는 과정을 진행했
SUPERVISOR_PROMPT = """너는 멀티 에이전트 시스템의 Supervisor야.
다음 에이전트 중 하나를 선택해 작업을 지시하거나 완료를 선언해줘.

- researcher: 웹 검색으로 정보를 수집해야 할 때
- writer: 수집된 정보를 바탕으로 글을 작성해야 할 때
- FINISH: 모든 작업이 완료됐을 때

현재 상황:
- 리서치 완료 여부: {research_done}
- 초안 작성 여부: {draft_done}
"""


def supervisor_node(state: State) -> dict:
    prompt = SUPERVISOR_PROMPT.format(
        research_done='완료' if state.get('research_result') else '미완료',
        draft_done='완료' if state.get('draft') else '미완료',
    )
    decision = supervisor_llm.invoke([
        SystemMessage(content=prompt),
        *state['messages'],
    ])
    return {'next': decision.next, 'messages': [
        AIMessage(content=f'[Supervisor → {decision.next}] {decision.reason}')
    ]}


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
    result = llm.invoke([
        system,
        HumanMessage(content=f'다음 리서치 결과로 글을 써줘:\n\n{state["research_result"]}'),
    ])
    return {
        'draft': result.content,
        'messages': [AIMessage(content=f'[Writer 완료]\n{result.content}')],
    }


# ── 라우팅 함수 ───────────────────────────────────────────────────────────────

def route(state: State) -> Literal['researcher', 'writer', '__end__']:
    return state['next'] if state['next'] != 'FINISH' else END


# ── 그래프 조립 ───────────────────────────────────────────────────────────────

builder = StateGraph(State)
builder.add_node('supervisor', supervisor_node)
builder.add_node('researcher', researcher_node)
builder.add_node('writer', writer_node)

builder.add_edge(START, 'supervisor')
        # add_conditional_edges(시작노드, 끝노드) -> add_edge랑 똑같은데,
        # 두번째 인자인 끝노드 -> 라우팅 함수 호출 결과에 따라 달라질 것.
builder.add_conditional_edges('supervisor', route)
builder.add_edge('researcher', 'supervisor')    # 완료 후 Supervisor에게 보고
builder.add_edge('writer', 'supervisor')        # 완료 후 Supervisor에게 보고

app = builder.compile()


result = app.invoke({
    'messages': [HumanMessage(content='LangGraph Multi-Agent 시스템에 대한 블로그 포스트를 써줘.')],
    'next': '',
    'research_result': '',
    'draft': '',
})

print('=== Supervisor 의사결정 흐름 ===')
for msg in result['messages']:
    if '[Supervisor' in msg.content or '[Researcher' in msg.content or '[Writer' in msg.content:
        print(f'  {msg.content[:100]}...' if len(msg.content) > 100 else f'  {msg.content}')

print('\n=== 최종 초안 ===')
print(result['draft'])
