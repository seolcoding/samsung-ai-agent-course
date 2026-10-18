"""챗봇 1단계(1-2): LangChain으로 부르고 답을 조각으로 보여 주기

실행(저장소 맨 위에서): uv run --env-file .env streamlit run course/Chapter01/chatbot/stage1.py
"""
import streamlit as st
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm
from ui import log_step, run_chat

load_dotenv()

llm = get_llm()

# 사이드바: 답 말투 고르기
style = st.sidebar.selectbox("답 말투", ["친절하게", "한 문장으로", "초등학생에게 설명하듯"])

# ✍️ 목표 4: system·user를 나눈 ChatPromptTemplate을 만듭니다(변수 {style}, {question})
prompt = None


def answer(question, history):
    # ✍️ 목표 4: prompt에 style과 question을 넣어 보낼 메시지를 만들고 log_step으로 남깁니다

    # ✍️ 목표 3: llm.stream()으로 받은 조각을 하나씩 내보내고(yield), 받은 조각 수를 log_step으로 남깁니다

    return "아직 답하는 코드가 없습니다. README.md의 1단계 할 일을 AI와 함께 작성합니다."


run_chat(answer, "나의 챗봇 - 1단계")
