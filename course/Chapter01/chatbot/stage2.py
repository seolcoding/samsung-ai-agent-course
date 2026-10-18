"""챗봇 2단계(1-3): 기억하고 도구 쓰는 챗봇

실행(저장소 맨 위에서): uv run --env-file .env streamlit run course/Chapter01/chatbot/stage2.py
"""
import streamlit as st
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm
from ui import log_step, run_chat

load_dotenv()

llm = get_llm()

# 사이드바: 답 방식과 말투 고르기
mode = st.sidebar.selectbox("답 방식", ["대화", "계산기 도구", "정리 카드"])
style = st.sidebar.selectbox("답 말투", ["친절하게", "한 문장으로", "초등학생에게 설명하듯"])


# ── 답 방식 "대화" (1단계 완성본) ─────────────────────────────────────────────
# ✍️ 목표 2: 이 prompt의 system과 human 사이에 MessagesPlaceholder("history")를 넣습니다
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 친절한 AI 도우미야. 답은 {style} 해 줘."),
    ("human", "{question}"),
])

# ✍️ 목표 1: prompt | llm | StrOutputParser()로 LCEL 체인을 만듭니다
chain = None


def chat_answer(question, history):
    # ✍️ 목표 1·2: chain.stream()에 style·history·question을 넣어 글자 조각을 내보냅니다
    #              (지금은 1단계 코드입니다. 앞의 대화를 기억하지 못합니다)
    messages = prompt.invoke({"style": style, "question": question})
    log_step("모델에 보낸 메시지", [(m.type, m.content) for m in messages.to_messages()])
    count = 0
    for chunk in llm.stream(messages):
        count += 1
        yield chunk.content
    log_step("받은 조각 수", count)


# ── 답 방식 "계산기 도구" ─────────────────────────────────────────────────────
# ✍️ 목표 3: @tool 계산기를 만들고 bind_tools로 llm에 연결합니다


def tool_answer(question):
    # ✍️ 목표 3: tool_calls가 있으면 도구를 실행해 ToolMessage로 돌려주고, 최종 답을 돌려줍니다
    return "아직 계산기 도구를 연결하지 않았습니다. README.md의 2단계 목표 3을 작성합니다."


# ── 답 방식 "정리 카드" ───────────────────────────────────────────────────────
# ✍️ 목표 4: Pydantic 스키마(제목·한 줄 요약·핵심 3가지)와 PydanticOutputParser로 카드 체인을 만듭니다


def card_answer(question):
    # ✍️ 목표 4: 카드를 받아 log_step으로 남기고, 제목·요약·핵심을 마크다운 글로 바꿔 돌려줍니다
    return "아직 정리 카드를 만들지 않았습니다. README.md의 2단계 목표 4를 작성합니다."


def answer(question, history):
    if mode == "계산기 도구":
        return tool_answer(question)
    if mode == "정리 카드":
        return card_answer(question)
    return chat_answer(question, history)


run_chat(answer, "나의 챗봇 - 2단계")
