"""
LangChain 트레이싱: Langfuse로 LLM 호출 흐름 기록하기

핵심 개념:
  - 트레이싱 = LLM 호출의 입력·출력·레이턴시·토큰 수를 자동 기록
  - CallbackHandler를 체인에 붙이면 별도 코드 수정 없이 모든 단계가 추적됨
  - cloud.langfuse.com 대시보드에서 실시간 확인 가능

사전 준비:
  1. cloud.langfuse.com 에서 프로젝트 생성 후 API 키 발급
  2. .env 파일에 아래 세 줄 추가:
       LANGFUSE_PUBLIC_KEY=pk-lf-...
       LANGFUSE_SECRET_KEY=sk-lf-...
       LANGFUSE_HOST=https://cloud.langfuse.com

실행:
  python solution/Chapter02/05-observability/01_tracing_basic.py
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langfuse import get_client
from langfuse.langchain import CallbackHandler

from config.llm import get_llm

load_dotenv()

# CallbackHandler: .env의 LANGFUSE_* 환경변수를 자동으로 읽어 인증
# 이 핸들러를 chain.invoke()에 전달하면 모든 단계가 Langfuse에 자동 기록됨
langfuse_handler = CallbackHandler()

llm = get_llm()
prompt = ChatPromptTemplate.from_messages([
    ('system', '한국어로 간결하게 답변하세요.'),
    ('human', '{question}'),
])
chain = prompt | llm | StrOutputParser()

print('=== 단일 질문 트레이싱 ===')
# config={"callbacks": [...]} — LangChain이 실행 중 각 단계마다 핸들러를 호출함
# TODO: chain.invoke를 호출하면서, config의 callback으로 `langfuse_handler`를 전달하세요.
result = chain.invoke(
    {'question': 'LangGraph와 LangChain의 차이를 한 줄로 설명해줘'},
    config={'callbacks': [langfuse_handler]},
)
print(result)
print()

print('=== 여러 질문 배치 트레이싱 ===')
questions = [
    {'question': 'RAG가 뭔가요?'},
    {'question': 'Vector DB는 왜 쓰나요?'},
]
# 각 invoke마다 별도의 trace로 기록됨
for q in questions:
    # TODO: chain.invoke를 호출하면서, config의 callback으로 `langfuse_handler`를 전달하세요.
    answer = chain.invoke(q, config={'callbacks': [langfuse_handler]})
    print(f"Q: {q['question']}")
    print(f"A: {answer}")
    print()

# flush: 비동기로 큐에 쌓인 이벤트를 Langfuse 서버로 전송 완료 후 종료
# 스크립트 종료 직전에 호출하지 않으면 일부 데이터가 누락될 수 있음
langfuse = get_client()
langfuse.flush()
print('Tracing에서 확인')
