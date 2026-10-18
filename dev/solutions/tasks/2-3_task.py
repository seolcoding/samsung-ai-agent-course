"""2-3 과제: 역할을 고르는 Streamlit 챗봇"""

import streamlit as st
from dotenv import load_dotenv

from config.llm import get_llm

load_dotenv()

llm = get_llm()

st.title("역할 챗봇")


# 아래에 AI와 함께 코드를 작성합니다
ROLES = {
    "친절한 선생님": "당신은 친절한 선생님입니다. 쉬운 말로 차근차근 설명하세요.",
    "간결한 비서": "당신은 간결한 비서입니다. 한두 문장으로 짧게 답하세요.",
}

role = st.sidebar.selectbox("답변 역할", list(ROLES))

# 화면이 다시 그려져도 기록이 남도록 session_state에 둔다
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.sidebar.button("대화 지우기"):
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if question := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    # 고른 역할을 system 메시지로 맨 앞에 넣는다
    prompt = [("system", ROLES[role])]
    prompt += [(m["role"], m["content"]) for m in st.session_state.messages]

    with st.chat_message("assistant"):
        answer = st.write_stream(chunk.content for chunk in llm.stream(prompt))
    st.session_state.messages.append({"role": "assistant", "content": answer})
