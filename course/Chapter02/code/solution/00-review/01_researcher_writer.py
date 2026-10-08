from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()

llm = get_llm()


# ── 도구 ──────────────────────────────────────────────────────────────────────

@tool
def search_web(query: str) -> str:
    """웹에서 주제를 조사한다."""
    # 실제 구현에서는 Tavily, SerpAPI 등을 사용한다.
    return (
        f'["{query}" 검색 결과]\n'
        f'- 해당 주제의 주요 동향: 최근 급격한 성장세를 보이고 있음\n'
        f'- 핵심 기술 요소: 트랜스포머 아키텍처, 대규모 데이터 학습\n'
        f'- 주요 플레이어: OpenAI, Anthropic, Google DeepMind\n'
        f'- 미래 전망: 향후 3년간 지속적인 발전이 예상됨'
    )


# ── 상태 ──────────────────────────────────────────────────────────────────────

class State(TypedDict):
    messages: Annotated[list, add_messages]
    research_result: str    # Researcher가 수집한 정보
    draft: str              # Writer가 작성한 초안


# ── Researcher Agent ──────────────────────────────────────────────────────────
# 역할: 주제를 조사해 research_result에 저장한다.

researcher_llm = llm.bind_tools([search_web])
researcher_tool_node = ToolNode([search_web])


def researcher_node(state: State) -> dict:
    system = SystemMessage(content=(
        '너는 전문 리서처야. '
        'search_web 도구를 사용해 주어진 주제를 철저히 조사하고, '
        '수집한 정보를 정리해서 제공해줘.'
    ))
    response = researcher_llm.invoke([system] + state['messages'])
    return {'messages': [response]}


def researcher_tools_node(state: State) -> dict:
    # ToolNode 실행 후 research_result에 도구 결과를 저장
    tool_result = researcher_tool_node.invoke(state)
    last_tool_msg = tool_result['messages'][-1]
    return {
        'messages': tool_result['messages'],
        'research_result': last_tool_msg.content,
    }


def researcher_condition(state: State):
    """Researcher가 도구 호출을 완료하면 writer로 넘어간다."""
    last = state['messages'][-1]
    if hasattr(last, 'tool_calls') and last.tool_calls:
        return 'researcher_tools'
    return 'writer'


# ── Writer Agent ──────────────────────────────────────────────────────────────
# 역할: Researcher의 조사 결과를 바탕으로 완성된 글을 작성한다.

def writer_node(state: State) -> dict:
    system = SystemMessage(content=(
        '너는 전문 작가야. '
        '제공된 리서치 결과를 바탕으로 독자가 이해하기 쉬운 글을 작성해줘. '
        '서론, 본론, 결론 구조를 갖춰줘.'
    ))
    context = f'[리서치 결과]\n{state.get("research_result", "")}'
    response = llm.invoke([
        system,
        HumanMessage(content=context),
        *state['messages'],
    ])
    return {'messages': [response], 'draft': response.content}


# ── 그래프 조립 ───────────────────────────────────────────────────────────────

builder = StateGraph(State)
builder.add_node('researcher', researcher_node)
builder.add_node('researcher_tools', researcher_tools_node)
builder.add_node('writer', writer_node)

builder.add_edge(START, 'researcher')
builder.add_conditional_edges('researcher', researcher_condition)
builder.add_edge('researcher_tools', 'researcher')
builder.add_edge('writer', END)

app = builder.compile()


result = app.invoke({
    'messages': [HumanMessage(content='AI Agent 기술의 현황과 전망을 조사해서 글로 써줘.')],
    'research_result': '',
    'draft': '',
})

print('=== 최종 글 ===')
print(result['draft'])
