from typing import Annotated

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()


# 02-langchain-basics/02_tool_calling.py 에서 만든 도구
# 거기서는 도구 실행 이후 다시 LLM을 호출하는 루프를 직접 구현해야 했다.
# LangGraph의 ToolNode + tools_condition이 그 반복 흐름을 처리한다.

@tool
def get_exchange_rate(base_currency: str, target_currency: str) -> float:
    """고정 환율을 반환한다. base_currency와 target_currency는 USD, KRW, EUR 중 하나."""
    rates = {
        ('USD', 'KRW'): 1350.0, ('KRW', 'USD'): 1 / 1350.0,
        ('EUR', 'KRW'): 1470.0, ('KRW', 'EUR'): 1 / 1470.0,
        ('USD', 'EUR'): 0.92,   ('EUR', 'USD'): 1.09,
    }
    if base_currency == target_currency:
        return 1.0
    return rates.get((base_currency, target_currency), -1.0)

@tool
def calculate(expression: str) -> float:
    """간단한 수식을 계산한다. 예: '1350 * 100'"""
    allowed = set('0123456789+-*/(). ')
    if not all(c in allowed for c in expression):
        raise ValueError('허용되지 않는 문자가 포함되어 있습니다.')
    return eval(expression)  # noqa: S307

# TODO: ToolNode와 LLM에 연결할 도구 목록을 작성해 주세요.
tools = [get_exchange_rate, calculate]
# TODO: bind_tools()로 LLM에 도구를 연결해 주세요.
llm = get_llm().bind_tools(tools)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent_node(state: State) -> dict:
    # TODO: State의 messages를 도구가 연결된 LLM에 전달해 주세요.
    return {'messages': [llm.invoke(state['messages'])]}


# ToolNode: AI 메시지에 포함된 tool_calls를 파싱하고 해당 도구를 실행한 뒤
#           결과를 ToolMessage 리스트로 반환한다.
# TODO: ToolNode를 생성해 주세요.
# ToolNode에게 기대하는 바는
    # 호출된 도구 (함수를) 실행해서 그 결과를 반환하기를 기대
        # ToolMessage로 반환하기를 기대한다.
    # State에 저장되는 messages에는
'''
    [
        ('human', ...),
        ('ai', ...),
        ('tool', ...),
    ]
'''
tool_node = ToolNode(tools)

# tools_condition: 마지막 메시지에 tool_calls가 있으면 'tools'로,
#                  없으면(최종 답변이면) END로 라우팅한다.
builder = StateGraph(State)
builder.add_node('agent', agent_node)
builder.add_node('tools', tool_node)
builder.add_edge(START, 'agent')
# reason -> tool -> observe -> finish? End or tool
builder.add_conditional_edges('agent', tools_condition)   # → 'tools' or END
# TODO: 도구 실행 후 다시 agent로 돌아가는 엣지를 추가해 주세요.
builder.add_edge('tools', 'agent')

app = builder.compile()

print('=== 직접 조립한 ReAct Agent ===')
result = app.invoke({'messages': [HumanMessage(content='100달러를 원화로 환산하면 얼마야?')]})
for msg in result['messages']:
    role = msg.__class__.__name__
    content = msg.content or str(getattr(msg, 'tool_calls', ''))
    print(f'  [{role}] {content}')

print()

# ── create_agent: 위와 동일한 ReAct 루프를 한 줄로 만드는 편의 함수 ────────────
# 커스텀 노드·엣지가 필요 없을 때 사용. 내부적으로 위와 같은 그래프를 자동 생성한다.
# 멀티에이전트처럼 여러 에이전트가 서로 통신하는 구조는 StateGraph 직접 조립이 필요하다.
print('=== create_agent ===')
agent = create_agent(get_llm(), tools)
result2 = agent.invoke({'messages': [HumanMessage(content='50유로는 몇 원이야?')]})
print(result2['messages'][-1].content)
print(result2)
