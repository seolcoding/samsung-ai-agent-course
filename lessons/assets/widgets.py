"""교안 노트북에서 쓰는 HTML 위젯 모음.

모든 함수는 IPython.display.HTML을 돌려준다. 코드 셀의 마지막 줄에 두면 출력 영역에 그려진다.
규칙은 lessons/AGENTS.md를 따른다: 외부 CDN 없음, 이미지·스크립트는 HTML 안에 넣음, 위젯마다 고유 id.

    show_slides      슬라이드 묶음에서 원하는 쪽만 뷰어로 보기
    show_trace       도구 호출 루프의 메시지 흐름을 한 단계씩 보기
    show_graph_run   LangGraph 그래프 구조와 실제 실행 순서를 한 단계씩 보기
    show_code_map    원본 코드를 구획별로 나눠 설명·슬라이드와 함께 보기
    show_checklist   리뷰 체크리스트
    show_scorecard   검증 규칙 통과 여부를 회차별로 비교
    show_order_quiz  순서 맞추기 퀴즈
    show_line_pick   코드에서 틀린 줄 찾기 퀴즈
    run_step         원본 파일의 한 구간을 보여 주고 그대로 실행
"""

import html
import json
import uuid
from pathlib import Path

from IPython.display import HTML

ASSETS = Path(__file__).parent
SLIDES = ASSETS / "slides"

# 프로젝터 뒷자리에서도 보이도록 글자를 크게 하고, 에디터 테마와 무관하게 밝은 바탕을 쓴다.
BOX = ("font-family:sans-serif;font-size:15px;line-height:1.5;color:#1f2328;background:#fff;"
       "border:1px solid #d0d7de;border-radius:8px;padding:12px;max-width:960px")
BLUE, GREEN, GRAY = "#1f6feb", "#1a7f37", "#eaeef2"


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

def show_slides(deck, pages=None):
    """슬라이드 묶음(assets/slides/<deck>.json)에서 pages 쪽만 뷰어로 보여 준다. 쪽 번호는 1부터."""
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
    data = _load_deck(deck) if deck else None
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
  <strong>{html.escape(title)}</strong>
  <div style="color:#57606a;margin:4px 0">카드를 올바른 순서대로 클릭한다. 잘못 눌렀으면 '다시'를 누른다.</div>
  <div data-role="pool" style="display:flex;flex-wrap:wrap;gap:6px;margin:8px 0"></div>
  <ol data-role="answer" style="min-height:24px"></ol>
  <button data-act="check">채점</button> <button data-act="reset">다시</button>
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
      b.style.cssText = "background:{GRAY};border:1px solid #d0d7de;border-radius:6px;padding:6px 10px;cursor:pointer;font-size:15px";
      b.onclick = () => {{ picked.push(s); draw(); }};
      pool.appendChild(b);
    }});
    picked.forEach(s => {{ const li = document.createElement("li"); li.textContent = s; answer.appendChild(li); }});
  }};
  root.querySelector('[data-act="reset"]').onclick = () => {{ picked = []; result.textContent = ""; draw(); }};
  root.querySelector('[data-act="check"]').onclick = () => {{
    if (picked.length < steps.length) {{ result.textContent = "카드를 모두 골라야 채점할 수 있다."; return; }}
    [...answer.children].forEach((li, k) => {{
      const ok = picked[k] === steps[k];
      li.style.color = ok ? "{GREEN}" : "#cf222e";
      li.textContent = picked[k] + (ok ? "  ✔" : `  ✖ (정답: ${{steps[k]}})`);
    }});
    const allOk = picked.every((s, k) => s === steps[k]);
    result.textContent = (allOk ? "정답이다. " : "틀린 칸이 있다. ") + explanation;
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
  <strong>{html.escape(title)}</strong>
  <div style="color:#57606a;margin:4px 0">문제가 있다고 생각하는 줄을 클릭한다.</div>
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
      result.style.color = ok ? "{GREEN}" : "#cf222e";
      result.textContent = ok ? `${{k + 1}}번 줄, 정답이다. ${{explanation}}` : `${{k + 1}}번 줄은 문제가 아니다. 다시 찾아본다.`;
    }};
    code.appendChild(row);
  }});
}})();
</script>""")


# 파일별 실행 이름공간. 같은 파일의 단계들은 변수를 이어서 쓴다.
_STEP_SPACES = {}


def run_step(path, start=None, end=None):
    """원본 파일에서 start 표시가 든 줄부터 end 표시가 든 줄 직전까지를 보여 주고 실행한다.

    start가 None이면 파일 처음부터, end가 None이면 파일 끝까지다. end는 start 뒤에서 찾는다.
    원본은 고치지 않는다. 같은 파일의 단계를 순서대로 모두 실행하면 원본 전체를 한 번 실행한 것과 같다.
    파일 처음(start=None)부터 다시 실행하면 그 파일의 변수를 새로 시작한다.
    """
    from IPython.display import display

    path = Path(path).resolve()
    lines = path.read_text(encoding="utf-8").splitlines()

    def find(marker, begin):
        hit = next((k for k in range(begin, len(lines)) if marker in lines[k]), None)
        if hit is None:
            raise ValueError(f"{path.name}에서 표시를 찾지 못했다: {marker!r}. 원본이 바뀌었는지 확인한다.")
        return hit

    first = 0 if start is None else find(start, 0)
    last = len(lines) if end is None else find(end, first + 1)
    if start is None or path not in _STEP_SPACES:
        _STEP_SPACES[path] = {"__name__": "__main__", "__file__": str(path)}
    space = _STEP_SPACES[path]

    rows = "".join(
        f'<div><span style="color:#8c959f;user-select:none;display:inline-block;width:3em">{k + 1}</span>'
        f"{html.escape(lines[k]) or ' '}</div>"
        for k in range(first, last)
    )
    display(HTML(
        f'<div style="{BOX};max-width:1200px;padding:8px">'
        f'<div style="color:#57606a;font-size:13px;margin-bottom:4px">{html.escape(path.name)} {first + 1}–{last}줄 (원본 그대로 실행)</div>'
        f'<pre style="margin:0;white-space:pre;overflow:auto;font-family:Menlo,Consolas,monospace;font-size:14px;'
        f'background:#f6f8fa;border-radius:6px;padding:8px">{rows}</pre></div>'
    ))
    # 줄 번호가 원본과 같도록 앞을 빈 줄로 채워 컴파일한다. 오류 위치가 원본 줄 번호로 나온다.
    source = "\n" * first + "\n".join(lines[first:last]) + "\n"
    exec(compile(source, str(path), "exec"), space)
    return space

