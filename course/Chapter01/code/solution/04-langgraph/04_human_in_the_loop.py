from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
# 사람의 개입으로 에이전트의 호출과 동작이 pending 되었다가
# 다시 동작 한다 -> 이전에 어디까지 작업했는지를 `기억` 할 수 잇어야 한다.
    # 즉, 상태 (state말고, memory)를 가지고 있어야 이어서 진행할 수 있겠다.
from langgraph.checkpoint.memory import MemorySaver
    # 메모리를 관리하는 방법이, MemorySaver가 등장하기 전에는 (LangChain만 사용)
        # SQliteSaver -> 물리적으로 파일 DB 만들어서 정리하기.
        # 근데 간단은 하지만.. 결국 DB가...... 
    # MySQL Postgre,... 
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()

llm = get_llm()


@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """이메일을 전송한다."""
    print(f'\n  [실제 전송] {recipient} / 제목: {subject}')
    return f'이메일이 {recipient}에게 성공적으로 전송되었습니다.'


tools = [send_email]
llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent_node(state: State) -> dict:
    return {'messages': [llm_with_tools.invoke(state['messages'])]}


builder = StateGraph(State)
builder.add_node('agent', agent_node)
builder.add_node('tools', tool_node)
builder.add_edge(START, 'agent')
builder.add_conditional_edges('agent', tools_condition)
builder.add_edge('tools', 'agent')

checkpointer = MemorySaver()

# interrupt_before: 지정한 노드 실행 직전에 그래프를 일시 중단한다.
    # 일시 중단할 시점 (노드의 이름 -> 문자열)
# 사용자가 도구 호출 내용을 확인하고 승인/거부할 수 있다.
app = builder.compile(checkpointer=checkpointer, interrupt_before=['tools'])

config = {'configurable': {'thread_id': 'hitl_demo'}}


# ── 1단계: tools 노드 직전까지 실행 ──────────────────────────────────────────
print('=== 1단계: 에이전트 실행 (tools 직전에서 중단) ===')
app.invoke(
    {'messages': [
        HumanMessage(
            content='kim@example.com에게 "오늘 회의 취소" 제목으로 "오후 3시 회의가 취소되었습니다"라는 이메일을 보내줘.')
            ]
    },
    config=config,
)

state = app.get_state(config)
pending_tools = state.values['messages'][-1].tool_calls
print(f'\n대기 중인 도구 호출:')
for tc in pending_tools:
    print(f'  - {tc["name"]}({tc["args"]})')


# # ── 2단계: 사용자 승인 후 재개 ────────────────────────────────────────────────
print('\n=== 2단계: 승인 후 재개 ===')
# None을 입력하면 마지막으로 중단된 지점부터 그래프가 이어서 실행된다.
result = app.invoke(None, config=config)
print(result['messages'][-1].content)


# # ── 거부 시나리오 ─────────────────────────────────────────────────────────────
print('\n=== 거부 시나리오 ===')
config2 = {'configurable': {'thread_id': 'hitl_reject'}}
app.invoke(
    {'messages': [HumanMessage(content='boss@example.com에게 "긴급" 제목으로 "즉시 연락 바랍니다"라는 이메일을 보내줘.')]},
    config=config2,
)

# # 거부: tool_calls를 직접 ToolMessage로 처리해 상태에 삽입한 뒤 재개
state2 = app.get_state(config2)
rejected_calls = state2.values['messages'][-1].tool_calls

rejection_messages = [
    ToolMessage(content='사용자가 이메일 전송을 취소했습니다.', tool_call_id=tc['id'])
    for tc in rejected_calls
]
app.update_state(config2, {'messages': rejection_messages}, as_node='tools')

result2 = app.invoke(None, config=config2)
print(result2['messages'][-1].content)
