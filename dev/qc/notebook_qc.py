"""교안 노트북 QC 하네스 — 규칙으로 판정할 수 있는 것만 검사한다.

노트북 종류는 파일 이름 끝으로 정한다.
    *_LEC.ipynb  강의 노트북: 슬라이드·설명·퀴즈. 실습 코드 도구(run_step 등)는 없어야 한다.
    *_LAB.ipynb  실습 노트북: 원본 코드를 셀로 넣는다. 준비 코드(접힘) → 예제(`# ✍️ CHANGE_HERE:` 값 바꿔 보기 + 성공 기준)·과제(힌트·성공 기준 → `# ✍️ WRITE_HERE:` 빈칸 셀 → 정답 보기).
수강생은 노트북만 받는다. 그래서 수강생 글에 .py·경로·다른 노트북 이야기가 없어야 한다(노트북 하나로 완결).

실행(프로젝트 루트):
    uv run python dev/qc/notebook_qc.py course/Chapter01/notebooks/1-2_llm_api_LEC.ipynb
    uv run python dev/qc/notebook_qc.py                 # course/Chapter*/notebooks/*.ipynb 전부
    uv run --extra notebooks python dev/qc/notebook_qc.py <노트북> --execute   # 새 커널 실행까지

결과는 검사마다 PASS/WARN/FAIL과 문제 셀 번호(0부터)·짧은 발췌를 출력한다. FAIL이 하나라도 있으면 종료 코드 1.
판단이 필요한 검사(내용·설명 수준 등)는 /notebook-qc 명령(.claude/commands/notebook-qc.md)의 점검표로 본다.
"""

import ast
import json
import re
import shutil
import sys
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[2]
TEMP = Path.home() / "000_Inbox" / "080_Temporary" / "notebook_qc"
TAGS = {"슬라이드", "퀴즈", "코드", "예제", "과제"}
BOX_HEAD = "<details><summary>강사용 메모</summary>"
CITE = re.compile(r"\(p\d+")  # "(p6)", "(p13, p14)" 같은 쪽 인용
STOCK = ("맞습니다.", "정답입니다.")
LAB_TOOLS = ("run_step", "show_code", "show_code_map", "make_blank", "show_diff")  # 강의 노트북에 있으면 FAIL
LAB_FILE_TOOLS = ("make_blank", "run_step", "show_diff", "show_code_map", "show_slides")  # 실습 노트북에 있으면 FAIL
BLANK = "✍"
BLANK_LINE = re.compile(r"^\s*\.\.\.\s*# ✍")  # 빈칸 줄: `...  # ✍️ 여기를 채웁니다`
ANSWER_HEAD = "<details><summary>정답 보기</summary>"
TOOL_CELL = re.compile(r"\b(show_\w+|slide_setup|check_env)\(|sys\.path\.insert|find_dotenv\(usecwd=True\)")  # 숨겨야 할 도구 셀
HINT_HEAD, CRITERIA_HEAD = "**프롬프트 힌트**", "**성공 기준**"
HINT_MAX_SENTENCES = 3
MARKER = re.compile(r"# ✍️ (CHANGE_HERE|WRITE_HERE):")
TODO_PLACEHOLDER = "작성 예정"


def kind_of(path):
    """파일 이름 끝(_LEC/_LAB)으로 노트북 종류를 정한다."""
    stem = Path(path).stem
    return "lecture" if stem.endswith("_LEC") else "lab" if stem.endswith("_LAB") else None


def excerpt(text, n=60):
    return " ".join(str(text).split())[:n]


def is_box(cell):
    return cell.cell_type == "markdown" and cell.source.lstrip().startswith("<details>")


def hidden(cell):
    return bool(cell.metadata.get("jupyter", {}).get("source_hidden"))


def student_md(nb):
    """수강생에게 보이는 마크다운 셀 (강사용 상자 제외)."""
    return [(i, c.source) for i, c in enumerate(nb.cells) if c.cell_type == "markdown" and not is_box(c)]


def learner_text(nb, quizzes):
    """수강생이 읽는 글: <details> 밖의 마크다운 + 퀴즈 문제·선택지·피드백."""
    out = [(i, re.sub(r"<details>.*?</details>", "", c.source, flags=re.S)) for i, c in enumerate(nb.cells)
           if c.cell_type == "markdown"]
    for i, _path, questions in quizzes:
        out.append((i, json.dumps(questions, ensure_ascii=False)))
    return out


def prose(src):
    """코드 블록(```), 인용(>), 인라인 코드(`...`)를 뺀 글만 남긴다."""
    out, fence = [], False
    for line in src.splitlines():
        if line.strip().startswith("```"):
            fence = not fence
            continue
        if fence or line.lstrip().startswith((">", "#")):  # 인용·제목 줄은 뺀다
            continue
        out.append(re.sub(r"`[^`]*`", "`…`", line))
    return "\n".join(out)


def outside_text_blocks(src):
    """```text 블록(CodeMate 지시문)을 뺀 나머지."""
    return re.sub(r"```text.*?```", "", src, flags=re.S)


def sentences(text):
    for line in text.splitlines():
        line = re.sub(r"^\s*([-*]|\d+\.)\s+", "", line).strip()
        for s in re.split(r"(?<=[.!?])\s+", line):
            if s.strip():
                yield s.strip()


def calls(src, names):
    """코드 셀에서 names에 든 함수 호출(ast.Call)을 찾는다. 파싱이 안 되면 빈 목록."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    return [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", None) in names]


def literal(node):
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError):
        return None


# ── 퀴즈 ───────────────────────────────────────────────
def check_quiz(nb, folder, R):
    code = [(i, c.source) for i, c in enumerate(nb.cells) if c.cell_type == "code"]
    bad_call, missing, loaded = [], [], []  # loaded: (셀, 경로, 문제 목록)
    for i, src in code:
        if "display_quiz(" in src:
            bad_call.append((i, "display_quiz 직접 호출"))
        if re.search(r"""["']correct["']\s*:""", src):
            bad_call.append((i, "셀 안에 정답(correct)이 보임"))
        for call in calls(src, {"show_quiz"}):
            path = literal(call.args[0]) if call.args else None
            if not (isinstance(path, str) and path.endswith(".json")):
                bad_call.append((i, "show_quiz가 JSON 파일 경로를 받지 않음"))
                continue
            f = (folder / path).resolve()
            if f.exists():
                loaded.append((i, path, json.loads(f.read_text(encoding="utf-8"))))
            else:
                missing.append((i, path))
        for call in calls(src, {"show_order_quiz"}):
            paths = re.findall(r"""["']([^"']+\.json)["']""", ast.get_source_segment(src, call) or "")
            if not paths or any(isinstance(a, (ast.List, ast.Tuple)) for a in call.args):
                bad_call.append((i, "순서 퀴즈가 파일에서 읽지 않음"))
            for p in paths:
                if not (folder / p).resolve().exists():
                    missing.append((i, p))
    R("퀴즈", "show_quiz 사용·문제는 파일에서 읽음", bad_call)
    R("퀴즈", "참조한 퀴즈 JSON 파일이 있음", missing)

    count, cite, stock, fb_seen = [], [], [], {}
    for i, path, questions in loaded:
        for n, q in enumerate(questions, 1):
            tag = f"{Path(path).name} {n}번"
            if q.get("type") == "multiple_choice":
                answers = q.get("answers", [])
                right = sum(bool(a.get("correct")) for a in answers)
                if len(answers) != 4 or right != 1:
                    count.append((i, f"{tag}: 선택지 {len(answers)}개, 정답 {right}개"))
            if CITE.search(json.dumps(q, ensure_ascii=False)):
                cite.append((i, f"{tag}: {excerpt(CITE.search(json.dumps(q, ensure_ascii=False)).group(0))}"))
            for a in q.get("answers", []):
                fb = a.get("feedback", "")
                if a.get("correct") and fb.strip().startswith(STOCK):
                    stock.append((i, f"{tag}: {excerpt(fb)}"))
                for s in sentences(fb):
                    fb_seen.setdefault(s, []).append(i)
    R("퀴즈", "객관식은 4지선다·정답 1개", count)
    R("퀴즈", "퀴즈에 쪽 인용 (pN) 없음", cite)
    R("퀴즈", "정답 피드백이 '맞습니다.' 같은 상투어로 시작하지 않음", stock)
    R("퀴즈", "같은 피드백 문장 3회 이상 반복 없음",
      [(v[0], f"{len(v)}회: {excerpt(s)}") for s, v in fb_seen.items() if len(v) >= 3])
    return loaded


# ── 수강생 글 ───────────────────────────────────────────
PROVIDER = [
    (r"LLM_PROVIDER", "LLM_PROVIDER"),
    (r"(?<![\w.])openai(?![\w.]*\.py)", "openai"),  # 02_openai.py 같은 파일 이름은 제외
    (r"gpt-6-luna", "gpt-6-luna"),
    (r"사외", "사외"),
    (r"(?<![./\w])samsung(?![./_\w])", "samsung"),  # config.samsung 같은 모듈 경로는 제외
    (r"강사용", "'강사용'이 상자 밖에 있음"),
]
DISCOURAGED = [
    (r"찍(다|습니다|히|어|은|는)", "찍다 → 출력하다"),
    (r"답 글자", "답 글자 → 답변 텍스트"),
    (r"이 권", "이 권 → 이 노트북"),
    (r"(?<!라고 )부(릅니다|르면|르고|른다|르는|릅시다)", "부르다 → 호출하다"),  # "…라고 부릅니다"(이름 붙이기)는 제외
]


FILE_REF = re.compile(r"\w+\.py\b|src/|lessons/|course/|dev/|\.ipynb")
CROSS_REF = re.compile(r"강의 노트북|실습 노트북|강의에서 본|_LEC|_LAB")


def written_files(nb):
    """노트북이 %%writefile로 직접 만드는 파일 이름(서버·앱·SKILL.md). 수강생 글에서 가리켜도 된다."""
    return {ln.split()[-1] for c in nb.cells if c.cell_type == "code"
            for ln in c.source.splitlines()[:1] if ln.startswith("%%writefile")}


# 수강생이 직접 여는 곳이라 글에서 가리켜도 되는 경로: 캡스톤 프로젝트 폴더
ALLOWED_REF = re.compile(r"capstone/")


def check_student_text(nb, quizzes, R):
    seen_text = learner_text(nb, quizzes)
    around = lambda src, m: f"…{excerpt(src[max(0, m.start() - 20):m.end() + 15], 50)}…"  # noqa: E731
    own = written_files(nb)

    def allowed(src, m):  # 이 노트북이 쓰는 파일을 터미널에서 실행하라는 안내, 캡스톤 폴더 안내는 괜찮다
        line = src[src.rfind("\n", 0, m.start()) + 1:src.find("\n", m.end()) % (len(src) + 1)]
        return any(f in line for f in own) or ALLOWED_REF.search(line)

    R("수강생 글", "보이지 않는 파일·경로(.py, src/, lessons/, .ipynb) 언급 없음 — 수강생은 노트북만 받는다(이 노트북이 쓰는 파일·캡스톤 폴더는 예외)",
      [(i, around(src, m)) for i, src in seen_text for m in FILE_REF.finditer(src) if not allowed(src, m)])
    R("수강생 글", "다른 노트북 언급 없음 — 노트북 하나로 완결",
      [(i, around(src, m)) for i, src in seen_text for m in CROSS_REF.finditer(src)], warn=True)
    R("수강생 글", "도구 이름(CodeMate) 대신 \"AI\"라고 씀",
      [(i, around(src, m)) for i, src in seen_text for m in re.finditer("CodeMate", src)])
    md = student_md(nb)
    R("수강생 글", "쪽 인용 (pN) 없음", [(i, f"…{excerpt(src[max(0, m.start() - 20):m.end() + 10], 40)}…")
                                    for i, src in md for m in CITE.finditer(src)])
    R("수강생 글", "provider·사외·강사용 단어 없음",
      [(i, f"{label}: …{excerpt(src[max(0, m.start() - 20):m.end() + 20], 50)}…")
       for i, src in md for pat, label in PROVIDER for m in re.finditer(pat, src)])
    R("수강생 글", "권장하지 않는 용어 없음",
      [(i, f"{label}: …{excerpt(src[max(0, m.start() - 15):m.end() + 15], 40)}…")
       for i, src in md for pat, label in DISCOURAGED for m in re.finditer(pat, src)], warn=True)

    plain, seen = [], {}
    for i, src in md:
        for s in sentences(prose(src)):
            if re.fullmatch(r"\*\*[^*]+\*\*", s):  # "**CodeMate 지시문**" 같은 굵은 이름표는 문장이 아니다
                continue
            if re.search(r"다\.$", s) and not re.search(r"니다\.$", s):
                plain.append((i, excerpt(s)))
            if len(s) >= 12:
                seen.setdefault(s, []).append(i)
    R("수강생 글", "합니다체 (…한다. …이다. 없음)", plain, warn=True)
    R("수강생 글", "같은 문장 3회 이상 반복 없음",
      [(v[0], f"{len(v)}회 (셀 {v}): {excerpt(s)}") for s, v in seen.items() if len(v) >= 3], warn=True)


# ── 구조 ───────────────────────────────────────────────
HEAD = re.compile(r"^(#{2,4}) (\d+(?:\.\d+)*)\.? (.*)$")


def check_structure(nb, kind, R):
    heads, bad_num, bad_tag = [], [], []
    counter = [0, 0, 0]
    for i, c in enumerate(nb.cells):
        if c.cell_type != "markdown" or is_box(c):
            continue
        for line in c.source.splitlines():
            if not re.match(r"#{2,4} ", line):
                continue
            m = HEAD.match(line)
            if not m:
                bad_num.append((i, f"번호 없는 제목: {excerpt(line)}"))
                continue
            level, nums = len(m.group(1)) - 2, [int(x) for x in m.group(2).split(".")]
            expect = counter[:level] + [counter[level] + 1]
            if nums != expect:
                bad_num.append((i, f"{m.group(2)} (기대 {'.'.join(map(str, expect))}): {excerpt(line)}"))
            counter = nums + [0] * (3 - len(nums))
            rest = m.group(3)
            small = re.search(r"\s*<small>(.*?)</small>\s*$", rest)
            title = rest[:small.start()] if small else rest
            if small:
                used = re.findall(r"\(([^)]*)\)", small.group(1))
                if not used or set(used) - TAGS or re.sub(r"\([^)]*\)|\s", "", small.group(1)):
                    bad_tag.append((i, f"허용되지 않은 표시: {excerpt(small.group(1))}"))
            if re.search(r"[\[(](슬라이드|퀴즈|코드|실습)[\])]", title):
                bad_tag.append((i, f"표시가 <small> 밖에 있음: {excerpt(line)}"))
            heads.append((i, level, m.group(2), title.strip(), small.group(1).strip() if small else ""))
    R("구조", "제목 번호가 1부터 차례로 (## N. / ### N.M / #### N.M.K)", bad_num)
    R("구조", "제목 옆 표시는 <small>(슬라이드)(퀴즈)(코드)(예제)(과제)</small>", bad_tag)

    toc = next(((i, c.source) for i, c in enumerate(nb.cells[:4]) if c.cell_type == "markdown" and "**목차**" in c.source), None)
    if toc is None:
        R("구조", "맨 위 목차가 모든 ##/### 제목을 담음", [(0, "처음 네 셀 안에 **목차** 셀이 없음")])
    else:
        R("구조", "맨 위 목차가 모든 ##/### 제목을 담음",
          [(i, f"목차에 없음: {n} {t} {lab}") for i, lv, n, t, lab in heads
           if lv <= 1 and f"{t} {lab}".strip() not in toc[1]])

    bad_box, boxes_here, last_head = [], 0, None
    for i, c in enumerate(nb.cells):
        if c.cell_type != "markdown":
            continue
        if any(h[0] == i for h in heads):
            boxes_here, last_head = 0, i
        if "강사용 메모" in c.source:
            if not (c.source.lstrip().startswith(BOX_HEAD) and c.source.rstrip().endswith("</details>")):
                bad_box.append((i, "강사용 메모가 <details> 상자 밖에 있음"))
            else:
                boxes_here += 1
                if boxes_here > 1:
                    bad_box.append((i, f"제목(셀 {last_head}) 아래 강사용 상자가 {boxes_here}개"))
    R("구조", "강사용 메모는 접힌 상자, 제목 사이에 한 개까지", bad_box)

    bad_hidden = []
    for i, c in enumerate(nb.cells):
        if c.cell_type != "code":
            continue
        predict = re.search(r"^예측_\w+\s*=", c.source, re.M)
        if predict and hidden(c):
            bad_hidden.append((i, "예측 입력 셀이 숨겨져 있음"))
        elif not predict and not hidden(c) and (kind != "lab" or TOOL_CELL.search(c.source)):
            bad_hidden.append((i, f"숨겨지지 않은 도구 셀: {excerpt(c.source, 40)}"))
    R("구조", "도구 셀은 source_hidden (강의: 예측 셀만 보임, 실습: 실습 코드 셀은 보임)", bad_hidden)

    if kind == "lab":  # 원본 파일마다 첫 구획(준비 코드)은 접는다
        first_open, section_code = [], None
        for i, c in enumerate(nb.cells):
            if is_head(c) and c.source.lstrip().startswith("## "):
                section_code = False
            elif c.cell_type == "code" and section_code is False:
                section_code = True
                if not hidden(c) and BLANK not in c.source:
                    first_open.append((i, f"절의 첫 코드 셀이 보임: {excerpt(c.source, 40)}"))
        R("구조", "원본 파일 절의 첫 코드(준비 코드)는 접힘", first_open, warn=True)



# ── 강의 노트북 ─────────────────────────────────────────
def has_deck_pdf(deck):
    """widgets._deck_pdf와 같은 규칙: "<덱>-*.pdf" 또는 "<덱>.pdf"(한글 이름은 NFC로 비교)."""
    import unicodedata

    nfc = lambda t: unicodedata.normalize("NFC", t)  # noqa: E731
    return any(nfc(p.stem).startswith(nfc(deck) + "-") or nfc(p.stem) == nfc(deck)
               for p in (ROOT / "course").glob("Chapter*/slides/**/*.pdf"))


def check_slides(nb, kind, R):
    codes = [(i, c.source) for i, c in enumerate(nb.cells) if c.cell_type == "code"]
    setup = next((i for i, s in codes if "slide_setup()" in s), None)
    first_slide = next((i for i, s in codes if "show_slides(" in s), None)
    probs = []
    if kind == "lab":  # 실습 노트북의 show_slides는 check_lab의 파일 도구 검사에서 FAIL
        return
    if kind == "lecture" and first_slide is None:
        probs.append((0, "show_slides 셀이 하나도 없음"))
    if first_slide is not None and (setup is None or setup > first_slide):
        probs.append((first_slide, "show_slides 앞에 slide_setup() 준비 셀이 없음"))
    for i, s in codes:
        for call in calls(s, {"show_slides"}):
            deck = literal(call.args[0]) if call.args else None
            if isinstance(deck, str) and not has_deck_pdf(deck):
                probs.append((i, f"덱 {deck!r}의 PDF가 course/ChapterNN/slides에 없음 (이미지 방식으로 그려짐)"))
        if "_show_slide_images" in s or "assets/slides/" in s or "<img" in s:
            probs.append((i, f"이미지 슬라이드 사용: {excerpt(s, 40)}"))
    R("구조", "준비 셀 slide_setup()·PDF.js 슬라이드(show_slides)", probs)


def check_lecture(nb, R):
    pat = re.compile(r"\b(" + "|".join(LAB_TOOLS) + r")\(")
    R("강의", "실습 코드 도구(run_step·show_code·show_code_map·make_blank·show_diff) 없음",
      [(i, f"{m.group(1)}: {excerpt(c.source, 40)}") for i, c in enumerate(nb.cells)
       if c.cell_type == "code" for m in pat.finditer(c.source)])


# ── 실습 노트북 ─────────────────────────────────────────
def is_head(c):
    return c.cell_type == "markdown" and not is_box(c) and re.match(r"#{1,4} ", c.source.lstrip()) is not None


def py_only(src):
    """셀 매직(%%writefile 등)과 셸 명령(!…) 줄을 빼고 파이썬 코드만 남긴다(문법 검사용)."""
    return "\n".join("" if ln.lstrip().startswith(("%%", "!")) else ln for ln in src.splitlines())


def fill_blanks(src, answers):
    """빈칸 줄(`...  # ✍️`)을 정답 코드로 차례대로 바꾼다(빈칸 줄의 들여쓰기를 유지)."""
    out, k = [], 0
    for line in src.splitlines():
        if BLANK_LINE.match(line) and k < len(answers):
            indent = line[: len(line) - len(line.lstrip())]
            out += [indent + a if a.strip() else a for a in answers[k].splitlines()]
            k += 1
        else:
            out.append(line)
    return "\n".join(out)


def section(cells, i):
    """셀 i가 든 절(앞 제목 다음 ~ 다음 제목 전)의 앞쪽·뒤쪽 셀 번호."""
    a = i - 1
    while a >= 0 and not is_head(cells[a]):
        a -= 1
    e = i + 1
    while e < len(cells) and not is_head(cells[e]):
        e += 1
    return range(a + 1, i), range(i + 1, e)


def check_lab(nb, R):
    cells = nb.cells
    pat = re.compile(r"\b(" + "|".join(LAB_FILE_TOOLS) + r")\(")
    R("실습", "파일 도구(make_blank·run_step·show_diff·show_code_map·show_slides) 없음 — 코드는 셀에 넣는다",
      [(i, f"{m.group(1)}: {excerpt(c.source, 40)}") for i, c in enumerate(cells)
       if c.cell_type == "code" for m in pat.finditer(c.source)])
    R("실습", "src/ 파일에 쓰는 코드 없음",
      [(i, excerpt(c.source, 50)) for i, c in enumerate(cells) if c.cell_type == "code"
       and "src/" in c.source and re.search(r"write_text|open\([^)]*['\"][wa]['\"]", c.source)])
    R("실습", "CodeMate 지시문 완성본을 주지 않음 — 힌트와 성공 기준만",
      [(i, excerpt(c.source, 50)) for i, c in enumerate(cells)
       if c.cell_type == "markdown" and not is_box(c) and "**CodeMate 지시문**" in c.source])
    R("실습", "보이는 코드 셀에 TODO 대신 `# ✍️ WRITE_HERE:`(과제)·`# ✍️ CHANGE_HERE:`(예제) 표시",
      [(i, ln.strip()[:50]) for i, c in enumerate(cells) if c.cell_type == "code" and not hidden(c)
       for ln in c.source.splitlines()
       if "TODO" in ln or (("WRITE_HERE" in ln or "CHANGE_HERE" in ln) and "# ✍️ " not in ln)])
    R("실습", "✍️ CHANGE_HERE·WRITE_HERE 표시는 주석만 있는 한 줄 (코드 줄 끝에 붙이지 않음)",
      [(i, ln.strip()[:50]) for i, c in enumerate(cells) if c.cell_type == "code" and not hidden(c)
       for ln in c.source.splitlines() if MARKER.search(ln) and not ln.lstrip().startswith("#")])
    R("실습", f"프롬프트 힌트는 {HINT_MAX_SENTENCES}문장 이내",
      [(i, f"{n}문장: {excerpt(c.source, 40)}") for i, c in enumerate(cells)
       if c.cell_type == "markdown" and c.source.lstrip().startswith(HINT_HEAD)
       and (n := len(re.findall(r"[.?!](?=\s|$)", prose(c.source[len(HINT_HEAD) + 1:])))) > HINT_MAX_SENTENCES])
    R("실습", "성공 기준 자동 검사 셀 없음 — 수강생이 스스로 판단한다",
      [(i, excerpt(c.source, 40)) for i, c in enumerate(cells) if c.cell_type == "code" and "show_criteria(" in c.source])

    syntax, guide_bad, draft, answer_bad, edit_bad = [], [], [], [], []
    for i, c in enumerate(cells):
        if c.cell_type != "code" or BLANK not in c.source or "show_criteria(" in c.source:
            continue
        before, after = section(cells, i)
        n_blank = sum(bool(BLANK_LINE.match(ln)) for ln in c.source.splitlines())
        if hidden(c):
            syntax.append((i, "✍️ 셀이 숨겨져 있음 — 수강생이 채우거나 바꿀 셀은 보여야 한다"))
            continue
        if not n_blank:  # 예제: 값만 바꿔 보는 셀. 같은 장 안에 🟢 성공 기준 글이 있어야 한다
            end = next((k for k in range(i + 1, len(cells)) if is_head(cells[k]) and cells[k].source.lstrip().startswith("## ")), len(cells))
            if not any(cells[k].cell_type == "markdown" and CRITERIA_HEAD in cells[k].source and "🟢" in cells[k].source
                       for k in range(i + 1, end)):
                edit_bad.append((i, "CHANGE_HERE 줄이 있는데 같은 장 뒤쪽에 🟢 **성공 기준** 글이 없음"))
            continue
        try:
            ast.parse(py_only(c.source))
        except SyntaxError as e:
            syntax.append((i, f"빈칸 상태로 문법 오류: {e.msg} ({e.lineno}행)"))
        # (b) 같은 절 앞쪽의 힌트와 성공 기준
        text = "\n".join(cells[k].source for k in before if cells[k].cell_type == "markdown" and not is_box(cells[k]))
        if TODO_PLACEHOLDER in text:
            draft.append((i, "힌트·성공 기준이 아직 (작성 예정)"))
        else:
            missing = [h for h in (HINT_HEAD, CRITERIA_HEAD) if h not in text]
            if missing:
                guide_bad.append((i, f"같은 절 앞쪽에 없음: {' '.join(missing)}"))
            elif "🟢" not in text:
                guide_bad.append((i, "성공 기준에 🟢 항목이 없음"))
        # (d) 다음 제목 전까지의 정답 보기 상자
        box = next((k for k in after if cells[k].cell_type == "markdown" and cells[k].source.lstrip().startswith(ANSWER_HEAD)), None)
        if box is None:
            answer_bad.append((i, "셀 뒤(다음 제목 전)에 <details><summary>정답 보기</summary> 상자가 없음"))
            continue
        answers = re.findall(r"```python\n(.*?)```", cells[box].source, flags=re.S)
        if len(answers) != n_blank:
            answer_bad.append((box, f"빈칸 {n_blank}곳인데 정답 코드 블록 {len(answers)}개"))
            continue
        try:
            ast.parse(py_only(fill_blanks(c.source, answers)))
        except SyntaxError as e:
            answer_bad.append((box, f"정답을 끼운 셀 {i}가 문법 오류: {e.msg} ({e.lineno}행)"))
    R("실습", "✍️ 셀이 보이고, 빈칸 상태 그대로 파이썬 문법에 맞음", syntax)
    R("실습", "과제 셀마다 앞에 **프롬프트 힌트**와 🟢 **성공 기준**", guide_bad)
    R("실습", "과제 셀마다 뒤에 정답 보기 상자, 정답을 끼우면 문법에 맞음", answer_bad)
    R("실습", "예제의 CHANGE_HERE마다 같은 장에 🟢 성공 기준 글", edit_bad)
    R("실습", "힌트·성공 기준이 모두 작성됨 (뼈대 상태면 WARN)", draft, warn=True)
    R("실습", "(작성 예정) 자리표시 없음", [(i, excerpt(c.source, 50)) for i, c in enumerate(cells)
                                     if not is_box(c) and TODO_PLACEHOLDER in c.source], warn=True)


# ── 안전·실행 ───────────────────────────────────────────
def check_safety(nb, kind, R):
    R("안전·실행", "저장된 출력·실행 번호 없음 (커밋용)",
      [(i, f"출력 {len(c.outputs)}개, 실행 번호 {c.execution_count}") for i, c in enumerate(nb.cells)
       if c.cell_type == "code" and (c.outputs or c.execution_count)])

    urls = []
    for i, c in enumerate(nb.cells):
        if is_box(c):
            continue
        if kind == "lab" and c.cell_type == "code" and not TOOL_CELL.search(c.source):
            continue  # 실습 노트북에 옮겨 넣은 원본 코드의 API 주소 문자열은 불러오기가 아니다
        src = outside_text_blocks(c.source) if c.cell_type == "markdown" else c.source
        if kind == "lab" and c.cell_type == "markdown":
            src = re.sub(r"```python.*?```", "", src, flags=re.S)  # 참고 코드 블록도 원본 코드
        urls += [(i, excerpt(m.group(0))) for m in re.finditer(r"(https?:)?//[\w.-]+\.\w+\S*|\bcdn\.\S+", src)]
    R("안전·실행", "외부 주소(http/https/cdn) 없음 (실습의 원본 코드는 제외)", urls)


def secret_values():
    """.env의 키·토큰 값(8자 이상). 값 자체는 출력하지 않고 출력물 검색에만 쓴다."""
    env = ROOT / ".env"
    if not env.exists():
        return []
    vals = []
    for line in env.read_text(encoding="utf-8").splitlines():
        name, _, val = line.partition("=")
        val = val.strip().strip("'\"")
        if re.search(r"KEY|TOKEN|TICKET|SECRET|PASSWORD", name) and len(val) >= 8:
            vals.append(val)
    return vals


def check_execute(path, R):
    from nbconvert.preprocessors import CellExecutionError, ExecutePreprocessor

    TEMP.mkdir(parents=True, exist_ok=True)
    out = TEMP / path.name
    shutil.copy(path, out)
    nb = nbformat.read(out, as_version=4)
    for c in nb.cells:  # 사람이 입력해야 하는 셀(input 등)은 건너뛴다
        if "skip-auto-run" in c.metadata.get("tags", []):
            c.source = "pass  # 자동 실행 검사에서 건너뜀(skip-auto-run)"
    print(f"✔ 새 커널로 실행 중: {path.name} (최대 셀당 300초)")
    crash = []
    try:
        ExecutePreprocessor(timeout=300, kernel_name="python3", allow_errors=True).preprocess(
            nb, {"metadata": {"path": str(path.parent)}})
    except CellExecutionError as e:  # allow_errors=True라 드물다
        crash.append((-1, excerpt(e, 80)))
    except Exception as e:
        crash.append((-1, f"실행 자체가 실패: {excerpt(e, 80)}"))
    nbformat.write(nb, out)
    print(f"✔ 실행본 저장: {out}")

    errors, leaks = list(crash), []
    pattern = re.compile(r"sk-[A-Za-z0-9_-]{16,}|Bearer\s+[A-Za-z0-9._-]{16,}"
                         r"|x-dep-ticket[\"']?\s*[:=]\s*[\"'][A-Za-z0-9._-]{8,}")
    secrets = secret_values()
    for i, c in enumerate(nb.cells):
        for o in c.get("outputs", []):
            if o.output_type == "error":
                errors.append((i, f"{o.ename}: {excerpt(o.evalue, 60)}"))
            text = json.dumps(o, ensure_ascii=False)
            if pattern.search(text) or any(s in text for s in secrets):
                leaks.append((i, "출력에 키처럼 보이는 값이 있음 (값은 표시하지 않음)"))
    R("안전·실행", "새 커널 실행 오류 없음", errors)
    R("안전·실행", "출력에 키·토큰 값 없음", sorted(set(leaks)))


# ── 실행과 보고 ─────────────────────────────────────────
def qc(path, execute=False):
    rows = []

    def R(group, name, problems, warn=False):
        status = "PASS" if not problems else ("WARN" if warn else "FAIL")
        rows.append((group, name, status, problems))

    nb = nbformat.read(path, as_version=4)
    kind = kind_of(path)
    if kind is None:
        R("종류", "파일 이름이 _LEC 또는 _LAB으로 끝남", [(0, path.name)], warn=True)
    if "course" in path.parts:  # 수강생본에는 강사용 메모가 없어야 한다(강사본은 dev/instructor/)
        R("구조", "수강생본에 강사용 메모 없음", [(i, "강사용 메모 상자") for i, c in enumerate(nb.cells) if c.cell_type == "markdown" and c.source.lstrip().startswith(BOX_HEAD)])
    quizzes = check_quiz(nb, path.parent, R)
    check_student_text(nb, quizzes, R)
    check_structure(nb, kind, R)
    check_slides(nb, kind, R)
    if kind == "lecture":
        check_lecture(nb, R)
    else:
        check_lab(nb, R)
    check_safety(nb, kind, R)
    if execute:
        check_execute(path, R)

    print(f"\n=== {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path} ({kind or '종류 모름'}) ===")
    for group, name, status, problems in rows:
        print(f"{status:<4} | {group:<5} | {name}")
        for i, msg in problems[:15]:
            print(f"       - 셀 {i}: {msg}")
        if len(problems) > 15:
            print(f"       … 외 {len(problems) - 15}건")
    counts = {s: sum(r[2] == s for r in rows) for s in ("PASS", "WARN", "FAIL")}
    print(f"합계: PASS {counts['PASS']} · WARN {counts['WARN']} · FAIL {counts['FAIL']}")
    return counts["FAIL"] == 0


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    execute = "--execute" in sys.argv
    paths = [Path(a).resolve() for a in args] or sorted((ROOT / "course").glob("Chapter*/notebooks/*.ipynb"))
    if not paths:
        print("✖ 검사할 노트북 | course/Chapter*/notebooks/에 .ipynb가 없음 | 경로를 인자로 주세요")
        return 1
    ok = True
    for n, p in enumerate(paths, 1):
        if not p.exists():
            print(f"✖ 노트북 읽기 | 파일 없음: {p} | 경로를 확인하세요")
            ok = False
            continue
        print(f"✔ [{n}/{len(paths)}] 검사: {p.name}")
        ok = qc(p, execute) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
