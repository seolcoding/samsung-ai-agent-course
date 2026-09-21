"""
LangGraph 트레이싱: StateGraph 실행 흐름 전체 기록하기

핵심 개념:
  - LangGraph 그래프는 여러 노드·엣지로 구성되는데, 트레이싱하면
    어느 노드에서 얼마나 걸렸는지 단계별로 확인 가능
  - with_config()로 그래프 자체에 CallbackHandler를 붙이면
    invoke() 호출마다 자동으로 추적됨

실행:
  python 11-observability/02_tracing_langgraph.py
"""

from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """도시의 현재 날씨를 반환한다."""
    data = {'서울': '맑음 23°C', '부산': '흐림 19°C', '제주': '비 17°C'}
    return data.get(city, f'{city}의 날씨 정보 없음')


tools = [get_weather]
llm = get_llm().bind_tools(tools)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent_node(state: State) -> dict:
    return {'messages': [llm.invoke(state['messages'])]}


builder = StateGraph(State)
builder.add_node('agent', agent_node)
builder.add_node('tools', ToolNode(tools))
builder.add_edge(START, 'agent')
builder.add_conditional_edges('agent', tools_condition)
builder.add_edge('tools', 'agent')

# with_config(): 그래프 인스턴스에 기본 config를 고정
# 이후 모든 invoke() / stream() 호출에 CallbackHandler가 자동 적용됨
langfuse_handler = CallbackHandler()
# TODO: 그래프를 컴파일 하면서, with_config 메서드를 통해 callback으로 `langfuse_handler`를 전달하세요.
app = builder.compile().with_config({'callbacks': [langfuse_handler]})

print('=== LangGraph 트레이싱 ===')
inputs = [
    '서울 날씨 알려줘',
    '부산이랑 제주 날씨 비교해줘',
]
for question in inputs:
    result = app.invoke({'messages': [HumanMessage(content=question)]})
    print(f'Q: {question}')
    print(f'A: {result["messages"][-1].content}')
    print()

langfuse = get_client()
langfuse.flush()
print('Tracing에서 확인')
