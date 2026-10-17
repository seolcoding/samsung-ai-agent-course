"""단계 화면 = 핵심(구조·핵심 코드·만들어 보기) + 써 보기(채팅) + 접어 둔 심화.

대화 기록은 사용자별 Session State에만 둔다.
"""

import hashlib
import inspect
import json
import os
import re
import time

import streamlit as st

import graphs
from backend import (RAG_STAGES, STAGE_RUNNERS, MemorySaver, build_store, cache_fingerprint,
                     graph_mermaid, load_recordings, missing_settings, run_live, run_replay)
from lesson import ANSWER_STYLES, COMMON_QUESTION, RUN_STAGES, STAGES

REPLAY = "녹화 재생"
GRAPH_STAGES = (5, 8)


def setting(name: str) -> str:
    try:
        value = st.secrets.get(name, "")
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        value = ""
    return str(value or os.getenv(name, "")).strip()


@st.cache_resource(ttl=3600, max_entries=8, show_spinner=False)
def cached_store(fingerprint: str, chunk_size: int, _settings: dict):
    # 인증 값은 해시 지문으로만 캐시 키에 들어간다.
    return build_store(_settings, chunk_size)


def connection_key() -> str:
    settings = st.session_state.execution_settings
    data = [st.session_state.mode, cache_fingerprint(settings, 0)]
    return hashlib.sha256(json.dumps(data).encode("utf-8")).hexdigest()[:16]


def options(stage: int) -> dict:
    state = st.session_state
    return {"role": state.role, "style": state.style, "top_k": state.top_k, "chunk_size": state.chunk_size}


def stage_runs(stage: int | None = None, with_compare: bool = False) -> list:
    """이 연결의 실행 기록. 비교 화면에서 한 번에 실행한 것은 단계 대화에 섞지 않는다."""
    key = connection_key()
    return [run for run in st.session_state.runs
            if run["conn"] == key and (stage is None or run["stage"] == stage)
            and (with_compare or not run.get("compare"))]


# ── 실행 ─────────────────────────────────────────────────────────────────────

def history_for(stage: int) -> list:
    """3단계부터: 이 단계에서 나눈 이전 대화. 화면 기록을 그대로 모델에 다시 보낸다."""
    turns = []
    for run in stage_runs(stage):
        if run["answer"] and not run.get("error"):
            turns += [{"role": "user", "content": run["question"]}, {"role": "assistant", "content": run["answer"]}]
    return turns[-20:]


def memory_for(stage: int) -> tuple:
    """5단계 checkpointer. 사용자 세션·연결마다 하나, '대화 지우기'로 새로 만든다."""
    memories = st.session_state.setdefault("memories", {})
    key = f"{connection_key()}:{stage}"
    if key not in memories:
        memories[key] = (MemorySaver(), f"{key}:{time.time_ns()}")
    return memories[key]


def events_for(stage: int, question: str, opts: dict, fresh: bool = False):
    if st.session_state.mode == REPLAY:
        return run_replay(stage, question)
    settings = st.session_state.execution_settings
    factory = lambda: cached_store(cache_fingerprint(settings, opts["chunk_size"]), opts["chunk_size"], settings)
    memory, thread_id = (MemorySaver(), "compare") if fresh else memory_for(stage)
    history = [] if fresh else history_for(stage)
    return run_live(stage, question, settings, opts, factory, history=history, memory=memory, thread_id=thread_id)


def new_run(stage: int, question: str, opts: dict, compare: bool = False) -> dict:
    return {"stage": stage, "mode": st.session_state.mode, "conn": connection_key(), "question": question, "compare": compare,
            "opts": opts, "answer": "", "trace": [], "sources": [], "photos": [], "review": {}, "metrics": {}}


def absorb(run: dict, event: dict) -> str:
    """이벤트 하나를 실행 기록에 넣고, 답변 글자면 그 글자를 돌려준다."""
    kind = event["type"]
    if kind == "token":
        text = strip_images(event["text"]) if run["photos"] else event["text"]
        run["answer"] += text
        return text
    if kind == "step":
        run["trace"].append(event)
    elif kind == "sources":
        run["sources"] += [source for source in event["data"] if source not in run["sources"]]
    elif kind == "photo":
        run["photos"].append(event["data"])
    elif kind in ("metrics", "review"):
        run[kind] = event["data"]
        if kind == "review" and event["data"].get("status") in ("error", "parse_error"):
            run["error"] = "검토 응답 형식 오류"
    return ""


def fail(run: dict, exc: Exception, started: float) -> str:
    run["metrics"].setdefault("seconds", round(time.perf_counter() - started, 2))
    if isinstance(exc, LookupError):
        run["error"] = "녹화 없음"
        return str(exc)
    # 오류 원문에는 인증 값이 섞일 수 있어 종류만 남긴다.
    run["error"] = type(exc).__name__
    if isinstance(exc, (ValueError, RuntimeError)) and str(exc).startswith(("필요한 설정", "도구 호출이")):
        return str(exc)
    return "실행이 완료되지 않았습니다. 실행 모드의 설정과 API 연결을 확인하세요."


def execute(stage: int, question: str, opts: dict) -> dict:
    """채팅 화면에 질문과 스트리밍 답변을 그린다."""
    run = new_run(stage, question, opts)
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        first = not stage_runs() and st.session_state.mode != REPLAY
        status = st.status("실행 중 · 처음 실행은 문서 인덱스를 만드느라 조금 걸립니다" if first else "실행 중",
                           expanded=False, type="compact")
        answer = st.empty()
        started = time.perf_counter()
        try:
            for event in events_for(stage, question, opts):
                if event["type"] == "step":
                    status.update(label=event["name"])
                if absorb(run, event):
                    answer.markdown(tame(run["answer"]))
            status.update(label="검토 응답 형식 오류" if run.get("error") else "완료",
                          state="error" if run.get("error") else "complete")
        except Exception as exc:
            message = fail(run, exc, started)
            status.update(label="실행 실패", state="error")
            (st.warning if run["error"] == "녹화 없음" else st.error)(message)
        render_extras(run)
    st.session_state.runs = (st.session_state.runs + [run])[-200:]
    return run


def execute_quietly(stage: int, question: str, opts: dict) -> dict:
    """비교 화면용. 채팅 없이 실행 기록만 만든다."""
    run = new_run(stage, question, opts, compare=True)
    started = time.perf_counter()
    try:
        for event in events_for(stage, question, opts, fresh=True):
            absorb(run, event)
    except Exception as exc:
        fail(run, exc, started)
    st.session_state.runs = (st.session_state.runs + [run])[-200:]
    return run


# ── 답변 표시 ─────────────────────────────────────────────────────────────────

def tame(text: str) -> str:
    """채팅용으로 다듬는다. 제목(#)은 굵은 글씨로 낮추고, 모델이 직접 적은 이미지는 그리지 않고 주소만 보인다."""
    text = re.sub(r"^#{1,6}\s*(.+)$", r"**\1**", text, flags=re.M)
    return re.sub(r"!\[([^\]]*)\]\(([^)]*)\)", r"`이미지(모델이 적은 주소, 확인 안 됨): \2`", text)


def strip_images(text: str) -> str:
    # 사진은 출처를 붙인 전용 영역에서 보여 준다.
    return re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)


def source_labels(run: dict) -> list[str]:
    labels = []
    for source in run["sources"]:
        label = f"PDF {source['page']}쪽" if source.get("page") is not None else source.get("source", "출처")
        if label not in labels:
            labels.append(label)
    return labels


def render_photos(photos: list):
    for photo in photos:
        if not photo.get("image_url"):
            continue
        st.image(photo["image_url"], width=320)
        license_text = (f"[{photo.get('license', '라이선스')}]({photo['license_url']})"
                        if photo.get("license_url") else photo.get("license", "라이선스 미확인"))
        st.caption(f"저작자: {photo.get('author', '미확인')} · {license_text} · [사진 출처]({photo.get('source_url', '')})")


def render_review(review: dict):
    if not review:
        return
    status = review.get("status")
    rewrites = f"재작성 {review.get('rewrites', 0)}회 / 최대 2회"
    if status == "passed":
        st.success(f"검토 통과 · {rewrites}", icon=":material/task_alt:")
    elif status in ("error", "parse_error"):
        st.error("검토 응답을 해석하지 못했습니다(JSON 형식 오류).", icon=":material/error:")
    else:
        st.warning(f"재작성 한도 도달 · 검토 미통과 · {rewrites}", icon=":material/warning:")
    st.caption("모델의 검토 의견입니다. 정답 보증이나 정확성 점수가 아닙니다.")


def render_extras(run: dict):
    render_photos(run["photos"])
    render_review(run["review"])
    labels = source_labels(run)
    if labels:
        st.caption("근거: " + " · ".join(labels))


def render_history(run: dict):
    with st.chat_message("user"):
        st.markdown(run["question"])
    with st.chat_message("assistant"):
        if run["answer"]:
            st.markdown(tame(run["answer"]))
        if run.get("error"):
            st.caption(f":red[실행 실패 · {run['error']}]")
        render_extras(run)


# ── 페이지 구성 ───────────────────────────────────────────────────────────────

def header(stage: int):
    lesson = STAGES[stage]
    st.subheader(f"{stage}. {lesson['name']}", anchor=False)
    st.markdown(lesson["change"])
    st.caption(f":material/lightbulb: {lesson['why']}")


def mode_notice():
    if st.session_state.mode == REPLAY:
        meta = load_recordings().get("meta", {})
        st.caption(f":material/replay: 녹화 재생 · {meta.get('recorded_at', '')} {meta.get('model', '')}로 실제 실행한 결과입니다. "
                   "예시 질문만 재생됩니다.")


def _pick(key: str):
    st.session_state.pending_question = st.session_state[key]
    st.session_state[key] = None


def clear_chat(stage: int):
    key = connection_key()
    st.session_state.runs = [run for run in st.session_state.runs
                             if not (run["conn"] == key and run["stage"] == stage and not run.get("compare"))]
    st.session_state.get("memories", {}).pop(f"{key}:{stage}", None)


def render_try(stage: int):
    lesson = STAGES[stage]
    replay = st.session_state.mode == REPLAY
    with st.container(horizontal=True, vertical_alignment="center"):
        st.markdown("**:material/chat: 써 보기**")
        st.caption(":material/memory: 이전 대화를 기억합니다" if lesson["memory"] else ":material/block: 이전 대화를 기억하지 않습니다")
        st.button("대화 지우기", icon=":material/delete_sweep:", type="tertiary", key=f"clear_{stage}",
                  on_click=clear_chat, args=(stage,))
    mode_notice()
    if stage == 2:
        with st.container(horizontal=True, vertical_alignment="bottom"):
            st.text_input("역할", key="role", persist_state="session", disabled=replay)
            st.segmented_control("답변 형식", ANSWER_STYLES, key="style", required=True,
                                 persist_state="session", disabled=replay)
    missing = [] if replay else missing_settings(st.session_state.execution_settings, rag=stage in RAG_STAGES)
    if missing:
        st.warning("이 실행 모드에 필요한 설정이 없습니다: " + ", ".join(missing))
    st.pills("예시 질문", lesson["examples"], key=f"examples_{stage}", on_change=_pick,
             args=(f"examples_{stage}",), disabled=bool(missing), wrap=True)
    messages = st.container()
    typed = st.chat_input("녹화 재생에서는 예시 질문만 실행됩니다" if replay else "동물이나 보험에 대해 질문하세요",
                          key=f"chat_{stage}", max_chars=2000, submit_mode="disable",
                          disabled=bool(missing) or replay)
    question = typed or st.session_state.pop("pending_question", None)
    with messages:
        previous = stage_runs(stage)
        for run in previous:
            render_history(run)
        if question:
            execute(stage, question, options(stage))
        elif not previous:
            st.caption("예시 질문을 위에서부터 차례로 눌러 보거나, 아래에 직접 질문해 보세요.")


def render_core(stage: int):
    lesson = STAGES[stage]
    structure, code, build = st.tabs([":material/schema: 구조", ":material/code: 핵심 코드", ":material/smart_toy: 만들어 보기"])
    with structure:
        st.mermaid_chart(lesson["diagram"] or graph_mermaid(stage))
        with st.container(horizontal=True):
            for concept in lesson["concepts"]:
                st.badge(concept, color="blue")
        visits_slot = st.empty() if stage in GRAPH_STAGES else None
    with code:
        st.code(lesson["code"], language="python")
        st.caption("줄인 코드입니다. 이 앱이 실제로 실행하는 코드는 아래 심화에 있습니다.")
    with build:
        st.caption("CodeMate에 붙여 넣고, 만든 앱에 같은 예시 질문을 넣어 이 화면과 비교하세요.")
        st.code(lesson["prompt"], language=None, wrap_lines=True)
        st.markdown("**성공 기준**")
        for index, text in enumerate(lesson["checks"]):
            st.checkbox(text, key=f"check_{stage}_{index}", persist_state="session")
    return visits_slot


def render_visits(stage: int, slot):
    """5·8단계: 마지막 실행에서 실제로 방문한 노드 순서. 실행이 끝난 뒤 채운다."""
    runs = stage_runs(stage)
    visits = [event["name"].removeprefix("노드: ") for event in (runs[-1]["trace"] if runs else [])
              if event["name"].startswith("노드: ")]
    with slot.container():
        st.markdown("**방문 순서** (마지막 실행)")
        st.code(" → ".join(["START", *visits, "END"]) if visits else "질문을 실행하면 표시됩니다.", language=None)
        st.caption("그림은 실행에 쓰는 그래프의 draw_mermaid() 결과입니다.")


def describe(event: dict) -> str:
    name, data = event["name"], event.get("data")
    if name == "도구 호출 요청":
        return f"도구 호출 요청 · `{data['name']}({json.dumps(data['args'], ensure_ascii=False)})`"
    if name == "도구 실행 결과":
        result = data["result"]
        outcome = "성공" if result.get("ok") else f"실패 · {result.get('message', '')}"
        return f"도구 실행 결과 · `{data['name']}` → {outcome} · 근거 {len(result.get('sources', []))}개"
    if isinstance(data, dict) and data.get("queries"):
        return f"{name} · " + " / ".join(f"`{q}`" for q in data["queries"])
    if isinstance(data, dict) and "kept_pages" in data:
        return f"{name} · 남긴 근거 PDF {', '.join(map(str, data['kept_pages'])) or '없음'}쪽"
    if isinstance(data, dict) and "count" in data:
        return f"{name} · {data['count']}개"
    if isinstance(data, dict) and "history" in data:
        return f"{name} · {len(data['history']) // 2}턴"
    if isinstance(data, dict) and data.get("pages"):
        return f"{name} · PDF {', '.join(map(str, data['pages']))}쪽"
    if name.startswith("노드: ") and isinstance(data, dict) and data.get("tool_calls"):
        return f"{name} → 도구 요청: {', '.join(data['tool_calls'])}"
    return name


def render_trace(run: dict | None):
    if not run:
        st.caption("질문을 실행하면 입력부터 답변까지의 과정이 기록됩니다.")
        return
    metrics = run["metrics"]
    with st.container(horizontal=True):
        st.metric("응답 시간", f"{metrics['seconds']:.1f}초" if metrics.get("seconds") is not None else "-", border=True)
        st.metric("LLM 호출", metrics.get("llm_calls", "-"), border=True)
        st.metric("근거", len(run["sources"]), border=True)
    if run["mode"] == REPLAY:
        st.caption("녹화 당시의 시간과 호출 수입니다.")
    for index, event in enumerate(run["trace"], start=1):
        st.markdown(f"**{index}.** {describe(event)}")
        st.json(event.get("data", {}), expanded=False)


def render_sources(run: dict | None):
    if not run or not run["sources"]:
        st.caption("이 실행에서 모은 근거가 없습니다.")
        return
    for source in run["sources"]:
        if source.get("page") is not None:
            st.markdown(f"**PDF {source['page']}쪽**" + (f" · 청크 {source['chunk_id']}" if source.get("chunk_id") else ""))
        else:
            st.markdown(f"**{source.get('source', '출처')}**" + (f" · [원문]({source['url']})" if source.get("url") else ""))
        if source.get("text"):
            st.text(source["text"])
    st.caption("보험 근거는 2024년 제공 문서 기준입니다. 답변의 쪽번호를 위 근거와 대조하세요.")


def render_settings(stage: int):
    replay = st.session_state.mode == REPLAY
    if stage == 1:
        st.caption("1단계는 설정 없이 질문만 보냅니다.")
        return
    if replay:
        st.caption("녹화 재생에서는 녹화 당시 설정으로 고정됩니다. OpenAI·사내 실행에서 바꿔 보세요.")
    if stage in RAG_STAGES:
        with st.container(horizontal=True):
            st.slider("검색 청크 수 (top_k)", 1, 6, key="top_k", persist_state="session", disabled=replay)
            st.select_slider("청크 크기 (글자 수)", options=[300, 600, 1000], key="chunk_size",
                             persist_state="session", disabled=replay)
    if stage >= 3:
        with st.container(horizontal=True, vertical_alignment="bottom"):
            st.text_input("역할", key="role", persist_state="session", disabled=replay)
            st.segmented_control("답변 형식", ANSWER_STYLES, key="style", required=True,
                                 persist_state="session", disabled=replay)
    st.caption("다음 질문부터 적용됩니다." + (" 청크 크기를 바꾸면 문서 인덱스를 새로 만듭니다." if stage in RAG_STAGES else ""))


def render_deep(stage: int):
    runs = stage_runs(stage)
    run = runs[-1] if runs else None
    st.markdown("**:material/expand_more: 심화** · 필요할 때 펼쳐 보세요")
    with st.expander("실행 기록 · 입력부터 답변까지", icon=":material/timeline:"):
        render_trace(run)
    with st.expander("근거 원문", icon=":material/description:"):
        render_sources(run)
    with st.expander("이 앱의 실제 실행 코드", icon=":material/terminal:"):
        st.code(inspect.getsource(STAGE_RUNNERS[stage]), language="python")
        if stage in GRAPH_STAGES:
            builder = graphs.build_basic_graph if stage == 5 else graphs.build_advanced_graph
            st.code(inspect.getsource(builder), language="python")
    with st.expander("설정 · 청크와 검색 수", icon=":material/tune:"):
        render_settings(stage)
    with st.expander("더 알아보기", icon=":material/school:"):
        st.markdown(STAGES[stage]["notes"])


def render_stage(stage: int):
    header(stage)
    left, right = st.columns([3, 2], gap="large")
    with right:
        visits_slot = render_core(stage)
    with left:
        render_try(stage)
    if visits_slot is not None:
        render_visits(stage, visits_slot)
    st.divider()
    render_deep(stage)


# ── 7단계: 비교 ───────────────────────────────────────────────────────────────

def render_compare():
    stage = 9
    header(stage)
    mode_notice()
    asked = [run["question"] for run in stage_runs(with_compare=True)]
    questions = list(dict.fromkeys([COMMON_QUESTION, *asked]))
    question = st.selectbox("비교할 질문", questions, key="compare_question")
    latest = {run["stage"]: run for run in stage_runs(with_compare=True) if run["question"] == question and run["stage"] in RUN_STAGES}
    todo = [s for s in RUN_STAGES if s not in latest]
    if todo:
        replayable = st.session_state.mode != REPLAY or question == COMMON_QUESTION
        if st.button(f"실행하지 않은 {len(todo)}개 단계를 한 번에 실행", icon=":material/play_arrow:",
                     type="primary", disabled=not replayable):
            with st.status("단계별로 실행 중", expanded=True) as status:
                for s in todo:
                    status.update(label=f"{s}. {STAGES[s]['name']} 실행 중")
                    latest[s] = execute_quietly(s, question, options(s))
                    st.caption(f"{s}. {STAGES[s]['name']} · {'실패' if latest[s].get('error') else '완료'}")
                status.update(label="실행 완료", state="complete", expanded=False)
        if not replayable:
            st.caption("녹화 재생에서는 공통 질문만 한 번에 실행할 수 있습니다.")
    if not latest:
        st.info("위 버튼을 누르거나 1~8단계에서 같은 질문을 실행하면 여기에 나란히 표시됩니다.")
        return
    rows = [{"단계": f"{s}. {STAGES[s]['name']}", "LLM 호출": run["metrics"].get("llm_calls"),
             "시간(초)": run["metrics"].get("seconds"), "읽거나 찾은 근거": ", ".join(source_labels(run)) or "-",
             "상태": run.get("error", "완료")} for s, run in sorted(latest.items())]
    st.dataframe(rows, hide_index=True)
    ordered = sorted(latest.items())
    for start in range(0, len(ordered), 3):
        for column, (s, run) in zip(st.columns(3), ordered[start:start + 3]):
            with column.container(border=True, height=360):
                st.markdown(f"**{s}. {STAGES[s]['name']}**")
                st.markdown(tame(run["answer"]) or "_답변 없음_")
                render_extras(run)
    st.divider()
    st.markdown("**:material/smart_toy: 내 앱 검토하기**")
    for index, text in enumerate(STAGES[stage]["checks"]):
        st.checkbox(text, key=f"check_{stage}_{index}", persist_state="session")
    st.text_area("내 앱에서 실패한 기준과, CodeMate에 다시 줄 지시", key="retry_instruction",
                 persist_state="session", placeholder="예) 2단계 답변에 쪽번호가 없다 → context를 만들 때 각 청크 앞에 [PDF N쪽]을 붙이라고 다시 지시")
