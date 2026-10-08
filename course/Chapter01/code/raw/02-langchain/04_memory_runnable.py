"""
메모리 전략 1 — LangChain 방식: RunnableWithMessageHistory

대화 기록을 체인 외부(InMemoryChatMessageHistory)에서 세션별로 관리.
체인 자체는 순수 함수처럼 동작하고, 히스토리는 wrapper가 주입한다.

실행:
  python 04_memory_runnable.py
"""

from dotenv import load_dotenv
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from config.llm import get_llm

load_dotenv()

llm = get_llm()


# ── 세션 저장소 ───────────────────────────────────────────────────────────────
# 실제 서비스에서는 Redis·DB로 교체 가능

session_store: dict[str, BaseChatMessageHistory] = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    # TODO: session_id별 InMemoryChatMessageHistory를 생성하고 반환해 주세요.
    # 아직 지정된 id 값으로 저장소가 만들어 지지 않았다면
    if session_id not in session_store:
        # 지금 대화한 맥락을 세션에 집어넣고
        session_store[session_id] = InMemoryChatMessageHistory()
    # 이미 있으면? 
        # 있던거 불러와서 반환 할거야
    return session_store[session_id]


# ── 체인 구성 ─────────────────────────────────────────────────────────────────
prompt = ChatPromptTemplate.from_messages([
    ('system', '너는 친절한 AI 어시스턴트야.'),
    MessagesPlaceholder(variable_name='history'),  # 이전 대화가 여기 삽입됨
    ('human', '{input}'),
])

'''
# 최초의 ChatPromptTemplate
('system', '너는 친절한 AI 어시스턴트야.'),
('human', '첫번째 질문'),
---

# 첫번째 Runnable invoke 결과 
('ai', '첫번째 응답'),

---
# 두번째 ChatPromptTemplate
('system', '너는 친절한 AI 어시스턴트야.'),
    ('human', '첫번째 질문'),
    ('ai', '첫번째 응답'),
('human', '두번째 질문'),
'''

chain = prompt | llm

# TODO: RunnableWithMessageHistory로 체인과 세션 히스토리를 연결해 주세요.
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key='input',
    history_messages_key='history'
)


# ── 세션 A ────────────────────────────────────────────────────────────────────
print('=== 세션 A: 홍길동 ===')
config_a = {'configurable': {'session_id': 'session_A'}}

r1 = chain_with_history.invoke({'input': '내 이름은 홍길동이야.'}, config=config_a)
print(f'AI: {r1.content}')

r2 = chain_with_history.invoke({'input': '내 이름이 뭐야?'}, config=config_a)
print(f'AI: {r2.content}')


# ── 세션 B ────────────────────────────────────────────────────────────────────
print('\n=== 세션 B: 별개 대화 ===')
config_b = {'configurable': {'session_id': 'session_B'}}

r3 = chain_with_history.invoke({'input': '내 이름이 뭐야?'}, config=config_b)
print(f'AI: {r3.content}')  # B는 A 대화를 모름


# ── 저장된 히스토리 확인 ──────────────────────────────────────────────────────
print('\n=== 세션 A 저장된 메시지 ===')
for msg in get_session_history('session_A').messages:
    role = '사람' if msg.type == 'human' else ' AI '
    print(f'[{role}] {msg.content}')


# ── LangChain 방식의 한계 ─────────────────────────────────────────────────────
print('''
[LangChain 방식 한계]
- 히스토리가 체인 외부에 있어 그래프와 통합이 어려움
- 도구 실행 결과가 메시지 흐름에 자동 포함되지 않음
- 복잡한 분기·반복 구조에서 히스토리 관리가 번거로움

→ LangGraph 방식(05_memory_langgraph.py)은 State 안에 messages를 두어 이 문제를 해결.
''')
