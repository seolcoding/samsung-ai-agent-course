"""4-2 과제: 기록과 점수가 남는 Agent

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
from langfuse import get_client  # noqa: E402

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
print("✍️ 목표 1은 아직 비어 있습니다. README.md의 할 일을 봅니다.")


print("\n=== 목표 2: @observe 중첩 기록 ===")
# ✍️ 목표 2: @observe를 붙인 함수 두 개(바깥 함수가 안쪽 함수와 chain을 부름)로 실행하고, 답과 trace ID를 출력합니다.
print("✍️ 목표 2는 아직 비어 있습니다.")


print("\n=== 목표 3: 점수 남기기 ===")
# ✍️ 목표 3: 목표 2의 trace에 규칙 점수 short-answer와 LLM 채점 점수 llm-judge를 create_score로 남기고 출력합니다.
print("✍️ 목표 3은 아직 비어 있습니다.")


print("\n=== 목표 4: 그래프 실행 기록 ===")
# ✍️ 목표 4: get_weather를 쓰는 그래프에 CallbackHandler를 붙여 실행하고, 메시지와 trace ID를 출력합니다.
print("✍️ 목표 4는 아직 비어 있습니다.")


# ✍️ 목표 3 (마지막): 모아 둔 기록과 점수를 Langfuse로 보냅니다.
