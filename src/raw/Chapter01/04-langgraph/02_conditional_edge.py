from typing import Annotated, Literal

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()

llm = get_llm()


class State(TypedDict):
    messages: Annotated[list, add_messages]
    language: str   # 감지된 언어 ('ko' | 'en')


# ── 노드 정의 ────────────────────────────────────────────────────────────────

def detect_language(state: State) -> dict:
    """마지막 메시지의 언어를 감지해 State에 기록한다."""
    # AIMessage, HumanMessage 
    # 단순히 글자만 띡 있는게 아니라.. 다양한 정보들
    last = state['messages'][-1].content
    # TODO: LLM으로 언어를 감지하고 'ko' 또는 'en' 값을 정해 주세요.
    result = llm.invoke(f'다음 텍스트의 언어를 "ko" 또는 "en" 중 하나로만 판별해: {last}')
    lang = 'ko' if 'ko' in result.content.lower() else 'en'
    return {'language': lang}


def korean_response(state: State) -> dict:
    response = llm.invoke([
        ('system', '반드시 한국어로만 답변하세요.'),
        *state['messages'],
    ])
    return {'messages': [response]}


def english_response(state: State) -> dict:
    response = llm.invoke([
        ('system', 'Respond only in English.'),
        *state['messages'],
    ])
    return {'messages': [response]}


# ── 라우팅 함수 ──────────────────────────────────────────────────────────────
# add_conditional_edges의 두 번째 인자로 전달되는 함수.
# State를 받아 다음에 실행할 노드 이름(또는 END)을 반환한다.
def route_by_language(state: State) -> Literal['korean_response', 'english_response']:
    # 반한값은 조건 분기하고 싶은 노드의 이름
    return 'korean_response' if state.get('language') == 'ko' else 'english_response'


# ── 그래프 조립 ──────────────────────────────────────────────────────────────
builder = StateGraph(State)
builder.add_node('detect_language', detect_language)
builder.add_node('korean_response', korean_response)
builder.add_node('english_response', english_response)

builder.add_edge(START, 'detect_language')

# 조건부 엣지: detect_language 노드 이후 route_by_language 결과에 따라 분기
# TODO: detect_language 이후 조건부 엣지를 추가해 주세요.
    # from -> to
        # 이번에는 언제 어디로 가야할지 도착 노드가 정해지지 않았음.
        # A면 a노드로, B면 b노드로 이동 할 것이다.
            # 그럼 to를 뭘로 결정하느냐? 함수 실행 결과로 결정
builder.add_conditional_edges('detect_language', route_by_language)

# 병렬처리
# builder.add_edge('detect_language', 'korean_response')
# builder.add_edge('detect_language', 'english_response')
builder.add_edge('korean_response', END)
builder.add_edge('english_response', END)

app = builder.compile()


# ── 실행 ─────────────────────────────────────────────────────────────────────
for question in [
    '안녕하세요! LangGraph에 대해 알려주세요.',
    'Hello! Tell me about LangGraph.',
]:
    result = app.invoke({'messages': [HumanMessage(content=question)], 'language': ''})
    print(f'Q: {question}')
    print(f'A: {result["messages"][-1].content}')
    print(f'감지 언어: {result["language"]}')
    print()
