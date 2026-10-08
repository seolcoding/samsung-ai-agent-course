from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()

llm = get_llm()


# ── 서브그래프 ────────────────────────────────────────────────────────────────
# 서브그래프는 독립적으로 컴파일된 그래프로, 부모 그래프의 노드로 사용된다.
# 복잡한 워크플로우를 재사용 가능한 단위로 분리할 때 활용한다.

class SummaryState(TypedDict):
    """서브그래프 전용 State. 부모 State와 독립적이다."""
    text: str
    summary: str


def summarize_node(state: SummaryState) -> dict:
    result = llm.invoke(f'다음 텍스트를 한 문장으로 요약해줘:\n\n{state["text"]}')
    return {'summary': result.content}


def translate_node(state: SummaryState) -> dict:
    result = llm.invoke(f'다음 문장을 영어로 번역해줘:\n\n{state["summary"]}')
    return {'summary': result.content}


summary_builder = StateGraph(SummaryState)
# TODO: summarize, translate 노드와 START/END 엣지를 연결해 주세요.
summary_builder.add_node('summarize', summarize_node)
summary_builder.add_node('translate', translate_node)
summary_builder.add_edge(START, 'summarize')
summary_builder.add_edge('summarize', 'translate')
summary_builder.add_edge('translate', END)
# 서브그래프를 독립적으로 컴파일
# TODO: 서브그래프를 컴파일해 주세요.
summary_subgraph = summary_builder.compile()


# ── 부모 그래프 ───────────────────────────────────────────────────────────────

class ParentState(TypedDict):
    messages: Annotated[list, add_messages]
    document: str
    summary: str


def fetch_document(state: ParentState) -> dict:
    # 실제로는 DB나 파일에서 문서를 가져온다.
    doc = '인공지능은 인간의 지능을 모방하는 컴퓨터 시스템으로, 최근 LLM의 등장으로 급격히 발전했습니다. 이제 AI는 텍스트 생성, 번역, 코딩 등 다양한 작업을 수행할 수 있습니다.'
    return {'document': doc}


def summarize_document(state: ParentState) -> dict:
    # 서브그래프를 노드처럼 호출
    # TODO: summary_subgraph를 호출해 document를 요약/번역해 주세요.
    # 그래프 호출시에 필요한 인자 정보 -> 해당 그래프의 STATE 정보를 따라간다ㅓ.
    response = summary_subgraph.invoke({
        'text': state['document'],
        'summary': ''
    })
    return {'summary': response['summary']}


def respond_node(state: ParentState) -> dict:
    response = llm.invoke(
        f'문서 요약(영문): {state["summary"]}\n\n이를 바탕으로 사용자 질문에 답해줘: {state["messages"][-1].content}'
    )
    return {'messages': [response]}


parent_builder = StateGraph(ParentState)
parent_builder.add_node('fetch_document', fetch_document)
parent_builder.add_node('summarize_document', summarize_document)   # 서브그래프 노드
parent_builder.add_node('respond', respond_node)

# TODO: 부모 그래프의 실행 순서를 START → fetch_document → summarize_document → respond → END로 연결해 주세요.
parent_builder.add_edge(START, 'fetch_document')
parent_builder.add_edge('fetch_document', 'summarize_document')
parent_builder.add_edge('summarize_document', 'respond')
parent_builder.add_edge('respond', END)

# TODO: 부모 그래프를 컴파일해 주세요.
app = parent_builder.compile()


result = app.invoke({
    'messages': [HumanMessage(content='문서의 핵심 내용이 뭐야?')],
    'document': '',
    'summary': '',
})

print(f'영문 요약: {result["summary"]}')
print(f'최종 답변: {result["messages"][-1].content}')
