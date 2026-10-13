"""데모 F(객관식 코드 채우기)에서 쓰는 도우미.

    try_option        고른 보기(A~D)를 실행하고 🟢/⛔와 해설을 보여 주기
    compare_options   보기 네 개를 같은 입력에 모두 돌려 결과를 표로 비교하기
    interrupt_picker  라디오 버튼으로 보기를 고르면 바로 그 설정으로 그래프 실행하기
    pick              고른 보기의 코드를 바로 아래 새 셀로 만들어 주기
"""

import html
import uuid
from types import SimpleNamespace

from IPython import get_ipython
from IPython.display import HTML, display

GREEN, RED, INK = "#1a7f37", "#c0392b", "#172033"


def _user_ns():
    return get_ipython().user_ns


def _last_line(err):
    return f"{type(err).__name__}: {str(err).splitlines()[0] if str(err) else ''}"


def try_option(choice, options, after=""):
    """options[choice]의 코드를 노트북 변수 공간에서 실행하고 결과를 알려 준다.

    options = {"A": {"code": "...", "ok": True, "why": "..."}, ...}
    after   보기 코드 뒤에 이어서 실행할 확인용 코드(예: 컴파일)
    """
    choice = str(choice).strip().upper()
    if choice not in options:
        print(f"⛔ CHOICE에 {', '.join(options)} 중 하나를 넣고 다시 실행합니다. 지금 값: {choice!r}")
        return
    opt = options[choice]
    print(f"── 고른 보기 {choice} ──\n{opt['code']}\n")
    try:
        exec(opt["code"] + "\n" + after, _user_ns())
    except Exception as err:  # 오류도 보여 주는 것이 목적이다
        print(f"⛔ 실행 오류  {_last_line(err)}")
    else:
        print("🟢 정답입니다." if opt["ok"] else "⛔ 오류는 없지만 정답이 아닙니다.")
    print(f"해설: {opt['why']}")


def compare_options(options, samples, my_choice=None):
    """보기마다 같은 줄을 여러 입력(samples)에 돌려 결과가 기대값과 맞는지 표로 보여 준다.

    options = {"A": 'lang = result.content', ...}  ← result.content를 읽어 lang을 정하는 줄
    samples = [("LLM의 답", "기대값"), ...]
    """
    head = "".join(f"<th>{html.escape(t)}</th>" for t, _ in samples)
    rows = []
    for key, line in options.items():
        cells, all_ok = [], True
        for text, want in samples:
            ns = {"result": SimpleNamespace(content=text)}
            try:
                exec(line, ns)
                got = ns.get("lang")
            except Exception as err:
                got = _last_line(err)
            ok = got == want
            all_ok &= ok
            cells.append(f"<td style='color:{GREEN if ok else RED}'>{html.escape(repr(got))} {'✔' if ok else '✖'}</td>")
        mark = " ← 내가 고른 보기" if my_choice and key == str(my_choice).upper() else ""
        verdict = "🟢 모두 맞음" if all_ok else "⛔"
        rows.append(f"<tr><td><b>{key}</b>{mark}<br><code>{html.escape(line)}</code></td>{''.join(cells)}<td>{verdict}</td></tr>")
    expect = "".join(f"<td><i>{html.escape(w)}</i></td>" for _, w in samples)
    display(HTML(f"""
<table style="font-size:14px;color:{INK};background:#fff;border-collapse:collapse" border="1" cellpadding="6">
<tr><th>보기 \\ LLM의 답</th>{head}<th>판정</th></tr>
<tr><td><i>기대값</i></td>{expect}<td></td></tr>
{''.join(rows)}
</table>"""))


def run_interrupt(builder, compile_code, question):
    """compile_code로 컴파일하고 질문 하나를 넣어, 멈춘 위치와 메일 전송 여부를 보여 준다."""
    from langchain_core.messages import HumanMessage
    from langgraph.checkpoint.memory import MemorySaver

    ns = {"builder": builder, "MemorySaver": MemorySaver}
    exec("app = " + compile_code, ns)
    app = ns["app"]
    config = {"configurable": {"thread_id": f"pick-{uuid.uuid4().hex[:8]}"}}
    print(f"── app = {compile_code}")
    app.invoke({"messages": [HumanMessage(content=question)]}, config=config)
    state = app.get_state(config)
    last = state.values["messages"][-1]
    pending = getattr(last, "tool_calls", None) or []
    print(f"다음에 실행할 노드: {list(state.next) or '없음(끝까지 실행됨)'}")
    print(f"대기 중인 도구 호출: {[t['name'] for t in pending] if state.next == ('tools',) else '없음'}")


def interrupt_picker(builder, options, question):
    """보기를 라디오 버튼으로 보여 주고, 고르는 즉시 그 설정으로 실행한다."""
    import ipywidgets as widgets

    radio = widgets.RadioButtons(options=list(options), value=None, layout={"width": "max-content"})
    out = widgets.Output()

    def on_pick(change):
        out.clear_output()
        with out:
            run_interrupt(builder, change["new"], question)
            ok, why = options[change["new"]]
            print("\n🟢 정답입니다. " if ok else "\n⛔ 정답이 아닙니다. ", why, sep="")

    radio.observe(on_pick, names="value")
    display(widgets.VBox([radio, out]))


def pick(choice, options):
    """고른 보기의 코드를 바로 아래 새 코드 셀로 만든다. 그 셀을 실행해 결과를 확인한다."""
    choice = str(choice).strip().upper()
    if choice not in options:
        print(f"⛔ {', '.join(options)} 중 하나를 넣고 다시 실행합니다. 지금 값: {choice!r}")
        return
    get_ipython().set_next_input(f"# 보기 {choice}\n" + options[choice], replace=False)
    print(f"보기 {choice}의 코드를 아래 새 셀로 만들었습니다. 그 셀을 실행합니다.")
