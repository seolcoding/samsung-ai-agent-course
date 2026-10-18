"""2-3 과제(강사용 정답) · 대화가 남는 Streamlit 약관 챗봇

시작본 course/Chapter01/tasks/2-3_task.py와 ✍️ 두 자리만 다르다.
약관 PDF를 그 폴더 기준으로 찾으므로, 그 자리에 복사해 실행한다.
"""
from pathlib import Path

import streamlit as st
from langchain_chroma import Chroma
from langchain_community.document_loaders import PDFMinerLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.embeddings import get_embeddings
from config.llm import get_llm

if __name__ == "__main__" and not st.runtime.exists():  # python으로 실행하면 Streamlit 앱으로 띄웁니다
    import sys
    from streamlit.web import cli
    sys.argv = ["streamlit", "run", __file__, "--server.showEmailPrompt", "false", "--server.address", "127.0.0.1"]
    sys.exit(cli.main())

PDF_PATH = Path(__file__).resolve().parent.parent / "notebooks" / "data" / "meritz_pet_insurance.pdf"


@st.cache_resource
def load_rag_chain():
    documents = PDFMinerLoader(str(PDF_PATH)).load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=75).split_documents(documents)
    retriever = Chroma.from_documents(chunks, embedding=get_embeddings()).as_retriever(search_kwargs={"k": 3})
    prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 펫보험 약관 안내 도우미야. 아래 context만 근거로 답해.\n\ncontext:\n{context}"),
        ("human", "{question}"),
    ])

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    return {"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | get_llm() | StrOutputParser()


st.title("펫보험 약관 챗봇 (2-3 과제)")
question = st.chat_input("질문을 입력하세요")

# ✍️ 1. 대화 기록 남기기
# ✨ st.session_state.messages(없으면 []) · question 있으면 {"role": "user", "content": …} append · 기록 전부 st.chat_message(role)로 다시 그리기
if "messages" not in st.session_state:
    st.session_state.messages = []
if question:
    st.session_state.messages.append({"role": "user", "content": question})
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question:
    with st.chat_message("assistant"):
        # ✍️ 2. 답을 조각으로 그리기
        # ✨ load_rag_chain().stream(question) → st.write_stream → 돌려받은 글을 assistant로 session_state.messages에 append
        reply = st.write_stream(load_rag_chain().stream(question))
        st.session_state.messages.append({"role": "assistant", "content": reply})

# ── ✅ 확인 (바꾸지 않습니다): 질문을 두 번 보낸 뒤 누릅니다 ──
if st.sidebar.button("✅ 과제 확인"):
    history = st.session_state.get("messages")
    asked = [m for m in history or [] if m.get("role") == "user"]
    answers = [m for m in history or [] if m.get("role") == "assistant"]
    not_text = [m["content"] for m in answers if not isinstance(m.get("content"), str) or not m["content"].strip()]
    if history is None:
        results = ["⛔ 1. 아직 작성하지 않았습니다 (st.session_state.messages가 없다)"]
    elif len(asked) < 2:
        results = [f"⛔ 1. 기록에 질문이 {len(asked)}개다 (질문을 두 번 보낸 뒤 누릅니다)"]
    else:
        results = [f"🟢 1. 질문 {len(asked)}개가 다시 실행돼도 기록에 남아 있다"]
    if not answers:
        results.append("⛔ 2. 아직 작성하지 않았습니다 (기록에 답이 없다)")
    elif not_text:
        results.append(f"⛔ 2. 기록된 답이 글이 아니다: {str(not_text[0])[:40]}")
    elif len(answers) != len(asked):
        results.append(f"⛔ 2. 질문 {len(asked)}개에 답이 {len(answers)}개다")
    else:
        results.append(f"🟢 2. 답 {len(answers)}개가 글로 기록에 남아 있다")
    print("✅ 확인\n" + "\n".join(results), flush=True)
    for line in results:
        st.sidebar.write(line)
