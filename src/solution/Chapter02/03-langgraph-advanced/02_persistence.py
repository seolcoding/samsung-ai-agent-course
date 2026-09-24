import os
import sqlite3
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()

llm = get_llm()


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State) -> dict:
    system = SystemMessage(content='너는 친절한 AI 어시스턴트야.')
    return {'messages': [llm.invoke([system] + state['messages'])]}


builder = StateGraph(State)
builder.add_node('chatbot', chatbot)
builder.add_edge(START, 'chatbot')
builder.add_edge('chatbot', END)


# ── MemorySaver vs SqliteSaver ────────────────────────────────────────────────
#
# MemorySaver  : 프로세스 메모리에 저장 → 프로그램 재시작 시 기록 사라짐 (개발/데모용)
# SqliteSaver  : SQLite 파일에 저장   → 재시작해도 기록 유지 (로컬 프로토타입용)
# PostgresSaver: PostgreSQL에 저장    → 실제 서비스용 (langgraph-checkpoint-postgres 패키지)

print('=== 1. MemorySaver (휘발성) ===')
mem_app = builder.compile(checkpointer=MemorySaver())
# mem_app = builder.compile()
config = {'configurable': {'thread_id': 'demo'}}

mem_app.invoke({'messages': [HumanMessage(content='내 이름은 홍길동이야.')]}, config=config)
result = mem_app.invoke({'messages': [HumanMessage(content='내 이름이 뭐야?')]}, config=config)
print(result['messages'][-1].content)


print('\n=== 2. SqliteSaver (영속성) ===')
DB_PATH = os.path.join(os.path.dirname(__file__), 'checkpoints.db')

with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
    sqlite_app = builder.compile(checkpointer=SqliteSaver(conn))
    config_sql = {'configurable': {'thread_id': 'persistent_demo'}}

    sqlite_app.invoke({'messages': [HumanMessage(content='내 취미는 독서야.')]}, config=config_sql)
    result_sql = sqlite_app.invoke({'messages': [HumanMessage(content='내 취미가 뭐야?')]}, config=config_sql)
    print(result_sql['messages'][-1].content)

    # 저장된 체크포인트 목록 확인
    checkpoints = list(sqlite_app.get_state_history(config_sql))
    print(f'\n저장된 체크포인트 수: {len(checkpoints)}')
    for cp in checkpoints[:3]:
        print(f'  - {cp.config["configurable"]["checkpoint_id"][:8]}... | 메시지 수: {len(cp.values["messages"])}')

    # Time-Travel: 특정 체크포인트로 되돌아가 다른 흐름으로 재실행
    if len(checkpoints) >= 2:
        past_config = checkpoints[-1].config   # 가장 오래된 체크포인트
        print(f'\n=== Time-Travel: 과거 시점에서 다른 질문으로 재실행 ===')
        result_tt = sqlite_app.invoke(
            {'messages': [HumanMessage(content='독서 말고 다른 취미도 있어?')]},
            config=past_config,
        )
        print(result_tt['messages'][-1].content)
