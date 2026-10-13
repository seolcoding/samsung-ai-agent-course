"""실습 노트북을 조립한다. 받은 실습 코드(course/Chapter01/code/raw)를 AI와 함께 채우고 솔루션(code/solution)과 비교한다.

실행(프로젝트 루트):
  uv run python dev/builders/build_lab.py 01-llm-api        # 실습 폴더 하나
  uv run python dev/builders/build_lab.py                   # labs/*.json 전부
  uv run python dev/builders/build_lab.py --scaffold        # 아직 없는 실습 폴더의 뼈대 JSON 만들기
  uv run python dev/builders/build_lab.py --mc               # 객관식판 전부(labs/<폴더>.choices.json, 파일 이름 끝 _LAB_MC)

입력: dev/builders/labs/<실습 폴더>.json
출력: course/Chapter01/notebooks/<번호>_<이름>_LAB.ipynb (출력 없음)

수강생에게는 노트북만 보인다(.py 실습 파일은 주지 않는다). 그래서 원본 코드를 빌드할 때 셀로 옮겨 넣는다.
정본은 계속 course/Chapter01/code/raw이고, 원본이 바뀌면 다시 빌드한다.

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
from pprint import pformat

sys.path.insert(0, str(Path(__file__).parent))
from nbkit import SELF_HELP, TRUSTSTORE_CODE, TRUSTSTORE_MD, Notebook, fmt  # noqa: E402

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
COURSE = ROOT / "course"
LABS = HERE / "labs"
COMMON = json.loads((HERE / "1-2_cells_common.json").read_text(encoding="utf-8"))

# 실습 폴더 ↔ 교안 번호와 노트북 이름
UNITS = {
    "01-llm-api": ("1-2", "llm_api"),
    "02-langchain": ("1-3", "langchain"),
    "03-rag": ("1-4", "rag"),
    "04-langgraph": ("2-1", "langgraph"),
    "05-multi-agent": ("2-2", "multi_agent"),
    "06-rag-streamlit": ("2-3", "rag_streamlit"),
    # Chapter02(M2). spec 파일은 labs/Chapter02/<실습 폴더>.json
    "00-review": ("3-1", "review"),
    "01-mcp": ("3-2", "mcp"),
    "02-a2a": ("3-3", "a2a"),
    "03-langgraph-advanced": ("3-4", "langgraph_advanced"),
    "04-harness": ("4-1", "harness"),
    "05-observability": ("4-2", "observability"),
}


def chapter_of(folder):
    """교안 번호 첫 자리로 챕터를 정한다: 1·2일차 → Chapter01, 3·4일차 → Chapter02."""
    return "Chapter01" if UNITS[folder][0][0] in "12" else "Chapter02"


def spec_path(folder):
    ch = chapter_of(folder)
    return LABS / f"{folder}.json" if ch == "Chapter01" else LABS / ch / f"{folder}.json"

KIND_EXAMPLE, KIND_TASK = "예제", "과제"  # 제목 옆 표시 (예제) (과제)

PROMPT_GUIDE = f"""실습은 두 종류입니다. 제목 옆 표시와 코드 주석으로 구분합니다.

- **{KIND_EXAMPLE}** `# ✍️ CHANGE_HERE:` 바로 아래 줄의 값을 바꿔 다시 실행해 봅니다.
- **{KIND_TASK}** `# ✍️ WRITE_HERE:` 아래 빈칸(`...`)을 AI와 함께 채웁니다. **프롬프트 힌트**를 보고 지시를 직접 씁니다.

실행한 뒤에는 **성공 기준**과 비교해 스스로 판단합니다. 🟢는 되어야 하는 것, ⛔는 다시 해야 하는 신호입니다. 과제는 그다음 접힌 "정답 보기"와 비교합니다.

"정답 보기"의 코드는 빈칸 줄과 같은 들여쓰기로 보여 줍니다. 붙여 넣을 때는 빈칸 줄 전체(줄 앞 공백까지)를 지우고 그 자리에 붙여 넣습니다."""


# 객관식 시험판(--mc): 빈칸 자리에 보기를 주석으로 넣고, 수강생이 하나를 골라 주석을 푼다.
PROMPT_GUIDE_MC = """코드 셀에서 손댈 곳은 주석으로 표시되어 있습니다.

- `# ✍️ CHANGE_HERE:` 바로 아래 줄의 값을 바꿔 다시 실행해 봅니다.
- `# ✅ CHOOSE_HERE:` 아래에 보기가 주석으로 들어 있습니다. 줄 끝의 번호(1️⃣~4️⃣)와 설명을 보고 하나를 고릅니다. 같은 번호가 붙은 줄을 모두 선택하고 `Ctrl + /`를 눌러 주석을 푼 뒤 실행합니다.

실행한 뒤에는 **성공 기준**과 비교해 봅니다. 🟢는 되어야 하는 것, ⛔는 다시 해야 하는 신호입니다. ⛔이면 푼 줄을 다시 선택하고 `Ctrl + /`로 주석 처리한 뒤 다른 보기를 고릅니다. 마지막으로 접힌 "정답 보기"에서 보기마다의 해설을 읽습니다."""
PROMPT_GUIDE_MC_NO_TASK = """코드 셀에서 손댈 곳은 주석으로 표시되어 있습니다.

- `# ✍️ CHANGE_HERE:` 바로 아래 줄의 값을 바꿔 다시 실행해 봅니다.

실행한 뒤에는 **성공 기준**과 비교해 봅니다. 🟢는 되어야 하는 것, ⛔는 다시 해야 하는 신호입니다."""
NUMS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
MARK_CHOOSE = "# ✅ CHOOSE_HERE:"
HOW_CHOOSE = "같은 번호의 줄을 모두 선택하고 Ctrl + / 를 누르면 주석이 풀립니다"  # CHOOSE_HERE 바로 아래에 늘 보이게 둔다


TERMINAL_NOTE = """{write}하면 이 폴더에 서버 파일이 만들어집니다(빈칸을 먼저 채웁니다). 서버는 터미널에서 띄웁니다.

1. VS Code 메뉴 **터미널 → 새 터미널**을 엽니다(저장소 맨 위 폴더에서 열립니다).
2. 아래 명령을 붙여 넣고 실행합니다.

```
uv run python {path}
```

3. 서버 시작 문구가 나오고 명령이 끝나지 않고 기다리면 켜진 것입니다. 이 터미널은 닫지 말고 노트북으로 돌아옵니다.
4. 서버 파일을 고쳤다면 터미널에서 **Ctrl+C**로 끄고, {rewrite} 같은 명령으로 다시 띄웁니다.{warn}"""

BLANK_LINE = "...  # ✍️ 여기를 채웁니다"

# LangChain·LangGraph 코드를 쓰는 실습은 맨 위 설정에 디버그 모드 셀을 따로 둔다(기본 켜짐, 2026-10-13 결정)
DEBUG_MD = "LangChain 디버그 모드를 켭니다. 체인과 그래프가 실행될 때 단계마다 입력과 출력이 셀 아래에 출력됩니다."
DEBUG_CODE = """from langchain_core.globals import set_debug

# 출력이 너무 길면 True를 False로 바꾸고 이 셀을 다시 실행합니다
set_debug(True)"""
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
        while e - 1 > a and not lines[e - 1].strip():  # 끝 표시 앞의 빈 줄은 빈칸에 넣지 않고 남긴다
            e -= 1
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


def _answer_code(text, indent):
    """정답 보기 코드: 빈칸 줄과 같은 들여쓰기로 맞춘다(빈칸 줄 전체를 지우고 붙여 넣으면 그대로 맞는다)."""
    import textwrap
    return textwrap.indent(_dedent_common(text), indent)


def _env_check(extra):
    """환경 점검 셀. 점검 로직은 course/config/check.py에 있다(수강생 AI도 같은 점검을 명령으로 돌린다)."""
    groups = f"{list(extra)!r}" if extra else ""
    return ("from config.check import check_env\n\n"
            "# 값은 출력하지 않고, 필요한 설정 이름이 있는지만 봅니다\n"
            f"check_env({groups})")


def _width(text):
    """화면에서 차지하는 폭(한글·이모지는 두 칸)."""
    import unicodedata
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def _choice_lines(indent, choice, need_body=False):
    """보기를 주석 줄로 만든다. 줄 끝에 번호를 달고, 보기의 첫 줄에는 짧은 설명을 붙인다."""
    multi = any(len(o["lines"]) > 1 for o in choice["options"])
    rows = []
    for k, o in enumerate(choice["options"]):
        if multi and k:
            rows.append((indent + "#", None))
        for m, ln in enumerate(o["lines"]):
            rows.append((f"{indent}# {ln}", f"{NUMS[k]} {o['note']}" if m == 0 else NUMS[k]))
    # 번호 열을 맞춘다. 아주 긴 줄 하나 때문에 번호가 멀리 밀리지 않도록 열은 60칸에서 자르고, 그보다 긴 줄은 두 칸 띄워 붙인다
    col = min(max(_width(a) for a, b in rows if b), 60) + 2
    # 함수 몸통이 보기뿐이면 고르기 전에도 문법에 맞도록 맨 밑에 pass를 둔다(골라 푼 줄은 그대로 먼저 실행된다)
    tail = [indent + "pass  # 그대로 둡니다"] if need_body else []
    return [a if b is None else a + " " * max(col - _width(a), 2) + "# " + b for a, b in rows] + tail


def _choice_answer(choice):
    """정답 보기 글: 정답 번호와 보기마다의 해설."""
    n = choice["answer"]
    return f"**정답: {NUMS[n - 1]}**\n\n" + "\n".join(f"- {NUMS[k]} {o['why']}" for k, o in enumerate(choice["options"]))


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


def build(folder, mc=False):
    spec = json.loads(spec_path(folder).read_text(encoding="utf-8"))
    cpath = spec_path(folder).with_suffix(".choices.json")
    choices = json.loads(cpath.read_text(encoding="utf-8")) if mc and cpath.exists() else {}
    if mc:  # 객관식판의 글: 예제·과제 구분 없이 쓴 글로 바꾼다
        text = choices.get("_text", {})
        spec.update({k: text[k] for k in ("intro", "closing") if k in text})
        seen = {}
        for f in spec["files"]:  # files.<파일 이름> 또는 같은 파일이 여러 번 나오면 files.<파일 이름>#<0부터 센 순서>
            k = seen[f["name"]] = seen.get(f["name"], -1) + 1
            files = text.get("files", {})
            f.update(files.get(f["name"], {}))
            f.update(files.get(f"{f['name']}#{k}", {}))
            for t in f.get("todos", []):  # 과제 글: explain·checks는 바꿔 쓰고, fail_all이 있으면 ⛔ 줄 전체를 바꾼다
                c = choices.get(t["todo"], {})
                t.update({key: c[key] for key in ("explain", "checks") if key in c})
                if "fail_all" in c:
                    t["fail"] = c["fail_all"]
    unit, slug = UNITS[folder]
    chapter = chapter_of(folder)
    nb = Notebook(COURSE / chapter / "assets" / "quizzes" / f"{unit}-lab", f"../assets/quizzes/{unit}-lab")

    nb.md(f"# [LAB] {spec['title']}\n\n{spec['intro']}")
    nb.meta(spec.get("intro__meta"))
    nb.code(_env_check(spec.get("env", [])))
    nb.md(COMMON["env_check_look"])
    if "LANGFUSE" in spec.get("env", []):
        nb.md(TRUSTSTORE_MD)
        nb.code(TRUSTSTORE_CODE, visible=True, kind="")
    if any(re.search(r"^\s*(from|import) (langchain|langgraph)", (COURSE / chapter / "code" / f.get("source", "raw") / folder / f["name"]).read_text(encoding="utf-8"), re.M)
           for f in spec["files"]):
        nb.md(DEBUG_MD)
        nb.code(DEBUG_CODE, visible=True, kind="")

    nb.h(2, "1. 실습 방법")
    if mc and not any(t.get("blank") for f in spec["files"] for t in f.get("todos", [])):
        nb.md(PROMPT_GUIDE_MC_NO_TASK)  # 고를 보기가 없는 실습: CHOOSE_HERE 안내를 빼고 CHANGE_HERE만
    else:
        nb.md(PROMPT_GUIDE_MC if mc else PROMPT_GUIDE)
    nb.md(SELF_HELP)

    for n, f in enumerate(spec["files"], start=2):
        # 원본을 먼저 정돈한다(읽기 쉽게). 원본·솔루션이 다르면 spec의 source로 깔끔한 쪽을 고른다
        src_dir = COURSE / chapter / "code" / f.get("source", "raw") / folder
        raw = _patch(fmt((src_dir / f["name"]).read_text(encoding="utf-8")).splitlines(), f.get("patch", []))
        todos = [t for t in f.get("todos", []) if t.get("blank")]  # 빈칸 범위가 없는 TODO(뼈대 미완성)는 건너뛴다
        for t in f.get("todos", []):
            if not t.get("blank"):
                print(f"✖ {folder}/{f['name']} TODO 빈칸 범위 없음 | 뼈대 추정 실패 | labs/{folder}.json의 blank를 채운다")
        lines, answers = _blank(raw, [choices.get(t["todo"], {}).get("blank", t["blank"]) for t in todos]) if todos else (raw, [])
        todos, answers = [t for t, x in zip(todos, answers) if x is not None], [x for x in answers if x is not None]
        blank_indents = [ln[: len(ln) - len(ln.lstrip())] for ln in lines if ln.endswith(BLANK_LINE)]
        if mc:  # 빈칸 줄을 보기 주석으로 바꾼다. 정답 보기가 지운 줄과 같은지 확인한다(조용히 틀리지 않게)
            out, j = [], 0
            for ln in lines:
                if ln.endswith(BLANK_LINE):
                    c = choices.get(todos[j]["todo"])
                    assert c, f"객관식 보기가 없음: {folder} {todos[j]['todo']!r} | {cpath.name}에 보기를 넣는다"
                    want = [x.strip() for x in todos[j].get("answer") or answers[j]]
                    assert c.get("rewrite") or [x.strip() for x in c["options"][c["answer"] - 1]["lines"]] == want, f"정답 보기가 원본 정답과 다름: {todos[j]['todo']}"
                    code_above = [x for x in out if x.strip() and not x.strip().startswith("#")]
                    out += _choice_lines(blank_indents[j], c, need_body=bool(code_above) and code_above[-1].rstrip().endswith(":"))
                    j += 1
                else:
                    out.append(ln)
            lines = out
        edits = f.get("edits", [])
        lines, edit_at = _mark(lines, edits)
        if mc:
            out, k, moved = [], 0, {}  # moved: 옛 줄 번호 → 새 줄 번호(안내 줄을 끼워 넣어 밀린 CHANGE_HERE 위치를 다시 맞춘다)
            while k < len(lines):
                ln = lines[k]
                moved[k] = len(out)
                out.append(ln.replace(MARK_TASK, MARK_CHOOSE))
                k += 1
                if MARK_TASK in ln:  # 여러 줄 지시문(이어지는 주석)이 끝난 뒤, 보기 바로 위에 고르는 법을 둔다
                    while k < len(lines) and lines[k].strip().startswith("#") and lines[k].strip() != "#" \
                            and not any(n in lines[k] for n in NUMS):
                        moved[k] = len(out)
                        out.append(lines[k])
                        k += 1
                    out.append(ln[: len(ln) - len(ln.lstrip())] + "# (" + HOW_CHOOSE + ")")
            lines, edit_at = out, [moved[a] for a in edit_at]
        # WRITE_HERE 주석 줄 위치로 어느 구획에 속하는지 정한다(찾지 못하면 순서대로 WRITE_HERE 줄을 쓴다)
        todo_lines = [k for k, ln in enumerate(lines) if MARK_TASK in ln or MARK_CHOOSE in ln]
        todo_at = [next((k for k in todo_lines if t["todo"][:12] in lines[k]), todo_lines[min(i, len(todo_lines) - 1)] if todo_lines else 0)
                   for i, t in enumerate(todos)]
        # Streamlit 앱·서버처럼 파일로 띄워야 하는 코드: 셀에서 파일로 쓰고 따로 실행한다.
        # split을 주면 구획마다 나눠 쓴다(첫 구획은 새로 쓰고, 다음부터는 이어 쓰기 -a)
        wf = f.get("writefile")
        split = f.get("split", []) if wf else f.get("split") or [ln.strip() for ln in lines if ln.startswith("# ──")]
        if mc:  # 구획 표시에 WRITE_HERE가 있으면 객관식판에서는 CHOOSE_HERE로 바뀌어 있다
            split = [m.replace("✍️ WRITE_HERE", "✅ CHOOSE_HERE").replace("WRITE_HERE", "CHOOSE_HERE") for m in split]
        nb.h(2, f"{n}. {f['title']}")
        nb.md(f["intro"])
        nb.meta(f.get("intro__meta"))
        pos, sub, visible, first_wf = 0, 0, 0, None
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
                nb.md("실행되지 않는 참고 코드입니다. 읽어만 봅니다.\n\n```python\n" + (notes + "\n" if notes else "") + ref + "\n```")
                continue
            if wf:
                if c == 0 and "/" in wf:  # %%writefile은 폴더를 만들지 않는다
                    folder_of = wf.rsplit("/", 1)[0]
                    nb.code(f"from pathlib import Path\n\nPath({folder_of!r}).mkdir(parents=True, exist_ok=True)", kind="")
                if c == 0:
                    first_wf = f"{n}.{sub + 1}"
                    text = f"%%writefile {wf}\n" + text
                else:  # 이어 쓰기 셀만 다시 실행하면 파일 끝(서버 실행 줄 뒤)에 붙어 반영되지 않는다
                    text = (f"%%writefile -a {wf}\n# 이어 쓰기 셀: 고쳤다면 {first_wf} 셀부터 차례로 다시 실행합니다"
                            f"(이 셀만 다시 실행하면 반영되지 않습니다)\n" + text)  # IPython이 끝에 줄바꿈을 붙여 이어 쓴다
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
                if mc:
                    nb.md(f"**✅ CHOOSE_HERE: {t['todo']}**\n\n{t['explain']}\n\n보기 고르는 법: {HOW_CHOOSE.replace('Ctrl + / ', '`Ctrl + /`')}.")
                else:
                    nb.md(f"**✍️ WRITE_HERE: {t['todo']}**\n\n{t['explain']}")
                    nb.md(f"**프롬프트 힌트** {t['hint']}")
                nb.md(_criteria_md(t.get("checks", []), [*t.get("fail", []), *choices.get(t["todo"], {}).get("fail", [])]))
                nb.meta(t.get("look__meta"))
            nb.code(text, visible=True, kind="" if mc else KIND_TASK if mine else KIND_EXAMPLE)  # 객관식판은 제목 옆 표시를 달지 않는다  # 수강생이 채우거나 바꿔서 실행하는 셀
            if shown in f.get("no_auto_run", []):  # input()처럼 사람이 답해야 하는 셀: 자동 실행 검사에서 건너뛴다
                nb.cells[-1].metadata.setdefault("tags", []).append("skip-auto-run")
            done = (f.get("chunk_success") or {}).get(shown)
            if done:  # 예제: 바꿔 실행한 뒤 스스로 확인할 성공 기준. 목록(🟢만) 또는 {"success": [...], "fail": [...]}
                nb.md(_criteria_md([], done.get("fail", []), done.get("success", [])) if isinstance(done, dict) else _criteria_md(done))
            if mine and mc:
                many = len(mine) > 1
                ans = "\n\n".join((f"**{todos[i]['todo']}**\n\n" if many else "") + _choice_answer(choices[todos[i]["todo"]]) for i in mine)
                nb.md(f"<details><summary>정답 보기</summary>\n\n{ans}\n\n</details>")
            elif mine:
                # 정답은 원본에서 지운 줄이 기본이고, 솔루션과 다른 곳은 spec의 answer로 바꿔 보여 준다
                ans = "\n\n".join("```python\n" + _answer_code("\n".join(todos[i].get("answer") or answers[i]), blank_indents[i]) + "\n```"
                                    for i in mine)
                nb.md(f"<details><summary>정답 보기</summary>\n\n{ans}\n\n</details>")
        if wf and f.get("run") == "terminal":  # 서버: 노트북 커널을 붙잡지 않도록 터미널에서 띄운다
            many = split and first_wf  # 여러 셀로 나눠 쓴 파일
            nb.md(f.get("run_note") or TERMINAL_NOTE.format(
                path=f"course/{chapter}/notebooks/{wf}",
                write=f"{first_wf} 셀부터 이 안내 바로 위 셀까지 차례로 실행" if many else "위 셀을 실행",
                rewrite=f"{first_wf} 셀부터 이 안내 바로 위 셀까지 차례로 모두 다시 실행한 뒤" if many else "위 셀을 다시 실행한 뒤",
                warn=" 고친 셀 하나만 다시 실행하면 파일 끝에 덧붙기만 해서 반영되지 않습니다." if many else "")
                .replace("(빈칸을 먼저 채웁니다)", "(보기를 먼저 고릅니다)" if mc else "(빈칸을 먼저 채웁니다)"))
        elif wf:
            nb.md(f.get("run_note", "위 셀을 실행하면 이 폴더에 앱 파일이 만들어집니다. 아래 셀을 실행하면 브라우저에 앱이 열립니다. 앱을 멈출 때는 이 셀의 실행을 중지(■)합니다."))
            # 셸 PATH에 가상환경이 없어도 되도록, 노트북 커널의 파이썬으로 streamlit을 실행한다.
            # 경로에 공백이 있어도 되게 따옴표로 감싼다(Windows cmd). showEmailPrompt false: 새 PC의 첫 실행이
            # 이메일 입력을 기다리며 멈추지 않게 한다. address 127.0.0.1: 방화벽 허용 창과 같은 망의 다른 PC 접속을 막는다.
            # --server.headless true는 브라우저 자동 열림까지 꺼지므로 쓰지 않는다.
            nb.code(f"import sys\n\n# 첫 실행 때 이메일을 묻지 않고, 이 PC에서만 열리게 합니다\n"
                    f"!\"{{sys.executable}}\" -m streamlit run {wf} --server.showEmailPrompt false --server.address 127.0.0.1",
                    visible=True, kind="" if mc else KIND_EXAMPLE)
            nb.cells[-1].metadata.setdefault("tags", []).append("skip-auto-run")  # 앱은 멈출 때까지 돈다
        nb.md(f["look"])
        nb.meta(f.get("look__meta"))
        ask = f.get("ask")
        if ask:
            sub += 1
            nb.h(3, f"{n}.{sub} AI에게 물어보기")
            nb.md(f"**프롬프트 힌트** {ask['hint']}")
            nb.md(_criteria_md([], ask.get("fail", []), ask.get("success", [])))

    nb.h(2, f"{len(spec['files']) + 2}. 정리")
    nb.md(spec["closing"])
    if mc:  # 객관식판은 # · ## 제목을 접은 채로 연다(JupyterLab·classic 메타데이터. VS Code 반영은 미확인)
        nb.flush()
        for cell in nb.cells:
            level = cell.metadata.get("heading", {}).get("level") or (1 if cell.cell_type == "markdown" and cell.source.startswith("# ") else None)
            if level and level <= 2:
                cell.metadata["jp-MarkdownHeadingCollapsed"] = True
                cell.metadata["heading_collapsed"] = True
    nb.finish(COURSE / chapter / "notebooks" / f"{unit}_{slug}_LAB{'_MC' if mc else ''}.ipynb")


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
    out = spec_path(folder)
    if out.exists():
        print(f"✔ 이미 있음: {out.name}")
        return
    raw_dir = COURSE / chapter_of(folder) / "code" / "raw" / folder
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
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✔ 뼈대 생성: {out.name} (파일 {len(files)}개, TODO {sum(len(f.get('todos', [])) for f in files)}개)")


def check_blanks(folder):
    """빈칸을 채우기 전 복사본이 파이썬 문법에 맞는지 확인한다(추정 범위 점검용)."""
    import tempfile

    sys.path.insert(0, str(COURSE / "Chapter01"))
    from assets.widgets import make_blank

    spec = json.loads(spec_path(folder).read_text(encoding="utf-8"))
    for f in spec["files"]:
        if not f.get("todos"):
            continue
        raw = COURSE / chapter_of(folder) / "code" / "raw" / folder / f["name"]
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
        for folder in args[1:] or UNITS:
            scaffold(folder)
            check_blanks(folder)
    elif args[:1] == ["--mc"]:  # 객관식판: labs/<폴더>.choices.json의 보기로 <번호>_<이름>_LAB_MC.ipynb를 만든다
        for folder in args[1:] or sorted(p.stem for p in LABS.glob("**/*.json") if p.stem in UNITS):
            build(folder, mc=True)
    elif args[:1] == ["--check"]:
        for folder in args[1:] or UNITS:
            check_blanks(folder)
    else:
        for folder in args or sorted(p.stem for p in LABS.glob("**/*.json") if p.stem in UNITS):
            build(folder)
