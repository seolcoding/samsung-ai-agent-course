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
    # Human, AI, System, Tool Message들이 쌓이는 것은 맞는데...
        # list 형태에 순차적으로 쌓여 나간다...
        # 그래서, 도구를 사용한 결과를 나중에서야 다시 써야 한다면?
            # 찾아와야하는 번거로움이 있을 수 있다.
    messages: Annotated[list, add_messages]
    research_result: str    # Researcher가 수집한 정보
    draft: str              # Writer가 작성한 초안


# ── Researcher Agent ──────────────────────────────────────────────────────────
# 역할: 주제를 조사해 research_result에 저장한다.

researcher_llm = llm.bind_tools([search_web])
researcher_tool_node = ToolNode([search_web])


def researcher_node(state: State) -> dict:
    # LLM의 역할 (페르소나) 정의
    system = SystemMessage(content=(
        '너는 전문 리서처야. '
        'search_web 도구를 사용해 주어진 주제를 철저히 조사하고, '
        '수집한 정보를 정리해서 제공해줘.'
    ))
    # TODO: Researcher LLM을 호출하고 응답 메시지를 반환해 주세요.
        # 파이썬에서는 [1, 2, 3] + [4, 5, 6] = [1, 2, 3, 4, 5, 6]
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

    # TODO: 마지막 메시지의 tool_calls 여부에 따라 researcher_tools 또는 writer를 반환해 주세요.
        # 상태의 마지막 메시지 -> 아마도 AI Message
            # 그 AI Message 객체가 가진 속성들 중, tool_calls가 있다?
            # 아, 도구를 호출하라는 메시지가 가장 최근이어싿.
    if hasattr(last, 'tool_calls') and last.tool_calls :
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
    # reseracher랑 같은 가우스모델을 사용하지만, 이번에는 도구가 없다.
        # 즉, llm이 메시지를 전달 받았을때, 어떤 정보가 포함되어 있든
        # 도구를 호출하려는 시도 (tool_calls)자체가 존재하지 않는다.
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

# TODO: START, 조건부 엣지, researcher_tools 반복, writer 종료 엣지를 연결해 주세요.
builder.add_edge(START, 'researcher')
    # 랭그래프가 직접 제공하는 tool_condition은 tool or END
builder.add_conditional_edges('researcher', researcher_condition)   # tools or writer
builder.add_edge('researcher_tools', 'researcher')
builder.add_edge('writer', END)

# TODO: 그래프를 컴파일해 주세요.
app = builder.compile()

# for chunk in app.stream({
#     'messages': [HumanMessage(content='AI Agent 기술의 현황과 전망을 조사해서 글로 써줘.')],
#     'research_result': '',
#     'draft': '',
# }):
#     if chunk.__class__.__name__:
#         print()
result = app.invoke({
    'messages': [HumanMessage(content='AI Agent 기술의 현황과 전망을 조사해서 글로 써줘.')],
    'research_result': '',
    'draft': '',
})

print('=== 최종 글 ===')
print(result['research_result'])
print(result['draft'])


'''
state: -> researcher_result: 도구를 통해 저장된 어떤 정보
                    START
                    |
                researcher agent
                (웹검색을 필수로 해야함 -> 도구 호출)
                / / (결과를 반환)
            tools               \
        (지정된 값 반환)            \
                                writer agent : state는 현재 Graph내에서 공유


'''