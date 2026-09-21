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
        '너는 전문 리서처인데, 검색이 필요하면 . '
        'search_web 도구를 사용해 주어진 주제를 철저히 조사하고, '
        '수집한 정보를 정리해서 제공해줘.'
        # '그래서, 검색이 끝낫으면 이번에는 작가가 되어서 그걸로 디테일한 보고서를 작성해줘.'
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

'''
    별거 아닌 업무였는데도 답변이 돌아오는 시간은 평소보다 훨씬 길다.
    이유는?
    1. agent에게 판단을 맡긴 주체가 추상적이다.
        -> 사용자 질문에 대해서 웹 검색 결과가 충분한가? -> finish를 작성
            -> 충분의 기점은?
            -> 충분의 기점을 명확히 하기 -> 프롬프트 엔지니어링
    2. 오.. 그럼 `통과 기준`을 프롬프트로 넣는다고 가정 해 봅시다.
    3. 근데, 에이전트가 해야하는 일이 2가지
        1. 웹서치
        2. 웹서치 결과물로 답변 생성하기
        -> `통과 기준` -> 웹서치를 통해서 얻어낸 결과물의 통과 기준을 시스템 지시사항으로 넣는다.
        -> 그럼... 웹서치 결과물로 `작성한 답변`의 통과 기준?
    4. 그러면 작성자 에이전트만 별도로 떼서 관리
    5. 즉, 웹서치 도구 호출 -> 웹 서치 에이전트가 어떤 질문에 대한 조사를 진행
    6. 작성 에이전트는 별도로 떼서 관리

        그럼 생기는 문제는?
        두 에이전트 간의 연결 고리는 어디감?

    7. 그러면 writer agent 안만들고 그냥 researcher agent로 프롬프트로만 나눠서 작업 하면 안됨?
        -> 프롬프트 엔지니어링만 복잡해지고
        -> 그 프롬프트 지시사항을 잘 따라주기를 기도하기.
'''