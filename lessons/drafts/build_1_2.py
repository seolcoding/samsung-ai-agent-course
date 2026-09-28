"""1-2 교안 노트북 A/B/C를 조립한다.

실행(프로젝트 루트): uv run python lessons/drafts/build_1_2.py
입력: lessons/drafts/1-2_cells_common.json(세 버전 공통), 1-2_cells_{A,B,C}.json(버전별 설명)
출력: lessons/1-2_llm_api_{A,B,C}.ipynb (출력 없음)

뼈대(셀 순서)는 이 파일이 정하고, 글은 JSON에서 가져온다. 원본 코드는 run_step으로 그대로 실행한다.
"""

import json
import sys
from pathlib import Path

import nbformat as nbf
from pprint import pformat

HERE = Path(__file__).parent
LESSONS = HERE.parent
RAW = "../src/raw/Chapter01/01-llm-api"
F01, F02, F03 = f"{RAW}/01_requests.py", f"{RAW}/02_openai.py", f"{RAW}/03_langchain.py"
LLM = "../src/config/llm.py"
SOL03 = "../src/solution/Chapter01/01-llm-api/03_langchain.py"
QUIZ_DIR = LESSONS / "assets" / "quizzes" / "1-2"
# p9 예시의 토큰 목록. 2-1 퀴즈의 정답(목록 길이)을 여기서 계산한다.
P9_TOKENS = ["Lang", "Chain", "으로", " AI", " Agent", "를", " 만든", "다", "."]
P9_SENTENCE = "LangChain으로 AI Agent를 만든다."


def build(version):
    common = json.loads((HERE / "1-2_cells_common.json").read_text(encoding="utf-8"))
    text = json.loads((HERE / f"1-2_cells_{version}.json").read_text(encoding="utf-8"))
    cells = []

    def md(src):
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
        # 설정·환경·강사용 내용은 접힌 상자에 넣는다. 수강생은 건너뛰어도 된다.
        cells.append(nbf.v4.new_markdown_cell(
            "<details><summary>강사용 메모 (수강생은 건너뛰어도 됩니다)</summary>\n\n" + src.strip() + "\n\n</details>"))
        cells[-1].metadata["tags"] = ["강사용"]

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
        QUIZ_DIR.mkdir(parents=True, exist_ok=True)
        (QUIZ_DIR / f"{name}.json").write_text(json.dumps(questions, ensure_ascii=False, indent=1), encoding="utf-8")
        code(f'display_quiz("assets/quizzes/1-2/{name}.json", max_width=800)')

    def quiz(key):
        quiz_file(key, [common[key]])

    def step(path, start, end, var, look, **opts):
        s = "None" if start is None else repr(start)
        e = "None" if end is None else repr(end)
        extra = "".join(f", {k}={v!r}" for k, v in opts.items())
        code(f"{var} = run_step({path!r}, {s}, {e}{extra})")
        c(look)

    # 0 도입
    md(common["title"].replace("{VERSION}", version))
    if common.get("title__meta"):
        meta(common["title__meta"].replace("{VERSION}", version))
    code(
        "import json\n\nfrom jupyterquiz import display_quiz\n"
        "from assets.widgets import run_step, show_checklist, show_code, show_code_map, show_order_quiz, show_slides"
    )
    slides(1, 2)
    v("intro")
    code(common["env_check_code"])
    c("env_check_look")

    # 1-1
    md("## 1. LLM의 학습과 추론\n### 1-1 사전 학습과 Instruction Tuning")
    c("q11_lead")
    quiz("q11")
    slides(3, 4)
    v("p4")
    slides(5)
    v("p5")
    v("sum11")

    # 1-2
    md("### 1-2 다음 토큰 예측과 생성 과정")
    slides(6)
    v("p6")
    md("**먼저 예측해 봅니다.** 다음 쪽을 보기 전에, 요청을 보내고 응답을 받기까지의 순서를 맞혀 보세요.")
    (QUIZ_DIR / "order12.json").write_text(json.dumps(common["order12"], ensure_ascii=False, indent=1), encoding="utf-8")
    code('show_order_quiz(**json.load(open("assets/quizzes/1-2/order12.json", encoding="utf-8")))')
    slides(7)
    v("p7")
    v("sum12")

    # 실행 ①
    md("### ▶ 실행 ① `01_requests.py` — 요청을 보내고 응답 받기")
    v("run1_intro")
    code(f"show_code_map({F01!r}, {pformat(common['map01'], width=100, sort_dicts=False)}, deck=\"1-2\")")
    c("q_run1_lead")
    quiz("q_run1")
    md("#### 실행 ① · 단계 1")
    v("r1s1")
    step(F01, None, "payload = {", "ns01", "look_r1s1", collapsed="준비 코드: 환경 설정(강사용)")
    md("#### 실행 ① · 단계 2")
    v("r1s2")
    step(F01, "payload = {", "new_response = requests.post", "ns01", "look_r1s2", fold=[("if provider", None, "환경별 설정 조정(강사용)")])
    md("#### 실행 ① · 단계 3")
    v("r1s3")
    step(F01, "new_response = requests.post", '"""', "ns01", "look_r1s3")
    v("sum_run1")

    # 2 Tokenization
    md("## 2. Tokenization\n### 2-1 토큰의 의미")
    slides(8, 9)
    v("p9")
    n, words = len(P9_TOKENS), len(P9_SENTENCE.split())
    quiz_file("q21", [{
        "question": f'p9 예시에서 "{P9_SENTENCE}"는 몇 개의 토큰으로 나뉘었나요?',
        "type": "multiple_choice",
        "answers": [
            {"answer": f"{words}개", "correct": False, "feedback": "띄어쓰기로 나눈 단어 수입니다. 토큰 수와는 다릅니다 (p9)."},
            {"answer": f"{n - 2}개", "correct": False, "feedback": "한 단어가 둘로 나뉜 곳을 다시 세어 보세요 (p9)."},
            {"answer": f"{n}개", "correct": True, "feedback": "맞습니다. 예시 목록의 항목 수입니다. 토큰은 단어의 일부나 조사로도 나뉩니다 (p9)."},
            {"answer": f"{n + 3}개", "correct": False, "feedback": "슬라이드 예시 목록에 든 항목만 셉니다 (p9)."},
        ],
    }])
    v("sum21")
    md("### 2-2 토큰 수와 비용")
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
    md("## 3. Context Window\n### 3-1 Context Window")
    c("q31")
    code(common["q31_code"], visible=True)
    slides(12, 13, 14)
    v("p14")
    v("sum31")

    # 실행 ②
    md("### ▶ 실행 ② `02_openai.py` — 한 번 묻기, 이어서 묻기, 조각으로 받기")
    v("run2_intro")
    code(f"show_code_map({F02!r}, {pformat(common['map02'], width=100, sort_dicts=False)}, deck=\"1-2\")")
    md("#### 실행 ② · 단계 1")
    v("r2s1")
    step(F02, None, "# ── Single Turn", "ns02", "look_r2s1", collapsed="준비 코드: 환경 설정(강사용)")
    md("#### 실행 ② · 단계 2")
    v("r2s2")
    step(F02, "# ── Single Turn", "# ── Multi Turn", "ns02", "look_r2s2")
    md("#### 실행 ② · 단계 3")
    v("r2s3")
    step(F02, "# ── Multi Turn", "# 이전 응답", "ns02", "look_r2s3")
    md("#### 실행 ② · 단계 4")
    v("r2s4")
    step(F02, "# 이전 응답", "# ── Streaming", "ns02", "look_r2s4")
    code(common["cmp31_code"])
    md("#### 실행 ② · 단계 5")
    v("r2s5")
    step(F02, "# ── Streaming", "# ── Temperature", "ns02", "look_r2s5")
    v("sum_run2")

    # 3-2
    md("### 3-2 입력 품질과 출력 품질")
    slides(15, 16)
    v("p16")
    code(f"show_checklist({pformat(common['check32'], width=100, sort_dicts=False)}, title='좋은 입력의 네 가지 (p16)')")
    v("sum32")

    # 4 대화 구조
    md("## 4. LLM API의 대화 구조\n### 4-1 System, User, Assistant 역할")
    slides(17, 18)
    v("p18")
    c("back41")
    quiz("q41")
    v("sum41")

    # 실행 ③
    md("### ▶ 실행 ③ `03_langchain.py` — LangChain과 `get_llm()`")
    v("run3_intro")
    code(f"show_code({LLM!r}, collapsed='get_llm() 안쪽: 환경에 맞는 모델 설정을 고르는 코드')")
    code(f"show_code_map({F03!r}, {pformat(common['map03'], width=100, sort_dicts=False)}, deck=\"1-2\")")
    md("#### 실행 ③ · 단계 1")
    v("r3s1")
    step(F03, None, "# ── 기본 invoke", "ns03", "look_r3s1")
    md("#### 실행 ③ · 단계 2")
    v("r3s2")
    step(F03, "# ── 기본 invoke", "# ── Streaming", "ns03", "look_r3s2")
    md("#### 실행 ③ · 단계 3")
    v("r3s3")
    c("warn_r3s3")
    step(F03, "# ── Streaming", None, "ns03", "look_r3s3")
    v("sum_run3")

    # 4-2
    md("### 4-2 모델 파라미터의 영향")
    slides(19)
    v("p19")
    c("note42")
    quiz("q42")
    v("sum42")

    # 5 CodeMate
    md("## 5. CodeMate 실습")
    v("cm_intro")
    c("cmA")
    code(f"show_checklist({pformat(common['checkA'], width=100, sort_dicts=False)}, title='실습 A 리뷰')")
    c("cmB")
    code(f"show_checklist({pformat(common['checkB'], width=100, sort_dicts=False)}, title='실습 B 리뷰')")
    c("cmC")

    # 6 정리
    md("## 6. 정리 퀴즈")
    quiz_file("final", common["final"])
    c("closing")

    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    out = LESSONS / f"1-2_llm_api_{version}.ipynb"
    nbf.write(nb, out)
    print(f"✔ {out.relative_to(LESSONS.parent)} ({len(cells)}셀)")


if __name__ == "__main__":
    for ver in sys.argv[1:] or ["A", "B", "C"]:
        build(ver)
