"""
@observe 데코레이터: LangChain 밖의 코드도 트레이싱하기

핵심 개념:
  - CallbackHandler는 LangChain 체인 내부만 추적한다.
  - @observe 데코레이터는 일반 Python 함수도 span으로 기록할 수 있다.
  - RAG의 검색 단계, 전처리 함수, 비즈니스 로직 등을 함께 추적할 때 유용하다.
  - 중첩 함수에 각각 @observe를 붙이면 부모-자식 트리 구조로 기록됨

실행:
  python course/Chapter02/code/solution/05-observability/03_observe_decorator.py
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langfuse import get_client, observe
from langfuse.langchain import CallbackHandler

from config.llm import get_llm

load_dotenv()

langfuse = get_client()
langfuse_handler = CallbackHandler()
llm = get_llm()


# @observe(): 이 함수의 호출이 Langfuse에 span으로 기록됨
# name 파라미터로 대시보드에 표시될 이름을 지정할 수 있음
@observe(name='retrieve-documents')
def retrieve(query: str) -> list[str]:
    # 실제로는 벡터스토어에서 검색하는 부분
    # 여기서는 시뮬레이션용 더미 데이터 반환
    return [
        f'[문서1] {query}에 관한 첫 번째 참고 자료입니다.',
        f'[문서2] {query}와 관련된 두 번째 참고 자료입니다.',
    ]


@observe(name='format-context')
def format_context(docs: list[str]) -> str:
    return '\n'.join(docs)


# @observe로 감싼 함수 안에서 LangChain 체인을 호출하면
# 체인 실행이 이 span의 자식으로 자동 연결됨
@observe(name='rag-pipeline')
def rag_pipeline(question: str) -> str:
    docs = retrieve(question)
    context = format_context(docs)

    prompt = ChatPromptTemplate.from_messages([
        ('system', '아래 컨텍스트를 바탕으로 질문에 답하세요.\n\n{context}'),
        ('human', '{question}'),
    ])
    chain = prompt | llm | StrOutputParser()

    # CallbackHandler를 여기서도 전달해야 LLM 호출이 같은 트레이스에 묶임
    return chain.invoke(
        {'context': context, 'question': question},
        config={'callbacks': [langfuse_handler]},
    )


print('=== @observe 데코레이터 트레이싱 ===')
questions = ['LangGraph란 무엇인가요?', 'RAG의 장점은?']
for q in questions:
    answer = rag_pipeline(q)
    print(f'Q: {q}')
    print(f'A: {answer}')
    print()

langfuse.flush()
print('✓ 대시보드에서 retrieve → format → LLM 호출 트리를 확인하세요.')
print('Tracing에서 확인')
