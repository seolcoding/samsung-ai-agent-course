from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()

llm = get_llm()


# ── LangGraph 3대 요소 ──────────────────────────────────────────────────────

# 1. State: 그래프 전체에서 공유되는 데이터 구조.
#    TypedDict 또는 Pydantic BaseModel로 정의한다.
#    add_messages Reducer 덕분에 messages는 덮어쓰기가 아닌 누적(append)이다.

# 이 State에 정의된 값에 저장되는 요소들은
    # 모든 노드 (LLM, tool, 다른 agent 등..)
    # 공통으로 전달받아서 사용할 수 있는 정보를 정의
class State(TypedDict):
    # Human, System, AI, TOOL 메시지 등..
    # 이 그래프가 동작하면서 발생하는 모든 메시지들
    # 을 내가 상황에 따라서 추가해 나가면서 처리
        # 이를 통해서.. 
        # A Agent가 B Agent를 호출하게 되어도
            # 전체 대화 맥락을 같이 공유할 수 있게 될 것이다.
    # 이걸 고도화 하면 CoT 방식을 내부에 직접 구현
    messages: Annotated[list, add_messages]


# 2. Node: State를 받아 State의 일부(dict)를 반환하는 함수.
#    반환된 dict는 Reducer 규칙에 따라 기존 State에 병합된다.
def chatbot_node(state: State) -> dict:
    '''
        챗봇 노드에게 기대하는 바는
        사용자가 입력했거나... 현재
        상태에 있는 메시지를 하나 전달해서
        답변을 생성하도록 하는 것
    '''
    # TODO: State의 messages를 LLM에 전달하고 응답을 messages에 담아 반환해 주세요.
    # 필요 하다면? 여기에서 prompt, llm, ouput 
    # 그러니까.. LCEL을 직접 정의해서 처리
    response = llm.invoke(state['messages'])
    return {'messages': [response]}


# 3. Edge: 노드 간 흐름을 정의한다.
#    START/END는 LangGraph가 제공하는 진입·종료 지점이다.
builder = StateGraph(State)
# TODO: chatbot 노드를 추가하고 START에서 chatbot, chatbot에서 END로 이어 주세요.
    # 내가 정의한 노드를 하나 추가 -> add_node
        # 첫 번쨰인자: 노드의 이름 
        # 두 번째인자: 그 노드가 하는 일
builder.add_node('chatbot', chatbot_node)
    # 간선을 추가한다. 간선의 역할은? 두 노드를 잇는 역할
    # from -> to
builder.add_edge(START, 'chatbot')  # 입력값을 내 챗봇에게 전달
builder.add_edge('chatbot', END)    # 챗봇이 생성한 결과를 출력
# TODO: 그래프를 컴파일해 실행 가능한 app을 만들어 주세요.
app = builder.compile()


# 그래프 구조 출력 (Mermaid 다이어그램)
print(app.get_graph().draw_mermaid())
print()

result = app.invoke({'messages': [HumanMessage(content='LangGraph가 뭔지 두 문장으로 설명해줘.')]})
print(result['messages'][-1].content)
