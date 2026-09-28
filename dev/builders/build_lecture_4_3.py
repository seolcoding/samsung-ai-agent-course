"""Chapter02 4-3 강의 노트북을 조립한다. 슬라이드·설명·퀴즈만 담고 실습 코드는 넣지 않는다
(실습은 4-3_capstone_LAB 안내 노트북과 course/Chapter02/capstone/ 폴더).

실행(프로젝트 루트): uv run python dev/builders/build_lecture_4_3.py
입력: dev/builders/4-3_cells.json(설명 셀·퀴즈·강사용 메모, C 수준)
출력: course/Chapter02/notebooks/4-3_capstone_LEC.ipynb (출력 없음), course/Chapter02/assets/quizzes/4-3/*.json
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nbkit import Notebook  # noqa: E402

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
COURSE = ROOT / "course"
OUT = COURSE / "Chapter02" / "notebooks" / "4-3_capstone_LEC.ipynb"


def build():
    text = json.loads((HERE / "4-3_cells.json").read_text(encoding="utf-8"))
    nb = Notebook(COURSE / "Chapter02" / "assets" / "quizzes" / "4-3", "../assets/quizzes/4-3")

    def v(key):  # 설명 셀과 그 강사용 메모
        nb.md(text[key])
        nb.meta(text.get(key + "__meta"))

    def slides(*pages):
        nb.code(f'show_slides("4-3", {list(pages)})')

    def quiz(key):
        nb.quiz_file(key, [text[key]])

    nb.md(text["title"])
    nb.meta(text.get("title__meta"))
    nb.code(
        "import sys\n\nsys.path.insert(0, '..')  # 챕터 폴더의 assets 도구를 불러오기 위한 경로\n\n"
        "from assets.widgets import show_quiz, show_slides, slide_setup\n\n"
        "slide_setup()  # 슬라이드 뷰어(PDF.js)를 불러옵니다. 슬라이드가 비어 보이면 이 셀을 다시 실행합니다."
    )
    slides(1, 2)
    v("intro")

    nb.h(2, "1. Workflow 구성")
    nb.h(3, "1.1 전체 흐름")
    slides(3)
    v("p3")
    quiz("q11")
    v("sum11")
    nb.h(3, "1.2 Human-in-the-loop")
    slides(4)
    v("p4")
    quiz("q12")
    v("sum12")

    nb.h(2, "2. MCP와 RAGaaS 활용")
    slides(5)
    v("p5")
    quiz("q2")
    v("sum2")

    nb.h(2, "3. Deep Agents와 Langfuse")
    nb.h(3, "3.1 Deep Agents")
    slides(6)
    v("p6")
    quiz("q31")
    v("sum31")
    nb.h(3, "3.2 Langfuse")
    slides(7)
    v("p7")
    quiz("q32")
    v("sum32")

    nb.h(2, "4. 보고서 품질 평가")
    slides(8, 9)
    v("p8")
    quiz("q4")
    v("sum4")

    nb.h(2, "5. 정리 퀴즈")
    nb.quiz_file("final", text["final"])
    nb.md(text["closing"])
    nb.finish(OUT)


if __name__ == "__main__":
    build()
