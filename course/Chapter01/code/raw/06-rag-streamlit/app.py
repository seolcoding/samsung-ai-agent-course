from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PDFMinerLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.embeddings import get_embeddings
from config.llm import get_llm

load_dotenv()

# ── RAG 파이프라인 초기화 (앱 시작 시 한 번만 실행) ─────────────────────────
# 사용자가 어떤 질문을 한다 -> agent를 `호출`한다. 
    # 결국 가우스 모델을 호출할건데 -> 함수 실행 결과에 불과 하겠죠.
@st.cache_resource
def load_rag_chain():
    PDF_PATH = Path(__file__).parent / 'data' / 'meritz_pet_insurance.pdf'

    loader = PDFMinerLoader(str(PDF_PATH.resolve()))
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=75)
    chunks = splitter.split_documents(documents)

    embeddings = get_embeddings()
    vectorstore = Chroma.from_documents(chunks, embedding=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={'k': 3})

    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ('system', '당신은 문서 기반 QA 어시스턴트입니다. 주어진 context만 근거로 답하세요.\n\ncontext:\n{context}'),
        ('human', '{question}'),
    ])

    def format_docs(docs):
        return '\n\n'.join(doc.page_content for doc in docs)

    chain = (
        {'context': retriever | format_docs, 'question': RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


# ── Streamlit UI ──────────────────────────────────────────────────────────────

st.title('보험 약관 QA 챗봇')
st.caption('메리츠 펫보험 약관을 기반으로 답변합니다.')

# 대화 기록을 session_state에 저장 (새로고침 전까지 유지)
    # 어디까지나 화면에 보여주기 위한 session 관리인 것
    # 이 message를 토대로 LLM이 이전 대화를 기억한다거나 그런건 X
if 'messages' not in st.session_state:
    st.session_state.messages = []

# 이전 대화 표시
for msg in st.session_state.messages:
    # msg -> LLM이 만들어낸 답변 messages (우리가 아까까지 graph의 State에 담던 그 messages)
        # user냐? AI냐?에 따라서
        # 대화창을 어디에 보여줄것인지를 달리 할 것
    with st.chat_message(msg['role']):
        st.write(msg['content'])

# 사용자 입력
if prompt := st.chat_input('질문을 입력하세요 (예: 보험료는 어떻게 계산되나요?)'):
    # 사용자 메시지 표시
    # TODO: 사용자 메시지를 session_state에 저장해 주세요.
    st.session_state.messages.append({'role': 'user', 'content': prompt})

    with st.chat_message('user'):
        st.write(prompt)

    # AI 응답 (스트리밍)
    with st.chat_message('assistant'):
        # 한개의 runnable을 받았다.
        rag_chain = load_rag_chain()
        # TODO: RAG 체인의 stream() 결과를 Streamlit에 출력해 주세요.
            # runnable을 실행하는 방법 -> invoke, stream
        response = st.write_stream(rag_chain.stream(prompt))

    # TODO: AI 응답을 session_state에 저장해 주세요.
    st.session_state.messages.append({'role': 'assistant', 'content': response})
