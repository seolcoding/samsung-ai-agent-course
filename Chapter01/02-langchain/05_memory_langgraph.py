"""
메모리 전략 2 — LangGraph 방식: State에 messages 내장

대화 기록이 State의 일부 → MemorySaver가 스레드별로 영속화.
외부 히스토리 관리 불필요. 도구 결과도 자동으로 메시지 흐름에 포함.

실행:
  python 05_memory_langgraph.py
"""

from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()

llm = get_llm()


# ── State 정의 ────────────────────────────────────────────────────────────────
# add_messages reducer: 기존 메시지 리스트에 새 메시지를 누적(append) 한다.
# 덮어쓰기 방지 → 대화 히스토리가 자동으로 쌓인다.

class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State) -> dict:
    system = SystemMessage(content='너는 친절한 AI 어시스턴트야.')
    # TODO: system 메시지와 State의 messages를 함께 LLM에 전달하고 결과를 반환해 주세요.
    return {'messages': []}


# ── 그래프 빌드 ───────────────────────────────────────────────────────────────
builder = StateGraph(State)
# TODO: chatbot 노드와 START/END 엣지를 추가해 주세요.

# MemorySaver: 스레드별 State를 메모리에 유지 (프로세스 재시작 시 초기화)
# TODO: MemorySaver를 생성하고 그래프를 컴파일해 주세요.
checkpointer = None
app = None


# ── 스레드 A: 홍길동 ───────────────────────────────────────────────────────────
print('=== 스레드 A ===')
config_a = {'configurable': {'thread_id': 'thread_A'}}

app.invoke({'messages': [HumanMessage(content='내 이름은 홍길동이야.')]}, config=config_a)
result = app.invoke({'messages': [HumanMessage(content='내 이름이 뭐야?')]}, config=config_a)
print(result['messages'][-1].content)


# ── 스레드 B: 별개 세션 ───────────────────────────────────────────────────────
print('\n=== 스레드 B (A와 독립) ===')
config_b = {'configurable': {'thread_id': 'thread_B'}}

result_b = app.invoke({'messages': [HumanMessage(content='내 이름이 뭐야?')]}, config=config_b)
print(result_b['messages'][-1].content)  # B는 A 대화를 모름


# ── 스냅샷 확인 ───────────────────────────────────────────────────────────────
print('\n=== 스레드 A 현재 State 스냅샷 ===')
snapshot = app.get_state(config_a)
for msg in snapshot.values['messages']:
    role = '사람' if msg.type == 'human' else ' AI '
    print(f'[{role}] {msg.content}')

print(f'\n다음 실행 노드: {snapshot.next}')  # () = 완료 상태


# ── LangGraph vs LangChain 방식 비교 ─────────────────────────────────────────
print('''
┌──────────────────┬─────────────────────────────┬───────────────────────────────┐
│                  │ LangChain (RunnableWithHist) │ LangGraph (MemorySaver)       │
├──────────────────┼─────────────────────────────┼───────────────────────────────┤
│ 히스토리 위치    │ 체인 외부 (session_store)    │ State 내부 (messages 필드)    │
│ 도구 결과 통합   │ 수동 처리 필요               │ 자동 (ToolMessage로 축적)     │
│ 분기/반복        │ 구현 복잡                    │ 그래프 구조로 자연스럽게 표현 │
│ 영속성           │ 별도 저장소 연결 필요        │ checkpointer 교체만으로 전환  │
│ 권장 시나리오    │ 단순 Q&A 챗봇                │ Agent, 복잡한 대화 흐름       │
└──────────────────┴─────────────────────────────┴───────────────────────────────┘
''')
