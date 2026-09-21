import re
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
    # 사용자 입력
    messages: Annotated[list, add_messages]
    # 감지된 언어 ('ko' | 'en')
    language: str   


# ── 노드 정의 ────────────────────────────────────────────────────────────────

def detect_language(state: State) -> dict:
    """마지막 메시지의 언어를 감지해 State에 기록한다."""
    last = state['messages'][-1].content
    result = llm.invoke(f"다음 텍스트의 언어를 'ko' 또는 'en' 중 하나로만 답해: {last}")
    # 확률적으로 답변을 하다보니... 가끔 대문자로 답하더라 -> 소문자로 변환
    lang = 'ko' if 'ko' in result.content.lower() else 'en'
    # 오로지, 상태중, language에 대한 부분만 답변하도록 처리
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
# 상태로 부터 어떤 정보를 얻을것 -> language 값
    # 메세지 말고 -> LLM 호출 안할 거니까 (조건 분기를 위한 것)
def route_by_language(state: State) -> Literal['korean_response', 'english_response']:
    # 반환 할 문자열 -> 다음 노드의 이름 (edge에 적을 대상 노드는 문자열 형태의 이름만 쓰면되니까)
    return 'korean_response' if state.get('language') == 'ko' else 'english_response'


# ── 그래프 조립 ──────────────────────────────────────────────────────────────
builder = StateGraph(State)
builder.add_node('detect_language', detect_language)
builder.add_node('korean_response', korean_response)
builder.add_node('english_response', english_response)

builder.add_edge(START, 'detect_language')  # ko or en만 반환하는 노드 호출

# 조건부 엣지: detect_language 노드 이후 route_by_language 결과에 따라 분기
    # detect_ 노드를 통해서 얻은 정보 ko/en 으로 조건 분기 
    # 함수의 반환값 -> korean_response or english_response
    # 동작 방식 자체는 그냥 add_edge랑 똑같다. 
builder.add_conditional_edges('detect_language', route_by_language)

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
