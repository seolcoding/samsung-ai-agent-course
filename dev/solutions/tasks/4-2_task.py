"""4-2 과제: 기록과 점수가 남는 질문 답변기"""

import truststore
from dotenv import load_dotenv
from langfuse import get_client

from config.llm import get_llm

truststore.inject_into_ssl()  # PC에 등록된 인증서(회사 인증서 포함)로 Langfuse에 연결합니다
load_dotenv()

langfuse = get_client()
llm = get_llm()


# 아래에 AI와 함께 코드를 작성합니다
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langfuse import observe
from langfuse.langchain import CallbackHandler

# 질문에 3문장 이내로 답하는 체인
prompt = ChatPromptTemplate.from_messages([
    ("system", "한국어로 3문장 이내로 답하세요."),
    ("human", "{question}"),
])
chain = prompt | llm | StrOutputParser()

# LLM 채점용 체인: 숫자 하나만 답하게 합니다
judge_prompt = ChatPromptTemplate.from_messages([
    ("system", "아래 답변이 질문에 직접 답했는지 0.0~1.0 사이 숫자 하나만 출력하세요. 다른 글은 쓰지 마세요."),
    ("human", "질문: {question}\n답변: {answer}"),
])
judge_chain = judge_prompt | llm | StrOutputParser()

# 기록 도구는 함수 밖에서 한 번 만듭니다
handler = CallbackHandler()


@observe(name="qa-task")
def answer_question(question: str) -> str:
    return chain.invoke({"question": question}, config={"callbacks": [handler]})


for question in ["Langfuse의 Trace가 뭐야?", "RAG를 한 문장으로 설명해줘"]:
    print(f"\nQ: {question}")
    answer = answer_question(question)
    trace_id = handler.last_trace_id
    print(f"A: {answer}")
    print(f"trace id: {trace_id}")

    # 규칙 점수: 200자 이하면 1.0
    short_score = 1.0 if len(answer) <= 200 else 0.0
    langfuse.create_score(trace_id=trace_id, name="short-answer", value=short_score,
                          comment=f"답 길이 {len(answer)}자")
    print(f"short-answer: {short_score} (답 길이 {len(answer)}자)")

    # LLM 채점 점수
    judge_text = judge_chain.invoke({"question": question, "answer": answer})
    try:
        judge_score = float(judge_text.strip())
    except ValueError:
        judge_score = 0.0
    langfuse.create_score(trace_id=trace_id, name="llm-judge", value=judge_score,
                          comment=f"LLM 채점: {judge_text}")
    print(f"llm-judge: {judge_score}")

langfuse.flush()
print("\nLangfuse Tracing에서 qa-task trace를 확인하세요.")
