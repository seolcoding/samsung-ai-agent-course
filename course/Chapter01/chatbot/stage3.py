"""챗봇 3단계(1-4): 약관 RAG 챗봇

실행(저장소 맨 위에서): uv run --env-file .env streamlit run course/Chapter01/chatbot/stage3.py
"""
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PDFMinerLoader
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field

from config.embeddings import get_embeddings
from config.llm import get_llm
from config.ragaas import post_ragaas
from ui import log_step, run_chat

load_dotenv()

llm = get_llm()

# 사이드바: 답 방식과 말투 고르기
mode = st.sidebar.selectbox("답 방식", ["대화", "계산기 도구", "정리 카드", "약관 질문"])
style = st.sidebar.selectbox("답 말투", ["친절하게", "한 문장으로", "초등학생에게 설명하듯"])
search_method = st.sidebar.selectbox("검색 방식", ["로컬 Chroma", "사내 RAGaaS"])


# ── 답 방식 "대화" ────────────────────────────────────────────────────────────
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 친절한 AI 도우미야. 답은 {style} 해 줘."),
    MessagesPlaceholder("history"),
    ("human", "{question}"),
])

chain = prompt | llm | StrOutputParser()


def chat_answer(question, history):
    inputs = {"style": style, "history": history, "question": question}
    log_step("모델에 보낸 메시지", [(m.type, m.content) for m in prompt.invoke(inputs).to_messages()])
    count = 0
    for text in chain.stream(inputs):
        count += 1
        yield text
    log_step("받은 조각 수", count)


# ── 답 방식 "계산기 도구" ─────────────────────────────────────────────────────
@tool
def calculate(expression: str) -> str:
    """수식을 계산한다. 예: '1234 * 5678'"""
    return str(eval(expression, {"__builtins__": {}}))  # noqa: S307


tools = [calculate]
tool_map = {t.name: t for t in tools}
llm_with_tools = llm.bind_tools(tools)


def tool_answer(question):
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
    card = card_chain.invoke({"question": question})
    log_step("받은 카드", card)
    lines = [f"### {card.title}", card.summary] + [f"- {point}" for point in card.points]
    return "\n".join(lines)


# ── 답 방식 "약관 질문" ───────────────────────────────────────────────────────
PDF_PATH = Path(__file__).resolve().parent.parent / "notebooks" / "data" / "meritz_pet_insurance.pdf"


# ✍️ 목표 1: PDF 읽기 → 나누기(500자, 겹침 75자) → get_embeddings()로 Chroma에 저장을 @st.cache_resource로 한 번만 합니다


def search(question):
    # ✍️ 목표 4: 검색 방식이 "사내 RAGaaS"면 post_ragaas("retrieve-rrf", …)로 찾은 글 3개를 돌려줍니다
    # ✍️ 목표 2: as_retriever(search_kwargs={"k": 3})로 찾은 청크 3개의 글을 돌려줍니다
    return []


# ✍️ 목표 3: context에 없는 질문이면 "문서에서 확인할 수 없습니다"라고 답하게 합니다


def rag_answer(question):
    # ✍️ 목표 2: 찾은 글을 log_step으로 근거로 남기고, context로 넣어 답을 조각으로 내보냅니다
    return "아직 약관 검색을 만들지 않았습니다. README.md의 3단계를 작성합니다."


def answer(question, history):
    if mode == "약관 질문":
        return rag_answer(question)
    if mode == "계산기 도구":
        return tool_answer(question)
    if mode == "정리 카드":
        return card_answer(question)
    return chat_answer(question, history)


run_chat(answer, "나의 챗봇 - 3단계")
