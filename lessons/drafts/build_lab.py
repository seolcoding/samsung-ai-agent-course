"""실습 노트북을 조립한다. 받은 실습 코드(src/raw)를 AI와 함께 채우고 솔루션(src/solution)과 비교한다.

실행(프로젝트 루트):
  uv run python lessons/drafts/build_lab.py 01-llm-api        # 실습 폴더 하나
  uv run python lessons/drafts/build_lab.py                   # labs/*.json 전부
  uv run python lessons/drafts/build_lab.py --scaffold        # 아직 없는 실습 폴더의 뼈대 JSON 만들기

입력: lessons/drafts/labs/<실습 폴더>.json
출력: lessons/Chapter01/<번호>_<이름>_LAB.ipynb (출력 없음)

수강생에게는 노트북만 보인다(.py 실습 파일은 주지 않는다). 그래서 원본 코드를 빌드할 때 셀로 옮겨 넣는다.
정본은 계속 src/raw이고, 원본이 바뀌면 다시 빌드한다.

모든 실습 노트북은 같은 구조다.
  제목 → 목차 → 1. 실습 방법 → 원본 파일마다 한 장:
    준비 코드(접힘) → 구획마다 한 절 → AI에게 물어보기(TODO가 없는 파일) → 정리
구획은 두 종류다.
  예제: 완성된 코드를 함께 실행한다. `# ✍️ CHANGE_HERE:` 주석 바로 아래 줄의 값만 바꿔 다시 실행해 본다.
  과제: 원본 TODO 주석을 `# ✍️ WRITE_HERE:`로 바꾸고, 그 아래 정답 줄을 빈칸(`...  # ✍️ …`)으로 바꿔 넣는다. 수강생이 AI와 채운다.
    [설명 → 프롬프트 힌트(3문장 이내) → 성공 기준(🟢/⛔)] → 빈칸 셀 → 정답 보기(접힘)
지시문 완성본은 주지 않는다. 짧은 프롬프트 힌트와 성공 기준만 주고, 지시는 수강생이 쓴다.
수강생 글에서는 도구 이름(CodeMate) 대신 "AI"라고 쓴다.
성공 기준은 자동으로 검사하지 않는다. 수강생이 실행 결과를 보고 스스로 판단한다.
"""

import ast
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nbkit import Notebook, fmt  # noqa: E402

HERE = Path(__file__).parent
LESSONS = HERE.parent
ROOT = LESSONS.parent
LABS = HERE / "labs"
REF = "../.."  # 노트북(lessons/Chapter01/)에서 프로젝트 루트까지
COMMON = json.loads((HERE / "1-2_cells_common.json").read_text(encoding="utf-8"))

# 실습 폴더 ↔ 교안 번호와 노트북 이름
UNITS = {
    "01-llm-api": ("1-2", "llm_api"),
    "02-langchain": ("1-3", "langchain"),
    "03-rag": ("1-4", "rag"),
    "04-langgraph": ("2-1", "langgraph"),
    "05-multi-agent": ("2-2", "multi_agent"),
    "06-rag-streamlit": ("2-3", "rag_streamlit"),
}

KIND_EXAMPLE, KIND_TASK = "예제", "과제"  # 제목 옆 표시 (예제) (과제)

PROMPT_GUIDE = f"""실습은 두 종류입니다. 제목 옆 표시와 코드 주석으로 구분합니다.

- **{KIND_EXAMPLE}** `# ✍️ CHANGE_HERE:` 바로 아래 줄의 값을 바꿔 다시 실행해 봅니다.
- **{KIND_TASK}** `# ✍️ WRITE_HERE:` 아래 빈칸(`...`)을 AI와 함께 채웁니다. **프롬프트 힌트**를 보고 지시를 직접 씁니다.

실행한 뒤에는 **성공 기준**과 비교해 스스로 판단합니다. 🟢는 되어야 하는 것, ⛔는 다시 해야 하는 신호입니다. 과제는 그다음 접힌 "정답 보기"와 비교합니다."""


BLANK_LINE = "...  # ✍️ 여기를 채웁니다"
MARK_TASK, MARK_EDIT = "# ✍️ WRITE_HERE:", "# ✍️ CHANGE_HERE:"


def _norm(text):
    """따옴표·공백 차이를 무시하고 비교한다(원본을 정돈한 뒤에도 표시 문자열이 맞도록)."""
    return re.sub(r"\s+", "", text.replace("'", '"'))


def _find(lines, marker, begin):
    m = _norm(marker)
    return next((k for k in range(begin, len(lines)) if m in _norm(lines[k])), None)


def _patch(lines, patches):
    """노트북에서만 원본을 손본다(가독성 우선 결정). 원본 파일은 그대로 둔다.

    patches: [{"find": 표시, "until": 끝 표시(포함, 없으면 한 줄), "lines": [바꿔 넣을 줄]}]
    lines가 []이면 그 구간을 지운다. 표시를 못 찾으면 멈춘다(조용히 틀리지 않게).
    """
    for p in patches:
        a = _find(lines, p["find"], 0)
        assert a is not None, f"patch 표시를 찾지 못함: {p['find']!r}"
        e = a if "until" not in p else _find(lines, p["until"], a)
        assert e is not None, f"patch 끝 표시를 찾지 못함: {p['until']!r}"
        lines = lines[:a] + list(p["lines"]) + lines[e + 1:]
    return fmt("\n".join(lines)).splitlines() if patches else lines


def _blank(lines, blanks):
    """blanks 구간을 빈칸 한 줄로 바꾼 줄 목록과, 구간마다 지운 정답 줄(주석 제외)을 돌려준다."""
    out, answers, k, cursor = [], [], 0, 0
    for b in blanks:
        a = _find(lines, b["start"], cursor)
        end = b.get("end")
        e = None if a is None else a + 1 if end is None else len(lines) if end == "EOF" else _find(lines, end, a + 1)
        if e is None:  # 표시 줄을 찾지 못함: 이 빈칸은 건너뛴다(정답 None)
            print(f"✖ 빈칸 범위 없음: {b['start'][:40]!r} | 원본에서 표시 줄을 찾지 못함 | labs/*.json의 blank를 고친다")
            answers.append(None)
            continue
        out += lines[k:a]
        indent = lines[a][: len(lines[a]) - len(lines[a].lstrip())]
        out.append(indent + BLANK_LINE)
        answers.append([ln for ln in lines[a:e] if ln.strip() and not ln.strip().startswith("#")])
        k = cursor = e
    return out + lines[k:], answers


def _chunks(lines, split):
    """split 표시가 든 줄마다 구획을 나눈다. [(제목, 줄 목록)]"""
    cuts, cursor = [0], 0
    for m in split:
        hit = _find(lines, m, cursor + 1 if cuts[-1] else cursor)
        if hit is not None and hit > cuts[-1]:
            cuts.append(hit)
            cursor = hit
    cuts.append(len(lines))
    out = []
    for a, e in zip(cuts, cuts[1:]):
        body = lines[a:e]
        while body and not body[-1].strip():
            body = body[:-1]
        head = body[0].strip() if body else ""
        title = head.strip("# ─").strip() if head.startswith("# ──") else None
        out.append((title, body))
    return out


def _dedent_common(text):
    import textwrap
    return textwrap.dedent(text)


def _criteria_md(checks, fail=(), success=()):
    """성공 기준 글: 통과 조건은 🟢, 다시 해야 하는 신호는 ⛔."""
    return "**성공 기준**\n\n" + "\n".join([f"- 🟢 {x}" for x in [*checks, *success]]
                                          + [f"- ⛔ {x}" for x in fail])


def _mark(lines, edits):
    """과제의 TODO 주석을 `# ✍️ WRITE_HERE:`로 바꾸고, 예제에서 바꿔 볼 줄 바로 위에 같은 들여쓰기로 `# ✍️ CHANGE_HERE:` 줄을 넣는다. 넣은 줄 위치를 돌려준다."""
    out = [ln.replace("# TODO:", MARK_TASK) if "# TODO:" in ln and "✍" not in ln else ln for ln in lines]
    at = []
    for e in edits:
        k = _find(out, e["line"], 0)
        assert k is not None, f"바꿔 볼 줄을 찾지 못함: {e['line']!r}"
        indent = out[k][: len(out[k]) - len(out[k].lstrip())]
        out.insert(k, f"{indent}{MARK_EDIT} {e['todo']}")
        at = [a + (a >= k) for a in at] + [k]
    return out, at


def build(folder):
    spec = json.loads((LABS / f"{folder}.json").read_text(encoding="utf-8"))
    unit, slug = UNITS[folder]
    nb = Notebook(LESSONS / "assets" / "quizzes" / f"{unit}-lab", f"../assets/quizzes/{unit}-lab")

    nb.md(f"# [LAB] {spec['title']}\n\n{spec['intro']}")
    nb.meta(spec.get("intro__meta"))
    nb.code(COMMON["env_check_code"])
    nb.md(COMMON["env_check_look"])

    nb.h(2, "1. 실습 방법")
    nb.md(PROMPT_GUIDE)

    for n, f in enumerate(spec["files"], start=2):
        # 원본을 먼저 정돈한다(읽기 쉽게). 원본·솔루션이 다르면 spec의 source로 깔끔한 쪽을 고른다
        src_dir = ROOT / "src" / f.get("source", "raw") / "Chapter01" / folder
        raw = _patch(fmt((src_dir / f["name"]).read_text(encoding="utf-8")).splitlines(), f.get("patch", []))
        todos = [t for t in f.get("todos", []) if t.get("blank")]  # 빈칸 범위가 없는 TODO(뼈대 미완성)는 건너뛴다
        for t in f.get("todos", []):
            if not t.get("blank"):
                print(f"✖ {folder}/{f['name']} TODO 빈칸 범위 없음 | 뼈대 추정 실패 | labs/{folder}.json의 blank를 채운다")
        lines, answers = _blank(raw, [t["blank"] for t in todos]) if todos else (raw, [])
        todos, answers = [t for t, x in zip(todos, answers) if x is not None], [x for x in answers if x is not None]
        edits = f.get("edits", [])
        lines, edit_at = _mark(lines, edits)
        # WRITE_HERE 주석 줄 위치로 어느 구획에 속하는지 정한다(찾지 못하면 순서대로 WRITE_HERE 줄을 쓴다)
        todo_lines = [k for k, ln in enumerate(lines) if MARK_TASK in ln]
        todo_at = [next((k for k in todo_lines if t["todo"][:12] in lines[k]), todo_lines[min(i, len(todo_lines) - 1)] if todo_lines else 0)
                   for i, t in enumerate(todos)]
        wf = f.get("writefile")  # Streamlit 앱처럼 파일로 띄워야 하는 코드: 한 셀로 묶어 파일로 쓰고 따로 실행한다
        split = [] if wf else f.get("split") or [ln.strip() for ln in lines if ln.startswith("# ──")]
        nb.h(2, f"{n}. {f['title']}")
        nb.md(f["intro"])
        nb.meta(f.get("intro__meta"))
        pos, sub, visible = 0, 0, 0
        for c, (title, body) in enumerate(_chunks(lines, split)):
            start, pos = pos, pos + len(body)
            while pos < len(lines) and not lines[pos].strip():
                pos += 1
            text = "\n".join(body).strip("\n")
            if not text.strip():
                continue
            code_only = "\n".join(ln for ln in body if not ln.strip().startswith("#")).strip()
            if code_only.startswith('"""') and code_only.endswith('"""'):  # 실행되지 않는 참고 코드(문자열)
                notes = "\n".join(ln for ln in body if ln.strip().startswith("#") and not ln.startswith("# ──"))
                ref = code_only.strip('"').strip("\n")
                sub += 1
                nb.h(3, f"{n}.{sub} 참고: {(f.get('titles') or {}).get(title or '', title) or '실행하지 않는 코드'}")
                nb.md("문자열로 감싸 두어 실행되지 않는 참고 코드입니다. 읽어만 봅니다.\n\n```python\n" + (notes + "\n" if notes else "") + ref + "\n```")
                continue
            if wf:
                text = f"%%writefile {wf}\n" + text
            elif c == 0 and f.get("hide_first", True):  # 준비 코드: 불러오기·환경 설정. 접어 둔다
                nb.md(f.get("setup_note", "준비 코드입니다. 필요한 도구를 불러오고 모델을 준비합니다. 접혀 있으니 펼치지 않아도 되고, 실행만 합니다."))
                nb.code(text, kind="")
                continue
            inside = range(start, start + len(body))
            mine = [i for i, at in enumerate(todo_at) if at in inside]
            my_edits = [edits[i] for i, at in enumerate(edit_at) if at in inside]
            sub += 1
            names = f.get("chunk_titles") or []  # 구획 제목: 명시 목록 → 제목 대응표 → 원본 구분선 이름
            shown = names[visible] if visible < len(names) else (f.get("titles") or {}).get(title or "", title) or "실행하기"
            visible += 1
            nb.h(3, f"{n}.{sub} {shown}")  # 예제·과제 표시는 nbkit가 제목 옆에 붙인다
            for e in my_edits:
                nb.md(f"**✍️ CHANGE_HERE: {e['todo']}**\n\n{e['explain']}")
            for i in mine:
                t = todos[i]
                nb.md(f"**✍️ WRITE_HERE: {t['todo']}**\n\n{t['explain']}")
                nb.md(f"**프롬프트 힌트** {t['hint']}")
                nb.md(_criteria_md(t.get("checks", []), t.get("fail", [])))
                nb.meta(t.get("look__meta"))
            nb.code(text, visible=True, kind=KIND_TASK if mine else KIND_EXAMPLE)  # 수강생이 채우거나 바꿔서 실행하는 셀
            if shown in f.get("no_auto_run", []):  # input()처럼 사람이 답해야 하는 셀: 자동 실행 검사에서 건너뛴다
                nb.cells[-1].metadata.setdefault("tags", []).append("skip-auto-run")
            done = (f.get("chunk_success") or {}).get(shown)
            if done:  # 예제: 바꿔 실행한 뒤 스스로 확인할 성공 기준
                nb.md(_criteria_md(done))
            if mine:
                # 정답은 원본에서 지운 줄이 기본이고, 솔루션과 다른 곳은 spec의 answer로 바꿔 보여 준다
                ans = "\n\n".join("```python\n" + _dedent_common("\n".join(todos[i].get("answer") or answers[i])) + "\n```" for i in mine)
                nb.md(f"<details><summary>정답 보기</summary>\n\n{ans}\n\n</details>")
        if wf:
            nb.md(f.get("run_note", "위 셀을 실행하면 이 폴더에 앱 파일이 만들어집니다. 아래 셀을 실행하면 브라우저에 앱이 열립니다. 앱을 멈출 때는 이 셀의 실행을 중지(■)합니다."))
            nb.code(f"!streamlit run {wf}", visible=True, kind=KIND_EXAMPLE)
        nb.md(f["look"])
        nb.meta(f.get("look__meta"))
        ask = f.get("ask")
        if not todos and ask:
            sub += 1
            nb.h(3, f"{n}.{sub} AI에게 물어보기")
            nb.md(f"**프롬프트 힌트** {ask['hint']}")
            nb.md(_criteria_md([], ask.get("fail", []), ask.get("success", [])))

    nb.h(2, f"{len(spec['files']) + 2}. 정리")
    nb.md(spec["closing"])
    nb.finish(LESSONS / "Chapter01" / f"{unit}_{slug}_LAB.ipynb")


def _sections(lines):
    """'# ──' 구분선을 코드 지도 구획으로 쓴다. 없으면 파일 전체를 한 구획으로."""
    secs = [{"title": "불러오기와 준비", "marker": lines[0].strip() or lines[1].strip(), "note": "필요한 도구를 불러오고 준비합니다."}]
    for line in lines:
        if line.startswith("# ──"):
            title = line.strip("# ─").strip() or "구획"
            secs.append({"title": title, "marker": line.strip(), "note": "(설명 작성 예정)"})
    return secs


def _guess_blank(lines, t):
    """TODO 줄(t) 다음의 정답 줄 범위를 추정한다. 주석은 건너뛰고, 빈 줄이나 같은 깊이의 주석·들여쓰기 감소에서 멈춘다."""
    indent = len(lines[t]) - len(lines[t].lstrip())
    a = t + 1
    while a < len(lines) and lines[a].strip().startswith("#"):
        a += 1
    if a >= len(lines):
        return None
    e = a + 1
    while e < len(lines):
        s = lines[e]
        if not s.strip():
            break
        ind = len(s) - len(s.lstrip())
        if ind < indent or (ind <= indent and s.strip().startswith("#")):
            break
        e += 1
    end = "EOF" if e >= len(lines) else lines[e].strip() or None
    if end is None:  # 빈 줄에서 멈춘 경우: 빈 줄 다음의 첫 줄을 끝 표시로 쓴다
        nxt = next((k for k in range(e, len(lines)) if lines[k].strip()), None)
        end = "EOF" if nxt is None else lines[nxt].strip()
    return {"start": lines[a].strip(), "end": end}


def scaffold(folder):
    """실습 폴더의 뼈대 JSON을 만든다. 설명·지시문은 '작성 예정'으로 두고, 빈칸 범위는 추정값이다."""
    out = LABS / f"{folder}.json"
    if out.exists():
        print(f"✔ 이미 있음: {out.name}")
        return
    raw_dir = ROOT / "src" / "raw" / "Chapter01" / folder
    files = []
    for py in sorted(raw_dir.glob("*.py")):
        lines = py.read_text(encoding="utf-8").splitlines()
        todos = []
        for t, line in enumerate(lines):
            if "TODO" in line:
                blank = _guess_blank(lines, t)
                todos.append({"todo": line.split("TODO:", 1)[-1].strip(), "blank": blank,
                              "explain": "(작성 예정)", "hint": "(작성 예정)", "checks": [], "fail": []})
        entry = {"name": py.name, "title": py.stem, "intro": "(작성 예정)", "map": _sections(lines),
                 "look": "(작성 예정)"}
        if todos:
            entry["todos"] = todos
        else:
            entry["ask"] = {"hint": "(작성 예정)", "success": ["(작성 예정)"], "fail": []}
        files.append(entry)
    unit = UNITS[folder][0]
    spec = {"draft": True, "title": f"{unit} 실습", "intro": "(작성 예정)", "files": files, "closing": "(작성 예정)"}
    LABS.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✔ 뼈대 생성: {out.name} (파일 {len(files)}개, TODO {sum(len(f.get('todos', [])) for f in files)}개)")


def check_blanks(folder):
    """빈칸을 채우기 전 복사본이 파이썬 문법에 맞는지 확인한다(추정 범위 점검용)."""
    import tempfile

    sys.path.insert(0, str(LESSONS))
    from assets.widgets import make_blank

    spec = json.loads((LABS / f"{folder}.json").read_text(encoding="utf-8"))
    for f in spec["files"]:
        if not f.get("todos"):
            continue
        raw = ROOT / "src" / "raw" / "Chapter01" / folder / f["name"]
        with tempfile.TemporaryDirectory() as d:
            work = Path(d) / f["name"]
            try:
                make_blank(raw, work, [t["blank"] for t in f["todos"]], reset=True)
                ast.parse(work.read_text(encoding="utf-8"))
                print(f"✔ {folder}/{f['name']}: 빈칸 {len(f['todos'])}곳, 문법 정상")
            except Exception as e:  # noqa: BLE001
                print(f"✖ {folder}/{f['name']} | {type(e).__name__}: {e} | labs/{folder}.json의 blank 범위를 고친다")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--scaffold"]:
        for folder in UNITS:
            scaffold(folder)
            check_blanks(folder)
    elif args[:1] == ["--check"]:
        for folder in args[1:] or UNITS:
            check_blanks(folder)
    else:
        for folder in args or sorted(p.stem for p in LABS.glob("*.json")):
            build(folder)
