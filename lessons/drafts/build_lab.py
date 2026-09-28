"""실습 노트북을 조립한다. 받은 실습 코드(src/raw)를 CodeMate와 함께 채우고 솔루션(src/solution)과 비교한다.

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
    준비 코드(접힘) → 구획마다 [TODO 설명·CodeMate 지시문 → 빈칸이 든 코드 셀 → 볼 지점 → 정답 보기(접힘)]
  → 정리
TODO 아래 정답 줄은 빈칸(`...  # ✍ …`)으로 바꿔 넣고, 정답은 접힌 "정답 보기"에 둔다.
"""

import ast
import json
import sys
from pathlib import Path
from pprint import pformat

sys.path.insert(0, str(Path(__file__).parent))
from nbkit import Notebook  # noqa: E402

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

PROMPT_GUIDE = """CodeMate에 주는 지시문은 다섯 칸으로 씁니다. 무엇을 원하는지, 어떤 조건인지, 어떤 모양으로 받을지, 헷갈릴 점과 하지 말 것을 미리 적어 두면 원하는 코드를 받기 쉽습니다.

```text
[역할·목표] 무엇을 하는 사람으로서, 무엇을 만들어 달라는지
[배경·제약] 어느 셀의 어느 빈칸인지, 쓸 수 있는 것과 없는 것
[출력 형식] 코드만? 코드 + 설명 3줄?
[모호함 줄이기] 헷갈릴 만한 부분을 미리 정해 주기
[하지 말 것] 빈칸 밖은 고치지 않기, 새 기능 추가하지 않기
```

순서는 늘 같습니다.
1. 빈칸 위의 TODO 주석을 읽고, 무엇을 채워야 하는지 한 문장으로 말해 봅니다.
2. 빈칸이 든 코드 셀을 선택한 상태에서 지시문을 CodeMate 채팅에 붙여 넣습니다.
3. CodeMate가 채운 코드를 읽고, 모르는 줄이 있으면 "이 줄이 하는 일"을 다시 묻습니다.
4. 실행해 봅니다. 오류가 나면 오류 메시지를 그대로 CodeMate에 붙여 넣고 원인부터 설명해 달라고 합니다.
5. 셀 아래 "정답 보기"를 펼쳐 비교합니다. 다르다고 틀린 것은 아닙니다. 왜 다른지 말할 수 있으면 됩니다."""

CHECK = [
    "빈칸만 채웠고 다른 줄은 바꾸지 않았다",
    "실행했을 때 오류 없이 결과가 나왔다",
    "채운 코드의 각 줄이 하는 일을 말할 수 있다",
    "정답과 다른 곳이 있다면 왜 다른지 설명할 수 있다",
]


BLANK_LINE = "...  # ✍ 여기를 CodeMate와 함께 채웁니다"


def _find(lines, marker, begin):
    return next((k for k in range(begin, len(lines)) if marker in lines[k]), None)


def _blank(lines, blanks):
    """blanks 구간을 빈칸 한 줄로 바꾼 줄 목록과, 구간마다 지운 정답 줄(주석 제외)을 돌려준다."""
    out, answers, k, cursor = [], [], 0, 0
    for b in blanks:
        a = _find(lines, b["start"], cursor)
        end = b.get("end")
        e = a + 1 if end is None else len(lines) if end == "EOF" else _find(lines, end, a + 1)
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


def build(folder):
    spec = json.loads((LABS / f"{folder}.json").read_text(encoding="utf-8"))
    unit, slug = UNITS[folder]
    nb = Notebook(LESSONS / "assets" / "quizzes" / f"{unit}-lab", f"../assets/quizzes/{unit}-lab")

    nb.md(f"# [LAB] {spec['title']}\n\n{spec['intro']}")
    nb.meta(spec.get("intro__meta"))
    nb.code("import sys\n\nsys.path.insert(0, '..')  # lessons/assets 도구를 불러오기 위한 경로\n\nfrom assets.widgets import show_checklist")
    nb.code(COMMON["env_check_code"])
    nb.md(COMMON["env_check_look"])

    nb.h(2, "1. 실습 방법")
    nb.md(PROMPT_GUIDE)

    for n, f in enumerate(spec["files"], start=2):
        raw = (ROOT / "src" / "raw" / "Chapter01" / folder / f["name"]).read_text(encoding="utf-8").splitlines()
        todos = [t for t in f.get("todos", []) if t.get("blank")]  # 빈칸 범위가 없는 TODO(뼈대 미완성)는 건너뛴다
        for t in f.get("todos", []):
            if not t.get("blank"):
                print(f"✖ {folder}/{f['name']} TODO 빈칸 범위 없음 | 뼈대 추정 실패 | labs/{folder}.json의 blank를 채운다")
        lines, answers = _blank(raw, [t["blank"] for t in todos]) if todos else (raw, [])
        # TODO 주석 줄 위치로 어느 구획에 속하는지 정한다(찾지 못하면 순서대로 TODO 줄을 쓴다)
        todo_lines = [k for k, ln in enumerate(lines) if "TODO" in ln]
        todo_at = [next((k for k in todo_lines if t["todo"][:12] in lines[k]), todo_lines[min(i, len(todo_lines) - 1)] if todo_lines else 0)
                   for i, t in enumerate(todos)]
        split = f.get("split") or [ln.strip() for ln in lines if ln.startswith("# ──")]
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
            if c == 0 and f.get("hide_first", True):  # 준비 코드: 불러오기·환경 설정. 접어 둔다
                nb.md(f.get("setup_note", "준비 코드입니다. 필요한 도구를 불러오고 모델을 준비합니다. 접혀 있으니 펼치지 않아도 되고, 실행만 합니다."))
                nb.code(text)
                continue
            mine = [i for i, at in enumerate(todo_at) if start <= at < start + len(body)]
            sub += 1
            names = f.get("chunk_titles") or []  # 구획 제목: 명시 목록 → 제목 대응표 → 원본 구분선 이름
            shown = names[visible] if visible < len(names) else (f.get("titles") or {}).get(title or "", title) or "실행하기"
            visible += 1
            nb.h(3, f"{n}.{sub} {shown}")
            for i in mine:
                t = todos[i]
                nb.md(f"**TODO: {t['todo']}**\n\n{t['explain']}")
                nb.md("**CodeMate 지시문**\n\n```text\n" + t["prompt"].strip() + "\n```")
            nb.code(text, visible=True)  # 수강생이 채우고 실행하는 셀
            if mine:
                for i in mine:
                    nb.md(todos[i]["look"])
                    nb.meta(todos[i].get("look__meta"))
                # 정답은 원본에서 지운 줄이 기본이고, 솔루션과 다른 곳은 spec의 answer로 바꿔 보여 준다
                ans = "\n\n".join("```python\n" + _dedent_common("\n".join(todos[i].get("answer") or answers[i])) + "\n```" for i in mine)
                nb.md(f"<details><summary>정답 보기</summary>\n\n{ans}\n\n</details>")
        nb.md(f["look"])
        nb.meta(f.get("look__meta"))
        if not todos and f.get("explain_prompt"):
            sub += 1
            nb.h(3, f"{n}.{sub} CodeMate로 설명 받기")
            nb.md("**CodeMate 지시문**\n\n```text\n" + f["explain_prompt"].strip() + "\n```")
            nb.md(f.get("explain_look", "CodeMate의 설명을 실행 결과와 대조합니다."))
        nb.code(f"show_checklist({pformat(f.get('checklist', CHECK), width=100)}, title='{f['title']} 리뷰')")

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
                              "explain": "(작성 예정)", "prompt": "(작성 예정)", "look": "(작성 예정)"})
        entry = {"name": py.name, "title": py.stem, "intro": "(작성 예정)", "map": _sections(lines),
                 "look": "(작성 예정)"}
        if todos:
            entry["todos"] = todos
        else:
            entry["explain_prompt"] = "(작성 예정)"
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
