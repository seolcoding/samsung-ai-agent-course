"""실행: uv run --extra notebooks streamlit run src/courseware/app.py"""

import asyncio
import uuid

import streamlit as st
from langgraph.types import Command

from courseware.capstone import build_capstone
from courseware.knowledge import answer_from_documents

st.set_page_config(page_title="근거를 확인하는 Agent 실습", page_icon=":material/school:")
st.title("근거를 확인하는 Agent 실습")
st.caption("교육용 모의 자료 · 모델 응답은 원문 발췌 · 실제 사내 문서 연결 없음")
mode = st.radio("실습 선택", ["문서 질문", "승인 후 보고서"], horizontal=True)

if mode == "문서 질문":
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if question := st.chat_input("RAG의 검색 근거는 어떻게 확인하나요?"):
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)
        result = answer_from_documents(question)
        with st.chat_message("assistant"):
            st.markdown(result["answer"])
            with st.expander("사용한 근거"):
                for source in result["sources"]:
                    st.write(f'{source["id"]} · {source["title"]} · {source["source"]}')
        st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
else:
    topic = st.text_input("보고서 주제", value="RAG 검색과 도구 연결, 승인")
    if st.button("근거 조사", disabled=not topic.strip()):
        st.session_state.graph = build_capstone()
        st.session_state.config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        st.session_state.result = asyncio.run(st.session_state.graph.ainvoke({"topic": topic, "trace": []}, st.session_state.config))
        st.session_state.pending = bool(st.session_state.result.get("__interrupt__"))
    if "result" in st.session_state:
        result = st.session_state.result
        for doc in result.get("evidence", []):
            with st.expander(f'{doc["id"]} · {doc["title"]}', expanded=True):
                st.write(doc["text"])
        if st.session_state.get("pending"):
            left, right = st.columns(2)
            approved = left.button("승인하고 작성")
            rejected = right.button("거절하고 중단")
            if approved or rejected:
                st.session_state.result = asyncio.run(st.session_state.graph.ainvoke(Command(resume={"approved": approved}), st.session_state.config))
                st.session_state.pending = False
                st.rerun()
        elif result.get("writer_executed"):
            st.markdown(result["report"])
            st.json(result["evaluation"])
            st.download_button("보고서 내려받기", result["report"], file_name="training_report.md", mime="text/markdown")
        elif "evidence" in result:
            st.info("작성하지 않고 종료했습니다. 승인 거절 또는 근거 부족을 확인하세요.")
        with st.expander("실행 순서 확인"):
            st.write(result.get("trace", []))
