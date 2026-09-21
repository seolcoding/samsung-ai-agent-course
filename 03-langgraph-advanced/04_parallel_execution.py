from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Send
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()

llm = get_llm()


# ── 패턴 1: 정적 병렬 (Fan-out → Fan-in) ────────────────────────────────────
# 고정된 수의 노드를 병렬로 실행할 때 사용한다.
# 각 분기가 State에 결과를 append하고, 이후 하나의 노드가 합쳐서 처리한다.

class StaticState(TypedDict):
    topic: str
    pros: str
    cons: str
    final: str


def pros_node(state: StaticState) -> dict:
    result = llm.invoke(f'{state["topic"]}의 장점 3가지를 간결하게 나열해줘.')
    return {'pros': result.content}


def cons_node(state: StaticState) -> dict:
    result = llm.invoke(f'{state["topic"]}의 단점 3가지를 간결하게 나열해줘.')
    return {'cons': result.content}


def summary_node(state: StaticState) -> dict:
    print(state['cons'], state['pros'])
    result = llm.invoke(
        f'장점:\n{state["pros"]}\n\n단점:\n{state["cons"]}\n\n위 내용을 바탕으로 한 문장 결론을 내려줘.'
    )
    return {'final': result.content}


static_builder = StateGraph(StaticState)
static_builder.add_node('pros', pros_node)
static_builder.add_node('cons', cons_node)
static_builder.add_node('summary', summary_node)

# TODO: START에서 pros/cons를 병렬로 실행하고 summary에서 합쳐 END로 이어 주세요.
static_builder.add_edge(START, 'pros')
static_builder.add_edge(START, 'cons')  # pros, cons 동시 시작
# 만약, 평소와 같이 summary 노드로 진입하는 간선이 1개만 있다면,
    # 당연하게도, 그 1개의 시작지점 노드 (pros)의 결과가 나오는 순간
    # 바로 summary노드가 작업을 시작 하겠지만
static_builder.add_edge('pros', 'summary') 
static_builder.add_edge('cons', 'summary')  # summary 노드로 진입하는 노드가 2개라면
                                            # 두 작업자의 작업이 모두 끝나야 summary가 실행
static_builder.add_edge('summary', END)
# TODO: 정적 병렬 그래프를 컴파일해 주세요.
static_app = static_builder.compile()

print('=== 정적 병렬 (Fan-out → Fan-in) ===')
result = static_app.invoke({'topic': 'Remote Work', 'pros': '', 'cons': '', 'final': ''})
print(f'장점: {result["pros"][:80]}...')
print(f'단점: {result["cons"][:80]}...')
print(f'결론: {result["final"]}')
print()


# ── 패턴 2: 동적 병렬 (Send API) ────────────────────────────────────────────
# 실행 시점에 작업 수가 결정될 때 사용한다.
# Send(노드명, state)를 리스트로 반환하면 LangGraph가 해당 노드를 병렬로 실행한다.

class DynamicState(TypedDict):
    queries: list[str]
    results: Annotated[list[str], lambda a, b: a + b]   # 결과를 누적


class WorkerState(TypedDict):
    query: str
    results: Annotated[list[str], lambda a, b: a + b]


def worker_node(state: WorkerState) -> dict:
    """각 쿼리를 독립적으로 처리하는 워커 노드."""
    result = llm.invoke(f'"{state["query"]}"에 대해 한 문장으로 답해줘.')
    return {'results': [f'[{state["query"]}] {result.content}']}


def fan_out(state: DynamicState) -> list[Send]:
    """쿼리 수만큼 worker_node를 병렬로 생성해 보낸다."""
    # TODO: queries 수만큼 Send('worker', ...) 목록을 만들어 주세요.
    # temp = []
    # for q in state['queries']:
        # temp.apppend(Send('worker', {'query': q, 'results': []}))
        # Send('worker', {'query': q, 'results': []})
    # python list comprehension
    # numbers = [num * 2 for num in [1, 2, 3, 4, 5]]
    return [
        Send('worker', {'query': q, 'results': []})
        for q in state['queries']
    ]


dynamic_builder = StateGraph(DynamicState)
dynamic_builder.add_node('worker', worker_node)
# 기존의 간선 형성 방식
# dynamic_builder.add_edge(START, 'worker')
# TODO: START에서 fan_out으로 worker를 동적 생성하고 worker 이후 END로 연결해 주세요.
dynamic_builder.add_conditional_edges(START, fan_out, ['worker'])
dynamic_builder.add_edge('worker', END)
# TODO: 동적 병렬 그래프를 컴파일해 주세요.
dynamic_app = dynamic_builder.compile()

print('=== 동적 병렬 (Send API) ===')
# 그래프를 설계하는 시점에서 애초에 질문을 리스트 형식으로 받을거야.
# 그래서, 동시에 여러개의 질문에 답변할 수 있도록 처리할거야.
queries = ['LangGraph란?', 'RAG란?', 'MCP란?']
result2 = dynamic_app.invoke({'queries': queries, 'results': []})
for r in result2['results']:
    print(f'  {r}')
