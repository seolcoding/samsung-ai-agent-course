"""Chapter01 1-2 교안 노트북을 조립한다.

실행(프로젝트 루트): uv run python lessons/drafts/build_1_2.py
입력: lessons/drafts/1-2_cells_common.json(공통 셀), 1-2_cells_C.json(설명 셀, C 수준으로 확정)
출력: lessons/Chapter01/1-2_llm_api.ipynb (출력 없음)

뼈대(셀 순서)는 이 파일이 정하고, 글은 JSON에서 가져온다. 원본 코드는 run_step으로 그대로 실행한다.
제목은 노트북 안에서 1부터 번호를 매기고, 제목마다 [슬라이드]·[퀴즈]·[코드]·[실습] 표시를 붙인다.
맨 위 목차는 이 제목과 표시로 자동으로 만든다.
"""

import json
import re
import sys
from pathlib import Path

import nbformat as nbf
from pprint import pformat

HERE = Path(__file__).parent
LESSONS = HERE.parent
RAW = "../../src/raw/Chapter01/01-llm-api"  # 노트북(lessons/Chapter01/) 기준 경로
F01, F02, F03 = f"{RAW}/01_requests.py", f"{RAW}/02_openai.py", f"{RAW}/03_langchain.py"
LLM = "../../src/config/llm.py"
OUT = LESSONS / "Chapter01" / "1-2_llm_api.ipynb"
QUIZ_DIR = LESSONS / "assets" / "quizzes" / "1-2"
# p9 예시의 토큰 목록. 2-1 퀴즈의 정답(목록 길이)을 여기서 계산한다.
P9_TOKENS = ["Lang", "Chain", "으로", " AI", " Agent", "를", " 만든", "다", "."]
P9_SENTENCE = "LangChain으로 AI Agent를 만든다."


TAG_ORDER = ["슬라이드", "퀴즈", "코드", "실습"]


def tags_of(cell):
    """셀 하나가 어떤 종류인지 돌려준다(목차·제목 옆 표시용)."""
    src = cell.source
    if cell.cell_type == "code":
        if "show_slides(" in src:
            return {"슬라이드"}
        if "show_quiz(" in src or "show_order_quiz(" in src:
            return {"퀴즈"}
        if not cell.metadata.get("jupyter", {}).get("source_hidden"):  # 수강생이 예측을 적는 셀
            return {"퀴즈"}
        if "show_checklist(" in src or "slide_setup(" in src:
            return set()
        return {"코드"}
    return {"실습"} if "CodeMate" in src and "```text" in src else set()


def build(version="C"):
    common = json.loads((HERE / "1-2_cells_common.json").read_text(encoding="utf-8"))
    text = json.loads((HERE / f"1-2_cells_{version}.json").read_text(encoding="utf-8"))
    cells = []

    pending = []  # 이 절에서 모은 강사용 메모. 다음 절 제목 앞에서 한 상자로 내보낸다.

    def flush():
        if pending:
            body = "\n\n---\n\n".join(pending)
            cell = nbf.v4.new_markdown_cell("<details><summary>강사용 메모</summary>\n\n" + body + "\n\n</details>")
            cell.metadata["tags"] = ["강사용"]
            cells.append(cell)
            pending.clear()

    def md(src):
        # 수강생 글에는 "(p6)" 같은 쪽 인용을 넣지 않는다(어색함). 쪽은 슬라이드 뷰어가 보여 준다.
        assert not re.search(r"\(p\d+", src), f"수강생 글에 쪽 인용이 남아 있다: {src[:60]!r}"
        if re.match(r"#{1,3} ", src.lstrip()):  # 새 절이 시작되면 앞 절의 강사용 메모를 먼저 내보낸다
            flush()
        cells.append(nbf.v4.new_markdown_cell(src.strip()))

    def code(src, visible=False):
        # 교안 도구를 부르는 코드는 수강생 화면에서 접어 두고 출력만 보이게 한다.
        # VS Code·Jupyter는 metadata.jupyter.source_hidden을 보고 입력 칸을 접는다.
        cell = nbf.v4.new_code_cell(src.strip())
        if not visible:
            cell.metadata["jupyter"] = {"source_hidden": True}
            cell.metadata["tags"] = ["교안도구"]
        cells.append(cell)

    def meta(src):
        # 설정·환경·강사용 내용은 절마다 한 상자로 모아 절 끝에 접어 둔다.
        pending.append(src.strip())

    def h(level, title):
        # 번호가 붙은 제목. 표시([슬라이드] 등)와 목차는 다 만든 뒤에 채운다.
        md("#" * level + " " + title)
        cells[-1].metadata["heading"] = {"level": level, "title": title}

    def with_meta(table, key):
        md(table[key])
        if table.get(key + "__meta"):
            meta(table[key + "__meta"])

    def v(key):  # 버전별 글
        with_meta(text, key)

    def c(key):  # 공통 글
        with_meta(common, key)

    def slides(*pages):
        code(f'show_slides("1-2", {list(pages)})')

    def quiz_file(name, questions):
        # 정답이 코드 셀에 보이지 않도록 문제는 파일로 두고 셀에서는 경로만 부른다.
        for q in questions:  # 퀴즈 선택지는 항상 4개, 정답은 1개
            assert len(q["answers"]) == 4, f"{name}: 선택지가 {len(q['answers'])}개"
            assert sum(a["correct"] for a in q["answers"]) == 1, f"{name}: 정답이 1개가 아님"
            assert "(p" not in json.dumps(q, ensure_ascii=False), f"{name}: 퀴즈에 쪽 인용이 남아 있다"
        QUIZ_DIR.mkdir(parents=True, exist_ok=True)
        (QUIZ_DIR / f"{name}.json").write_text(json.dumps(questions, ensure_ascii=False, indent=1), encoding="utf-8")
        code(f'show_quiz("../assets/quizzes/1-2/{name}.json")')

    def quiz(key):
        quiz_file(key, [common[key]])

    def step(path, start, end, var, look, **opts):
        s = "None" if start is None else repr(start)
        e = "None" if end is None else repr(end)
        extra = "".join(f", {k}={v!r}" for k, v in opts.items())
        code(f"{var} = run_step({path!r}, {s}, {e}{extra})")
        c(look)

    # 0 도입
    md(common["title"])
    if common.get("title__meta"):
        meta(common["title__meta"].replace("{VERSION}", "C"))
    code(
        "import json\nimport sys\n\nsys.path.insert(0, '..')  # lessons/assets 도구를 불러오기 위한 경로\n\n"
        "from assets.widgets import run_step, show_checklist, show_code, show_code_map, show_order_quiz, show_quiz, show_slides, slide_setup\n\n"
        "slide_setup()  # 슬라이드 뷰어(PDF.js)를 불러옵니다. 슬라이드가 비어 보이면 이 셀을 다시 실행합니다."
    )
    slides(1, 2)
    v("intro")
    code(common["env_check_code"])
    c("env_check_look")

    # 1-1
    h(2, "1. LLM의 학습과 추론")
    h(3, "1.1 사전 학습과 Instruction Tuning")
    c("q11_lead")
    quiz("q11")
    slides(3, 4)
    v("p4")
    slides(5)
    v("p5")
    v("sum11")

    # 1-2
    h(3, "1.2 다음 토큰 예측과 생성 과정")
    slides(6)
    v("p6")
    md("**먼저 예측해 봅니다.** 다음 쪽을 보기 전에, 요청을 보내고 응답을 받기까지의 순서를 맞혀 보세요.")
    (QUIZ_DIR / "order12.json").write_text(json.dumps(common["order12"], ensure_ascii=False, indent=1), encoding="utf-8")
    code('show_order_quiz(**json.load(open("../assets/quizzes/1-2/order12.json", encoding="utf-8")))')
    slides(7)
    v("p7")
    v("sum12")

    # 실행 ①
    h(3, "1.3 실행: 요청을 보내고 응답 받기 (`01_requests.py`)")
    v("run1_intro")
    code(f"show_code_map({F01!r}, {pformat(common['map01'], width=100, sort_dicts=False)})")
    c("q_run1_lead")
    quiz("q_run1")
    h(4, "1.3.1 준비")
    v("r1s1")
    step(F01, None, "payload = {", "ns01", "look_r1s1", collapsed="준비 코드: 환경 설정(강사용)")
    h(4, "1.3.2 요청 본문")
    v("r1s2")
    step(F01, "payload = {", "new_response = requests.post", "ns01", "look_r1s2", fold=[("if provider", None, "환경별 설정 조정(강사용)")])
    h(4, "1.3.3 전송과 응답")
    v("r1s3")
    step(F01, "new_response = requests.post", '"""', "ns01", "look_r1s3")
    v("sum_run1")

    # 2 Tokenization
    h(2, "2. Tokenization")
    h(3, "2.1 토큰의 의미")
    slides(8, 9)
    v("p9")
    n, words = len(P9_TOKENS), len(P9_SENTENCE.split())
    quiz_file("q21", [{
        "question": f'슬라이드 예시에서 "{P9_SENTENCE}"는 몇 개의 토큰으로 나뉘었나요?',
        "type": "multiple_choice",
        "answers": [
            {"answer": f"{words}개", "correct": False, "feedback": "띄어쓰기로 나눈 단어 수입니다. 토큰 수와는 다릅니다."},
            {"answer": f"{n - 2}개", "correct": False, "feedback": "한 단어가 둘로 나뉜 곳을 다시 세어 보세요."},
            {"answer": f"{n}개", "correct": True, "feedback": "예시 목록의 항목 수입니다. 토큰은 단어의 일부나 조사로도 나뉩니다."},
            {"answer": f"{n + 3}개", "correct": False, "feedback": "슬라이드 예시 목록에 든 항목만 셉니다."},
        ],
    }])
    v("sum21")
    h(3, "2.2 토큰 수와 비용")
    slides(10)
    v("p10")
    c("back22")
    code(common["back22_code"])
    c("back22_look")
    slides(11)
    v("p11")
    quiz("q22")
    v("sum22")

    # 3 Context Window
    h(2, "3. Context Window")
    h(3, "3.1 Context Window")
    c("q31")
    code(common["q31_code"], visible=True)
    slides(12, 13, 14)
    v("p14")
    v("sum31")

    # 실행 ②
    h(3, "3.2 실행: 한 번 묻기, 이어서 묻기, 조각으로 받기 (`02_openai.py`)")
    v("run2_intro")
    code(f"show_code_map({F02!r}, {pformat(common['map02'], width=100, sort_dicts=False)})")
    h(4, "3.2.1 준비")
    v("r2s1")
    step(F02, None, "# ── Single Turn", "ns02", "look_r2s1", collapsed="준비 코드: 환경 설정(강사용)")
    h(4, "3.2.2 한 번 묻기")
    v("r2s2")
    step(F02, "# ── Single Turn", "# ── Multi Turn", "ns02", "look_r2s2")
    h(4, "3.2.3 이어서 묻기")
    v("r2s3")
    step(F02, "# ── Multi Turn", "# 이전 응답", "ns02", "look_r2s3")
    h(4, "3.2.4 앞 대화 이어 붙이기")
    v("r2s4")
    step(F02, "# 이전 응답", "# ── Streaming", "ns02", "look_r2s4")
    code(common["cmp31_code"])
    h(4, "3.2.5 조각으로 받기")
    v("r2s5")
    step(F02, "# ── Streaming", "# ── Temperature", "ns02", "look_r2s5")
    v("sum_run2")

    # 3-2
    h(3, "3.3 입력 품질과 출력 품질")
    slides(15, 16)
    v("p16")
    code(f"show_checklist({pformat(common['check32'], width=100, sort_dicts=False)}, title='좋은 입력의 네 가지')")
    v("sum32")

    # 4 대화 구조
    h(2, "4. LLM API의 대화 구조")
    h(3, "4.1 System, User, Assistant 역할")
    slides(17, 18)
    v("p18")
    c("back41")
    quiz("q41")
    v("sum41")

    # 실행 ③
    h(3, "4.2 실행: LangChain과 `get_llm()` (`03_langchain.py`)")
    v("run3_intro")
    code(f"show_code({LLM!r}, collapsed='get_llm() 안쪽: 환경에 맞는 모델 설정을 고르는 코드')")
    code(f"show_code_map({F03!r}, {pformat(common['map03'], width=100, sort_dicts=False)})")
    h(4, "4.2.1 불러오기와 모델 준비")
    v("r3s1")
    step(F03, None, "# ── 기본 invoke", "ns03", "look_r3s1")
    h(4, "4.2.2 역할 메시지로 묻기")
    v("r3s2")
    step(F03, "# ── 기본 invoke", "# ── Streaming", "ns03", "look_r3s2")
    h(4, "4.2.3 조각으로 받기")
    v("r3s3")
    c("warn_r3s3")
    step(F03, "# ── Streaming", None, "ns03", "look_r3s3")
    v("sum_run3")

    # 4-2
    h(3, "4.3 모델 파라미터의 영향")
    slides(19)
    v("p19")
    c("note42")
    quiz("q42")
    v("sum42")

    # 5 CodeMate
    h(2, "5. CodeMate 실습")
    v("cm_intro")
    h(3, "5.1 실습 A: 원본 설명 받기")
    c("cmA")
    code(f"show_checklist({pformat(common['checkA'], width=100, sort_dicts=False)}, title='실습 A 리뷰')")
    h(3, "5.2 실습 B: 원본끼리 비교하기")
    c("cmB")
    code(f"show_checklist({pformat(common['checkB'], width=100, sort_dicts=False)}, title='실습 B 리뷰')")
    h(3, "5.3 실습 C (선택): 지시로 다시 만들고 비교하기")
    c("cmC")

    # 6 정리
    h(2, "6. 정리 퀴즈")
    quiz_file("final", common["final"])
    c("closing")

    flush()

    # 제목마다 그 아래(하위 제목 포함)에 든 셀의 종류를 모아 표시하고, 맨 위에 목차를 만든다.
    heads = [k for k, cell in enumerate(cells) if "heading" in cell.metadata]
    toc = []
    for n, k in enumerate(heads):
        level = cells[k].metadata["heading"]["level"]
        end = next((j for j in heads[n + 1:] if cells[j].metadata["heading"]["level"] <= level), len(cells))
        found = set().union(*(tags_of(cells[j]) for j in range(k + 1, end) if "강사용" not in cells[j].metadata.get("tags", [])))
        if cells[k].metadata["heading"]["title"].startswith("5."):
            found.add("실습")
        label = " ".join(f"({t})" for t in TAG_ORDER if t in found)
        title = cells[k].metadata["heading"]["title"]
        # 표시는 제목 바로 옆에 작게 붙인다: "1.1 제목 (슬라이드) (퀴즈)"
        cells[k].source = "#" * level + " " + title + (f" <small>{label}</small>" if label else "")
        if level <= 3:
            toc.append("  " * (level - 2) + f"- {title}" + (f" {label}" if label else ""))
    toc_cell = nbf.v4.new_markdown_cell("**목차**\n\n" + "\n".join(toc))
    cells.insert(1, toc_cell)

    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, OUT)
    print(f"✔ {OUT.relative_to(LESSONS.parent)} ({len(cells)}셀)")


if __name__ == "__main__":
    build()
