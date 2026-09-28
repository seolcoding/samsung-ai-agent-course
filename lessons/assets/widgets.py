"""교안 노트북에서 쓰는 HTML 위젯 모음.

모든 함수는 IPython.display.HTML을 돌려준다. 코드 셀의 마지막 줄에 두면 출력 영역에 그려진다.
규칙은 lessons/AGENTS.md를 따른다: 외부 CDN 없음, 이미지·스크립트는 HTML 안에 넣음, 위젯마다 고유 id.

    show_slides      원본 PDF에서 원하는 쪽만 뷰어로 보기 (PDF.js, 글자 선택 가능)
    slide_setup      PDF.js를 화면에 불러오기 (노트북 맨 위 준비 셀)
    show_trace       도구 호출 루프의 메시지 흐름을 한 단계씩 보기
    show_graph_run   LangGraph 그래프 구조와 실제 실행 순서를 한 단계씩 보기
    show_code_map    원본 코드를 구획별로 나눠 설명·슬라이드와 함께 보기
    show_checklist   리뷰 체크리스트
    show_scorecard   검증 규칙 통과 여부를 회차별로 비교
    show_order_quiz  순서 맞추기 퀴즈
    show_line_pick   코드에서 틀린 줄 찾기 퀴즈
    run_step         원본 파일의 한 구간을 보여 주고 그대로 실행 (일부를 접어 둘 수 있음)
    show_code        원본 파일의 한 구간을 실행하지 않고 보여 주기
"""

import html
import json
import uuid
from pathlib import Path

from IPython.display import HTML

ASSETS = Path(__file__).resolve().parent
SLIDES = ASSETS / "slides"

# 프로젝터 뒷자리에서도 보이도록 글자를 크게 하고, 에디터 테마와 무관하게 밝은 바탕을 쓴다.
BOX = ("font-family:sans-serif;font-size:15px;line-height:1.5;color:#1f2328;background:#fff;"
       "border:1px solid #d0d7de;border-radius:8px;padding:12px;max-width:960px")
# 색은 교안 슬라이드(Marp PDF)에서 뽑았다: 제목 남색, 강조 파랑, 본문 먹색.
NAVY, BLUE, INK = "#2a3f8c", "#446af3", "#172033"
GRAY, LINE, PALE = "#eef1f8", "#d9deec", "#f5f7fc"
GREEN, RED = "#1a7f37", "#c0392b"

# jupyterquiz 색을 슬라이드 색에 맞춘다. show_quiz가 이 값을 쓴다.
QUIZ_COLORS = {
    "--jq-multiple-choice-bg": NAVY, "--jq-many-choice-bg": NAVY, "--jq-numeric-bg": NAVY, "--jq-string-bg": NAVY,
    "--jq-mc-button-bg": PALE, "--jq-mc-button-border": LINE, "--jq-mc-button-inset-shadow": BLUE,
    "--jq-numeric-input-bg": PALE, "--jq-numeric-input-label": INK, "--jq-numeric-input-shadow": LINE,
    "--jq-correct-color": GREEN, "--jq-incorrect-color": RED, "--jq-text-color": "#ffffff", "--jq-link-color": "#c9d4ff",
}
# 퀴즈 제목 띠. jupyterquiz 문제 칸과 같은 모양으로 맞춘다.
QUIZ_TITLE = f"background:{NAVY};color:#fff;border-radius:8px;padding:10px 14px;font-size:17px;font-weight:600"
BTN = f"font-size:14px;padding:4px 12px;border:1px solid {LINE};border-radius:6px;background:{PALE};color:{INK};cursor:pointer"


# 선택지 칸은 모두 같은 크기로 두고, 글이 넘치면 글자만 줄인다(최소 12px).
_QUIZ_FIT = """
<style>
.Quiz .Answer{grid-auto-rows:76px}
.Quiz .MCButton{height:76px;box-sizing:border-box;overflow:hidden;line-height:1.3;font-size:17px;color:#172033}
</style>
<script>
(() => {
  if (window.__jqFit) return;
  window.__jqFit = true;
  const fit = () => document.querySelectorAll(".Quiz .MCButton:not([data-fit])").forEach(b => {
    if (!b.clientHeight) return;
    let size = 17;
    b.style.fontSize = size + "px";
    while ((b.scrollHeight > b.clientHeight || b.scrollWidth > b.clientWidth) && size > 12) {
      size -= 1; b.style.fontSize = size + "px";
    }
    b.dataset.fit = "1";
  });
  setInterval(fit, 300);
})();
</script>
"""


def show_quiz(path):
    """jupyterquiz 문제 파일을 슬라이드 색으로 보여 준다. 선택지 칸은 모두 같은 크기다."""
    from IPython.display import display
    from jupyterquiz import display_quiz

    display(HTML(_QUIZ_FIT))
    return display_quiz(path, max_width=800, colors=QUIZ_COLORS)


def _id():
    return "w" + uuid.uuid4().hex[:8]


def _js(value):
    """Python 값을 <script> 안에 안전하게 넣을 JSON 문자열로 바꾼다."""
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def _load_deck(deck):
    path = SLIDES / f"{deck}.json"
    if not path.exists():
        raise FileNotFoundError(f"슬라이드 묶음이 없다: {path}. build_slide_deck.py로 먼저 만든다.")
    return json.loads(path.read_text(encoding="utf-8"))


def _plain(value):
    """State 값(메시지 객체 포함)을 화면에 보여 줄 수 있는 JSON 값으로 바꾼다."""
    if hasattr(value, "content") and hasattr(value, "type"):
        text = f"[{type(value).__name__}] {value.content}"
        calls = getattr(value, "tool_calls", None)
        return text + (f" tool_calls={calls}" if calls else "")
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


# ── 슬라이드 ─────────────────────────────────────────────────────────────────

# 슬라이드는 원본 PDF를 PDF.js로 그대로 그린다(벡터라 선명하고, 글자를 선택·복사할 수 있다).
# PDF.js는 사내망 규칙대로 assets/vendor에 두고 HTML 안에 넣는다. 외부 주소는 쓰지 않는다.
PDFJS = ASSETS / "vendor" / "pdfjs-3.11.174"
DOCS_RAW = ASSETS.parent.parent / "docs" / "raw"
_PDF_SENT = {"lib": False, "decks": set()}  # 이 커널에서 화면에 이미 보낸 것

_TEXT_LAYER_CSS = """
.pdfslide .textLayer{position:absolute;inset:0;overflow:hidden;opacity:.25;line-height:1;text-align:initial;
  -webkit-text-size-adjust:none;text-size-adjust:none;forced-color-adjust:none;transform-origin:0 0;z-index:2}
.pdfslide .textLayer :is(span,br){color:transparent;position:absolute;white-space:pre;cursor:text;transform-origin:0% 0%}
.pdfslide .textLayer span.markedContent{top:0;height:0}
.pdfslide .textLayer ::selection{background:#446af3}
"""


def _deck_pdf(deck):
    """"1-2"처럼 쓴 이름으로 docs/raw 아래의 원본 PDF(1-2-*.pdf)를 찾는다. 없으면 None."""
    hits = sorted(DOCS_RAW.rglob(f"{deck}-*.pdf"))
    return hits[0] if hits else None


def slide_setup():
    """PDF.js를 화면에 한 번 불러온다. 노트북 맨 위 준비 셀에서 부른다.

    show_slides도 처음 한 번은 스스로 불러오므로 꼭 필요하지는 않다.
    노트북을 다시 열어 슬라이드가 비어 보이면 이 셀을 다시 실행한다.
    """
    _PDF_SENT["lib"] = False
    _PDF_SENT["decks"].clear()
    return HTML(_pdfjs_loader())


def _pdfjs_loader():
    _PDF_SENT["lib"] = True
    lib = (PDFJS / "pdf.min.js").read_text(encoding="utf-8")
    worker = (PDFJS / "pdf.worker.min.js").read_text(encoding="utf-8")
    return (f"<style>{_TEXT_LAYER_CSS}</style>"
            # Jupyter 화면에 require.js(AMD)가 있으면 PDF.js가 전역 pdfjsLib 대신 AMD 모듈로 등록된다. 잠시 숨긴다.
            "<script>window.__amdDefine = window.define; window.define = undefined;</script>"
            f"<script>{lib}</script>"
            "<script>window.define = window.__amdDefine;</script>"
            "<script>(() => {"
            f"const code = {_js(worker)};"
            "window.pdfjsLib.GlobalWorkerOptions.workerSrc = URL.createObjectURL(new Blob([code], {type: 'text/javascript'}));"
            "window.__pdfDecks = window.__pdfDecks || {}; window.__pdfDocs = window.__pdfDocs || {};"
            "})();</script>")


def show_slides(deck, pages=None):
    """원본 PDF에서 pages 쪽만 뷰어로 보여 준다. 쪽 번호는 1부터.

    PDF가 없는 묶음(예: 커리큘럼 PPTX)은 예전처럼 이미지 묶음(assets/slides/<deck>.json)으로 보여 준다.
    """
    pdf = _deck_pdf(deck)
    if pdf is None:
        return _show_slide_images(deck, pages)
    import subprocess
    total = int(next(l.split()[-1] for l in subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout.splitlines() if l.startswith("Pages:")))
    pages = list(pages or range(1, total + 1))
    bad = [p for p in pages if not 1 <= p <= total]
    if bad:
        raise ValueError(f"{deck}에 없는 쪽: {bad} (전체 {total}쪽)")

    head = "" if _PDF_SENT["lib"] else _pdfjs_loader()
    if deck not in _PDF_SENT["decks"]:
        import base64
        data = base64.b64encode(pdf.read_bytes()).decode("ascii")
        head += f"<script>(window.__pdfDecks = window.__pdfDecks || {{}})[{_js(deck)}] = {_js(data)};</script>"
        _PDF_SENT["decks"].add(deck)

    wid = _id()
    btn = "font-size:14px;padding:2px 10px;border:1px solid #d0d7de;border-radius:6px;background:#f6f8fa;cursor:pointer"
    return HTML(head + f"""
<div id="{wid}" class="pdfslide" style="{BOX};max-width:980px" tabindex="0">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
    <b style="flex:1">{html.escape(pdf.name)}</b>
    <button data-role="prev" style="{btn}">◀ 이전</button>
    <span data-role="label" style="min-width:90px;text-align:center"></span>
    <button data-role="next" style="{btn}">다음 ▶</button>
  </div>
  <div data-role="page" style="position:relative;margin:0 auto;box-shadow:0 1px 4px rgba(0,0,0,.2)">
    <canvas data-role="canvas" style="display:block"></canvas>
    <div data-role="text" class="textLayer"></div>
  </div>
  <div data-role="msg" style="color:#cf222e"></div>
</div>
<script>(() => {{
  const root = document.getElementById({_js(wid)});
  const q = r => root.querySelector(`[data-role="${{r}}"]`);
  const pages = {_js(pages)}, deck = {_js(deck)};
  let i = 0, tries = 0;
  const b64 = s => {{ const b = atob(s); const u = new Uint8Array(b.length); for (let k = 0; k < b.length; k++) u[k] = b.charCodeAt(k); return u; }};
  async function draw() {{
    q("label").textContent = `p${{pages[i]}} (${{i + 1}} / ${{pages.length}})`;
    const doc = await (window.__pdfDocs[deck] = window.__pdfDocs[deck] ||
      window.pdfjsLib.getDocument({{data: b64(window.__pdfDecks[deck])}}).promise);
    const page = await doc.getPage(pages[i]);
    const width = Math.min(root.clientWidth - 26, 960);
    const vp = page.getViewport({{scale: width / page.getViewport({{scale: 1}}).width}});
    const ratio = window.devicePixelRatio || 1, canvas = q("canvas");
    canvas.width = Math.floor(vp.width * ratio); canvas.height = Math.floor(vp.height * ratio);
    canvas.style.width = vp.width + "px"; canvas.style.height = vp.height + "px";
    q("page").style.width = vp.width + "px"; q("page").style.height = vp.height + "px";
    await page.render({{canvasContext: canvas.getContext("2d"), viewport: vp, transform: ratio !== 1 ? [ratio, 0, 0, ratio, 0, 0] : null}}).promise;
    const text = q("text"); text.innerHTML = ""; text.style.setProperty("--scale-factor", vp.scale);
    await window.pdfjsLib.renderTextLayer({{textContentSource: page.streamTextContent(), container: text, viewport: vp}}).promise;
  }}
  function start() {{
    if (!window.pdfjsLib || !(window.__pdfDecks || {{}})[deck]) {{
      if (++tries > 50) {{ q("msg").textContent = "슬라이드 도구가 아직 불러와지지 않았습니다. 맨 위 준비 셀을 다시 실행해 주세요."; return; }}
      return setTimeout(start, 100);
    }}
    draw().catch(e => q("msg").textContent = "슬라이드를 그리지 못했습니다: " + e);
  }}
  const ready = () => window.pdfjsLib && (window.__pdfDecks || {{}})[deck];
  q("prev").onclick = () => {{ if (ready() && i > 0) {{ i--; draw(); }} }};
  q("next").onclick = () => {{ if (ready() && i < pages.length - 1) {{ i++; draw(); }} }};
  root.addEventListener("keydown", e => {{ if (e.key === "ArrowLeft") q("prev").click(); if (e.key === "ArrowRight") q("next").click(); }});
  start();
}})();</script>""")


def _show_slide_images(deck, pages=None):
    """이미지 묶음(assets/slides/<deck>.json)에서 pages 쪽만 뷰어로 보여 준다. PDF가 없는 자료용."""
    data = _load_deck(deck)
    total = len(data["images"])
    pages = list(pages or range(1, total + 1))
    bad = [p for p in pages if not 1 <= p <= total]
    if bad:
        raise ValueError(f"{deck}에 없는 쪽: {bad} (전체 {total}쪽)")
    template = (ASSETS / "slide_viewer_template.html").read_text(encoding="utf-8")
    return HTML(template
                .replace("__VIEWER_ID__", _id())
                .replace("__TITLE__", html.escape(data["source"]))
                .replace("__PAGES__", _js(pages))
                .replace("__IMAGES__", _js([data["images"][p - 1] for p in pages])))


# ── 도구 호출 흐름 ───────────────────────────────────────────────────────────

def show_trace(messages):
    """메시지 목록(Human → AI(tool_calls) → Tool → AI)을 카드로 그리고 한 단계씩 넘겨 본다."""
    rows = []
    for m in messages:
        kind = type(m).__name__
        calls = [{"name": c["name"], "args": c["args"], "id": c["id"]} for c in getattr(m, "tool_calls", None) or []]
        if kind == "HumanMessage":
            label = "사용자 요청"
        elif kind == "ToolMessage":
            label = "도구 실행 결과 (앱이 실행하고 모델에 돌려줌)"
        elif calls:
            label = "모델: 도구와 인자를 고름 (실행은 하지 않음)"
        else:
            label = "모델: 최종 답변"
        rows.append({"kind": kind, "label": label, "content": str(m.content or ""), "calls": calls,
                     "call_id": getattr(m, "tool_call_id", None)})
    wid = _id()
    return HTML(f"""
<div id="{wid}" style="{BOX}">
  <div style="display:flex;gap:8px;align-items:center;margin-bottom:8px">
    <strong style="flex:1">메시지 흐름</strong>
    <button data-act="next">다음 단계</button><button data-act="all">모두 보기</button>
    <span data-role="pos"></span>
  </div>
  <div data-role="cards"></div>
  <small style="color:#57606a">도구 호출 카드를 클릭하면 같은 id의 결과가 강조된다.</small>
</div>
<script>
(() => {{
  const rows = {_js(rows)};
  const root = document.getElementById("{wid}");
  const box = root.querySelector('[data-role="cards"]');
  const colors = {{HumanMessage: "#fff8c5", AIMessage: "#ddf4ff", ToolMessage: "#dafbe1"}};
  let shown = 1;
  const cards = rows.map((r, i) => {{
    const c = document.createElement("div");
    c.style.cssText = `background:${{colors[r.kind] || "#f6f8fa"}};border-radius:6px;padding:8px;margin:6px 0;white-space:pre-wrap`;
    const head = document.createElement("div");
    head.innerHTML = `<b>${{i + 1}}. ${{r.label}}</b> <span style="color:#57606a">${{r.kind}}</span>`;
    c.appendChild(head);
    if (r.content) {{ const p = document.createElement("div"); p.textContent = r.content; c.appendChild(p); }}
    r.calls.forEach(call => {{
      const t = document.createElement("div");
      t.style.cssText = "font-family:monospace;background:#fff;border:1px solid #d0d7de;border-radius:4px;padding:4px;margin-top:4px;cursor:pointer";
      t.textContent = `${{call.name}}(${{JSON.stringify(call.args, null, 0)}})  id=${{call.id}}`;
      t.onclick = () => cards.forEach((k, j) => k.style.outline = rows[j].call_id === call.id ? "3px solid {GREEN}" : "none");
      c.appendChild(t);
    }});
    if (r.call_id) {{ const s = document.createElement("small"); s.textContent = `tool_call_id=${{r.call_id}}`; c.appendChild(s); }}
    box.appendChild(c);
    return c;
  }});
  const paint = () => {{
    cards.forEach((c, i) => c.style.display = i < shown ? "block" : "none");
    root.querySelector('[data-role="pos"]').textContent = `${{shown}} / ${{rows.length}}`;
  }};
  root.querySelector('[data-act="next"]').onclick = () => {{ shown = Math.min(rows.length, shown + 1); paint(); }};
  root.querySelector('[data-act="all"]').onclick = () => {{ shown = rows.length; paint(); }};
  paint();
}})();
</script>""")


# ── LangGraph 실행 ───────────────────────────────────────────────────────────

def _layout(node_ids, edges):
    """START에서의 거리로 층을 정하고, 층마다 가로로 나란히 놓는다. 반환: {id: (x, y)}."""
    layer = {"__start__": 0}
    queue = ["__start__"]
    while queue:
        s = queue.pop(0)
        for e in edges:
            if e["s"] == s and e["t"] not in layer:
                layer[e["t"]] = layer[s] + 1
                queue.append(e["t"])
    # END는 항상 맨 아래 층에 둔다.
    layer.pop("__end__", None)
    last = max(layer.values(), default=0) + 1
    for n in node_ids:
        layer.setdefault(n, last)
    rows = {}
    for n in node_ids:
        rows.setdefault(layer[n], []).append(n)
    pos = {}
    for depth, names in rows.items():
        for k, n in enumerate(names):
            pos[n] = (int(620 * (k + 1) / (len(names) + 1)), 40 + depth * 90)
    return pos


def show_graph_run(app, inputs, config=None):
    """그래프 구조를 그리고, app.stream으로 실제 실행한 순서대로 노드와 State 변화를 넘겨 본다."""
    graph = app.get_graph()
    node_ids = list(graph.nodes)
    edges = [{"s": e.source, "t": e.target, "c": bool(e.conditional)} for e in graph.edges]
    pos = _layout(node_ids, edges)

    steps = [{"node": "__start__", "update": _plain(inputs)}]
    for chunk in app.stream(inputs, config=config, stream_mode="updates"):
        for node, update in chunk.items():
            steps.append({"node": node, "update": _plain(update)})
    steps.append({"node": "__end__", "update": None})

    wid = _id()
    height = max(y for _, y in pos.values()) + 50
    return HTML(f"""
<div id="{wid}" style="{BOX}">
  <div style="display:flex;gap:8px;align-items:center;margin-bottom:6px">
    <strong style="flex:1">그래프 실행 따라가기</strong>
    <button data-act="prev">◀ 이전</button><span data-role="pos"></span><button data-act="next">다음 ▶</button>
  </div>
  <div style="display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px">
    <svg viewBox="0 0 620 {height}" style="width:100%" data-role="svg"></svg>
    <div><div data-role="title" style="font-weight:bold"></div>
      <pre data-role="update" style="white-space:pre-wrap;background:#f6f8fa;border-radius:6px;padding:8px;font-size:13px"></pre></div>
  </div>
  <small style="color:#57606a">점선 = 조건부 엣지. 파란 노드 = 지금 실행된 노드, 초록 테두리 = 이미 지나온 노드.</small>
</div>
<script>
(() => {{
  const pos = {_js(pos)}, edges = {_js(edges)}, steps = {_js(steps)};
  const root = document.getElementById("{wid}");
  const svg = root.querySelector('[data-role="svg"]');
  const NS = "http://www.w3.org/2000/svg", W = 170, H = 40;
  const el = (tag, attrs, parent) => {{
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    (parent || svg).appendChild(e); return e;
  }};
  const defs = el("defs", {{}});
  const marker = el("marker", {{id: "{wid}-arr", viewBox: "0 0 10 10", refX: 10, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto"}}, defs);
  el("path", {{d: "M0,0 L10,5 L0,10 z", fill: "#57606a"}}, marker);
  edges.forEach(e => {{
    const [x1, y1] = pos[e.s], [x2, y2] = pos[e.t];
    const d = y2 > y1 ? `M${{x1}},${{y1 + H / 2}} L${{x2}},${{y2 - H / 2}}`
                      : `M${{x1 + W / 2}},${{y1}} C${{x1 + W}},${{y1}} ${{x2 + W}},${{y2}} ${{x2 + W / 2}},${{y2}}`;
    el("path", {{d, fill: "none", stroke: "#57606a", "stroke-dasharray": e.c ? "5" : "", "marker-end": "url(#{wid}-arr)"}});
  }});
  const boxes = {{}};
  for (const [name, [x, y]] of Object.entries(pos)) {{
    const g = el("g", {{}});
    const r = el("rect", {{x: x - W / 2, y: y - H / 2, width: W, height: H, rx: 8, fill: "{GRAY}", stroke: "#d0d7de", "stroke-width": 2}}, g);
    const t = el("text", {{x, y: y + 5, "text-anchor": "middle", "font-size": 16, fill: "#1f2328"}}, g);
    t.textContent = name;
    boxes[name] = [r, t];
  }}
  let i = 0;
  const show = (n) => {{
    i = Math.max(0, Math.min(steps.length - 1, n));
    const seen = new Set(steps.slice(0, i).map(s => s.node));
    for (const [name, [r, t]] of Object.entries(boxes)) {{
      const now = name === steps[i].node;
      r.setAttribute("fill", now ? "{BLUE}" : "{GRAY}");
      r.setAttribute("stroke", seen.has(name) && !now ? "{GREEN}" : "#d0d7de");
      t.setAttribute("fill", now ? "#fff" : "#1f2328");
    }}
    const s = steps[i];
    root.querySelector('[data-role="pos"]').textContent = `${{i + 1}} / ${{steps.length}}`;
    root.querySelector('[data-role="title"]').textContent =
      s.node === "__start__" ? "입력 State" : s.node === "__end__" ? "실행 끝" : `노드 ${{s.node}}가 State에 쓴 값`;
    root.querySelector('[data-role="update"]').textContent = s.update === null ? "" : JSON.stringify(s.update, null, 2);
  }};
  root.querySelector('[data-act="prev"]').onclick = () => show(i - 1);
  root.querySelector('[data-act="next"]').onclick = () => show(i + 1);
  show(0);
}})();
</script>""")


# ── 코드 지도 ────────────────────────────────────────────────────────────────

def show_code_map(path, sections, deck=None):
    """원본 코드를 구획으로 나눠 보여 준다.

    sections: [{"title", "marker", "note", "page"(선택)}]. marker는 그 구획이 시작하는 줄에 들어 있는 글자다.
    구획을 클릭하면 설명과 대응 슬라이드 쪽(deck의 page)이 오른쪽에 나온다.
    """
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    # 쪽 이미지는 이미지 묶음이 있을 때만 옆에 보여 준다. PDF 교안은 show_slides로 따로 본다.
    data = _load_deck(deck) if deck and (SLIDES / f"{deck}.json").exists() else None
    starts, cursor = [], 0
    for sec in sections:
        hit = next((k for k in range(cursor, len(lines)) if sec["marker"] in lines[k]), None)
        if hit is None:
            raise ValueError(f"{path}에서 구획 표시를 찾지 못했다: {sec['marker']!r}. 원본이 바뀌었는지 확인한다.")
        starts.append(hit)
        cursor = hit + 1
    parts = []
    for k, sec in enumerate(sections):
        end = starts[k + 1] if k + 1 < len(sections) else len(lines)
        page = sec.get("page")
        parts.append({"title": sec["title"], "note": sec["note"], "start": starts[k], "end": end,
                      "page": page, "image": data["images"][page - 1] if data and page else None})
    wid = _id()
    return HTML(f"""
<div id="{wid}" style="{BOX};max-width:1200px">
  <div data-role="tabs" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px"></div>
  <div style="display:grid;grid-template-columns:minmax(0,3fr) minmax(0,2fr);gap:12px">
    <pre data-role="code" style="margin:0;max-height:560px;overflow:auto;white-space:pre;font-family:Menlo,Consolas,monospace;background:#f6f8fa;border-radius:6px;padding:8px;font-size:14px;position:relative"></pre>
    <div data-role="panel"></div>
  </div>
  <small style="color:#57606a">위 버튼이나 코드 줄을 클릭하면 해당 구획의 설명과 슬라이드가 나온다. 코드는 {html.escape(str(path))}를 그대로 읽은 것이다.</small>
</div>
<script>
(() => {{
  const lines = {_js(lines)}, parts = {_js(parts)};
  const colors = ["#fff8c5", "#ddf4ff", "#dafbe1", "#fbefff", "#ffebe9", "#fff1e5", "#eaeef2"];
  const root = document.getElementById("{wid}");
  const code = root.querySelector('[data-role="code"]'), panel = root.querySelector('[data-role="panel"]');
  const tabs = root.querySelector('[data-role="tabs"]');
  const owner = lines.map((_, n) => parts.findIndex(p => n >= p.start && n < p.end));
  const rows = lines.map((text, n) => {{
    const r = document.createElement("div");
    r.textContent = `${{String(n + 1).padStart(3)}}  ${{text}}`;
    r.style.cursor = "pointer";
    r.onclick = () => owner[n] >= 0 && pick(owner[n]);
    code.appendChild(r); return r;
  }});
  const buttons = parts.map((p, k) => {{
    const b = document.createElement("button");
    b.textContent = `${{k + 1}}. ${{p.title}}`;
    b.style.cssText = `background:${{colors[k % colors.length]}};border:1px solid #d0d7de;border-radius:6px;padding:4px 8px;cursor:pointer`;
    b.onclick = () => pick(k);
    tabs.appendChild(b); return b;
  }});
  const pick = (k) => {{
    const p = parts[k];
    rows.forEach((r, n) => {{
      r.style.background = owner[n] === k ? colors[k % colors.length] : "transparent";
      r.style.opacity = owner[n] === k ? "1" : "0.45";
    }});
    buttons.forEach((b, j) => b.style.outline = j === k ? "2px solid {BLUE}" : "none");
    code.scrollTop = rows[p.start].offsetTop - 8;
    panel.innerHTML = "";
    const h = document.createElement("div"); h.style.fontWeight = "bold"; h.textContent = p.title;
    const n = document.createElement("div"); n.style.whiteSpace = "pre-wrap"; n.style.margin = "6px 0"; n.textContent = p.note;
    panel.append(h, n);
    if (p.image) {{
      const cap = document.createElement("small"); cap.textContent = `대응 슬라이드 p${{p.page}}`;
      const img = document.createElement("img"); img.src = p.image;
      img.style.cssText = "width:100%;border:1px solid #d0d7de;border-radius:6px";
      panel.append(cap, img);
    }}
  }};
  pick(0);
}})();
</script>""")


# ── 리뷰·검증 ────────────────────────────────────────────────────────────────

def show_checklist(items, title="리뷰 체크리스트"):
    """체크박스 목록. 체크 상태는 화면에만 있고 저장되지 않는다."""
    wid = _id()
    return HTML(f"""
<div id="{wid}" style="{BOX}">
  <strong>{html.escape(title)}</strong> <span data-role="count"></span>
  <div data-role="items" style="margin-top:6px"></div>
</div>
<script>
(() => {{
  const items = {_js(list(items))};
  const root = document.getElementById("{wid}");
  const box = root.querySelector('[data-role="items"]');
  const count = () => root.querySelector('[data-role="count"]').textContent =
    `(${{box.querySelectorAll("input:checked").length}} / ${{items.length}})`;
  items.forEach(text => {{
    const label = document.createElement("label");
    label.style.cssText = "display:block;margin:4px 0;cursor:pointer";
    const cb = document.createElement("input"); cb.type = "checkbox"; cb.onchange = count;
    label.append(cb, " " + text);
    box.appendChild(label);
  }});
  count();
}})();
</script>""")


def show_scorecard(rounds):
    """검증 결과를 회차별로 나란히 보여 준다.

    rounds: [{"label": "1회차 ...", "checks": [(규칙, 통과여부), ...], "text": 검증한 출력}]
    회차 제목을 클릭하면 그 회차의 출력 전문이 아래에 나온다.
    """
    if not rounds:
        raise ValueError("비교할 회차가 없다. 먼저 검증을 한 번 이상 실행한다.")
    rules = [rule for rule, _ in rounds[0]["checks"]]
    table = [{"label": r["label"], "text": r.get("text", ""), "ok": [ok for _, ok in r["checks"]]} for r in rounds]
    wid = _id()
    return HTML(f"""
<div id="{wid}" style="{BOX}">
  <table style="border-collapse:collapse;width:100%" data-role="table"></table>
  <pre data-role="text" style="white-space:pre-wrap;background:#f6f8fa;border-radius:6px;padding:8px;font-size:13px;display:none;max-height:400px;overflow:auto"></pre>
</div>
<script>
(() => {{
  const rules = {_js(rules)}, rounds = {_js(table)};
  const root = document.getElementById("{wid}");
  const t = root.querySelector('[data-role="table"]'), pre = root.querySelector('[data-role="text"]');
  const cell = (tag, text, css) => {{ const c = document.createElement(tag); c.textContent = text;
    c.style.cssText = "border:1px solid #d0d7de;padding:6px;" + (css || ""); return c; }};
  const head = document.createElement("tr");
  head.appendChild(cell("th", "검증 규칙", "text-align:left"));
  rounds.forEach(r => {{
    const th = cell("th", r.label + " ▾", "cursor:pointer;color:{BLUE}");
    th.onclick = () => {{ pre.style.display = "block"; pre.textContent = `[${{r.label}}]\\n\\n${{r.text}}`; }};
    head.appendChild(th);
  }});
  t.appendChild(head);
  rules.forEach((rule, k) => {{
    const tr = document.createElement("tr");
    tr.appendChild(cell("td", rule));
    rounds.forEach(r => tr.appendChild(cell("td", r.ok[k] ? "✔" : "✖",
      `text-align:center;font-weight:bold;color:${{r.ok[k] ? "{GREEN}" : "#cf222e"}}`)));
    t.appendChild(tr);
  }});
  const sum = document.createElement("tr");
  sum.appendChild(cell("td", "통과", "font-weight:bold"));
  rounds.forEach(r => sum.appendChild(cell("td", `${{r.ok.filter(Boolean).length}} / ${{rules.length}}`, "text-align:center;font-weight:bold")));
  t.appendChild(sum);
}})();
</script>""")


# ── 퀴즈 ─────────────────────────────────────────────────────────────────────

def show_order_quiz(steps, title="순서 맞추기", explanation=""):
    """steps(정답 순서)를 섞어 보여 주고, 클릭한 순서가 맞는지 채점한다."""
    import random

    shuffled = list(steps)
    while len(steps) > 1 and shuffled == list(steps):
        random.shuffle(shuffled)
    wid = _id()
    return HTML(f"""
<div id="{wid}" style="{BOX}">
  <div style="{QUIZ_TITLE}">{html.escape(title)}</div>
  <div style="color:#57606a;margin:8px 0 4px">카드를 올바른 순서대로 클릭합니다. 잘못 눌렀으면 '다시'를 누릅니다.</div>
  <div data-role="pool" style="display:flex;flex-wrap:wrap;gap:6px;margin:8px 0"></div>
  <ol data-role="answer" style="min-height:24px"></ol>
  <button data-act="check" style="{BTN}">채점</button> <button data-act="reset" style="{BTN}">다시</button>
  <div data-role="result" style="margin-top:8px;white-space:pre-wrap"></div>
</div>
<script>
(() => {{
  const steps = {_js(list(steps))}, shuffled = {_js(shuffled)}, explanation = {_js(explanation)};
  const root = document.getElementById("{wid}");
  const pool = root.querySelector('[data-role="pool"]'), answer = root.querySelector('[data-role="answer"]');
  const result = root.querySelector('[data-role="result"]');
  let picked = [];
  const draw = () => {{
    pool.innerHTML = ""; answer.innerHTML = "";
    shuffled.forEach(s => {{
      if (picked.includes(s)) return;
      const b = document.createElement("button");
      b.textContent = s;
      b.style.cssText = "background:{PALE};border:1px solid {LINE};border-left:4px solid {BLUE};border-radius:6px;padding:6px 10px;cursor:pointer;font-size:15px;color:{INK}";
      b.onclick = () => {{ picked.push(s); draw(); }};
      pool.appendChild(b);
    }});
    picked.forEach(s => {{ const li = document.createElement("li"); li.textContent = s; answer.appendChild(li); }});
  }};
  root.querySelector('[data-act="reset"]').onclick = () => {{ picked = []; result.textContent = ""; draw(); }};
  root.querySelector('[data-act="check"]').onclick = () => {{
    if (picked.length < steps.length) {{ result.textContent = "카드를 모두 골라야 채점할 수 있습니다."; return; }}
    [...answer.children].forEach((li, k) => {{
      const ok = picked[k] === steps[k];
      li.style.color = ok ? "{GREEN}" : "{RED}";
      li.textContent = picked[k] + (ok ? "  ✔" : `  ✖ (정답: ${{steps[k]}})`);
    }});
    const allOk = picked.every((s, k) => s === steps[k]);
    result.textContent = (allOk ? "정답입니다. " : "틀린 칸이 있습니다. ") + explanation;
  }};
  draw();
}})();
</script>""")


def show_line_pick(code, answer_lines, title="틀린 줄 찾기", explanation=""):
    """코드를 줄 번호와 함께 보여 주고, 클릭한 줄이 answer_lines(1부터)에 들어 있는지 알려 준다."""
    lines = code.strip("\n").splitlines()
    wid = _id()
    return HTML(f"""
<div id="{wid}" style="{BOX}">
  <div style="{QUIZ_TITLE}">{html.escape(title)}</div>
  <div style="color:#57606a;margin:8px 0 4px">문제가 있다고 생각하는 줄을 클릭합니다.</div>
  <pre data-role="code" style="margin:0;white-space:pre;overflow-x:auto;font-family:Menlo,Consolas,monospace;background:#f6f8fa;border-radius:6px;padding:8px;font-size:14px"></pre>
  <div data-role="result" style="margin-top:8px;white-space:pre-wrap"></div>
</div>
<script>
(() => {{
  const lines = {_js(lines)}, answers = {_js(list(answer_lines))}, explanation = {_js(explanation)};
  const root = document.getElementById("{wid}");
  const code = root.querySelector('[data-role="code"]'), result = root.querySelector('[data-role="result"]');
  lines.forEach((text, k) => {{
    const row = document.createElement("div");
    row.textContent = `${{String(k + 1).padStart(3)}}  ${{text}}`;
    row.style.cursor = "pointer";
    row.onclick = () => {{
      const ok = answers.includes(k + 1);
      row.style.background = ok ? "#dafbe1" : "#ffebe9";
      result.style.color = ok ? "{GREEN}" : "{RED}";
      result.textContent = ok ? `${{k + 1}}번 줄, 정답이다. ${{explanation}}` : `${{k + 1}}번 줄은 문제가 아니다. 다시 찾아본다.`;
    }};
    code.appendChild(row);
  }});
}})();
</script>""")


# 파일별 실행 이름공간. 같은 파일의 단계들은 변수를 이어서 쓴다.
_STEP_SPACES = {}


def _slice(path, start, end):
    """원본에서 start 표시 줄부터 end 표시 줄 직전까지의 범위(0부터 센 줄 번호)를 찾는다."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()

    def find(marker, begin):
        hit = next((k for k in range(begin, len(lines)) if marker in lines[k]), None)
        if hit is None:
            raise ValueError(f"{Path(path).name}에서 표시를 찾지 못했다: {marker!r}. 원본이 바뀌었는지 확인한다.")
        return hit

    first = 0 if start is None else find(start, 0)
    last = len(lines) if end is None else find(end, first + 1)
    return lines, first, last, find


def _code_box(path, lines, first, last, fold=(), collapsed=None, note="원본 그대로 실행"):
    """코드 구간을 줄 번호와 함께 그린다.

    fold: [(시작 표시, 끝 표시, 이름)] — 이 구간 안의 줄 묶음을 접어서 한 줄로 보여 준다. 끝 표시가 None이면 구간 끝까지.
    collapsed: 문자열이면 코드 전체를 그 이름으로 접는다. 수강생에게는 접힌 제목만 보이고, 누르면 펼쳐진다.
    접기는 화면 표시만 바꾼다. 실행되는 코드는 같다.
    """
    folds = []
    for fs, fe, label in fold:
        a = next(k for k in range(first, last) if fs in lines[k])
        b = last if fe is None else next((k for k in range(a + 1, last) if fe in lines[k]), last)
        folds.append((a, b, label))

    def row(k):
        return (f'<div><span style="color:#8c959f;user-select:none;display:inline-block;width:3em">{k + 1}</span>'
                f"{html.escape(lines[k]) or ' '}</div>")

    summary_style = "cursor:pointer;color:#57606a;font-size:13px"
    parts, k = [], first
    while k < last:
        f = next((x for x in folds if x[0] == k), None)
        if f:
            a, b, label = f
            inner = "".join(row(j) for j in range(a, b))
            parts.append(f'<details><summary style="{summary_style}">{a + 1}–{b}줄 · {html.escape(label)} (접힘, 눌러서 보기)</summary>{inner}</details>')
            k = b
        else:
            parts.append(row(k))
            k += 1
    pre = ('<pre style="margin:0;white-space:pre;overflow:auto;font-family:Menlo,Consolas,monospace;font-size:14px;'
           f'background:#f6f8fa;border-radius:6px;padding:8px">{"".join(parts)}</pre>')
    head = f"{html.escape(Path(path).name)} {first + 1}–{last}줄 ({note})"
    if collapsed:
        body = f'<details><summary style="{summary_style}">{head} · {html.escape(collapsed)} (접힘, 눌러서 보기)</summary>{pre}</details>'
    else:
        body = f'<div style="color:#57606a;font-size:13px;margin-bottom:4px">{head}</div>{pre}'
    return HTML(f'<div style="{BOX};max-width:1200px;padding:8px">{body}</div>')


def show_code(path, start=None, end=None, fold=(), collapsed=None):
    """원본 구간을 실행하지 않고 보여 주기만 한다. 인자는 run_step과 같다."""
    lines, first, last, _ = _slice(Path(path).resolve(), start, end)
    return _code_box(Path(path).resolve(), lines, first, last, fold, collapsed, note="읽기만 함")


def run_step(path, start=None, end=None, fold=(), collapsed=None):
    """원본 파일에서 start 표시가 든 줄부터 end 표시가 든 줄 직전까지를 보여 주고 실행한다.

    start가 None이면 파일 처음부터, end가 None이면 파일 끝까지다. end는 start 뒤에서 찾는다.
    원본은 고치지 않는다. 같은 파일의 단계를 순서대로 모두 실행하면 원본 전체를 한 번 실행한 것과 같다.
    파일 처음(start=None)부터 다시 실행하면 그 파일의 변수를 새로 시작한다.
    fold·collapsed는 화면에서 접어 둘 부분이다(_code_box 참고). 실행에는 영향이 없다.
    """
    from IPython.display import display

    path = Path(path).resolve()
    lines, first, last, _ = _slice(path, start, end)
    if start is None or path not in _STEP_SPACES:
        _STEP_SPACES[path] = {"__name__": "__main__", "__file__": str(path)}
    space = _STEP_SPACES[path]
    display(_code_box(path, lines, first, last, fold, collapsed))
    # 줄 번호가 원본과 같도록 앞을 빈 줄로 채워 컴파일한다. 오류 위치가 원본 줄 번호로 나온다.
    source = "\n" * first + "\n".join(lines[first:last]) + "\n"
    exec(compile(source, str(path), "exec"), space)
    return space
