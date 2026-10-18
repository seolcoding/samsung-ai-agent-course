"""4-2 과제: 기록과 점수가 남는 Agent (강사용 정답)

실행(저장소 맨 위에서):
    uv run --env-file .env python course/Chapter02/tasks/4-2/4-2_task.py

할 일과 프롬프트 힌트는 같은 폴더의 README.md에 있습니다.
"""

import truststore

truststore.inject_into_ssl()  # 파이썬이 PC에 등록된 인증서(회사 인증서 포함)를 믿게 합니다. Langfuse보다 먼저 둡니다

from dotenv import load_dotenv  # noqa: E402
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from langchain_core.tools import tool  # noqa: E402
from typing import Annotated  # noqa: E402

from langchain_core.messages import HumanMessage  # noqa: E402
from langfuse import get_client, observe  # noqa: E402
from langfuse.langchain import CallbackHandler  # noqa: E402
from langgraph.graph import START, StateGraph  # noqa: E402
from langgraph.graph.message import add_messages  # noqa: E402
from langgraph.prebuilt import ToolNode, tools_condition  # noqa: E402
from typing_extensions import TypedDict  # noqa: E402

from config.llm import get_llm  # noqa: E402

load_dotenv()

langfuse = get_client()
llm = get_llm()

# 질문에 3문장 이내로 답하는 체인(목표 1~3에서 씁니다)
prompt = ChatPromptTemplate.from_messages([
    ("system", "한국어로 3문장 이내로 답하세요."),
    ("human", "{question}"),
])
chain = prompt | llm | StrOutputParser()


# 날씨 도구(목표 4의 그래프에서 씁니다)
@tool
def get_weather(city: str) -> str:
    """도시의 현재 날씨를 반환한다."""
    data = {"서울": "맑음 23°C", "부산": "흐림 19°C", "제주": "비 17°C"}
    return data.get(city, f"{city}의 날씨 정보 없음")


print("=== 목표 1: 체인 실행 기록 ===")
# ✍️ 목표 1: CallbackHandler를 config로 넘겨 chain을 실행하고, 답과 trace ID를 출력합니다.
handler = CallbackHandler()
answer1 = chain.invoke({"question": "Langfuse의 Trace가 뭐야?"}, config={"callbacks": [handler]})
print(f"A: {answer1}")
print(f"trace id: {handler.last_trace_id}")


print("\n=== 목표 2: @observe 중첩 기록 ===")
# ✍️ 목표 2: @observe를 붙인 함수 두 개(바깥 함수가 안쪽 함수와 chain을 부름)로 실행하고, 답과 trace ID를 출력합니다.
@observe(name="find-docs")
def find_docs(question: str) -> str:
    return f"[참고] {question}에 관한 참고 자료입니다."


@observe(name="qa-pipeline")
def qa_pipeline(question: str) -> str:
    context = find_docs(question)
    return chain.invoke({"question": f"{context}\n질문: {question}"}, config={"callbacks": [handler]})


question2 = "RAG를 한 문장으로 설명해줘"
answer2 = qa_pipeline(question2)
trace_id2 = handler.last_trace_id
print(f"A: {answer2}")
print(f"trace id: {trace_id2}")


print("\n=== 목표 3: 점수 남기기 ===")
# ✍️ 목표 3: 목표 2의 trace에 규칙 점수 short-answer와 LLM 채점 점수 llm-judge를 create_score로 남기고 출력합니다.
short_score = 1.0 if len(answer2) <= 200 else 0.0
langfuse.create_score(trace_id=trace_id2, name="short-answer", value=short_score)
print(f"short-answer: {short_score} (답 길이 {len(answer2)}자)")

judge_prompt = ChatPromptTemplate.from_messages([
    ("system", "아래 답변이 질문에 직접 답했는지 0.0~1.0 사이 숫자 하나만 출력하세요."),
    ("human", "질문: {question}\n답변: {answer}"),
])
judge_chain = judge_prompt | llm | StrOutputParser()
judge_text = judge_chain.invoke({"question": question2, "answer": answer2})
try:
    judge_score = max(0.0, min(1.0, float(judge_text.strip())))
except ValueError:
    judge_score = 0.0
langfuse.create_score(trace_id=trace_id2, name="llm-judge", value=judge_score)
print(f"llm-judge: {judge_score}")


print("\n=== 목표 4: 그래프 실행 기록 ===")
# ✍️ 목표 4: get_weather를 쓰는 그래프에 CallbackHandler를 붙여 실행하고, 메시지와 trace ID를 출력합니다.
class State(TypedDict):
    messages: Annotated[list, add_messages]


tools = [get_weather]
llm_with_tools = llm.bind_tools(tools)


def agent_node(state: State) -> dict:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


builder = StateGraph(State)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")
weather_graph = builder.compile().with_config({"callbacks": [handler]})

weather_graph_result = weather_graph.invoke({"messages": [HumanMessage(content="서울 날씨 알려줘")]})
results = weather_graph_result["messages"]
for m in results:
    m.pretty_print()
print(f"trace id: {handler.last_trace_id}")


# ✍️ 목표 3 (마지막): 모아 둔 기록과 점수를 Langfuse로 보냅니다.
langfuse.flush()
