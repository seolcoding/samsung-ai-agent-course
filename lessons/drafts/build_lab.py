"""실습 노트북을 조립한다. 받은 실습 코드(src/raw)를 CodeMate와 함께 채우고 솔루션(src/solution)과 비교한다.

실행(프로젝트 루트):
  uv run python lessons/drafts/build_lab.py 01-llm-api        # 실습 폴더 하나
  uv run python lessons/drafts/build_lab.py                   # labs/*.json 전부
  uv run python lessons/drafts/build_lab.py --scaffold        # 아직 없는 실습 폴더의 뼈대 JSON 만들기

입력: lessons/drafts/labs/<실습 폴더>.json
출력: lessons/Chapter01/<번호>_<이름>_LAB.ipynb (출력 없음)

모든 실습 노트북은 같은 구조다.
  제목 → 목차 → 1. 실습 방법 → 파일마다 한 장(코드 구조 → TODO마다 CodeMate 지시 → 실행과 솔루션 비교) → 정리
원본은 고치지 않는다. 수강생은 lessons/work/ 아래 빈칸 복사본을 채운다.
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

PROMPT_GUIDE = """CodeMate에 주는 지시문은 네 칸으로 씁니다. 강의의 "좋은 입력의 네 가지"를 그대로 쓴 것입니다.

```text
[역할·목표] 무엇을 하는 사람으로서, 무엇을 만들어 달라는지
[배경·제약] 어느 파일의 어느 빈칸인지, 쓸 수 있는 것과 없는 것
[출력 형식] 코드만? 코드 + 설명 3줄?
[모호함 줄이기] 헷갈릴 만한 부분을 미리 정해 주기
[하지 말 것] 빈칸 밖은 고치지 않기, 새 기능 추가하지 않기
```

순서는 늘 같습니다.
1. 빈칸 위의 TODO 주석을 읽고, 무엇을 채워야 하는지 한 문장으로 말해 봅니다.
2. 지시문을 CodeMate 채팅에 붙여 넣습니다. 실습 파일을 열어 둔 상태에서 합니다.
3. CodeMate가 채운 코드를 읽고, 모르는 줄이 있으면 "이 줄이 하는 일"을 다시 묻습니다.
4. 실행해 봅니다. 오류가 나면 오류 메시지를 그대로 CodeMate에 붙여 넣고 원인부터 설명해 달라고 합니다.
5. 솔루션과 비교합니다. 다르다고 틀린 것은 아닙니다. 왜 다른지 말할 수 있으면 됩니다."""

CHECK = [
    "빈칸만 채웠고 다른 줄은 바꾸지 않았다",
    "실행했을 때 오류 없이 결과가 나왔다",
    "채운 코드의 각 줄이 하는 일을 말할 수 있다",
    "솔루션과 다른 곳이 있다면 왜 다른지 설명할 수 있다",
]


def build(folder):
    spec = json.loads((LABS / f"{folder}.json").read_text(encoding="utf-8"))
    unit, slug = UNITS[folder]
    raw_dir, sol_dir = f"{REF}/src/raw/Chapter01/{folder}", f"{REF}/src/solution/Chapter01/{folder}"
    work_dir = f"../work/Chapter01/{folder}"
    nb = Notebook(LESSONS / "assets" / "quizzes" / f"{unit}-lab", f"../assets/quizzes/{unit}-lab")

    nb.md(f"# [LAB] {spec['title']}\n\n{spec['intro']}")
    nb.meta(spec.get("intro__meta"))
    nb.code(
        "import sys\n\nsys.path.insert(0, '..')  # lessons/assets 도구를 불러오기 위한 경로\n\n"
        "from assets.widgets import make_blank, run_step, show_checklist, show_code_map, show_diff"
    )
    nb.code(COMMON["env_check_code"])
    nb.md(COMMON["env_check_look"])

    nb.h(2, "1. 실습 방법")
    nb.md(PROMPT_GUIDE)

    made_blank = ran_once = False  # 실습 파일·실행 안내는 처음 한 번만 쓴다
    for n, f in enumerate(spec["files"], start=2):
        name = f["name"]
        raw, sol, work = f"{raw_dir}/{name}", f"{sol_dir}/{name}", f"{work_dir}/{name}"
        nb.h(2, f"{n}. {f['title']} (`{name}`)")
        nb.md(f["intro"])
        nb.meta(f.get("intro__meta"))
        todos = f.get("todos", [])
        if todos:
            # 빈칸 복사본을 먼저 만들고, 코드 지도도 복사본으로 보여 준다(원본을 보여 주면 정답이 보인다).
            if not made_blank:
                nb.md("아래 셀을 실행하면 실습 파일이 `lessons/work/` 아래에 만들어집니다. TODO 아래 정답 줄은 빈칸(`...`)으로 "
                      "바뀌어 있습니다. VS Code에서 그 파일을 열어 두고 CodeMate와 함께 채웁니다.")
                made_blank = True
            nb.code(f"make_blank({raw!r}, {work!r}, {pformat([t['blank'] for t in todos], width=100, sort_dicts=False)})")
        nb.h(3, f"{n}.1 코드 구조 보기")
        nb.code(f"show_code_map({(work if todos else raw)!r}, {pformat(f['map'], width=100, sort_dicts=False)})")
        if todos:
            for k, t in enumerate(todos, start=2):
                nb.h(3, f"{n}.{k} TODO: {t['todo']}")
                nb.md(t["explain"])
                nb.md("**CodeMate 지시문**\n\n```text\n" + t["prompt"].strip() + "\n```")
                nb.md(t["look"])
                nb.meta(t.get("look__meta"))
            last = len(todos) + 2
            nb.h(3, f"{n}.{last} 실행하고 솔루션과 비교하기")
            if f.get("run_intro") or not ran_once:  # 기본 안내는 처음 한 번만 쓴다(반복 방지)
                nb.md(f.get("run_intro", "빈칸을 모두 채웠으면 실행합니다. 결과를 본 뒤 솔루션과 나란히 비교합니다."))
            ran_once = True
            nb.code(f"run_step({work!r})")
            nb.md(f["look"])
            nb.code(f"show_diff({work!r}, {sol!r})")
        else:
            nb.h(3, f"{n}.2 실행하기")
            nb.md(f.get("run_intro", "원본을 그대로 실행하고 결과를 봅니다."))
            nb.code(f"run_step({raw!r})")
            nb.md(f["look"])
            nb.h(3, f"{n}.3 CodeMate로 설명 받기")
            nb.md("**CodeMate 지시문**\n\n```text\n" + f["explain_prompt"].strip() + "\n```")
            nb.md(f.get("explain_look", "CodeMate의 설명을 실행 결과와 대조합니다. 설명과 결과가 다르면 어느 쪽이 맞는지 다시 묻습니다."))
        nb.code(f"show_checklist({pformat(f.get('checklist', CHECK), width=100)}, title='{name} 리뷰')")
        nb.meta(f.get("look__meta"))

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
