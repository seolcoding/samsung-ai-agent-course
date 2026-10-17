"""동물보험 챗봇 8단계 실습 견본 앱. 공통 사이드바와 상단 내비게이션."""

import streamlit as st
from backend import initial_mode, resolve_settings
from lesson import STAGES
from ui import REPLAY, setting

st.set_page_config(page_title="동물보험 챗봇 · 8단계", page_icon=":material/pets:", layout="wide")

state = st.session_state
state.setdefault("runs", [])
state.setdefault("mode", {"openai": "OpenAI 실행", "samsung": "사내 실행"}.get(initial_mode(setting), REPLAY))
for key, value in {"role": "동물보험 안내 도우미", "style": "짧은 문단", "top_k": 3, "chunk_size": 600}.items():
    state.setdefault(key, value)

pages = [st.Page("app_pages/overview.py", title="한눈에 보기", icon=":material/map:", default=True)]
pages += [st.Page(f"app_pages/{lesson['slug']}.py", title=f"{n}. {lesson['name']}",
                  icon=f":material/{lesson['icon']}:", url_path=lesson["slug"])
          for n, lesson in STAGES.items()]
page = st.navigation(pages, position="top")

with st.sidebar:
    st.header("실행 모드", anchor=False)
    mode = st.segmented_control("실행 모드", [REPLAY, "OpenAI 실행", "사내 실행"], key="mode",
                                required=True, label_visibility="collapsed")
    settings = resolve_settings(mode, setting)
    state["execution_settings"] = settings
    if mode == REPLAY:
        st.caption("OpenAI로 미리 실제 실행해 저장한 결과를 다시 보여 줍니다. API를 호출하지 않습니다.")
    else:
        st.caption(f"LLM: {settings.get('model') or '모델 미설정'} · 임베딩: {settings.get('embed_model') or '미설정'}")
        st.caption("설정은 Secrets를 먼저, 없으면 환경변수를 읽습니다.")
    st.divider()
    with st.expander("보험 문서 기준"):
        st.markdown("메리츠 펫보험 약관(2024년 제공 문서, 28쪽)을 사용합니다. 쪽번호는 PDF의 물리적 쪽번호입니다.")
        st.caption("현재 판매 조건이나 개인별 보험료는 이 문서로 확인할 수 없습니다.")

page.run()
