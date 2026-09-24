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
        ('USD', 'KRW'): 1540.0, ('KRW', 'USD'): 1 / 1540.0,
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


tools = [get_exchange_rate, calculate]
# llm이 자신이 가진 도구 목록을 토대로
    # 도구를 호출 할 것인지 말 것인지를 결정 할 것
    # 따라서, 도구 목록을 llm에게 쥐어주어야 한다.
        # 당연하게도... llm -> 흔히 말하는 ChatGPT, Gemini, Claude, Gauss가
        # 학습할때 도구를 뭘 호출해야할지를 배웠는가? -> 당연히 아니다.....
        # 그럼 어떻게 이 get_llm으로 얻어낸 llm이 bind_tools 라는 함수를 통해서
        # 도구 목록을 전달받고, 이걸 사용할 수 있느냐 -> langchain 프레임워크를 쓰는 이유죠.
llm = get_llm().bind_tools(tools)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent_node(state: State) -> dict:
    return {'messages': [llm.invoke(state['messages'])]}


# ToolNode: AI 메시지에 포함된 tool_calls를 파싱하고 해당 도구를 실행한 뒤
#           결과를 ToolMessage 리스트로 반환한다.
tool_node = ToolNode(tools)

# tools_condition: 마지막 메시지에 tool_calls가 있으면 'tools'로,
#                  없으면(최종 답변이면) END로 라우팅한다.
builder = StateGraph(State)
builder.add_node('agent', agent_node)
builder.add_node('tools', tool_node)
builder.add_edge(START, 'agent')
builder.add_conditional_edges('agent', tools_condition)   # → 'tools' or END
builder.add_edge('tools', 'agent')                        # 도구 실행 후 다시 agent → ReAct 루프

app = builder.compile()

print('=== 직접 조립한 ReAct Agent ===')
result = app.invoke({'messages': [HumanMessage(content='100달러를 원화로 환산하면 얼마야?')]})
for msg in result['messages']:
    from pprint import pprint
    pprint(msg)
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
