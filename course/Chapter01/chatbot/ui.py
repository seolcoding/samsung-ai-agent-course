"""챗봇 화면(고정). 이 파일은 고치지 않습니다.

단계 파일(stage1.py ~ stage5.py)이 answer 함수를 만들어 run_chat에 넘깁니다.
answer(question, history)는 답을 문자열로 돌려주거나, 글자 조각을 하나씩 내보내는(yield) 제너레이터로 돌려줍니다.
"""
import uuid
from pprint import pformat

import streamlit as st


def log_step(title, content):
    """실행 기록을 남깁니다. 화면에는 접힌 상자로 모두 보이고, 터미널에는 print로 앞부분 한 줄만 보입니다."""
    text = content if isinstance(content, str) else pformat(content, width=100)
    print(f"[{title}] {' '.join(text.split())[:300]}", flush=True)
    with st.expander(title):
        st.code(text, language=None, wrap_lines=True)


def add_message(role, content):
    """대화 기록에 메시지 하나를 더합니다(role은 "user" 또는 "assistant")."""
    st.session_state.messages.append({"role": role, "content": content})


def run_chat(answer, title):
    """제목, 대화 기록, 입력창, "대화 지우기" 버튼을 그리고, 질문이 오면 answer로 답합니다."""
    st.title(title)

    # 대화 기록과 대화 번호(thread_id)는 st.session_state에 둡니다. 화면이 다시 그려져도 남습니다.
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    if st.sidebar.button("대화 지우기"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())  # 새 대화 번호: 그래프의 기억도 새로 시작합니다

    # 지금까지의 대화를 다시 그립니다
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("질문을 입력하세요")
    if not question:
        return

    history = list(st.session_state.messages)  # 이번 질문 앞까지의 대화
    add_message("user", question)
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        reply = answer(question, history)
        if isinstance(reply, str):
            st.markdown(reply)
        else:
            reply = st.write_stream(reply)  # 조각이 올 때마다 이어 붙여 보여 주고, 다 붙인 글을 돌려줍니다
    add_message("assistant", reply)
