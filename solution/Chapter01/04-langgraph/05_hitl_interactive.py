from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
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


@tool
def search_web(query: str) -> str:
    """웹을 검색한다."""
    return f'"{query}" 검색 결과: (검색 결과 예시 데이터)'


tools = [send_email, search_web]
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

app = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before=['tools'],
)


def print_tool_calls(tool_calls: list[dict]) -> None:
    print('\n실행 대기 중인 도구 호출')
    for index, tool_call in enumerate(tool_calls, start=1):
        print(f'{index}. {tool_call["name"]}')
        for key, value in tool_call['args'].items():
            print(f'   - {key}: {value}')


def reject_tool_calls(config: dict, tool_calls: list[dict], reason: str) -> None:
    rejection_messages = [
        ToolMessage(
            content=f'사용자가 도구 실행을 거부했습니다. 사유: {reason}',
            tool_call_id=tool_call['id'],
        )
        for tool_call in tool_calls
    ]
    app.update_state(config, {'messages': rejection_messages}, as_node='tools')


def ask_human_decision() -> tuple[str, str]:
    print('\n도구를 실행할까요?')
    print('- y: 승인 후 실행')
    print('- n: 거부 후 에이전트에게 취소 사유 전달')
    print('- q: 프로그램 종료')

    decision = input('선택(y/n/q): ').strip().lower()
    if decision == 'n':
        reason = input('거부 사유를 입력하세요: ').strip()
        return decision, reason
    return decision, ''


def run_agent(user_input: str, thread_id: str = 'hitl_demo') -> None:
    config = {'configurable': {'thread_id': thread_id}}
    result = app.invoke({'messages': [HumanMessage(content=user_input)]}, config=config)

    while True:
        state = app.get_state(config)
        tool_calls = state.values['messages'][-1].tool_calls

        if not tool_calls:
            print('\n에이전트 응답')
            print(result['messages'][-1].content)
            break

        print_tool_calls(tool_calls)
        decision, reason = ask_human_decision()

        if decision == 'y':
            result = app.invoke(None, config=config)
        elif decision == 'n':
            reject_tool_calls(config, tool_calls, reason or '사유 없음')
            result = app.invoke(None, config=config)
        elif decision == 'q':
            print('프로그램을 종료합니다.')
            break
        else:
            print('y, n, q 중 하나를 입력하세요.')


if __name__ == '__main__':
    request = input('에이전트에게 요청할 내용을 입력하세요: ')
    run_agent(request)
