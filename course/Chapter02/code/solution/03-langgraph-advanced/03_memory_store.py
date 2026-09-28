import re
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.store.memory import InMemoryStore
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()

llm = get_llm()


# ── Checkpointer vs Store ─────────────────────────────────────────────────────
#
# Checkpointer (MemorySaver 등)
#   - thread(세션) 단위로 State를 저장
#   - 같은 thread 안에서 대화 흐름을 이어감 (단기 기억)
#
# Store (InMemoryStore 등)
#   - thread를 넘어 여러 세션에서 공유되는 장기 기억
#   - 사용자 프로필, 선호도, 중요 사실 등을 저장
#   - namespace (tuple)로 데이터를 논리적으로 분리한다

store = InMemoryStore()


class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str


def chatbot(state: State) -> dict:
    user_id = state.get('user_id', 'anonymous')

    # Store에서 이 사용자의 장기 기억 조회
    namespace = ('memories', user_id)
    memories = store.search(namespace)
    memory_text = '\n'.join(f'- {m.value["fact"]}' for m in memories) if memories else '없음'

    system_prompt = f"""너는 친절한 AI 어시스턴트야.

사용자에 대해 알고 있는 정보:
{memory_text}

대화 중 사용자의 중요한 정보(이름, 취미, 직업 등)가 나오면,
"[기억 저장: <내용>]" 형식으로 메시지 앞에 표시해줘."""

    response = llm.invoke([SystemMessage(content=system_prompt)] + state['messages'])

    # LLM이 기억할 내용을 표시했으면 Store에 저장
    content = response.content
    if '[기억 저장:' in content:
        facts = re.findall(r'\[기억 저장: (.+?)\]', content)
        for i, fact in enumerate(facts):
            key = f'fact_{len(memories) + i}'
            store.put(namespace, key, {'fact': fact})

    return {'messages': [response]}


builder = StateGraph(State)
builder.add_node('chatbot', chatbot)
builder.add_edge(START, 'chatbot')
builder.add_edge('chatbot', END)

app = builder.compile(checkpointer=MemorySaver(), store=store)


def chat(user_id: str, thread_id: str, message: str) -> str:
    config = {'configurable': {'thread_id': thread_id}}
    result = app.invoke(
        {'messages': [HumanMessage(content=message)], 'user_id': user_id},
        config=config,
    )
    return result['messages'][-1].content


print('=== 세션 1: 정보 입력 ===')
print(chat('user_001', 'session_1', '안녕! 나는 이지수야. 취미는 피아노 연주야.'))

print('\n=== 세션 2: 새 세션에서도 기억 유지 ===')
print(chat('user_001', 'session_2', '내 이름이랑 취미 알아?'))

print('\n=== Store에 저장된 장기 기억 ===')
memories = store.search(('memories', 'user_001'))
for m in memories:
    print(f'  [{m.key}] {m.value["fact"]}')
