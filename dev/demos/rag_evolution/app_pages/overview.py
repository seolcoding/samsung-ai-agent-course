"""한눈에 보기 · 8단계 지도와 사용법."""

import streamlit as st
from lesson import COMMON_QUESTION, GROUPS, STAGES

st.title("동물보험 챗봇, 8단계로 발전시키기", anchor=False)
st.markdown("날것의 LLM API에서 시작해 한계를 하나씩 겪고, LangChain 부품·도구·LangGraph·RAG를 붙여 "
            "스스로 점검하는 **에이전트**가 되기까지를 따라가는 실습 견본 앱입니다.")

with st.container(horizontal=True):
    for icon, text in [("chat", "① 예시 질문으로 써 보기"), ("schema", "② 구조와 핵심 코드 보기"),
                       ("smart_toy", "③ CodeMate로 내 앱 만들기"), ("compare", "④ 같은 질문으로 비교하기")]:
        st.badge(text, icon=f":material/{icon}:", color="blue")

for title, subtitle, stages in GROUPS:
    st.markdown(f"**{title}** · {subtitle}")
    for column, n in zip(st.columns(3), stages):
        lesson = STAGES[n]
        with column.container(border=True, height="stretch"):
            st.page_link(f"app_pages/{lesson['slug']}.py", label=f"{n}. {lesson['name']}",
                         icon=f":material/{lesson['icon']}:")
            st.caption(lesson["change"])

st.page_link(f"app_pages/{STAGES[9]['slug']}.py", label=f"9. {STAGES[9]['name']} — 같은 질문의 단계별 결과를 나란히",
             icon=f":material/{STAGES[9]['icon']}:")
st.info(f"**공통 질문** · {COMMON_QUESTION}\n\n모든 단계의 예시 질문에 들어 있습니다. 단계마다 답이 어떻게 달라지는지 보고, 9에서 나란히 비교하세요.",
        icon=":material/help:")
st.caption("왼쪽 사이드바의 실행 모드: **녹화 재생**은 미리 실행한 결과를 보여 주고, **OpenAI 실행**·**사내 실행**은 실제 API를 호출합니다.")
