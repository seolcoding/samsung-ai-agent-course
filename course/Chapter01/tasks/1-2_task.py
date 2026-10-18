"""1-2 과제 · requests와 LangChain stream으로 답하는 챗봇

▶️ 실행   uv run --env-file .env python course/Chapter01/tasks/1-2_task.py
✅ 확인   사이드바 "✅ 과제 확인" 버튼
🆘 막히면 오류 메시지 전체를 AI에게 붙여 넣기
"""
import traceback
from pprint import pformat

import requests
import streamlit as st

from config.llm import get_llm
from config.samsung import llm_config

if __name__ == "__main__" and not st.runtime.exists():  # python으로 실행하면 Streamlit 앱으로 띄웁니다
    import sys
    from streamlit.web import cli
    sys.argv = ["streamlit", "run", __file__, "--server.showEmailPrompt", "false", "--server.address", "127.0.0.1"]
    sys.exit(cli.main())

llm = get_llm()
method = st.sidebar.selectbox("연결 방식", ["requests로 직접", "LangChain stream"])


def requests_answer(question):
    samsung = llm_config()  # 사내 게이트웨이 주소·모델·인증 헤더
    url = samsung["base_url"].rstrip("/") + "/chat/completions"
    headers = {**samsung["headers"], "Content-Type": "application/json"}
    # ✍️ 1. requests로 보내고 답 꺼내기
    # ✨ json: model · messages(user 질문) · include_reasoning False → requests.post → log_step("응답 JSON") → choices[0].message.content
    raise NotImplementedError("✍️ 1. 아직 작성하지 않았습니다")


def stream_answer(question):
    # ✍️ 2. LangChain stream()으로 조각 보여 주기
    # ✨ llm.stream(question) → 조각.content를 yield → 다 받으면 log_step("받은 조각 수")
    raise NotImplementedError("✍️ 2. 아직 작성하지 않았습니다")


def answer(question):
    if method == "requests로 직접":
        return requests_answer(question)
    return stream_answer(question)


# ── 화면 (바꾸지 않습니다) ───────────────────────────────────────────────────
LOG = {}  # log_step이 남긴 기록(✅ 과제 확인이 봅니다)


def log_step(title, content):  # 답 아래 접힌 기록 상자 + 터미널 한 줄
    LOG[title] = content
    text = content if isinstance(content, str) else pformat(content, width=100)
    print(f"[{title}] {' '.join(text.split())[:300]}", flush=True)
    st.expander(title).code(text, language=None, wrap_lines=True)


st.title("나의 챗봇 (1-2 과제)")
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])
if question := st.chat_input("질문을 입력하세요"):
    st.chat_message("user").markdown(question)
    with st.chat_message("assistant"):
        try:
            reply = answer(question)
            reply = reply if isinstance(reply, str) else st.write_stream(reply)
            st.session_state.messages += [{"role": "user", "content": question}, {"role": "assistant", "content": reply}]
        except Exception as error:  # 말풍선에는 한 줄, 터미널에는 오류 전체
            traceback.print_exc()
            st.error(f"⚠️ {error}")


# ── ✅ 확인 (바꾸지 않습니다) ────────────────────────────────────────────────
def check(name, test, why):  # test()가 참이면 🟢, 거짓이면 ⛔ why, 오류면 ⛔ 오류 메시지
    try:
        mark, note = ("🟢", "") if test() else ("⛔", why)
    except Exception as error:
        mark, note = ("❔", "사내망에서만 확인됩니다") if "사내 API 설정" in str(error) else ("⛔", str(error))
    print(f"{mark} {name} {note}", flush=True)
    st.sidebar.write(f"{mark} {name}" + (f" — {note}" if note else ""))


def test_requests():
    reply = requests_answer("파이썬이 뭐야? 한 문장으로.")
    return isinstance(reply, str) and reply.strip() and "choices" in LOG.get("응답 JSON", {})


def test_stream():
    pieces = stream_answer("파이썬이 뭐야? 한 문장으로.")
    return not isinstance(pieces, str) and len(list(pieces)) >= 2


if st.sidebar.button("✅ 과제 확인"):
    st.sidebar.markdown("**✅ 확인**")
    scratch = st.empty()
    with scratch.container():  # 확인하며 그린 것은 끝나면 지운다
        check("1. requests로 답을 꺼냈다", test_requests, "답이 문장이 아니거나 '응답 JSON' 기록이 없습니다")
        check("2. stream()으로 답을 조각으로 보냈다", test_stream, "조각이 2개 이상 오지 않았습니다")
    scratch.empty()
