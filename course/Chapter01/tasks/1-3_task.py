"""1-3 과제 · 체인으로 답하고 앞 대화를 기억하는 챗봇

✍️ 할 곳  코드의 `# ✍️` 표시 2곳만 채웁니다 (`# ✨` 줄은 AI에게 말할 힌트)
▶️ 실행   uv run --env-file .env python course/Chapter01/tasks/1-3_task.py
✅ 확인   사이드바 "✅ 과제 확인" 버튼
🆘 막히면 오류 메시지 전체를 AI에게 붙여 넣기
"""
import traceback
from pprint import pformat

import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from config.llm import get_llm

if __name__ == "__main__" and not st.runtime.exists():  # python으로 실행하면 Streamlit 앱으로 띄웁니다
    import sys
    from streamlit.web import cli
    sys.argv = ["streamlit", "run", __file__, "--server.showEmailPrompt", "false", "--server.address", "127.0.0.1"]
    sys.exit(cli.main())

llm = get_llm()
style = st.sidebar.selectbox("답 말투", ["친절하게", "한 문장으로", "초등학생에게 설명하듯"])

# ✍️ 1. prompt | llm | parser 체인 만들기
# ✨ ChatPromptTemplate.from_messages: system(말투 {style}) · human({question}) → prompt | llm | StrOutputParser()
prompt = chain = None


def answer(question, history):
    if chain is None:
        raise NotImplementedError("✍️ 1. 아직 작성하지 않았습니다")
    inputs = {"style": style, "question": question}
    # ✍️ 2. MessagesPlaceholder로 앞 대화 기억하기
    # ✨ 1의 prompt에서 system과 human 사이 MessagesPlaceholder("history") · inputs에 history
    sent = prompt.invoke(inputs).to_messages()
    log_step("모델에 보낸 메시지", [(m.type, m.content) for m in sent])
    return chain.stream(inputs)


# ── 화면 (바꾸지 않습니다) ───────────────────────────────────────────────────
LOG = {}  # log_step이 남긴 기록(✅ 과제 확인이 봅니다)


def log_step(title, content):  # 답 아래 접힌 기록 상자 + 터미널 한 줄
    LOG[title] = content
    text = content if isinstance(content, str) else pformat(content, width=100)
    print(f"[{title}] {' '.join(text.split())[:300]}", flush=True)
    st.expander(title).code(text, language=None, wrap_lines=True)


st.title("나의 챗봇 (1-3 과제)")
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])
if question := st.chat_input("질문을 입력하세요"):
    st.chat_message("user").markdown(question)
    with st.chat_message("assistant"):
        try:
            reply = answer(question, list(st.session_state.messages))  # 이번 질문 앞까지의 대화
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
        mark, note = "⛔", str(error)
    print(f"{mark} {name} {note}", flush=True)
    st.sidebar.write(f"{mark} {name}" + (f" — {note}" if note else ""))


def test_chain():
    text = "".join(answer("안녕?", []))
    system = LOG["모델에 보낸 메시지"][0]
    return text.strip() and system[0] == "system" and style in system[1] and isinstance(chain.last, StrOutputParser)


def test_history():
    history = [{"role": "user", "content": "내 이름은 민수야."}, {"role": "assistant", "content": "반가워, 민수야!"}]
    text = "".join(answer("내 이름이 뭐야?", history))
    return len(LOG["모델에 보낸 메시지"]) >= 4 and "민수" in text


if st.sidebar.button("✅ 과제 확인"):
    st.sidebar.markdown("**✅ 확인**")
    scratch = st.empty()
    with scratch.container():  # 확인하며 그린 것은 끝나면 지운다
        check("1. prompt | llm | parser 체인으로 답했다", test_chain, "system에 말투가 없거나 체인 끝이 StrOutputParser가 아닙니다")
        check("2. 앞 대화를 보내 이름을 기억했다", test_history, "보낸 메시지에 앞 대화가 없거나 이름을 몰랐습니다")
    scratch.empty()
