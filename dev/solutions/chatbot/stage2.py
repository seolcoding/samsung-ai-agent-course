"""챗봇 2단계(1-3): 기억하고 도구 쓰는 챗봇

실행(저장소 맨 위에서): uv run --env-file .env streamlit run course/Chapter01/chatbot/stage2.py
"""
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from config.llm import get_llm
from ui import log_step, run_chat

load_dotenv()

llm = get_llm()

# 사이드바: 답 방식과 말투 고르기
mode = st.sidebar.selectbox("답 방식", ["대화", "계산기 도구", "정리 카드"])
style = st.sidebar.selectbox("답 말투", ["친절하게", "한 문장으로", "초등학생에게 설명하듯"])


# ── 답 방식 "대화" ────────────────────────────────────────────────────────────
# ✍️ 목표 2: 이 prompt의 system과 human 사이에 MessagesPlaceholder("history")를 넣습니다
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 친절한 AI 도우미야. 답은 {style} 해 줘."),
    MessagesPlaceholder("history"),
    ("human", "{question}"),
])

# ✍️ 목표 1: prompt | llm | StrOutputParser()로 LCEL 체인을 만듭니다
chain = prompt | llm | StrOutputParser()


def chat_answer(question, history):
    # ✍️ 목표 1·2: chain.stream()에 style·history·question을 넣어 글자 조각을 내보냅니다
    inputs = {"style": style, "history": history, "question": question}
    log_step("모델에 보낸 메시지", [(m.type, m.content) for m in prompt.invoke(inputs).to_messages()])
    count = 0
    for text in chain.stream(inputs):
        count += 1
        yield text
    log_step("받은 조각 수", count)


# ── 답 방식 "계산기 도구" ─────────────────────────────────────────────────────
# ✍️ 목표 3: @tool 계산기를 만들고 bind_tools로 llm에 연결합니다
@tool
def calculate(expression: str) -> str:
    """수식을 계산한다. 예: '1234 * 5678'"""
    return str(eval(expression, {"__builtins__": {}}))  # noqa: S307


tools = [calculate]
tool_map = {t.name: t for t in tools}
llm_with_tools = llm.bind_tools(tools)


def tool_answer(question):
    # ✍️ 목표 3: tool_calls가 있으면 도구를 실행해 ToolMessage로 돌려주고, 최종 답을 돌려줍니다
    messages = [HumanMessage(content=question)]
    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)
        if not response.tool_calls:
            return response.content
        for call in response.tool_calls:
            result = tool_map[call["name"]].invoke(call["args"])
            log_step("도구 실행", f"{call['name']}({call['args']}) → {result}")
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))


# ── 답 방식 "정리 카드" ───────────────────────────────────────────────────────
# ✍️ 목표 4: Pydantic 스키마(제목·한 줄 요약·핵심 3가지)와 PydanticOutputParser로 카드 체인을 만듭니다
class Card(BaseModel):
    title: str = Field(description="제목")
    summary: str = Field(description="한 줄 요약")
    points: list[str] = Field(description="핵심 3가지")


parser = PydanticOutputParser(pydantic_object=Card)
card_prompt = ChatPromptTemplate.from_messages([
    ("system", "질문에 대한 답을 정리 카드로 만들어. {format_instructions}"),
    ("human", "{question}"),
]).partial(format_instructions=parser.get_format_instructions())
card_chain = card_prompt | llm | parser


def card_answer(question):
    # ✍️ 목표 4: 카드를 받아 log_step으로 남기고, 제목·요약·핵심을 마크다운 글로 바꿔 돌려줍니다
    card = card_chain.invoke({"question": question})
    log_step("받은 카드", card)
    lines = [f"### {card.title}", card.summary] + [f"- {point}" for point in card.points]
    return "\n".join(lines)


def answer(question, history):
    if mode == "계산기 도구":
        return tool_answer(question)
    if mode == "정리 카드":
        return card_answer(question)
    return chat_answer(question, history)


run_chat(answer, "나의 챗봇 - 2단계")
