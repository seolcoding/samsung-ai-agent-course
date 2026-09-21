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

# messages는 랭체인에서 사용했었던 각종 메시지들 (human, ai, system 등) 그 메세지를 의미하는 것
# 상태 -> 더 많은 정보들 
#       (세션 ID, 유저 ID, 인덱스 정보, 메타데이터 등등.. 노드를 나타낼 수 있는 모든것)
class State(TypedDict):
    messages: Annotated[list, add_messages]


# 2. Node: State를 받아 State의 일부(dict)를 반환하는 함수.
#    반환된 dict는 Reducer 규칙에 따라 기존 State에 병합된다.
def chatbot_node(state: State) -> dict:
    '''
        chatbot에게 기대하는 바 -> 사용자 질문에 대한 LLM의 응답
        message에 대한 정보를 반환 하기를 기대
    '''
    # 지금은 실습상 가우스 모델만 사용 하고 있으니
    # 챗봇 노드가 사용하는 llm은 가우스 모델 하나지만?
    # 상황에 따라서는 다양한 모델들을 적절히 사용할 수 도 있겠다. 
        # 내가 사용할 수 있는 모델이 GPT-5-mini, gemma, sonnet-4.2
        # model_gpt, model_gemma, model_claude <- 이런식으로 여러개의 Client 만들어서 관리
    response = llm.invoke(state['messages'])
    return {'messages': [response]}


# 3. Edge: 노드 간 흐름을 정의한다.
#    START/END는 LangGraph가 제공하는 진입·종료 지점이다.
builder = StateGraph(State)
builder.add_node('chatbot', chatbot_node)
builder.add_edge(START, 'chatbot')
builder.add_edge('chatbot', END)

app = builder.compile()


# 그래프 구조 출력 (Mermaid 다이어그램)
print(app.get_graph().draw_mermaid())
print()

result = app.invoke(
    {'messages': 
     [
        HumanMessage(content='내 이름은 홍길동이야.')
    ]
    })
print(result['messages'][-1].content)
# result = app.invoke({'messages': [HumanMessage(content='내 이름이 뭐라고?')]})
# print(result['messages'][-1].content)
