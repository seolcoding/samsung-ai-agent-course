"""1-4 과제 · 약관 PDF로 답하는 RAG 챗봇

✍️ 할 곳  코드의 `# ✍️` 표시 2곳만 채웁니다 (`# ✨` 줄은 AI에게 말할 힌트)
▶️ 실행   uv run --env-file .env python course/Chapter01/tasks/1-4_task.py
✅ 확인   사이드바 "✅ 과제 확인" 버튼
🆘 막히면 오류 메시지 전체를 AI에게 붙여 넣기
"""
import traceback
from pathlib import Path
from pprint import pformat

import streamlit as st
from langchain_chroma import Chroma
from langchain_community.document_loaders import PDFMinerLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.embeddings import get_embeddings
from config.llm import get_llm

if __name__ == "__main__" and not st.runtime.exists():  # python으로 실행하면 Streamlit 앱으로 띄웁니다
    import sys
    from streamlit.web import cli
    sys.argv = ["streamlit", "run", __file__, "--server.showEmailPrompt", "false", "--server.address", "127.0.0.1"]
    sys.exit(cli.main())

PDF_PATH = Path(__file__).resolve().parent.parent / "notebooks" / "data" / "meritz_pet_insurance.pdf"


@st.cache_resource  # 앱이 다시 실행돼도 PDF 읽기·임베딩은 처음 한 번만
def load_retriever():
    documents = PDFMinerLoader(str(PDF_PATH)).load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=75).split_documents(documents)
    print(f"[벡터 저장소] 청크 {len(chunks)}개 저장", flush=True)
    return Chroma.from_documents(chunks, embedding=get_embeddings()).as_retriever(search_kwargs={"k": 3})


retriever = load_retriever()
llm = get_llm()


def answer(question):
    # ✍️ 1. 검색 결과를 context로 넣어 답하기
    # ✨ retriever.invoke(question) → log_step("근거") → page_content 합쳐 context → (prompt | llm | StrOutputParser()).stream
    raise NotImplementedError("✍️ 1. 아직 작성하지 않았습니다")


# ✍️ 2. 문서에 없으면 "문서에서 확인할 수 없습니다"라고 답하기
# ✨ system 문장에 규칙 더하기 · context만 근거로 · 없으면 "문서에서 확인할 수 없습니다"만
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 펫보험 약관 안내 도우미야.\n\ncontext:\n{context}"),
    ("human", "{question}"),
])


# ── 화면 (바꾸지 않습니다) ───────────────────────────────────────────────────
LOG = {}  # log_step이 남긴 기록(✅ 과제 확인이 봅니다)


def log_step(title, content):  # 답 아래 접힌 기록 상자 + 터미널 한 줄
    LOG[title] = content
    text = content if isinstance(content, str) else pformat(content, width=100)
    print(f"[{title}] {' '.join(text.split())[:300]}", flush=True)
    st.expander(title).code(text, language=None, wrap_lines=True)


st.title("나의 약관 챗봇 (1-4 과제)")
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
        mark, note = "⛔", str(error)
    print(f"{mark} {name} {note}", flush=True)
    st.sidebar.write(f"{mark} {name}" + (f" — {note}" if note else ""))


def test_rag():  # 약관에만 있는 수술 당일 한도(200만·150만 원)가 답에 나오면 context를 쓴 것
    text = "".join(answer("반려견이 수술을 받으면 수술비도 보장되나요?"))
    return any(title.startswith("근거") for title in LOG) and any(n in text for n in ("200", "150"))


def test_unknown():
    if "확인할 수 없습니다" not in str(prompt):
        raise NotImplementedError("✍️ 2. 아직 작성하지 않았습니다")
    return "확인할 수 없습니다" in "".join(answer("삼성전자의 오늘 주가는 얼마야?"))


if st.sidebar.button("✅ 과제 확인"):
    st.sidebar.markdown("**✅ 확인**")
    scratch = st.empty()
    with scratch.container():  # 확인하며 그린 것은 끝나면 지운다
        check("1. 약관 근거로 답했다", test_rag, "'근거' 기록이 없거나 답에 약관의 수술 한도가 없습니다")
        check("2. 문서에 없는 질문을 거절했다", test_unknown, "주가 질문에 '문서에서 확인할 수 없습니다'라고 하지 않았습니다")
    scratch.empty()
