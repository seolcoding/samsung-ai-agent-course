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
    '''
        이 노드가 하는 일은 원본 text (사용자의 입력 문서내용)을 요약하는것
        text에는 원본 데이터가 들어있고

        이 llm이 요약한 정보는 요약본이라는 상태에 별도로 저장
        summary -> 요약본 저장
        summary_subgraph -> 이 생태계에는 공유 가능한 상태 2가지
    '''
    result = llm.invoke(f'다음 텍스트를 한 문장으로 요약해줘:\n\n{state["text"]}')
    return {'summary': result.content}


def translate_node(state: SummaryState) -> dict:
    # '''
    #     지금은, 상태에 저장된 summary를 요약해 달라고 했다.
    #     근데 우리는 요약본 말고 원본을 영어로 번역해야 하는 상황이 있을 수도 있곘죠?

    #     summary_subgraph를 확장 한다 라고 한다면

    #         START -> supervisor node
    #                 (사용자가 요약해 달라고 했는가?)
    #                     y/n
    #                 /          \
    #             summarize       translate  (text 원본 기반 번역)
    #                 |              |
    #             translate   
    #                     \        /
    #                         END
    # '''
    result = llm.invoke(f'다음 문장을 영어로 번역해줘:\n\n{state["summary"]}')
    return {'summary': result.content}


summary_builder = StateGraph(SummaryState)
summary_builder.add_node('summarize', summarize_node)
summary_builder.add_node('translate', translate_node)
summary_builder.add_edge(START, 'summarize')
summary_builder.add_edge('summarize', 'translate')
summary_builder.add_edge('translate', END)

# 서브그래프를 독립적으로 컴파일
summary_subgraph = summary_builder.compile()


# result = summary_subgraph.invoke({'text': [HumanMessage(content='인공지능은 인간의 지능을 모방하는 컴퓨터 시스템으로, 최근 LLM의 등장으로 급격히 발전했습니다. 이제 AI는 텍스트 생성, 번역, 코딩 등 다양한 작업을 수행할 수 있습니다.')], 'summary': ''})
# print(result)

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
    result = summary_subgraph.invoke({'text': state['document'], 'summary': ''})
    return {'summary': result['summary']}


def respond_node(state: ParentState) -> dict:
    response = llm.invoke(
        f'문서 요약(영문): {state["summary"]}\n\n이를 바탕으로 사용자 질문에 답해줘: {state["messages"][-1].content}'
    )
    return {'messages': [response]}


parent_builder = StateGraph(ParentState)
parent_builder.add_node('fetch_document', fetch_document)
parent_builder.add_node('summarize_document', summarize_document)   # 서브그래프 노드
parent_builder.add_node('respond', respond_node)

parent_builder.add_edge(START, 'fetch_document')
parent_builder.add_edge('fetch_document', 'summarize_document')
parent_builder.add_edge('summarize_document', 'respond')
parent_builder.add_edge('respond', END)

app = parent_builder.compile()


result = app.invoke({
    'messages': [HumanMessage(content='문서의 핵심 내용이 뭐야?')],
    'document': '',
    'summary': '',
})

print(f'영문 요약: {result["summary"]}')
print(f'최종 답변: {result["messages"][-1].content}')
